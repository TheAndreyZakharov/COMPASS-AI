from __future__ import annotations

import json
import shutil

import pandas as pd
from sandbox_app.backend.core.paths import PATHS
from sandbox_app.backend.features.build_features import (
    FeatureBuildConfig,
    build_features_for_dataset,
)


def write_json(path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def test_build_features_for_generated_dataset() -> None:
    dataset_id = "pytest_feature_builder"
    dataset_dir = PATHS.data_dir / "generated" / dataset_id

    if dataset_dir.exists():
        shutil.rmtree(dataset_dir)

    dataset_dir.mkdir(parents=True, exist_ok=True)

    write_json(
        dataset_dir / "employees.json",
        [
            {
                "employee_id": "employee_001",
                "name": "Alice",
                "role": "backend",
                "grade": "middle",
                "skills": ["python", "fastapi"],
                "learning_goals": ["ml"],
                "availability_score": 0.8,
                "current_workload": 0.35,
                "fatigue_score": 0.2,
                "avg_completion_speed": 1.1,
                "avg_quality_score": 0.88,
                "deadline_reliability": 0.91,
                "mentor_level": 0.4,
                "custom_features": {"domain_depth": 0.7, "remote_ready": True},
            }
        ],
    )
    write_json(
        dataset_dir / "tasks.json",
        [
            {
                "task_id": "task_001",
                "title": "Build API",
                "project_id": "project_001",
                "status": "todo",
                "priority": "high",
                "task_type": "backend",
                "complexity": 0.65,
                "deadline_days": 5,
                "estimated_hours": 12,
                "required_skills": ["python", "fastapi"],
                "custom_features": {"requires_review": True},
            }
        ],
    )
    write_json(
        dataset_dir / "assignment_history.json",
        [
            {
                "assignment_id": "assignment_001",
                "employee_id": "employee_001",
                "task_id": "task_000",
                "planned_hours": 6,
                "actual_hours": 7,
                "quality_score": 0.84,
                "deadline_status": "on_time",
                "outcome_label": "good",
                "was_rework_needed": False,
            }
        ],
    )
    pd.DataFrame(
        [
            {
                "pair_id": "pair_001",
                "task_id": "task_001",
                "employee_id": "employee_001",
                "label": 1,
                "target_score": 0.9,
                "target_mode": "balanced",
                "split": "train",
            }
        ]
    ).to_parquet(dataset_dir / "training_pairs.parquet", index=False)

    result = build_features_for_dataset(
        FeatureBuildConfig(
            dataset_id=dataset_id,
            dataset_kind="generated",
            target_mode="balanced",
            overwrite=True,
        )
    )

    features_dir = dataset_dir / "features"
    assert result["status"] == "built"
    assert (features_dir / "features.parquet").exists()
    assert (features_dir / "targets.parquet").exists()
    assert (features_dir / "feature_metadata.json").exists()

    metadata = json.loads(
        (features_dir / "feature_metadata.json").read_text(encoding="utf-8")
    )
    assert metadata["feature_dimensions"]["feature_count"] > 0
    assert metadata["output_counts"]["feature_rows"] == 1

    features = pd.read_parquet(features_dir / "features.parquet")
    targets = pd.read_parquet(features_dir / "targets.parquet")

    assert len(features) == 1
    assert len(targets) == 1
    assert "skill_match_ratio" in features.columns

    shutil.rmtree(dataset_dir)