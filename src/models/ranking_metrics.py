from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]

TEST_PATH = PROJECT_ROOT / "data" / "processed" / "test.parquet"
TEST_PREDICTIONS_PATH = PROJECT_ROOT / "reports" / "test_predictions.csv"
RANKING_METRICS_PATH = PROJECT_ROOT / "reports" / "ranking_metrics.json"


def precision_at_k(labels: list[int], k: int) -> float:
    if not labels:
        return 0.0

    top_k = labels[:k]

    if not top_k:
        return 0.0

    return float(sum(top_k) / k)


def dcg_at_k(labels: list[int], k: int) -> float:
    labels_at_k = labels[:k]

    return float(
        sum(
            (2**label - 1) / np.log2(index + 2)
            for index, label in enumerate(labels_at_k)
        )
    )


def ndcg_at_k(labels: list[int], k: int) -> float:
    actual_dcg = dcg_at_k(labels, k)
    ideal_labels = sorted(labels, reverse=True)
    ideal_dcg = dcg_at_k(ideal_labels, k)

    if ideal_dcg == 0:
        return 0.0

    return float(actual_dcg / ideal_dcg)


def reciprocal_rank(labels: list[int]) -> float:
    for index, label in enumerate(labels, start=1):
        if label == 1:
            return float(1 / index)

    return 0.0


def evaluate_ranking(
    data: pd.DataFrame,
    score_column: str,
) -> dict[str, float]:
    precision_1_values: list[float] = []
    precision_3_values: list[float] = []
    ndcg_3_values: list[float] = []
    reciprocal_rank_values: list[float] = []

    for _, group in data.groupby("task_id"):
        ranked = group.sort_values(score_column, ascending=False)
        labels = ranked["success_label"].astype(int).tolist()

        precision_1_values.append(precision_at_k(labels, 1))
        precision_3_values.append(precision_at_k(labels, 3))
        ndcg_3_values.append(ndcg_at_k(labels, 3))
        reciprocal_rank_values.append(reciprocal_rank(labels))

    return {
        "precision_at_1": float(np.mean(precision_1_values)),
        "precision_at_3": float(np.mean(precision_3_values)),
        "ndcg_at_3": float(np.mean(ndcg_3_values)),
        "mrr": float(np.mean(reciprocal_rank_values)),
        "tasks_evaluated": float(data["task_id"].nunique()),
        "rows_evaluated": float(len(data)),
    }


def add_random_baseline(data: pd.DataFrame, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    result = data.copy()
    result["random_score"] = rng.random(len(result))
    return result


def add_rule_based_baseline(data: pd.DataFrame) -> pd.DataFrame:
    result = data.copy()

    required_columns = {
        "pair_skill_match_score",
        "pair_growth_match_score",
        "pair_speed_score",
        "pair_risk_score",
        "pair_role_affinity",
        "pair_workload_pressure",
        "employee_avg_quality_score",
        "employee_deadline_reliability",
    }

    missing_columns = required_columns - set(result.columns)

    if missing_columns:
        raise ValueError(f"Missing rule-based columns: {sorted(missing_columns)}")

    result["rule_based_score"] = (
        0.30 * result["pair_skill_match_score"]
        + 0.10 * result["pair_growth_match_score"]
        + 0.15 * result["pair_speed_score"]
        + 0.15 * result["employee_avg_quality_score"]
        + 0.15 * result["employee_deadline_reliability"]
        + 0.10 * result["pair_role_affinity"]
        + 0.05 * (1.0 - result["pair_workload_pressure"])
        - 0.10 * result["pair_risk_score"]
    )

    return result


def load_ranking_data() -> pd.DataFrame:
    if not TEST_PATH.exists():
        raise FileNotFoundError(f"Missing test data: {TEST_PATH}")

    if not TEST_PREDICTIONS_PATH.exists():
        raise FileNotFoundError(
            f"Missing test predictions: {TEST_PREDICTIONS_PATH}. "
            "Run: python src/models/evaluate.py"
        )

    test_data = pd.read_parquet(TEST_PATH)
    predictions = pd.read_csv(TEST_PREDICTIONS_PATH)

    merged = test_data.merge(
        predictions[
            [
                "assignment_id",
                "success_probability",
            ]
        ],
        on="assignment_id",
        how="inner",
    )

    if len(merged) != len(test_data):
        raise ValueError(
            f"Predictions merge changed row count: {len(test_data)} -> {len(merged)}"
        )

    return merged


def save_ranking_metrics(metrics: dict[str, dict[str, float]]) -> None:
    RANKING_METRICS_PATH.parent.mkdir(parents=True, exist_ok=True)

    rounded = {
        model_name: {
            metric_name: round(metric_value, 6)
            for metric_name, metric_value in model_metrics.items()
        }
        for model_name, model_metrics in metrics.items()
    }

    with RANKING_METRICS_PATH.open("w", encoding="utf-8") as file:
        json.dump(rounded, file, ensure_ascii=False, indent=2)


def main() -> None:
    data = load_ranking_data()
    data = add_random_baseline(data)
    data = add_rule_based_baseline(data)

    metrics = {
        "ml_model": evaluate_ranking(data, "success_probability"),
        "rule_based_baseline": evaluate_ranking(data, "rule_based_score"),
        "random_baseline": evaluate_ranking(data, "random_score"),
    }

    save_ranking_metrics(metrics)

    print(f"Ranking metrics saved: {RANKING_METRICS_PATH}")
    print(json.dumps(metrics, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()