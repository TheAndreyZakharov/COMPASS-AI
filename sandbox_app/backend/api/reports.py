from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from sandbox_app.backend.reports.training_report import (
    generate_training_report,
    list_training_reports,
    read_training_report,
    read_training_report_html,
)
from sandbox_app.backend.training.train_session import TRAINING_SESSIONS_DIR

router = APIRouter(prefix="/reports", tags=["reports"])


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