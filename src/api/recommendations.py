from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from src.agents.orchestrator import recommend_synthetic_task, run_agentic_recommendation
from src.agents.state import normalize_mode
from src.integration.plane_client import PlaneClient, PlaneClientError

router = APIRouter(tags=["recommendations"])

OPEN_STATE_GROUPS = {"backlog", "unstarted", "started"}
CLOSED_STATE_GROUPS = {"completed", "cancelled"}


class ManualRecommendationRequest(BaseModel):
    issue: dict[str, Any] = Field(
        ...,
        description="Manual task payload in Plane-like or COMPASS-like format.",
    )
    employees: list[dict[str, Any]] | None = Field(
        default=None,
        description=(
            "Optional future extension. Current pipeline uses synthetic team "
            "from data/synthetic/employees.csv."
        ),
    )
    mode: str = Field(default="balanced_workload")
    top_k: int = Field(default=3, ge=1, le=10)
    use_llm: bool = Field(default=False)


def extract_results(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]

    if isinstance(payload, dict):
        results = payload.get("results", [])
        if isinstance(results, list):
            return [item for item in results if isinstance(item, dict)]

    return []


def work_item_identifier_matches(work_item: dict[str, Any], issue_id: str) -> bool:
    candidate_values = {
        str(work_item.get("id", "")),
        str(work_item.get("sequence_id", "")),
        str(work_item.get("identifier", "")),
        str(work_item.get("name", "")),
    }

    return issue_id in candidate_values


def is_open_work_item(work_item: dict[str, Any]) -> bool:
    state = work_item.get("state")

    if isinstance(state, dict):
        state_group = str(state.get("group", "")).lower()
        if state_group in CLOSED_STATE_GROUPS:
            return False
        if state_group in OPEN_STATE_GROUPS:
            return True

    completed_at = work_item.get("completed_at")
    if completed_at:
        return False

    archived_at = work_item.get("archived_at")

    return not archived_at


def resolve_plane_work_item(
    client: PlaneClient,
    issue_id: str,
    project_id: str | None = None,
) -> tuple[str, dict[str, Any]]:
    if project_id:
        return _resolve_plane_work_item_in_project(
            client=client,
            issue_id=issue_id,
            project_id=project_id,
        )

    projects_payload = client.list_projects()

    for project in extract_results(projects_payload):
        current_project_id = str(project.get("id", ""))
        if not current_project_id:
            continue

        try:
            work_items_payload = client.list_work_items(current_project_id)
        except PlaneClientError:
            continue

        for work_item in extract_results(work_items_payload):
            if work_item_identifier_matches(work_item, issue_id):
                return current_project_id, work_item

    raise HTTPException(
        status_code=404,
        detail=(
            "Plane work item not found. Pass project_id explicitly if issue_id "
            "is not a Plane UUID visible in the first work-items page."
        ),
    )


def _resolve_plane_work_item_in_project(
    client: PlaneClient,
    issue_id: str,
    project_id: str,
) -> tuple[str, dict[str, Any]]:
    try:
        work_item = client.get_work_item(project_id=project_id, work_item_id=issue_id)
        return project_id, work_item
    except PlaneClientError as error:
        work_items_payload = client.list_work_items(project_id)

        for work_item in extract_results(work_items_payload):
            if work_item_identifier_matches(work_item, issue_id):
                return project_id, work_item

        detail = f"Plane work item not found: project_id={project_id}, issue_id={issue_id}"
        raise HTTPException(status_code=404, detail=detail) from error


