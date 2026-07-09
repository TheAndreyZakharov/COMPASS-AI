from __future__ import annotations

import copy
import json
import re
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

SANDBOX_DIR = Path(__file__).resolve().parents[2]
CONFIG_DIR = SANDBOX_DIR / "config"
SETTINGS_PATH = CONFIG_DIR / "app_settings.json"

MODEL_NAMES = {
    "baseline_rule_based",
    "sgd_classifier",
    "logistic_regression",
    "random_forest",
    "hist_gradient_boosting",
    "torch_mlp",
}

DATASET_MODES = {
    "small_preview",
    "medium_validation",
    "large_training",
    "huge_training",
}

TARGET_MODES = {
    "quality",
    "speed",
    "balanced",
    "learning",
    "risk_aware",
}

RECOMMENDATION_MODES = {
    "balanced",
    "best_quality",
    "fastest_delivery",
    "best_learning",
    "risk_aware",
}

PATH_KEYS = {
    "generated_data_dir",
    "imported_data_dir",
    "test_cases_dir",
    "training_sessions_dir",
    "assignment_sessions_dir",
    "reports_dir",
    "exports_dir",
    "logs_dir",
}

ISOLATION_KEYS = {
    "autonomous_subproject",
    "do_not_import_main_src",
    "do_not_import_main_llm",
    "do_not_import_main_agents",
    "do_not_modify_main_compass_api",
    "forbid_main_src_imports",
    "forbid_main_llm_imports",
    "forbid_main_agent_imports",
}

DEFAULT_SETTINGS: dict[str, Any] = {
    "app": {
        "name": "COMPASS AI Sandbox",
        "slug": "compass-ai-sandbox",
        "version": "0.1.0",
        "environment": "local",
        "host": "127.0.0.1",
        "port": 8601,
        "target_python": "3.11.15",
        "python_version": "3.11.15",
    },
    "isolation": {
        "autonomous_subproject": True,
        "do_not_import_main_src": True,
        "do_not_import_main_llm": True,
        "do_not_import_main_agents": True,
        "do_not_modify_main_compass_api": True,
        "forbid_main_src_imports": True,
        "forbid_main_llm_imports": True,
        "forbid_main_agent_imports": True,
    },
    "paths": {
        "generated_data_dir": "sandbox_app/data/generated",
        "imported_data_dir": "sandbox_app/data/imported",
        "test_cases_dir": "sandbox_app/data/test_cases",
        "training_sessions_dir": "sandbox_app/training_sessions",
        "assignment_sessions_dir": "sandbox_app/assignment_sessions",
        "reports_dir": "sandbox_app/reports",
        "exports_dir": "sandbox_app/data/exports",
        "logs_dir": "sandbox_app/logs",
    },
    "defaults": {
        "seed": 27027,
        "domain_profile": "developers",
        "dataset_mode": "small_preview",
        "target_mode": "balanced",
        "recommendation_mode": "balanced",
        "assignment_mode": "balanced",
        "training_models": [
            "baseline_rule_based",
            "logistic_regression",
            "random_forest",
        ],
    },
    "generation": {
        "small_preview": {
            "employees_count": 10,
            "tasks_count": 100,
            "history_depth_per_employee": 5,
            "target_pairs": 1000,
            "candidates_per_task": 10,
        },
        "medium_validation": {
            "employees_count": 30,
            "tasks_count": 1000,
            "history_depth_per_employee": 10,
            "target_pairs": 30000,
            "candidates_per_task": 30,
        },
        "large_training": {
            "employees_count": 100,
            "tasks_count": 10000,
            "history_depth_per_employee": 20,
            "target_pairs": 1000000,
            "candidates_per_task": 100,
        },
    },
    "limits": {
        "huge_generation_requires_confirmation": True,
        "huge_max_employees": 1000,
        "huge_max_tasks": 100000,
        "huge_max_pairs": 10000000,
        "ui_schema_preview_limit": 50,
    },
    "ollama": {
        "base_url": "http://localhost:11434",
        "model": "qwen2.5:1.5b-instruct",
        "timeout_seconds": 30,
        "auto_pull": True,
    },
}

