import { api } from "../api.js";
import { htmlEscape, prettyJson, toast } from "../app.js";
import { renderSummaryCards } from "../components/charts.js";
import { renderDataTable } from "../components/table.js";

const state = {
  sessions: null,
  selectedSessionId: "",
  selectedModelName: "",
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

function selectedSession() {
  return (state.sessions?.sessions || []).find(
    (session) => session.session_id === state.selectedSessionId,
  );
}

function readControls() {
  state.selectedSessionId = document.querySelector("#modelsSession").value;
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
        latest_models: sessions[0]?.trained_models?.length || 0,
        latest_rows: sessions[0]?.rows || 0,
        latest_features: sessions[0]?.feature_count || 0,
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
      <div class="viewer-section-header">
        <div>
          <h2>Model artifacts</h2>
          <p class="muted">Artifact metadata, predictions, metrics and export validation.</p>
        </div>
      </div>
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

async function refreshSessions() {
  try {
    setModelsLoading(true, "Sessions...");
    state.sessions = await api.trainingSessions();

    if (!state.selectedSessionId) {
      state.selectedSessionId = state.sessions?.sessions?.[0]?.session_id || "";
    }

    document.querySelector("#modelsSession").innerHTML = sessionOptions(state.sessions);
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

async function loadModelArtifact(modelName) {
  try {
    readControls();

    if (!state.selectedSessionId) {
      throw new Error("Сначала выбери training session.");
    }

    setModelsLoading(true, `${modelName}...`);
    const details = await api.trainingModelArtifact(state.selectedSessionId, modelName);
    renderModelArtifact(details);
  } catch (error) {
    renderError(error);
    toast("Model artifact", error.message || String(error));
  } finally {
    setModelsLoading(false);
  }
}

function bindModelButtons() {
  document.querySelectorAll("[data-models-action='model']").forEach((button) => {
    button.addEventListener("click", () => {
      loadModelArtifact(button.dataset.modelName);
    });
  });
}

function bindEvents() {
  document.querySelector("#modelsSession").addEventListener("change", readControls);

  document.querySelector("[data-models-action='refresh']").addEventListener("click", () => {
    refreshSessions();
  });

  document.querySelector("[data-models-action='sessions']").addEventListener("click", () => {
    renderSessionsList();
  });

  document.querySelector("[data-models-action='details']").addEventListener("click", () => {
    loadSessionDetails();
  });
}

export async function renderModels() {
  state.sessions = await api.trainingSessions();
  state.selectedSessionId = state.sessions?.sessions?.[0]?.session_id || "";

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
              Training sessions, model artifacts, predictions, metrics and export validation.
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
        </div>

        <div class="toolbar">
          <button class="button button-secondary" data-models-action="sessions" type="button">
            Sessions
          </button>
          <button class="button button-primary" data-models-action="details" type="button">
            Session details
          </button>
          <button class="button button-secondary" data-models-action="refresh" type="button">
            Refresh
          </button>
        </div>
      </article>

      <article class="card">
        <h2>Selected session</h2>
        <pre class="code">${prettyJson(selectedSession() || {})}</pre>
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