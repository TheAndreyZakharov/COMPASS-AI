from __future__ import annotations

import copy
import re
from pathlib import Path
from typing import Any

from sandbox_app.backend.core.paths import PATHS
from sandbox_app.backend.core.time import moscow_now_iso
from sandbox_app.backend.utils.json_io import read_json, write_json

PROFILE_ID_RE = re.compile(r"^[a-z][a-z0-9_-]{1,63}$")
FEATURE_NAME_RE = re.compile(r"^[a-z][a-z0-9_]{1,63}$")

ALLOWED_FEATURE_GROUPS = {"employee", "task", "outcome"}
ALLOWED_FEATURE_TYPES = {"numeric", "categorical", "boolean", "text", "skill_list"}
SYSTEM_PROFILE_IDS = {"developers", "designers"}


class FeatureSchemaError(RuntimeError):
    """Raised when a sandbox feature schema is invalid or cannot be modified."""


def utc_now_iso() -> str:
    return moscow_now_iso()


def validate_profile_id(profile_id: str) -> str:
    if not isinstance(profile_id, str) or not PROFILE_ID_RE.match(profile_id):
        raise FeatureSchemaError(
            "profile_id must start with a lowercase letter and contain only "
            "lowercase letters, digits, underscores, or hyphens"
        )
    return profile_id


def validate_feature_name(feature_name: str) -> str:
    if not isinstance(feature_name, str) or not FEATURE_NAME_RE.match(feature_name):
        raise FeatureSchemaError(
            "feature name must start with a lowercase letter and contain only "
            "lowercase letters, digits, or underscores"
        )
    return feature_name


def validate_feature_group(group: str) -> str:
    if group not in ALLOWED_FEATURE_GROUPS:
        allowed = ", ".join(sorted(ALLOWED_FEATURE_GROUPS))
        raise FeatureSchemaError(
            f"Unknown feature group '{group}'. Allowed groups: {allowed}"
        )
    return group


def validate_feature_type(feature_type: str) -> str:
    if feature_type not in ALLOWED_FEATURE_TYPES:
        allowed = ", ".join(sorted(ALLOWED_FEATURE_TYPES))
        raise FeatureSchemaError(
            f"Unknown feature type '{feature_type}'. Allowed types: {allowed}"
        )
    return feature_type


def schema_path(profile_id: str) -> Path:
    validate_profile_id(profile_id)
    return PATHS.feature_schemas_dir / f"{profile_id}.json"


def list_feature_schema_paths() -> list[Path]:
    PATHS.feature_schemas_dir.mkdir(parents=True, exist_ok=True)
    return sorted(PATHS.feature_schemas_dir.glob("*.json"))


def load_feature_schema(profile_id: str) -> dict[str, Any]:
    path = schema_path(profile_id)
    if not path.exists():
        raise FeatureSchemaError(f"Feature schema '{profile_id}' not found")
    return validate_schema(read_json(path))


def load_all_feature_schemas() -> list[dict[str, Any]]:
    schemas = [validate_schema(read_json(path)) for path in list_feature_schema_paths()]
    return sorted(schemas, key=lambda item: item["profile_id"])


def save_feature_schema(schema: dict[str, Any]) -> dict[str, Any]:
    validated = validate_schema(schema)
    write_json(schema_path(validated["profile_id"]), validated)
    return validated


def delete_feature_schema(profile_id: str) -> None:
    schema = load_feature_schema(profile_id)

    if schema.get("system") is True or profile_id in SYSTEM_PROFILE_IDS:
        raise FeatureSchemaError(f"System feature schema '{profile_id}' cannot be deleted")

    path = schema_path(profile_id)
    path.unlink(missing_ok=False)


