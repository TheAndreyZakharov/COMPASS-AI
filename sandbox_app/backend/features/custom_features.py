from __future__ import annotations

import hashlib
import json
from typing import Any


def stable_text_number(value: Any) -> float:
    text = str(value or "")
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    integer = int(digest[:12], 16)
    return float(integer / 0xFFFFFFFFFFFF)


def parse_jsonish(value: Any) -> Any:
    if not isinstance(value, str):
        return value

    stripped = value.strip()
    if not stripped or stripped[0] not in "[{":
        return value

    try:
        return json.loads(stripped)
    except json.JSONDecodeError:
        return value


def collect_custom_features(record: dict[str, Any]) -> dict[str, Any]:
    candidates = (
        record.get("custom_features"),
        record.get("custom_employee_features"),
        record.get("custom_task_features"),
        record.get("custom_outcome_features"),
    )

    merged: dict[str, Any] = {}

    for candidate in candidates:
        parsed = parse_jsonish(candidate)
        if isinstance(parsed, dict):
            merged.update(parsed)

    return merged


def flatten_custom_features(prefix: str, record: dict[str, Any]) -> dict[str, float]:
    features: dict[str, float] = {}

    for raw_name, raw_value in collect_custom_features(record).items():
        name = str(raw_name).strip().lower().replace(" ", "_")
        value = parse_jsonish(raw_value)
        column_prefix = f"{prefix}_{name}"

        if isinstance(value, bool):
            features[column_prefix] = 1.0 if value else 0.0
        elif isinstance(value, int | float):
            features[column_prefix] = float(value)
        elif isinstance(value, (list, dict)):
            features[f"{column_prefix}_count"] = float(len(value))
            features[f"{column_prefix}_hash"] = stable_text_number(
                json.dumps(value, ensure_ascii=False, sort_keys=True)
            )
        elif value is None:
            features[column_prefix] = 0.0
        else:
            features[f"{column_prefix}_hash"] = stable_text_number(value)

    return features