from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd
import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SYNTHETIC_SCHEMA_PATH = PROJECT_ROOT / "config" / "synthetic_schema.yaml"
EMPLOYEES_PATH = PROJECT_ROOT / "data" / "synthetic" / "employees.csv"
TASKS_PATH = PROJECT_ROOT / "data" / "synthetic" / "tasks.csv"
SKILL_VOCAB_PATH = PROJECT_ROOT / "data" / "processed" / "skill_vocab.json"


@dataclass(frozen=True)
class SkillVectorizationResult:
    skill_names: list[str]
    vector: list[float]
    source_size: int


def normalize_skill_name(skill: Any) -> str:
    value = str(skill or "").strip().lower()
    value = value.replace("_", " ")
    value = value.replace("-", " ")
    value = " ".join(value.split())
    return value


def load_json_cell(value: Any, default: Any) -> Any:
    if value is None:
        return default

    if isinstance(value, float) and math.isnan(value):
        return default

    if isinstance(value, (dict, list)):
        return value

    if isinstance(value, str):
        stripped = value.strip()

        if not stripped:
            return default

        try:
            return json.loads(stripped)
        except json.JSONDecodeError:
            return default

    return default


def load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}

    with path.open("r", encoding="utf-8") as file:
        data = yaml.safe_load(file)

    return data or {}


def add_normalized_items(skills: set[str], values: list[Any] | dict[Any, Any]) -> None:
    for item in values:
        normalized_skill = normalize_skill_name(item)
        if normalized_skill:
            skills.add(normalized_skill)


def extract_skills_from_schema(schema: dict[str, Any]) -> set[str]:
    skills: set[str] = set()

    def walk(value: Any) -> None:
        if isinstance(value, dict):
            for key, nested_value in value.items():
                is_skill_container = (
                    isinstance(key, str)
                    and key.lower() in {"skills", "technical_skills"}
                    and isinstance(nested_value, (list, dict))
                )

                if is_skill_container:
                    add_normalized_items(skills, nested_value)

                walk(nested_value)

        elif isinstance(value, list):
            for item in value:
                walk(item)

    walk(schema)
    return {skill for skill in skills if skill}


def extract_skills_from_series(series: pd.Series) -> set[str]:
    skills: set[str] = set()

    for value in series.dropna():
        parsed = load_json_cell(value, default={})

        if isinstance(parsed, (dict, list)):
            add_normalized_items(skills, parsed)

    return {skill for skill in skills if skill}


def build_skill_vocab(
    employees_path: Path = EMPLOYEES_PATH,
    tasks_path: Path = TASKS_PATH,
    schema_path: Path = SYNTHETIC_SCHEMA_PATH,
) -> list[str]:
    schema = load_yaml(schema_path)
    skills = extract_skills_from_schema(schema)

    if employees_path.exists():
        employees = pd.read_csv(employees_path)
        if "skills" in employees.columns:
            skills.update(extract_skills_from_series(employees["skills"]))
        if "learning_goals" in employees.columns:
            skills.update(extract_skills_from_series(employees["learning_goals"]))

    if tasks_path.exists():
        tasks = pd.read_csv(tasks_path)
        if "required_skills" in tasks.columns:
            skills.update(extract_skills_from_series(tasks["required_skills"]))
        if "required_stack" in tasks.columns:
            skills.update(extract_skills_from_series(tasks["required_stack"]))

    return sorted(skill for skill in skills if skill)


def save_skill_vocab(skill_names: list[str], path: Path = SKILL_VOCAB_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    payload = {
        "size": len(skill_names),
        "skills": skill_names,
    }

    with path.open("w", encoding="utf-8") as file:
        json.dump(payload, file, ensure_ascii=False, indent=2)


def load_skill_vocab(path: Path = SKILL_VOCAB_PATH) -> list[str]:
    if not path.exists():
        skill_names = build_skill_vocab()
        save_skill_vocab(skill_names, path)
        return skill_names

    with path.open("r", encoding="utf-8") as file:
        payload = json.load(file)

    skills = payload.get("skills", [])
    return [normalize_skill_name(skill) for skill in skills]


def skill_dict_from_cell(value: Any) -> dict[str, float]:
    parsed = load_json_cell(value, default={})

    if isinstance(parsed, dict):
        result = {}
        for skill, level in parsed.items():
            normalized_skill = normalize_skill_name(skill)
            try:
                result[normalized_skill] = float(level)
            except (TypeError, ValueError):
                result[normalized_skill] = 0.0
        return result

    if isinstance(parsed, list):
        return {normalize_skill_name(skill): 1.0 for skill in parsed}

    return {}


def vectorize_skill_dict(
    skills: dict[str, float],
    skill_names: list[str],
    max_level: float = 5.0,
) -> list[float]:
    vector = []

    for skill_name in skill_names:
        raw_level = float(skills.get(skill_name, 0.0))
        normalized_level = max(0.0, min(raw_level / max_level, 1.0))
        vector.append(round(normalized_level, 6))

    return vector


def vectorize_skills_cell(
    value: Any,
    skill_names: list[str],
    max_level: float = 5.0,
) -> SkillVectorizationResult:
    skills = skill_dict_from_cell(value)
    vector = vectorize_skill_dict(skills, skill_names, max_level=max_level)

    return SkillVectorizationResult(
        skill_names=skill_names,
        vector=vector,
        source_size=len(skills),
    )


def employee_skill_vector(
    employee: dict[str, Any] | pd.Series,
    skill_names: list[str],
) -> list[float]:
    value = employee.get("skills", {})
    return vectorize_skills_cell(value, skill_names).vector


def task_required_skill_vector(
    task: dict[str, Any] | pd.Series,
    skill_names: list[str],
) -> list[float]:
    value = task.get("required_skills", {})
    return vectorize_skills_cell(value, skill_names).vector


def main() -> None:
    skill_names = build_skill_vocab()
    save_skill_vocab(skill_names)

    print(f"Skill vocab saved: {SKILL_VOCAB_PATH}")
    print(f"Skills count: {len(skill_names)}")
    print("First skills:")
    for skill in skill_names[:20]:
        print(f"- {skill}")


if __name__ == "__main__":
    main()