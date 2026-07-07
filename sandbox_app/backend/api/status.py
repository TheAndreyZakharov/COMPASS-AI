from __future__ import annotations

import platform
import urllib.error
import urllib.request
from typing import Any

from fastapi import APIRouter

from sandbox_app.backend.core.settings import load_app_settings

router = APIRouter(prefix="/api", tags=["status"])


def _ollama_available() -> bool:
    settings = load_app_settings()
    base_url = settings.get("ollama", {}).get("base_url", "http://localhost:11434")
    url = f"{base_url.rstrip('/')}/api/tags"

    try:
        with urllib.request.urlopen(url, timeout=1.5) as response:
            return 200 <= response.status < 500
    except (OSError, urllib.error.URLError):
        return False


@router.get("/health")
def health() -> dict[str, Any]:
    settings = load_app_settings()

    return {
        "app": settings.get("app_name", "COMPASS AI Sandbox"),
        "version": settings.get("app_version", "0.1.0"),
        "status": "ok",
        "local_mode": bool(settings.get("local_mode", True)),
    }


@router.get("/status")
def status() -> dict[str, Any]:
    payload = health()
    payload.update(
        {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "ollama_available": _ollama_available(),
        },
    )
    return payload