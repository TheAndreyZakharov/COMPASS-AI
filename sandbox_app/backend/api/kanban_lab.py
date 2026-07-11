from __future__ import annotations

import json
import re
import shutil
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from sandbox_app.backend.core.paths import PATHS
from sandbox_app.backend.core.time import moscow_stamp
from sandbox_app.backend.inference.model_loader import ModelLoadError
from sandbox_app.backend.inference.model_loader import load_model as load_sandbox_model
from sandbox_app.backend.inference.recommend import (
    RECOMMENDATION_MODES,
    RecommendationError,
    candidate_result,
    predict_scores,
    recommendation_id,
    utc_now_iso,
    validate_mode,
    validate_top_k,
)
from sandbox_app.backend.inference.scoring import build_pair_feature_frame, to_float

router = APIRouter(prefix="/kanban-lab", tags=["kanban-lab"])
LAB_ID_RE = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9_-]{2,80}$")


class KanbanBoardRecommendationRequest(BaseModel):
    session_id: str = Field(min_length=1)
    model_name: str = Field(min_length=1)
    source_id: str = "kanban_lab"
    recommendation_mode: str = "balanced"
    top_k: int = Field(default=3, ge=1, le=25)
    team: list[dict[str, Any]] = Field(min_length=1)
    tasks: list[dict[str, Any]] = Field(min_length=1, max_length=20000)
    statuses_for_recommendation: list[str] = Field(
        default_factory=lambda: ["todo", "in_progress", "review", "blocked"]
    )


class KanbanBoardSaveRequest(BaseModel):
    lab_id: str | None = Field(default=None, max_length=81)
    name: str = Field(default="Kanban lab board", min_length=1, max_length=120)
    source_test_case_id: str | None = Field(default=None, max_length=120)
    source_dataset_value: str | None = Field(default=None, max_length=180)
    team: list[dict[str, Any]] = Field(min_length=1)
    history: list[dict[str, Any]] = Field(default_factory=list)
    tasks: list[dict[str, Any]] = Field(min_length=0, max_length=20000)
    config: dict[str, Any] = Field(default_factory=dict)
    overwrite: bool = True


def safe_lab_id(value: str) -> str:
    lab_id = value.strip()
    if not LAB_ID_RE.match(lab_id):
        raise ValueError(
            "lab_id must contain 3-81 characters: letters, digits, underscore or dash"
        )
    return lab_id


def make_lab_id(name: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9_-]+", "_", name.strip().lower()).strip("_")
    slug = slug[:36] or "kanban_lab"
    return safe_lab_id(f"{slug}_{moscow_stamp()}")


def lab_dir(lab_id: str):
    return PATHS.kanban_lab_dir / safe_lab_id(lab_id)


def board_path(lab_id: str):
    return lab_dir(lab_id) / "board.json"


def write_json(path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def read_json(path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"Could not read kanban lab board: {path}") from exc

    if not isinstance(payload, dict):
        raise ValueError("Kanban lab board must be a JSON object")

    return payload


def status_counts(tasks: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for task in tasks:
        status = str(task.get("status") or "unknown").lower()
        counts[status] = counts.get(status, 0) + 1
    return counts


def board_summary(payload: dict[str, Any]) -> dict[str, Any]:
    metadata = payload.get("metadata") or {}
    return {
        "lab_id": payload.get("lab_id"),
        "name": payload.get("name"),
        "created_at": payload.get("created_at"),
        "updated_at": payload.get("updated_at"),
        "source_test_case_id": payload.get("source_test_case_id"),
        "source_dataset_value": payload.get("source_dataset_value"),
        "team_count": metadata.get("team_count", len(payload.get("team") or [])),
        "task_count": metadata.get("task_count", len(payload.get("tasks") or [])),
        "history_count": metadata.get("history_count", len(payload.get("history") or [])),
        "status_counts": metadata.get("status_counts", {}),
    }


@router.get("/boards")
def list_boards() -> dict[str, Any]:
    PATHS.kanban_lab_dir.mkdir(parents=True, exist_ok=True)
    boards: list[dict[str, Any]] = []

    for directory in sorted(PATHS.kanban_lab_dir.iterdir(), reverse=True):
        if not directory.is_dir():
            continue

        path = directory / "board.json"
        if not path.exists():
            continue

        try:
            boards.append(board_summary(read_json(path)))
        except ValueError:
            continue

    return {
        "boards": boards,
        "total": len(boards),
        "storage_dir": str(PATHS.kanban_lab_dir),
    }


@router.get("/boards/{lab_id}")
def get_board(lab_id: str) -> dict[str, Any]:
    try:
        path = board_path(lab_id)
        if not path.exists():
            raise ValueError(f"Kanban lab board not found: {lab_id}")
        return read_json(path)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/boards")
def save_board(payload: KanbanBoardSaveRequest) -> dict[str, Any]:
    try:
        lab_id = safe_lab_id(payload.lab_id) if payload.lab_id else make_lab_id(payload.name)
        path = board_path(lab_id)

        if path.exists() and not payload.overwrite:
            raise ValueError(f"Kanban lab board already exists: {lab_id}")

        previous = read_json(path) if path.exists() else {}
        created_at = previous.get("created_at") or utc_now_iso()
        tasks = payload.tasks
        board = {
            "lab_id": lab_id,
            "name": payload.name,
            "created_at": created_at,
            "updated_at": utc_now_iso(),
            "source_test_case_id": payload.source_test_case_id,
            "source_dataset_value": payload.source_dataset_value,
            "team": payload.team,
            "history": payload.history,
            "tasks": tasks,
            "config": payload.config,
            "metadata": {
                "team_count": len(payload.team),
                "task_count": len(tasks),
                "history_count": len(payload.history),
                "status_counts": status_counts(tasks),
            },
        }
        write_json(path, board)

        return {
            "status": "saved",
            "board": board_summary(board),
            "path": str(path),
        }
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.delete("/boards/{lab_id}")
def delete_board(lab_id: str) -> dict[str, Any]:
    try:
        directory = lab_dir(lab_id)
        if not directory.exists():
            raise ValueError(f"Kanban lab board not found: {lab_id}")
        shutil.rmtree(directory)
        return {
            "status": "deleted",
            "lab_id": lab_id,
        }
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


def status_allowed(task: dict[str, Any], statuses: set[str]) -> bool:
    return str(task.get("status", "")).lower() in statuses


def recommendation_for_task(
    *,
    model: Any,
    task: dict[str, Any],
    team: list[dict[str, Any]],
    payload: KanbanBoardRecommendationRequest,
) -> dict[str, Any]:
    feature_frame = build_pair_feature_frame(
        task=task,
        employees=team,
        recommendation_mode=payload.recommendation_mode,
    )
    scores = predict_scores(model, feature_frame)

    if len(scores) != len(team):
        raise RecommendationError("Model returned unexpected number of scores")

    rows = feature_frame.to_dict(orient="records")
    ranked_candidates = [
        candidate_result(
            task=task,
            employee=employee,
            row=row,
            model_score=score,
            mode=payload.recommendation_mode,
        )
        for employee, row, score in zip(team, rows, scores, strict=True)
    ]
    ranked_candidates.sort(
        key=lambda item: (
            -to_float(item["score"]),
            to_float(item["risk_summary"]["max_risk_score"]),
            str(item["employee_id"]),
        )
    )

    top_candidates = ranked_candidates[: payload.top_k]

    return {
        "recommendation_id": recommendation_id(),
        "created_at": utc_now_iso(),
        "source": "kanban_lab",
        "source_id": payload.source_id,
        "session_id": payload.session_id,
        "model_name": payload.model_name,
        "task_id": task.get("task_id"),
        "recommendation_mode": payload.recommendation_mode,
        "mode_details": RECOMMENDATION_MODES[payload.recommendation_mode],
        "top_k": payload.top_k,
        "task": task,
        "top_1": top_candidates[0] if top_candidates else None,
        "top_3": top_candidates[:3],
        "candidates": top_candidates,
        "all_candidates_count": len(ranked_candidates),
        "model_metadata": getattr(model, "metadata", {}),
        "config": {
            "source_id": payload.source_id,
            "recommendation_mode": payload.recommendation_mode,
            "top_k": payload.top_k,
        },
    }


@router.post("/recommend-board")
def recommend_board(payload: KanbanBoardRecommendationRequest) -> dict[str, Any]:
    try:
        validate_mode(payload.recommendation_mode)
        validate_top_k(payload.top_k)

        statuses = {
            str(status).strip().lower()
            for status in payload.statuses_for_recommendation
            if str(status).strip()
        }
        if not statuses:
            raise RecommendationError("statuses_for_recommendation must not be empty")

        tasks = [task for task in payload.tasks if status_allowed(task, statuses)]
        if not tasks:
            return {
                "status": "completed",
                "source": "kanban_lab",
                "source_id": payload.source_id,
                "recommendations": [],
                "total": 0,
                "message": "No tasks matched selected statuses",
            }

        model = load_sandbox_model(payload.session_id, payload.model_name)
        recommendations = [
            recommendation_for_task(
                model=model,
                task=task,
                team=payload.team,
                payload=payload,
            )
            for task in tasks
        ]

        return {
            "status": "completed",
            "source": "kanban_lab",
            "source_id": payload.source_id,
            "session_id": payload.session_id,
            "model_name": payload.model_name,
            "recommendation_mode": payload.recommendation_mode,
            "top_k": payload.top_k,
            "statuses_for_recommendation": sorted(statuses),
            "recommendations": recommendations,
            "total": len(recommendations),
        }
    except (ModelLoadError, RecommendationError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
