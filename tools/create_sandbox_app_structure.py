# ruff: noqa: E501
import json
from pathlib import Path

ROOT = Path.cwd()
SANDBOX = ROOT / "sandbox_app"

DIRS = [
    "backend/api",
    "backend/core",
    "backend/data_generation",
    "backend/features",
    "backend/training",
    "backend/inference",
    "backend/reports",
    "backend/llm",
    "backend/utils",
    "config/data_contracts",
    "config/feature_schemas",
    "scripts",
    "frontend/css",
    "frontend/js",
    "frontend/assets",
    "data/generated",
    "data/imported",
    "data/test_cases",
    "data/exports",
    "training_sessions",
    "assignment_sessions",
    "reports",
    "logs",
    "tests",
]

PACKAGE_DIRS = [
    "backend",
    "backend/api",
    "backend/core",
    "backend/data_generation",
    "backend/features",
    "backend/training",
    "backend/inference",
    "backend/reports",
    "backend/llm",
    "backend/utils",
    "tests",
]

GITKEEP_DIRS = [
    "config/data_contracts",
    "frontend/assets",
    "data/generated",
    "data/imported",
    "data/test_cases",
    "data/exports",
    "training_sessions",
    "assignment_sessions",
    "reports",
    "logs",
]

SCRIPT_FILES = [
    "scripts/start.sh",
    "scripts/stop.sh",
    "scripts/restart.sh",
    "scripts/smoke_test.sh",
    "scripts/clean_tmp.sh",
]

README = """# COMPASS AI Sandbox

Autonomous local sandbox for COMPASS-AI experiments.

## Purpose

The sandbox lives entirely inside sandbox_app and is isolated from the main COMPASS API, src modules, main LLM modules, and agent modules.

It is designed for the full local experiment cycle:

- configurable domain feature schemas
- synthetic team and backlog generation
- assignment history generation
- large training dataset generation
- data viewing in a browser
- multi-model training
- training sessions and model artifacts
- recommendations and bulk assignment simulation
- reports, exports, and Russian Qwen/Ollama explanations

## Runtime

Target Python version: 3.11.x.

Expected project environment:

source .venv/bin/activate

The sandbox has its own requirements.txt but uses the existing project .venv.

## Structure

backend contains sandbox-only backend code.
frontend contains browser UI files.
config contains sandbox settings, model presets, data contracts, and feature schemas.
data contains generated, imported, test case, and export data.
training_sessions stores reproducible training runs.
assignment_sessions stores bulk assignment runs.
reports stores generated reports.
logs stores runtime logs and pid files.
tests contains sandbox tests.

## Roadmap

27.1 creates the autonomous structure and validated JSON/Python foundations.
27.2 adds local run, stop, restart, smoke test, and Makefile commands.
27.3 adds the FastAPI backend foundation.
"""

REQUIREMENTS = """fastapi>=0.115.0
uvicorn[standard]>=0.30.0
pydantic>=2.8.0
pydantic-settings>=2.4.0
python-multipart>=0.0.9
httpx>=0.27.0
numpy>=1.26.0
pandas>=2.2.0
pyarrow>=16.0.0
scikit-learn>=1.5.0
joblib>=1.4.0
matplotlib>=3.9.0
pytest>=8.2.0
"""

APP_SETTINGS = {
    "app": {
        "name": "COMPASS AI Sandbox",
        "slug": "compass-ai-sandbox",
        "version": "0.1.0",
        "environment": "local",
        "target_python": "3.11.x",
        "host": "127.0.0.1",
        "port": 8601
    },
    "isolation": {
        "autonomous_subproject": True,
        "do_not_import_main_src": True,
        "do_not_import_main_llm": True,
        "do_not_import_main_agents": True,
        "do_not_modify_main_compass_api": True
    },
    "paths": {
        "config_dir": "sandbox_app/config",
        "feature_schemas_dir": "sandbox_app/config/feature_schemas",
        "data_contracts_dir": "sandbox_app/config/data_contracts",
        "generated_data_dir": "sandbox_app/data/generated",
        "imported_data_dir": "sandbox_app/data/imported",
        "test_cases_dir": "sandbox_app/data/test_cases",
        "exports_dir": "sandbox_app/data/exports",
        "training_sessions_dir": "sandbox_app/training_sessions",
        "assignment_sessions_dir": "sandbox_app/assignment_sessions",
        "reports_dir": "sandbox_app/reports",
        "logs_dir": "sandbox_app/logs"
    },
    "defaults": {
        "seed": 42,
        "domain_profile": "developers",
        "dataset_mode": "small_preview",
        "recommendation_mode": "balanced",
        "training_models": [
            "baseline_rule_based",
            "sgd_classifier",
            "logistic_regression"
        ]
    },
    "dataset_modes": {
        "small_preview": {
            "employees_count": 10,
            "tasks_count": 100,
            "target_pairs": 1000,
            "history_depth_per_employee": 25
        },
        "medium_validation": {
            "employees_count": 30,
            "tasks_count": 1000,
            "target_pairs": 30000,
            "history_depth_per_employee": 100
        },
        "large_training": {
            "employees_count": 100,
            "tasks_count": 10000,
            "target_pairs": 1000000,
            "history_depth_per_employee": 250
        },
        "huge_training": {
            "requires_confirmation": True,
            "max_employees_count": 1000,
            "max_tasks_count": 100000,
            "max_target_pairs": 10000000
        }
    },
    "ollama": {
        "base_url": "http://localhost:11434",
        "model": "qwen2.5:1.5b-instruct",
        "timeout_seconds": 30,
        "explanations_only": True,
        "can_change_ranking": False
    }
}

