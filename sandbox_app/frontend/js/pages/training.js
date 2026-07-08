import { api } from "../api.js";
import { getLastDatasetId, htmlEscape, prettyJson, setLastDatasetId, toast } from "../app.js";
import { renderSummaryCards } from "../components/charts.js";
import { renderDataTable } from "../components/table.js";

const state = {
  datasets: null,
  datasetId: "",
  datasetKind: "generated",
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

function readControls() {
  const parsed = parseDatasetValue(document.querySelector("#featureDataset").value);
  state.datasetId = parsed.datasetId;
  state.datasetKind = parsed.datasetKind;

  if (state.datasetId) {
    setLastDatasetId(state.datasetId);
  }
}

function setFeatureLoading(isLoading, label = "Build features...") {
  const status = document.querySelector("#featureStatus");
  const buttons = document.querySelectorAll("[data-feature-action]");

  buttons.forEach((button) => {
    button.disabled = isLoading;
    button.classList.toggle("loading", isLoading);
  });

  status.className = isLoading ? "status-pill status-pending" : "status-pill status-ok";
  status.innerHTML = isLoading
    ? `<span class="status-dot"></span><span>${htmlEscape(label)}</span>`
    : '<span class="status-dot"></span><span>Готов</span>';
}

function renderResult(result) {
  const metadata = result.metadata || result;
  const dimensions = metadata.feature_dimensions || {};
  const counts = metadata.output_counts || {};
  const featureRows = [
    {
      feature_count: dimensions.feature_count || 0,
      skill_vocabulary_size: dimensions.skill_vocabulary_size || 0,
      feature_rows: counts.feature_rows || 0,
      target_rows: counts.target_rows || 0,
      skipped_pairs: counts.skipped_pairs || 0,
      target_mode: metadata.target_mode || "",
    },
  ];

  document.querySelector("#featureResult").innerHTML = `
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
  `;
}

function renderError(error) {
  document.querySelector("#featureResult").innerHTML = `
    <article class="card">
      <span class="badge">Error</span>
      <h2>Feature builder failed</h2>
      <p class="muted">${htmlEscape(error.message || String(error))}</p>
    </article>
  `;
}

async function buildFeatures() {
  try {
    readControls();
    setFeatureLoading(true, "Building features...");

    const payload = {
      dataset_id: state.datasetId,
      dataset_kind: state.datasetKind,
      target_mode: document.querySelector("#featureTargetMode").value,
      overwrite: document.querySelector("#featureOverwrite").checked,
    };

    const maxPairs = Number.parseInt(document.querySelector("#featureMaxPairs").value, 10);
    if (Number.isFinite(maxPairs) && maxPairs > 0) {
      payload.max_pairs = maxPairs;
    }

    const result = await api.buildFeatures(payload);
    renderResult(result);
    toast("Features built", `${state.datasetId} · ${payload.target_mode}`);
  } catch (error) {
    renderError(error);
    toast("Feature builder", error.message || String(error));
  } finally {
    setFeatureLoading(false);
  }
}

async function loadMetadata() {
  try {
    readControls();
    setFeatureLoading(true, "Loading metadata...");

    const query = `?dataset_kind=${encodeURIComponent(state.datasetKind)}`;
    const result = await api.featureMetadata(state.datasetId, query);
    renderResult(result);
  } catch (error) {
    renderError(error);
    toast("Feature metadata", error.message || String(error));
  } finally {
    setFeatureLoading(false);
  }
}

function bindEvents() {
  document.querySelector("#featureDataset").addEventListener("change", readControls);

  document.querySelector("[data-feature-action='build']").addEventListener("click", () => {
    buildFeatures();
  });

  document.querySelector("[data-feature-action='metadata']").addEventListener("click", () => {
    loadMetadata();
  });
}

export async function renderTraining() {
  state.datasets = await api.datasets();
  selectInitialDataset();

  window.setTimeout(bindEvents, 0);

  return `
    <section class="grid grid-2">
      <article class="card">
        <div class="viewer-section-header">
          <div>
            <h2>Feature Builder</h2>
            <p class="muted">
              Собирает model-ready features и targets для generated или imported dataset.
            </p>
          </div>
          <div class="status-pill status-ok" id="featureStatus">
            <span class="status-dot"></span>
            <span>Готов</span>
          </div>
        </div>

        <div class="form">
          <div class="grid grid-2">
            <div class="form-row">
              <label for="featureDataset">Dataset</label>
              <select class="select" id="featureDataset">
                ${datasetOptions(state.datasets)}
              </select>
            </div>

            <div class="form-row">
              <label for="featureTargetMode">target_mode</label>
              <select class="select" id="featureTargetMode">
                <option value="balanced">balanced</option>
                <option value="quality">quality</option>
                <option value="speed">speed</option>
                <option value="learning">learning</option>
                <option value="risk_aware">risk_aware</option>
              </select>
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

            <div class="form-row checkbox-row">
              <label>
                <input checked id="featureOverwrite" type="checkbox" />
                overwrite existing features
              </label>
            </div>
          </div>

          <div class="toolbar">
            <button class="button button-primary" data-feature-action="build" type="button">
              Build features
            </button>
            <button class="button button-secondary" data-feature-action="metadata" type="button">
              Load metadata
            </button>
          </div>
        </div>
      </article>

      <article class="card">
        <h2>Selected dataset</h2>
        <pre class="code">${prettyJson(selectedDataset() || {})}</pre>
      </article>
    </section>

    <section id="featureResult" style="margin-top: 16px;">
      <article class="card">
        <h2>Training stage</h2>
        <p class="muted">
          Сейчас готов feature builder. Multi-model training будет подключён на следующем этапе.
        </p>
      </article>
    </section>
  `;
}