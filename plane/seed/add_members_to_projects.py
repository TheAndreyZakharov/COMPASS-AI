from __future__ import annotations

from src.integration.plane_client import PlaneClient, PlaneClientError

DEMO_EMAILS = {
    "polina.vasilieva@compass.local",
    "nikita.egorov@compass.local",
    "sergey.pavlov@compass.local",
    "olga.volkova@compass.local",
    "darya.solovieva@compass.local",
    "pavel.volkov@compass.local",
    "andrey.gromov@compass.local",
    "admin@compass.local",
}

PROJECT_MEMBER_ROLE = 15


def email_of(member: dict[str, object]) -> str:
    return str(member.get("email") or "").strip().lower()


def member_id_of(member: dict[str, object]) -> str:
    return str(member.get("id") or member.get("member") or "").strip()


def main() -> None:
    print("Adding active Plane workspace members to projects...")

    try:
        with PlaneClient() as client:
            workspace_members = client.list_workspace_members()
            active_members_by_email = {
                email_of(member): member
                for member in workspace_members
                if email_of(member) in DEMO_EMAILS and member_id_of(member)
            }

            print(f"Active demo workspace members: {len(active_members_by_email)}")

            missing = sorted(DEMO_EMAILS - set(active_members_by_email))
            if missing:
                print()
                print("These users are not active workspace members yet:")
                for email in missing:
                    print(f"- {email}")
                print()
                print("Fix them in Plane first. Pending invitations are not enough.")

            projects = client.list_projects()

            for project in projects:
                project_id = str(project.get("id") or "")
                project_name = str(project.get("name") or "")

                if not project_id:
                    continue

                existing_project_members = client.list_project_members(project_id)
                existing_ids = {member_id_of(member) for member in existing_project_members}

                print()
                print(f"Project: {project_name}")
                print(f"Existing project members: {len(existing_ids)}")

                for email, member in active_members_by_email.items():
                    member_id = member_id_of(member)

                    if member_id in existing_ids:
                        print(f"  exists: {email}")
                        continue

                    try:
                        client.create_project_member(
                            project_id=project_id,
                            member_id=member_id,
                            role=PROJECT_MEMBER_ROLE,
                        )
                    except PlaneClientError as exc:
                        print(f"  failed: {email} -> {exc}")
                        continue

                    print(f"  added: {email}")

            print()
            print("Project member seeding completed.")

    except PlaneClientError as exc:
        raise SystemExit(f"Project member seeding failed: {exc}") from exc


if __name__ == "__main__":
    main()