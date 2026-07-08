from __future__ import annotations

from functools import lru_cache
from typing import Any

from sandbox_app.backend.core.paths import PATHS
from sandbox_app.backend.utils.json_io import read_json


class SettingsError(RuntimeError):
    """Raised when sandbox settings are missing or invalid."""


REQUIRED_APP_KEYS = {"name", "slug", "version", "environment", "target_python", "host", "port"}


def _validate_settings(settings: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(settings, dict):
        raise SettingsError("app_settings.json must contain a JSON object")

    app = settings.get("app")
    if not isinstance(app, dict):
        raise SettingsError("app_settings.json must contain app object")

    missing = sorted(REQUIRED_APP_KEYS - set(app))
    if missing:
        raise SettingsError(f"app_settings.json missing app keys: {', '.join(missing)}")

    if app["host"] != "127.0.0.1":
        raise SettingsError("Sandbox backend must bind to 127.0.0.1 only")

    if int(app["port"]) != 8601:
        raise SettingsError("Sandbox backend must use port 8601")

    isolation = settings.get("isolation", {})
    if not isinstance(isolation, dict):
        raise SettingsError("app_settings.json isolation must be an object")

    for key in (
        "autonomous_subproject",
        "do_not_import_main_src",
        "do_not_import_main_llm",
        "do_not_import_main_agents",
        "do_not_modify_main_compass_api",
    ):
        if isolation.get(key) is not True:
            raise SettingsError(f"app_settings.json isolation.{key} must be true")

    return settings


@lru_cache(maxsize=1)
def load_settings() -> dict[str, Any]:
    return _validate_settings(read_json(PATHS.app_settings_path))


@lru_cache(maxsize=1)
def load_model_presets() -> dict[str, Any]:
    presets = read_json(PATHS.model_presets_path)
    if not isinstance(presets, dict):
        raise SettingsError("model_presets.json must contain a JSON object")
    if "models" not in presets:
        raise SettingsError("model_presets.json must contain models")
    return presets


def reload_settings_cache() -> None:
    load_settings.cache_clear()
    load_model_presets.cache_clear()