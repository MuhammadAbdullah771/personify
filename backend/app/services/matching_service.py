from __future__ import annotations

import logging
from typing import Any, Optional

import numpy as np

from app.config import Settings
from app.schemas.search import PersonDetails, SearchSuccessMatch, SearchSuccessNoMatch
from app.services.face_processor import FaceAnalysisResult, FaceProcessor
from app.services.supabase_service import SupabaseService

logger = logging.getLogger(__name__)


class MatchingService:
    def __init__(
        self,
        settings: Settings,
        face_processor: FaceProcessor | None = None,
        supabase_service: SupabaseService | None = None,
    ) -> None:
        self._settings = settings
        self._face = face_processor or FaceProcessor()
        self._supabase = supabase_service or SupabaseService(settings)
        self._encoding_cache: dict[str, np.ndarray] = {}

    def find_match(self, probe_bytes: bytes) -> dict[str, Any]:
        probe = self._face.analyze_image_bytes(probe_bytes)
        if probe is None:
            return {
                "status": "error",
                "message": "No face detected in the uploaded photo.",
            }

        cases = self._supabase.fetch_active_cases()
        if not cases:
            return SearchSuccessNoMatch().model_dump()

        ranked: list[dict[str, Any]] = []
        threshold = self._settings.match_distance_threshold

        for case in cases:
            case_id = str(case.get("id", ""))
            image_url = case.get("image_url")
            if not case_id or not image_url:
                continue

            try:
                candidate_encoding = self._get_case_encoding(case_id, str(image_url))
            except Exception as exc:  # noqa: BLE001 — log and skip bad records
                logger.warning("Skipping case %s: %s", case_id, exc)
                continue

            distance = self._face.distance(probe.encoding, candidate_encoding)
            confidence = self._face.distance_to_confidence(distance, threshold)

            ranked.append(
                {
                    "case_id": case_id,
                    "reporter_id": str(case.get("reporter_id", "")),
                    "distance": round(distance, 4),
                    "confidence": confidence,
                    "full_name": case.get("full_name", ""),
                    "contact_info": case.get("contact_info", ""),
                    "reporter_address": case.get("reporter_address", ""),
                    "missing_address": case.get("missing_address", ""),
                    "image_url": image_url,
                    "landmark_regions": self._face.landmarks_summary(probe.landmarks),
                }
            )

        ranked.sort(key=lambda item: item["distance"])

        best: Optional[dict[str, Any]] = ranked[0] if ranked else None
        if best is None or best["distance"] >= threshold:
            return SearchSuccessNoMatch().model_dump()

        person = PersonDetails(
            case_id=best["case_id"],
            full_name=best["full_name"],
            contact_info=best["contact_info"],
            reporter_address=best["reporter_address"],
            missing_address=best["missing_address"],
            image_url=best["image_url"],
        )

        payload = SearchSuccessMatch(
            confidence=best["confidence"],
            person_details=person,
            distance=best["distance"],
            ranked_matches=ranked[:5],
        )

        reporter_id = best.get("reporter_id")
        if reporter_id:
            try:
                self._supabase.insert_match_notification(
                    reporter_id=reporter_id,
                    case_id=best["case_id"],
                    matched_person_name=best["full_name"],
                    missing_address=best["missing_address"],
                    contact_info=best["contact_info"],
                    confidence=best["confidence"],
                )
            except Exception as exc:  # noqa: BLE001
                logger.warning("Could not insert match notification: %s", exc)

        return payload.model_dump()

    def _get_case_encoding(self, case_id: str, image_url: str) -> np.ndarray:
        if case_id in self._encoding_cache:
            return self._encoding_cache[case_id]

        image_bytes = self._supabase.download_image(image_url)
        analysis = self._face.analyze_image_bytes(image_bytes)
        if analysis is None:
            raise ValueError(f"No face found in database image for case {case_id}")

        self._encoding_cache[case_id] = analysis.encoding
        return analysis.encoding

    def shutdown(self) -> None:
        self._supabase.close()
