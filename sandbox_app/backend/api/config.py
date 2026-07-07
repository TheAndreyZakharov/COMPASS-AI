from __future__ import annotations

from typing import Any

from fastapi import APIRouter

from sandbox_app.backend.core.settings import public_app_settings

router = APIRouter(prefix="/api", tags=["config"])


@router.get("/config")
def config() -> dict[str, Any]:
    return public_app_settings()