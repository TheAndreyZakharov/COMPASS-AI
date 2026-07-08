from __future__ import annotations

from fastapi import APIRouter, HTTPException, Response
from sandbox_app.backend.reports.training_report import (
    TrainingReportError,
    generate_training_report,
    list_training_reports,
    read_training_report,
    read_training_report_html,
)

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/training")
def get_training_reports() -> dict[str, object]:
    return list_training_reports()


@router.post("/training/{session_id}/generate")
def generate_report(session_id: str) -> dict[str, object]:
    try:
        return generate_training_report(session_id)
    except TrainingReportError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/training/{session_id}")
def get_training_report(session_id: str) -> dict[str, object]:
    try:
        return read_training_report(session_id)
    except TrainingReportError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/training/{session_id}/html")
def get_training_report_html(session_id: str) -> Response:
    try:
        html_text = read_training_report_html(session_id)
    except TrainingReportError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return Response(content=html_text, media_type="text/html")