from __future__ import annotations

import shutil
from typing import Any

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.responses import FileResponse as ExportFileResponse
from pydantic import BaseModel as ExportBaseModel
from sandbox_app.backend.core.paths import PATHS
from sandbox_app.backend.reports.assignment_report import generate_assignment_report
from sandbox_app.backend.reports.dataset_report import generate_dataset_report
from sandbox_app.backend.reports.html_export import (
    ExportError,
    list_export_reports,
    read_json,
    safe_report_file,
)
from sandbox_app.backend.reports.model_report import generate_model_report
from sandbox_app.backend.reports.training_report import (
    generate_training_report,
    list_training_reports,
    read_training_report,
    read_training_report_html,
)
from sandbox_app.backend.training.train_session import TRAINING_SESSIONS_DIR

router = APIRouter(prefix="/reports", tags=["reports"])


def delete_export_report_dirs(report_id: str) -> dict[str, object]:
    deleted_paths: list[str] = []

    for root in (PATHS.reports_dir, PATHS.exports_dir):
        target = (root / report_id).resolve()
        safe_root = root.resolve()
        if target.exists():
            if not target.is_dir() or target == safe_root or safe_root not in target.parents:
                raise ExportError("Refusing to delete path outside reports roots")
            shutil.rmtree(target)
            deleted_paths.append(str(target))

    if not deleted_paths:
        raise ExportError(f"Report export not found: {report_id}")

    return {
        "deleted": True,
        "report_id": report_id,
        "paths": deleted_paths,
    }


def normalize_training_manifest(session_id: str, manifest: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(manifest)
    session_dir = TRAINING_SESSIONS_DIR / session_id
    reports_dir = session_dir / "reports"

    manifest_path = normalized.get("manifest_path")
    if not manifest_path:
        manifest_path = normalized.get("report_manifest_path")

    if not manifest_path:
        candidate_path = reports_dir / "report_manifest.json"
        if candidate_path.exists():
            manifest_path = str(candidate_path)

    html_path = normalized.get("html_path")
    if not html_path:
        html_path = normalized.get("report_path")

    if not html_path:
        candidate_path = reports_dir / "training_report.html"
        if candidate_path.exists():
            html_path = str(candidate_path)

    normalized["session_id"] = session_id
    normalized["manifest_path"] = str(manifest_path or "")
    normalized["html_path"] = str(html_path or "")
    normalized["reports_dir"] = str(reports_dir)

    return normalized


@router.get("/training")
def get_training_reports() -> dict[str, object]:
    return list_training_reports()


@router.post("/training/{session_id}/generate")
def create_training_report(session_id: str) -> dict[str, object]:
    try:
        manifest = generate_training_report(session_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return normalize_training_manifest(session_id, manifest)


@router.get("/training/{session_id}")
def get_training_report(session_id: str) -> dict[str, object]:
    try:
        manifest = read_training_report(session_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return normalize_training_manifest(session_id, manifest)


@router.get("/training/{session_id}/html")
def get_training_report_html(session_id: str) -> HTMLResponse:
    try:
        html = read_training_report_html(session_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return HTMLResponse(content=html)


@router.get("/training/{session_id}/files/{relative_path:path}")
def get_training_report_file(session_id: str, relative_path: str) -> FileResponse:
    session_dir = TRAINING_SESSIONS_DIR / session_id
    reports_dir = session_dir / "reports"

    if not reports_dir.exists():
        raise HTTPException(status_code=404, detail="Training report was not generated")

    requested_path = (reports_dir / relative_path).resolve()
    reports_root = reports_dir.resolve()

    if requested_path != reports_root and reports_root not in requested_path.parents:
        raise HTTPException(status_code=400, detail="Invalid report file path")

    if not requested_path.exists() or not requested_path.is_file():
        raise HTTPException(status_code=404, detail="Report file not found")

    return FileResponse(requested_path)




class DatasetExportRequest(ExportBaseModel):
    dataset_kind: str | None = None


@router.get("/exports")
def list_reports_exports() -> dict[str, object]:
    return {
        "reports": list_export_reports(),
    }


@router.get("/exports/{report_id}")
def get_reports_export(report_id: str) -> dict[str, object]:
    try:
        manifest_path = safe_report_file(report_id, "report_manifest.json")
        report_path = safe_report_file(report_id, "report.json")
    except ExportError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return {
        "manifest": read_json(manifest_path, default={}),
        "report": read_json(report_path, default={}),
    }


@router.get("/exports/{report_id}/files/{file_name}")
def get_reports_export_file(report_id: str, file_name: str) -> ExportFileResponse:
    try:
        path = safe_report_file(report_id, file_name)
    except ExportError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return ExportFileResponse(path)


@router.delete("/exports/{report_id}")
def delete_reports_export(report_id: str) -> dict[str, object]:
    try:
        return delete_export_report_dirs(report_id)
    except ExportError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/exports/datasets/{dataset_id}")
def create_dataset_export(
    dataset_id: str,
    payload: DatasetExportRequest,
) -> dict[str, object]:
    try:
        return generate_dataset_report(
            dataset_id=dataset_id,
            dataset_kind=payload.dataset_kind,
        )
    except ExportError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/exports/dataset/{dataset_id}")
def create_dataset_export_alias(
    dataset_id: str,
    payload: DatasetExportRequest,
) -> dict[str, object]:
    return create_dataset_export(dataset_id=dataset_id, payload=payload)


@router.post("/exports/models/{session_id}")
def create_model_export(session_id: str) -> dict[str, object]:
    try:
        return generate_model_report(session_id=session_id)
    except ExportError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/exports/model/{session_id}")
def create_model_export_alias(session_id: str) -> dict[str, object]:
    return create_model_export(session_id=session_id)


@router.post("/exports/assignments/{assignment_session_id}")
def create_assignment_export(assignment_session_id: str) -> dict[str, object]:
    try:
        return generate_assignment_report(
            assignment_session_id=assignment_session_id,
        )
    except ExportError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/exports/assignment/{assignment_session_id}")
def create_assignment_export_alias(assignment_session_id: str) -> dict[str, object]:
    return create_assignment_export(assignment_session_id=assignment_session_id)
