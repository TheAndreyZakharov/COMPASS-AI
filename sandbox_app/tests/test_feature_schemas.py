from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCHEMAS_DIR = ROOT / "config" / "feature_schemas"

REQUIRED_CONFIG_FILES = {
    "developers.json",
    "designers.json",
    "custom.json",
}

REQUIRED_SYSTEM_PROFILES = {
    "developers",
    "designers",
}

ALLOWED_FEATURE_TYPES = {
    "numeric",
    "categorical",
    "boolean",
    "text",
    "skill_list",
}

REQUIRED_SCHEMA_LOADER_FRAGMENTS = {
    "load_all_feature_schemas",
    "load_feature_schema",
    "create_feature_schema",
    "update_feature_schema",
    "delete_feature_schema",
    "add_feature",
    "patch_feature",
    "delete_feature",
    "schema_preview",
    "build_profile_template",
}

REQUIRED_API_ROUTE_FRAGMENTS = {
    "@router.get",
    "@router.post",
    "@router.put",
    "@router.patch",
    "@router.delete",
    "load_all_feature_schemas",
    "load_feature_schema",
    "create_feature_schema",
    "update_feature_schema",
    "delete_feature_schema",
    "add_feature",
    "patch_feature",
    "delete_feature",
    "schema_preview",
    "build_profile_template",
}

FEATURE_GROUP_ALIASES = {
    "employee": ("employee_features", "employees", "employee"),
    "task": ("task_features", "tasks", "task"),
    "outcome": ("outcome_features", "outcomes", "outcome"),
}


def read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))

    assert isinstance(payload, dict)

    return payload


def schema_feature_group(schema: dict[str, Any], group_name: str) -> list[dict[str, Any]]:
    feature_groups = schema.get("feature_groups")
    if isinstance(feature_groups, dict):
        value = feature_groups.get(group_name)

        if isinstance(value, list):
            return value

    for key in FEATURE_GROUP_ALIASES[group_name]:
        value = schema.get(key)

        if isinstance(value, list):
            return value

    nested_features = schema.get("features")
    if isinstance(nested_features, dict):
        for key in FEATURE_GROUP_ALIASES[group_name]:
            value = nested_features.get(key)

            if isinstance(value, list):
                return value

    return []


def all_schema_features(schema: dict[str, Any]) -> list[dict[str, Any]]:
    features: list[dict[str, Any]] = []

    for group_name in FEATURE_GROUP_ALIASES:
        features.extend(schema_feature_group(schema, group_name))

    return features


def test_feature_schema_config_files_exist_and_are_valid_json() -> None:
    existing_files = {path.name for path in SCHEMAS_DIR.glob("*.json")}

    assert existing_files >= REQUIRED_CONFIG_FILES

    for file_name in REQUIRED_CONFIG_FILES:
        payload = read_json(SCHEMAS_DIR / file_name)

        assert payload["profile_id"]
        assert payload["name"]
        assert isinstance(payload.get("roles", []), list)
        assert isinstance(payload.get("grades", []), list)
        assert isinstance(payload.get("skills", []), list)


def test_feature_schema_feature_definitions_are_valid_when_present() -> None:
    for schema_path in SCHEMAS_DIR.glob("*.json"):
        payload = read_json(schema_path)
        features = all_schema_features(payload)

        feature_names: set[str] = set()

        for feature in features:
            assert isinstance(feature, dict)
            assert feature["name"]
            assert feature["type"] in ALLOWED_FEATURE_TYPES
            assert feature["name"] not in feature_names

            feature_names.add(feature["name"])


def test_system_feature_schemas_are_marked_as_system_profiles() -> None:
    for profile_id in REQUIRED_SYSTEM_PROFILES:
        schema = read_json(SCHEMAS_DIR / f"{profile_id}.json")

        assert schema["profile_id"] == profile_id
        assert schema["system"] is True


def test_custom_feature_schema_is_editable() -> None:
    custom_schema = read_json(SCHEMAS_DIR / "custom.json")

    assert custom_schema["profile_id"] == "custom"
    assert custom_schema["system"] is False


def test_feature_schema_loader_supports_full_crud_contract() -> None:
    schema_loader = (ROOT / "backend" / "features" / "schema.py").read_text(
        encoding="utf-8",
    )

    for fragment in REQUIRED_SCHEMA_LOADER_FRAGMENTS:
        assert fragment in schema_loader


def test_feature_schema_api_supports_full_crud_routes() -> None:
    feature_schemas_api = (ROOT / "backend" / "api" / "feature_schemas.py").read_text(
        encoding="utf-8",
    )

    for fragment in REQUIRED_API_ROUTE_FRAGMENTS:
        assert fragment in feature_schemas_api