router = APIRouter(prefix="/settings", tags=["settings"])


class SettingsPayload(BaseModel):
    settings: dict[str, Any] = Field(default_factory=dict)


class SettingsPatchPayload(BaseModel):
    section: str
    values: dict[str, Any] = Field(default_factory=dict)


def deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    merged = copy.deepcopy(base)

    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = deep_merge(merged[key], value)
        else:
            merged[key] = value

    return merged


def read_json(path: Path, default: dict[str, Any]) -> dict[str, Any]:
    if not path.exists():
        return copy.deepcopy(default)

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return copy.deepcopy(default)

    if not isinstance(payload, dict):
        return copy.deepcopy(default)

    return payload


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def normalize_settings(payload: dict[str, Any]) -> dict[str, Any]:
    return deep_merge(DEFAULT_SETTINGS, payload)


def validate_relative_path(value: str) -> str:
    if not value or not isinstance(value, str):
        raise ValueError("Path value must be a non-empty string")

    if Path(value).is_absolute():
        raise ValueError("Path must be relative to project root")

    normalized = value.replace("\\", "/").strip()

    if ".." in Path(normalized).parts:
        raise ValueError("Path must not contain parent traversal")

    if not normalized.startswith("sandbox_app/"):
        raise ValueError("Path must stay inside sandbox_app")

    return normalized


def validate_profile_id(value: str) -> str:
    if not re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9_-]{1,63}", value):
        raise ValueError("domain_profile must be 2-64 chars: letters, digits, _ or -")

    return value


def validate_positive_int(value: Any, field_name: str, min_value: int = 1) -> int:
    if isinstance(value, bool):
        raise ValueError(f"{field_name} must be an integer")

    number = int(value)

    if number < min_value:
        raise ValueError(f"{field_name} must be >= {min_value}")

    return number


def validate_bool(value: Any, field_name: str) -> bool:
    if not isinstance(value, bool):
        raise ValueError(f"{field_name} must be boolean")

    return value


def validate_isolation_flags(settings: dict[str, Any]) -> None:
    isolation = settings["isolation"]

    for isolation_key in ISOLATION_KEYS:
        isolation[isolation_key] = validate_bool(
            isolation.get(isolation_key),
            f"isolation.{isolation_key}",
        )

        if not isolation[isolation_key]:
            raise ValueError(f"isolation.{isolation_key} must be true")


def validate_paths(settings: dict[str, Any]) -> None:
    paths = settings["paths"]

    for path_key in PATH_KEYS:
        paths[path_key] = validate_relative_path(str(paths[path_key]))


def validate_defaults(settings: dict[str, Any]) -> None:
    defaults = settings["defaults"]
    defaults["seed"] = validate_positive_int(defaults["seed"], "seed", 1)
    defaults["domain_profile"] = validate_profile_id(str(defaults["domain_profile"]))

    if defaults["dataset_mode"] not in DATASET_MODES:
        raise ValueError("Unsupported dataset_mode")

    if defaults["target_mode"] not in TARGET_MODES:
        raise ValueError("Unsupported target_mode")

    if defaults["recommendation_mode"] not in RECOMMENDATION_MODES:
        raise ValueError("Unsupported recommendation_mode")

    if defaults["assignment_mode"] not in RECOMMENDATION_MODES:
        raise ValueError("Unsupported assignment_mode")

    training_models = defaults.get("training_models", [])
    if not isinstance(training_models, list) or not training_models:
        raise ValueError("training_models must be a non-empty list")

    invalid_models = sorted(set(training_models) - MODEL_NAMES)
    if invalid_models:
        raise ValueError(f"Unsupported training models: {', '.join(invalid_models)}")


