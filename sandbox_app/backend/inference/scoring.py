from __future__ import annotations

from datetime import UTC, date, datetime
from typing import Any

import pandas as pd

PRIORITY_WEIGHTS = {
    "low": 0.15,
    "medium": 0.4,
    "high": 0.75,
    "critical": 1.0,
}

GRADE_WEIGHTS = {
    "junior": 0.2,
    "middle": 0.5,
    "senior": 0.8,
    "lead": 1.0,
}


def clamp(value: float, minimum: float = 0.0, maximum: float = 1.0) -> float:
    return round(max(minimum, min(maximum, value)), 6)


def to_float(value: Any, default: float = 0.0) -> float:
    if value is None:
        return default

    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return default

    if numeric != numeric:
        return default

    return numeric


def to_string_list(value: Any) -> list[str]:
    if value is None:
        return []

    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]

    if isinstance(value, tuple | set):
        return [str(item).strip() for item in value if str(item).strip()]

    if isinstance(value, str):
        return [item.strip() for item in value.split(",") if item.strip()]

    return []


def deadline_days(task: dict[str, Any]) -> float:
    raw_deadline = task.get("deadline") or task.get("due_date")

    if not raw_deadline:
        return 30.0

    try:
        parsed = datetime.fromisoformat(str(raw_deadline).replace("Z", "+00:00"))
    except ValueError:
        return 30.0

    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)

    today = datetime.now(UTC).date()
    return float((parsed.date() - today).days)


def skill_match(employee: dict[str, Any], task: dict[str, Any]) -> dict[str, Any]:
    employee_skills = set(to_string_list(employee.get("skills")))
    required_skills = set(to_string_list(task.get("required_skills")))

    if not required_skills:
        return {
            "matched_skills": [],
            "missing_skills": [],
            "skill_match_ratio": 1.0,
            "required_skills_count": 0,
            "matched_skills_count": 0,
            "missing_skills_count": 0,
        }

    matched = sorted(employee_skills & required_skills)
    missing = sorted(required_skills - employee_skills)

    return {
        "matched_skills": matched,
        "missing_skills": missing,
        "skill_match_ratio": clamp(len(matched) / len(required_skills)),
        "required_skills_count": len(required_skills),
        "matched_skills_count": len(matched),
        "missing_skills_count": len(missing),
    }


def learning_match(employee: dict[str, Any], task: dict[str, Any]) -> float:
    learning_goals = set(to_string_list(employee.get("learning_goals")))
    required_skills = set(to_string_list(task.get("required_skills")))

    if not required_skills or not learning_goals:
        return 0.0

    return clamp(len(learning_goals & required_skills) / len(required_skills))


def workload_pressure(employee: dict[str, Any]) -> float:
    workload = to_float(employee.get("current_workload"))
    active_tasks = len(to_string_list(employee.get("active_task_ids")))
    active_task_pressure = clamp(active_tasks / 8.0)

    return clamp(workload * 0.72 + active_task_pressure * 0.28)


def priority_weight(task: dict[str, Any]) -> float:
    return PRIORITY_WEIGHTS.get(str(task.get("priority", "")).lower(), 0.4)


def grade_weight(employee: dict[str, Any]) -> float:
    return GRADE_WEIGHTS.get(str(employee.get("grade", "")).lower(), 0.5)


