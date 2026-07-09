from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from sandbox_app.backend.inference.bulk_assignment import (
    BulkAssignmentError,
    load_assignment_session,
)
from sandbox_app.backend.llm.ollama_client import OllamaClient
from sandbox_app.backend.llm.qwen_explainer import (
    ExplanationError,
    explain_assignment_session,
    explain_recommendation,
)

router = APIRouter(prefix="/llm", tags=["llm"])


class RecommendationExplanationRequest(BaseModel):
    recommendation: dict[str, object] = Field(default_factory=dict)
    use_llm: bool = True


class AssignmentExplanationRequest(BaseModel):
    assignment_session: dict[str, object] = Field(default_factory=dict)
    use_llm: bool = True


@router.get("/status")
def get_llm_status() -> dict[str, object]:
    return OllamaClient().health()


@router.post("/explain/recommendation")
def explain_recommendation_payload(
    payload: RecommendationExplanationRequest,
) -> dict[str, object]:
    try:
        return explain_recommendation(
            recommendation=payload.recommendation,
            use_llm=payload.use_llm,
        )
    except ExplanationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/explain/assignment")
def explain_assignment_payload(
    payload: AssignmentExplanationRequest,
) -> dict[str, object]:
    try:
        return explain_assignment_session(
            assignment_session=payload.assignment_session,
            use_llm=payload.use_llm,
        )
    except ExplanationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/explain/assignment-sessions/{assignment_session_id}")
def explain_saved_assignment_session(
    assignment_session_id: str,
    use_llm: bool = True,
) -> dict[str, object]:
    try:
        session = load_assignment_session(assignment_session_id)
        return explain_assignment_session(
            assignment_session=session,
            use_llm=use_llm,
        )
    except (BulkAssignmentError, ExplanationError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc