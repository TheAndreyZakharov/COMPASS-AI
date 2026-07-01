from __future__ import annotations

from src.integration.plane_client import PlaneClient, PlaneClientError


def main() -> None:
    print("Checking Plane connection...")

    try:
        with PlaneClient() as client:
            print(f"Workspace slug: {client.workspace_slug}")
            print(f"Base URL: {client.base_url}")

            if not client.healthcheck():
                raise PlaneClientError(
                    "Plane API healthcheck failed. Check PLANE_BASE_URL, "
                    "PLANE_WORKSPACE_SLUG and PLANE_API_KEY."
                )

            print("Plane API healthcheck: OK")

            projects = client.list_projects()
            print(f"Projects found: {len(projects)}")

            if not projects:
                print("No projects found.")
                return

            for project in projects:
                project_id = project.get("id")
                project_name = project.get("name")
                project_identifier = project.get("identifier")

                print()
                print(f"Project: {project_name} ({project_identifier})")
                print(f"Project ID: {project_id}")

                if not project_id:
                    print("  Missing project id, skipping.")
                    continue

                try:
                    work_items = client.list_work_items(project_id)
                    states = client.list_states(project_id)
                    labels = client.list_labels(project_id)

                    print(f"  Work items: {len(work_items)}")
                    print(f"  States: {len(states)}")
                    print(f"  Labels: {len(labels)}")

                    if work_items:
                        first_item = work_items[0]
                        print(
                            "  First work item:",
                            first_item.get("name") or first_item.get("title"),
                        )

                except PlaneClientError as exc:
                    print(f"  Project check failed: {exc}")

            print()
            print("Plane connection check completed.")

    except PlaneClientError as exc:
        raise SystemExit(f"Plane connection failed: {exc}") from exc


if __name__ == "__main__":
    main()