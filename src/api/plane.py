from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd
from fastapi import APIRouter, HTTPException, Query

from src.agents.orchestrator import run_agentic_recommendation
from src.integration.plane_client import PlaneClient, PlaneClientError

router = APIRouter(prefix="/plane", tags=["plane"])

PROJECT_ROOT = Path(__file__).resolve().parents[2]
EMPLOYEES_PATH = PROJECT_ROOT / "data" / "synthetic" / "employees.csv"
EMPLOYEE_MAPPING_PATH = PROJECT_ROOT / "data" / "processed" / "employee_plane_mapping.csv"

DEFAULT_MEMBER_ROLE = "plane_member"
DEFAULT_MEMBER_GRADE = "unknown"


def extract_email(member: dict[str, Any]) -> str:
    direct_email = str(member.get("email") or "").strip().lower()
    if direct_email:
        return direct_email

    member_detail = member.get("member_detail")
    if isinstance(member_detail, dict):
        return str(member_detail.get("email") or "").strip().lower()

    user = member.get("user")
    if isinstance(user, dict):
        return str(user.get("email") or "").strip().lower()

    return ""


def extract_display_name(member: dict[str, Any]) -> str:
    for key in ("display_name", "name", "first_name"):
        value = str(member.get(key) or "").strip()
        if value:
            return value

    member_detail = member.get("member_detail")
    if isinstance(member_detail, dict):
        for key in ("display_name", "name", "first_name"):
            value = str(member_detail.get(key) or "").strip()
            if value:
                return value

    email = extract_email(member)
    if email:
        return email.split("@")[0]

    return "Plane member"


def extract_member_id(member: dict[str, Any]) -> str:
    for key in ("member", "member_id", "user", "user_id", "id"):
        value = member.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()

    member_detail = member.get("member_detail")
    if isinstance(member_detail, dict):
        for key in ("id", "member", "user_id"):
            value = member_detail.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()

    user = member.get("user")
    if isinstance(user, dict):
        value = user.get("id")
        if isinstance(value, str) and value.strip():
            return value.strip()

    return ""


def extract_results(response: object) -> list[dict[str, Any]]:
    if isinstance(response, list):
        return [item for item in response if isinstance(item, dict)]

    if isinstance(response, dict):
        results = response.get("results")
        if isinstance(results, list):
            return [item for item in results if isinstance(item, dict)]

    return []


def is_open_work_item(work_item: dict[str, Any]) -> bool:
    if work_item.get("completed_at") or work_item.get("archived_at"):
        return False

    state = work_item.get("state")

    if isinstance(state, dict):
        state_group = str(state.get("group") or "").strip().lower()
        if state_group in {"completed", "cancelled"}:
            return False

    return True


def work_item_title(work_item: dict[str, Any]) -> str:
    return str(work_item.get("name") or work_item.get("title") or "").strip()


def work_item_identifier(work_item: dict[str, Any]) -> str:
    sequence_id = work_item.get("sequence_id")
    if sequence_id not in (None, ""):
        return str(sequence_id)

    return str(work_item.get("id") or "").strip()


def assignee_ids_from_work_item(work_item: dict[str, Any]) -> set[str]:
    assignees = work_item.get("assignees")
    result: set[str] = set()

    if not isinstance(assignees, list):
        return result

    for assignee in assignees:
        if isinstance(assignee, str) and assignee.strip():
            result.add(assignee.strip())
            continue

        if isinstance(assignee, dict):
            for key in ("id", "member", "member_id", "user_id"):
                value = assignee.get(key)
                if isinstance(value, str) and value.strip():
                    result.add(value.strip())

    return result


def normalize_project(project: dict[str, Any]) -> dict[str, Any]:
    return {
        "project_id": project.get("id"),
        "name": project.get("name"),
        "identifier": project.get("identifier"),
        "total_members": project.get("total_members"),
        "total_cycles": project.get("total_cycles"),
        "workspace": project.get("workspace"),
    }