MODEL_PRESETS = {
    "models": {
        "baseline_rule_based": {
            "enabled": True,
            "type": "rules",
            "description": "Deterministic baseline for comparison."
        },
        "sgd_classifier": {
            "enabled": True,
            "type": "sklearn",
            "default_params": {
                "loss": "log_loss",
                "penalty": "l2",
                "max_iter": 1000,
                "random_state": 42
            }
        },
        "logistic_regression": {
            "enabled": True,
            "type": "sklearn",
            "default_params": {
                "max_iter": 1000,
                "class_weight": "balanced",
                "random_state": 42
            }
        },
        "random_forest": {
            "enabled": True,
            "type": "sklearn",
            "default_params": {
                "n_estimators": 300,
                "max_depth": None,
                "n_jobs": -1,
                "random_state": 42
            }
        },
        "hist_gradient_boosting": {
            "enabled": True,
            "type": "sklearn",
            "default_params": {
                "max_iter": 300,
                "learning_rate": 0.08,
                "random_state": 42
            }
        },
        "torch_mlp": {
            "enabled": True,
            "type": "pytorch",
            "default_params": {
                "hidden_layers": [256, 128],
                "dropout": 0.15,
                "epochs": 20,
                "batch_size": 512,
                "learning_rate": 0.001,
                "seed": 42
            }
        }
    },
    "target_modes": [
        "quality",
        "speed",
        "balanced",
        "learning",
        "risk_aware"
    ],
    "metrics": [
        "roc_auc",
        "f1",
        "precision",
        "recall",
        "accuracy",
        "log_loss",
        "mae_for_score",
        "top_1_accuracy",
        "top_3_accuracy"
    ]
}

def feature_schema(profile_id, name, system, roles, grades, skills, task_types):
    return {
        "profile_id": profile_id,
        "name": name,
        "system": system,
        "version": "1.0.0",
        "description": f"{name} domain profile for COMPASS AI Sandbox.",
        "roles": roles,
        "grades": grades,
        "skills": skills,
        "task_types": task_types,
        "feature_groups": {
            "employee": [
                {"name": "availability_score", "type": "numeric", "required": True, "min": 0, "max": 1},
                {"name": "current_workload", "type": "numeric", "required": True, "min": 0, "max": 1},
                {"name": "fatigue_score", "type": "numeric", "required": True, "min": 0, "max": 1},
                {"name": "avg_completion_speed", "type": "numeric", "required": True, "min": 0, "max": 1},
                {"name": "avg_quality_score", "type": "numeric", "required": True, "min": 0, "max": 1},
                {"name": "deadline_reliability", "type": "numeric", "required": True, "min": 0, "max": 1},
                {"name": "mentor_level", "type": "numeric", "required": True, "min": 0, "max": 1},
                {"name": "learning_goals", "type": "skill_list", "required": False}
            ],
            "task": [
                {"name": "priority", "type": "categorical", "required": True, "values": ["low", "medium", "high", "critical"]},
                {"name": "complexity", "type": "numeric", "required": True, "min": 1, "max": 10},
                {"name": "estimated_hours", "type": "numeric", "required": True, "min": 0.5, "max": 240},
                {"name": "deadline_days", "type": "numeric", "required": True, "min": 0, "max": 365},
                {"name": "required_skills", "type": "skill_list", "required": True},
                {"name": "requires_mentor", "type": "boolean", "required": False}
            ],
            "outcome": [
                {"name": "planned_hours", "type": "numeric", "required": True, "min": 0.5, "max": 240},
                {"name": "actual_hours", "type": "numeric", "required": True, "min": 0.5, "max": 400},
                {"name": "quality_score", "type": "numeric", "required": True, "min": 0, "max": 1},
                {"name": "deadline_status", "type": "categorical", "required": True, "values": ["early", "on_time", "late", "missed"]},
                {"name": "outcome_label", "type": "categorical", "required": True, "values": ["success", "good", "acceptable", "late", "failed", "rework"]},
                {"name": "was_rework_needed", "type": "boolean", "required": True},
                {"name": "feedback_score", "type": "numeric", "required": False, "min": 0, "max": 1}
            ]
        }
    }

