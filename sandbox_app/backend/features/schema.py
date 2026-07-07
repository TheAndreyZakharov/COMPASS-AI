from __future__ import annotations

import json
import re
from copy import deepcopy
from pathlib import Path
from typing import Any

from sandbox_app.backend.core.paths import CONFIG_DIR

FEATURE_SCHEMAS_DIR = CONFIG_DIR / "feature_schemas"

ALLOWED_FEATURE_TYPES = {
    "numeric",
    "categorical",
    "boolean",
    "text",
    "skill_list",
}

FEATURE_GROUPS = {
    "employee": "employee_features",
    "task": "task_features",
    "outcome": "outcome_features",
}

SYSTEM_PROFILE_IDS = {
    "developers",
    "designers",
}

PROFILE_ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9_-]{1,63}$")
FEATURE_NAME_PATTERN = re.compile(r"^[a-zA-Z][a-zA-Z0-9_]{1,63}$")


class FeatureSchemaError(ValueError):
    pass


def list_feature_schemas() -> list[dict[str, Any]]:
    schemas = []

    for schema_path in sorted(FEATURE_SCHEMAS_DIR.glob("*.json")):
        schema = load_feature_schema(schema_path.stem)
        schemas.append(build_schema_preview(schema))

    return schemas


def load_feature_schema(profile_id: str) -> dict[str, Any]:
    schema_path = get_schema_path(profile_id)

    if not schema_path.exists():
        raise FeatureSchemaError(f"Feature schema not found: {profile_id}")

    with schema_path.open("r", encoding="utf-8") as file:
        schema = json.load(file)

    return normalize_schema(schema)


def save_feature_schema(schema: dict[str, Any]) -> dict[str, Any]:
    normalized_schema = normalize_schema(schema)
    validate_feature_schema(normalized_schema)

    FEATURE_SCHEMAS_DIR.mkdir(parents=True, exist_ok=True)

    schema_path = get_schema_path(normalized_schema["profile_id"])
    with schema_path.open("w", encoding="utf-8") as file:
        json.dump(normalized_schema, file, ensure_ascii=False, indent=2)
        file.write("\n")

    return normalized_schema


def delete_feature_schema(profile_id: str) -> None:
    if profile_id in SYSTEM_PROFILE_IDS:
        raise FeatureSchemaError("System feature schemas cannot be deleted.")

    schema_path = get_schema_path(profile_id)

    if not schema_path.exists():
        raise FeatureSchemaError(f"Feature schema not found: {profile_id}")

    schema_path.unlink()


def create_feature_schema(schema: dict[str, Any]) -> dict[str, Any]:
    profile_id = str(schema.get("profile_id", "")).strip()
    schema_path = get_schema_path(profile_id)

    if schema_path.exists():
        raise FeatureSchemaError(f"Feature schema already exists: {profile_id}")

    return save_feature_schema(schema)


def update_feature_schema(
    profile_id: str,
    schema: dict[str, Any],
) -> dict[str, Any]:
    existing_schema = load_feature_schema(profile_id)
    updated_schema = deepcopy(schema)
    updated_schema["profile_id"] = profile_id

    if existing_schema.get("metadata", {}).get("system"):
        metadata = dict(updated_schema.get("metadata", {}))
        metadata["system"] = True
        updated_schema["metadata"] = metadata

    return save_feature_schema(updated_schema)


def add_feature(
    profile_id: str,
    group: str,
    feature: dict[str, Any],
) -> dict[str, Any]:
    schema = load_feature_schema(profile_id)
    group_key = get_group_key(group)
    normalized_feature = normalize_feature(feature)

    feature_names = {
        item["name"]
        for item in schema[group_key]
    }

    if normalized_feature["name"] in feature_names:
        raise FeatureSchemaError(
            f"Feature already exists: {normalized_feature['name']}"
        )

    schema[group_key].append(normalized_feature)
    return save_feature_schema(schema)


def rename_feature(
    profile_id: str,
    group: str,
    old_name: str,
    new_name: str,
) -> dict[str, Any]:
    schema = load_feature_schema(profile_id)
    group_key = get_group_key(group)

    validate_feature_name(new_name)

    for feature in schema[group_key]:
        if feature["name"] == old_name:
            feature["name"] = new_name
            return save_feature_schema(schema)

    raise FeatureSchemaError(f"Feature not found: {old_name}")


def delete_feature(
    profile_id: str,
    group: str,
    feature_name: str,
) -> dict[str, Any]:
    schema = load_feature_schema(profile_id)
    group_key = get_group_key(group)

    next_features = [
        feature
        for feature in schema[group_key]
        if feature["name"] != feature_name
    ]

    if len(next_features) == len(schema[group_key]):
        raise FeatureSchemaError(f"Feature not found: {feature_name}")

    schema[group_key] = next_features
    return save_feature_schema(schema)