def task_employee_feature_map(
    task: dict[str, Any],
    employee: dict[str, Any],
    recommendation_mode: str,
) -> dict[str, float | int | str]:
    match = skill_match(employee, task)
    workload = to_float(employee.get("current_workload"))
    fatigue = to_float(employee.get("fatigue_score"))
    availability = to_float(employee.get("availability_score"))
    complexity = to_float(task.get("complexity"), 0.5)
    estimated_hours = to_float(task.get("estimated_hours"), 8.0)
    days_left = deadline_days(task)
    active_task_count = len(to_string_list(employee.get("active_task_ids")))
    skill_ratio = to_float(match["skill_match_ratio"])
    learning_ratio = learning_match(employee, task)

    speed_score = to_float(employee.get("avg_completion_speed"), 0.5)
    quality_score = to_float(employee.get("avg_quality_score"), 0.5)
    deadline_reliability = to_float(employee.get("deadline_reliability"), 0.5)
    mentor_level = to_float(employee.get("mentor_level"), 0.0)

    deadline_pressure = clamp(1.0 - max(days_left, 0.0) / 30.0)
    workload_risk = clamp(workload_pressure(employee))
    fatigue_risk = clamp(fatigue)
    availability_gap = clamp(1.0 - availability)
    overload_indicator = 1 if workload_risk >= 0.78 else 0
    high_fatigue_indicator = 1 if fatigue_risk >= 0.7 else 0

    return {
        "pair_id": f"{task.get('task_id', '')}::{employee.get('employee_id', '')}",
        "task_id": str(task.get("task_id", "")),
        "employee_id": str(employee.get("employee_id", "")),
        "recommendation_mode": recommendation_mode,
        "employee_availability_score": availability,
        "employee_current_workload": workload,
        "employee_fatigue_score": fatigue,
        "employee_avg_completion_speed": speed_score,
        "employee_avg_quality_score": quality_score,
        "employee_deadline_reliability": deadline_reliability,
        "employee_mentor_level": mentor_level,
        "employee_grade_weight": grade_weight(employee),
        "employee_active_tasks_count": active_task_count,
        "task_complexity": complexity,
        "task_estimated_hours": estimated_hours,
        "task_priority_weight": priority_weight(task),
        "task_deadline_days": days_left,
        "task_deadline_pressure": deadline_pressure,
        "skill_match_ratio": skill_ratio,
        "skill_overlap_ratio": skill_ratio,
        "matched_skills_count": int(match["matched_skills_count"]),
        "missing_skills_count": int(match["missing_skills_count"]),
        "required_skills_count": int(match["required_skills_count"]),
        "learning_goal_match_ratio": learning_ratio,
        "workload_pressure": workload_risk,
        "workload_risk": workload_risk,
        "fatigue_risk": fatigue_risk,
        "availability_gap": availability_gap,
        "overload_indicator": overload_indicator,
        "high_fatigue_indicator": high_fatigue_indicator,
        "quality_fit_score": clamp(
            quality_score * 0.38
            + skill_ratio * 0.32
            + deadline_reliability * 0.18
            + mentor_level * 0.12
        ),
        "speed_fit_score": clamp(
            speed_score * 0.42
            + availability * 0.28
            + deadline_reliability * 0.18
            - workload_risk * 0.12
        ),
        "learning_fit_score": clamp(
            learning_ratio * 0.5
            + mentor_level * 0.2
            + skill_ratio * 0.2
            + availability * 0.1
        ),
        "risk_fit_score": clamp(
            1.0
            - workload_risk * 0.34
            - fatigue_risk * 0.28
            - availability_gap * 0.2
            - deadline_pressure * 0.1
            - complexity * 0.08
        ),
    }


def build_pair_feature_frame(
    task: dict[str, Any],
    employees: list[dict[str, Any]],
    recommendation_mode: str,
) -> pd.DataFrame:
    rows = [
        task_employee_feature_map(
            task=task,
            employee=employee,
            recommendation_mode=recommendation_mode,
        )
        for employee in employees
    ]

    if not rows:
        return pd.DataFrame()

    return pd.DataFrame(rows)


def feature_factors(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "skill_match_ratio": to_float(row.get("skill_match_ratio")),
        "matched_skills_count": int(to_float(row.get("matched_skills_count"))),
        "missing_skills_count": int(to_float(row.get("missing_skills_count"))),
        "quality_fit_score": to_float(row.get("quality_fit_score")),
        "speed_fit_score": to_float(row.get("speed_fit_score")),
        "learning_fit_score": to_float(row.get("learning_fit_score")),
        "risk_fit_score": to_float(row.get("risk_fit_score")),
        "workload_pressure": to_float(row.get("workload_pressure")),
        "fatigue_risk": to_float(row.get("fatigue_risk")),
        "availability_gap": to_float(row.get("availability_gap")),
        "deadline_days": to_float(row.get("task_deadline_days")),
    }


def today_iso() -> str:
    return date.today().isoformat()