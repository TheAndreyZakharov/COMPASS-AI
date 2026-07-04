from __future__ import annotations

from pathlib import Path
from typing import Any, Literal

import pandas as pd
import torch

from src.models.matching_net import MatchingNetConfig, TaskEmployeeMatchingNet
from src.models.train import select_device

PROJECT_ROOT = Path(__file__).resolve().parents[2]

MODEL_PATH = PROJECT_ROOT / "models" / "compass_matching_model.pt"
TRAINING_PAIRS_PATH = PROJECT_ROOT / "data" / "processed" / "training_pairs.parquet"
EMPLOYEES_PATH = PROJECT_ROOT / "data" / "synthetic" / "employees.csv"

RecommendationMode = Literal[
    "fast_delivery",
    "balanced_workload",
    "growth",
    "risk_minimization",
]


def load_checkpoint(path: Path = MODEL_PATH) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(
            f"Missing model checkpoint: {path}. "
            "Run: python src/models/train.py"
        )

    return torch.load(path, map_location="cpu")


def build_model_from_checkpoint(checkpoint: dict[str, Any]) -> TaskEmployeeMatchingNet:
    config_payload = checkpoint["model_config"]

    config = MatchingNetConfig(
        task_input_dim=int(config_payload["task_input_dim"]),
        employee_input_dim=int(config_payload["employee_input_dim"]),
        pair_input_dim=int(config_payload["pair_input_dim"]),
        task_embedding_dim=int(config_payload["task_embedding_dim"]),
        employee_embedding_dim=int(config_payload["employee_embedding_dim"]),
        hidden_dim=int(config_payload["hidden_dim"]),
        dropout=float(config_payload["dropout"]),
    )

    model = TaskEmployeeMatchingNet(config)
    model.load_state_dict(checkpoint["model_state_dict"])

    return model


def checkpoint_feature_columns(checkpoint: dict[str, Any]) -> dict[str, list[str]]:
    feature_columns = checkpoint["feature_columns"]

    return {
        "task_feature_columns": list(feature_columns["task_feature_columns"]),
        "employee_feature_columns": list(feature_columns["employee_feature_columns"]),
        "pair_feature_columns": list(feature_columns["pair_feature_columns"]),
    }


def _validate_prediction_columns(
    data: pd.DataFrame,
    feature_columns: dict[str, list[str]],
) -> None:
    required_columns = (
        feature_columns["task_feature_columns"]
        + feature_columns["employee_feature_columns"]
        + feature_columns["pair_feature_columns"]
    )

    missing_columns = sorted(set(required_columns) - set(data.columns))

    if missing_columns:
        raise ValueError(f"Missing model feature columns: {missing_columns[:20]}")


def predict_pairs_dataframe(
    data: pd.DataFrame,
    checkpoint_path: Path = MODEL_PATH,
    batch_size: int = 512,
) -> pd.DataFrame:
    checkpoint = load_checkpoint(checkpoint_path)
    feature_columns = checkpoint_feature_columns(checkpoint)
    _validate_prediction_columns(data, feature_columns)

    model = build_model_from_checkpoint(checkpoint)
    device = select_device()
    model.to(device)
    model.eval()

    task_columns = feature_columns["task_feature_columns"]
    employee_columns = feature_columns["employee_feature_columns"]
    pair_columns = feature_columns["pair_feature_columns"]

    probabilities: list[float] = []

    with torch.no_grad():
        for start in range(0, len(data), batch_size):
            batch = data.iloc[start : start + batch_size]

            task_features = torch.tensor(
                batch[task_columns].to_numpy(dtype="float32"),
                dtype=torch.float32,
                device=device,
            )
            employee_features = torch.tensor(
                batch[employee_columns].to_numpy(dtype="float32"),
                dtype=torch.float32,
                device=device,
            )
            pair_features = torch.tensor(
                batch[pair_columns].to_numpy(dtype="float32"),
                dtype=torch.float32,
                device=device,
            )

            output = model(task_features, employee_features, pair_features)

            batch_probabilities = (
                output["success_probability"]
                .detach()
                .cpu()
                .numpy()
                .reshape(-1)
                .tolist()
            )
            probabilities.extend(float(value) for value in batch_probabilities)

    result = data.copy()
    result["success_probability"] = probabilities

    return result


def _column_or_default(row: pd.Series, column: str, default: float = 0.0) -> float:
    if column not in row:
        return default

    value = row[column]

    if pd.isna(value):
        return default

    return float(value)


