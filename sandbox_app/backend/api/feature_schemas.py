from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException
from sandbox_app.backend.features.schema import (
    FeatureSchemaError,
    add_feature,
    build_profile_template,
    create_feature_schema,
    delete_feature,
    delete_feature_schema,
    list_schema_previews,
    load_all_feature_schemas,
    load_feature_schema,
    patch_feature,
    schema_preview,
    update_feature_schema,
)
from sandbox_app.backend.utils.json_io import JsonFileError

router = APIRouter(prefix="/feature-schemas", tags=["feature-schemas"])


def feature_schema_http_error(exc: Exception, not_found: bool = False) -> HTTPException:
    if not_found:
        return HTTPException(status_code=404, detail=str(exc))
    return HTTPException(status_code=400, detail=str(exc))


@router.get("")
def list_feature_schemas(preview: bool = False) -> dict[str, Any]:
    try:
        if preview:
            items = list_schema_previews()
            return {"items": items, "count": len(items), "preview": True}

        items = load_all_feature_schemas()
        return {
            "items": items,
            "count": len(items),
            "preview": False,
        }
    except (FeatureSchemaError, JsonFileError) as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/template")
def get_feature_schema_template(
    profile_id: str = "custom_domain",
    name: str | None = None,
) -> dict[str, Any]:
    try:
        template = build_profile_template(profile_id=profile_id, name=name)
        return {
            "template": template,
            "preview": schema_preview(template),
        }
    except FeatureSchemaError as exc:
        raise feature_schema_http_error(exc) from exc


@router.get("/{profile_id}")
def get_feature_schema(profile_id: str, preview: bool = False) -> dict[str, Any]:
    try:
        schema = load_feature_schema(profile_id)
        return {
            "schema": schema,
            "preview": schema_preview(schema) if preview else None,
        }
    except FeatureSchemaError as exc:
        raise feature_schema_http_error(exc, not_found=True) from exc
    except JsonFileError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("")
def create_schema(payload: dict[str, Any]) -> dict[str, Any]:
    try:
        schema = create_feature_schema(payload)
        return {
            "schema": schema,
            "preview": schema_preview(schema),
        }
    except FeatureSchemaError as exc:
        raise feature_schema_http_error(exc) from exc
    except JsonFileError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.put("/{profile_id}")
def update_schema(profile_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    try:
        schema = update_feature_schema(profile_id, payload)
        return {
            "schema": schema,
            "preview": schema_preview(schema),
        }
    except FeatureSchemaError as exc:
        raise feature_schema_http_error(exc) from exc
    except JsonFileError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.delete("/{profile_id}")
def delete_schema(profile_id: str) -> dict[str, Any]:
    try:
        delete_feature_schema(profile_id)
        return {
            "deleted": True,
            "profile_id": profile_id,
        }
    except FeatureSchemaError as exc:
        raise feature_schema_http_error(exc) from exc
    except JsonFileError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/{profile_id}/features/{group}")
def add_schema_feature(profile_id: str, group: str, payload: dict[str, Any]) -> dict[str, Any]:
    try:
        schema = add_feature(profile_id, group, payload)
        return {
            "schema": schema,
            "preview": schema_preview(schema),
        }
    except FeatureSchemaError as exc:
        raise feature_schema_http_error(exc) from exc
    except JsonFileError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.patch("/{profile_id}/features/{group}/{feature_name}")
def patch_schema_feature(
    profile_id: str,
    group: str,
    feature_name: str,
    payload: dict[str, Any],
) -> dict[str, Any]:
    try:
        schema = patch_feature(profile_id, group, feature_name, payload)
        return {
            "schema": schema,
            "preview": schema_preview(schema),
        }
    except FeatureSchemaError as exc:
        raise feature_schema_http_error(exc) from exc
    except JsonFileError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.delete("/{profile_id}/features/{group}/{feature_name}")
def delete_schema_feature(profile_id: str, group: str, feature_name: str) -> dict[str, Any]:
    try:
        schema = delete_feature(profile_id, group, feature_name)
        return {
            "schema": schema,
            "preview": schema_preview(schema),
        }
    except FeatureSchemaError as exc:
        raise feature_schema_http_error(exc) from exc
    except JsonFileError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc