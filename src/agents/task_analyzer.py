from __future__ import annotations

import json
import re
from datetime import date, datetime
from html import unescape
from typing import Any

from src.agents.state import AgentState

TASK_TYPE_BY_LABEL = {
    "backend": "backend_feature",
    "frontend": "frontend_feature",
    "ml": "ml_pipeline",
    "data": "analytics_report",
    "devops": "devops_task",
    "bug": "bugfix",
    "refactoring": "refactoring",
    "security": "security_task",
    "testing": "testing_task",
    "documentation": "documentation_task",
}

TASK_TYPE_SKILLS = {
    "backend_feature": {
        "Python": 4,
        "FastAPI": 4,
        "PostgreSQL": 3,
        "API Design": 4,
    },
    "frontend_feature": {
        "React": 4,
        "TypeScript": 4,
        "HTML/CSS": 3,
    },
    "bugfix": {
        "Testing": 3,
        "Code Review": 3,
    },
    "refactoring": {
        "System Design": 3,
        "Code Review": 4,
    },
    "database_migration": {
        "PostgreSQL": 4,
        "Backend Architecture": 3,
    },
    "api_integration": {
        "API Design": 4,
        "FastAPI": 3,
        "Python": 3,
    },
    "ml_pipeline": {
        "Python": 4,
        "Machine Learning": 4,
        "PyTorch": 3,
        "Data Pipelines": 3,
    },
    "analytics_report": {
        "Data Analysis": 4,
        "Documentation": 3,
    },
    "devops_task": {
        "Docker": 4,
        "Kubernetes": 3,
        "CI/CD": 3,
    },
    "testing_task": {
        "Testing": 4,
        "QA Strategy": 3,
    },
    "security_task": {
        "Security": 4,
        "Risk Management": 3,
    },
    "documentation_task": {
        "Documentation": 4,
        "Communication": 3,
    },
}

STACK_BY_TASK_TYPE = {
    "backend_feature": ["Python", "FastAPI", "PostgreSQL"],
    "frontend_feature": ["React", "TypeScript", "HTML/CSS"],
    "database_migration": ["PostgreSQL"],
    "api_integration": ["Python", "FastAPI"],
    "ml_pipeline": ["Python", "PyTorch"],
    "devops_task": ["Docker", "Kubernetes"],
}


def strip_html(value: str) -> str:
    text = re.sub(r"<[^>]+>", " ", value)
    text = unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def parse_json_cell(value: Any, default: Any) -> Any:
    if value is None:
        return default

    if isinstance(value, float):
        return default

    if isinstance(value, str):
        value = value.strip()

        if not value:
            return default

        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return default

    return value


def labels_from_issue(issue: dict[str, Any]) -> list[str]:
    raw_labels = issue.get("labels", [])
    labels: list[str] = []

    if isinstance(raw_labels, list):
        for label in raw_labels:
            if isinstance(label, dict):
                name = label.get("name") or label.get("title") or label.get("slug")
                if name:
                    labels.append(str(name).lower())
            else:
                labels.append(str(label).lower())

    return sorted(set(labels))


def extract_compass_task_id(issue: dict[str, Any]) -> str:
    text = " ".join(
        [
            str(issue.get("description", "")),
            str(issue.get("description_html", "")),
            str(issue.get("name", "")),
            str(issue.get("title", "")),
        ]
    )

    match = re.search(r"COMPASS\s+task_id\s*[:=]\s*(TASK-\d+)", text, re.IGNORECASE)

    if match:
        return match.group(1)

    if issue.get("task_id"):
        return str(issue["task_id"])

    return ""


def detect_task_type(title: str, description: str, labels: list[str]) -> str:
    for label in labels:
        if label in TASK_TYPE_BY_LABEL:
            return TASK_TYPE_BY_LABEL[label]

    text = f"{title} {description}".lower()

    keyword_mapping = {
        "frontend_feature": ["react", "frontend", "dashboard", "ui", "страниц"],
        "backend_feature": ["api", "backend", "jwt", "endpoint", "авторизац"],
        "ml_pipeline": ["ml", "model", "нейросет", "embedding", "pipeline"],
        "analytics_report": ["report", "analytics", "отчёт", "аналит"],
        "devops_task": ["docker", "kubernetes", "ci", "deploy"],
        "security_task": ["security", "token", "секрет", "уязвим"],
        "testing_task": ["test", "pytest", "qa", "тест"],
        "bugfix": ["bug", "fix", "ошиб", "почин"],
        "refactoring": ["refactor", "рефактор"],
        "documentation_task": ["docs", "readme", "документ"],
    }

    for task_type, keywords in keyword_mapping.items():
        if any(keyword in text for keyword in keywords):
            return task_type

    return "backend_feature"


