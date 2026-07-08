from __future__ import annotations

import shutil

from sandbox_app.backend.core.paths import PATHS
from sandbox_app.backend.data_generation.dataset import (
    DatasetGenerationError,
    generate_full_dataset,
)


def test_generate_full_dataset_small_preview() -> None:
    dataset_id = "pytest_full_dataset"
    dataset_dir = PATHS.data_dir / "generated" / dataset_id

    if dataset_dir.exists():
        shutil.rmtree(dataset_dir)

    result = generate_full_dataset(
        {
            "dataset_id": dataset_id,
            "domain_profile": "custom",
            "dataset_mode": "small_preview",
            "employees_count": 5,
            "tasks_count": 20,
            "history_depth_per_employee": 4,
            "target_pairs": 100,
            "candidates_per_task": 5,
            "target_mode": "balanced",
            "seed": 901,
            "overwrite": True,
        }
    )

    metadata = result["metadata"]
    generation_report = result["generation_report"]

    assert result["dataset_id"] == dataset_id
    assert metadata["dataset_id"] == dataset_id
    assert metadata["dataset_type"] == "generated"
    assert metadata["domain_profile"] == "custom"
    assert metadata["counts"]["employees"] == 5
    assert metadata["counts"]["tasks"] == 20
    assert metadata["counts"]["assignment_history"] == 20
    assert metadata["counts"]["training_pairs"] == 100
    assert generation_report["status"] == "completed"

    assert (dataset_dir / "employees.json").exists()
    assert (dataset_dir / "employees.csv").exists()
    assert (dataset_dir / "tasks.json").exists()
    assert (dataset_dir / "tasks.csv").exists()
    assert (dataset_dir / "assignment_history.json").exists()
    assert (dataset_dir / "assignment_history.csv").exists()
    assert (dataset_dir / "training_pairs.parquet").exists()
    assert (dataset_dir / "dataset_metadata.json").exists()
    assert (dataset_dir / "generation_report.json").exists()

    shutil.rmtree(dataset_dir)


def test_huge_generation_requires_confirmation() -> None:
    try:
        generate_full_dataset(
            {
                "dataset_id": "pytest_huge_without_confirmation",
                "domain_profile": "custom",
                "dataset_mode": "huge_training",
                "employees_count": 1,
                "tasks_count": 1,
                "target_pairs": 1,
                "seed": 1,
                "overwrite": True,
            }
        )
    except DatasetGenerationError as exc:
        assert "confirm_huge_generation" in str(exc)
    else:
        raise AssertionError("huge_training must require confirmation")