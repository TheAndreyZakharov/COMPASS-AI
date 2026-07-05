from __future__ import annotations

from typing import Any

from src.agents.state import AgentState
from src.integration.plane_client import PlaneClient, PlaneClientError
from src.integration.plane_comment_formatter import (
    COMMENT_MARKER,
    format_plane_recommendation_comment,
    has_compass_marker,
)


def _extract_results(response: Any) -> list[dict[str, Any]]:
    if isinstance(response, list):
        return [item for item in response if isinstance(item, dict)]

    if isinstance(response, dict):
        results = response.get("results")
        if isinstance(results, list):
            return [item for item in results if isinstance(item, dict)]

    return []


def _comment_text(comment: dict[str, Any]) -> str:
    text_parts = [
        comment.get("comment_html"),
        comment.get("comment_stripped"),
        comment.get("comment_json"),
        comment.get("description_html"),
        comment.get("description"),
        comment.get("body"),
        comment.get("text"),
    ]

    return " ".join(str(part) for part in text_parts if part)


def _safe_score(candidate: dict[str, Any]) -> float:
    try:
        return float(candidate.get("score") or 0.0)
    except (TypeError, ValueError):
        return 0.0


def _valid_plane_user_id(value: Any) -> str | None:
    if value is None:
        return None

    text = str(value).strip()

    if not text or text.lower() in {"nan", "none", "null"}:
        return None

    return text


def _top_candidate(recommendation: dict[str, Any]) -> dict[str, Any] | None:
    candidates = recommendation.get("top_candidates") or recommendation.get("candidates") or []

    if not isinstance(candidates, list) or not candidates:
        return None

    candidate = candidates[0]

    if not isinstance(candidate, dict):
        return None

    return candidate


def _default_write_back_status(write_back: bool) -> dict[str, Any]:
    return {
        "enabled": write_back,
        "written": False,
        "skipped": not write_back,
        "reason": "write_back disabled" if not write_back else None,
    }


def _default_auto_assign_status(auto_assign: bool) -> dict[str, Any]:
    return {
        "enabled": auto_assign,
        "assigned": False,
        "skipped": True,
        "reason": "auto_assign disabled" if not auto_assign else None,
    }


def load_plane_work_item(
    project_id: str,
    work_item_id: str,
    client: PlaneClient | None = None,
) -> dict[str, Any]:
    plane_client = client or PlaneClient()
    return plane_client.get_work_item(project_id=project_id, work_item_id=work_item_id)


def existing_compass_comment_exists(
    project_id: str,
    work_item_id: str,
    client: PlaneClient | None = None,
) -> bool:
    plane_client = client or PlaneClient()

    comments_response = plane_client.list_work_item_comments(
        project_id=project_id,
        work_item_id=work_item_id,
    )

    comments = _extract_results(comments_response)

    return any(has_compass_marker(_comment_text(comment)) for comment in comments)


def write_recommendation_comment(
    recommendation: dict[str, Any],
    project_id: str,
    work_item_id: str,
    client: PlaneClient | None = None,
) -> dict[str, Any]:
    plane_client = client or PlaneClient()

    if existing_compass_comment_exists(
        project_id=project_id,
        work_item_id=work_item_id,
        client=plane_client,
    ):
        return {
            "enabled": True,
            "written": False,
            "skipped": True,
            "reason": "COMPASS AI comment already exists",
        }

    comment_text = format_plane_recommendation_comment(recommendation)

    response = plane_client.create_work_item_comment(
        project_id=project_id,
        work_item_id=work_item_id,
        text=comment_text,
    )

    return {
        "enabled": True,
        "written": True,
        "skipped": False,
        "reason": None,
        "marker": COMMENT_MARKER,
        "response": response,
    }