def normalize_work_item(
    work_item: dict[str, Any],
    project_id: str,
    project_name: str,
    project_identifier: str,
) -> dict[str, Any]:
    assignees = work_item.get("assignees")
    labels = work_item.get("labels")

    return {
        "id": work_item.get("id"),
        "name": work_item_title(work_item),
        "identifier": work_item_identifier(work_item),
        "sequence_id": work_item.get("sequence_id"),
        "priority": work_item.get("priority"),
        "state": work_item.get("state"),
        "labels": labels if isinstance(labels, list) else [],
        "assignees": assignees if isinstance(assignees, list) else [],
        "assignees_count": len(assignees) if isinstance(assignees, list) else 0,
        "project_id": project_id,
        "project_name": project_name,
        "project_identifier": project_identifier,
        "target_date": work_item.get("target_date"),
        "start_date": work_item.get("start_date"),
        "created_at": work_item.get("created_at"),
        "updated_at": work_item.get("updated_at"),
        "completed_at": work_item.get("completed_at"),
        "archived_at": work_item.get("archived_at"),
        "is_open": is_open_work_item(work_item),
    }


def load_employee_profiles() -> pd.DataFrame:
    if not EMPLOYEES_PATH.exists():
        return pd.DataFrame()

    employees = pd.read_csv(EMPLOYEES_PATH)
    if "employee_id" not in employees.columns:
        return pd.DataFrame()

    return employees


def load_employee_mapping() -> pd.DataFrame:
    if not EMPLOYEE_MAPPING_PATH.exists():
        return pd.DataFrame()

    mapping = pd.read_csv(EMPLOYEE_MAPPING_PATH)
    required_columns = {"employee_id", "plane_user_id"}

    if not required_columns.issubset(set(mapping.columns)):
        return pd.DataFrame()

    return mapping


def mapped_employee_by_plane_user_id() -> dict[str, dict[str, Any]]:
    employees = load_employee_profiles()
    mapping = load_employee_mapping()

    if employees.empty or mapping.empty:
        return {}

    merged = employees.merge(
        mapping[["employee_id", "plane_user_id", "mapping_status"]],
        on="employee_id",
        how="left",
        suffixes=("", "_mapping"),
    )

    result: dict[str, dict[str, Any]] = {}

    for _, row in merged.iterrows():
        plane_user_id = str(row.get("plane_user_id_mapping") or "").strip()
        if not plane_user_id:
            plane_user_id = str(row.get("plane_user_id") or "").strip()

        if not plane_user_id:
            continue

        employee = row.to_dict()
        employee["plane_user_id"] = plane_user_id
        employee["mapping_status"] = row.get("mapping_status", "mapped")
        result[plane_user_id] = employee

    return result


def workload_from_active_tasks(active_tasks_count: int) -> float:
    if active_tasks_count <= 0:
        return 0.15

    if active_tasks_count == 1:
        return 0.35

    if active_tasks_count == 2:
        return 0.55

    if active_tasks_count == 3:
        return 0.75

    return 0.90


def workload_risk(workload: float) -> str:
    if workload >= 0.95:
        return "critical"

    if workload >= 0.85:
        return "high"

    if workload >= 0.70:
        return "medium"

    return "low"


def fallback_employee_from_member(
    member: dict[str, Any],
    active_tasks_count: int,
) -> dict[str, Any]:
    plane_user_id = extract_member_id(member)
    email = extract_email(member)
    display_name = extract_display_name(member)
    current_workload = workload_from_active_tasks(active_tasks_count)

    return {
        "employee_id": f"PLANE-{plane_user_id[:8] or email}",
        "plane_user_id": plane_user_id,
        "name": display_name,
        "email": email,
        "role": DEFAULT_MEMBER_ROLE,
        "grade": DEFAULT_MEMBER_GRADE,
        "experience_years": 1,
        "primary_stack": "unknown",
        "skills": {},
        "current_workload": current_workload,
        "active_tasks_count": active_tasks_count,
        "avg_completion_speed": 0.70,
        "avg_quality_score": 0.70,
        "deadline_reliability": 0.70,
        "learning_goals": [],
        "mentor_level": 1,
        "availability": "available",
        "availability_score": max(0.0, 1.0 - current_workload),
        "timezone": "Europe/Berlin",
        "workload_risk": workload_risk(current_workload),
        "mapping_status": "plane_unmapped",
        "source": "plane_project_member",
    }


