from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_llm_assets_are_wired() -> None:
    ollama = read("backend/llm/ollama_client.py")
    explainer = read("backend/llm/qwen_explainer.py")
    api_py = read("backend/api/llm.py")
    assignment_lab = read("frontend/js/pages/assignment_lab.js")
    api_js = read("frontend/js/api.js")

    assert "SANDBOX_OLLAMA_BASE_URL" in ollama
    assert "SANDBOX_OLLAMA_MODEL" in ollama
    assert "SANDBOX_LLM_TIMEOUT_SECONDS" in ollama
    assert "OllamaClient" in ollama

    assert "explain_recommendation" in explainer
    assert "fallback_recommendation_explanation" in explainer
    assert "validate_candidate_references" in explainer
    assert "ranking_source" in explainer
    assert "model_output_unchanged" in explainer

    assert 'prefix="/llm"' in api_py
    assert 'router.get("/status")' in api_py
    assert 'router.post("/explain/recommendation")' in api_py
    assert 'router.post("/explain/assignment")' in api_py

    assert "useLlmExplanations" in assignment_lab
    assert "LLM explanations через Qwen/Ollama" in assignment_lab
    assert "maybeExplainSingleRecommendation" in assignment_lab
    assert "maybeExplainBulkAssignment" in assignment_lab

    assert "llmStatus" in api_js
    assert "explainRecommendation" in api_js
    assert "explainAssignment" in api_js