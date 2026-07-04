from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from src.features.skill_vectorizer import (
    load_json_cell,
    load_skill_vocab,
    normalize_skill_name,
    task_required_skill_vector,
)
from src.features.text_embeddings import EMBEDDING_DIM, load_task_text_embeddings

PROJECT_ROOT = Path(__file__).resolve().parents[2]

EMPLOYEES_PATH = PROJECT_ROOT / "data" / "synthetic" / "employees.csv"
TASKS_PATH = PROJECT_ROOT / "data" / "synthetic" / "tasks.csv"
ASSIGNMENTS_PATH = PROJECT_ROOT / "data" / "synthetic" / "assignments.csv"

TRAINING_PAIRS_PATH = PROJECT_ROOT / "data" / "processed" / "training_pairs.parquet"
FEATURE_METADATA_PATH = PROJECT_ROOT / "data" / "processed" / "feature_metadata.json"

ID_COLUMNS = {
    "assignment_id",
    "task_id",
    "employee_id",
    "plane_work_item_id",
    "plane_issue_id",
}

TASK_TYPES = [
    "analytics_report",
    "api_integration",
    "backend_feature",
    "bugfix",
    "database_migration",
    "devops_task",
    "documentation_task",
    "frontend_feature",
    "ml_pipeline",
    "refactoring",
    "security_task",
    "testing_task",
]

PROJECT_KEYS = ["BACK", "DATA", "FRONT", "TOOLS"]

ROLES = [
    "backend_developer",
    "frontend_developer",
    "qa_engineer",
    "data_ml_engineer",
    "devops_engineer",
    "team_lead",
]

GRADES = ["junior", "middle", "senior", "lead"]

AVAILABILITY_VALUES = ["available", "limited", "overloaded"]

PRIORITY_MAP = {
    "none": 0.0,
    "low": 0.25,
    "medium": 0.5,
    "high": 0.75,
    "urgent": 1.0,
}

ROLE_TASK_AFFINITY = {
    "backend_feature": {
        "backend_developer": 1.0,
        "team_lead": 0.8,
    },
    "api_integration": {
        "backend_developer": 1.0,
        "team_lead": 0.8,
        "data_ml_engineer": 0.45,
    },
    "database_migration": {
        "backend_developer": 0.9,
        "data_ml_engineer": 0.65,
        "devops_engineer": 0.55,
    },
    "security_task": {
        "backend_developer": 0.8,
        "devops_engineer": 0.75,
        "team_lead": 0.65,
    },
    "frontend_feature": {
        "frontend_developer": 1.0,
        "team_lead": 0.75,
    },
    "bugfix": {
        "backend_developer": 0.8,
        "frontend_developer": 0.8,
        "qa_engineer": 0.7,
    },
    "refactoring": {
        "backend_developer": 0.75,
        "frontend_developer": 0.75,
        "team_lead": 0.65,
    },
    "ml_pipeline": {
        "data_ml_engineer": 1.0,
        "backend_developer": 0.45,
        "devops_engineer": 0.35,
    },
    "analytics_report": {
        "data_ml_engineer": 0.9,
        "qa_engineer": 0.45,
        "team_lead": 0.35,
    },
    "devops_task": {
        "devops_engineer": 1.0,
        "backend_developer": 0.45,
        "team_lead": 0.45,
    },
    "testing_task": {
        "qa_engineer": 1.0,
        "backend_developer": 0.45,
        "frontend_developer": 0.45,
    },
    "documentation_task": {
        "qa_engineer": 0.6,
        "team_lead": 0.65,
        "backend_developer": 0.35,
        "frontend_developer": 0.35,
        "data_ml_engineer": 0.35,
    },
}


def clamp(value: float, min_value: float = 0.0, max_value: float = 1.0) -> float:
    return max(min_value, min(max_value, value))


def safe_float(value: Any, default: float = 0.0) -> float:
    if value is None:
        return default

    if isinstance(value, float) and math.isnan(value):
        return default

    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def safe_bool(value: Any) -> float:
    if isinstance(value, bool):
        return float(value)

    if isinstance(value, (int, float)):
        return float(value > 0)

    if isinstance(value, str):
        return float(value.strip().lower() in {"1", "true", "yes", "y"})

    return 0.0


def nullable_string(value: Any) -> str | None:
    if value is None:
        return None

    if isinstance(value, float) and math.isnan(value):
        return None

    text = str(value).strip()
    return text if text else None


def one_hot(value: Any, vocabulary: list[str], prefix: str) -> dict[str, float]:
    normalized_value = str(value or "").strip()

    return {f"{prefix}_{item}": float(normalized_value == item) for item in vocabulary}


