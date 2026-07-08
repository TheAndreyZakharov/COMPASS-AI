import { api } from "../api.js";
import { getLastDatasetId, htmlEscape, prettyJson, setLastDatasetId, toast } from "../app.js";
import { renderSummaryCards } from "../components/charts.js";
import { renderDataTable } from "../components/table.js";
import {
  normalizeMetricRows,
  renderModelMetricCards,
  renderTrainingMetrics,
} from "../components/training_metrics.js";
import { renderReportLinks, renderTrainingPlots } from "../components/training_plots.js";

const MODEL_NAMES = [
  "baseline_rule_based",
  "sgd_classifier",
  "logistic_regression",
  "random_forest",
  "hist_gradient_boosting",
  "torch_mlp",
];

const state = {
  datasets: null,
  datasetId: "",
  datasetKind: "generated",
  lastTrainingResult: null,
  sessions: null,
  selectedSessionId: "",
};

function allDatasets(payload) {
  return [
    ...(payload?.generated || []).map((item) => ({ ...item, dataset_kind: "generated" })),
    ...(payload?.imported || []).map((item) => ({ ...item, dataset_kind: "imported" })),
  ];
}

function datasetOptionValue(dataset) {
  return `${dataset.dataset_kind}:${dataset.dataset_id}`;
}

function parseDatasetValue(value) {
  const [datasetKind, ...datasetIdParts] = value.split(":");

  return {
    datasetKind: datasetKind || "generated",
    datasetId: datasetIdParts.join(":"),
  };
}

function datasetOptions(payload) {
  const datasets = allDatasets(payload);

  if (datasets.length === 0) {
    return '<option value="">Нет datasets</option>';
  }

  return datasets
    .map((dataset) => {
      const selected =
        dataset.dataset_id === state.datasetId &&
        dataset.dataset_kind === state.datasetKind
          ? "selected"
          : "";

      return `
        <option value="${htmlEscape(datasetOptionValue(dataset))}" ${selected}>
          ${htmlEscape(dataset.dataset_id)} · ${htmlEscape(dataset.dataset_kind)}
        </option>
      `;
    })
    .join("");
}

function sessionOptions(payload) {
  const sessions = payload?.sessions || [];

  if (sessions.length === 0) {
    return '<option value="">Нет sessions</option>';
  }

  return sessions
    .map((session) => {
      const selected = session.session_id === state.selectedSessionId ? "selected" : "";

      return `
        <option value="${htmlEscape(session.session_id)}" ${selected}>
          ${htmlEscape(session.session_id)} · ${htmlEscape(session.status || "")}
        </option>
      `;
    })
    .join("");
}

function selectInitialDataset() {
  const datasets = allDatasets(state.datasets);
  const lastDatasetId = getLastDatasetId();
  const lastDataset = datasets.find((dataset) => dataset.dataset_id === lastDatasetId);
  const selectedDataset = lastDataset || datasets[0] || null;

  state.datasetId = selectedDataset?.dataset_id || "";
  state.datasetKind = selectedDataset?.dataset_kind || "generated";
}

function selectedDataset() {
  return allDatasets(state.datasets).find(
    (dataset) =>
      dataset.dataset_id === state.datasetId &&
      dataset.dataset_kind === state.datasetKind,
  );
}

function selectedModels() {
  return MODEL_NAMES.filter((modelName) => {
    const checkbox = document.querySelector(`[data-training-model="${modelName}"]`);
    return checkbox?.checked;
  });
}

function readDatasetControls() {
  const parsed = parseDatasetValue(document.querySelector("#trainingDataset").value);
  state.datasetId = parsed.datasetId;
  state.datasetKind = parsed.datasetKind;

  if (state.datasetId) {
    setLastDatasetId(state.datasetId);
  }
}

function readSessionControls() {
  state.selectedSessionId = document.querySelector("#trainingSessionSelect").value;
}

function numberValue(selector, fallback) {
  const value = Number.parseFloat(document.querySelector(selector).value);

  if (!Number.isFinite(value)) {
    return fallback;
  }

  return value;
}

function integerValue(selector, fallback) {
  const value = Number.parseInt(document.querySelector(selector).value, 10);

  if (!Number.isFinite(value)) {
    return fallback;
  }

  return value;
}

function setTrainingLoading(isLoading, label = "Training...") {
  const status = document.querySelector("#trainingStatus");
  const buttons = document.querySelectorAll("[data-training-action]");

  buttons.forEach((button) => {
    button.disabled = isLoading;
    button.classList.toggle("loading", isLoading);
  });

  status.className = isLoading ? "status-pill status-pending" : "status-pill status-ok";
  status.innerHTML = isLoading
    ? `<span class="status-dot"></span><span>${htmlEscape(label)}</span>`
    : '<span class="status-dot"></span><span>Готов</span>';
}