def priority_to_score(priority: str) -> float:
    priority_scores = {
        "none": 0.0,
        "low": 0.2,
        "medium": 0.5,
        "high": 0.8,
        "urgent": 1.0,
    }

    return priority_scores.get(priority.lower(), 0.5)


def deadline_days_from_issue(issue: dict[str, Any]) -> int:
    explicit_deadline_days = issue.get("deadline_days")

    if explicit_deadline_days is not None:
        return max(1, int(explicit_deadline_days))

    target_date = issue.get("target_date")

    if not target_date:
        return 14

    try:
        target = date.fromisoformat(str(target_date)[:10])
    except ValueError:
        return 14

    return max(1, (target - datetime.now().date()).days)


def estimate_complexity(issue: dict[str, Any], task_type: str) -> int:
    if issue.get("complexity") is not None:
        return max(1, min(5, int(issue["complexity"])))

    priority = str(issue.get("priority", "medium")).lower()
    title = str(issue.get("name") or issue.get("title") or "")
    description = str(issue.get("description") or issue.get("description_html") or "")

    base_by_type = {
        "backend_feature": 3,
        "frontend_feature": 3,
        "bugfix": 2,
        "refactoring": 3,
        "database_migration": 4,
        "api_integration": 3,
        "ml_pipeline": 4,
        "analytics_report": 3,
        "devops_task": 3,
        "testing_task": 2,
        "security_task": 4,
        "documentation_task": 2,
    }

    complexity = base_by_type.get(task_type, 3)
    text_length = len(title) + len(description)

    if priority in {"high", "urgent"}:
        complexity += 1

    if text_length > 700:
        complexity += 1

    return max(1, min(5, complexity))


def analyze_task(issue: dict[str, Any]) -> dict[str, Any]:
    title = str(issue.get("title") or issue.get("name") or "")
    description = str(issue.get("description") or issue.get("description_html") or "")
    description = strip_html(description)

    labels = labels_from_issue(issue)
    task_type = detect_task_type(title, description, labels)
    required_skills = TASK_TYPE_SKILLS.get(task_type, TASK_TYPE_SKILLS["backend_feature"])
    required_stack = STACK_BY_TASK_TYPE.get(task_type, [])

    priority = str(issue.get("priority", "medium")).lower()
    complexity = estimate_complexity(issue, task_type)
    deadline_days = deadline_days_from_issue(issue)

    return {
        "task_id": extract_compass_task_id(issue),
        "plane_work_item_id": str(issue.get("id", "")),
        "plane_issue_id": str(issue.get("id", "")),
        "plane_project_id": str(issue.get("project", "")),
        "project_key": str(issue.get("project_key", "")),
        "title": title,
        "description": description,
        "labels": labels,
        "task_type": task_type,
        "required_stack": required_stack,
        "required_skills": required_skills,
        "complexity": complexity,
        "priority": priority,
        "priority_score": priority_to_score(priority),
        "business_criticality": max(1, min(5, complexity + int(priority in {"high", "urgent"}))),
        "deadline_days": deadline_days,
        "estimated_hours": int(issue.get("estimated_hours") or complexity * 10),
        "dependencies_count": int(issue.get("dependencies_count") or 0),
        "is_growth_task": "growth-task" in labels,
        "source": "plane" if issue.get("id") else "manual",
    }


def run_task_analyzer(state: AgentState) -> AgentState:
    if not state.issue:
        state.add_error("task_analyzer", "AgentState.issue is empty.")
        return state

    try:
        state.task_features = analyze_task(state.issue)
    except Exception as error:
        state.add_error("task_analyzer", str(error))

    return state