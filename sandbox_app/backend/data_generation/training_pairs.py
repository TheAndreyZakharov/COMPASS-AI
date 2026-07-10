from __future__ import annotations

import random
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from sandbox_app.backend.core.data_contracts import validate_record_required_fields
from sandbox_app.backend.core.time import moscow_now_iso


class TrainingPairsGenerationError(RuntimeError):
    """Raised when training pair generation cannot be completed safely."""


@dataclass(frozen=True)
class TrainingPairSettings:
    dataset_id: str
    target_pairs: int
    candidates_per_task: int
    target_mode: str
    seed: int | None


TARGET_MODES = {"quality", "speed", "balanced", "learning", "risk_aware"}


def utc_now_iso() -> str:
    return moscow_now_iso()


def clamp(value: float, minimum: float = 0.0, maximum: float = 1.0) -> float:
    return max(minimum, min(maximum, value))


def skill_match_score(employee: dict[str, Any], task: dict[str, Any]) -> float:
    employee_skills = {str(item).lower() for item in employee.get("skills", [])}
    required_skills = {str(item).lower() for item in task.get("required_skills", [])}

    if not required_skills:
        return 1.0

    return len(employee_skills & required_skills) / len(required_skills)


def learning_match_score(employee: dict[str, Any], task: dict[str, Any]) -> float:
    learning_goals = {str(item).lower() for item in employee.get("learning_goals", [])}
    required_skills = {str(item).lower() for item in task.get("required_skills", [])}

    if not learning_goals or not required_skills:
        return 0.0

    return len(learning_goals & required_skills) / len(required_skills)


def safe_float(value: Any, fallback: float) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return fallback


def aggregate_history_metrics(
    assignment_history: list[dict[str, Any]],
) -> dict[str, dict[str, float]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)

    for row in assignment_history:
        employee_id = str(row.get("employee_id", "")).strip()
        if employee_id:
            grouped[employee_id].append(row)

    metrics: dict[str, dict[str, float]] = {}

    for employee_id, rows in grouped.items():
        count = len(rows)

        avg_quality = sum(
            safe_float(row.get("quality_score"), 0.5)
            for row in rows
        ) / max(1, count)
        avg_feedback = sum(
            safe_float(row.get("feedback_score"), 0.5)
            for row in rows
        ) / max(1, count)
        avg_skill_match = sum(
            safe_float(row.get("skill_match_score"), 0.5)
            for row in rows
        ) / max(1, count)
        rework_share = sum(
            1 for row in rows if row.get("was_rework_needed") is True
        ) / max(1, count)
        late_share = sum(
            1
            for row in rows
            if str(row.get("deadline_status")) in {"late", "missed"}
        ) / max(1, count)
        success_share = sum(
            1
            for row in rows
            if str(row.get("outcome_label")) in {"success", "good"}
        ) / max(1, count)

        planned_total = sum(
            safe_float(row.get("planned_hours"), 1.0)
            for row in rows
        )
        actual_total = sum(
            safe_float(row.get("actual_hours"), 1.0)
            for row in rows
        )
        speed_score = clamp(planned_total / max(actual_total, 0.5))

        metrics[employee_id] = {
            "history_count": float(count),
            "avg_quality": round(avg_quality, 4),
            "avg_feedback": round(avg_feedback, 4),
            "avg_skill_match": round(avg_skill_match, 4),
            "rework_share": round(rework_share, 4),
            "late_share": round(late_share, 4),
            "success_share": round(success_share, 4),
            "speed_score": round(speed_score, 4),
        }

    return metrics


def score_pair(
    employee: dict[str, Any],
    task: dict[str, Any],
    employee_history: dict[str, float],
    target_mode: str,
) -> tuple[float, dict[str, float]]:
    skill_score = skill_match_score(employee, task)
    learning_score = learning_match_score(employee, task)

    quality_base = safe_float(
        employee.get("avg_quality_score", employee_history.get("avg_quality", 0.55)),
        0.55,
    )
    speed_base = safe_float(
        employee.get("avg_completion_speed", employee_history.get("speed_score", 0.55)),
        0.55,
    )
    deadline_base = safe_float(employee.get("deadline_reliability"), 0.6)
    workload = safe_float(
        employee.get("current_workload", employee.get("workload_current", 0.45)),
        0.45,
    )
    fatigue = safe_float(employee.get("fatigue_score"), 0.35)
    complexity = clamp((safe_float(task.get("complexity"), 5.0) - 1.0) / 9.0)
    success_share = employee_history.get("success_share", 0.5)
    rework_share = employee_history.get("rework_share", 0.15)
    late_share = employee_history.get("late_share", 0.18)

    quality_component = clamp(
        0.34 * skill_score
        + 0.24 * quality_base
        + 0.16 * success_share
        + 0.12 * deadline_base
        - 0.08 * rework_share
        - 0.06 * complexity
    )
    speed_component = clamp(
        0.34 * speed_base
        + 0.2 * deadline_base
        + 0.18 * skill_score
        - 0.16 * workload
        - 0.08 * fatigue
        - 0.04 * late_share
    )
    learning_component = clamp(
        0.42 * learning_score
        + 0.2 * skill_score
        + 0.16 * safe_float(employee.get("mentor_level"), 0.35)
        + 0.1 * quality_base
        - 0.08 * workload
        - 0.04 * fatigue
    )
    risk_component = clamp(
        1.0
        - (
            0.28 * workload
            + 0.24 * fatigue
            + 0.18 * (1.0 - deadline_base)
            + 0.14 * late_share
            + 0.1 * rework_share
            + 0.06 * complexity
        )
    )

    if target_mode == "quality":
        score = quality_component
    elif target_mode == "speed":
        score = speed_component
    elif target_mode == "learning":
        score = learning_component
    elif target_mode == "risk_aware":
        score = risk_component
    else:
        score = (
            quality_component * 0.34
            + speed_component * 0.24
            + learning_component * 0.16
            + risk_component * 0.26
        )

    factors = {
        "skill_match_score": round(skill_score, 4),
        "learning_match_score": round(learning_score, 4),
        "quality_component": round(quality_component, 4),
        "speed_component": round(speed_component, 4),
        "learning_component": round(learning_component, 4),
        "risk_component": round(risk_component, 4),
        "workload": round(clamp(workload), 4),
        "fatigue": round(clamp(fatigue), 4),
        "complexity": round(complexity, 4),
    }

    return round(clamp(score), 4), factors


def ranked_candidates_for_task(
    task: dict[str, Any],
    employees: list[dict[str, Any]],
    history_metrics: dict[str, dict[str, float]],
    target_mode: str,
) -> list[dict[str, Any]]:
    ranked: list[dict[str, Any]] = []

    for employee in employees:
        employee_id = str(employee.get("employee_id", "")).strip()
        if not employee_id:
            continue

        score, factors = score_pair(
            employee=employee,
            task=task,
            employee_history=history_metrics.get(employee_id, {}),
            target_mode=target_mode,
        )
        ranked.append(
            {
                "employee_id": employee_id,
                "score": score,
                "factors": factors,
            }
        )

    return sorted(ranked, key=lambda item: item["score"], reverse=True)


def validate_training_pair_settings(settings: TrainingPairSettings) -> None:
    if settings.target_mode not in TARGET_MODES:
        allowed_modes = ", ".join(sorted(TARGET_MODES))
        raise TrainingPairsGenerationError(
            f"target_mode must be one of: {allowed_modes}"
        )

    if settings.target_pairs < 1:
        raise TrainingPairsGenerationError("target_pairs must be greater than zero")

    if settings.candidates_per_task < 1:
        raise TrainingPairsGenerationError(
            "candidates_per_task must be greater than zero"
        )


def validate_training_pair_inputs(
    employees: list[dict[str, Any]],
    tasks: list[dict[str, Any]],
) -> None:
    if not employees:
        raise TrainingPairsGenerationError("employees must not be empty")

    if not tasks:
        raise TrainingPairsGenerationError("tasks must not be empty")