def normalize_priority(value: Any) -> float:
    return PRIORITY_MAP.get(str(value or "medium").strip().lower(), 0.5)


def role_affinity_score(task_type: str, role: str) -> float:
    task_mapping = ROLE_TASK_AFFINITY.get(str(task_type or ""), {})
    return float(task_mapping.get(str(role or ""), 0.15))


def required_skill_dict(task: pd.Series) -> dict[str, float]:
    raw = load_json_cell(task.get("required_skills"), default={})

    if isinstance(raw, dict):
        result = {}
        for skill, level in raw.items():
            result[normalize_skill_name(skill)] = safe_float(level, default=0.0)

        return result

    if isinstance(raw, list):
        return {normalize_skill_name(skill): 3.0 for skill in raw}

    return {}


def employee_skill_dict(employee: pd.Series) -> dict[str, float]:
    raw = load_json_cell(employee.get("skills"), default={})

    if not isinstance(raw, dict):
        return {}

    result = {}
    for skill, level in raw.items():
        result[normalize_skill_name(skill)] = safe_float(level, default=0.0)

    return result


def mean_skill_gap(
    required_skills: dict[str, float],
    employee_skills: dict[str, float],
) -> float:
    if not required_skills:
        return 0.0

    gaps = []

    for skill, required_level in required_skills.items():
        employee_level = employee_skills.get(skill, 0.0)
        gap = max(required_level - employee_level, 0.0) / 5.0
        gaps.append(gap)

    return round(float(np.mean(gaps)), 6)


def max_skill_gap(
    required_skills: dict[str, float],
    employee_skills: dict[str, float],
) -> float:
    if not required_skills:
        return 0.0

    gaps = []

    for skill, required_level in required_skills.items():
        employee_level = employee_skills.get(skill, 0.0)
        gap = max(required_level - employee_level, 0.0) / 5.0
        gaps.append(gap)

    return round(float(np.max(gaps)), 6)


def overqualified_ratio(
    required_skills: dict[str, float],
    employee_skills: dict[str, float],
) -> float:
    if not required_skills:
        return 0.0

    overqualified = 0

    for skill, required_level in required_skills.items():
        employee_level = employee_skills.get(skill, 0.0)

        if employee_level >= required_level + 1.0:
            overqualified += 1

    return round(overqualified / len(required_skills), 6)


def complexity_gap(task_complexity: float, grade: str) -> float:
    comfortable_complexity = {
        "junior": 2.0,
        "middle": 3.5,
        "senior": 5.0,
        "lead": 5.0,
    }.get(str(grade or ""), 3.0)

    return clamp((task_complexity - comfortable_complexity) / 5.0)


def deadline_pressure(deadline_days: float) -> float:
    if deadline_days <= 1:
        return 1.0

    if deadline_days >= 60:
        return 0.0

    return clamp(1.0 - (deadline_days / 60.0))


def workload_pressure(workload: float) -> float:
    return clamp(workload)


def build_task_features(
    task: pd.Series,
    text_embedding: np.ndarray,
) -> dict[str, float]:
    deadline_days = safe_float(task.get("deadline_days"), 14.0)

    features: dict[str, float] = {
        "task_complexity": safe_float(task.get("complexity"), 3.0) / 5.0,
        "task_priority_score": normalize_priority(task.get("priority")),
        "task_business_criticality": safe_float(
            task.get("business_criticality"),
            3.0,
        )
        / 5.0,
        "task_deadline_days": clamp(deadline_days / 60.0),
        "task_deadline_pressure": deadline_pressure(deadline_days),
        "task_estimated_hours": clamp(
            safe_float(task.get("estimated_hours"), 8.0) / 120.0,
        ),
        "task_dependencies_count": clamp(
            safe_float(task.get("dependencies_count"), 0.0) / 10.0,
        ),
        "task_is_growth_task": safe_bool(task.get("is_growth_task")),
    }

    features.update(one_hot(task.get("task_type"), TASK_TYPES, "task_type"))
    features.update(one_hot(task.get("project_key"), PROJECT_KEYS, "project"))

    for index, value in enumerate(text_embedding):
        features[f"task_text_embedding_{index:03d}"] = float(value)

    return features


def build_employee_features(
    employee: pd.Series,
    skill_names: list[str],
) -> dict[str, float]:
    employee_skills = employee_skill_dict(employee)
    skill_vector = [
        clamp(employee_skills.get(skill_name, 0.0) / 5.0) for skill_name in skill_names
    ]

    features: dict[str, float] = {
        "employee_experience_years": clamp(
            safe_float(employee.get("experience_years"), 0.0) / 15.0,
        ),
        "employee_current_workload": clamp(
            safe_float(employee.get("current_workload"), 0.0),
        ),
        "employee_active_tasks_count": clamp(
            safe_float(employee.get("active_tasks_count"), 0.0) / 12.0,
        ),
        "employee_avg_completion_speed": clamp(
            safe_float(employee.get("avg_completion_speed"), 0.5),
        ),
        "employee_avg_quality_score": clamp(
            safe_float(employee.get("avg_quality_score"), 0.5),
        ),
        "employee_deadline_reliability": clamp(
            safe_float(employee.get("deadline_reliability"), 0.5),
        ),
        "employee_mentor_level": clamp(
            safe_float(employee.get("mentor_level"), 0.0) / 5.0,
        ),
    }

    features.update(one_hot(employee.get("role"), ROLES, "employee_role"))
    features.update(one_hot(employee.get("grade"), GRADES, "employee_grade"))
    features.update(
        one_hot(
            employee.get("availability"),
            AVAILABILITY_VALUES,
            "employee_availability",
        ),
    )

    for skill_name, value in zip(skill_names, skill_vector, strict=True):
        features[f"employee_skill_{skill_name}"] = float(value)

    return features


def build_pair_features(
    assignment: pd.Series,
    task: pd.Series,
    employee: pd.Series,
    task_skill_vector: list[float],
    employee_skill_vector: list[float],
) -> dict[str, float]:
    required_skills = required_skill_dict(task)
    employee_skills = employee_skill_dict(employee)

    task_complexity = safe_float(task.get("complexity"), 3.0)
    employee_workload = safe_float(employee.get("current_workload"), 0.0)
    deadline_days = safe_float(task.get("deadline_days"), 14.0)

    task_vector = np.array(task_skill_vector, dtype=np.float32)
    employee_vector = np.array(employee_skill_vector, dtype=np.float32)

    task_norm = float(np.linalg.norm(task_vector))
    employee_norm = float(np.linalg.norm(employee_vector))

    if task_norm > 0 and employee_norm > 0:
        skill_cosine = float(
            np.dot(task_vector, employee_vector) / (task_norm * employee_norm),
        )
    else:
        skill_cosine = 0.0

    return {
        "pair_skill_match_score": clamp(
            safe_float(assignment.get("skill_match_score"), 0.0),
        ),
        "pair_growth_match_score": clamp(
            safe_float(assignment.get("growth_match_score"), 0.0),
        ),
        "pair_speed_score": clamp(
            safe_float(assignment.get("speed_score"), 0.0),
        ),
        "pair_collaboration_score": clamp(
            safe_float(assignment.get("collaboration_score"), 0.0),
        ),
        "pair_risk_score": clamp(
            safe_float(assignment.get("risk_score"), 0.0),
        ),
        "pair_skill_cosine": clamp(skill_cosine),
        "pair_mean_skill_gap": mean_skill_gap(required_skills, employee_skills),
        "pair_max_skill_gap": max_skill_gap(required_skills, employee_skills),
        "pair_overqualified_ratio": overqualified_ratio(
            required_skills,
            employee_skills,
        ),
        "pair_complexity_gap": complexity_gap(
            task_complexity,
            str(employee.get("grade", "")),
        ),
        "pair_deadline_pressure": deadline_pressure(deadline_days),
        "pair_workload_pressure": workload_pressure(employee_workload),
        "pair_role_affinity": role_affinity_score(
            str(task.get("task_type", "")),
            str(employee.get("role", "")),
        ),
    }


def save_feature_metadata(
    path: Path,
    task_feature_columns: list[str],
    employee_feature_columns: list[str],
    pair_feature_columns: list[str],
    label_column: str,
    skill_names: list[str],
) -> None:
    payload = {
        "task_feature_columns": task_feature_columns,
        "employee_feature_columns": employee_feature_columns,
        "pair_feature_columns": pair_feature_columns,
        "label_column": label_column,
        "task_feature_dim": len(task_feature_columns),
        "employee_feature_dim": len(employee_feature_columns),
        "pair_feature_dim": len(pair_feature_columns),
        "skill_vocab_size": len(skill_names),
        "text_embedding_dim": EMBEDDING_DIM,
    }

    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as file:
        json.dump(payload, file, ensure_ascii=False, indent=2)


