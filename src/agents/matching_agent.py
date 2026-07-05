from __future__ import annotations

from typing import Any

from src.agents.state import AgentState
from src.models.inference import score_task_candidates
from src.recommendation.rule_based_ranker import (
    rank_employees_for_task,
    recommendation_to_dict,
)


def _task_id_from_state(state: AgentState) -> str:
    task = state.task_features or {}
    return str(task.get("task_id") or "").strip()


def _has_scoped_candidates(state: AgentState) -> bool:
    return bool(state.employees)


def _is_synthetic_task(state: AgentState) -> bool:
    task_id = _task_id_from_state(state)
    return task_id.startswith("TASK-")


def _top_candidates_from_response(response: dict[str, Any]) -> list[dict[str, Any]]:
    candidates = response.get("top_candidates") or response.get("candidates") or []

    if not isinstance(candidates, list):
        return []

    return [candidate for candidate in candidates if isinstance(candidate, dict)]


def _set_candidates_from_response(
    state: AgentState,
    response: dict[str, Any],
) -> AgentState:
    candidates = _top_candidates_from_response(response)
    state.candidate_scores = candidates
    state.top_candidates = candidates
    return state


def _run_ml_matching(state: AgentState, top_k: int) -> AgentState:
    task_id = _task_id_from_state(state)

    if not task_id:
        raise ValueError("ML matching requires task_id.")

    response = score_task_candidates(
        task_id=task_id,
        mode=state.recommendation_mode,
        top_k=top_k,
    )

    return _set_candidates_from_response(state=state, response=response)


def _run_rule_based_matching(
    state: AgentState,
    top_k: int,
    source: str,
) -> AgentState:
    task = state.task_features or {}
    employees = state.employees or []

    if not employees:
        state.add_error("matching_agent", "No employees available for matching.")
        state.candidate_scores = []
        state.top_candidates = []
        return state

    recommendation = rank_employees_for_task(
        task=task,
        employees=employees,
        mode=state.recommendation_mode,
        top_k=top_k,
    )
    response = recommendation_to_dict(recommendation)
    candidates = _top_candidates_from_response(response)

    for candidate in candidates:
        candidate["source"] = source

    state.candidate_scores = candidates
    state.top_candidates = candidates
    return state


def _run_plane_scoped_matching(state: AgentState, top_k: int) -> AgentState:
    state = _run_rule_based_matching(
        state=state,
        top_k=top_k,
        source="plane_project_members_rule_based",
    )

    allowed_plane_user_ids = {
        str(employee.get("plane_user_id") or "").strip()
        for employee in state.employees or []
        if str(employee.get("plane_user_id") or "").strip()
    }
    allowed_employee_ids = {
        str(employee.get("employee_id") or "").strip()
        for employee in state.employees or []
        if str(employee.get("employee_id") or "").strip()
    }

    filtered_candidates: list[dict[str, Any]] = []

    for candidate in state.top_candidates:
        plane_user_id = str(candidate.get("plane_user_id") or "").strip()
        employee_id = str(candidate.get("employee_id") or "").strip()

        if plane_user_id in allowed_plane_user_ids or employee_id in allowed_employee_ids:
            filtered_candidates.append(candidate)

    for index, candidate in enumerate(filtered_candidates, start=1):
        candidate["rank"] = index
        candidate["candidate_scope"] = "plane_project_members"

    state.candidate_scores = filtered_candidates
    state.top_candidates = filtered_candidates

    if not filtered_candidates:
        state.add_error(
            "matching_agent",
            "Plane scoped matching returned no candidates after scope validation.",
        )

    return state


def run_matching_agent(
    state: AgentState,
    top_k: int = 3,
) -> AgentState:
    normalized_top_k = max(1, min(int(top_k), 10))

    if not state.task_features:
        state.add_error("matching_agent", "Task features are empty.")
        state.candidate_scores = []
        state.top_candidates = []
        return state

    if _has_scoped_candidates(state):
        return _run_plane_scoped_matching(state=state, top_k=normalized_top_k)

    if _is_synthetic_task(state):
        try:
            return _run_ml_matching(state=state, top_k=normalized_top_k)
        except Exception as error:
            state.add_error("matching_agent", f"ML matching failed: {error}")

    return _run_rule_based_matching(
        state=state,
        top_k=normalized_top_k,
        source="rule_based_fallback",
    )