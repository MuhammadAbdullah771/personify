import asyncio
import logging

from fastapi import APIRouter, File, UploadFile
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.services.matching_service import MatchingService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["search"])

_matching_service: MatchingService | None = None


def get_matching_service() -> MatchingService:
    global _matching_service  # noqa: PLW0603
    if _matching_service is None:
        _matching_service = MatchingService(get_settings())
    return _matching_service


@router.post("/search-missing")
async def search_missing(image: UploadFile = File(...)) -> JSONResponse:
    """
  Accepts multipart field `image` from the Flutter client.
  Returns match JSON or structured errors.
  """
    try:
        if not image.content_type or not image.content_type.startswith("image/"):
            return JSONResponse(
                status_code=400,
                content={
                    "status": "error",
                    "message": "Uploaded file must be an image (JPEG/PNG/WebP).",
                },
            )

        probe_bytes = await image.read()
        if not probe_bytes:
            return JSONResponse(
                status_code=400,
                content={"status": "error", "message": "Empty image upload."},
            )

        service = get_matching_service()
        result = await asyncio.to_thread(service.find_match, probe_bytes)

        if result.get("status") == "error":
            return JSONResponse(status_code=400, content=result)

        return JSONResponse(status_code=200, content=result)
    except ValueError as exc:
        logger.exception("Configuration error")
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(exc)},
        )
    except Exception as exc:  # noqa: BLE001
        logger.exception("Search failed")
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": f"Internal server error during face matching: {exc}",
            },
        )
