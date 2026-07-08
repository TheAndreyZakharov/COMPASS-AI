import { api } from "../api.js";
import {
  getLastDatasetId,
  htmlEscape,
  prettyJson,
  setLastDatasetId,
  toast,
} from "../app.js";
import {
  countByField,
  renderBarChart,
  renderSummaryCards,
} from "../components/charts.js";
import { renderKanbanBoard } from "../components/kanban.js";
import {
  preferredColumnsForTable,
  renderDataTable,
  renderPagination,
} from "../components/table.js";

const TABLES = ["employees", "tasks", "assignment_history", "training_pairs"];

const state = {
  datasets: null,
  datasetId: "",
  datasetKind: "generated",
  tableName: "employees",
  page: 1,
  pageSize: 25,
  search: "",
  filters: {
    status: "",
    role: "",
    grade: "",
    project_id: "",
    priority: "",
  },
};

function allDatasets(datasetsPayload) {
  return [
    ...(datasetsPayload?.generated || []).map((item) => ({
      ...item,
      dataset_kind: "generated",
    })),
    ...(datasetsPayload?.imported || []).map((item) => ({
      ...item,
      dataset_kind: "imported",
    })),
  ];
}

function datasetOptionValue(dataset) {
  return `${dataset.dataset_kind}:${dataset.dataset_id}`;
}

function parseDatasetOptionValue(value) {
  const [datasetKind, ...datasetIdParts] = value.split(":");
  const datasetId = datasetIdParts.join(":");

  return {
    datasetId,
    datasetKind: datasetKind || "generated",
  };
}

function datasetOptions(datasetsPayload) {
  const datasets = allDatasets(datasetsPayload);

  if (datasets.length === 0) {
    return '<option value="">Нет datasets</option>';
  }

  return datasets
    .map((dataset) => {
      const isSelected =
        dataset.dataset_id === state.datasetId &&
        dataset.dataset_kind === state.datasetKind;
      const selected = isSelected ? "selected" : "";
      const kind = dataset.dataset_kind || dataset.dataset_type || "dataset";

      return `
        <option value="${htmlEscape(datasetOptionValue(dataset))}" ${selected}>
          ${htmlEscape(dataset.dataset_id)} · ${htmlEscape(kind)}
        </option>
      `;
    })
    .join("");
}

function tableOptions() {
  return TABLES.map((tableName) => {
    const selected = tableName === state.tableName ? "selected" : "";
    return `<option value="${tableName}" ${selected}>${tableName}</option>`;
  }).join("");
}

function selectedDatasetDescriptor() {
  const datasets = allDatasets(state.datasets);

  return (
    datasets.find(
      (dataset) =>
        dataset.dataset_id === state.datasetId &&
        dataset.dataset_kind === state.datasetKind,
    ) ||
    datasets.find((dataset) => dataset.dataset_id === state.datasetId) ||
    null
  );
}

function selectedDatasetKind() {
  return selectedDatasetDescriptor()?.dataset_kind || state.datasetKind || "generated";
}

function datasetKindQuery() {
  return `?dataset_kind=${encodeURIComponent(selectedDatasetKind())}`;
}

function buildQuery() {
  const params = new URLSearchParams();
  params.set("dataset_kind", selectedDatasetKind());
  params.set("page", String(state.page));
  params.set("page_size", String(state.pageSize));

  if (state.search) {
    params.set("search", state.search);
  }

  Object.entries(state.filters).forEach(([name, value]) => {
    if (value) {
      params.set(name, value);
    }
  });

  return `?${params.toString()}`;
}

function setSelectedDataset(dataset) {
  if (!dataset) {
    state.datasetId = "";
    state.datasetKind = "generated";
    return;
  }

  state.datasetId = dataset.dataset_id;
  state.datasetKind = dataset.dataset_kind || dataset.dataset_type || "generated";
}

function selectInitialDataset() {
  const datasets = allDatasets(state.datasets);
  const lastDatasetId = getLastDatasetId();

  if (state.datasetId) {
    const existing = datasets.find(
      (dataset) =>
        dataset.dataset_id === state.datasetId &&
        dataset.dataset_kind === state.datasetKind,
    );

    if (existing) {
      setSelectedDataset(existing);
      return;
    }
  }

  const lastDataset = datasets.find((dataset) => dataset.dataset_id === lastDatasetId);
  setSelectedDataset(lastDataset || datasets[0] || null);
}

