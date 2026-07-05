from __future__ import annotations

from typing import Any

from src.agents.state import AgentState
from src.models.inference import score_task_candidates
from src.recommendation.rule_based_ranker import (
    rank_employees_for_task,
    recommendation_to_dict,
)

PLANE_EMPLOYEE_SOURCES = {
    "plane_project_member",
    "plane_workspace_member",
}


def _employee_value(employee: dict[str, Any], key: str) -> str:
    value = employee.get(key)

    if value is None:
        return ""

    return str(value).strip()


def _has_plane_scoped_employees(state: AgentState) -> bool:
    if not state.employees:
        return False

    for employee in state.employees:
        if not isinstance(employee, dict):
            continue

        source = _employee_value(employee, "source")
        mapping_status = _employee_value(employee, "mapping_status")
        plane_user_id = _employee_value(employee, "plane_user_id")

        if source in PLANE_EMPLOYEE_SOURCES:
            return True

        if mapping_status == "plane_unmapped" and plane_user_id:
            return True

    return False


def _ml_candidates_available(state: AgentState) -> bool:
    if _has_plane_scoped_employees(state):
        return False

    task_features = state.task_features or {}
    task_id = str(task_features.get("task_id", ""))

    return task_id.startswith("TASK-")


def _run_ml_matching(state: AgentState, top_k: int) -> list[dict[str, Any]]:
    task_id = str(state.task_features["task_id"])

    return score_task_candidates(
        task_id=task_id,
        mode=state.recommendation_mode,
        top_k=top_k,
    )


def _run_rule_based_fallback(state: AgentState, top_k: int) -> list[dict[str, Any]]:
    recommendation = rank_employees_for_task(
        task=state.task_features,
        employees=state.employees,
        mode=state.recommendation_mode,
        top_k=top_k,
    )
    payload = recommendation_to_dict(recommendation)

    candidates: list[dict[str, Any]] = []

    for candidate in payload["candidates"]:
        candidate = dict(candidate)
        candidate["success_probability"] = candidate["score"]

        if _has_plane_scoped_employees(state):
            candidate["source"] = "plane_scoped_rule_based"
        else:
            candidate["source"] = "rule_based_fallback"

        candidates.append(candidate)

    return candidates


def _filter_plane_scoped_candidates(
    state: AgentState,
    candidates: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    if not _has_plane_scoped_employees(state):
        return candidates

    allowed_plane_user_ids = {
        _employee_value(employee, "plane_user_id")
        for employee in state.employees
        if isinstance(employee, dict)
    }
    allowed_plane_user_ids = {value for value in allowed_plane_user_ids if value}

    allowed_employee_ids = {
        _employee_value(employee, "employee_id")
        for employee in state.employees
        if isinstance(employee, dict)
    }
    allowed_employee_ids = {value for value in allowed_employee_ids if value}

    filtered_candidates: list[dict[str, Any]] = []

    for candidate in candidates:
        plane_user_id = _employee_value(candidate, "plane_user_id")
        employee_id = _employee_value(candidate, "employee_id")

        if plane_user_id and plane_user_id in allowed_plane_user_ids:
            filtered_candidates.append(candidate)
            continue

        if employee_id and employee_id in allowed_employee_ids:
            filtered_candidates.append(candidate)

    return filtered_candidates


def run_matching_agent(state: AgentState, top_k: int = 3) -> AgentState:
    if not state.task_features:
        state.add_error("matching_agent", "Task features are empty.")
        return state

    if not state.employees:
        state.add_error("matching_agent", "Employee list is empty.")
        return state

    try:
        if _ml_candidates_available(state):
            candidates = _run_ml_matching(state, top_k=top_k)
        else:
            candidates = _run_rule_based_fallback(state, top_k=top_k)

        candidates = _filter_plane_scoped_candidates(state, candidates)
        state.candidate_scores = candidates
        state.top_candidates = candidates[:top_k]

        if _has_plane_scoped_employees(state) and not state.top_candidates:
            state.add_error(
                "matching_agent",
                "Plane scoped matching returned no valid project members.",
            )

    except Exception as error:
        state.add_error("matching_agent", str(error))

        try:
            candidates = _run_rule_based_fallback(state, top_k=top_k)
            candidates = _filter_plane_scoped_candidates(state, candidates)
            state.candidate_scores = candidates
            state.top_candidates = candidates[:top_k]
        except Exception as fallback_error:
            state.add_error("matching_agent_fallback", str(fallback_error))

    return state