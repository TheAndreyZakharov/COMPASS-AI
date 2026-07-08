from __future__ import annotations

import hashlib
from collections import defaultdict
from typing import Any

GRADE_RANK = {
    "intern": 0.2,
    "junior": 0.35,
    "middle": 0.55,
    "mid": 0.55,
    "senior": 0.78,
    "lead": 0.9,
    "principal": 1.0,
}

PRIORITY_RANK = {
    "low": 0.2,
    "medium": 0.5,
    "normal": 0.5,
    "high": 0.78,
    "critical": 1.0,
    "urgent": 1.0,
}


def as_float(value: Any, default: float = 0.0) -> float:
    if value is None or value == "":
        return default

    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def stable_category_number(value: Any) -> float:
    text = str(value or "unknown").strip().lower()
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    integer = int(digest[:10], 16)
    return float(integer / 0xFFFFFFFFFF)


def grade_rank(value: Any) -> float:
    return GRADE_RANK.get(str(value or "").strip().lower(), stable_category_number(value))


def priority_rank(value: Any) -> float:
    return PRIORITY_RANK.get(str(value or "").strip().lower(), stable_category_number(value))


def deadline_status_score(value: Any) -> float:
    status = str(value or "").strip().lower()
    if status in {"early", "on_time"}:
        return 1.0
    if status in {"late", "missed"}:
        return 0.0
    return 0.5


def outcome_success_score(value: Any) -> float:
    label = str(value or "").strip().lower()
    if label in {"success", "excellent", "good"}:
        return 1.0
    if label in {"acceptable", "late", "rework"}:
        return 0.55
    if label in {"bad", "failed"}:
        return 0.0
    return 0.5


def aggregate_history_by_employee(
    assignment_history: list[dict[str, Any]],
) -> dict[str, dict[str, float]]:
    accumulator: dict[str, dict[str, float]] = defaultdict(
        lambda: {
            "history_count": 0.0,
            "history_quality_sum": 0.0,
            "history_speed_sum": 0.0,
            "history_deadline_success_sum": 0.0,
            "history_outcome_success_sum": 0.0,
            "history_rework_sum": 0.0,
        }
    )

    for record in assignment_history:
        employee_id = str(record.get("employee_id") or "")
        if not employee_id:
            continue

        stats = accumulator[employee_id]
        stats["history_count"] += 1.0
        planned_hours = as_float(record.get("planned_hours"), 0.0)
        actual_hours = as_float(record.get("actual_hours"), planned_hours)
        speed_score = planned_hours / max(actual_hours, 0.01)

        stats["history_quality_sum"] += as_float(record.get("quality_score"), 0.5)
        stats["history_speed_sum"] += min(speed_score, 2.0)
        stats["history_deadline_success_sum"] += deadline_status_score(
            record.get("deadline_status")
        )
        stats["history_outcome_success_sum"] += outcome_success_score(
            record.get("outcome_label")
        )
        stats["history_rework_sum"] += 1.0 if record.get("was_rework_needed") else 0.0

    result: dict[str, dict[str, float]] = {}

    for employee_id, stats in accumulator.items():
        count = max(stats["history_count"], 1.0)
        result[employee_id] = {
            "employee_history_count": stats["history_count"],
            "employee_history_quality_mean": stats["history_quality_sum"] / count,
            "employee_history_speed_mean": stats["history_speed_sum"] / count,
            "employee_history_deadline_success_mean": (
                stats["history_deadline_success_sum"] / count
            ),
            "employee_history_outcome_success_mean": (
                stats["history_outcome_success_sum"] / count
            ),
            "employee_history_rework_rate": stats["history_rework_sum"] / count,
        }

    return result


def build_pair_features(
    pair: dict[str, Any],
    employee: dict[str, Any],
    task: dict[str, Any],
    employee_history: dict[str, float],
) -> dict[str, float]:
    estimated_hours = as_float(task.get("estimated_hours"), 0.0)
    deadline_days = as_float(task.get("deadline_days"), 0.0)
    current_workload = as_float(employee.get("current_workload"), 0.0)
    availability = as_float(employee.get("availability_score"), 0.5)
    fatigue = as_float(employee.get("fatigue_score"), 0.5)
    complexity = as_float(task.get("complexity"), 0.5)
    mentor_level = as_float(employee.get("mentor_level"), 0.0)

    workload_pressure = current_workload + estimated_hours / 40.0
    deadline_pressure = estimated_hours / max(deadline_days * 8.0, 1.0)
    learning_signal = max(0.0, complexity - grade_rank(employee.get("grade")))

    features = {
        "employee_availability_score": availability,
        "employee_current_workload": current_workload,
        "employee_fatigue_score": fatigue,
        "employee_avg_completion_speed": as_float(
            employee.get("avg_completion_speed"),
            1.0,
        ),
        "employee_avg_quality_score": as_float(employee.get("avg_quality_score"), 0.5),
        "employee_deadline_reliability": as_float(
            employee.get("deadline_reliability"),
            0.5,
        ),
        "employee_mentor_level": mentor_level,
        "employee_grade_rank": grade_rank(employee.get("grade")),
        "employee_role_hash": stable_category_number(employee.get("role")),
        "task_complexity": complexity,
        "task_estimated_hours": estimated_hours,
        "task_deadline_days": deadline_days,
        "task_priority_rank": priority_rank(task.get("priority")),
        "task_status_hash": stable_category_number(task.get("status")),
        "task_type_hash": stable_category_number(task.get("task_type")),
        "task_project_hash": stable_category_number(task.get("project_id")),
        "pair_existing_target_score": as_float(pair.get("target_score"), 0.0),
        "pair_existing_label": as_float(pair.get("label"), 0.0),
        "pair_candidate_rank_hint": as_float(pair.get("candidate_rank_hint"), 0.0),
        "pair_workload_pressure": workload_pressure,
        "pair_deadline_pressure": deadline_pressure,
        "pair_fatigue_pressure": fatigue * max(complexity, 0.1),
        "pair_learning_signal": learning_signal,
        "pair_availability_after_task": availability - estimated_hours / 40.0,
        "pair_mentor_complexity_fit": mentor_level * complexity,
    }

    features.update(employee_history)
    return features