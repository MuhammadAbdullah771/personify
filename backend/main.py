"""
Personify AI Face Matching Server
Run: uvicorn main:app --host 0.0.0.0 --port 8000 --reload
"""

from __future__ import annotations

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.search import router as search_router
from app.config import get_settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

settings = get_settings()

app = FastAPI(
    title="Personify AI Matching API",
    description="Local face recognition server for missing person identification.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(search_router)


@app.get("/health")
async def health_check() -> dict[str, str | bool]:
    configured = bool(settings.supabase_url and settings.supabase_key)
    return {
        "status": "ok",
        "service": "personify-matcher",
        "supabase_configured": configured,
        "hint": None
        if configured
        else "Set SUPABASE_URL and SUPABASE_KEY in backend/.env then restart Docker.",
    }


@app.on_event("shutdown")
async def shutdown_event() -> None:
    from app.api.routes.search import _matching_service  # noqa: PLC0415

    if _matching_service is not None:
        _matching_service.shutdown()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True,
    )