function setOutput(html) {
  document.querySelector("#trainingOutput").innerHTML = html;
}

function renderError(title, error) {
  setOutput(`
    <article class="card">
      <span class="badge">Error</span>
      <h2>${htmlEscape(title)}</h2>
      <p class="muted">${htmlEscape(error.message || String(error))}</p>
    </article>
  `);
}

function buildFeaturePayload() {
  readDatasetControls();

  const payload = {
    dataset_id: state.datasetId,
    dataset_kind: state.datasetKind,
    target_mode: document.querySelector("#trainingTargetMode").value,
    overwrite: document.querySelector("#featureOverwrite").checked,
  };

  const maxPairs = integerValue("#featureMaxPairs", 0);
  if (maxPairs > 0) {
    payload.max_pairs = maxPairs;
  }

  return payload;
}

function buildModelParams() {
  return {
    logistic_regression: {
      max_iter: integerValue("#paramLogisticMaxIter", 500),
    },
    random_forest: {
      max_depth: integerValue("#paramRandomForestDepth", 0) || null,
      n_estimators: integerValue("#paramRandomForestEstimators", 120),
    },
    sgd_classifier: {
      alpha: numberValue("#paramSgdAlpha", 0.0001),
      max_iter: integerValue("#paramSgdMaxIter", 1000),
    },
    torch_mlp: {
      batch_size: integerValue("#paramTorchBatchSize", 128),
      dropout: numberValue("#paramTorchDropout", 0.1),
      epochs: integerValue("#paramTorchEpochs", 12),
      hidden_size: integerValue("#paramTorchHidden", 64),
      learning_rate: numberValue("#paramTorchLr", 0.001),
    },
  };
}

function buildTrainingPayload() {
  readDatasetControls();

  const modelNames = selectedModels();

  if (modelNames.length === 0) {
    throw new Error("Выбери хотя бы одну модель.");
  }

  return {
    auto_build_features: document.querySelector("#trainingAutoBuild").checked,
    dataset_id: state.datasetId,
    dataset_kind: state.datasetKind,
    model_names: modelNames,
    model_params: buildModelParams(),
    seed: integerValue("#trainingSeed", 19001),
    split: {
      test: numberValue("#splitTest", 0.15),
      train: numberValue("#splitTrain", 0.7),
      validation: numberValue("#splitValidation", 0.15),
    },
    target_mode: document.querySelector("#trainingTargetMode").value,
  };
}

function renderFeatureResult(result) {
  const metadata = result.metadata || result;
  const dimensions = metadata.feature_dimensions || {};
  const counts = metadata.output_counts || {};
  const featureRows = [
    {
      feature_count: dimensions.feature_count || 0,
      feature_rows: counts.feature_rows || 0,
      skipped_pairs: counts.skipped_pairs || 0,
      skill_vocabulary_size: dimensions.skill_vocabulary_size || 0,
      target_mode: metadata.target_mode || "",
      target_rows: counts.target_rows || 0,
    },
  ];

  setOutput(`
    <section class="grid grid-4">
      ${renderSummaryCards({
        feature_count: dimensions.feature_count || 0,
        skill_vocabulary_size: dimensions.skill_vocabulary_size || 0,
        feature_rows: counts.feature_rows || 0,
        target_rows: counts.target_rows || 0,
      })}
    </section>

    <article class="card" style="margin-top: 16px;">
      <h2>Feature dimensions</h2>
      ${renderDataTable(featureRows)}
    </article>

    <article class="card" style="margin-top: 16px;">
      <h2>Feature metadata</h2>
      <pre class="code">${prettyJson(metadata)}</pre>
    </article>
  `);
}

function renderTrainingResult(result) {
  const comparison = result.comparison_metrics || result.metrics || [];
  const normalizedMetrics = normalizeMetricRows(comparison);
  const sessionId = result.session_id || result.summary?.session_id || "";

  state.lastTrainingResult = result;
  state.selectedSessionId = sessionId || state.selectedSessionId;

  setOutput(`
    <section class="grid grid-4">
      ${renderSummaryCards({
        session: sessionId || "created",
        status: result.status || "",
        models: normalizedMetrics.length,
        failed: result.failed_models?.length || 0,
      })}
    </section>

    <section class="grid grid-3" style="margin-top: 16px;">
      ${renderModelMetricCards(normalizedMetrics)}
    </section>

    <section style="margin-top: 16px;">
      ${renderTrainingMetrics(normalizedMetrics)}
    </section>

    <article class="card" style="margin-top: 16px;">
      <h2>Training response</h2>
      <pre class="code">${prettyJson(result)}</pre>
    </article>
  `);
}

