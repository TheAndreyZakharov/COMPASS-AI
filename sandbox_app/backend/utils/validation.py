from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class RecordValidationIssue:
    row_index: int
    table_name: str
    field_name: str
    message: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "row_index": self.row_index,
            "table_name": self.table_name,
            "field_name": self.field_name,
            "message": self.message,
        }


FALLBACK_REQUIRED_FIELDS: dict[str, tuple[str, ...]] = {
    "employees": (
        "employee_id",
        "name",
        "role",
        "grade",
        "skills",
    ),
    "tasks": (
        "task_id",
        "title",
        "status",
        "priority",
        "project_id",
    ),
    "assignment_history": (
        "assignment_id",
        "employee_id",
        "task_id",
        "planned_hours",
        "actual_hours",
        "quality_score",
        "deadline_status",
        "outcome_label",
    ),
    "training_pairs": (
        "pair_id",
        "task_id",
        "employee_id",
        "label",
        "target_score",
        "target_mode",
        "split",
    ),
}


def required_fields_for_table(table_name: str) -> tuple[str, ...]:
    return FALLBACK_REQUIRED_FIELDS.get(table_name, ())


def validate_record_required_fields_fallback(
    table_name: str,
    row_index: int,
    record: dict[str, Any],
) -> list[RecordValidationIssue]:
    issues: list[RecordValidationIssue] = []

    for field_name in required_fields_for_table(table_name):
        value = record.get(field_name)
        if value is None or value == "":
            issues.append(
                RecordValidationIssue(
                    row_index=row_index,
                    table_name=table_name,
                    field_name=field_name,
                    message=f"Missing required field '{field_name}'",
                )
            )

    return issues


def validate_record_with_core_contract(
    table_name: str,
    row_index: int,
    record: dict[str, Any],
) -> list[RecordValidationIssue]:
    try:
        from sandbox_app.backend.core.data_contracts import (
            validate_record_required_fields,
        )
    except ImportError:
        return validate_record_required_fields_fallback(table_name, row_index, record)

    try:
        result = validate_record_required_fields(table_name, record)
    except Exception as exc:
        return [
            RecordValidationIssue(
                row_index=row_index,
                table_name=table_name,
                field_name="__record__",
                message=str(exc),
            )
        ]

    if result is None or result is True:
        return []

    if isinstance(result, dict):
        missing = result.get("missing") or result.get("missing_fields") or []
        return [
            RecordValidationIssue(
                row_index=row_index,
                table_name=table_name,
                field_name=str(field_name),
                message=f"Missing required field '{field_name}'",
            )
            for field_name in missing
        ]

    if isinstance(result, (list, tuple, set)):
        return [
            RecordValidationIssue(
                row_index=row_index,
                table_name=table_name,
                field_name=str(field_name),
                message=f"Missing required field '{field_name}'",
            )
            for field_name in result
        ]

    return validate_record_required_fields_fallback(table_name, row_index, record)


def validate_records_against_contract(
    table_name: str,
    records: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    issues: list[RecordValidationIssue] = []

    for row_index, record in enumerate(records):
        if not isinstance(record, dict):
            issues.append(
                RecordValidationIssue(
                    row_index=row_index,
                    table_name=table_name,
                    field_name="__record__",
                    message="Record must be an object",
                )
            )
            continue

        issues.extend(validate_record_with_core_contract(table_name, row_index, record))

    return [issue.as_dict() for issue in issues]