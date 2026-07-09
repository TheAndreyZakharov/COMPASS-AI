from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = ROOT.parent


REQUIRED_DIRECTORIES = {
    "backend",
    "frontend",
    "config",
    "scripts",
    "data",
    "training_sessions",
    "assignment_sessions",
    "reports",
    "logs",
    "docs",
    "tests",
}


REQUIRED_FILES = {
    ".python-version",
    "README.md",
    "requirements.txt",
    "config/app_settings.json",
    "backend/main.py",
    "frontend/index.html",
    "frontend/css/styles.css",
    "frontend/js/app.js",
    "frontend/js/api.js",
    "docs/final_readiness_checklist.md",
    "docs/end_to_end_pipeline_checklist.md",
    "tests/test_end_to_end_pipeline_assets.py",
    "tests/test_readme_assets.py",
}


REQUIRED_FRONTEND_PAGES = {
    "frontend/js/pages/dashboard.js",
    "frontend/js/pages/generator.js",
    "frontend/js/pages/viewer.js",
    "frontend/js/pages/import_data.js",
    "frontend/js/pages/training.js",
    "frontend/js/pages/models.js",
    "frontend/js/pages/assignment_lab.js",
    "frontend/js/pages/reports.js",
    "frontend/js/pages/settings.js",
}


REQUIRED_BACKEND_API_FILES = {
    "backend/api/config.py",
    "backend/api/contracts.py",
    "backend/api/feature_schemas.py",
    "backend/api/generate_team.py",
    "backend/api/generate_tasks.py",
    "backend/api/generate_history.py",
    "backend/api/generate_dataset.py",
    "backend/api/data_viewer.py",
    "backend/api/import_data.py",
    "backend/api/features.py",
    "backend/api/training.py",
    "backend/api/models.py",
    "backend/api/test_cases.py",
    "backend/api/recommendations.py",
    "backend/api/assignment_sessions.py",
    "backend/api/llm.py",
    "backend/api/reports.py",
    "backend/api/settings.py",
}


REQUIRED_TESTS = {
    "tests/test_feature_schemas.py",
    "tests/test_task_generator.py",
    "tests/test_history_generator.py",
    "tests/test_full_dataset_generator.py",
    "tests/test_data_viewer_api.py",
    "tests/test_importers.py",
    "tests/test_feature_builder.py",
    "tests/test_training_session.py",
    "tests/test_training_session_artifacts.py",
    "tests/test_model_export.py",
    "tests/test_training_reports.py",
    "tests/test_test_team_generator.py",
    "tests/test_single_recommendation.py",
    "tests/test_bulk_assignment.py",
    "tests/test_qwen_explainer.py",
    "tests/test_report_exports_helpers.py",
    "tests/test_reports_exports_assets.py",
    "tests/test_settings_assets.py",
    "tests/test_readme_assets.py",
    "tests/test_end_to_end_pipeline_assets.py",
}


REQUIRED_ISOLATION_FLAGS = {
    "autonomous_subproject",
    "do_not_import_main_src",
    "do_not_import_main_llm",
    "do_not_import_main_agents",
    "do_not_modify_main_compass_api",
    "forbid_main_src_imports",
    "forbid_main_llm_imports",
    "forbid_main_agent_imports",
}


REQUIRED_MAKE_TARGETS = {
    "sandbox-start",
    "sandbox-stop",
    "sandbox-restart",
    "sandbox-test",
    "sandbox-clean",
}


REQUIRED_REGISTERED_ROUTERS = {
    "status.router",
    "config.router",
    "sessions.router",
    "contracts.router",
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
}


REQUIRED_READINESS_PHRASES = {
    "Custom schemas can be created",
    "Full dataset generator works",
    "Training runs multiple models",
    "Single task recommendation works",
    "Bulk todo assignment works",
    "Fallback explanation works without LLM",
    "README exists",
}


def read(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


def assert_file(relative_path: str) -> None:
    path = ROOT / relative_path

    assert path.exists(), f"Missing file: {relative_path}"
    assert path.is_file(), f"Not a file: {relative_path}"
    assert path.read_text(encoding="utf-8").strip(), f"Empty file: {relative_path}"


def test_sandbox_directory_structure_is_complete() -> None:
    for directory in REQUIRED_DIRECTORIES:
        path = ROOT / directory

        assert path.exists(), f"Missing directory: {directory}"
        assert path.is_dir(), f"Not a directory: {directory}"


def test_required_project_files_exist() -> None:
    for relative_path in REQUIRED_FILES:
        assert_file(relative_path)


def test_backend_api_surface_exists() -> None:
    for relative_path in REQUIRED_BACKEND_API_FILES:
        assert_file(relative_path)


def test_frontend_pages_exist() -> None:
    for relative_path in REQUIRED_FRONTEND_PAGES:
        assert_file(relative_path)


def test_final_test_suite_assets_exist() -> None:
    for relative_path in REQUIRED_TESTS:
        assert_file(relative_path)


def test_app_settings_keep_sandbox_isolated_and_local() -> None:
    settings = json.loads(read("config/app_settings.json"))

    assert settings["app"]["host"] == "127.0.0.1"
    assert int(settings["app"]["port"]) == 8601
    assert settings["app"]["slug"] == "compass-ai-sandbox"
    assert settings["app"]["target_python"] == "3.11.15"

    isolation = settings["isolation"]

    for flag in REQUIRED_ISOLATION_FLAGS:
        assert isolation[flag] is True


def test_run_scripts_cover_start_stop_restart_smoke_and_clean() -> None:
    scripts = {
        "scripts/start.sh": ("127.0.0.1", "8601", "sandbox_app.pid"),
        "scripts/stop.sh": ("sandbox_app.pid", "Stopping"),
        "scripts/restart.sh": ("start.sh", "stop.sh"),
        "scripts/smoke_test.sh": ("/api/health", "smoke test passed"),
        "scripts/clean_tmp.sh": ("logs", "server.log", ".gitkeep"),
    }

    for relative_path, fragments in scripts.items():
        content = read(relative_path)

        for fragment in fragments:
            assert fragment in content


def test_makefile_contains_sandbox_targets() -> None:
    makefile_path = PROJECT_ROOT / "Makefile"

    assert makefile_path.exists()

    makefile = makefile_path.read_text(encoding="utf-8")

    for target in REQUIRED_MAKE_TARGETS:
        assert target in makefile


def test_backend_main_registers_final_api_surface() -> None:
    main_py = read("backend/main.py")

    expected_fragments = (
        "FastAPI",
        "CORSMiddleware",
        "StaticFiles",
        "create_app",
        "include_router",
    )

    for fragment in expected_fragments:
        assert fragment in main_py

    for router_name in REQUIRED_REGISTERED_ROUTERS:
        assert router_name in main_py


def test_frontend_is_vanilla_browser_ui() -> None:
    index_html = read("frontend/index.html")
    app_js = read("frontend/js/app.js")

    assert "streamlit" not in index_html.lower()
    assert "streamlit" not in app_js.lower()
    assert "dashboard" in index_html.lower()
    assert "Data Generator" in index_html
    assert "Data Viewer" in index_html
    assert "Training" in index_html
    assert "Models" in index_html
    assert "Assignment Lab" in index_html
    assert "Reports" in index_html
    assert "Settings" in index_html


def test_readme_and_final_checklist_document_milestone() -> None:
    readme = read("README.md")
    checklist = read("docs/final_readiness_checklist.md")

    for phrase in REQUIRED_READINESS_PHRASES:
        assert phrase in checklist

    assert "COMPASS AI Sandbox" in readme
    assert "pytest sandbox_app/tests" in readme
    assert "bash sandbox_app/scripts/start.sh" in readme
    assert "не должен менять основной COMPASS API" in readme


def test_sandbox_backend_does_not_import_main_project_modules() -> None:
    forbidden_fragments = (
        "from src.",
        "import src.",
        "from agents",
        "import agents",
        "from llm",
        "import llm",
    )

    offenders: list[str] = []

    for path in (ROOT / "backend").rglob("*.py"):
        content = path.read_text(encoding="utf-8")

        for fragment in forbidden_fragments:
            if fragment in content:
                offenders.append(f"{path.relative_to(ROOT)} contains {fragment}")

    assert not offenders, "Forbidden main project imports:\n" + "\n".join(offenders)