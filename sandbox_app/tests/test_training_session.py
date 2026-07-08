from __future__ import annotations

import json
import shutil

import pandas as pd
from sandbox_app.backend.core.paths import PATHS
from sandbox_app.backend.training.train_session import (
    TRAINING_SESSIONS_DIR,
    TrainingSessionConfig,
    list_training_sessions,
    read_training_session,
    run_training_session,
)


def write_json(path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def test_run_training_session_with_baseline_and_logistic_regression() -> None:
    dataset_id = "pytest_training_session"
    dataset_dir = PATHS.data_dir / "generated" / dataset_id
    features_dir = dataset_dir / "features"

    if dataset_dir.exists():
        shutil.rmtree(dataset_dir)

    dataset_dir.mkdir(parents=True, exist_ok=True)
    features_dir.mkdir(parents=True, exist_ok=True)

    features = pd.DataFrame(
        [
            {
                "pair_id": "pair_001",
                "skill_match_ratio": 1.0,
                "employee_avg_quality_score": 0.9,
                "employee_deadline_reliability": 0.9,
                "employee_availability_score": 0.8,
                "pair_workload_pressure": 0.2,
                "employee_fatigue_score": 0.1,
            },
            {
                "pair_id": "pair_002",
                "skill_match_ratio": 0.1,
                "employee_avg_quality_score": 0.4,
                "employee_deadline_reliability": 0.4,
                "employee_availability_score": 0.3,
                "pair_workload_pressure": 0.9,
                "employee_fatigue_score": 0.8,
            },
            {
                "pair_id": "pair_003",
                "skill_match_ratio": 0.8,
                "employee_avg_quality_score": 0.7,
                "employee_deadline_reliability": 0.8,
                "employee_availability_score": 0.7,
                "pair_workload_pressure": 0.3,
                "employee_fatigue_score": 0.2,
            },
            {
                "pair_id": "pair_004",
                "skill_match_ratio": 0.2,
                "employee_avg_quality_score": 0.3,
                "employee_deadline_reliability": 0.3,
                "employee_availability_score": 0.2,
                "pair_workload_pressure": 0.95,
                "employee_fatigue_score": 0.9,
            },
        ]
    )
    targets = pd.DataFrame(
        [
            {
                "pair_id": "pair_001",
                "task_id": "task_001",
                "employee_id": "employee_001",
                "split": "train",
                "target_mode": "balanced",
                "target_score": 0.92,
                "label": 1,
            },
            {
                "pair_id": "pair_002",
                "task_id": "task_001",
                "employee_id": "employee_002",
                "split": "train",
                "target_mode": "balanced",
                "target_score": 0.15,
                "label": 0,
            },
            {
                "pair_id": "pair_003",
                "task_id": "task_002",
                "employee_id": "employee_001",
                "split": "test",
                "target_mode": "balanced",
                "target_score": 0.81,
                "label": 1,
            },
            {
                "pair_id": "pair_004",
                "task_id": "task_002",
                "employee_id": "employee_002",
                "split": "test",
                "target_mode": "balanced",
                "target_score": 0.12,
                "label": 0,
            },
        ]
    )

    features.to_parquet(features_dir / "features.parquet", index=False)
    targets.to_parquet(features_dir / "targets.parquet", index=False)

    write_json(
        features_dir / "feature_metadata.json",
        {
            "dataset_id": dataset_id,
            "dataset_kind": "generated",
            "target_mode": "balanced",
            "feature_dimensions": {"feature_count": 6},
        },
    )
    write_json(
        dataset_dir / "dataset_metadata.json",
        {
            "dataset_id": dataset_id,
            "dataset_type": "generated",
            "counts": {"training_pairs": 4},
        },
    )

    result = run_training_session(
        TrainingSessionConfig(
            dataset_id=dataset_id,
            dataset_kind="generated",
            target_mode="balanced",
            model_names=["baseline_rule_based", "logistic_regression"],
            seed=16001,
            auto_build_features=False,
        )
    )

    session_id = result["session_id"]
    session_dir = TRAINING_SESSIONS_DIR / session_id

    assert result["status"] == "completed"
    assert (session_dir / "session_config.json").exists()
    assert (session_dir / "session_summary.json").exists()
    assert (session_dir / "comparison_metrics.json").exists()
    assert (session_dir / "comparison_metrics.csv").exists()
    assert (session_dir / "models" / "baseline_rule_based" / "model.joblib").exists()
    assert (session_dir / "models" / "logistic_regression" / "model.joblib").exists()
    assert (
        session_dir / "models" / "baseline_rule_based" / "predictions.parquet"
    ).exists()

    details = read_training_session(session_id)
    assert details["summary"]["session_id"] == session_id

    sessions = list_training_sessions()
    assert any(item["session_id"] == session_id for item in sessions["sessions"])

    shutil.rmtree(dataset_dir)
    shutil.rmtree(session_dir)