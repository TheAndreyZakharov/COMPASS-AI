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
from sandbox_app.backend.api.data_viewer import (
    DataViewerError,
    parse_jsonish,
    read_table,
    resolve_dataset_dir,
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


class TestCaseFromDatasetRequest(BaseModel):
    dataset_id: str = Field(min_length=3, max_length=81)
    dataset_kind: str = "generated"
    test_case_id: str | None = None
    task_statuses: list[str] = Field(default_factory=lambda: ["todo", "in_progress", "review", "blocked"])
    overwrite: bool = True


def string_value(value: Any, fallback: str = "") -> str:
    text = str(value or "").strip()
    return text or fallback


def float_value(value: Any, fallback: float = 0.0) -> float:
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return fallback

    if numeric != numeric:
        return fallback

    return numeric


def bool_value(value: Any) -> bool:
    if isinstance(value, bool):
        return value

    return str(value or "").strip().lower() in {"1", "true", "yes", "y", "да"}


def list_value(value: Any) -> list[str]:
    parsed = parse_jsonish(value)

    if isinstance(parsed, list):
        return [str(item).strip() for item in parsed if str(item).strip()]

    if isinstance(parsed, tuple):
        return [str(item).strip() for item in parsed if str(item).strip()]

    text = str(parsed or "").strip()
    if not text:
        return []

    return [item.strip() for item in text.split(",") if item.strip()]


def dict_value(value: Any) -> dict[str, Any]:
    parsed = parse_jsonish(value)
    return parsed if isinstance(parsed, dict) else {}


def normalize_dataset_employee(row: dict[str, Any], index: int) -> dict[str, Any]:
    employee_id = string_value(row.get("employee_id"), f"employee_{index + 1:04d}")

    return {
        **row,
        "employee_id": employee_id,
        "name": string_value(row.get("name"), employee_id),
        "role": string_value(
            row.get("role") or row.get("position") or row.get("specialization"),
            "employee",
        ),
        "grade": string_value(
            row.get("grade") or row.get("level") or row.get("seniority"),
            "unknown",
        ),
        "skills": list_value(row.get("skills") or row.get("tags")),
        "learning_goals": list_value(row.get("learning_goals")),
        "current_workload": float_value(row.get("current_workload"), 0.0),
        "fatigue_score": float_value(row.get("fatigue_score"), 0.0),
        "availability_score": float_value(row.get("availability_score"), 1.0),
        "avg_completion_speed": float_value(row.get("avg_completion_speed"), 0.5),
        "avg_quality_score": float_value(row.get("avg_quality_score"), 0.5),
        "deadline_reliability": float_value(row.get("deadline_reliability"), 0.5),
        "active_task_ids": list_value(row.get("active_task_ids")),
    }


def normalize_dataset_task(row: dict[str, Any], index: int) -> dict[str, Any]:
    task_id = string_value(row.get("task_id"), f"task_{index + 1:06d}")

    return {
        **row,
        "task_id": task_id,
        "title": string_value(row.get("title") or row.get("name"), task_id),
        "status": string_value(row.get("status"), "todo").lower(),
        "priority": string_value(row.get("priority"), "medium").lower(),
        "task_type": string_value(row.get("task_type") or row.get("type"), "task"),
        "project_id": string_value(row.get("project_id"), "project_001"),
        "complexity": float_value(row.get("complexity"), 0.5),
        "estimated_hours": float_value(row.get("estimated_hours"), 8.0),
        "required_skills": list_value(row.get("required_skills") or row.get("skills")),
        "dependencies": list_value(row.get("dependencies")),
        "custom_features": dict_value(row.get("custom_features")),
    }


def normalize_dataset_history(row: dict[str, Any], index: int) -> dict[str, Any]:
    history_id = string_value(
        row.get("history_id") or row.get("assignment_id"),
        f"history_{index + 1:08d}",
    )

    return {
        **row,
        "history_id": history_id,
        "employee_id": string_value(row.get("employee_id")),
        "task_id": string_value(row.get("task_id"), f"history_task_{index + 1:08d}"),
        "task_type": string_value(row.get("task_type") or row.get("type"), "task"),
        "required_skills": list_value(row.get("required_skills") or row.get("skills")),
        "planned_hours": float_value(row.get("planned_hours"), 0.0),
        "actual_hours": float_value(row.get("actual_hours"), 0.0),
        "quality_score": float_value(row.get("quality_score"), 0.0),
        "deadline_status": string_value(row.get("deadline_status"), "unknown"),
        "outcome_label": string_value(
            row.get("outcome_label") or row.get("outcome") or row.get("status"),
            "unknown",
        ),
        "was_rework_needed": bool_value(row.get("was_rework_needed")),
        "feedback_score": float_value(row.get("feedback_score"), 0.0),
        "custom_outcome_features": dict_value(row.get("custom_outcome_features")),
    }


def attach_active_task_ids_to_team(
    team: list[dict[str, Any]],
    active_tasks: list[dict[str, Any]],
) -> None:
    by_employee_id = {
        str(employee.get("employee_id")): employee
        for employee in team
        if employee.get("employee_id")
    }

    for task in active_tasks:
        employee_id = string_value(task.get("assigned_employee_id"))
        if not employee_id or employee_id not in by_employee_id:
            continue

        active_task_ids = by_employee_id[employee_id].setdefault("active_task_ids", [])
        if isinstance(active_task_ids, list):
            active_task_ids.append(task.get("task_id"))


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


@router.post("/from-dataset")
def create_case_from_dataset(payload: TestCaseFromDatasetRequest) -> dict[str, object]:
    try:
        _, dataset_dir = resolve_dataset_dir(payload.dataset_id, payload.dataset_kind)
        team, _, _ = read_table(dataset_dir, "employees")
        tasks, _, _ = read_table(dataset_dir, "tasks")

        try:
            history, _, _ = read_table(dataset_dir, "assignment_history")
        except DataViewerError:
            history = []

        allowed_statuses = {
            str(status).lower().strip()
            for status in payload.task_statuses
            if str(status).lower().strip()
        }
        team = [
            normalize_dataset_employee(employee, index)
            for index, employee in enumerate(team)
        ]
        active_tasks = [
            normalize_dataset_task(task, index)
            for index, task in enumerate(tasks)
            if str(task.get("status", "todo")).lower() in allowed_statuses
        ]
        history = [
            normalize_dataset_history(item, index)
            for index, item in enumerate(history)
        ]
        attach_active_task_ids_to_team(team, active_tasks)

        test_case_id = payload.test_case_id or f"{payload.dataset_id}_case"
        return import_test_case(
            test_case_id=test_case_id,
            team=team,
            active_tasks=active_tasks,
            history=history,
            metadata={
                "source": "dataset",
                "dataset_id": payload.dataset_id,
                "dataset_kind": payload.dataset_kind,
                "task_statuses": sorted(allowed_statuses),
            },
            overwrite=payload.overwrite,
        )
    except (TestTeamError, DataViewerError) as exc:
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