function renderSessionDetails(details) {
  const comparison = details.comparison_metrics || [];
  const artifacts = details.artifacts || [];
  const artifactRows = artifacts.map((artifact) => ({
    artifact_format: artifact.metadata?.artifact_format || "",
    export_status: artifact.export_validation?.status || "",
    files: (artifact.files || []).join(", "),
    model_name: artifact.model_name,
    prediction_rows: artifact.prediction_rows || artifact.metadata?.prediction_rows || 0,
  }));

  setOutput(`
    <section class="grid grid-4">
      ${renderSummaryCards({
        session: details.session_id || state.selectedSessionId,
        status: details.summary?.status || "",
        models: artifacts.length,
        failures: details.summary?.failed_models?.length || 0,
      })}
    </section>

    <section style="margin-top: 16px;">
      ${renderTrainingMetrics(comparison)}
    </section>

    <article class="card" style="margin-top: 16px;">
      <h2>Model artifacts</h2>
      ${renderDataTable(artifactRows)}
    </article>

    <article class="card" style="margin-top: 16px;">
      <h2>Session summary</h2>
      <pre class="code">${prettyJson(details.summary || details)}</pre>
    </article>
  `);
}

function renderReport(sessionId, manifest) {
  setOutput(`
    ${renderReportLinks(sessionId, manifest)}
    <section style="margin-top: 16px;">
      ${renderTrainingPlots(sessionId, manifest)}
    </section>
    <article class="card" style="margin-top: 16px;">
      <h2>Report manifest</h2>
      <pre class="code">${prettyJson(manifest)}</pre>
    </article>
  `);
}

async function buildFeatures() {
  try {
    setTrainingLoading(true, "Building features...");
    const result = await api.buildFeatures(buildFeaturePayload());
    renderFeatureResult(result);
    toast("Features built", `${state.datasetId}`);
  } catch (error) {
    renderError("Feature builder failed", error);
    toast("Feature builder", error.message || String(error));
  } finally {
    setTrainingLoading(false);
  }
}

async function loadFeatureMetadata() {
  try {
    readDatasetControls();
    setTrainingLoading(true, "Loading metadata...");
    const query = `?dataset_kind=${encodeURIComponent(state.datasetKind)}`;
    const result = await api.featureMetadata(state.datasetId, query);
    renderFeatureResult(result);
  } catch (error) {
    renderError("Feature metadata failed", error);
    toast("Feature metadata", error.message || String(error));
  } finally {
    setTrainingLoading(false);
  }
}

async function runTraining() {
  try {
    setTrainingLoading(true, "Training models...");
    const result = await api.runTraining(buildTrainingPayload());
    renderTrainingResult(result);
    await refreshSessions(false);
    toast("Training finished", result.session_id || state.datasetId);
  } catch (error) {
    renderError("Training failed", error);
    toast("Training", error.message || String(error));
  } finally {
    setTrainingLoading(false);
  }
}

async function refreshSessions(render = true) {
  state.sessions = await api.trainingSessions();

  if (!state.selectedSessionId) {
    state.selectedSessionId = state.sessions?.sessions?.[0]?.session_id || "";
  }

  const select = document.querySelector("#trainingSessionSelect");
  if (select) {
    select.innerHTML = sessionOptions(state.sessions);
    select.value = state.selectedSessionId;
  }

  if (render) {
    const rows = state.sessions?.sessions || [];
    setOutput(`
      <article class="card">
        <h2>Training sessions</h2>
        ${renderDataTable(rows)}
      </article>
    `);
  }
}

async function loadSessionDetails() {
  try {
    readSessionControls();

    if (!state.selectedSessionId) {
      throw new Error("Training session не выбрана.");
    }

    setTrainingLoading(true, "Loading session...");
    const details = await api.trainingSession(state.selectedSessionId);
    renderSessionDetails(details);
  } catch (error) {
    renderError("Session details failed", error);
    toast("Training session", error.message || String(error));
  } finally {
    setTrainingLoading(false);
  }
}

async function generateReport() {
  try {
    readSessionControls();

    if (!state.selectedSessionId) {
      throw new Error("Training session не выбрана.");
    }

    setTrainingLoading(true, "Generating report...");
    const manifest = await api.generateTrainingReport(state.selectedSessionId);
    renderReport(state.selectedSessionId, manifest);
    toast("Report generated", state.selectedSessionId);
  } catch (error) {
    renderError("Report generation failed", error);
    toast("Training report", error.message || String(error));
  } finally {
    setTrainingLoading(false);
  }
}

