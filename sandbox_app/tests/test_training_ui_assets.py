from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_training_ui_assets_are_wired() -> None:
    training_js = read("frontend/js/pages/training.js")
    metrics_js = read("frontend/js/components/training_metrics.js")
    plots_js = read("frontend/js/components/training_plots.js")
    api_js = read("frontend/js/api.js")

    assert "export async function renderTraining" in training_js
    assert "api.runTraining" in training_js
    assert "api.generateTrainingReport" in training_js
    assert "renderTrainingMetrics" in training_js
    assert "renderTrainingPlots" in training_js
    assert "baseline_rule_based" in training_js
    assert "logistic_regression" in training_js
    assert "random_forest" in training_js
    assert "torch_mlp" in training_js
    assert 'id="featureMaxPairs"' in training_js
    assert 'value="120000"' in training_js
    assert "payload.max_pairs = maxPairs" in training_js
    assert 'id="paramRandomForestEstimators" type="number" value="80"' in training_js
    assert 'id="paramTorchEpochs" type="number" value="8"' in training_js
    assert 'id="paramTorchBatchSize" type="number" value="64"' in training_js

    assert "export function renderTrainingMetrics" in metrics_js
    assert "export function renderTrainingPlots" in plots_js
    assert "/api/reports/training/" in plots_js
    assert "plots.session_plots" in plots_js
    assert "plots.model_plots" in plots_js
    assert "typeof path !== \"string\"" in plots_js
    assert "Сводные графики" in plots_js
    assert "training-plot-image" in plots_js

    assert "runTraining" in api_js
    assert "trainingSessions" in api_js
    assert "generateTrainingReport" in api_js
