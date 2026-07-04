from __future__ import annotations

import json
import math
from dataclasses import dataclass
from typing import Any

from src.recommendation.skill_matching import normalize_skill_name, parse_required_skills


@dataclass(frozen=True)
class GrowthScoreResult:
    score: float
    matched_learning_goals: list[str]
    complexity_fit: float
    mentor_available: bool
    reasons: list[str]
    risks: list[str]


GRADE_COMPLEXITY_LIMITS: dict[str, int] = {
    "junior": 2,
    "middle": 4,
    "senior": 5,
    "lead": 5,
}


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None:
            return default

        if isinstance(value, float) and math.isnan(value):
            return default

        return float(value)
    except (TypeError, ValueError):
        return default


def _parse_json_like(value: Any, default: Any) -> Any:
    if value is None:
        return default

    if isinstance(value, float) and math.isnan(value):
        return default

    if isinstance(value, (dict, list)):
        return value

    if isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            return default

        try:
            return json.loads(stripped)
        except json.JSONDecodeError:
            return default

    return default


def parse_learning_goals(employee: dict[str, Any]) -> list[str]:
    raw_goals = _parse_json_like(employee.get("learning_goals"), default=[])

    if isinstance(raw_goals, list):
        return [normalize_skill_name(goal) for goal in raw_goals if str(goal).strip()]

    if isinstance(raw_goals, str) and raw_goals.strip():
        return [normalize_skill_name(raw_goals)]

    return []


def complexity_fit_score(task: dict[str, Any], employee: dict[str, Any]) -> float:
    complexity = int(_safe_float(task.get("complexity"), default=3.0))
    grade = str(employee.get("grade", "middle")).strip().lower()
    max_safe_complexity = GRADE_COMPLEXITY_LIMITS.get(grade, 3)

    if complexity <= max_safe_complexity:
        return 1.0

    gap = complexity - max_safe_complexity

    if gap == 1:
        return 0.55

    return 0.2


def calculate_growth_score(
    task: dict[str, Any],
    employee: dict[str, Any],
    *,
    mentor_available: bool = False,
) -> GrowthScoreResult:
    learning_goals = parse_learning_goals(employee)
    required_skills = parse_required_skills(task)
    required_skill_names = set(required_skills)

    matched_goals = sorted(goal for goal in learning_goals if goal in required_skill_names)

    if required_skill_names:
        goal_match_score = len(matched_goals) / len(required_skill_names)
    else:
        goal_match_score = 0.0

    fit_score = complexity_fit_score(task, employee)

    mentor_bonus = 0.1 if mentor_available else 0.0
    score = (0.65 * goal_match_score) + (0.35 * fit_score) + mentor_bonus
    score = max(0.0, min(1.0, score))

    reasons: list[str] = []
    risks: list[str] = []

    if matched_goals:
        reasons.append("task supports employee learning goals")

    if fit_score >= 0.9:
        reasons.append("task complexity fits employee grade")
    elif fit_score >= 0.5:
        reasons.append("task is a moderate growth stretch")
        if not mentor_available:
            risks.append("mentor support recommended")
    else:
        risks.append("task may be too complex for current grade")

    if mentor_available:
        reasons.append("mentor support available")

    return GrowthScoreResult(
        score=round(score, 4),
        matched_learning_goals=matched_goals,
        complexity_fit=round(fit_score, 4),
        mentor_available=mentor_available,
        reasons=reasons,
        risks=risks,
    )


def growth_score(
    task: dict[str, Any],
    employee: dict[str, Any],
    *,
    mentor_available: bool = False,
) -> float:
    return calculate_growth_score(
        task,
        employee,
        mentor_available=mentor_available,
    ).score