DEVELOPERS_SCHEMA = feature_schema(
    "developers",
    "Developers",
    True,
    ["backend_engineer", "frontend_engineer", "fullstack_engineer", "qa_engineer", "devops_engineer", "ml_engineer", "tech_lead"],
    ["junior", "middle", "senior", "lead"],
    ["python", "fastapi", "sql", "postgresql", "javascript", "typescript", "react", "testing", "docker", "ci_cd", "ml", "data_processing", "api_design", "debugging"],
    ["feature", "bugfix", "refactor", "test", "infra", "research", "documentation", "review"]
)

DESIGNERS_SCHEMA = feature_schema(
    "designers",
    "Designers",
    True,
    ["product_designer", "ux_designer", "ui_designer", "researcher", "design_lead", "brand_designer"],
    ["junior", "middle", "senior", "lead"],
    ["figma", "ux_research", "wireframing", "prototyping", "design_systems", "accessibility", "visual_design", "interaction_design", "user_testing", "handoff"],
    ["research", "wireframe", "prototype", "ui_design", "design_system", "usability_test", "handoff", "review"]
)

CUSTOM_SCHEMA = feature_schema(
    "custom",
    "Custom",
    False,
    ["specialist", "operator", "analyst", "manager", "lead"],
    ["junior", "middle", "senior", "lead"],
    ["domain_knowledge", "communication", "analysis", "execution", "quality_control", "planning"],
    ["task", "review", "analysis", "support", "research", "delivery"]
)

MAIN_PY = '''"""Sandbox backend entry module.

FastAPI application wiring is implemented in roadmap item 27.3.
This file exists now so package imports and compile checks are stable from 27.1.
"""

SANDBOX_APP_NAME = "COMPASS AI Sandbox"
SANDBOX_TARGET_PYTHON = "3.11.x"
SANDBOX_API_HOST = "127.0.0.1"
SANDBOX_API_PORT = 8601
'''

INIT_PY = '''"""COMPASS AI Sandbox package."""
'''

def write_text(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")

def write_json(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def main():
    SANDBOX.mkdir(exist_ok=True)

    for directory in DIRS:
        (SANDBOX / directory).mkdir(parents=True, exist_ok=True)

    for directory in PACKAGE_DIRS:
        write_text(SANDBOX / directory / "__init__.py", INIT_PY)

    for directory in GITKEEP_DIRS:
        write_text(SANDBOX / directory / ".gitkeep", "")

    for script in SCRIPT_FILES:
        write_text(SANDBOX / script, "")

    write_text(SANDBOX / ".python-version", "3.11.15\n")
    write_text(SANDBOX / "README.md", README)
    write_text(SANDBOX / "requirements.txt", REQUIREMENTS)
    write_text(SANDBOX / "backend/main.py", MAIN_PY)

    write_json(SANDBOX / "config/app_settings.json", APP_SETTINGS)
    write_json(SANDBOX / "config/model_presets.json", MODEL_PRESETS)
    write_json(SANDBOX / "config/feature_schemas/developers.json", DEVELOPERS_SCHEMA)
    write_json(SANDBOX / "config/feature_schemas/designers.json", DESIGNERS_SCHEMA)
    write_json(SANDBOX / "config/feature_schemas/custom.json", CUSTOM_SCHEMA)

    for json_path in [
        SANDBOX / "config/app_settings.json",
        SANDBOX / "config/model_presets.json",
        SANDBOX / "config/feature_schemas/developers.json",
        SANDBOX / "config/feature_schemas/designers.json",
        SANDBOX / "config/feature_schemas/custom.json",
    ]:
        json.loads(json_path.read_text(encoding="utf-8"))

    print("sandbox_app structure created")
    print("JSON configs validated")

if __name__ == "__main__":
    main()