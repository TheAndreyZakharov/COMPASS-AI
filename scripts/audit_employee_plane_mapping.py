from __future__ import annotations

from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MAPPING_CSV_PATH = PROJECT_ROOT / "data" / "processed" / "employee_plane_mapping.csv"

EXPECTED_EMAIL_BY_NAME = {
    "Полина Васильева": "polina.vasilieva@compass.local",
    "Никита Егоров": "nikita.egorov@compass.local",
    "Сергей Павлов": "sergey.pavlov@compass.local",
    "Ольга Волкова": "olga.volkova@compass.local",
    "Дарья Соловьёва": "darya.solovieva@compass.local",
    "Павел Волков": "pavel.volkov@compass.local",
    "Андрей Громов": "andrey.gromov@compass.local",
}


def clean_text(value: object) -> str:
    if value is None:
        return ""

    text = str(value).strip()

    if text.lower() in {"nan", "none", "null"}:
        return ""

    return text


def clean_email(value: object) -> str:
    return clean_text(value).lower()


def main() -> None:
    if not MAPPING_CSV_PATH.exists():
        raise SystemExit(f"Mapping file not found: {MAPPING_CSV_PATH}")

    mapping = pd.read_csv(MAPPING_CSV_PATH)
    errors: list[str] = []

    for employee_name, expected_email in EXPECTED_EMAIL_BY_NAME.items():
        rows = mapping[mapping["name"].astype(str) == employee_name]

        if rows.empty:
            errors.append(f"Missing employee in mapping: {employee_name}")
            continue

        row = rows.iloc[0]
        actual_email = clean_email(row.get("email"))
        plane_user_id = clean_text(row.get("plane_user_id"))
        mapping_status = clean_text(row.get("mapping_status"))

        if actual_email != expected_email:
            errors.append(
                f"{employee_name}: expected {expected_email}, got {actual_email}"
            )

        if not plane_user_id:
            errors.append(f"{employee_name}: missing plane_user_id")

        if mapping_status == "manual_required":
            errors.append(f"{employee_name}: still manual_required")

    forbidden_matches = {
        "Анна Смирнова",
        "Иван Петров",
        "Мария Кузнецова",
        "Дмитрий Соколов",
        "Екатерина Новикова",
        "Максим Орлов",
        "Алексей Морозов",
    }

    for employee_name in forbidden_matches:
        rows = mapping[mapping["name"].astype(str) == employee_name]
        if rows.empty:
            continue

        row = rows.iloc[0]
        actual_email = clean_email(row.get("email"))
        plane_user_id = clean_text(row.get("plane_user_id"))

        if actual_email or plane_user_id:
            errors.append(
                f"{employee_name}: must not be mapped, "
                f"got email={actual_email}, plane_user_id={plane_user_id}"
            )

    if errors:
        print("Employee Plane mapping audit failed:")
        for error in errors:
            print(f"- {error}")
        raise SystemExit(1)

    print("Employee Plane mapping audit passed.")


if __name__ == "__main__":
    main()