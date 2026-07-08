from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class SandboxPaths:
    project_root: Path
    sandbox_root: Path
    backend_dir: Path
    frontend_dir: Path
    frontend_css_dir: Path
    frontend_js_dir: Path
    frontend_assets_dir: Path
    config_dir: Path
    data_contracts_dir: Path
    feature_schemas_dir: Path
    model_presets_path: Path
    app_settings_path: Path
    data_dir: Path
    generated_data_dir: Path
    imported_data_dir: Path
    test_cases_dir: Path
    exports_dir: Path
    training_sessions_dir: Path
    assignment_sessions_dir: Path
    reports_dir: Path
    logs_dir: Path
    server_log_path: Path
    pid_path: Path
    tests_dir: Path


def get_paths() -> SandboxPaths:
    backend_dir = Path(__file__).resolve().parents[1]
    sandbox_root = backend_dir.parent
    project_root = sandbox_root.parent
    frontend_dir = sandbox_root / "frontend"
    config_dir = sandbox_root / "config"
    data_dir = sandbox_root / "data"
    logs_dir = sandbox_root / "logs"

    return SandboxPaths(
        project_root=project_root,
        sandbox_root=sandbox_root,
        backend_dir=backend_dir,
        frontend_dir=frontend_dir,
        frontend_css_dir=frontend_dir / "css",
        frontend_js_dir=frontend_dir / "js",
        frontend_assets_dir=frontend_dir / "assets",
        config_dir=config_dir,
        data_contracts_dir=config_dir / "data_contracts",
        feature_schemas_dir=config_dir / "feature_schemas",
        model_presets_path=config_dir / "model_presets.json",
        app_settings_path=config_dir / "app_settings.json",
        data_dir=data_dir,
        generated_data_dir=data_dir / "generated",
        imported_data_dir=data_dir / "imported",
        test_cases_dir=data_dir / "test_cases",
        exports_dir=data_dir / "exports",
        training_sessions_dir=sandbox_root / "training_sessions",
        assignment_sessions_dir=sandbox_root / "assignment_sessions",
        reports_dir=sandbox_root / "reports",
        logs_dir=logs_dir,
        server_log_path=logs_dir / "server.log",
        pid_path=logs_dir / "sandbox_app.pid",
        tests_dir=sandbox_root / "tests",
    )


PATHS = get_paths()


def ensure_runtime_dirs() -> None:
    for path in (
        PATHS.generated_data_dir,
        PATHS.imported_data_dir,
        PATHS.test_cases_dir,
        PATHS.exports_dir,
        PATHS.training_sessions_dir,
        PATHS.assignment_sessions_dir,
        PATHS.reports_dir,
        PATHS.logs_dir,
    ):
        path.mkdir(parents=True, exist_ok=True)