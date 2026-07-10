from __future__ import annotations

import hashlib
import json
import re
from typing import Any

TEXT_BUCKET_COUNT = 8
SKIPPED_CUSTOM_FEATURE_NAMES = {
    "id",
    "ids",
    "uuid",
    "guid",
    "name",
    "full_name",
    "first_name",
    "last_name",
    "surname",
    "title",
    "description",
    "summary",
    "comment",
    "comments",
    "note",
    "notes",
    "text",
    "body",
}
IDENTIFIER_SUFFIXES = ("_id", "_ids", "_uuid", "_guid")
FEATURE_NAME_RE = re.compile(r"[^a-z0-9_]+")


def stable_text_bucket(value: Any, bucket_count: int = TEXT_BUCKET_COUNT) -> int:
    text = str(value or "")
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    return int(digest[:8], 16) % bucket_count


def normalize_feature_name(value: Any) -> str:
    text = str(value or "").strip().lower().replace(" ", "_")
    text = FEATURE_NAME_RE.sub("_", text).strip("_")
    return text or "custom_feature"


def should_skip_custom_feature(name: str) -> bool:
    return name in SKIPPED_CUSTOM_FEATURE_NAMES or name.endswith(IDENTIFIER_SUFFIXES)


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
        name = normalize_feature_name(raw_name)

        if should_skip_custom_feature(name):
            continue

        value = parse_jsonish(raw_value)
        column_prefix = f"{prefix}_{name}"

        if isinstance(value, bool):
            features[column_prefix] = 1.0 if value else 0.0
        elif isinstance(value, int | float):
            features[column_prefix] = float(value)
        elif isinstance(value, (list, dict)):
            features[f"{column_prefix}_count"] = float(len(value))
            bucket = stable_text_bucket(json.dumps(value, ensure_ascii=False, sort_keys=True))
            for index in range(TEXT_BUCKET_COUNT):
                features[f"{column_prefix}_bucket_{index}"] = 1.0 if index == bucket else 0.0
        elif value is None:
            features[column_prefix] = 0.0
        else:
            text = str(value).strip()
            features[f"{column_prefix}_present"] = 1.0 if text else 0.0
            bucket = stable_text_bucket(text)
            for index in range(TEXT_BUCKET_COUNT):
                features[f"{column_prefix}_bucket_{index}"] = 1.0 if index == bucket else 0.0

    return features
