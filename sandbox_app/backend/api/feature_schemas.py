from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Body, HTTPException

from sandbox_app.backend.features.schema import (
    FeatureSchemaError,
    add_feature,
    build_schema_preview,
    create_feature_schema,
    delete_feature,
    delete_feature_schema,
    list_feature_schemas,
    load_feature_schema,
    rename_feature,
    update_feature_schema,
)

router = APIRouter(prefix="/api/feature-schemas", tags=["feature-schemas"])

JsonBody = Annotated[dict[str, Any], Body()]
RenameBody = Annotated[dict[str, str], Body()]


@router.get("")
def list_schemas() -> dict[str, Any]:
    return {
        "schemas": list_feature_schemas(),
    }


@router.get("/{profile_id}")
def get_schema(profile_id: str) -> dict[str, Any]:
    try:
        schema = load_feature_schema(profile_id)
    except FeatureSchemaError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error

    return {
        "schema": schema,
        "preview": build_schema_preview(schema),
    }


@router.post("")
def create_schema(schema: JsonBody) -> dict[str, Any]:
    try:
        created_schema = create_feature_schema(schema)
    except FeatureSchemaError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

    return {
        "schema": created_schema,
        "preview": build_schema_preview(created_schema),
    }


@router.put("/{profile_id}")
def update_schema(
    profile_id: str,
    schema: JsonBody,
) -> dict[str, Any]:
    try:
        updated_schema = update_feature_schema(profile_id, schema)
    except FeatureSchemaError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

    return {
        "schema": updated_schema,
        "preview": build_schema_preview(updated_schema),
    }


@router.delete("/{profile_id}")
def remove_schema(profile_id: str) -> dict[str, str]:
    try:
        delete_feature_schema(profile_id)
    except FeatureSchemaError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

    return {
        "status": "deleted",
        "profile_id": profile_id,
    }


@router.post("/{profile_id}/features/{group}")
def create_schema_feature(
    profile_id: str,
    group: str,
    feature: JsonBody,
) -> dict[str, Any]:
    try:
        schema = add_feature(profile_id, group, feature)
    except FeatureSchemaError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

    return {
        "schema": schema,
        "preview": build_schema_preview(schema),
    }


@router.patch("/{profile_id}/features/{group}/{feature_name}")
def rename_schema_feature(
    profile_id: str,
    group: str,
    feature_name: str,
    payload: RenameBody,
) -> dict[str, Any]:
    new_name = payload.get("new_name", "")

    try:
        schema = rename_feature(profile_id, group, feature_name, new_name)
    except FeatureSchemaError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

    return {
        "schema": schema,
        "preview": build_schema_preview(schema),
    }


@router.delete("/{profile_id}/features/{group}/{feature_name}")
def remove_schema_feature(
    profile_id: str,
    group: str,
    feature_name: str,
) -> dict[str, Any]:
    try:
        schema = delete_feature(profile_id, group, feature_name)
    except FeatureSchemaError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

    return {
        "schema": schema,
        "preview": build_schema_preview(schema),
    }