def mode_adjusted_score(row: pd.Series, mode: RecommendationMode) -> float:
    base_score = _column_or_default(row, "success_probability")

    if mode == "fast_delivery":
        adjustment = (
            0.08 * _column_or_default(row, "pair_speed_score")
            + 0.04 * _column_or_default(row, "employee_deadline_reliability")
            - 0.04 * _column_or_default(row, "pair_deadline_pressure")
        )
    elif mode == "growth":
        adjustment = (
            0.12 * _column_or_default(row, "pair_growth_match_score")
            - 0.05 * _column_or_default(row, "pair_risk_score")
        )
    elif mode == "risk_minimization":
        adjustment = (
            0.07 * _column_or_default(row, "employee_avg_quality_score")
            + 0.07 * _column_or_default(row, "employee_deadline_reliability")
            - 0.10 * _column_or_default(row, "pair_risk_score")
        )
    else:
        adjustment = (
            0.06 * (1.0 - _column_or_default(row, "pair_workload_pressure"))
            - 0.04 * _column_or_default(row, "pair_risk_score")
        )

    return max(0.0, min(1.0, base_score + adjustment))


def load_employee_profiles(path: Path = EMPLOYEES_PATH) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Missing employees file: {path}")

    return pd.read_csv(path)


def score_task_candidates(
    task_id: str,
    mode: RecommendationMode = "balanced_workload",
    top_k: int = 3,
    training_pairs_path: Path = TRAINING_PAIRS_PATH,
) -> list[dict[str, Any]]:
    if not training_pairs_path.exists():
        raise FileNotFoundError(
            f"Missing training pairs: {training_pairs_path}. "
            "Run: make build-features"
        )

    training_pairs = pd.read_parquet(training_pairs_path)
    task_rows = training_pairs[training_pairs["task_id"].astype(str) == str(task_id)]

    if task_rows.empty:
        raise ValueError(f"No precomputed model features found for task_id={task_id}")

    predictions = predict_pairs_dataframe(task_rows)
    predictions["final_score"] = predictions.apply(
        lambda row: mode_adjusted_score(row, mode),
        axis=1,
    )

    employees = load_employee_profiles()
    employee_columns = [
        "employee_id",
        "plane_user_id",
        "name",
        "role",
        "grade",
        "current_workload",
        "avg_quality_score",
        "deadline_reliability",
    ]

    predictions = predictions.merge(
        employees[employee_columns],
        on="employee_id",
        how="left",
    )

    ranked = predictions.sort_values("final_score", ascending=False).head(top_k)

    candidates: list[dict[str, Any]] = []

    for rank, (_, row) in enumerate(ranked.iterrows(), start=1):
        candidates.append(
            {
                "rank": rank,
                "employee_id": str(row["employee_id"]),
                "plane_user_id": str(row.get("plane_user_id", "") or ""),
                "name": str(row.get("name", "")),
                "role": str(row.get("role", "")),
                "grade": str(row.get("grade", "")),
                "score": round(float(row["final_score"]), 6),
                "success_probability": round(float(row["success_probability"]), 6),
                "factors": {
                    "skill_match": round(
                        _column_or_default(row, "pair_skill_match_score"),
                        6,
                    ),
                    "growth_match": round(
                        _column_or_default(row, "pair_growth_match_score"),
                        6,
                    ),
                    "speed": round(_column_or_default(row, "pair_speed_score"), 6),
                    "risk": round(_column_or_default(row, "pair_risk_score"), 6),
                    "role_affinity": round(
                        _column_or_default(row, "pair_role_affinity"),
                        6,
                    ),
                    "workload_pressure": round(
                        _column_or_default(row, "pair_workload_pressure"),
                        6,
                    ),
                    "quality": round(
                        _column_or_default(row, "employee_avg_quality_score"),
                        6,
                    ),
                    "deadline_reliability": round(
                        _column_or_default(row, "employee_deadline_reliability"),
                        6,
                    ),
                },
                "reasons": [
                    "ML model scored this candidate using task, employee and pair features.",
                    f"Mode adjustment applied: {mode}.",
                ],
                "risks": _candidate_risks(row),
                "source": "task_employee_matching_net",
            }
        )

    return candidates


def _candidate_risks(row: pd.Series) -> list[str]:
    risks: list[str] = []

    risk_score = _column_or_default(row, "pair_risk_score")
    workload_pressure = _column_or_default(row, "pair_workload_pressure")
    skill_match = _column_or_default(row, "pair_skill_match_score")

    if risk_score >= 0.65:
        risks.append("High model risk score.")

    if workload_pressure >= 0.75:
        risks.append("Potential workload pressure.")

    if skill_match < 0.50:
        risks.append("Weak skill match for this task.")

    return risks


def main() -> None:
    candidates = score_task_candidates(
        task_id="TASK-0001",
        mode="balanced_workload",
        top_k=3,
    )

    for candidate in candidates:
        print(candidate)


if __name__ == "__main__":
    main()