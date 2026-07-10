from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


REQUIRED_ISOLATION_KEYS = {
    "autonomous_subproject",
    "do_not_import_main_src",
    "do_not_import_main_llm",
    "do_not_import_main_agents",
    "do_not_modify_main_compass_api",
    "forbid_main_src_imports",
    "forbid_main_llm_imports",
    "forbid_main_agent_imports",
}


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_settings_backend_assets_are_wired() -> None:
    settings_api = read("backend/api/settings.py")
    main_py = read("backend/main.py")
    settings_json = json.loads(read("config/app_settings.json"))

    assert "APIRouter(prefix=\"/settings\"" in settings_api
    assert "@router.get(\"\")" in settings_api
    assert "@router.put(\"\")" in settings_api
    assert "@router.patch(\"\")" in settings_api
    assert "@router.post(\"/reset\")" in settings_api
    assert "@router.get(\"/schema\")" in settings_api
    assert "validate_settings" in settings_api
    assert "validate_isolation_flags" in settings_api
    assert "sandbox_app/" in settings_api

    assert "settings" in main_py
    assert "settings.router" in main_py

    assert settings_json["app"]["slug"] == "compass-ai-sandbox"
    assert settings_json["app"]["environment"] == "local"
    assert settings_json["app"]["target_python"] == "3.11.15"
    assert settings_json["defaults"]["domain_profile"]
    assert settings_json["defaults"]["dataset_mode"]
    assert settings_json["defaults"]["recommendation_mode"]
    assert settings_json["ollama"]["base_url"]
    assert settings_json["ollama"]["model"]
    assert settings_json["paths"]["generated_data_dir"].startswith("sandbox_app/")

    for key in REQUIRED_ISOLATION_KEYS:
        assert settings_json["isolation"][key] is True
        assert key in settings_api

    assert "\"target_python\": \"3.11.15\"" in settings_api
    assert "\"environment\": \"local\"" in settings_api
    assert "\"slug\": \"compass-ai-sandbox\"" in settings_api
    assert "ISOLATION_KEYS" in settings_api


def test_settings_are_compatible_with_core_loader() -> None:
    from sandbox_app.backend.core.settings import load_settings

    settings = load_settings()

    assert settings["app"]["slug"] == "compass-ai-sandbox"
    assert settings["app"]["environment"] == "local"
    assert settings["app"]["target_python"] == "3.11.15"


def test_backend_app_can_be_created_with_settings() -> None:
    from sandbox_app.backend.main import create_app

    app = create_app()

    assert app.title == "COMPASS AI Sandbox"


def test_settings_frontend_assets_are_wired() -> None:
    settings_js = read("frontend/js/pages/settings.js")
    api_js = read("frontend/js/api.js")
    index_html = read("frontend/index.html")

    assert "Настройки и схемы данных" in settings_js
    assert "Raw settings JSON" not in settings_js
    assert "<pre" not in settings_js
    assert "api.sandboxSettings" in settings_js
    assert "api.sandboxSettingsSchema" in settings_js
    assert "api.updateSandboxSettings" in settings_js
    assert "api.patchSandboxSettings" in settings_js
    assert "api.resetSandboxSettings" in settings_js
    assert "api.featureSchemas" in settings_js
    assert "api.featureSchemaTemplate" in settings_js
    assert "api.createFeatureSchema" in settings_js
    assert "api.updateFeatureSchema" in settings_js
    assert "api.deleteFeatureSchema" in settings_js
    assert "api.addSchemaFeature" in settings_js
    assert "api.deleteSchemaFeature" in settings_js
    assert "export async function renderSettings" in settings_js
    assert "export async function renderPage" in settings_js
    assert "export default renderSettings" in settings_js

    assert "apiPut" in api_js
    assert "apiPatch" in api_js
    assert "sandboxSettings" in api_js
    assert "sandboxSettingsSchema" in api_js
    assert "updateSandboxSettings" in api_js
    assert "resetSandboxSettings" in api_js
    assert "featureSchemaTemplate" in api_js
    assert "addSchemaFeature" in api_js
    assert "deleteSchemaFeature" in api_js

    assert "Настройки" in index_html
