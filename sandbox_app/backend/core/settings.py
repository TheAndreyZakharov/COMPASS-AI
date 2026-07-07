from __future__ import annotations

from typing import Any

from sandbox_app.backend.core.paths import APP_SETTINGS_PATH
from sandbox_app.backend.utils.json_io import read_json


def load_app_settings() -> dict[str, Any]:
    return read_json(APP_SETTINGS_PATH)


def public_app_settings() -> dict[str, Any]:
    settings = load_app_settings()

    public_settings = dict(settings)
    ollama = dict(public_settings.get("ollama", {}))

    if "api_key" in ollama:
        ollama["api_key"] = "***"

    public_settings["ollama"] = ollama

    return public_settings