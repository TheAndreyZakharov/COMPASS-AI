from __future__ import annotations

import random
from datetime import UTC, datetime, timedelta
from typing import Any

GRADE_SCORE_BONUS = {
    "junior": 0.00,
    "middle": 0.08,
    "senior": 0.16,
    "lead": 0.22,
}

DEADLINE_STATUSES = [
    "early",
    "on_time",
    "late",
    "failed",
]

OUTCOME_LABELS = [
    "good",
    "bad",
    "late",
    "failed",
]


def build_assignment_outcome(
    employee: dict[str, Any],
    task: dict[str, Any],
    assigned_at: datetime,
    planned_hours: float,
    params: dict[str, float],
    rng: random.Random,
) -> dict[str, Any]:
    score = calculate_success_score(employee, task, params)
    score = add_noise(score, rng)

    actual_hours = build_actual_hours(planned_hours, score, rng)
    quality_score = build_quality_score(score, rng)
    deadline_status = build_deadline_status(score, rng)
    outcome_label = build_outcome_label(score, deadline_status)
    was_rework_needed = build_rework_flag(score, params, rng)
    feedback_score = build_feedback_score(score, was_rework_needed, rng)

    completed_at = assigned_at + timedelta(hours=actual_hours)

    return {
        "completed_at": completed_at.replace(tzinfo=UTC).isoformat(),
        "actual_hours": round_float(actual_hours),
        "quality_score": quality_score,
        "deadline_status": deadline_status,
        "outcome_label": outcome_label,
        "was_rework_needed": was_rework_needed,
        "feedback_score": feedback_score,
        "success_score": round_float(score),
        "skill_match_score": calculate_skill_match(employee, task),
    }


def calculate_success_score(
    employee: dict[str, Any],
    task: dict[str, Any],
    params: dict[str, float],
) -> float:
    skill_match = calculate_skill_match(employee, task)
    grade_bonus = GRADE_SCORE_BONUS.get(str(employee.get("grade", "")), 0.05)
    workload = float(employee.get("current_workload", 0.5))
    fatigue = float(employee.get("fatigue_level", 0.3))
    complexity = normalize_complexity(task)
    learning_bonus = calculate_learning_bonus(employee, task)

    score = 0.48
    score += skill_match * params["skill_match_bonus_strength"]
    score += grade_bonus
    score += learning_bonus * params["learning_bonus_strength"]
    score -= workload * params["overload_penalty_strength"]
    score -= fatigue * params["fatigue_penalty_strength"]
    score -= complexity * params["complexity_penalty_strength"]

    return clamp(score, 0.02, 0.98)


def calculate_skill_match(
    employee: dict[str, Any],
    task: dict[str, Any],
) -> float:
    employee_skills = set(employee.get("skills", []))
    required_skills = set(task.get("required_skills", []))

    if not required_skills:
        return 1.0

    matched_skills = employee_skills.intersection(required_skills)
    return len(matched_skills) / len(required_skills)


def calculate_learning_bonus(
    employee: dict[str, Any],
    task: dict[str, Any],
) -> float:
    learning_goals = set(employee.get("learning_goals", []))
    required_skills = set(task.get("required_skills", []))

    if not required_skills:
        return 0.0

    matched_goals = learning_goals.intersection(required_skills)
    return len(matched_goals) / len(required_skills)


def normalize_complexity(task: dict[str, Any]) -> float:
    complexity = float(task.get("complexity", 5))
    return clamp(complexity / 10.0, 0.0, 1.0)


def add_noise(score: float, rng: random.Random) -> float:
    return clamp(score + rng.uniform(-0.10, 0.10), 0.0, 1.0)


def build_actual_hours(
    planned_hours: float,
    score: float,
    rng: random.Random,
) -> float:
    speed_factor = 1.45 - score * 0.70
    noise = rng.uniform(0.85, 1.25)

    return max(0.25, planned_hours * speed_factor * noise)


def build_quality_score(
    score: float,
    rng: random.Random,
) -> float:
    return round_float(clamp(score + rng.uniform(-0.08, 0.08), 0.0, 1.0))


def build_deadline_status(
    score: float,
    rng: random.Random,
) -> str:
    if score >= 0.82:
        return rng.choices(["early", "on_time", "late"], [0.35, 0.60, 0.05])[0]

    if score >= 0.62:
        return rng.choices(["on_time", "late", "failed"], [0.70, 0.25, 0.05])[0]

    if score >= 0.38:
        return rng.choices(["on_time", "late", "failed"], [0.35, 0.50, 0.15])[0]

    return rng.choices(["late", "failed"], [0.45, 0.55])[0]


def build_outcome_label(
    score: float,
    deadline_status: str,
) -> str:
    if deadline_status == "failed":
        return "failed"

    if deadline_status == "late":
        return "late"

    if score >= 0.62:
        return "good"

    return "bad"


def build_rework_flag(
    score: float,
    params: dict[str, float],
    rng: random.Random,
) -> bool:
    base_probability = params["rework_probability"]
    adjusted_probability = base_probability + max(0.0, 0.60 - score) * 0.45

    return rng.random() < clamp(adjusted_probability, 0.0, 0.95)


def build_feedback_score(
    score: float,
    was_rework_needed: bool,
    rng: random.Random,
) -> float:
    penalty = 0.12 if was_rework_needed else 0.0
    feedback = score - penalty + rng.uniform(-0.06, 0.06)

    return round_float(clamp(feedback, 0.0, 1.0))


def round_float(value: float) -> float:
    return round(value, 4)


def clamp(
    value: float,
    min_value: float,
    max_value: float,
) -> float:
    return max(min_value, min(max_value, value))