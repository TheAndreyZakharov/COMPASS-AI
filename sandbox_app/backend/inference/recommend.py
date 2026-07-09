from __future__ import annotations

import json
import re
import uuid
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pandas as pd
from sandbox_app.backend.data_generation.test_team import (
    TEST_CASES_DIR,
    TestTeamError,
    load_test_case,
)
from sandbox_app.backend.inference.model_loader import (
    ModelLoadError,
)
from sandbox_app.backend.inference.model_loader import (
    load_model as load_sandbox_model,
)
from sandbox_app.backend.inference.risk_factors import candidate_risks, risk_summary
from sandbox_app.backend.inference.scoring import (
    build_pair_feature_frame,
    clamp,
    feature_factors,
    skill_match,
    to_float,
)

RECOMMENDATION_ID_RE = re.compile(r"^rec_[a-zA-Z0-9_-]{8,80}$")

RECOMMENDATION_MODES = {
    "best_quality": {
        "label": "Best quality",
        "description": "Максимизирует качество и skill match.",
    },
    "fastest_delivery": {
        "label": "Fastest delivery",
        "description": "Максимизирует скорость, доступность и надёжность дедлайна.",
    },
    "best_learning": {
        "label": "Best learning",
        "description": "Балансирует результат и развитие learning goals.",
    },
    "balanced": {
        "label": "Balanced",
        "description": "Сбалансированный режим по качеству, скорости, обучению и рискам.",
    },
    "risk_aware": {
        "label": "Risk aware",
        "description": "Сильнее штрафует загрузку, усталость, дедлайны и skill gaps.",
    },
}


class RecommendationError(ValueError):
    """Raised when recommendation cannot be built."""


@dataclass(frozen=True)
class RecommendationConfig:
    session_id: str
    model_name: str
    test_case_id: str
    task_id: str
    recommendation_mode: str = "balanced"
    top_k: int = 3
    candidate_employee_ids: list[str] = field(default_factory=list)
    save_result: bool = True


def utc_now_iso() -> str:
    return datetime.now(UTC).isoformat()


def recommendation_id() -> str:
    stamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    return f"rec_{stamp}_{uuid.uuid4().hex[:8]}"


def validate_mode(mode: str) -> None:
    if mode not in RECOMMENDATION_MODES:
        allowed = ", ".join(sorted(RECOMMENDATION_MODES))
        raise RecommendationError(
            f"Unknown recommendation_mode: {mode}. Allowed: {allowed}"
        )


def validate_top_k(top_k: int) -> None:
    if top_k < 1:
        raise RecommendationError("top_k must be positive")

    if top_k > 100:
        raise RecommendationError("top_k must be <= 100")


def find_task(test_case: dict[str, Any], task_id: str) -> dict[str, Any]:
    tasks = test_case.get("active_tasks") or []

    for task in tasks:
        if str(task.get("task_id")) == task_id:
            return task

    raise RecommendationError(f"Task not found in test case: {task_id}")


def filter_candidates(
    test_case: dict[str, Any],
    candidate_employee_ids: list[str],
) -> list[dict[str, Any]]:
    team = test_case.get("team") or []

    if not candidate_employee_ids:
        return list(team)

    allowed = set(candidate_employee_ids)
    candidates = [
        employee
        for employee in team
        if str(employee.get("employee_id")) in allowed
    ]

    if not candidates:
        raise RecommendationError("candidate_employee_ids did not match any employee")

    return candidates


def predict_scores(model: Any, frame: pd.DataFrame) -> list[float]:
    if frame.empty:
        return []

    if hasattr(model, "predict_scores"):
        raw_scores = model.predict_scores(frame)
    elif hasattr(model, "predict_score"):
        raw_scores = model.predict_score(frame)
    else:
        raise RecommendationError("Loaded model does not expose predict_scores")

    return [clamp(to_float(score)) for score in raw_scores]


def mode_adjusted_score(
    model_score: float,
    factors: dict[str, Any],
    mode: str,
) -> float:
    quality = to_float(factors.get("quality_fit_score"))
    speed = to_float(factors.get("speed_fit_score"))
    learning = to_float(factors.get("learning_fit_score"))
    risk_fit = to_float(factors.get("risk_fit_score"))
    skill = to_float(factors.get("skill_match_ratio"))

    if mode == "best_quality":
        return clamp(model_score * 0.48 + quality * 0.34 + skill * 0.18)

    if mode == "fastest_delivery":
        return clamp(model_score * 0.42 + speed * 0.38 + risk_fit * 0.2)

    if mode == "best_learning":
        return clamp(
            model_score * 0.36
            + learning * 0.34
            + quality * 0.18
            + risk_fit * 0.12
        )

    if mode == "risk_aware":
        return clamp(
            model_score * 0.42
            + risk_fit * 0.38
            + quality * 0.14
            + speed * 0.06
        )

    return clamp(
        model_score * 0.44
        + quality * 0.22
        + speed * 0.16
        + learning * 0.08
        + risk_fit * 0.1
    )


def factor_breakdown(
    model_score: float,
    adjusted_score: float,
    factors: dict[str, Any],
    mode: str,
) -> dict[str, Any]:
    return {
        "mode": mode,
        "model_score": model_score,
        "adjusted_score": adjusted_score,
        "skill_match_ratio": to_float(factors.get("skill_match_ratio")),
        "quality_fit_score": to_float(factors.get("quality_fit_score")),
        "speed_fit_score": to_float(factors.get("speed_fit_score")),
        "learning_fit_score": to_float(factors.get("learning_fit_score")),
        "risk_fit_score": to_float(factors.get("risk_fit_score")),
        "workload_pressure": to_float(factors.get("workload_pressure")),
        "fatigue_risk": to_float(factors.get("fatigue_risk")),
        "availability_gap": to_float(factors.get("availability_gap")),
    }


def candidate_result(
    task: dict[str, Any],
    employee: dict[str, Any],
    row: dict[str, Any],
    model_score: float,
    mode: str,
) -> dict[str, Any]:
    factors = feature_factors(row)
    adjusted_score = mode_adjusted_score(
        model_score=model_score,
        factors=factors,
        mode=mode,
    )
    risks = candidate_risks(
        employee=employee,
        task=task,
        factors=factors,
    )
    match = skill_match(employee, task)

    return {
        "employee_id": employee.get("employee_id"),
        "name": employee.get("name"),
        "role": employee.get("role"),
        "grade": employee.get("grade"),
        "score": adjusted_score,
        "model_score": model_score,
        "factors": factor_breakdown(
            model_score=model_score,
            adjusted_score=adjusted_score,
            factors=factors,
            mode=mode,
        ),
        "matched_skills": match["matched_skills"],
        "missing_skills": match["missing_skills"],
        "risks": risks,
        "risk_summary": risk_summary(risks),
        "employee_snapshot": {
            "current_workload": employee.get("current_workload"),
            "fatigue_score": employee.get("fatigue_score"),
            "availability_score": employee.get("availability_score"),
            "avg_quality_score": employee.get("avg_quality_score"),
            "avg_completion_speed": employee.get("avg_completion_speed"),
            "deadline_reliability": employee.get("deadline_reliability"),
            "active_task_ids": employee.get("active_task_ids", []),
        },
    }


def recommendations_dir(test_case_id: str) -> Path:
    return TEST_CASES_DIR / test_case_id / "recommendations"


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def read_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RecommendationError(f"Could not read recommendation file: {path}") from exc

    if not isinstance(payload, dict):
        raise RecommendationError(
            f"Recommendation file must contain JSON object: {path}"
        )

    return payload


