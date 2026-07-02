from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd
import yaml

from src.data.generate_assignments import generate_assignments, save_assignments
from src.data.generate_employees import generate_employees, save_employees
from src.data.generate_tasks import generate_tasks, save_tasks

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SYNTHETIC_DATA_CONFIG_PATH = PROJECT_ROOT / "config" / "synthetic_data.yaml"


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def assert_file_exists(path: Path) -> None:
    if not path.exists():
        raise FileNotFoundError(f"Expected generated file does not exist: {path}")


def print_dataset_stats() -> None:
    config = load_yaml(SYNTHETIC_DATA_CONFIG_PATH)

    employees_path = PROJECT_ROOT / config["output"]["employees_csv"]
    tasks_path = PROJECT_ROOT / config["output"]["tasks_csv"]
    assignments_path = PROJECT_ROOT / config["output"]["assignments_csv"]

    assert_file_exists(employees_path)
    assert_file_exists(tasks_path)
    assert_file_exists(assignments_path)

    employees = pd.read_csv(employees_path)
    tasks = pd.read_csv(tasks_path)
    assignments = pd.read_csv(assignments_path)

    print()
    print("Synthetic data summary")
    print("======================")
    print(f"Employees: {len(employees)}")
    print(f"Tasks: {len(tasks)}")
    print(f"Assignments: {len(assignments)}")

    print()
    print("Employees by role:")
    print(employees["role"].value_counts().to_string())

    print()
    print("Tasks by type:")
    print(tasks["task_type"].value_counts().sort_index().to_string())

    print()
    print("Tasks by project:")
    print(tasks["project_key"].value_counts().sort_index().to_string())

    print()
    print("Success label distribution:")
    print(assignments["success_label"].value_counts(normalize=True).sort_index().to_string())

    print()
    print("Average workload:")
    print(round(float(employees["current_workload"].mean()), 3))

    print()
    print("Average skill match:")
    print(round(float(assignments["skill_match_score"].mean()), 3))


def main() -> None:
    print("Generating synthetic employees...")
    employees = generate_employees()
    save_employees(employees)

    print()
    print("Generating synthetic tasks...")
    tasks = generate_tasks()
    save_tasks(tasks)

    print()
    print("Generating synthetic assignment history...")
    assignments = generate_assignments()
    save_assignments(assignments)

    print_dataset_stats()

    print()
    print("Synthetic data generation completed.")


if __name__ == "__main__":
    main()