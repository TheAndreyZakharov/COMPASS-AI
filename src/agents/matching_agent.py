from __future__ import annotations

from typing import Any

from src.agents.state import AgentState
from src.models.inference import score_task_candidates
from src.recommendation.rule_based_ranker import (
    rank_employees_for_task,
    recommendation_to_dict,
)


def _ml_candidates_available(task_features: dict[str, Any]) -> bool:
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
        candidate["source"] = "rule_based_fallback"
        candidates.append(candidate)

    return candidates


def run_matching_agent(state: AgentState, top_k: int = 3) -> AgentState:
    if not state.task_features:
        state.add_error("matching_agent", "Task features are empty.")
        return state

    if not state.employees:
        state.add_error("matching_agent", "Employee list is empty.")
        return state

    try:
        if _ml_candidates_available(state.task_features):
            candidates = _run_ml_matching(state, top_k=top_k)
        else:
            candidates = _run_rule_based_fallback(state, top_k=top_k)

        state.candidate_scores = candidates
        state.top_candidates = candidates[:top_k]
    except Exception as error:
        state.add_error("matching_agent", str(error))

        try:
            candidates = _run_rule_based_fallback(state, top_k=top_k)
            state.candidate_scores = candidates
            state.top_candidates = candidates[:top_k]
        except Exception as fallback_error:
            state.add_error("matching_agent_fallback", str(fallback_error))

    return state