function readControls() {
  const datasetValue = document.querySelector("#viewerDataset").value;
  const parsedDataset = parseDatasetOptionValue(datasetValue);

  state.datasetId = parsedDataset.datasetId;
  state.datasetKind = parsedDataset.datasetKind;
  state.tableName = document.querySelector("#viewerTable").value;
  state.pageSize = Number.parseInt(document.querySelector("#viewerPageSize").value, 10) || 25;
  state.search = document.querySelector("#viewerSearch").value.trim();
  state.filters = {
    status: document.querySelector("#viewerStatus").value.trim(),
    role: document.querySelector("#viewerRole").value.trim(),
    grade: document.querySelector("#viewerGrade").value.trim(),
    project_id: document.querySelector("#viewerProject").value.trim(),
    priority: document.querySelector("#viewerPriority").value.trim(),
  };

  if (state.datasetId) {
    setLastDatasetId(state.datasetId);
  }

  renderSelectedDatasetCard();
}

function setViewerLoading(isLoading, label = "Загрузка...") {
  const status = document.querySelector("#viewerStatusPill");
  const buttons = document.querySelectorAll("[data-viewer-action], [data-pagination-action]");

  buttons.forEach((button) => {
    button.disabled = isLoading;
    button.classList.toggle("loading", isLoading);
  });

  status.className = isLoading ? "status-pill status-pending" : "status-pill status-ok";
  status.innerHTML = isLoading
    ? `<span class="status-dot"></span><span>${htmlEscape(label)}</span>`
    : '<span class="status-dot"></span><span>Готов</span>';
}

function ensureDatasetSelected() {
  if (!state.datasetId) {
    throw new Error("Сначала выбери dataset.");
  }
}

function renderOutput(html) {
  document.querySelector("#viewerOutput").innerHTML = html;
}

function renderSelectedDatasetCard() {
  const element = document.querySelector("#viewerSelectedDatasetJson");

  if (!element) {
    return;
  }

  element.textContent = prettyJson(
    selectedDatasetDescriptor() || {
      dataset_id: state.datasetId || null,
      dataset_kind: state.datasetKind || null,
    },
  );
}

function renderError(error) {
  renderOutput(`
    <article class="card">
      <span class="badge">Error</span>
      <h2>Data Viewer error</h2>
      <p class="muted">${htmlEscape(error.message || error)}</p>
    </article>
  `);
}

async function loadDatasets() {
  setViewerLoading(true, "Datasets...");

  try {
    state.datasets = await api.datasets();
    selectInitialDataset();

    document.querySelector("#viewerDataset").innerHTML = datasetOptions(state.datasets);
    renderSelectedDatasetCard();
    renderDatasetList();
  } catch (error) {
    renderError(error);
  } finally {
    setViewerLoading(false);
  }
}

function renderDatasetList() {
  const datasets = allDatasets(state.datasets);

  if (datasets.length === 0) {
    renderOutput(`
      <article class="card">
        <h2>Datasets</h2>
        <p class="muted">Generated и imported datasets пока не найдены.</p>
      </article>
    `);
    return;
  }

  const rows = datasets.map((dataset) => ({
    dataset_id: dataset.dataset_id,
    kind: dataset.dataset_kind,
    domain_profile: dataset.domain_profile || "",
    dataset_mode: dataset.dataset_mode || "",
    employees: dataset.counts?.employees || 0,
    tasks: dataset.counts?.tasks || 0,
    training_pairs: dataset.counts?.training_pairs || 0,
    created_at: dataset.created_at || "",
  }));

  renderOutput(`
    <section class="grid grid-3">
      ${renderSummaryCards(state.datasets?.counts || {})}
    </section>

    <article class="card" style="margin-top: 16px;">
      <h2>Datasets</h2>
      ${renderDataTable(rows, [
        "dataset_id",
        "kind",
        "domain_profile",
        "dataset_mode",
        "employees",
        "tasks",
        "training_pairs",
        "created_at",
      ])}
    </article>
  `);
}