def candidate_from_mapped_employee(
    employee: dict[str, Any],
    member: dict[str, Any],
    active_tasks_count: int,
) -> dict[str, Any]:
    result = dict(employee)
    current_workload = workload_from_active_tasks(active_tasks_count)

    result["plane_user_id"] = extract_member_id(member)
    result["email"] = extract_email(member)
    result["name"] = result.get("name") or extract_display_name(member)
    result["active_tasks_count"] = active_tasks_count
    result["current_workload"] = current_workload
    result["availability_score"] = max(0.0, 1.0 - current_workload)
    result["workload_risk"] = workload_risk(current_workload)
    result["mapping_status"] = result.get("mapping_status") or "mapped"
    result["source"] = "plane_project_member"

    return result


def build_active_task_count_by_member(
    work_items: list[dict[str, Any]],
) -> dict[str, int]:
    counts: dict[str, int] = {}

    for work_item in work_items:
        if not is_open_work_item(work_item):
            continue

        for assignee_id in assignee_ids_from_work_item(work_item):
            counts[assignee_id] = counts.get(assignee_id, 0) + 1

    return counts


def build_plane_candidate_profiles(
    project_members: list[dict[str, Any]],
    work_items: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    mapped_by_user_id = mapped_employee_by_plane_user_id()
    active_task_counts = build_active_task_count_by_member(work_items)

    candidates: list[dict[str, Any]] = []

    for member in project_members:
        plane_user_id = extract_member_id(member)
        if not plane_user_id:
            continue

        active_tasks_count = active_task_counts.get(plane_user_id, 0)
        mapped_employee = mapped_by_user_id.get(plane_user_id)

        if mapped_employee is not None:
            candidate = candidate_from_mapped_employee(
                employee=mapped_employee,
                member=member,
                active_tasks_count=active_tasks_count,
            )
        else:
            candidate = fallback_employee_from_member(
                member=member,
                active_tasks_count=active_tasks_count,
            )

        candidates.append(candidate)

    return candidates


def project_payload(
    client: PlaneClient,
    project: dict[str, Any],
    include_work_items: bool = True,
) -> dict[str, Any]:
    project_id = str(project.get("id") or "")
    project_name = str(project.get("name") or "")
    project_identifier = str(project.get("identifier") or "")

    members = client.list_project_members(project_id)
    work_items = client.list_work_items(project_id) if include_work_items else []
    normalized_work_items = [
        normalize_work_item(
            work_item=work_item,
            project_id=project_id,
            project_name=project_name,
            project_identifier=project_identifier,
        )
        for work_item in work_items
    ]

    open_work_items = [
        work_item
        for work_item in normalized_work_items
        if bool(work_item.get("is_open"))
    ]

    return {
        **normalize_project(project),
        "members_count": len(members),
        "members": members,
        "work_items_count": len(normalized_work_items),
        "open_work_items_count": len(open_work_items),
        "work_items": normalized_work_items,
    }


@router.get("/members")
def list_plane_members() -> dict[str, Any]:
    try:
        with PlaneClient() as client:
            workspace_members = client.list_workspace_members()
            invitations = client.list_workspace_invitations()
            projects = client.list_projects()

            project_items = [
                project_payload(client=client, project=project, include_work_items=False)
                for project in projects
                if project.get("id")
            ]

            active_emails = {extract_email(member) for member in workspace_members}
            pending_invitations = [
                invitation
                for invitation in invitations
                if not invitation.get("accepted")
                and extract_email(invitation) not in active_emails
            ]

            return {
                "workspace_slug": client.workspace_slug,
                "workspace_members_count": len(workspace_members),
                "pending_invitations_count": len(pending_invitations),
                "workspace_members": workspace_members,
                "pending_invitations": pending_invitations,
                "projects": project_items,
            }

    except PlaneClientError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.get("/projects")
def list_plane_projects() -> dict[str, Any]:
    try:
        with PlaneClient() as client:
            projects = client.list_projects()

            return {
                "workspace_slug": client.workspace_slug,
                "projects_count": len(projects),
                "projects": [normalize_project(project) for project in projects],
            }

    except PlaneClientError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.get("/projects/{project_id}/work-items")
def list_project_work_items(project_id: str) -> dict[str, Any]:
    try:
        with PlaneClient() as client:
            projects = client.list_projects()
            project = next(
                (
                    item
                    for item in projects
                    if str(item.get("id") or "") == str(project_id)
                ),
                None,
            )

            if project is None:
                raise HTTPException(status_code=404, detail="Plane project not found.")

            payload = project_payload(client=client, project=project, include_work_items=True)

            return {
                "workspace_slug": client.workspace_slug,
                "project": normalize_project(project),
                "members_count": payload["members_count"],
                "members": payload["members"],
                "work_items_count": payload["work_items_count"],
                "open_work_items_count": payload["open_work_items_count"],
                "work_items": payload["work_items"],
            }

    except PlaneClientError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.get("/live")
def plane_live() -> dict[str, Any]:
    try:
        with PlaneClient() as client:
            workspace_members = client.list_workspace_members()
            invitations = client.list_workspace_invitations()
            projects = client.list_projects()

            project_items = [
                project_payload(client=client, project=project, include_work_items=True)
                for project in projects
                if project.get("id")
            ]

            work_items_count = sum(
                int(project.get("work_items_count") or 0)
                for project in project_items
            )
            open_work_items_count = sum(
                int(project.get("open_work_items_count") or 0)
                for project in project_items
            )

            active_emails = {extract_email(member) for member in workspace_members}
            pending_invitations = [
                invitation
                for invitation in invitations
                if not invitation.get("accepted")
                and extract_email(invitation) not in active_emails
            ]

            return {
                "workspace_slug": client.workspace_slug,
                "workspace_members_count": len(workspace_members),
                "pending_invitations_count": len(pending_invitations),
                "projects_count": len(project_items),
                "work_items_count": work_items_count,
                "open_work_items_count": open_work_items_count,
                "workspace_members": workspace_members,
                "pending_invitations": pending_invitations,
                "projects": project_items,
            }

    except PlaneClientError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.get("/recommendations/work-item/{work_item_id}")
def recommend_plane_work_item(
    work_item_id: str,
    project_id: str = Query(...),
    mode: str = "balanced_workload",
    top_k: int = Query(default=3, ge=1, le=10),
    write_back: bool = False,
    auto_assign: bool = False,
    threshold: float = Query(default=0.75, ge=0.0, le=1.0),
    use_llm: bool = False,
) -> dict[str, Any]:
    try:
        with PlaneClient() as client:
            issue = client.get_work_item(project_id, work_item_id)
            project_members = client.list_project_members(project_id)
            work_items = client.list_work_items(project_id)

        candidates = build_plane_candidate_profiles(
            project_members=project_members,
            work_items=work_items,
        )

        if not candidates:
            raise HTTPException(
                status_code=400,
                detail="Plane project has no active members available for recommendation.",
            )

        response = run_agentic_recommendation(
            issue=issue,
            project_id=project_id,
            work_item_id=work_item_id,
            mode=mode,
            top_k=top_k,
            write_back=write_back,
            auto_assign=auto_assign,
            threshold=threshold,
            use_llm=use_llm,
            employees_override=candidates,
        )

        response["plane_live"] = {
            "project_id": project_id,
            "work_item_id": work_item_id,
            "candidate_scope": "plane_project_members",
            "candidate_count": len(candidates),
            "mapped_candidates_count": sum(
                1 for candidate in candidates if candidate.get("mapping_status") != "plane_unmapped"
            ),
            "unmapped_candidates_count": sum(
                1 for candidate in candidates if candidate.get("mapping_status") == "plane_unmapped"
            ),
        }

        return response

    except PlaneClientError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc