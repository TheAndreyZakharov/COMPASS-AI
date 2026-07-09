from __future__ import annotations

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from sandbox_app.backend.inference.assignment_optimizer import ASSIGNMENT_MODES
from sandbox_app.backend.inference.bulk_assignment import (
    BulkAssignmentConfig,
    BulkAssignmentError,
    list_assignment_sessions,
    load_assignment_session,
    load_assignment_session_file,
    run_bulk_assignment,
)

router = APIRouter(prefix="/assignment-sessions", tags=["assignment-sessions"])


class BulkAssignmentRequest(BaseModel):
    session_id: str = Field(min_length=1)
    model_name: str = Field(min_length=1)
    test_case_id: str = Field(min_length=1)
    assignment_mode: str = "balanced"
    recommendation_mode: str = "balanced"
    top_k: int = Field(default=3, ge=1, le=100)
    max_workload_per_person: float = Field(default=0.95, gt=0.0, le=1.5)
    fairness_penalty: float = Field(default=0.12, ge=0.0, le=2.0)
    fatigue_penalty: float = Field(default=0.12, ge=0.0, le=2.0)
    learning_bonus: float = Field(default=0.08, ge=0.0, le=2.0)
    workload_penalty: float = Field(default=0.18, ge=0.0, le=2.0)
    task_statuses: list[str] = Field(default_factory=lambda: ["todo"])
    save_session: bool = True


def config_from_request(payload: BulkAssignmentRequest) -> BulkAssignmentConfig:
    return BulkAssignmentConfig(
        session_id=payload.session_id,
        model_name=payload.model_name,
        test_case_id=payload.test_case_id,
        assignment_mode=payload.assignment_mode,
        recommendation_mode=payload.recommendation_mode,
        top_k=payload.top_k,
        max_workload_per_person=payload.max_workload_per_person,
        fairness_penalty=payload.fairness_penalty,
        fatigue_penalty=payload.fatigue_penalty,
        learning_bonus=payload.learning_bonus,
        workload_penalty=payload.workload_penalty,
        task_statuses=payload.task_statuses,
        save_session=payload.save_session,
    )


@router.get("/modes")
def get_assignment_modes() -> dict[str, object]:
    return {
        "modes": ASSIGNMENT_MODES,
        "default": "balanced",
    }


@router.post("/run")
def run_assignment_session(payload: BulkAssignmentRequest) -> dict[str, object]:
    try:
        return run_bulk_assignment(config_from_request(payload))
    except BulkAssignmentError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("")
def list_sessions() -> dict[str, object]:
    try:
        return list_assignment_sessions()
    except BulkAssignmentError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/{assignment_session_id}")
def get_session(assignment_session_id: str) -> dict[str, object]:
    try:
        return load_assignment_session(assignment_session_id)
    except BulkAssignmentError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/{assignment_session_id}/files/{file_name}")
def get_session_file(
    assignment_session_id: str,
    file_name: str,
) -> FileResponse:
    try:
        path = load_assignment_session_file(assignment_session_id, file_name)
    except BulkAssignmentError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return FileResponse(path)