def assign_top_candidate_if_allowed(
    recommendation: dict[str, Any],
    project_id: str,
    work_item_id: str,
    client: PlaneClient | None = None,
    auto_assign: bool = False,
    threshold: float = 0.75,
) -> dict[str, Any]:
    if not auto_assign:
        return _default_auto_assign_status(auto_assign=False)

    candidate = _top_candidate(recommendation)

    if candidate is None:
        return {
            "enabled": True,
            "assigned": False,
            "skipped": True,
            "reason": "top candidate not found",
        }

    score = _safe_score(candidate)

    if score < threshold:
        return {
            "enabled": True,
            "assigned": False,
            "skipped": True,
            "reason": f"score below threshold: {score:.4f} < {threshold:.4f}",
            "score": score,
            "threshold": threshold,
        }

    plane_user_id = _valid_plane_user_id(candidate.get("plane_user_id"))

    if plane_user_id is None:
        return {
            "enabled": True,
            "assigned": False,
            "skipped": True,
            "reason": "top candidate has no plane_user_id",
            "score": score,
            "threshold": threshold,
            "employee_id": candidate.get("employee_id"),
        }

    plane_client = client or PlaneClient()

    response = plane_client.update_work_item_assignee(
        project_id=project_id,
        work_item_id=work_item_id,
        assignee_id=plane_user_id,
    )

    return {
        "enabled": True,
        "assigned": True,
        "skipped": False,
        "reason": None,
        "score": score,
        "threshold": threshold,
        "employee_id": candidate.get("employee_id"),
        "plane_user_id": plane_user_id,
        "response": response,
    }


def run_plane_agent(
    state: AgentState,
    project_id: str | None = None,
    work_item_id: str | None = None,
    write_back: bool = False,
    auto_assign: bool = False,
    threshold: float = 0.75,
    client: PlaneClient | None = None,
) -> AgentState:
    if state.final_response is None:
        state.final_response = {}

    state.final_response["plane_write_back"] = _default_write_back_status(write_back)
    state.final_response["plane_auto_assign"] = _default_auto_assign_status(auto_assign)

    if not write_back and not auto_assign:
        return state

    resolved_project_id = project_id or state.final_response.get("plane_project_id")
    resolved_work_item_id = (
        work_item_id
        or state.final_response.get("plane_work_item_id")
        or state.final_response.get("plane_issue_id")
    )

    if not resolved_project_id or not resolved_work_item_id:
        state.add_error(
            "plane_agent",
            "project_id and work_item_id are required for Plane write-back or auto-assign.",
        )
        state.final_response["plane_write_back"] = {
            "enabled": write_back,
            "written": False,
            "skipped": True,
            "reason": "missing project_id or work_item_id",
        }
        state.final_response["plane_auto_assign"] = {
            "enabled": auto_assign,
            "assigned": False,
            "skipped": True,
            "reason": "missing project_id or work_item_id",
        }
        return state

    resolved_project_id = str(resolved_project_id)
    resolved_work_item_id = str(resolved_work_item_id)

    if resolved_work_item_id.startswith("TASK-"):
        state.add_error(
            "plane_agent",
            "Synthetic TASK-* items cannot be written back to Plane.",
        )
        state.final_response["plane_write_back"] = {
            "enabled": write_back,
            "written": False,
            "skipped": True,
            "reason": "synthetic TASK-* item has no Plane comment target",
        }
        state.final_response["plane_auto_assign"] = {
            "enabled": auto_assign,
            "assigned": False,
            "skipped": True,
            "reason": "synthetic TASK-* item has no Plane assignment target",
        }
        return state

    plane_client = client or PlaneClient()

    try:
        if write_back:
            state.final_response["plane_write_back"] = write_recommendation_comment(
                recommendation=state.final_response,
                project_id=resolved_project_id,
                work_item_id=resolved_work_item_id,
                client=plane_client,
            )

        if auto_assign:
            state.final_response["plane_auto_assign"] = assign_top_candidate_if_allowed(
                recommendation=state.final_response,
                project_id=resolved_project_id,
                work_item_id=resolved_work_item_id,
                client=plane_client,
                auto_assign=auto_assign,
                threshold=threshold,
            )

    except PlaneClientError as error:
        state.add_error("plane_agent", f"Plane API error: {error}")
        state.final_response["plane_write_back"] = {
            "enabled": write_back,
            "written": False,
            "skipped": False,
            "reason": str(error),
        }
        state.final_response["plane_auto_assign"] = {
            "enabled": auto_assign,
            "assigned": False,
            "skipped": False,
            "reason": str(error),
        }
    except Exception as error:
        state.add_error("plane_agent", f"Unexpected Plane agent error: {error}")
        state.final_response["plane_write_back"] = {
            "enabled": write_back,
            "written": False,
            "skipped": False,
            "reason": str(error),
        }
        state.final_response["plane_auto_assign"] = {
            "enabled": auto_assign,
            "assigned": False,
            "skipped": False,
            "reason": str(error),
        }

    return state