async function loadReport() {
  try {
    readSessionControls();

    if (!state.selectedSessionId) {
      throw new Error("Training session не выбрана.");
    }

    setTrainingLoading(true, "Loading report...");
    const manifest = await api.trainingReport(state.selectedSessionId);
    renderReport(state.selectedSessionId, manifest);
  } catch (error) {
    renderError("Report loading failed", error);
    toast("Training report", error.message || String(error));
  } finally {
    setTrainingLoading(false);
  }
}

function toggleAllModels(checked) {
  MODEL_NAMES.forEach((modelName) => {
    const checkbox = document.querySelector(`[data-training-model="${modelName}"]`);
    if (checkbox) {
      checkbox.checked = checked;
    }
  });
}

function bindEvents() {
  document.querySelector("#trainingDataset").addEventListener("change", readDatasetControls);
  document.querySelector("#trainingSessionSelect").addEventListener("change", readSessionControls);

  document.querySelector("[data-training-action='features']").addEventListener("click", () => {
    buildFeatures();
  });

  document.querySelector("[data-training-action='metadata']").addEventListener("click", () => {
    loadFeatureMetadata();
  });

  document.querySelector("[data-training-action='run']").addEventListener("click", () => {
    runTraining();
  });

  document.querySelector("[data-training-action='sessions']").addEventListener("click", () => {
    refreshSessions(true);
  });

  document.querySelector("[data-training-action='session-details']").addEventListener(
    "click",
    () => {
      loadSessionDetails();
    },
  );

  document.querySelector("[data-training-action='report-generate']").addEventListener(
    "click",
    () => {
      generateReport();
    },
  );

  document.querySelector("[data-training-action='report-load']").addEventListener("click", () => {
    loadReport();
  });

  document.querySelector("[data-training-action='select-all']").addEventListener("click", () => {
    toggleAllModels(true);
  });

  document.querySelector("[data-training-action='select-core']").addEventListener("click", () => {
    toggleAllModels(false);
    ["baseline_rule_based", "logistic_regression", "random_forest"].forEach((modelName) => {
      const checkbox = document.querySelector(`[data-training-model="${modelName}"]`);
      if (checkbox) {
        checkbox.checked = true;
      }
    });
  });
}

function renderModelCheckboxes() {
  return MODEL_NAMES.map((modelName) => {
    const checked = ["baseline_rule_based", "logistic_regression", "random_forest"].includes(
      modelName,
    )
      ? "checked"
      : "";

    return `
      <label class="checkbox-row">
        <input ${checked} data-training-model="${htmlEscape(modelName)}" type="checkbox" />
        <span>${htmlEscape(modelName)}</span>
      </label>
    `;
  }).join("");
}

