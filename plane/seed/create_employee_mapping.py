from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from src.integration.plane_client import PlaneClient, PlaneClientError

PROJECT_ROOT = Path(__file__).resolve().parents[2]
EMPLOYEES_CSV_PATH = PROJECT_ROOT / "data" / "synthetic" / "employees.csv"
MAPPING_CSV_PATH = PROJECT_ROOT / "data" / "processed" / "employee_plane_mapping.csv"

PLANE_EMAIL_TO_EMPLOYEE_NAME = {
    "polina.vasilieva@compass.local": "Полина Васильева",
    "nikita.egorov@compass.local": "Никита Егоров",
    "sergey.pavlov@compass.local": "Сергей Павлов",
    "olga.volkova@compass.local": "Ольга Волкова",
    "darya.solovieva@compass.local": "Дарья Соловьёва",
    "pavel.volkov@compass.local": "Павел Волков",
    "andrey.gromov@compass.local": "Андрей Громов",
}

UNMAPPED_PLANE_EMAILS = {
    "admin@compass.local",
}


def clean_text(value: Any) -> str:
    if value is None:
        return ""

    text = str(value).strip()

    if text.lower() in {"nan", "none", "null"}:
        return ""

    return text


def clean_email(value: Any) -> str:
    return clean_text(value).lower()


def normalize_member(member: dict[str, Any]) -> dict[str, str]:
    user = member.get("member") or member.get("user") or member

    if not isinstance(user, dict):
        user = member

    member_detail = member.get("member_detail")
    if not isinstance(member_detail, dict):
        member_detail = {}

    plane_user_id = clean_text(
        user.get("id")
        or user.get("user_id")
        or member_detail.get("id")
        or member_detail.get("user_id")
        or member.get("member_id")
        or member.get("member")
        or member.get("user")
        or member.get("id")
    )

    first_name = clean_text(
        user.get("first_name")
        or member_detail.get("first_name")
        or member.get("first_name")
    )
    last_name = clean_text(
        user.get("last_name")
        or member_detail.get("last_name")
        or member.get("last_name")
    )
    display_name = clean_text(
        user.get("display_name")
        or user.get("name")
        or member_detail.get("display_name")
        or member_detail.get("name")
        or member.get("display_name")
        or member.get("name")
    )
    email = clean_email(
        user.get("email")
        or member_detail.get("email")
        or member.get("email")
    )

    if not display_name:
        display_name = " ".join(part for part in [first_name, last_name] if part)

    if not display_name and email:
        display_name = email.split("@")[0]

    return {
        "plane_user_id": plane_user_id,
        "plane_display_name": display_name,
        "plane_first_name": first_name,
        "plane_last_name": last_name,
        "plane_email": email,
    }


def collect_plane_members() -> list[dict[str, str]]:
    members_by_id: dict[str, dict[str, str]] = {}

    with PlaneClient() as client:
        projects = client.list_projects()

        if not projects:
            raise PlaneClientError("No Plane projects found.")

        for project in projects:
            project_id = clean_text(project.get("id"))
            project_name = clean_text(project.get("name"))

            if not project_id:
                continue

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

    return sorted(
        members_by_id.values(),
        key=lambda item: item["plane_email"] or item["plane_display_name"],
    )


def employee_lookup_by_name(employees: pd.DataFrame) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}

    for _, employee in employees.iterrows():
        name = clean_text(employee.get("name"))
        if not name:
            continue

        result[name] = employee.to_dict()

    return result


def plane_member_by_employee_name(
    plane_members: list[dict[str, str]],
) -> dict[str, dict[str, str]]:
    result: dict[str, dict[str, str]] = {}

    for member in plane_members:
        email = clean_email(member.get("plane_email"))
        employee_name = PLANE_EMAIL_TO_EMPLOYEE_NAME.get(email)

        if not employee_name:
            continue

        result[employee_name] = member

    return result


def validate_plane_members(plane_members: list[dict[str, str]]) -> None:
    known_emails = set(PLANE_EMAIL_TO_EMPLOYEE_NAME) | UNMAPPED_PLANE_EMAILS
    actual_emails = {
        clean_email(member.get("plane_email"))
        for member in plane_members
        if clean_email(member.get("plane_email"))
    }

    unknown_emails = sorted(actual_emails - known_emails)
    missing_emails = sorted(set(PLANE_EMAIL_TO_EMPLOYEE_NAME) - actual_emails)

    if unknown_emails:
        print()
        print("Unknown Plane member emails found:")
        for email in unknown_emails:
            print(f"- {email}")
        print("They will stay unmapped until you add them to the mapping dictionary.")

    if missing_emails:
        print()
        print("Expected Plane member emails not found in project members:")
        for email in missing_emails:
            print(f"- {email}")


def create_mapping() -> pd.DataFrame:
    if not EMPLOYEES_CSV_PATH.exists():
        raise FileNotFoundError(
            f"Missing synthetic employees file: {EMPLOYEES_CSV_PATH}. "
            "Run make generate-data first."
        )

    employees = pd.read_csv(EMPLOYEES_CSV_PATH)
    plane_members = collect_plane_members()

    validate_plane_members(plane_members)

    members_by_employee_name = plane_member_by_employee_name(plane_members)
    mapping_rows: list[dict[str, str]] = []

    for _, employee in employees.iterrows():
        employee_id = clean_text(employee.get("employee_id"))
        employee_name = clean_text(employee.get("name"))
        matched_member = members_by_employee_name.get(employee_name, {})

        mapping_rows.append(
            {
                "employee_id": employee_id,
                "plane_user_id": clean_text(matched_member.get("plane_user_id")),
                "name": employee_name,
                "email": clean_email(matched_member.get("plane_email")),
                "role": clean_text(employee.get("role")),
                "grade": clean_text(employee.get("grade")),
                "plane_display_name": clean_text(
                    matched_member.get("plane_display_name")
                ),
                "mapping_status": (
                    "auto_matched_by_email"
                    if matched_member
                    else "manual_required"
                ),
            }
        )

    mapping = pd.DataFrame(mapping_rows)
    MAPPING_CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
    mapping.to_csv(MAPPING_CSV_PATH, index=False)

    return mapping


def print_plane_members(plane_members: list[dict[str, str]]) -> None:
    print()
    print("Plane members found:")
    for member in plane_members:
        print(
            "- "
            f"{member['plane_display_name']} | "
            f"{member['plane_email']} | "
            f"{member['plane_user_id']}"
        )


def main() -> None:
    plane_members = collect_plane_members()
    print_plane_members(plane_members)

    mapping = create_mapping()

    print()
    print("Employee to Plane user mapping prepared.")
    print(f"Mapping saved to: {MAPPING_CSV_PATH}")
    print()
    print(mapping["mapping_status"].value_counts().to_string())
    print()
    print(mapping.to_string(index=False))


if __name__ == "__main__":
    main()