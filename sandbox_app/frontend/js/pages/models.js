import { api } from "../api.js";
import { htmlEscape, prettyJson, toast } from "../app.js";
import { renderSummaryCards } from "../components/charts.js";
import { renderDataTable } from "../components/table.js";

const state = {
  sessions: null,
  models: null,
  selectedSessionId: "",
  selectedModelName: "",
  exportOnnx: false,
  sampleSize: 100,
};

function sessionOptions(payload) {
  const sessions = payload?.sessions || [];

  if (sessions.length === 0) {
    return '<option value="">Нет training sessions</option>';
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

function modelOptions() {
  const models = filteredModels();

  if (models.length === 0) {
    return '<option value="">Нет моделей</option>';
  }

  return models
    .map((model) => {
      const selected = model.model_name === state.selectedModelName ? "selected" : "";

      return `
        <option value="${htmlEscape(model.model_name)}" ${selected}>
          ${htmlEscape(model.model_name)} · ${htmlEscape(model.artifact_format || "")}
        </option>
      `;
    })
    .join("");
}

function filteredModels() {
  return (state.models?.models || []).filter(
    (model) => model.session_id === state.selectedSessionId,
  );
}

function selectedSession() {
  return (state.sessions?.sessions || []).find(
    (session) => session.session_id === state.selectedSessionId,
  );
}

function selectedModel() {
  return filteredModels().find((model) => model.model_name === state.selectedModelName);
}

function readControls() {
  state.selectedSessionId = document.querySelector("#modelsSession").value;
  state.selectedModelName = document.querySelector("#modelsModel").value;
  state.exportOnnx = document.querySelector("#modelsExportOnnx").checked;
  state.sampleSize = Number.parseInt(
    document.querySelector("#modelsSampleSize").value,
    10,
  ) || 100;
}

function syncModelSelect() {
  const select = document.querySelector("#modelsModel");
  select.innerHTML = modelOptions();

  if (!state.selectedModelName) {
    state.selectedModelName = filteredModels()[0]?.model_name || "";
    select.value = state.selectedModelName;
  }
}

function setModelsLoading(isLoading, label = "Loading...") {
  const status = document.querySelector("#modelsStatus");
  const buttons = document.querySelectorAll("[data-models-action]");

  buttons.forEach((button) => {
    button.disabled = isLoading;
    button.classList.toggle("loading", isLoading);
  });

  status.className = isLoading ? "status-pill status-pending" : "status-pill status-ok";
  status.innerHTML = isLoading
    ? `<span class="status-dot"></span><span>${htmlEscape(label)}</span>`
    : '<span class="status-dot"></span><span>Готов</span>';
}

function renderOutput(html) {
  document.querySelector("#modelsOutput").innerHTML = html;
}

function renderError(error) {
  renderOutput(`
    <article class="card">
      <span class="badge">Error</span>
      <h2>Models error</h2>
      <p class="muted">${htmlEscape(error.message || String(error))}</p>
    </article>
  `);
}

function renderSessionsList() {
  const sessions = state.sessions?.sessions || [];
  const models = state.models?.models || [];

  if (sessions.length === 0) {
    renderOutput(`
      <article class="card">
        <h2>Training sessions</h2>
        <p class="muted">Training sessions пока не найдены.</p>
      </article>
    `);
    return;
  }

  const rows = sessions.map((session) => ({
    session_id: session.session_id,
    status: session.status,
    dataset_id: session.dataset_id,
    dataset_kind: session.dataset_kind,
    target_mode: session.target_mode,
    feature_count: session.feature_count,
    rows: session.rows,
    trained_models: (session.trained_models || []).join(", "),
    completed_at: session.completed_at,
  }));

  renderOutput(`
    <section class="grid grid-4">
      ${renderSummaryCards({
        sessions: state.sessions.total || 0,
        models: models.length,
        validated: models.filter(
          (model) => model.export_validation_status === "validated",
        ).length,
        onnx: models.filter((model) => model.onnx_path).length,
      })}
    </section>

    <article class="card" style="margin-top: 16px;">
      <h2>Training sessions</h2>
      ${renderDataTable(rows, [
        "session_id",
        "status",
        "dataset_id",
        "dataset_kind",
        "target_mode",
        "feature_count",
        "rows",
        "trained_models",
        "completed_at",
      ])}
    </article>
  `);
}

function renderModelsList() {
  const models = state.models?.models || [];

  if (models.length === 0) {
    renderOutput(`
      <article class="card">
        <h2>Saved models</h2>
        <p class="muted">Saved models пока не найдены.</p>
      </article>
    `);
    return;
  }

  const rows = models.map((model) => ({
    session_id: model.session_id,
    model_name: model.model_name,
    artifact_format: model.artifact_format,
    dataset_id: model.dataset_id,
    target_mode: model.target_mode,
    feature_count: model.feature_count,
    validation: model.export_validation_status,
    onnx: model.onnx_path ? "yes" : "no",
  }));

  renderOutput(`
    <article class="card">
      <h2>Saved models</h2>
      ${renderDataTable(rows, [
        "session_id",
        "model_name",
        "artifact_format",
        "dataset_id",
        "target_mode",
        "feature_count",
        "validation",
        "onnx",
      ])}
    </article>
  `);
}

function renderSessionDetails(details) {
  const artifacts = details.artifacts || [];
  const artifactRows = artifacts.map((artifact) => ({
    model_name: artifact.model_name,
    status: artifact.export_validation?.status || "",
    artifact_format: artifact.metadata?.artifact_format || "",
    feature_count: artifact.metadata?.feature_count || 0,
    train_rows: artifact.metadata?.train_rows || 0,
    prediction_rows: artifact.metadata?.prediction_rows || 0,
    files: (artifact.files || []).join(", "),
  }));

  const buttons = artifacts
    .map(
      (artifact) => `
        <button
          class="button button-secondary"
          data-model-name="${htmlEscape(artifact.model_name)}"
          data-models-action="model"
          type="button"
        >
          ${htmlEscape(artifact.model_name)}
        </button>
      `,
    )
    .join("");

  renderOutput(`
    <section class="grid grid-4">
      ${renderSummaryCards({
        models: artifacts.length,
        rows: details.summary?.rows || 0,
        feature_count: details.summary?.feature_count || 0,
        failures: details.summary?.failed_models?.length || 0,
      })}
    </section>

    <article class="card" style="margin-top: 16px;">
      <h2>Session summary</h2>
      <pre class="code">${prettyJson(details.summary || {})}</pre>
    </article>

    <article class="card" style="margin-top: 16px;">
      <h2>Model artifacts</h2>
      ${renderDataTable(artifactRows)}
      <div class="toolbar" style="margin-top: 12px;">${buttons}</div>
    </article>

    <article class="card" style="margin-top: 16px;">
      <h2>Comparison metrics</h2>
      ${renderDataTable(details.comparison_metrics || [])}
    </article>
  `);

  bindModelButtons();
}

function renderModelArtifact(details) {
  renderOutput(`
    <section class="grid grid-3">
      <article class="card">
        <h2>${htmlEscape(details.model_name)}</h2>
        <p class="muted">${htmlEscape(details.model_dir || "")}</p>
      </article>
      <article class="card">
        <h2>Export validation</h2>
        <p><strong>${htmlEscape(details.export_validation?.status || "unknown")}</strong></p>
      </article>
      <article class="card">
        <h2>Predictions</h2>
        <p><strong>${htmlEscape(details.prediction_rows || 0)}</strong> rows</p>
      </article>
    </section>

    <article class="card" style="margin-top: 16px;">
      <h2>Model metadata</h2>
      <pre class="code">${prettyJson(details.metadata || {})}</pre>
    </article>

    <article class="card" style="margin-top: 16px;">
      <h2>Export validation</h2>
      <pre class="code">${prettyJson(details.export_validation || {})}</pre>
    </article>

    <article class="card" style="margin-top: 16px;">
      <h2>Metrics</h2>
      <pre class="code">${prettyJson(details.metrics || {})}</pre>
    </article>

    <article class="card" style="margin-top: 16px;">
      <h2>Predictions preview</h2>
      ${renderDataTable(details.predictions_preview || [])}
    </article>
  `);
}

function renderExportResult(result) {
  renderOutput(`
    <section class="grid grid-3">
      <article class="card">
        <h2>${htmlEscape(result.model_name)}</h2>
        <p class="muted">${htmlEscape(result.session_id)}</p>
      </article>
      <article class="card">
        <h2>Validation</h2>
        <p><strong>${htmlEscape(result.status || "unknown")}</strong></p>
      </article>
      <article class="card">
        <h2>ONNX</h2>
        <p><strong>${htmlEscape(result.onnx?.status || "not_requested")}</strong></p>
      </article>
    </section>

    <article class="card" style="margin-top: 16px;">
      <h2>Export validation</h2>
      <pre class="code">${prettyJson(result)}</pre>
    </article>
  `);
}

async function refreshAll() {
  state.sessions = await api.trainingSessions();
  state.models = await api.modelsList();

  if (!state.selectedSessionId) {
    state.selectedSessionId = state.sessions?.sessions?.[0]?.session_id || "";
  }

  if (!state.selectedModelName) {
    state.selectedModelName = filteredModels()[0]?.model_name || "";
  }

  document.querySelector("#modelsSession").innerHTML = sessionOptions(state.sessions);
  syncModelSelect();
}

async function refreshSessions() {
  try {
    setModelsLoading(true, "Sessions...");
    await refreshAll();
    renderSessionsList();
  } catch (error) {
    renderError(error);
    toast("Models", error.message || String(error));
  } finally {
    setModelsLoading(false);
  }
}

async function loadSessionDetails() {
  try {
    readControls();

    if (!state.selectedSessionId) {
      throw new Error("Сначала выбери training session.");
    }

    setModelsLoading(true, "Session details...");
    const details = await api.trainingSession(state.selectedSessionId);
    renderSessionDetails(details);
  } catch (error) {
    renderError(error);
    toast("Models", error.message || String(error));
  } finally {
    setModelsLoading(false);
  }
}

async function loadModelArtifact(modelName = null) {
  try {
    readControls();

    const selectedModelName = modelName || state.selectedModelName;

    if (!state.selectedSessionId || !selectedModelName) {
      throw new Error("Сначала выбери training session и model.");
    }

    setModelsLoading(true, `${selectedModelName}...`);
    const details = await api.trainingModelArtifact(
      state.selectedSessionId,
      selectedModelName,
    );
    renderModelArtifact(details);
  } catch (error) {
    renderError(error);
    toast("Model artifact", error.message || String(error));
  } finally {
    setModelsLoading(false);
  }
}

async function validateSelectedModel(exportOnnx = false) {
  try {
    readControls();

    if (!state.selectedSessionId || !state.selectedModelName) {
      throw new Error("Сначала выбери training session и model.");
    }

    setModelsLoading(true, exportOnnx ? "Export..." : "Validate...");
    const payload = {
      export_onnx: exportOnnx,
      sample_size: state.sampleSize,
    };
    const result = exportOnnx
      ? await api.exportModel(state.selectedSessionId, state.selectedModelName, payload)
      : await api.validateModel(state.selectedSessionId, state.selectedModelName, payload);

    renderExportResult(result);
    state.models = await api.modelsList();
    syncModelSelect();
  } catch (error) {
    renderError(error);
    toast("Model export", error.message || String(error));
  } finally {
    setModelsLoading(false);
  }
}

function bindModelButtons() {
  document.querySelectorAll("[data-models-action='model']").forEach((button) => {
    button.addEventListener("click", () => {
      state.selectedModelName = button.dataset.modelName;
      document.querySelector("#modelsModel").value = state.selectedModelName;
      loadModelArtifact(button.dataset.modelName);
    });
  });
}

function bindEvents() {
  document.querySelector("#modelsSession").addEventListener("change", () => {
    readControls();
    state.selectedModelName = filteredModels()[0]?.model_name || "";
    syncModelSelect();
  });

  document.querySelector("#modelsModel").addEventListener("change", readControls);
  document.querySelector("#modelsExportOnnx").addEventListener("change", readControls);
  document.querySelector("#modelsSampleSize").addEventListener("change", readControls);

  document.querySelector("[data-models-action='refresh']").addEventListener("click", () => {
    refreshSessions();
  });

  document.querySelector("[data-models-action='sessions']").addEventListener("click", () => {
    renderSessionsList();
  });

  document.querySelector("[data-models-action='models']").addEventListener("click", () => {
    renderModelsList();
  });

  document.querySelector("[data-models-action='details']").addEventListener("click", () => {
    loadSessionDetails();
  });

  document.querySelector("[data-models-action='selected-model']").addEventListener(
    "click",
    () => {
      loadModelArtifact();
    },
  );

  document.querySelector("[data-models-action='validate']").addEventListener("click", () => {
    validateSelectedModel(false);
  });

  document.querySelector("[data-models-action='export']").addEventListener("click", () => {
    validateSelectedModel(state.exportOnnx);
  });
}

export async function renderModels() {
  state.sessions = await api.trainingSessions();
  state.models = await api.modelsList();
  state.selectedSessionId = state.sessions?.sessions?.[0]?.session_id || "";
  state.selectedModelName = filteredModels()[0]?.model_name || "";

  window.setTimeout(() => {
    bindEvents();
    renderSessionsList();
  }, 0);

  return `
    <section class="grid grid-2">
      <article class="card">
        <div class="viewer-section-header">
          <div>
            <h2>Models</h2>
            <p class="muted">
              Saved models, native artifacts, optional ONNX export and validation status.
            </p>
          </div>
          <div class="status-pill status-ok" id="modelsStatus">
            <span class="status-dot"></span>
            <span>Готов</span>
          </div>
        </div>

        <div class="toolbar">
          <div class="form-row">
            <label for="modelsSession">Training session</label>
            <select class="select" id="modelsSession">
              ${sessionOptions(state.sessions)}
            </select>
          </div>

          <div class="form-row">
            <label for="modelsModel">Model</label>
            <select class="select" id="modelsModel">
              ${modelOptions()}
            </select>
          </div>

          <div class="form-row">
            <label for="modelsSampleSize">Validation sample</label>
            <input
              class="input"
              id="modelsSampleSize"
              min="1"
              max="10000"
              type="number"
              value="100"
            />
          </div>
        </div>

        <label class="checkbox-row">
          <input id="modelsExportOnnx" type="checkbox" />
          <span>Try optional ONNX export</span>
        </label>

        <div class="toolbar">
          <button class="button button-secondary" data-models-action="sessions" type="button">
            Sessions
          </button>
          <button class="button button-secondary" data-models-action="models" type="button">
            Models
          </button>
          <button class="button button-primary" data-models-action="details" type="button">
            Session details
          </button>
          <button
            class="button button-secondary"
            data-models-action="selected-model"
            type="button"
          >
            Model details
          </button>
          <button class="button button-secondary" data-models-action="validate" type="button">
            Validate native
          </button>
          <button class="button button-secondary" data-models-action="export" type="button">
            Export / validate
          </button>
          <button class="button button-secondary" data-models-action="refresh" type="button">
            Refresh
          </button>
        </div>
      </article>

      <article class="card">
        <h2>Selected</h2>
        <pre class="code">${prettyJson({
          session: selectedSession() || {},
          model: selectedModel() || {},
        })}</pre>
      </article>
    </section>

    <section id="modelsOutput" style="margin-top: 16px;">
      <article class="card">
        <h2>Training sessions</h2>
        <p class="muted">Загрузка sessions...</p>
      </article>
    </section>
  `;
}