export async function renderTraining() {
  state.datasets = await api.datasets();
  state.sessions = await api.trainingSessions();
  selectInitialDataset();
  state.selectedSessionId = state.sessions?.sessions?.[0]?.session_id || "";

  window.setTimeout(bindEvents, 0);

  return `
    <section class="grid grid-2">
      <article class="card">
        <div class="viewer-section-header">
          <div>
            <h2>Training</h2>
            <p class="muted">
              Build features, train multiple models, compare metrics and generate plots.
            </p>
          </div>
          <div class="status-pill status-ok" id="trainingStatus">
            <span class="status-dot"></span>
            <span>Готов</span>
          </div>
        </div>

        <div class="form">
          <div class="grid grid-2">
            <div class="form-row">
              <label for="trainingDataset">Dataset</label>
              <select class="select" id="trainingDataset">
                ${datasetOptions(state.datasets)}
              </select>
            </div>

            <div class="form-row">
              <label for="trainingTargetMode">target_mode</label>
              <select class="select" id="trainingTargetMode">
                <option value="balanced">balanced</option>
                <option value="quality">quality</option>
                <option value="speed">speed</option>
                <option value="learning">learning</option>
                <option value="risk_aware">risk_aware</option>
              </select>
            </div>

            <div class="form-row">
              <label for="trainingSeed">seed</label>
              <input class="input" id="trainingSeed" type="number" value="19001" />
            </div>

            <div class="form-row">
              <label for="featureMaxPairs">max_pairs</label>
              <input
                class="input"
                id="featureMaxPairs"
                min="1"
                placeholder="empty = all pairs"
                type="number"
              />
            </div>
          </div>

          <div class="grid grid-3">
            <div class="form-row">
              <label for="splitTrain">train split</label>
              <input class="input" id="splitTrain" step="0.01" type="number" value="0.70" />
            </div>
            <div class="form-row">
              <label for="splitValidation">validation split</label>
              <input
                class="input"
                id="splitValidation"
                step="0.01"
                type="number"
                value="0.15"
              />
            </div>
            <div class="form-row">
              <label for="splitTest">test split</label>
              <input class="input" id="splitTest" step="0.01" type="number" value="0.15" />
            </div>
          </div>

          <div class="grid grid-2">
            <label class="checkbox-row">
              <input checked id="featureOverwrite" type="checkbox" />
              <span>overwrite existing features</span>
            </label>
            <label class="checkbox-row">
              <input checked id="trainingAutoBuild" type="checkbox" />
              <span>auto build features before training</span>
            </label>
          </div>

          <h3>Models</h3>
          <div class="grid grid-2">
            ${renderModelCheckboxes()}
          </div>

          <div class="toolbar">
            <button class="button button-secondary" data-training-action="select-core" type="button">
              Select core
            </button>
            <button class="button button-secondary" data-training-action="select-all" type="button">
              Select all
            </button>
            <button class="button button-secondary" data-training-action="features" type="button">
              Build features
            </button>
            <button class="button button-secondary" data-training-action="metadata" type="button">
              Load metadata
            </button>
            <button class="button button-primary" data-training-action="run" type="button">
              Run training
            </button>
          </div>
        </div>
      </article>

      <article class="card">
        <h2>Model params</h2>
        <div class="grid grid-2">
          <div class="form-row">
            <label for="paramLogisticMaxIter">logistic max_iter</label>
            <input class="input" id="paramLogisticMaxIter" type="number" value="500" />
          </div>
          <div class="form-row">
            <label for="paramRandomForestEstimators">rf n_estimators</label>
            <input class="input" id="paramRandomForestEstimators" type="number" value="120" />
          </div>
          <div class="form-row">
            <label for="paramRandomForestDepth">rf max_depth</label>
            <input class="input" id="paramRandomForestDepth" placeholder="empty" type="number" />
          </div>
          <div class="form-row">
            <label for="paramSgdAlpha">sgd alpha</label>
            <input class="input" id="paramSgdAlpha" step="0.0001" type="number" value="0.0001" />
          </div>
          <div class="form-row">
            <label for="paramSgdMaxIter">sgd max_iter</label>
            <input class="input" id="paramSgdMaxIter" type="number" value="1000" />
          </div>
          <div class="form-row">
            <label for="paramTorchEpochs">torch epochs</label>
            <input class="input" id="paramTorchEpochs" type="number" value="12" />
          </div>
          <div class="form-row">
            <label for="paramTorchHidden">torch hidden</label>
            <input class="input" id="paramTorchHidden" type="number" value="64" />
          </div>
          <div class="form-row">
            <label for="paramTorchDropout">torch dropout</label>
            <input class="input" id="paramTorchDropout" step="0.01" type="number" value="0.10" />
          </div>
          <div class="form-row">
            <label for="paramTorchLr">torch lr</label>
            <input class="input" id="paramTorchLr" step="0.0001" type="number" value="0.001" />
          </div>
          <div class="form-row">
            <label for="paramTorchBatchSize">torch batch_size</label>
            <input class="input" id="paramTorchBatchSize" type="number" value="128" />
          </div>
        </div>
      </article>
    </section>

    <section class="grid grid-2" style="margin-top: 16px;">
      <article class="card">
        <h2>Training sessions</h2>
        <div class="toolbar">
          <select class="select" id="trainingSessionSelect">
            ${sessionOptions(state.sessions)}
          </select>
          <button class="button button-secondary" data-training-action="sessions" type="button">
            Refresh sessions
          </button>
          <button
            class="button button-secondary"
            data-training-action="session-details"
            type="button"
          >
            Session details
          </button>
          <button
            class="button button-secondary"
            data-training-action="report-generate"
            type="button"
          >
            Generate plots
          </button>
          <button class="button button-secondary" data-training-action="report-load" type="button">
            Load plots
          </button>
        </div>
      </article>

      <article class="card">
        <h2>Selected dataset</h2>
        <pre class="code">${prettyJson(selectedDataset() || {})}</pre>
      </article>
    </section>

    <section id="trainingOutput" style="margin-top: 16px;">
      <article class="card">
        <h2>Training UI</h2>
        <p class="muted">
          Выбери dataset, target mode, модели и запусти training прямо из браузера.
        </p>
      </article>
    </section>
  `;
}