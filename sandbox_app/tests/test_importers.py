from __future__ import annotations

import json
import shutil

from sandbox_app.backend.utils.importers import (
    IMPORTED_ROOT,
    ImportSource,
    import_dataset_from_sources,
    preview_import_source,
)


def employee_record() -> dict[str, object]:
    return {
        "employee_id": "employee_001",
        "name": "Alice",
        "role": "analyst",
        "grade": "middle",
        "skills": ["python", "analytics"],
        "current_workload": 0.32,
        "fatigue_score": 0.18,
        "availability_score": 0.82,
        "avg_completion_speed": 0.91,
        "avg_quality_score": 0.88,
        "deadline_reliability": 0.93,
        "mentor_level": 0.42,
        "learning_goals": ["data_modeling"],
        "custom_features": {},
    }


def task_record() -> dict[str, object]:
    return {
        "task_id": "task_001",
        "title": "Prepare analysis",
        "description": "Prepare imported dataset analysis.",
        "project_id": "project_001",
        "task_type": "analysis",
        "status": "todo",
        "priority": "high",
        "complexity": 0.45,
        "estimated_hours": 8,
        "deadline_days": 7,
        "required_skills": ["python"],
        "dependencies": [],
        "custom_features": {},
    }


def test_preview_import_source_reads_csv() -> None:
    source = ImportSource(
        table_name="employees",
        filename="employees.csv",
        content=(
            b"employee_id,name,role,grade,skills,current_workload,fatigue_score,"
            b"availability_score,avg_completion_speed,avg_quality_score,"
            b"deadline_reliability,mentor_level,learning_goals,custom_features\n"
            b'employee_001,Alice,analyst,middle,"[""python"",""analytics""]",'
            b'0.32,0.18,0.82,0.91,0.88,0.93,0.42,"[""data_modeling""]",{}\n'
        ),
    )

    preview = preview_import_source(source)

    assert preview["table_name"] == "employees"
    assert preview["format"] == "csv"
    assert preview["rows"] == 1
    assert preview["validation_errors"] == []


def test_import_dataset_from_sources_saves_imported_dataset() -> None:
    dataset_id = "pytest_import_dataset"
    dataset_dir = IMPORTED_ROOT / dataset_id

    if dataset_dir.exists():
        shutil.rmtree(dataset_dir)

    employees = ImportSource(
        table_name="employees",
        filename="employees.json",
        content=json.dumps([employee_record()]).encode("utf-8"),
    )
    tasks = ImportSource(
        table_name="tasks",
        filename="tasks.json",
        content=json.dumps([task_record()]).encode("utf-8"),
    )

    result = import_dataset_from_sources(
        dataset_id,
        [employees, tasks],
        domain_profile="custom",
        overwrite=True,
    )

    assert result["status"] == "imported"
    assert (dataset_dir / "employees.json").exists()
    assert (dataset_dir / "employees.csv").exists()
    assert (dataset_dir / "tasks.json").exists()
    assert (dataset_dir / "tasks.csv").exists()
    assert (dataset_dir / "dataset_metadata.json").exists()
    assert result["metadata"]["dataset_type"] == "imported"

    shutil.rmtree(dataset_dir)