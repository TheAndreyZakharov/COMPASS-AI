from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class WorkloadScoreResult:
    score: float
    workload: float
    active_tasks_count: int
    availability: float
    risk_level: str
    reasons: list[str]


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None:
            return default

        if isinstance(value, float) and math.isnan(value):
            return default

        return float(value)
    except (TypeError, ValueError):
        return default


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        if value is None:
            return default

        if isinstance(value, float) and math.isnan(value):
            return default

        return int(value)
    except (TypeError, ValueError):
        return default


def normalize_workload(value: Any) -> float:
    workload = _safe_float(value, default=0.0)

    if workload > 1.0:
        workload = workload / 100.0

    return max(0.0, min(1.0, workload))


def workload_risk_level(workload: float) -> str:
    if workload >= 0.95:
        return "critical"

    if workload >= 0.85:
        return "high"

    if workload >= 0.70:
        return "medium"

    return "low"


def calculate_workload_score(employee: dict[str, Any]) -> WorkloadScoreResult:
    workload = normalize_workload(employee.get("current_workload", 0.0))
    active_tasks_count = _safe_int(employee.get("active_tasks_count", 0))
    availability = normalize_workload(employee.get("availability", 1.0))

    base_score = 1.0 - workload

    if workload >= 0.95:
        base_score *= 0.2
    elif workload >= 0.85:
        base_score *= 0.45
    elif workload >= 0.70:
        base_score *= 0.75

    if active_tasks_count >= 8:
        base_score *= 0.75
    elif active_tasks_count >= 5:
        base_score *= 0.9

    if availability < 0.5:
        base_score *= 0.5
    elif availability < 0.8:
        base_score *= 0.8

    score = max(0.0, min(1.0, base_score))
    risk_level = workload_risk_level(workload)

    reasons: list[str] = []

    if risk_level == "critical":
        reasons.append("critical workload")
    elif risk_level == "high":
        reasons.append("high workload")
    elif risk_level == "medium":
        reasons.append("moderate workload")
    else:
        reasons.append("available capacity")

    if active_tasks_count >= 8:
        reasons.append("many active tasks")
    elif active_tasks_count >= 5:
        reasons.append("several active tasks")

    if availability < 0.8:
        reasons.append("limited availability")

    return WorkloadScoreResult(
        score=round(score, 4),
        workload=round(workload, 4),
        active_tasks_count=active_tasks_count,
        availability=round(availability, 4),
        risk_level=risk_level,
        reasons=reasons,
    )


def workload_score(employee: dict[str, Any]) -> float:
    return calculate_workload_score(employee).score


def workload_penalty(employee: dict[str, Any]) -> float:
    return round(1.0 - workload_score(employee), 4)