@router.get("/recommendations/issue/{issue_id}")
def recommend_for_issue(
    issue_id: str,
    project_id: str | None = Query(default=None),
    mode: str = Query(default="balanced_workload"),
    top_k: int = Query(default=3, ge=1, le=10),
    write_back: bool = Query(default=False),
    auto_assign: bool = Query(default=False),
    threshold: float = Query(default=0.75, ge=0.0, le=1.0),
    use_llm: bool = Query(default=False),
) -> dict[str, Any]:
    normalized_mode = normalize_mode(mode)

    if issue_id.startswith("TASK-"):
        if write_back:
            raise HTTPException(
                status_code=400,
                detail="write_back=true is available only for real Plane work items.",
            )

        if auto_assign:
            raise HTTPException(
                status_code=400,
                detail="auto_assign=true is available only for real Plane work items.",
            )

        return recommend_synthetic_task(
            task_id=issue_id,
            mode=normalized_mode,
            top_k=top_k,
            use_llm=use_llm,
        )

    try:
        client = PlaneClient()
        resolved_project_id, work_item = resolve_plane_work_item(
            client=client,
            issue_id=issue_id,
            project_id=project_id,
        )

        return run_agentic_recommendation(
            issue=work_item,
            project_id=resolved_project_id,
            work_item_id=str(work_item.get("id", issue_id)),
            mode=normalized_mode,
            top_k=top_k,
            write_back=write_back,
            auto_assign=auto_assign,
            threshold=threshold,
            use_llm=use_llm,
        )
    except HTTPException:
        raise
    except PlaneClientError as error:
        raise HTTPException(status_code=502, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error)) from error


@router.get("/recommendations/project/{project_id}/open-issues")
def recommend_for_project_open_issues(
    project_id: str,
    mode: str = Query(default="balanced_workload"),
    limit: int = Query(default=10, ge=1, le=50),
    use_llm: bool = Query(default=False),
) -> dict[str, Any]:
    normalized_mode = normalize_mode(mode)

    try:
        client = PlaneClient()
        work_items_payload = client.list_work_items(project_id)
        work_items = extract_results(work_items_payload)
        open_work_items = [
            work_item for work_item in work_items if is_open_work_item(work_item)
        ][:limit]

        recommendations = _recommend_for_work_items(
            work_items=open_work_items,
            project_id=project_id,
            mode=normalized_mode,
            use_llm=use_llm,
        )

        return {
            "project_id": project_id,
            "mode": normalized_mode,
            "limit": limit,
            "processed_count": len(recommendations),
            "write_back": False,
            "recommendations": recommendations,
        }
    except PlaneClientError as error:
        raise HTTPException(status_code=502, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error)) from error


def _recommend_for_work_items(
    work_items: list[dict[str, Any]],
    project_id: str,
    mode: str,
    use_llm: bool,
) -> list[dict[str, Any]]:
    recommendations: list[dict[str, Any]] = []

    for work_item in work_items:
        try:
            recommendation = run_agentic_recommendation(
                issue=work_item,
                project_id=project_id,
                work_item_id=str(work_item.get("id", "")),
                mode=mode,
                top_k=3,
                write_back=False,
                auto_assign=False,
                threshold=0.75,
                use_llm=use_llm,
            )
            recommendations.append(recommendation)
        except Exception as error:
            recommendations.append(
                {
                    "task_id": str(work_item.get("id", "")),
                    "title": str(work_item.get("name", "")),
                    "source": "agentic_pipeline",
                    "errors": [
                        {
                            "step": "batch_recommendation",
                            "message": str(error),
                        }
                    ],
                }
            )

    return recommendations


@router.post("/recommendations/manual")
def recommend_for_manual_task(
    request: ManualRecommendationRequest,
) -> dict[str, Any]:
    normalized_mode = normalize_mode(request.mode)

    try:
        response = run_agentic_recommendation(
            issue=request.issue,
            mode=normalized_mode,
            top_k=request.top_k,
            write_back=False,
            auto_assign=False,
            threshold=0.75,
            use_llm=request.use_llm,
        )

        if request.employees:
            response["manual_employees_note"] = (
                "Manual employees were received, but current orchestrator uses "
                "synthetic team profiles from data/synthetic/employees.csv. "
                "Employee override can be added later in Team Analyzer if needed."
            )

        return response
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error)) from error