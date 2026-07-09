from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from sandbox_app.backend.inference.recommend import (
    RECOMMENDATION_MODES,
    RecommendationConfig,
    RecommendationError,
    list_recommendable_tasks,
    list_recommendations,
    load_recommendation,
    recommend_single_task,
)

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


class SingleRecommendationRequest(BaseModel):
    session_id: str = Field(min_length=1)
    model_name: str = Field(min_length=1)
    test_case_id: str = Field(min_length=1)
    task_id: str = Field(min_length=1)
    recommendation_mode: str = "balanced"
    top_k: int = Field(default=3, ge=1, le=100)
    candidate_employee_ids: list[str] = Field(default_factory=list)
    save_result: bool = True


def config_from_request(payload: SingleRecommendationRequest) -> RecommendationConfig:
    return RecommendationConfig(
        session_id=payload.session_id,
        model_name=payload.model_name,
        test_case_id=payload.test_case_id,
        task_id=payload.task_id,
        recommendation_mode=payload.recommendation_mode,
        top_k=payload.top_k,
        candidate_employee_ids=payload.candidate_employee_ids,
        save_result=payload.save_result,
    )


@router.get("/modes")
def get_recommendation_modes() -> dict[str, object]:
    return {
        "modes": RECOMMENDATION_MODES,
        "default": "balanced",
    }


@router.get("/test-cases/{test_case_id}/tasks")
def get_recommendable_tasks(test_case_id: str) -> dict[str, object]:
    try:
        return list_recommendable_tasks(test_case_id)
    except RecommendationError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/single")
def single_recommendation(payload: SingleRecommendationRequest) -> dict[str, object]:
    try:
        return recommend_single_task(config_from_request(payload))
    except RecommendationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/test-cases/{test_case_id}")
def get_saved_recommendations(test_case_id: str) -> dict[str, object]:
    try:
        return list_recommendations(test_case_id)
    except RecommendationError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/test-cases/{test_case_id}/{recommendation_id}")
def get_saved_recommendation(
    test_case_id: str,
    recommendation_id: str,
) -> dict[str, object]:
    try:
        return load_recommendation(test_case_id, recommendation_id)
    except RecommendationError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc