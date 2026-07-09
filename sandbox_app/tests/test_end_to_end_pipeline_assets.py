from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


REQUIRED_TEST_FILES = {
    "feature schemas": "tests/test_feature_schemas.py",
    "team generator": "tests/test_test_team_generator.py",
    "task generator": "tests/test_task_generator.py",
    "history generator": "tests/test_history_generator.py",
    "full dataset generator": "tests/test_full_dataset_generator.py",
    "data viewer api": "tests/test_data_viewer_api.py",
    "import validation": "tests/test_importers.py",
    "feature builder": "tests/test_feature_builder.py",
    "training smoke": "tests/test_training_session.py",
    "training sessions": "tests/test_training_session_artifacts.py",
    "model loading": "tests/test_model_export.py",
    "single recommendation": "tests/test_single_recommendation.py",
    "bulk assignment": "tests/test_bulk_assignment.py",
    "qwen fallback": "tests/test_qwen_explainer.py",
    "backend startup": "tests/test_settings_assets.py",
    "reports exports": "tests/test_reports_exports_assets.py",
    "frontend bootstrap": "tests/test_frontend_bootstrap_assets.py",
}


REQUIRED_FRONTEND_PAGES = {
    "dashboard": "frontend/js/pages/dashboard.js",
    "generator": "frontend/js/pages/generator.js",
    "viewer": "frontend/js/pages/viewer.js",
    "import data": "frontend/js/pages/import_data.js",
    "training": "frontend/js/pages/training.js",
    "models": "frontend/js/pages/models.js",
    "assignment lab": "frontend/js/pages/assignment_lab.js",
    "reports": "frontend/js/pages/reports.js",
    "settings": "frontend/js/pages/settings.js",
}


REQUIRED_API_FILES = {
    "feature schemas": "backend/api/feature_schemas.py",
    "team generator": "backend/api/generate_team.py",
    "task generator": "backend/api/generate_tasks.py",
    "history generator": "backend/api/generate_history.py",
    "full dataset": "backend/api/generate_dataset.py",
    "data viewer": "backend/api/data_viewer.py",
    "import data": "backend/api/import_data.py",
    "features": "backend/api/features.py",
    "training": "backend/api/training.py",
    "models": "backend/api/models.py",
    "test cases": "backend/api/test_cases.py",
    "recommendations": "backend/api/recommendations.py",
    "assignment sessions": "backend/api/assignment_sessions.py",
    "llm": "backend/api/llm.py",
    "reports": "backend/api/reports.py",
    "settings": "backend/api/settings.py",
}


PIPELINE_STEPS = (
    "create custom schema",
    "generate full dataset",
    "open data viewer",
    "build features",
    "train models",
    "save training session",
    "open model session",
    "generate test team",
    "run single recommendation",
    "run bulk assignment",
    "enable qwen explanations",
    "save assignment session",
    "open reports",
    "export results",
)


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def assert_existing_file(relative_path: str) -> None:
    path = ROOT / relative_path

    assert path.exists(), f"Missing required file: {relative_path}"
    assert path.is_file(), f"Required path is not a file: {relative_path}"
    assert path.read_text(encoding="utf-8").strip(), f"Empty file: {relative_path}"


def test_pipeline_test_coverage_files_exist() -> None:
    missing = [
        f"{name}: {relative_path}"
        for name, relative_path in REQUIRED_TEST_FILES.items()
        if not (ROOT / relative_path).is_file()
    ]

    assert not missing, "Missing pipeline test coverage:\n" + "\n".join(missing)


def test_pipeline_backend_api_files_exist() -> None:
    for relative_path in REQUIRED_API_FILES.values():
        assert_existing_file(relative_path)


def test_pipeline_frontend_pages_exist() -> None:
    for relative_path in REQUIRED_FRONTEND_PAGES.values():
        assert_existing_file(relative_path)


def test_pipeline_routes_are_registered() -> None:
    main_py = read("backend/main.py")

    expected_routers = (
        "feature_schemas.router",
        "generate_team.router",
        "generate_tasks.router",
        "generate_history.router",
        "generate_dataset.router",
        "data_viewer.router",
        "import_data.router",
        "features.router",
        "training.router",
        "models.router",
        "test_cases.router",
        "recommendations.router",
        "assignment_sessions.router",
        "llm.router",
        "reports.router",
        "settings.router",
    )

    for router_name in expected_routers:
        assert router_name in main_py


def test_frontend_api_client_covers_full_pipeline() -> None:
    api_js = read("frontend/js/api.js")

    expected_methods = (
        "featureSchemas",
        "createFeatureSchema",
        "updateFeatureSchema",
        "generateDataset",
        "datasets",
        "datasetSummary",
        "datasetTable",
        "buildFeatures",
        "featureMetadata",
        "runTraining",
        "trainingSessions",
        "trainingSession",
        "modelsList",
        "modelMetadata",
        "validateModel",
        "generateTestCase",
        "testCases",
        "singleRecommendation",
        "runBulkAssignment",
        "llmStatus",
        "explainRecommendation",
        "explainAssignment",
        "exportReports",
        "generateDatasetExport",
        "generateModelExport",
        "generateAssignmentExport",
        "sandboxSettings",
    )

    for method_name in expected_methods:
        assert method_name in api_js


def test_manual_browser_pipeline_checklist_is_documented() -> None:
    checklist_path = ROOT / "docs" / "end_to_end_pipeline_checklist.md"

    assert checklist_path.exists(), "Missing manual browser E2E checklist"

    checklist = checklist_path.read_text(encoding="utf-8").lower()

    for step in PIPELINE_STEPS:
        assert step in checklist


def test_startup_smoke_script_exists_and_checks_health() -> None:
    smoke_script = read("scripts/smoke_test.sh")

    assert "/api/health" in smoke_script
    assert 'HOST="127.0.0.1"' in smoke_script
    assert 'PORT="8601"' in smoke_script


def test_main_compass_api_is_not_imported_by_sandbox_backend() -> None:
    backend_files = list((ROOT / "backend").rglob("*.py"))
    forbidden_fragments = (
        "from src.",
        "import src.",
        "from agents",
        "import agents",
        "from llm",
        "import llm",
    )

    offenders: list[str] = []

    for path in backend_files:
        content = path.read_text(encoding="utf-8")

        for fragment in forbidden_fragments:
            if fragment in content:
                offenders.append(f"{path.relative_to(ROOT)} contains {fragment}")

    assert not offenders, "Sandbox backend imports forbidden main project modules:\n" + (
        "\n".join(offenders)
    )