def validate_limits(settings: dict[str, Any]) -> None:
    limits = settings["limits"]
    limits["huge_generation_requires_confirmation"] = validate_bool(
        limits["huge_generation_requires_confirmation"],
        "huge_generation_requires_confirmation",
    )
    limits["huge_max_employees"] = validate_positive_int(
        limits["huge_max_employees"],
        "huge_max_employees",
    )
    limits["huge_max_tasks"] = validate_positive_int(
        limits["huge_max_tasks"],
        "huge_max_tasks",
    )
    limits["huge_max_pairs"] = validate_positive_int(
        limits["huge_max_pairs"],
        "huge_max_pairs",
    )
    limits["ui_schema_preview_limit"] = validate_positive_int(
        limits["ui_schema_preview_limit"],
        "ui_schema_preview_limit",
    )


def validate_ollama(settings: dict[str, Any]) -> None:
    ollama = settings["ollama"]
    ollama["base_url"] = str(ollama["base_url"]).strip().rstrip("/")
    ollama["model"] = str(ollama["model"]).strip()
    ollama["timeout_seconds"] = validate_positive_int(
        ollama["timeout_seconds"],
        "timeout_seconds",
    )
    ollama["auto_pull"] = validate_bool(ollama["auto_pull"], "auto_pull")

    if not ollama["base_url"].startswith(("http://", "https://")):
        raise ValueError("Ollama base_url must start with http:// or https://")

    if not ollama["model"]:
        raise ValueError("Ollama model must be non-empty")


def validate_settings(settings: dict[str, Any]) -> dict[str, Any]:
    normalized = normalize_settings(settings)

    validate_isolation_flags(normalized)
    validate_paths(normalized)
    validate_defaults(normalized)
    validate_limits(normalized)
    validate_ollama(normalized)

    return normalized


def load_settings() -> dict[str, Any]:
    payload = read_json(SETTINGS_PATH, DEFAULT_SETTINGS)
    return validate_settings(payload)


def save_settings(settings: dict[str, Any]) -> dict[str, Any]:
    normalized = validate_settings(settings)
    write_json(SETTINGS_PATH, normalized)
    return normalized


@router.get("")
def get_settings() -> dict[str, Any]:
    return {
        "settings": load_settings(),
        "settings_path": str(SETTINGS_PATH),
        "defaults": copy.deepcopy(DEFAULT_SETTINGS),
    }


@router.put("")
def replace_settings(payload: SettingsPayload) -> dict[str, Any]:
    try:
        settings = save_settings(payload.settings)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {
        "settings": settings,
        "settings_path": str(SETTINGS_PATH),
    }


@router.patch("")
def patch_settings(payload: SettingsPatchPayload) -> dict[str, Any]:
    current = load_settings()

    if payload.section not in DEFAULT_SETTINGS:
        raise HTTPException(status_code=400, detail="Unsupported settings section")

    current[payload.section] = deep_merge(
        current.get(payload.section, {}),
        payload.values,
    )

    try:
        settings = save_settings(current)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {
        "settings": settings,
        "settings_path": str(SETTINGS_PATH),
    }


@router.post("/reset")
def reset_settings() -> dict[str, Any]:
    settings = save_settings(copy.deepcopy(DEFAULT_SETTINGS))

    return {
        "settings": settings,
        "settings_path": str(SETTINGS_PATH),
        "reset": True,
    }


@router.get("/schema")
def get_settings_schema() -> dict[str, Any]:
    return {
        "dataset_modes": sorted(DATASET_MODES),
        "target_modes": sorted(TARGET_MODES),
        "recommendation_modes": sorted(RECOMMENDATION_MODES),
        "training_models": sorted(MODEL_NAMES),
        "path_keys": sorted(PATH_KEYS),
        "isolation_keys": sorted(ISOLATION_KEYS),
        "sections": sorted(DEFAULT_SETTINGS),
    }