async function loadSummary() {
  ensureDatasetSelected();
  setViewerLoading(true, "Summary...");

  try {
    const summary = await api.datasetSummary(state.datasetId, datasetKindQuery());
    const counts = summary.summary_counts || summary.dataset?.counts || {};
    const metadata = summary.metadata || {};

    renderOutput(`
      <section class="grid grid-4">
        ${renderSummaryCards(counts)}
      </section>

      <section class="grid grid-2" style="margin-top: 16px;">
        ${renderBarChart("Table sizes", counts)}
        <article class="card">
          <h3>Dataset profile</h3>
          <pre class="code">${prettyJson(summary.dataset || {})}</pre>
        </article>
      </section>

      <article class="card" style="margin-top: 16px;">
        <h2>Metadata</h2>
        <pre class="code">${prettyJson(metadata)}</pre>
      </article>
    `);
  } catch (error) {
    renderError(error);
  } finally {
    setViewerLoading(false);
  }
}

async function loadTable() {
  ensureDatasetSelected();
  setViewerLoading(true, `${state.tableName}...`);

  try {
    const result = await api.datasetTable(state.datasetId, state.tableName, buildQuery());
    const columns = preferredColumnsForTable(state.tableName);
    const pagination = result.pagination || {};
    const items = result.items || [];

    renderOutput(`
      <article class="card">
        <div class="viewer-section-header">
          <div>
            <h2>${htmlEscape(state.tableName)}</h2>
            <p class="muted">
              ${htmlEscape(result.format || "table")} · ${htmlEscape(result.source || "")}
            </p>
          </div>
          <span class="badge">${htmlEscape(pagination.total || 0)} rows</span>
        </div>

        ${renderDataTable(items, columns)}
        ${renderPagination(pagination)}
      </article>
    `);

    bindPaginationEvents(pagination);
  } catch (error) {
    renderError(error);
  } finally {
    setViewerLoading(false);
  }
}

async function loadKanban() {
  ensureDatasetSelected();
  setViewerLoading(true, "Kanban...");

  try {
    const kanban = await api.kanban(state.datasetId, datasetKindQuery());
    const counts = kanban.counts || {};

    renderOutput(`
      <section class="grid grid-2">
        ${renderBarChart("Kanban counts", counts)}
        <article class="card">
          <h3>Kanban summary</h3>
          <pre class="code">${prettyJson({
            total: kanban.total,
            counts,
          })}</pre>
        </article>
      </section>

      <article class="card" style="margin-top: 16px;">
        <h2>Kanban board</h2>
        ${renderKanbanBoard(kanban)}
      </article>
    `);
  } catch (error) {
    renderError(error);
  } finally {
    setViewerLoading(false);
  }
}

async function loadCharts() {
  ensureDatasetSelected();
  setViewerLoading(true, "Charts...");

  try {
    const chartQuery =
      `?dataset_kind=${encodeURIComponent(selectedDatasetKind())}` +
      "&page=1&page_size=500";
    const tasks = await api.datasetTable(state.datasetId, "tasks", chartQuery);
    const employees = await api.datasetTable(state.datasetId, "employees", chartQuery);
    const taskRows = tasks.items || [];
    const employeeRows = employees.items || [];

    renderOutput(`
      <section class="grid grid-2">
        ${renderBarChart("Tasks by status", countByField(taskRows, "status"))}
        ${renderBarChart("Tasks by priority", countByField(taskRows, "priority"))}
        ${renderBarChart("Employees by role", countByField(employeeRows, "role"))}
        ${renderBarChart("Employees by grade", countByField(employeeRows, "grade"))}
      </section>
    `);
  } catch (error) {
    renderError(error);
  } finally {
    setViewerLoading(false);
  }
}

function bindPaginationEvents(pagination) {
  document.querySelectorAll("[data-pagination-action]").forEach((button) => {
    button.addEventListener("click", async () => {
      const action = button.dataset.paginationAction;

      if (action === "previous" && pagination.has_previous) {
        state.page = Math.max(1, state.page - 1);
      }

      if (action === "next" && pagination.has_next) {
        state.page += 1;
      }

      await loadTable();
    });
  });
}

