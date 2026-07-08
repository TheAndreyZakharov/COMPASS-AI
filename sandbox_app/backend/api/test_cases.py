from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from sandbox_app.backend.data_generation.test_team import (
    DEFAULT_GRADES,
    DEFAULT_PRIORITIES,
    DEFAULT_ROLES,
    DEFAULT_SKILLS,
    DEFAULT_TASK_TYPES,
    TestTeamConfig,
    TestTeamError,
    active_todo_tasks,
    build_test_case_summary,
    delete_test_case,
    generate_test_case,
    import_test_case,
    list_test_cases,
    load_test_case,
    load_test_case_table,
    recommendation_context,
)

router = APIRouter(prefix="/test-cases", tags=["test-cases"])


class GenerateTestCaseRequest(BaseModel):
    test_case_id: str | None = None
    domain_profile: str = "developers"
    people_count: int = Field(default=10, ge=1, le=1000)
    active_tasks_count: int = Field(default=16, ge=0, le=10000)
    history_depth: int = Field(default=8, ge=0, le=1000)
    seed: int | None = 21001
    roles: list[str] = Field(default_factory=lambda: DEFAULT_ROLES.copy())
    grades: list[str] = Field(default_factory=lambda: DEFAULT_GRADES.copy())
    skills: list[str] = Field(default_factory=lambda: DEFAULT_SKILLS.copy())
    task_types: list[str] = Field(default_factory=lambda: DEFAULT_TASK_TYPES.copy())
    priorities: list[str] = Field(default_factory=lambda: DEFAULT_PRIORITIES.copy())
    workload_min: float = Field(default=0.1, ge=0.0, le=1.0)
    workload_max: float = Field(default=0.85, ge=0.0, le=1.0)
    fatigue_min: float = Field(default=0.05, ge=0.0, le=1.0)
    fatigue_max: float = Field(default=0.8, ge=0.0, le=1.0)
    availability_min: float = Field(default=0.15, ge=0.0, le=1.0)
    availability_max: float = Field(default=1.0, ge=0.0, le=1.0)
    learning_goals_min: int = Field(default=1, ge=0, le=20)
    learning_goals_max: int = Field(default=3, ge=0, le=20)
    active_tasks_per_person_max: int = Field(default=4, ge=0, le=1000)
    overwrite: bool = False


class ImportTestCaseRequest(BaseModel):
    test_case_id: str
    team: list[dict[str, Any]] = Field(min_length=1)
    active_tasks: list[dict[str, Any]] = Field(default_factory=list)
    history: list[dict[str, Any]] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    overwrite: bool = False


def config_from_request(payload: GenerateTestCaseRequest) -> TestTeamConfig:
    return TestTeamConfig(
        test_case_id=payload.test_case_id,
        domain_profile=payload.domain_profile,
        people_count=payload.people_count,
        active_tasks_count=payload.active_tasks_count,
        history_depth=payload.history_depth,
        seed=payload.seed,
        roles=payload.roles,
        grades=payload.grades,
        skills=payload.skills,
        task_types=payload.task_types,
        priorities=payload.priorities,
        workload_min=payload.workload_min,
        workload_max=payload.workload_max,
        fatigue_min=payload.fatigue_min,
        fatigue_max=payload.fatigue_max,
        availability_min=payload.availability_min,
        availability_max=payload.availability_max,
        learning_goals_min=payload.learning_goals_min,
        learning_goals_max=payload.learning_goals_max,
        active_tasks_per_person_max=payload.active_tasks_per_person_max,
        overwrite=payload.overwrite,
    )


@router.get("")
def list_cases() -> dict[str, object]:
    try:
        return list_test_cases()
    except TestTeamError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/generate")
def generate_case(payload: GenerateTestCaseRequest) -> dict[str, object]:
    try:
        return generate_test_case(config_from_request(payload))
    except TestTeamError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/import")
def import_case(payload: ImportTestCaseRequest) -> dict[str, object]:
    try:
        return import_test_case(
            test_case_id=payload.test_case_id,
            team=payload.team,
            active_tasks=payload.active_tasks,
            history=payload.history,
            metadata=payload.metadata,
            overwrite=payload.overwrite,
        )
    except TestTeamError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/{test_case_id}")
def get_case(test_case_id: str) -> dict[str, object]:
    try:
        return load_test_case(test_case_id)
    except TestTeamError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/{test_case_id}/summary")
def get_case_summary(test_case_id: str) -> dict[str, object]:
    try:
        return build_test_case_summary(test_case_id)
    except TestTeamError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/{test_case_id}/tables/{table_name}")
def get_case_table(test_case_id: str, table_name: str) -> dict[str, object] | list[object]:
    try:
        table = load_test_case_table(test_case_id, table_name)
    except TestTeamError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    if isinstance(table, list):
        return table

    if isinstance(table, dict):
        return table

    raise HTTPException(status_code=400, detail="Unsupported table payload")


@router.get("/{test_case_id}/pending-tasks")
def get_pending_tasks(test_case_id: str) -> dict[str, object]:
    try:
        tasks = active_todo_tasks(test_case_id)
    except TestTeamError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return {
        "test_case_id": test_case_id,
        "tasks": tasks,
        "total": len(tasks),
    }


@router.get("/{test_case_id}/recommendation-context")
def get_recommendation_context(test_case_id: str) -> dict[str, object]:
    try:
        return recommendation_context(test_case_id)
    except TestTeamError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.delete("/{test_case_id}")
def delete_case(test_case_id: str) -> dict[str, object]:
    try:
        return delete_test_case(test_case_id)
    except TestTeamError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc