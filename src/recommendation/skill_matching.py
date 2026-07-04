from __future__ import annotations

import json
import math
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class SkillMatchResult:
    score: float
    matched_skills: list[str]
    missing_skills: list[str]
    weak_skills: list[str]
    required_skills_count: int
    average_required_level: float


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None:
            return default

        if isinstance(value, float) and math.isnan(value):
            return default

        return float(value)
    except (TypeError, ValueError):
        return default


def _parse_json_like(value: Any, default: Any) -> Any:
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


def normalize_skill_name(skill: Any) -> str:
    return str(skill).strip().lower().replace("_", " ").replace("-", " ")


def normalize_stack_name(stack_item: Any) -> str:
    return normalize_skill_name(stack_item)


def parse_employee_skills(employee: dict[str, Any]) -> dict[str, float]:
    raw_skills = _parse_json_like(employee.get("skills"), default={})

    if not isinstance(raw_skills, dict):
        return {}

    return {
        normalize_skill_name(skill): max(0.0, min(5.0, _safe_float(level)))
        for skill, level in raw_skills.items()
    }


def parse_required_skills(task: dict[str, Any]) -> dict[str, float]:
    raw_required_skills = _parse_json_like(task.get("required_skills"), default={})

    if isinstance(raw_required_skills, dict):
        return {
            normalize_skill_name(skill): max(1.0, min(5.0, _safe_float(level, default=3.0)))
            for skill, level in raw_required_skills.items()
        }

    if isinstance(raw_required_skills, list):
        return {normalize_skill_name(skill): 3.0 for skill in raw_required_skills}

    return {}


def parse_required_stack(task: dict[str, Any]) -> list[str]:
    raw_stack = _parse_json_like(task.get("required_stack"), default=[])

    if isinstance(raw_stack, list):
        return [normalize_stack_name(item) for item in raw_stack if str(item).strip()]

    if isinstance(raw_stack, str) and raw_stack.strip():
        return [normalize_stack_name(raw_stack)]

    return []


def skill_level(employee: dict[str, Any], skill_name: str) -> float:
    skills = parse_employee_skills(employee)
    return skills.get(normalize_skill_name(skill_name), 0.0)


def calculate_skill_match(task: dict[str, Any], employee: dict[str, Any]) -> SkillMatchResult:
    employee_skills = parse_employee_skills(employee)
    required_skills = parse_required_skills(task)
    required_stack = parse_required_stack(task)

    if not required_skills and required_stack:
        required_skills = {stack_item: 3.0 for stack_item in required_stack}

    if not required_skills:
        return SkillMatchResult(
            score=0.0,
            matched_skills=[],
            missing_skills=[],
            weak_skills=[],
            required_skills_count=0,
            average_required_level=0.0,
        )

    skill_scores: list[float] = []
    matched_skills: list[str] = []
    missing_skills: list[str] = []
    weak_skills: list[str] = []

    for skill_name, required_level in required_skills.items():
        employee_level = employee_skills.get(skill_name, 0.0)

        if employee_level <= 0:
            missing_skills.append(skill_name)
            skill_scores.append(0.0)
            continue

        ratio = min(employee_level / required_level, 1.0)
        skill_scores.append(ratio)

        if ratio >= 0.85:
            matched_skills.append(skill_name)
        else:
            weak_skills.append(skill_name)

    base_score = sum(skill_scores) / len(skill_scores)

    stack_bonus = 0.0
    if required_stack:
        stack_matches = sum(1 for item in required_stack if employee_skills.get(item, 0.0) >= 2.0)
        stack_bonus = 0.05 * (stack_matches / len(required_stack))

    score = max(0.0, min(1.0, base_score + stack_bonus))

    return SkillMatchResult(
        score=round(score, 4),
        matched_skills=matched_skills,
        missing_skills=missing_skills,
        weak_skills=weak_skills,
        required_skills_count=len(required_skills),
        average_required_level=round(sum(required_skills.values()) / len(required_skills), 4),
    )


def skill_match_score(task: dict[str, Any], employee: dict[str, Any]) -> float:
    return calculate_skill_match(task, employee).score