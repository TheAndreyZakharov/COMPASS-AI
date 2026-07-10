from __future__ import annotations

from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression, SGDClassifier

SKLEARN_MODEL_NAMES = {
    "sgd_classifier",
    "logistic_regression",
    "random_forest",
    "hist_gradient_boosting",
}


def build_sklearn_model(
    model_name: str,
    seed: int,
    params: dict[str, Any] | None = None,
):
    params = params or {}

    if model_name == "sgd_classifier":
        return SGDClassifier(
            loss=params.get("loss", "log_loss"),
            alpha=float(params.get("alpha", 0.0001)),
            max_iter=int(params.get("max_iter", 1000)),
            random_state=seed,
            class_weight=params.get("class_weight"),
        )

    if model_name == "logistic_regression":
        return LogisticRegression(
            C=float(params.get("C", 1.0)),
            max_iter=int(params.get("max_iter", 1000)),
            solver=str(params.get("solver", "lbfgs")),
            random_state=seed,
            class_weight=params.get("class_weight"),
        )

    if model_name == "random_forest":
        return RandomForestClassifier(
            n_estimators=int(params.get("n_estimators", 120)),
            max_depth=params.get("max_depth"),
            min_samples_leaf=int(params.get("min_samples_leaf", 1)),
            random_state=seed,
            n_jobs=int(params.get("n_jobs", 1)),
            class_weight=params.get("class_weight"),
        )

    if model_name == "hist_gradient_boosting":
        return HistGradientBoostingClassifier(
            learning_rate=float(params.get("learning_rate", 0.08)),
            max_iter=int(params.get("max_iter", 140)),
            max_leaf_nodes=int(params.get("max_leaf_nodes", 31)),
            random_state=seed,
        )

    raise ValueError(f"Unsupported sklearn model: {model_name}")


def train_sklearn_model(
    model_name: str,
    features: pd.DataFrame,
    labels: pd.Series,
    seed: int,
    params: dict[str, Any] | None = None,
):
    model = build_sklearn_model(model_name=model_name, seed=seed, params=params)
    model.fit(features, labels.astype(int))
    return model


def sklearn_positive_scores(model, features: pd.DataFrame) -> np.ndarray:
    if hasattr(model, "predict_proba"):
        probabilities = model.predict_proba(features)
        if probabilities.shape[1] == 1:
            return np.asarray(probabilities[:, 0], dtype=float)
        return np.asarray(probabilities[:, 1], dtype=float)

    if hasattr(model, "decision_function"):
        decision = np.asarray(model.decision_function(features), dtype=float)
        return 1.0 / (1.0 + np.exp(-decision))

    predictions = np.asarray(model.predict(features), dtype=float)
    return np.clip(predictions, 0.0, 1.0)


def save_sklearn_model(model, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, path)
