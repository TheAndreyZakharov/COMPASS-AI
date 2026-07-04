from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from src.agents.explanation_agent import run_explanation_agent
from src.agents.matching_agent import run_matching_agent
from src.agents.plane_agent import load_plane_work_item, run_plane_agent
from src.agents.state import AgentState, normalize_mode
from src.agents.task_analyzer import run_task_analyzer
from src.agents.team_analyzer import run_team_analyzer

PROJECT_ROOT = Path(__file__).resolve().parents[2]
TASKS_PATH = PROJECT_ROOT / "data" / "synthetic" / "tasks.csv"


def _state_to_response(state: AgentState) -> dict[str, Any]:
    task = state.task_features

    response = {
        "task_id": task.get("task_id"),
        "plane_work_item_id": task.get("plane_work_item_id"),
        "plane_issue_id": task.get("plane_issue_id"),
        "title": task.get("title"),
        "task_type": task.get("task_type"),
        "mode": state.recommendation_mode,
        "top_candidates": state.top_candidates,
        "explanation": state.explanation,
        "errors": state.error_payload(),
        "source": "agentic_pipeline",
    }

    response.update(state.final_response)

    return response


def run_agentic_recommendation(
    issue: dict[str, Any] | None = None,
    project_id: str | None = None,
    work_item_id: str | None = None,
    mode: str = "balanced_workload",
    top_k: int = 3,
    write_back: bool = False,
    use_llm: bool = True,
) -> dict[str, Any]:
    if issue is None:
        if not project_id or not work_item_id:
            raise ValueError("Either issue or project_id + work_item_id must be provided.")

        issue = load_plane_work_item(
            project_id=project_id,
            work_item_id=work_item_id,
        )

    state = AgentState(
        issue=issue,
        recommendation_mode=normalize_mode(mode),
    )

    state = run_task_analyzer(state)
    state = run_team_analyzer(state)
    state = run_matching_agent(state, top_k=top_k)
    state = run_explanation_agent(state, use_llm=use_llm)
    state.final_response = _state_to_response(state)

    state = run_plane_agent(
        state=state,
        project_id=project_id,
        work_item_id=work_item_id,
        write_back=write_back,
    )

    state.final_response = _state_to_response(state)

    return state.final_response


def load_synthetic_task(task_id: str) -> dict[str, Any]:
    if not TASKS_PATH.exists():
        raise FileNotFoundError(
            f"Missing tasks file: {TASKS_PATH}. "
            "Run: python scripts/generate_synthetic_data.py"
        )

    tasks = pd.read_csv(TASKS_PATH)
    row = tasks[tasks["task_id"].astype(str) == str(task_id)]

    if row.empty:
        raise ValueError(f"Synthetic task not found: {task_id}")

    return row.iloc[0].to_dict()


def recommend_synthetic_task(
    task_id: str,
    mode: str = "balanced_workload",
    top_k: int = 3,
    use_llm: bool = False,
) -> dict[str, Any]:
    task = load_synthetic_task(task_id)

    issue = {
        "id": task.get("plane_work_item_id", ""),
        "task_id": task.get("task_id", ""),
        "project": task.get("plane_project_id", ""),
        "project_key": task.get("project_key", ""),
        "title": task.get("title", ""),
        "name": task.get("title", ""),
        "description": task.get("description", ""),
        "description_html": task.get("description", ""),
        "priority": task.get("priority", "medium"),
        "complexity": int(task.get("complexity", 3)),
        "deadline_days": int(task.get("deadline_days", 14)),
        "estimated_hours": int(task.get("estimated_hours", 30)),
        "dependencies_count": int(task.get("dependencies_count", 0)),
    }

    return run_agentic_recommendation(
        issue=issue,
        mode=mode,
        top_k=top_k,
        write_back=False,
        use_llm=use_llm,
    )


def main() -> None:
    response = recommend_synthetic_task(
        task_id="TASK-0001",
        mode="balanced_workload",
        top_k=3,
        use_llm=False,
    )

    import json

    print(json.dumps(response, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()