def create_feature_schema(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise FeatureSchemaError("Feature schema payload must be an object")

    profile_id = validate_profile_id(str(payload.get("profile_id", "")))
    path = schema_path(profile_id)

    if path.exists():
        raise FeatureSchemaError(f"Feature schema '{profile_id}' already exists")

    schema = normalize_schema(payload, is_new=True)
    schema["system"] = bool(schema.get("system", False))
    schema["created_at"] = utc_now_iso()
    schema["updated_at"] = schema["created_at"]

    return save_feature_schema(schema)


def update_feature_schema(profile_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    current = load_feature_schema(profile_id)

    if not isinstance(payload, dict):
        raise FeatureSchemaError("Feature schema payload must be an object")

    updated = copy.deepcopy(current)
    for key, value in payload.items():
        if key in {"profile_id", "system", "created_at"}:
            continue
        updated[key] = value

    updated["profile_id"] = profile_id
    updated["system"] = bool(current.get("system", False))
    updated["created_at"] = current.get("created_at", utc_now_iso())
    updated["updated_at"] = utc_now_iso()

    return save_feature_schema(normalize_schema(updated, is_new=False))


def add_feature(profile_id: str, group: str, feature_payload: dict[str, Any]) -> dict[str, Any]:
    group = validate_feature_group(group)
    schema = load_feature_schema(profile_id)
    feature = validate_feature(feature_payload)

    features = schema["feature_groups"][group]
    if any(item["name"] == feature["name"] for item in features):
        raise FeatureSchemaError(
            f"Feature '{feature['name']}' already exists in group '{group}'"
            f" for profile '{profile_id}'"
        )

    features.append(feature)
    schema["updated_at"] = utc_now_iso()

    return save_feature_schema(schema)


def patch_feature(
    profile_id: str,
    group: str,
    feature_name: str,
    patch_payload: dict[str, Any],
) -> dict[str, Any]:
    group = validate_feature_group(group)
    feature_name = validate_feature_name(feature_name)

    if not isinstance(patch_payload, dict):
        raise FeatureSchemaError("Feature patch payload must be an object")

    schema = load_feature_schema(profile_id)
    features = schema["feature_groups"][group]

    index = next((idx for idx, item in enumerate(features) if item["name"] == feature_name), None)
    if index is None:
        raise FeatureSchemaError(
            f"Feature '{feature_name}' not found in group '{group}' for profile '{profile_id}'"
        )

    patched = copy.deepcopy(features[index])

    if "new_name" in patch_payload:
        new_name = validate_feature_name(str(patch_payload["new_name"]))
        if new_name != feature_name and any(item["name"] == new_name for item in features):
            raise FeatureSchemaError(
                f"Feature '{new_name}' already exists in group '{group}' for profile '{profile_id}'"
            )
        patched["name"] = new_name

    for key, value in patch_payload.items():
        if key == "new_name":
            continue
        patched[key] = value

    features[index] = validate_feature(patched)
    schema["updated_at"] = utc_now_iso()

    return save_feature_schema(schema)


def delete_feature(profile_id: str, group: str, feature_name: str) -> dict[str, Any]:
    group = validate_feature_group(group)
    feature_name = validate_feature_name(feature_name)

    schema = load_feature_schema(profile_id)
    features = schema["feature_groups"][group]

    next_features = [item for item in features if item["name"] != feature_name]
    if len(next_features) == len(features):
        raise FeatureSchemaError(
            f"Feature '{feature_name}' not found in group '{group}' for profile '{profile_id}'"
        )

    schema["feature_groups"][group] = next_features
    schema["updated_at"] = utc_now_iso()

    return save_feature_schema(schema)


def normalize_schema(payload: dict[str, Any], is_new: bool) -> dict[str, Any]:
    profile_id = validate_profile_id(str(payload.get("profile_id", "")))

    schema = {
        "profile_id": profile_id,
        "name": str(payload.get("name") or profile_id.replace("_", " ").replace("-", " ").title()),
        "system": bool(payload.get("system", False)),
        "version": str(payload.get("version", "1.0.0")),
        "description": str(payload.get("description", "")),
        "domain_examples": list(payload.get("domain_examples", [])),
        "roles": list(payload.get("roles", [])),
        "grades": list(payload.get("grades", [])),
        "skills": list(payload.get("skills", [])),
        "task_types": list(payload.get("task_types", [])),
        "feature_groups": payload.get("feature_groups", {}),
    }

    if not schema["description"]:
        schema["description"] = f"{schema['name']} domain profile for COMPASS AI Sandbox."

    if not schema["roles"]:
        schema["roles"] = ["specialist", "manager", "lead"]

    if not schema["grades"]:
        schema["grades"] = ["junior", "middle", "senior", "lead"]

    if not schema["skills"]:
        schema["skills"] = ["domain_knowledge", "communication", "planning", "quality_control"]

    if not schema["task_types"]:
        schema["task_types"] = ["task", "analysis", "review", "delivery"]

    feature_groups = schema["feature_groups"]
    if not isinstance(feature_groups, dict):
        raise FeatureSchemaError("feature_groups must be an object")

    normalized_groups: dict[str, list[dict[str, Any]]] = {}
    for group in sorted(ALLOWED_FEATURE_GROUPS):
        raw_features = feature_groups.get(group, [])
        if not isinstance(raw_features, list):
            raise FeatureSchemaError(f"feature_groups.{group} must be a list")
        normalized_groups[group] = [validate_feature(item) for item in raw_features]

    schema["feature_groups"] = normalized_groups

    if is_new:
        schema["created_at"] = str(payload.get("created_at", utc_now_iso()))
    elif "created_at" in payload:
        schema["created_at"] = str(payload["created_at"])

    if "updated_at" in payload:
        schema["updated_at"] = str(payload["updated_at"])

    return schema


def validate_schema(schema: dict[str, Any]) -> dict[str, Any]:
    normalized = normalize_schema(schema, is_new=False)

    if normalized["profile_id"] in SYSTEM_PROFILE_IDS and normalized["system"] is not True:
        raise FeatureSchemaError(
            f"System profile '{normalized['profile_id']}' must have system=true"
        )

    if normalized["system"] is True and normalized["profile_id"] not in SYSTEM_PROFILE_IDS:
        builtins = ", ".join(sorted(SYSTEM_PROFILE_IDS))
        raise FeatureSchemaError(
            f"Only built-in profiles can have system=true. Built-ins: {builtins}"
        )

    for list_key in ("roles", "grades", "skills", "task_types", "domain_examples"):
        values = normalized.get(list_key)
        if not isinstance(values, list):
            raise FeatureSchemaError(f"{list_key} must be a list")
        for value in values:
            if not isinstance(value, str) or not value.strip():
                raise FeatureSchemaError(f"{list_key} must contain non-empty strings")

    return normalized


def validate_feature(feature: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(feature, dict):
        raise FeatureSchemaError("Feature must be an object")

    name = validate_feature_name(str(feature.get("name", "")))
    feature_type = validate_feature_type(str(feature.get("type", "")))

    normalized = copy.deepcopy(feature)
    normalized["name"] = name
    normalized["type"] = feature_type
    normalized["required"] = bool(feature.get("required", False))

    if feature_type == "numeric":
        minimum = normalized.get("min", normalized.get("minimum"))
        maximum = normalized.get("max", normalized.get("maximum"))

        if minimum is not None and not isinstance(minimum, (int, float)):
            raise FeatureSchemaError(f"Numeric feature '{name}' min must be a number")

        if maximum is not None and not isinstance(maximum, (int, float)):
            raise FeatureSchemaError(f"Numeric feature '{name}' max must be a number")

        if minimum is not None and maximum is not None and minimum > maximum:
            raise FeatureSchemaError(f"Numeric feature '{name}' min cannot be greater than max")

        if minimum is not None:
            normalized["min"] = minimum
            normalized.pop("minimum", None)

        if maximum is not None:
            normalized["max"] = maximum
            normalized.pop("maximum", None)

    if feature_type == "categorical":
        values = normalized.get("values")
        if not isinstance(values, list) or not values:
            raise FeatureSchemaError(
                f"Categorical feature '{name}' must define non-empty values list"
            )
        for value in values:
            if not isinstance(value, str) or not value.strip():
                raise FeatureSchemaError(
                    f"Categorical feature '{name}' values must be non-empty strings"
                )

    if feature_type in {"boolean", "text", "skill_list"}:
        normalized.pop("values", None)

    return normalized


def schema_preview(schema: dict[str, Any]) -> dict[str, Any]:
    validated = validate_schema(schema)
    groups = validated["feature_groups"]

    return {
        "profile_id": validated["profile_id"],
        "name": validated["name"],
        "system": validated["system"],
        "version": validated["version"],
        "roles_count": len(validated["roles"]),
        "grades_count": len(validated["grades"]),
        "skills_count": len(validated["skills"]),
        "task_types_count": len(validated["task_types"]),
        "feature_counts": {
            group: len(features)
            for group, features in groups.items()
        },
        "feature_names": {
            group: [feature["name"] for feature in features]
            for group, features in groups.items()
        },
        "supported_feature_types": sorted(ALLOWED_FEATURE_TYPES),
        "editable": validated["system"] is not True,
    }


def list_schema_previews() -> list[dict[str, Any]]:
    return [schema_preview(schema) for schema in load_all_feature_schemas()]


def build_profile_template(profile_id: str, name: str | None = None) -> dict[str, Any]:
    profile_id = validate_profile_id(profile_id)

    return {
        "profile_id": profile_id,
        "name": name or profile_id.replace("_", " ").replace("-", " ").title(),
        "system": False,
        "version": "1.0.0",
        "description": f"{name or profile_id} custom domain profile for COMPASS AI Sandbox.",
        "domain_examples": [
            "medicine",
            "law",
            "sales",
            "design",
            "development",
            "education",
            "operations"
        ],
        "roles": [
            "specialist",
            "operator",
            "analyst",
            "manager",
            "lead"
        ],
        "grades": [
            "junior",
            "middle",
            "senior",
            "lead"
        ],
        "skills": [
            "domain_knowledge",
            "communication",
            "analysis",
            "execution",
            "quality_control",
            "planning"
        ],
        "task_types": [
            "task",
            "review",
            "analysis",
            "support",
            "research",
            "delivery"
        ],
        "feature_groups": {
            "employee": [
                {
                    "name": "availability_score",
                    "type": "numeric",
                    "required": True,
                    "min": 0,
                    "max": 1
                }
            ],
            "task": [
                {
                    "name": "priority",
                    "type": "categorical",
                    "required": True,
                    "values": [
                        "low",
                        "medium",
                        "high",
                        "critical"
                    ]
                }
            ],
            "outcome": [
                {
                    "name": "outcome_label",
                    "type": "categorical",
                    "required": True,
                    "values": [
                        "success",
                        "good",
                        "acceptable",
                        "late",
                        "failed",
                        "rework"
                    ]
                }
            ]
        },
        "created_at": utc_now_iso(),
        "updated_at": utc_now_iso()
    }
