import { api } from "../api.js";
import {
  getLastDatasetId,
  htmlEscape,
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
  viewMode: "datasets",
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
    return '<option value="">Нет датасетов</option>';
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
    return `<option value="${tableName}" ${selected}>${tableLabel(tableName)}</option>`;
  }).join("");
}

function tableLabel(tableName) {
  return {
    employees: "Сотрудники",
    tasks: "Задачи",
    assignment_history: "История выполнений",
    training_pairs: "Пары для обучения",
  }[tableName] || tableName;
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

function setActiveViewerAction(action) {
  state.viewMode = action;
  document.querySelectorAll("[data-viewer-action]").forEach((button) => {
    const active = button.dataset.viewerAction === action;
    button.classList.toggle("button-primary", active);
    button.classList.toggle("button-secondary", !active);
    button.classList.toggle("active", active);
    button.setAttribute("aria-pressed", active ? "true" : "false");
  });
}

function ensureDatasetSelected() {
  if (!state.datasetId) {
    throw new Error("Сначала выберите датасет.");
  }
}

function renderOutput(html) {
  document.querySelector("#viewerOutput").innerHTML = html;
}

function renderError(error) {
  renderOutput(`
    <article class="card">
      <span class="badge">Ошибка</span>
      <h2>Не удалось открыть данные</h2>
      <p class="muted">${htmlEscape(error.message || error)}</p>
    </article>
  `);
}

async function loadDatasets() {
  setViewerLoading(true, "Датасеты...");

  try {
    state.datasets = await api.datasets();
    selectInitialDataset();

    document.querySelector("#viewerDataset").innerHTML = datasetOptions(state.datasets);
    renderDatasetList();
  } catch (error) {
    renderError(error);
  } finally {
    setViewerLoading(false);
  }
}

function renderDatasetList() {
  setActiveViewerAction("datasets");
  const datasets = allDatasets(state.datasets);

  if (datasets.length === 0) {
    renderOutput(`
      <article class="card">
        <h2>Датасеты</h2>
        <p class="muted">Датасетов пока нет. Создайте данные или импортируйте свои файлы.</p>
        <div class="toolbar">
          <a class="button button-primary" href="/generator" data-link>Создать данные</a>
          <a class="button button-secondary" href="/import-data" data-link>Импортировать файлы</a>
        </div>
      </article>
    `);
    return;
  }

  const rows = datasets.map((dataset) => ({
    "Датасет": dataset.dataset_id,
    "Тип": dataset.dataset_kind === "generated" ? "созданный" : "импортированный",
    "Профиль": dataset.domain_profile || "",
    "Размер": dataset.dataset_mode || "",
    "Сотрудники": dataset.counts?.employees || 0,
    "Задачи": dataset.counts?.tasks || 0,
    "Пары для обучения": dataset.counts?.training_pairs || 0,
    "Создан": dataset.created_at || "",
  }));

  renderOutput(`
    <section class="grid grid-3">
      ${renderSummaryCards(state.datasets?.counts || {})}
    </section>

    <article class="card" style="margin-top: 16px;">
      <h2>Датасеты</h2>
      ${renderDataTable(rows, [
        "Датасет",
        "Тип",
        "Профиль",
        "Размер",
        "Сотрудники",
        "Задачи",
        "Пары для обучения",
        "Создан",
      ])}
    </article>
  `);
}

async function loadSummary() {
  ensureDatasetSelected();
  setActiveViewerAction("summary");
  setViewerLoading(true, "Сводка...");

  try {
    const summary = await api.datasetSummary(state.datasetId, datasetKindQuery());
    const counts = summary.summary_counts || summary.dataset?.counts || {};
    const dataset = summary.dataset || {};

    renderOutput(`
      <section class="grid grid-4">
        ${renderSummaryCards(counts)}
      </section>

      <section class="grid grid-2" style="margin-top: 16px;">
        ${renderBarChart("Размер таблиц", counts)}
        <article class="card">
          <h3>Профиль датасета</h3>
          <div class="info-list">
            <p><strong>ID:</strong> ${htmlEscape(dataset.dataset_id || state.datasetId)}</p>
            <p><strong>Тип:</strong> ${htmlEscape(dataset.dataset_kind || state.datasetKind)}</p>
            <p><strong>Домен:</strong> ${htmlEscape(dataset.domain_profile || "не указан")}</p>
            <p><strong>Режим:</strong> ${htmlEscape(dataset.dataset_mode || "не указан")}</p>
          </div>
        </article>
      </section>
    `);
  } catch (error) {
    renderError(error);
  } finally {
    setViewerLoading(false);
  }
}

async function loadTable() {
  ensureDatasetSelected();
  setActiveViewerAction("table");
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
            <h2>${htmlEscape(tableLabel(state.tableName))}</h2>
            <p class="muted">
              ${htmlEscape(result.format || "table")} · ${htmlEscape(result.source || "")}
            </p>
          </div>
          <span class="badge">${htmlEscape(pagination.total || 0)} строк</span>
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
  setActiveViewerAction("kanban");
  setViewerLoading(true, "Канбан...");

  try {
    const kanban = await api.kanban(state.datasetId, datasetKindQuery());
    const counts = kanban.counts || {};

    renderOutput(`
      <section class="grid grid-2">
        ${renderBarChart("Статусы задач", counts)}
        <article class="card">
          <h3>Сводка по задачам</h3>
          <p><strong>${htmlEscape(kanban.total || 0)}</strong> задач всего</p>
          <p class="muted">Ниже показано распределение по статусам.</p>
        </article>
      </section>

      <article class="card" style="margin-top: 16px;">
        <h2>Канбан задач</h2>
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
  setActiveViewerAction("charts");
  setViewerLoading(true, "Графики...");

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
        ${renderBarChart("Задачи по статусам", countByField(taskRows, "status"))}
        ${renderBarChart("Задачи по приоритетам", countByField(taskRows, "priority"))}
        ${renderBarChart("Сотрудники по ролям", countByField(employeeRows, "role"))}
        ${renderBarChart("Сотрудники по уровням", countByField(employeeRows, "grade"))}
      </section>
    `);
  } catch (error) {
    renderError(error);
  } finally {
    setViewerLoading(false);
  }
}

async function deleteSelectedDataset() {
  readControls();
  ensureDatasetSelected();

  const confirmed = window.confirm(
    `Удалить датасет "${state.datasetId}" (${selectedDatasetKind()})? Это удалит его файлы.`,
  );

  if (!confirmed) {
    return;
  }

  setViewerLoading(true, "Удаление датасета...");

  try {
    await api.deleteDataset(state.datasetId, selectedDatasetKind());
    if (getLastDatasetId() === state.datasetId) {
      setLastDatasetId("");
    }
    state.datasetId = "";
    state.page = 1;
    state.datasets = await api.datasets();
    selectInitialDataset();
    document.querySelector("#viewerDataset").innerHTML = datasetOptions(state.datasets);
    renderDatasetList();
    toast("Датасет удален", "Файлы удалены из sandbox_app.");
  } catch (error) {
    renderError(error);
    toast("Просмотр данных", error.message || String(error));
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
  document.querySelector("#viewerDeleteDataset").addEventListener("click", deleteSelectedDataset);

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
        toast("Просмотр данных", error.message || String(error));
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
    renderDatasetList();
  }, 0);

  return `
    <section class="grid">
      <article class="card">
        <div class="viewer-section-header">
          <div>
            <h2>Просмотр данных</h2>
            <p class="muted">
              Выберите датасет, таблицу и режим просмотра. Данные можно искать,
              фильтровать и проверять без открытия файлов.
            </p>
          </div>
          <div class="status-pill status-ok" id="viewerStatusPill">
            <span class="status-dot"></span>
            <span>Готов</span>
          </div>
        </div>

        <div class="toolbar">
          <div class="form-row">
            <label for="viewerDataset">Датасет</label>
            <select class="select" id="viewerDataset">
              ${datasetOptions(state.datasets)}
            </select>
          </div>

          <div class="form-row">
            <label for="viewerTable">Таблица</label>
            <select class="select" id="viewerTable">${tableOptions()}</select>
          </div>

          <div class="form-row">
            <label for="viewerPageSize">Строк на странице</label>
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
            <label for="viewerSearch">Поиск</label>
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
          <button
            class="button ${state.viewMode === "datasets" ? "button-primary active" : "button-secondary"}"
            data-viewer-action="datasets"
            type="button"
            aria-pressed="${state.viewMode === "datasets" ? "true" : "false"}"
          >
            Датасеты
          </button>
          <button
            class="button ${state.viewMode === "summary" ? "button-primary active" : "button-secondary"}"
            data-viewer-action="summary"
            type="button"
            aria-pressed="${state.viewMode === "summary" ? "true" : "false"}"
          >
            Сводка
          </button>
          <button
            class="button ${state.viewMode === "table" ? "button-primary active" : "button-secondary"}"
            data-viewer-action="table"
            type="button"
            aria-pressed="${state.viewMode === "table" ? "true" : "false"}"
          >
            Таблица
          </button>
          <button
            class="button ${state.viewMode === "charts" ? "button-primary active" : "button-secondary"}"
            data-viewer-action="charts"
            type="button"
            aria-pressed="${state.viewMode === "charts" ? "true" : "false"}"
          >
            Графики
          </button>
          <button
            class="button ${state.viewMode === "kanban" ? "button-primary active" : "button-secondary"}"
            data-viewer-action="kanban"
            type="button"
            aria-pressed="${state.viewMode === "kanban" ? "true" : "false"}"
          >
            Канбан
          </button>
          <button class="button button-secondary" id="viewerClearFilters" type="button">
            Очистить фильтры
          </button>
          <button class="button button-secondary" id="viewerRefreshDatasets" type="button">
            Обновить список
          </button>
          <button class="button button-danger" id="viewerDeleteDataset" type="button">
            Удалить датасет
          </button>
        </div>
      </article>
    </section>

    <section id="viewerOutput" style="margin-top: 16px;">
      <article class="card">
        <h2>Датасеты</h2>
        <p class="muted">Загрузка датасетов...</p>
      </article>
    </section>
  `;
}
