from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
README_PATH = ROOT / "README.md"


REQUIRED_SECTIONS = (
    "# COMPASS AI Sandbox",
    "## Главные принципы",
    "## Быстрый запуск",
    "## Makefile targets",
    "## Структура папок",
    "## Backend",
    "## Frontend",
    "## Data contracts",
    "## Feature schemas",
    "## Custom schema editor",
    "## Генерация команды",
    "## Генерация задач",
    "## Генерация истории",
    "## Full dataset generation",
    "## Imported datasets",
    "## Data Viewer",
    "## Feature builder",
    "## Обучение моделей",
    "## Training sessions",
    "## Model export",
    "## Training plots и reports",
    "## Test team",
    "## Single recommendation",
    "## Bulk assignment",
    "## Qwen и Ollama explanations",
    "## Reports и exports",
    "## Settings",
    "## Полный browser pipeline",
    "## Проверки",
    "## Ограничения",
    "## Troubleshooting",
    "## Статус готовности",
)


REQUIRED_TROUBLESHOOTING_ITEMS = (
    "Port 8601 is busy",
    "Python is not from .venv",
    "FastAPI is not installed",
    "PyArrow is not installed",
    "Dataset is too large",
    "Feature schema is invalid",
    "Training session failed",
    "Model cannot be loaded",
    "ONNX Runtime is not installed",
    "Ollama is not running",
    "Qwen model not found",
    "Browser shows old JS after cache",
)


REQUIRED_ENDPOINTS = (
    "GET /api/health",
    "GET /api/status",
    "GET /api/config",
    "POST /api/generate/dataset",
    "GET /api/data-viewer/datasets",
    "POST /api/features/build",
    "POST /api/training/run",
    "GET /api/models",
    "POST /api/test-cases/generate",
    "POST /api/recommendations/single",
    "POST /api/assignment-sessions/run",
    "GET /api/llm/status",
    "GET /api/reports/exports",
    "GET /api/settings",
)


REQUIRED_COMMANDS = (
    "bash sandbox_app/scripts/start.sh",
    "bash sandbox_app/scripts/stop.sh",
    "bash sandbox_app/scripts/restart.sh",
    "bash sandbox_app/scripts/smoke_test.sh",
    "pytest sandbox_app/tests",
    "python -m compileall -q sandbox_app/backend sandbox_app/tests",
)


def read_readme() -> str:
    return README_PATH.read_text(encoding="utf-8")


def test_readme_exists_and_is_not_empty() -> None:
    assert README_PATH.exists()
    assert README_PATH.is_file()
    assert read_readme().strip()


def test_readme_contains_required_sections() -> None:
    readme = read_readme()

    for section in REQUIRED_SECTIONS:
        assert section in readme


def test_readme_contains_troubleshooting_items() -> None:
    readme = read_readme()

    for item in REQUIRED_TROUBLESHOOTING_ITEMS:
        assert item in readme


def test_readme_documents_core_endpoints() -> None:
    readme = read_readme()

    for endpoint in REQUIRED_ENDPOINTS:
        assert endpoint in readme


def test_readme_documents_operational_commands() -> None:
    readme = read_readme()

    for command in REQUIRED_COMMANDS:
        assert command in readme


def test_readme_documents_isolation_and_main_api_safety() -> None:
    readme = read_readme().lower()

    assert "не должен напрямую импортировать основной src" in readme
    assert "не должен напрямую импортировать основные llm modules" in readme
    assert "не должен напрямую импортировать основные agents" in readme
    assert "не должен менять основной compass api" in readme


def test_readme_avoids_markdown_code_fences() -> None:
    readme = read_readme()

    assert "```" not in readme