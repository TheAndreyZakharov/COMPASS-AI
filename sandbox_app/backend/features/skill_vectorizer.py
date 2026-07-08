from __future__ import annotations

import re
from collections.abc import Iterable
from typing import Any

SKILL_RE = re.compile(r"[^a-zA-Z0-9_+#.-]+")


def normalize_skill(value: Any) -> str:
    text = str(value or "").strip().lower()
    text = SKILL_RE.sub("_", text)
    text = text.strip("_")
    return text


def parse_skill_list(value: Any) -> list[str]:
    if value is None:
        return []

    if isinstance(value, list):
        return sorted({normalize_skill(item) for item in value if normalize_skill(item)})

    if isinstance(value, tuple | set):
        return sorted({normalize_skill(item) for item in value if normalize_skill(item)})

    if isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            return []

        if stripped.startswith("[") and stripped.endswith("]"):
            import json

            try:
                payload = json.loads(stripped)
            except json.JSONDecodeError:
                payload = None

            if isinstance(payload, list):
                return parse_skill_list(payload)

        parts = [item.strip() for item in stripped.split(",")]
        return sorted({normalize_skill(item) for item in parts if normalize_skill(item)})

    return []


def collect_skill_vocabulary(records: Iterable[dict[str, Any]]) -> list[str]:
    vocabulary: set[str] = set()

    for record in records:
        for field_name in ("skills", "required_skills", "learning_goals"):
            vocabulary.update(parse_skill_list(record.get(field_name)))

    return sorted(vocabulary)


def skill_vector(prefix: str, skills: list[str], vocabulary: list[str]) -> dict[str, float]:
    skill_set = set(skills)
    return {f"{prefix}_{skill}": 1.0 if skill in skill_set else 0.0 for skill in vocabulary}


def skill_overlap_features(
    employee_skills: list[str],
    task_skills: list[str],
) -> dict[str, float]:
    employee_set = set(employee_skills)
    task_set = set(task_skills)
    overlap = employee_set & task_set
    missing = task_set - employee_set

    required_count = len(task_set)
    employee_count = len(employee_set)
    overlap_count = len(overlap)
    missing_count = len(missing)

    return {
        "skill_employee_count": float(employee_count),
        "skill_required_count": float(required_count),
        "skill_overlap_count": float(overlap_count),
        "skill_missing_count": float(missing_count),
        "skill_match_ratio": float(overlap_count / max(required_count, 1)),
        "skill_missing_ratio": float(missing_count / max(required_count, 1)),
        "skill_employee_extra_count": float(len(employee_set - task_set)),
    }