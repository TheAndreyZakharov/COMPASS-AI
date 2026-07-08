from __future__ import annotations

import json
import shutil

import pandas as pd
from sandbox_app.backend.core.paths import PATHS
from sandbox_app.backend.reports.training_report import (
    generate_training_report,
    read_training_report,
    read_training_report_html,
)
from sandbox_app.backend.training.train_session import (
    TRAINING_SESSIONS_DIR,
    TrainingSessionConfig,
    run_training_session,
)


def write_json(path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def test_generate_training_report_for_session() -> None:
    dataset_id = "pytest_training_reports"
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
                "employee_avg_quality_score": 0.95,
                "employee_deadline_reliability": 0.9,
                "employee_availability_score": 0.85,
                "pair_workload_pressure": 0.15,
                "employee_fatigue_score": 0.1,
            },
            {
                "pair_id": "pair_002",
                "skill_match_ratio": 0.0,
                "employee_avg_quality_score": 0.25,
                "employee_deadline_reliability": 0.35,
                "employee_availability_score": 0.2,
                "pair_workload_pressure": 0.95,
                "employee_fatigue_score": 0.9,
            },
            {
                "pair_id": "pair_003",
                "skill_match_ratio": 0.9,
                "employee_avg_quality_score": 0.82,
                "employee_deadline_reliability": 0.8,
                "employee_availability_score": 0.75,
                "pair_workload_pressure": 0.25,
                "employee_fatigue_score": 0.2,
            },
            {
                "pair_id": "pair_004",
                "skill_match_ratio": 0.1,
                "employee_avg_quality_score": 0.3,
                "employee_deadline_reliability": 0.25,
                "employee_availability_score": 0.25,
                "pair_workload_pressure": 0.92,
                "employee_fatigue_score": 0.85,
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
                "target_score": 0.95,
                "label": 1,
            },
            {
                "pair_id": "pair_002",
                "task_id": "task_001",
                "employee_id": "employee_002",
                "split": "train",
                "target_mode": "balanced",
                "target_score": 0.05,
                "label": 0,
            },
            {
                "pair_id": "pair_003",
                "task_id": "task_002",
                "employee_id": "employee_001",
                "split": "test",
                "target_mode": "balanced",
                "target_score": 0.88,
                "label": 1,
            },
            {
                "pair_id": "pair_004",
                "task_id": "task_002",
                "employee_id": "employee_002",
                "split": "test",
                "target_mode": "balanced",
                "target_score": 0.08,
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
            seed=18001,
            auto_build_features=False,
        )
    )
    session_id = result["session_id"]
    session_dir = TRAINING_SESSIONS_DIR / session_id

    manifest = generate_training_report(session_id)

    assert manifest["status"] == "generated"
    assert (session_dir / "reports" / "training_report.html").exists()
    assert (session_dir / "reports" / "report_manifest.json").exists()
    assert (session_dir / "reports" / "plots" / "model_comparison.png").exists()

    model_plot_dirs = list((session_dir / "reports" / "plots").glob("*"))
    assert model_plot_dirs

    loaded_manifest = read_training_report(session_id)
    assert loaded_manifest["session_id"] == session_id

    html_text = read_training_report_html(session_id)
    assert "Training report" in html_text
    assert "Model comparison" in html_text

    shutil.rmtree(dataset_dir)
    shutil.rmtree(session_dir)