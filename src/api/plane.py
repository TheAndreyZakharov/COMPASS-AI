from __future__ import annotations

from fastapi import APIRouter, HTTPException

from src.integration.plane_client import PlaneClient, PlaneClientError

router = APIRouter(prefix="/plane", tags=["plane"])


def extract_email(member: dict[str, object]) -> str:
    return str(member.get("email") or "").strip().lower()


def extract_member_id(member: dict[str, object]) -> str:
    return str(member.get("id") or member.get("member") or "").strip()


@router.get("/members")
def list_plane_members() -> dict[str, object]:
    try:
        with PlaneClient() as client:
            workspace_members = client.list_workspace_members()
            invitations = client.list_workspace_invitations()
            projects = client.list_projects()

            project_payload = []

            for project in projects:
                project_id = str(project.get("id") or "")
                if not project_id:
                    continue

                members = client.list_project_members(project_id)

                project_payload.append(
                    {
                        "project_id": project_id,
                        "name": project.get("name"),
                        "identifier": project.get("identifier"),
                        "members_count": len(members),
                        "members": members,
                    },
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
                "workspace_members": workspace_members,
                "pending_invitations": pending_invitations,
                "projects": project_payload,
            }

    except PlaneClientError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc