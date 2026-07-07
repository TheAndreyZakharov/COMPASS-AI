from __future__ import annotations

from pathlib import Path

SANDBOX_ROOT = Path(__file__).resolve().parents[2]
PROJECT_ROOT = SANDBOX_ROOT.parent

CONFIG_DIR = SANDBOX_ROOT / "config"
APP_SETTINGS_PATH = CONFIG_DIR / "app_settings.json"

FRONTEND_DIR = SANDBOX_ROOT / "frontend"
FRONTEND_ASSETS_DIR = FRONTEND_DIR / "assets"
FRONTEND_INDEX_PATH = FRONTEND_DIR / "index.html"

DATA_DIR = SANDBOX_ROOT / "data"
GENERATED_DATA_DIR = DATA_DIR / "generated"
IMPORTED_DATA_DIR = DATA_DIR / "imported"
TEST_CASES_DIR = DATA_DIR / "test_cases"
EXPORTS_DIR = DATA_DIR / "exports"

TRAINING_SESSIONS_DIR = SANDBOX_ROOT / "training_sessions"
ASSIGNMENT_SESSIONS_DIR = SANDBOX_ROOT / "assignment_sessions"
REPORTS_DIR = SANDBOX_ROOT / "reports"
LOGS_DIR = SANDBOX_ROOT / "logs"


def ensure_runtime_dirs() -> None:
    runtime_dirs = (
        GENERATED_DATA_DIR,
        IMPORTED_DATA_DIR,
        TEST_CASES_DIR,
        EXPORTS_DIR,
        TRAINING_SESSIONS_DIR,
        ASSIGNMENT_SESSIONS_DIR,
        REPORTS_DIR,
        LOGS_DIR,
    )

    for path in runtime_dirs:
        path.mkdir(parents=True, exist_ok=True)