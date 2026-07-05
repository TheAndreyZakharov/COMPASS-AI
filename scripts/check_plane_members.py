from __future__ import annotations

from src.integration.plane_client import PlaneClient, PlaneClientError


def value(item: dict[str, object], *keys: str) -> object:
    for key in keys:
        current = item.get(key)
        if current not in (None, ""):
            return current
    return ""


def main() -> None:
    print("Checking Plane members...")

    try:
        with PlaneClient() as client:
            print(f"Workspace slug: {client.workspace_slug}")
            print(f"Base URL: {client.base_url}")
            print()

            workspace_members = client.list_workspace_members()
            print(f"Workspace members: {len(workspace_members)}")

            for member in workspace_members:
                print(
                    "-",
                    value(member, "email"),
                    "|",
                    value(member, "display_name", "name"),
                    "| id:",
                    value(member, "id", "member"),
                    "| role:",
                    value(member, "role"),
                )

            print()
            invitations = client.list_workspace_invitations()
            print(f"Workspace invitations: {len(invitations)}")

            for invitation in invitations:
                print(
                    "-",
                    value(invitation, "email"),
                    "| accepted:",
                    value(invitation, "accepted"),
                    "| responded_at:",
                    value(invitation, "responded_at"),
                    "| id:",
                    value(invitation, "id"),
                )

            print()
            projects = client.list_projects()

            for project in projects:
                project_id = str(project.get("id") or "")
                project_name = str(project.get("name") or "")
                project_identifier = str(project.get("identifier") or "")

                if not project_id:
                    continue

                project_members = client.list_project_members(project_id)

                print()
                print(f"Project: {project_name} ({project_identifier})")
                print(f"Project ID: {project_id}")
                print(f"Project members: {len(project_members)}")

                for member in project_members:
                    print(
                        "  -",
                        value(member, "email"),
                        "|",
                        value(member, "display_name", "name"),
                        "| id:",
                        value(member, "id", "member"),
                        "| role:",
                        value(member, "role"),
                    )

            print()
            print("Plane members check completed.")

    except PlaneClientError as exc:
        raise SystemExit(f"Plane members check failed: {exc}") from exc


if __name__ == "__main__":
    main()