"""Face detection, 68-point landmarks, and 128-D embeddings via dlib/face_recognition."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

import cv2
import face_recognition
import numpy as np


@dataclass(frozen=True)
class FaceAnalysisResult:
    encoding: np.ndarray
    landmarks: dict[str, list[tuple[int, int]]]
    face_location: tuple[int, int, int, int]


class FaceProcessor:
    """Wraps OpenCV decode + face_recognition (dlib ResNet + 68-point shape predictor)."""

    def analyze_image_bytes(self, image_bytes: bytes) -> Optional[FaceAnalysisResult]:
        rgb_image = self._bytes_to_rgb(image_bytes)
        if rgb_image is None:
            return None

        face_locations = face_recognition.face_locations(rgb_image, model="hog")
        if not face_locations:
            return None

        landmarks_list = face_recognition.face_landmarks(rgb_image, face_locations)
        encodings = face_recognition.face_encodings(rgb_image, face_locations)

        if not encodings:
            return None

        return FaceAnalysisResult(
            encoding=encodings[0],
            landmarks=landmarks_list[0],
            face_location=face_locations[0],
        )

    @staticmethod
    def _bytes_to_rgb(image_bytes: bytes) -> Optional[np.ndarray]:
        buffer = np.frombuffer(image_bytes, dtype=np.uint8)
        bgr = cv2.imdecode(buffer, cv2.IMREAD_COLOR)
        if bgr is None:
            return None
        return cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)

    @staticmethod
    def distance(probe: np.ndarray, candidate: np.ndarray) -> float:
        distances = face_recognition.face_distance([candidate], probe)
        return float(distances[0])

    @staticmethod
    def distance_to_confidence(distance: float, threshold: float) -> float:
        """Map Euclidean distance to a 0–1 confidence score (higher is better)."""
        if distance >= threshold:
            return 0.0
        return round(max(0.0, 1.0 - (distance / threshold)), 4)

    @staticmethod
    def landmarks_summary(landmarks: dict[str, list[tuple[int, int]]]) -> dict[str, Any]:
        return {region: len(points) for region, points in landmarks.items()}