def feature_columns(dataset: pd.DataFrame, prefix: str) -> list[str]:
    return sorted(
        column
        for column in dataset.columns
        if column.startswith(prefix) and column not in ID_COLUMNS
    )


def build_training_features(
    employees_path: Path = EMPLOYEES_PATH,
    tasks_path: Path = TASKS_PATH,
    assignments_path: Path = ASSIGNMENTS_PATH,
    output_path: Path = TRAINING_PAIRS_PATH,
) -> pd.DataFrame:
    employees = pd.read_csv(employees_path)
    tasks = pd.read_csv(tasks_path)
    assignments = pd.read_csv(assignments_path)

    skill_names = load_skill_vocab()
    text_embeddings = load_task_text_embeddings()

    if len(text_embeddings) != len(tasks):
        raise ValueError(
            f"Embeddings count {len(text_embeddings)} does not match "
            f"tasks count {len(tasks)}"
        )

    employees_by_id = {
        str(row["employee_id"]): row for _, row in employees.iterrows()
    }

    tasks_by_id = {str(row["task_id"]): row for _, row in tasks.iterrows()}

    task_embedding_by_id = {
        str(task_id): text_embeddings[index]
        for index, task_id in enumerate(tasks["task_id"].astype(str).tolist())
    }

    employee_skill_vector_by_id = {
        employee_id: [
            clamp(employee_skill_dict(employee).get(skill_name, 0.0) / 5.0)
            for skill_name in skill_names
        ]
        for employee_id, employee in employees_by_id.items()
    }

    task_skill_vector_by_id = {
        task_id: task_required_skill_vector(task, skill_names)
        for task_id, task in tasks_by_id.items()
    }

    records: list[dict[str, Any]] = []

    for _, assignment in assignments.iterrows():
        task_id = str(assignment["task_id"])
        employee_id = str(assignment["employee_id"])

        task = tasks_by_id.get(task_id)
        employee = employees_by_id.get(employee_id)

        if task is None or employee is None:
            continue

        task_features = build_task_features(task, task_embedding_by_id[task_id])
        employee_features = build_employee_features(employee, skill_names)
        pair_features = build_pair_features(
            assignment=assignment,
            task=task,
            employee=employee,
            task_skill_vector=task_skill_vector_by_id[task_id],
            employee_skill_vector=employee_skill_vector_by_id[employee_id],
        )

        record: dict[str, Any] = {
            "assignment_id": str(assignment["assignment_id"]),
            "task_id": task_id,
            "employee_id": employee_id,
            "plane_work_item_id": nullable_string(
                assignment.get("plane_work_item_id"),
            ),
            "plane_issue_id": nullable_string(assignment.get("plane_issue_id")),
            "success_label": int(assignment["success_label"]),
        }

        record.update(task_features)
        record.update(employee_features)
        record.update(pair_features)

        records.append(record)

    dataset = pd.DataFrame.from_records(records)

    task_feature_columns = feature_columns(dataset, "task_")
    employee_feature_columns = feature_columns(dataset, "employee_")
    pair_feature_columns = feature_columns(dataset, "pair_")

    ordered_columns = [
        "assignment_id",
        "task_id",
        "employee_id",
        "plane_work_item_id",
        "plane_issue_id",
        *task_feature_columns,
        *employee_feature_columns,
        *pair_feature_columns,
        "success_label",
    ]

    dataset = dataset[ordered_columns]

    output_path.parent.mkdir(parents=True, exist_ok=True)
    dataset.to_parquet(output_path, index=False)

    save_feature_metadata(
        path=FEATURE_METADATA_PATH,
        task_feature_columns=task_feature_columns,
        employee_feature_columns=employee_feature_columns,
        pair_feature_columns=pair_feature_columns,
        label_column="success_label",
        skill_names=skill_names,
    )

    return dataset


def main() -> None:
    dataset = build_training_features()

    task_feature_count = len(feature_columns(dataset, "task_"))
    employee_feature_count = len(feature_columns(dataset, "employee_"))
    pair_feature_count = len(feature_columns(dataset, "pair_"))

    print(f"Training features saved: {TRAINING_PAIRS_PATH}")
    print(f"Feature metadata saved: {FEATURE_METADATA_PATH}")
    print(f"Rows: {len(dataset)}")
    print(f"Columns: {len(dataset.columns)}")
    print(f"Success rate: {round(float(dataset['success_label'].mean()), 4)}")
    print(f"Task feature columns: {task_feature_count}")
    print(f"Employee feature columns: {employee_feature_count}")
    print(f"Pair feature columns: {pair_feature_count}")


if __name__ == "__main__":
    main()