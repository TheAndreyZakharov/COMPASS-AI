from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from src.integration.plane_client import PlaneClient, PlaneClientError

PROJECT_ROOT = Path(__file__).resolve().parents[2]
EMPLOYEES_CSV_PATH = PROJECT_ROOT / "data" / "synthetic" / "employees.csv"
MAPPING_CSV_PATH = PROJECT_ROOT / "data" / "processed" / "employee_plane_mapping.csv"


def normalize_member(member: dict[str, Any]) -> dict[str, str]:
    user = member.get("member") or member.get("user") or member

    if not isinstance(user, dict):
        user = member

    plane_user_id = str(
        user.get("id")
        or user.get("user_id")
        or member.get("member_id")
        or member.get("id")
        or ""
    ).strip()

    display_name = str(
        user.get("display_name")
        or user.get("name")
        or user.get("first_name")
        or member.get("display_name")
        or ""
    ).strip()

    email = str(
        user.get("email")
        or member.get("email")
        or ""
    ).strip()

    return {
        "plane_user_id": plane_user_id,
        "plane_display_name": display_name,
        "plane_email": email,
    }


def collect_plane_members() -> list[dict[str, str]]:
    members_by_id: dict[str, dict[str, str]] = {}

    with PlaneClient() as client:
        projects = client.list_projects()

        if not projects:
            raise PlaneClientError("No Plane projects found.")

        for project in projects:
            project_id = str(project["id"])
            project_name = str(project.get("name", ""))

            try:
                members = client.list_project_members(project_id)
            except PlaneClientError as exc:
                print(f"Could not read members for project {project_name}: {exc}")
                continue

            for member in members:
                normalized = normalize_member(member)

                if not normalized["plane_user_id"]:
                    continue

                members_by_id[normalized["plane_user_id"]] = normalized

    return list(members_by_id.values())


def create_mapping() -> pd.DataFrame:
    if not EMPLOYEES_CSV_PATH.exists():
        raise FileNotFoundError(
            f"Missing synthetic employees file: {EMPLOYEES_CSV_PATH}. Run make generate-data first."
        )

    employees = pd.read_csv(EMPLOYEES_CSV_PATH)
    plane_members = collect_plane_members()

    mapping_rows: list[dict[str, str]] = []

    for index, employee in employees.iterrows():
        matched_member = plane_members[index] if index < len(plane_members) else {}

        mapping_rows.append(
            {
                "employee_id": str(employee["employee_id"]),
                "plane_user_id": str(matched_member.get("plane_user_id", "")),
                "name": str(employee["name"]),
                "email": str(matched_member.get("plane_email", "")),
                "role": str(employee["role"]),
                "grade": str(employee["grade"]),
                "mapping_status": "auto_matched" if matched_member else "manual_required",
            }
        )

    mapping = pd.DataFrame(mapping_rows)
    MAPPING_CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
    mapping.to_csv(MAPPING_CSV_PATH, index=False)

    return mapping


def main() -> None:
    mapping = create_mapping()

    print("Employee to Plane user mapping prepared.")
    print(f"Mapping saved to: {MAPPING_CSV_PATH}")
    print()
    print(mapping["mapping_status"].value_counts().to_string())
    print()
    print(mapping.to_string(index=False))


if __name__ == "__main__":
    main()