def save_recommendation(test_case_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    rec_id = str(payload["recommendation_id"])
    directory = recommendations_dir(test_case_id)
    path = directory / f"{rec_id}.json"

    payload["paths"] = {
        "recommendation": str(path),
        "latest": str(directory / "latest_recommendation.json"),
    }

    write_json(path, payload)
    write_json(directory / "latest_recommendation.json", payload)

    return payload


def recommend_single_task(config: RecommendationConfig) -> dict[str, Any]:
    validate_mode(config.recommendation_mode)
    validate_top_k(config.top_k)

    try:
        test_case = load_test_case(config.test_case_id)
    except TestTeamError as exc:
        raise RecommendationError(str(exc)) from exc

    task = find_task(test_case, config.task_id)
    candidates = filter_candidates(test_case, config.candidate_employee_ids)

    try:
        model = load_sandbox_model(config.session_id, config.model_name)
    except ModelLoadError as exc:
        raise RecommendationError(str(exc)) from exc

    feature_frame = build_pair_feature_frame(
        task=task,
        employees=candidates,
        recommendation_mode=config.recommendation_mode,
    )
    scores = predict_scores(model, feature_frame)

    if len(scores) != len(candidates):
        raise RecommendationError("Model returned unexpected number of scores")

    candidate_rows = feature_frame.to_dict(orient="records")
    ranked_candidates = [
        candidate_result(
            task=task,
            employee=employee,
            row=row,
            model_score=score,
            mode=config.recommendation_mode,
        )
        for employee, row, score in zip(candidates, candidate_rows, scores, strict=True)
    ]
    ranked_candidates.sort(
        key=lambda item: (
            -to_float(item["score"]),
            to_float(item["risk_summary"]["max_risk_score"]),
            str(item["employee_id"]),
        )
    )

    top_candidates = ranked_candidates[: config.top_k]
    top_1 = top_candidates[0] if top_candidates else None
    top_3 = top_candidates[:3]

    result = {
        "recommendation_id": recommendation_id(),
        "created_at": utc_now_iso(),
        "session_id": config.session_id,
        "model_name": config.model_name,
        "test_case_id": config.test_case_id,
        "task_id": config.task_id,
        "recommendation_mode": config.recommendation_mode,
        "mode_details": RECOMMENDATION_MODES[config.recommendation_mode],
        "top_k": config.top_k,
        "task": task,
        "top_1": top_1,
        "top_3": top_3,
        "candidates": top_candidates,
        "all_candidates_count": len(ranked_candidates),
        "candidate_employee_ids": config.candidate_employee_ids,
        "model_metadata": getattr(model, "metadata", {}),
        "config": asdict(config),
    }

    if config.save_result:
        return save_recommendation(config.test_case_id, result)

    return result


def list_recommendations(test_case_id: str) -> dict[str, Any]:
    directory = recommendations_dir(test_case_id)

    if not directory.exists():
        return {
            "test_case_id": test_case_id,
            "recommendations": [],
            "total": 0,
        }

    items: list[dict[str, Any]] = []

    for path in sorted(directory.glob("rec_*.json"), reverse=True):
        payload = read_json(path)
        top_1 = payload.get("top_1") or {}

        items.append(
            {
                "recommendation_id": payload.get("recommendation_id"),
                "created_at": payload.get("created_at"),
                "session_id": payload.get("session_id"),
                "model_name": payload.get("model_name"),
                "task_id": payload.get("task_id"),
                "recommendation_mode": payload.get("recommendation_mode"),
                "top_1_employee_id": top_1.get("employee_id"),
                "top_1_score": top_1.get("score"),
                "path": str(path),
            }
        )

    return {
        "test_case_id": test_case_id,
        "recommendations": items,
        "total": len(items),
    }


def load_recommendation(test_case_id: str, rec_id: str) -> dict[str, Any]:
    if not RECOMMENDATION_ID_RE.match(rec_id):
        raise RecommendationError(f"Invalid recommendation_id: {rec_id}")

    path = recommendations_dir(test_case_id) / f"{rec_id}.json"

    if not path.exists():
        raise RecommendationError(f"Recommendation not found: {test_case_id}/{rec_id}")

    return read_json(path)


def list_recommendable_tasks(test_case_id: str) -> dict[str, Any]:
    try:
        test_case = load_test_case(test_case_id)
    except TestTeamError as exc:
        raise RecommendationError(str(exc)) from exc

    tasks = [
        task
        for task in test_case.get("active_tasks", [])
        if task.get("status") in {"todo", "in_progress", "review", "blocked"}
    ]

    return {
        "test_case_id": test_case_id,
        "tasks": tasks,
        "total": len(tasks),
    }