from __future__ import annotations

import json
import shutil
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from sandbox_app.backend.core.paths import PATHS
from sandbox_app.backend.training.export_models import (
    ModelExportConfig,
    ModelExportError,
    export_and_validate_model,
    list_models_for_api,
    predict_with_saved_model,
    read_export_validation,
    read_model_metadata,
)

router = APIRouter(prefix="/models", tags=["models"])


class ExportModelRequest(BaseModel):
    export_onnx: bool = False
    sample_size: int = Field(default=100, ge=1, le=10000)


class PredictRequest(BaseModel):
    records: list[dict[str, Any]] = Field(min_length=1, max_length=1000)


def delete_model_artifact_dir(session_id: str, model_name: str) -> dict[str, object]:
    models_root = (PATHS.training_sessions_dir / session_id / "models").resolve()
    target = (PATHS.training_sessions_dir / session_id / "models" / model_name).resolve()

    if not target.exists() or not target.is_dir():
        raise ModelExportError(f"Model artifact not found: {session_id}/{model_name}")

    if target == models_root or models_root not in target.parents:
        raise ModelExportError("Refusing to delete path outside model artifacts root")

    shutil.rmtree(target)

    summary_path = PATHS.training_sessions_dir / session_id / "session_summary.json"
    if summary_path.exists():
        try:
            summary = json.loads(summary_path.read_text(encoding="utf-8"))
            for key in ("trained_models", "failed_models"):
                if isinstance(summary.get(key), list):
                    summary[key] = [item for item in summary[key] if item != model_name]
            summary_path.write_text(
                json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
        except (OSError, json.JSONDecodeError):
            pass

    return {
        "deleted": True,
        "session_id": session_id,
        "model_name": model_name,
        "path": str(target),
    }


@router.get("")
def list_models() -> dict[str, object]:
    return list_models_for_api()


@router.get("/{session_id}/{model_name}")
def get_model_metadata(session_id: str, model_name: str) -> dict[str, object]:
    try:
        return read_model_metadata(session_id, model_name)
    except ModelExportError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/{session_id}/{model_name}/validation")
def get_model_validation(session_id: str, model_name: str) -> dict[str, object]:
    try:
        return read_export_validation(session_id, model_name)
    except ModelExportError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/{session_id}/{model_name}/export")
def export_model(
    session_id: str,
    model_name: str,
    payload: ExportModelRequest,
) -> dict[str, object]:
    try:
        return export_and_validate_model(
            ModelExportConfig(
                session_id=session_id,
                model_name=model_name,
                export_onnx=payload.export_onnx,
                sample_size=payload.sample_size,
            )
        )
    except ModelExportError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/{session_id}/{model_name}/validate")
def validate_model(
    session_id: str,
    model_name: str,
    payload: ExportModelRequest,
) -> dict[str, object]:
    try:
        return export_and_validate_model(
            ModelExportConfig(
                session_id=session_id,
                model_name=model_name,
                export_onnx=False,
                sample_size=payload.sample_size,
            )
        )
    except ModelExportError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/{session_id}/{model_name}/predict")
def predict_model(
    session_id: str,
    model_name: str,
    payload: PredictRequest,
) -> dict[str, object]:
    try:
        return predict_with_saved_model(
            session_id=session_id,
            model_name=model_name,
            records=payload.records,
        )
    except ModelExportError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.delete("/{session_id}/{model_name}")
def delete_model_artifact(session_id: str, model_name: str) -> dict[str, object]:
    try:
        return delete_model_artifact_dir(session_id, model_name)
    except ModelExportError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