def build_schema_preview(schema: dict[str, Any]) -> dict[str, Any]:
    normalized_schema = normalize_schema(schema)

    return {
        "profile_id": normalized_schema["profile_id"],
        "title": normalized_schema["title"],
        "description": normalized_schema["description"],
        "roles_count": len(normalized_schema["roles"]),
        "grades_count": len(normalized_schema["grades"]),
        "skills_count": len(normalized_schema["skills"]),
        "employee_features_count": len(normalized_schema["employee_features"]),
        "task_features_count": len(normalized_schema["task_features"]),
        "outcome_features_count": len(normalized_schema["outcome_features"]),
        "metadata": normalized_schema["metadata"],
    }


def normalize_schema(schema: dict[str, Any]) -> dict[str, Any]:
    normalized_schema = {
        "profile_id": str(schema.get("profile_id", "")).strip(),
        "title": str(schema.get("title", "")).strip(),
        "description": str(schema.get("description", "")).strip(),
        "roles": list(schema.get("roles", [])),
        "grades": list(schema.get("grades", [])),
        "skills": list(schema.get("skills", [])),
        "employee_features": list(schema.get("employee_features", [])),
        "task_features": list(schema.get("task_features", [])),
        "outcome_features": list(schema.get("outcome_features", [])),
        "grade_order": list(schema.get("grade_order", [])),
        "metadata": dict(schema.get("metadata", {})),
    }

    normalized_schema["roles"] = normalize_string_list(normalized_schema["roles"])
    normalized_schema["grades"] = normalize_string_list(normalized_schema["grades"])
    normalized_schema["skills"] = normalize_string_list(normalized_schema["skills"])

    if not normalized_schema["grade_order"]:
        normalized_schema["grade_order"] = normalized_schema["grades"]

    normalized_schema["grade_order"] = normalize_string_list(
        normalized_schema["grade_order"]
    )

    for group_key in FEATURE_GROUPS.values():
        normalized_schema[group_key] = [
            normalize_feature(feature)
            for feature in normalized_schema[group_key]
        ]

    return normalized_schema


def normalize_feature(feature: dict[str, Any]) -> dict[str, Any]:
    feature_type = str(feature.get("type", "")).strip()
    normalized_feature: dict[str, Any] = {
        "name": str(feature.get("name", "")).strip(),
        "type": feature_type,
    }

    if "label" in feature:
        normalized_feature["label"] = str(feature["label"]).strip()

    if "description" in feature:
        normalized_feature["description"] = str(feature["description"]).strip()

    if feature_type == "numeric":
        normalized_feature["min"] = feature.get("min", 0)
        normalized_feature["max"] = feature.get("max", 1)

    if feature_type == "categorical":
        values = feature.get("values", [])
        normalized_feature["values"] = normalize_string_list(values)

    return normalized_feature


def validate_feature_schema(schema: dict[str, Any]) -> None:
    validate_profile_id(schema["profile_id"])

    if not schema["title"]:
        raise FeatureSchemaError("Feature schema title is required.")

    for group_key in FEATURE_GROUPS.values():
        validate_features(schema[group_key])

    validate_unique_strings(schema["roles"], "roles")
    validate_unique_strings(schema["grades"], "grades")
    validate_unique_strings(schema["skills"], "skills")
    validate_unique_strings(schema["grade_order"], "grade_order")


def validate_features(features: list[dict[str, Any]]) -> None:
    feature_names = []

    for feature in features:
        validate_feature_name(feature["name"])

        if feature["type"] not in ALLOWED_FEATURE_TYPES:
            raise FeatureSchemaError(
                f"Unsupported feature type: {feature['type']}"
            )

        if feature["type"] == "numeric":
            validate_numeric_range(feature)

        feature_names.append(feature["name"])

    validate_unique_strings(feature_names, "feature names")


def validate_numeric_range(feature: dict[str, Any]) -> None:
    min_value = feature.get("min")
    max_value = feature.get("max")

    if not isinstance(min_value, int | float):
        raise FeatureSchemaError("Numeric feature min must be a number.")

    if not isinstance(max_value, int | float):
        raise FeatureSchemaError("Numeric feature max must be a number.")

    if min_value >= max_value:
        raise FeatureSchemaError("Numeric feature min must be less than max.")


def validate_profile_id(profile_id: str) -> None:
    if not PROFILE_ID_PATTERN.match(profile_id):
        raise FeatureSchemaError(
            "Profile id must use lowercase letters, numbers, dash or underscore."
        )


def validate_feature_name(feature_name: str) -> None:
    if not FEATURE_NAME_PATTERN.match(feature_name):
        raise FeatureSchemaError(
            "Feature name must use letters, numbers and underscores."
        )


def validate_unique_strings(values: list[str], label: str) -> None:
    if len(values) != len(set(values)):
        raise FeatureSchemaError(f"Duplicate values found in {label}.")


def normalize_string_list(values: list[Any]) -> list[str]:
    normalized_values = []

    for value in values:
        text_value = str(value).strip()
        if text_value:
            normalized_values.append(text_value)

    return normalized_values


def get_group_key(group: str) -> str:
    group_key = FEATURE_GROUPS.get(group)

    if not group_key:
        raise FeatureSchemaError(f"Unsupported feature group: {group}")

    return group_key


def get_schema_path(profile_id: str) -> Path:
    return FEATURE_SCHEMAS_DIR / f"{profile_id}.json"