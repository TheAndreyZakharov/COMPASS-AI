from __future__ import annotations

from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd


class RuleBasedAssignmentModel:
    model_name = "baseline_rule_based"

    def __init__(self, weights: dict[str, float] | None = None) -> None:
        self.weights = weights or {
            "skill_match_ratio": 0.3,
            "employee_avg_quality_score": 0.2,
            "employee_deadline_reliability": 0.16,
            "employee_availability_score": 0.14,
            "workload_fit": 0.12,
            "fatigue_fit": 0.08,
        }

    def fit(self, features: pd.DataFrame, labels: pd.Series) -> RuleBasedAssignmentModel:
        _ = features
        _ = labels
        return self

    def predict_score(self, features: pd.DataFrame) -> np.ndarray:
        scores = np.zeros(len(features), dtype=float)

        skill_match = features.get("skill_match_ratio", 0.0)
        quality = features.get("employee_avg_quality_score", 0.5)
        reliability = features.get("employee_deadline_reliability", 0.5)
        availability = features.get("employee_availability_score", 0.5)
        workload = features.get("pair_workload_pressure", 0.5)
        fatigue = features.get("employee_fatigue_score", 0.5)

        scores += self.weights["skill_match_ratio"] * np.asarray(skill_match, dtype=float)
        scores += self.weights["employee_avg_quality_score"] * np.asarray(quality, dtype=float)
        scores += self.weights["employee_deadline_reliability"] * np.asarray(
            reliability,
            dtype=float,
        )
        scores += self.weights["employee_availability_score"] * np.asarray(
            availability,
            dtype=float,
        )
        scores += self.weights["workload_fit"] * (1.0 - np.asarray(workload, dtype=float))
        scores += self.weights["fatigue_fit"] * (1.0 - np.asarray(fatigue, dtype=float))

        return np.clip(scores, 0.0, 1.0)

    def predict_proba(self, features: pd.DataFrame) -> np.ndarray:
        positive_scores = self.predict_score(features)
        negative_scores = 1.0 - positive_scores
        return np.vstack([negative_scores, positive_scores]).T

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self, path)


def train_baseline_model(
    features: pd.DataFrame,
    labels: pd.Series,
    params: dict[str, Any] | None = None,
) -> RuleBasedAssignmentModel:
    weights = None
    if params:
        raw_weights = params.get("weights")
        if isinstance(raw_weights, dict):
            weights = {str(key): float(value) for key, value in raw_weights.items()}

    return RuleBasedAssignmentModel(weights=weights).fit(features, labels)