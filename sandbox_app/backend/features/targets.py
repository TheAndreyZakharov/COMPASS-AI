from __future__ import annotations

from typing import Any


def as_float(value: Any, default: float = 0.0) -> float:
    if value is None or value == "":
        return default

    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def clamp(value: float, lower: float = 0.0, upper: float = 1.0) -> float:
    return max(lower, min(upper, value))


def target_score_for_mode(
    pair: dict[str, Any],
    feature_row: dict[str, float],
    target_mode: str,
) -> float:
    existing_score = pair.get("target_score")
    if existing_score is not None and target_mode == str(pair.get("target_mode", target_mode)):
        return clamp(as_float(existing_score, 0.0))

    quality = feature_row.get("employee_avg_quality_score", 0.5)
    speed = feature_row.get("employee_avg_completion_speed", 1.0)
    speed_score = clamp(speed / 2.0)
    availability = clamp(feature_row.get("employee_availability_score", 0.5))
    fatigue_risk = clamp(1.0 - feature_row.get("employee_fatigue_score", 0.5))
    workload_fit = clamp(1.0 - feature_row.get("pair_workload_pressure", 0.5))
    skill_match = clamp(feature_row.get("skill_match_ratio", 0.0))
    learning = clamp(feature_row.get("pair_learning_signal", 0.0))
    deadline = clamp(feature_row.get("employee_deadline_reliability", 0.5))

    if target_mode == "quality":
        return clamp(0.5 * quality + 0.3 * skill_match + 0.2 * deadline)

    if target_mode == "speed":
        return clamp(0.45 * speed_score + 0.25 * availability + 0.3 * skill_match)

    if target_mode == "learning":
        return clamp(0.45 * learning + 0.25 * skill_match + 0.3 * quality)

    if target_mode == "risk_aware":
        return clamp(0.3 * quality + 0.25 * workload_fit + 0.25 * fatigue_risk + 0.2 * deadline)

    return clamp(
        0.25 * quality
        + 0.2 * speed_score
        + 0.2 * skill_match
        + 0.2 * workload_fit
        + 0.15 * deadline
    )


def target_label(score: float) -> int:
    return 1 if score >= 0.5 else 0


def build_target_row(
    pair: dict[str, Any],
    feature_row: dict[str, float],
    target_mode: str,
) -> dict[str, Any]:
    score = target_score_for_mode(pair, feature_row, target_mode)
    raw_label = pair.get("label")
    label = int(raw_label) if raw_label is not None else target_label(score)

    return {
        "pair_id": str(pair.get("pair_id") or ""),
        "task_id": str(pair.get("task_id") or ""),
        "employee_id": str(pair.get("employee_id") or ""),
        "split": str(pair.get("split") or "train"),
        "target_mode": target_mode,
        "target_score": score,
        "label": label,
    }