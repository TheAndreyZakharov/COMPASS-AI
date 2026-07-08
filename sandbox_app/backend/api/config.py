from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException
from sandbox_app.backend.core.paths import PATHS
from sandbox_app.backend.core.settings import load_model_presets, load_settings
from sandbox_app.backend.utils.json_io import JsonFileError, read_json

router = APIRouter(prefix="/config", tags=["config"])


def _load_feature_schemas() -> dict[str, Any]:
    schemas: dict[str, Any] = {}

    for schema_path in sorted(PATHS.feature_schemas_dir.glob("*.json")):
        schema = read_json(schema_path)
        profile_id = schema.get("profile_id") if isinstance(schema, dict) else None
        if not profile_id:
            raise JsonFileError(f"Feature schema without profile_id: {schema_path}")
        schemas[str(profile_id)] = schema

    return schemas


@router.get("")
def get_config() -> dict[str, Any]:
    try:
        return {
            "settings": load_settings(),
            "model_presets": load_model_presets(),
            "feature_schemas": _load_feature_schemas(),
        }
    except JsonFileError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/settings")
def get_settings() -> dict[str, Any]:
    return load_settings()


@router.get("/model-presets")
def get_model_presets() -> dict[str, Any]:
    return load_model_presets()


@router.get("/feature-schemas")
def get_feature_schemas() -> dict[str, Any]:
    try:
        return {
            "items": list(_load_feature_schemas().values()),
            "count": len(_load_feature_schemas()),
        }
    except JsonFileError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc