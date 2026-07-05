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


def _normalize_threshold(value: float) -> float:
    try:
        threshold = float(value)
    except (TypeError, ValueError):
        return 0.75

    return max(0.0, min(1.0, threshold))


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
        "enabled": bool(write_back),
        "written": False,
        "skipped": not write_back,
        "reason": "write_back disabled" if not write_back else None,
    }


def _default_auto_assign_status(auto_assign: bool) -> dict[str, Any]:
    return {
        "enabled": bool(auto_assign),
        "assigned": False,
        "skipped": True,
        "reason": "auto_assign disabled" if not auto_assign else None,
    }


def _missing_target_status(
    write_back: bool,
    auto_assign: bool,
    threshold: float,
) -> tuple[dict[str, Any], dict[str, Any]]:
    write_back_status = {
        "enabled": bool(write_back),
        "written": False,
        "skipped": True,
        "reason": "missing project_id or work_item_id",
    }
    auto_assign_status = {
        "enabled": bool(auto_assign),
        "assigned": False,
        "skipped": True,
        "reason": "missing project_id or work_item_id",
        "threshold": threshold,
    }

    return write_back_status, auto_assign_status


def _synthetic_target_status(
    write_back: bool,
    auto_assign: bool,
    threshold: float,
) -> tuple[dict[str, Any], dict[str, Any]]:
    write_back_status = {
        "enabled": bool(write_back),
        "written": False,
        "skipped": True,
        "reason": "synthetic TASK-* item has no Plane comment target",
    }
    auto_assign_status = {
        "enabled": bool(auto_assign),
        "assigned": False,
        "skipped": True,
        "reason": "synthetic TASK-* item has no Plane assignment target",
        "threshold": threshold,
    }

    return write_back_status, auto_assign_status


def load_plane_work_item(
    project_id: str,
    work_item_id: str,
    client: PlaneClient | None = None,
) -> dict[str, Any]:
    plane_client = client or PlaneClient()

    return plane_client.get_work_item(
        project_id=project_id,
        work_item_id=work_item_id,
    )


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
            "marker": COMMENT_MARKER,
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
    normalized_threshold = _normalize_threshold(threshold)

    if not auto_assign:
        return _default_auto_assign_status(auto_assign=False)

    candidate = _top_candidate(recommendation)

    if candidate is None:
        return {
            "enabled": True,
            "assigned": False,
            "skipped": True,
            "reason": "top candidate not found",
            "threshold": normalized_threshold,
        }

    score = _safe_score(candidate)

    if score < normalized_threshold:
        reason = f"score below threshold: {score:.4f} < {normalized_threshold:.4f}"
        return {
            "enabled": True,
            "assigned": False,
            "skipped": True,
            "reason": reason,
            "score": score,
            "threshold": normalized_threshold,
            "employee_id": candidate.get("employee_id"),
        }

    plane_user_id = _valid_plane_user_id(candidate.get("plane_user_id"))

    if plane_user_id is None:
        return {
            "enabled": True,
            "assigned": False,
            "skipped": True,
            "reason": "top candidate has no plane_user_id",
            "score": score,
            "threshold": normalized_threshold,
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
        "threshold": normalized_threshold,
        "employee_id": candidate.get("employee_id"),
        "plane_user_id": plane_user_id,
        "response": response,
    }


def _resolve_plane_target(
    state: AgentState,
    project_id: str | None = None,
    work_item_id: str | None = None,
) -> tuple[str | None, str | None]:
    if state.final_response is None:
        return project_id, work_item_id

    resolved_project_id = project_id or state.final_response.get("plane_project_id")
    resolved_work_item_id = (
        work_item_id
        or state.final_response.get("plane_work_item_id")
        or state.final_response.get("plane_issue_id")
    )

    if resolved_project_id is not None:
        resolved_project_id = str(resolved_project_id)

    if resolved_work_item_id is not None:
        resolved_work_item_id = str(resolved_work_item_id)

    return resolved_project_id, resolved_work_item_id


def _handle_write_back_error(
    state: AgentState,
    error: Exception,
    is_plane_error: bool,
) -> None:
    prefix = "Plane comment write-back failed"
    if not is_plane_error:
        prefix = "Unexpected Plane comment write-back error"

    state.add_error(agent="plane_agent", message=f"{prefix}: {error}")
    state.final_response["plane_write_back"] = {
        "enabled": True,
        "written": False,
        "skipped": False,
        "reason": str(error),
    }


def _handle_auto_assign_error(
    state: AgentState,
    error: Exception,
    threshold: float,
    is_plane_error: bool,
) -> None:
    prefix = "Plane auto-assign failed"
    if not is_plane_error:
        prefix = "Unexpected Plane auto-assign error"

    state.add_error(agent="plane_agent", message=f"{prefix}: {error}")
    state.final_response["plane_auto_assign"] = {
        "enabled": True,
        "assigned": False,
        "skipped": False,
        "reason": str(error),
        "threshold": threshold,
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

    normalized_threshold = _normalize_threshold(threshold)

    state.final_response["plane_write_back"] = _default_write_back_status(write_back)
    state.final_response["plane_auto_assign"] = _default_auto_assign_status(auto_assign)

    if not write_back and not auto_assign:
        return state

    resolved_project_id, resolved_work_item_id = _resolve_plane_target(
        state=state,
        project_id=project_id,
        work_item_id=work_item_id,
    )

    if not resolved_project_id or not resolved_work_item_id:
        write_status, assign_status = _missing_target_status(
            write_back=write_back,
            auto_assign=auto_assign,
            threshold=normalized_threshold,
        )
        state.add_error(
            agent="plane_agent",
            message="project_id and work_item_id are required for Plane actions.",
        )
        state.final_response["plane_write_back"] = write_status
        state.final_response["plane_auto_assign"] = assign_status
        return state

    if resolved_work_item_id.startswith("TASK-"):
        write_status, assign_status = _synthetic_target_status(
            write_back=write_back,
            auto_assign=auto_assign,
            threshold=normalized_threshold,
        )
        state.add_error(
            agent="plane_agent",
            message="Synthetic TASK-* items cannot be written back to Plane.",
        )
        state.final_response["plane_write_back"] = write_status
        state.final_response["plane_auto_assign"] = assign_status
        return state

    plane_client = client or PlaneClient()

    if write_back:
        try:
            state.final_response["plane_write_back"] = write_recommendation_comment(
                recommendation=state.final_response,
                project_id=resolved_project_id,
                work_item_id=resolved_work_item_id,
                client=plane_client,
            )
        except PlaneClientError as error:
            _handle_write_back_error(state=state, error=error, is_plane_error=True)
        except Exception as error:
            _handle_write_back_error(state=state, error=error, is_plane_error=False)

    if auto_assign:
        try:
            state.final_response["plane_auto_assign"] = assign_top_candidate_if_allowed(
                recommendation=state.final_response,
                project_id=resolved_project_id,
                work_item_id=resolved_work_item_id,
                client=plane_client,
                auto_assign=auto_assign,
                threshold=normalized_threshold,
            )
        except PlaneClientError as error:
            _handle_auto_assign_error(
                state=state,
                error=error,
                threshold=normalized_threshold,
                is_plane_error=True,
            )
        except Exception as error:
            _handle_auto_assign_error(
                state=state,
                error=error,
                threshold=normalized_threshold,
                is_plane_error=False,
            )

    return state