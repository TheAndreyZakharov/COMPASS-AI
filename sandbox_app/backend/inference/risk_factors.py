from __future__ import annotations

from typing import Any

from sandbox_app.backend.inference.scoring import clamp, to_float


def risk_level(score: float) -> str:
    if score >= 0.75:
        return "high"

    if score >= 0.45:
        return "medium"

    return "low"


def candidate_risks(
    employee: dict[str, Any],
    task: dict[str, Any],
    factors: dict[str, Any],
) -> list[dict[str, Any]]:
    risks: list[dict[str, Any]] = []

    workload_pressure = to_float(factors.get("workload_pressure"))
    fatigue_risk = to_float(factors.get("fatigue_risk"))
    availability_gap = to_float(factors.get("availability_gap"))
    skill_gap = clamp(1.0 - to_float(factors.get("skill_match_ratio")))
    deadline_days = to_float(factors.get("deadline_days"), 30.0)
    complexity = to_float(task.get("complexity"), 0.5)

    if workload_pressure >= 0.65:
        risks.append(
            {
                "type": "workload",
                "level": risk_level(workload_pressure),
                "score": workload_pressure,
                "message": "У кандидата уже высокая текущая загрузка.",
            }
        )

    if fatigue_risk >= 0.55:
        risks.append(
            {
                "type": "fatigue",
                "level": risk_level(fatigue_risk),
                "score": fatigue_risk,
                "message": "Есть риск просадки качества из-за усталости.",
            }
        )

    if availability_gap >= 0.45:
        risks.append(
            {
                "type": "availability",
                "level": risk_level(availability_gap),
                "score": availability_gap,
                "message": "Доступность кандидата ограничена.",
            }
        )

    if skill_gap >= 0.35:
        risks.append(
            {
                "type": "skill_gap",
                "level": risk_level(skill_gap),
                "score": skill_gap,
                "message": "Не все требуемые навыки покрыты кандидатом.",
            }
        )

    if deadline_days <= 3 and complexity >= 0.55:
        risks.append(
            {
                "type": "deadline",
                "level": "high",
                "score": clamp(1.0 - max(deadline_days, 0.0) / 3.0),
                "message": "Сложная задача с близким дедлайном.",
            }
        )

    if not risks:
        risks.append(
            {
                "type": "none",
                "level": "low",
                "score": 0.0,
                "message": "Критичных рисков не обнаружено.",
            }
        )

    return risks


def risk_summary(risks: list[dict[str, Any]]) -> dict[str, Any]:
    high = sum(1 for risk in risks if risk.get("level") == "high")
    medium = sum(1 for risk in risks if risk.get("level") == "medium")
    low = sum(1 for risk in risks if risk.get("level") == "low")

    max_score = max((to_float(risk.get("score")) for risk in risks), default=0.0)

    return {
        "high": high,
        "medium": medium,
        "low": low,
        "max_risk_score": max_score,
    }