def select_candidate(
    ranked: list[dict[str, Any]],
    rng: random.Random,
    positive_count: int,
    positive_target: int,
    candidates_per_task: int,
) -> tuple[dict[str, Any], int, int]:
    candidate_limit = min(candidates_per_task, len(ranked))
    positive_pool_size = max(1, min(candidate_limit, max(1, len(ranked) // 4)))
    negative_start = min(positive_pool_size, len(ranked) - 1)

    if positive_count < positive_target:
        return rng.choice(ranked[:positive_pool_size]), 1, positive_count + 1

    negative_pool = ranked[negative_start:]
    return rng.choice(negative_pool or ranked[-1:]), 0, positive_count


def candidate_rank(
    ranked: list[dict[str, Any]],
    candidate: dict[str, Any],
) -> int:
    return next(
        index + 1
        for index, item in enumerate(ranked)
        if item["employee_id"] == candidate["employee_id"]
    )


def normalize_target_score(
    candidate_score: float,
    label: int,
    rng: random.Random,
) -> float:
    if label == 0:
        return round(min(candidate_score, rng.uniform(0.02, 0.49)), 4)

    return round(max(candidate_score, rng.uniform(0.51, 0.98)), 4)


def build_pair(
    pair_index: int,
    settings: TrainingPairSettings,
    task: dict[str, Any],
    candidate: dict[str, Any],
    label: int,
    rank: int,
    target_score: float,
) -> dict[str, Any]:
    return {
        "pair_id": f"pair_{pair_index:010d}",
        "dataset_id": settings.dataset_id,
        "task_id": str(task.get("task_id")),
        "employee_id": candidate["employee_id"],
        "label": label,
        "target_score": target_score,
        "target_mode": settings.target_mode,
        "candidate_rank_hint": rank,
        "features_ref": {
            "factors": candidate["factors"],
            "generated_at": utc_now_iso(),
        },
        "split": "train",
    }


def build_training_pairs(
    employees: list[dict[str, Any]],
    tasks: list[dict[str, Any]],
    assignment_history: list[dict[str, Any]],
    settings: TrainingPairSettings,
) -> list[dict[str, Any]]:
    validate_training_pair_settings(settings)
    validate_training_pair_inputs(employees, tasks)

    rng = random.Random(settings.seed)
    history_metrics = aggregate_history_metrics(assignment_history)
    pairs: list[dict[str, Any]] = []
    pair_index = 1

    positive_target = settings.target_pairs // 2
    negative_target = settings.target_pairs - positive_target
    positive_count = 0
    negative_count = 0

    shuffled_tasks = list(tasks)
    rng.shuffle(shuffled_tasks)

    while len(pairs) < settings.target_pairs:
        for task in shuffled_tasks:
            if len(pairs) >= settings.target_pairs:
                break

            ranked = ranked_candidates_for_task(
                task=task,
                employees=employees,
                history_metrics=history_metrics,
                target_mode=settings.target_mode,
            )

            if not ranked:
                raise TrainingPairsGenerationError(
                    "No ranked candidates could be produced"
                )

            candidate, label, positive_count = select_candidate(
                ranked=ranked,
                rng=rng,
                positive_count=positive_count,
                positive_target=positive_target,
                candidates_per_task=settings.candidates_per_task,
            )
            negative_count += int(label == 0)

            rank = candidate_rank(ranked, candidate)
            target_score = normalize_target_score(
                candidate_score=safe_float(candidate.get("score"), 0.5),
                label=label,
                rng=rng,
            )

            pair = build_pair(
                pair_index=pair_index,
                settings=settings,
                task=task,
                candidate=candidate,
                label=label,
                rank=rank,
                target_score=target_score,
            )

            missing_required = validate_record_required_fields("training_pairs", pair)
            if missing_required:
                missing = ", ".join(missing_required)
                raise TrainingPairsGenerationError(
                    f"Generated pair {pair['pair_id']} missing required fields: "
                    f"{missing}"
                )

            pairs.append(pair)
            pair_index += 1

            if positive_count >= positive_target and negative_count >= negative_target:
                break

    return pairs[: settings.target_pairs]


def assign_splits(
    pairs: list[dict[str, Any]],
    seed: int | None,
    train_share: float = 0.8,
    validation_share: float = 0.1,
) -> list[dict[str, Any]]:
    if train_share <= 0 or validation_share < 0:
        raise TrainingPairsGenerationError(
            "train_share must be positive and validation_share must be non-negative"
        )

    if train_share + validation_share >= 1:
        raise TrainingPairsGenerationError(
            "train_share + validation_share must be less than 1"
        )

    rng = random.Random(seed)
    shuffled = list(pairs)
    rng.shuffle(shuffled)

    total = len(shuffled)
    train_cut = int(total * train_share)
    validation_cut = train_cut + int(total * validation_share)

    for index, pair in enumerate(shuffled):
        if index < train_cut:
            pair["split"] = "train"
        elif index < validation_cut:
            pair["split"] = "validation"
        else:
            pair["split"] = "test"

    return shuffled


def serialize_features_ref(value: Any) -> str:
    return str(value or {})


def write_training_pairs_parquet(path: Path, pairs: list[dict[str, Any]]) -> None:
    try:
        import pandas as pd
    except ImportError as exc:
        raise TrainingPairsGenerationError(
            "pandas is required to write training_pairs.parquet"
        ) from exc

    path.parent.mkdir(parents=True, exist_ok=True)

    rows: list[dict[str, Any]] = []
    for pair in pairs:
        row = dict(pair)
        row["features_ref"] = serialize_features_ref(row.get("features_ref"))
        rows.append(row)

    frame = pd.DataFrame(rows)
    try:
        frame.to_parquet(path, index=False)
    except Exception as exc:
        raise TrainingPairsGenerationError(
            "Could not write training_pairs.parquet. "
            "Check that pyarrow or fastparquet is installed."
        ) from exc


def summarize_training_pairs(pairs: list[dict[str, Any]]) -> dict[str, Any]:
    labels = {0: 0, 1: 0}
    splits: dict[str, int] = {}

    for pair in pairs:
        label = int(pair["label"])
        labels[label] = labels.get(label, 0) + 1
        split = str(pair.get("split", "unknown"))
        splits[split] = splits.get(split, 0) + 1

    avg_score = sum(
        safe_float(pair.get("target_score"), 0.0)
        for pair in pairs
    ) / max(1, len(pairs))

    return {
        "pairs": len(pairs),
        "positive_examples": labels.get(1, 0),
        "negative_examples": labels.get(0, 0),
        "split_counts": dict(sorted(splits.items())),
        "avg_target_score": round(avg_score, 4),
    }