function bindViewerEvents() {
  document.querySelector("#viewerDataset").addEventListener("change", () => {
    readControls();
    state.page = 1;
    renderDatasetList();
  });

  document.querySelector("#viewerTable").addEventListener("change", () => {
    readControls();
    state.page = 1;
  });

  document.querySelector("#viewerRefreshDatasets").addEventListener("click", loadDatasets);

  document.querySelectorAll("[data-viewer-action]").forEach((button) => {
    button.addEventListener("click", async () => {
      try {
        readControls();

        if (button.dataset.viewerAction !== "table") {
          state.page = 1;
        }

        const action = button.dataset.viewerAction;

        if (action === "datasets") {
          renderDatasetList();
        } else if (action === "summary") {
          await loadSummary();
        } else if (action === "table") {
          await loadTable();
        } else if (action === "kanban") {
          await loadKanban();
        } else if (action === "charts") {
          await loadCharts();
        }
      } catch (error) {
        renderError(error);
        toast("Data Viewer", error.message || String(error));
      }
    });
  });

  document.querySelector("#viewerClearFilters").addEventListener("click", () => {
    [
      "viewerSearch",
      "viewerStatus",
      "viewerRole",
      "viewerGrade",
      "viewerProject",
      "viewerPriority",
    ].forEach((id) => {
      document.querySelector(`#${id}`).value = "";
    });

    state.page = 1;
    readControls();
  });
}

export async function renderViewer() {
  state.datasets = await api.datasets();
  selectInitialDataset();

  window.setTimeout(() => {
    bindViewerEvents();
    renderSelectedDatasetCard();
    renderDatasetList();
  }, 0);

  return `
    <section class="grid grid-2">
      <article class="card">
        <div class="viewer-section-header">
          <div>
            <h2>Data Viewer</h2>
            <p class="muted">
              Просмотр generated и imported datasets без ручного открытия CSV, JSON или Parquet.
            </p>
          </div>
          <div class="status-pill status-ok" id="viewerStatusPill">
            <span class="status-dot"></span>
            <span>Готов</span>
          </div>
        </div>

        <div class="toolbar">
          <div class="form-row">
            <label for="viewerDataset">Dataset</label>
            <select class="select" id="viewerDataset">
              ${datasetOptions(state.datasets)}
            </select>
          </div>

          <div class="form-row">
            <label for="viewerTable">Table</label>
            <select class="select" id="viewerTable">${tableOptions()}</select>
          </div>

          <div class="form-row">
            <label for="viewerPageSize">Page size</label>
            <input
              class="input"
              id="viewerPageSize"
              min="1"
              max="500"
              type="number"
              value="25"
            />
          </div>

          <div class="form-row">
            <label for="viewerSearch">Search</label>
            <input class="input" id="viewerSearch" placeholder="Поиск..." type="search" />
          </div>
        </div>

        <div class="toolbar">
          <div class="form-row">
            <label for="viewerStatus">status</label>
            <input class="input" id="viewerStatus" placeholder="todo" type="text" />
          </div>

          <div class="form-row">
            <label for="viewerRole">role</label>
            <input class="input" id="viewerRole" placeholder="backend" type="text" />
          </div>

          <div class="form-row">
            <label for="viewerGrade">grade</label>
            <input class="input" id="viewerGrade" placeholder="middle" type="text" />
          </div>

          <div class="form-row">
            <label for="viewerProject">project_id</label>
            <input class="input" id="viewerProject" placeholder="project_001" type="text" />
          </div>

          <div class="form-row">
            <label for="viewerPriority">priority</label>
            <input class="input" id="viewerPriority" placeholder="high" type="text" />
          </div>
        </div>

        <div class="toolbar">
          <button class="button button-secondary" data-viewer-action="datasets" type="button">
            Datasets
          </button>
          <button class="button button-secondary" data-viewer-action="summary" type="button">
            Summary
          </button>
          <button class="button button-primary" data-viewer-action="table" type="button">
            Table
          </button>
          <button class="button button-secondary" data-viewer-action="charts" type="button">
            Charts
          </button>
          <button class="button button-secondary" data-viewer-action="kanban" type="button">
            Kanban
          </button>
          <button class="button button-secondary" id="viewerClearFilters" type="button">
            Clear filters
          </button>
          <button class="button button-secondary" id="viewerRefreshDatasets" type="button">
            Refresh datasets
          </button>
        </div>
      </article>

      <article class="card">
        <h2>Selected dataset</h2>
        <pre class="code" id="viewerSelectedDatasetJson">${prettyJson(
          selectedDatasetDescriptor() || {
            dataset_id: state.datasetId || null,
            dataset_kind: state.datasetKind || null,
          },
        )}</pre>
      </article>
    </section>

    <section id="viewerOutput" style="margin-top: 16px;">
      <article class="card">
        <h2>Datasets</h2>
        <p class="muted">Загрузка datasets...</p>
      </article>
    </section>
  `;
}