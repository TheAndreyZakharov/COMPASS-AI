import { api } from "../api.js";
import { getLastDatasetId, htmlEscape, prettyJson, tableFromRows, toast } from "../app.js";

const TABLES = ["employees", "tasks", "assignment_history", "training_pairs"];

function datasetOptions(datasets, selectedDatasetId) {
  const allDatasets = [...(datasets.generated || []), ...(datasets.imported || [])];

  if (allDatasets.length === 0) {
    return '<option value="">Нет datasets</option>';
  }

  return allDatasets
    .map((dataset) => {
      const selected = dataset.dataset_id === selectedDatasetId ? "selected" : "";
      return `<option value="${htmlEscape(dataset.dataset_id)}" ${selected}>${htmlEscape(
        dataset.dataset_id,
      )}</option>`;
    })
    .join("");
}

function bindViewerEvents() {
  const loadButton = document.querySelector("#loadViewerTable");
  const summaryButton = document.querySelector("#loadViewerSummary");
  const kanbanButton = document.querySelector("#loadViewerKanban");

  async function loadTable() {
    const datasetId = document.querySelector("#viewerDataset").value;
    const tableName = document.querySelector("#viewerTable").value;
    const pageSize = document.querySelector("#viewerPageSize").value;
    const search = encodeURIComponent(document.querySelector("#viewerSearch").value.trim());
    const output = document.querySelector("#viewerOutput");

    if (!datasetId) {
      toast("Data Viewer", "Сначала выбери dataset.");
      return;
    }

    const query = `?page=1&page_size=${pageSize}${search ? `&search=${search}` : ""}`;
    const result = await api.datasetTable(datasetId, tableName, query);
    output.innerHTML = `
      <h2>${htmlEscape(tableName)}</h2>
      ${tableFromRows(result.items)}
      <pre class="code">${prettyJson(result.pagination)}</pre>
    `;
  }

  async function loadSummary() {
    const datasetId = document.querySelector("#viewerDataset").value;
    const output = document.querySelector("#viewerOutput");

    if (!datasetId) {
      toast("Data Viewer", "Сначала выбери dataset.");
      return;
    }

    const result = await api.datasetSummary(datasetId);
    output.innerHTML = `<h2>Summary</h2><pre class="code">${prettyJson(result)}</pre>`;
  }

  async function loadKanban() {
    const datasetId = document.querySelector("#viewerDataset").value;
    const output = document.querySelector("#viewerOutput");

    if (!datasetId) {
      toast("Data Viewer", "Сначала выбери dataset.");
      return;
    }

    const result = await api.kanban(datasetId);
    const columns = Object.entries(result.columns || {})
      .map(([status, tasks]) => {
        const cards = tasks
          .slice(0, 20)
          .map(
            (task) => `
              <div class="kanban-card">
                <strong>${htmlEscape(task.task_id)}</strong>
                <p class="muted">${htmlEscape(task.title || task.description || "")}</p>
              </div>
            `,
          )
          .join("");

        return `
          <section class="kanban-column">
            <h3>${htmlEscape(status)} <span>${tasks.length}</span></h3>
            ${cards || '<p class="muted">Нет задач</p>'}
          </section>
        `;
      })
      .join("");

    output.innerHTML = `<h2>Kanban</h2><div class="kanban">${columns}</div>`;
  }

  loadButton.addEventListener("click", () => loadTable().catch((error) => toast("Ошибка", error.message)));
  summaryButton.addEventListener("click", () => loadSummary().catch((error) => toast("Ошибка", error.message)));
  kanbanButton.addEventListener("click", () => loadKanban().catch((error) => toast("Ошибка", error.message)));
}

export async function renderViewer() {
  const datasets = await api.datasets();
  const selectedDatasetId = getLastDatasetId();

  window.setTimeout(bindViewerEvents, 0);

  return `
    <article class="card">
      <div class="toolbar">
        <div class="form-row">
          <label for="viewerDataset">Dataset</label>
          <select class="select" id="viewerDataset">
            ${datasetOptions(datasets, selectedDatasetId)}
          </select>
        </div>
        <div class="form-row">
          <label for="viewerTable">Table</label>
          <select class="select" id="viewerTable">
            ${TABLES.map((table) => `<option value="${table}">${table}</option>`).join("")}
          </select>
        </div>
        <div class="form-row">
          <label for="viewerPageSize">Page size</label>
          <input class="input" id="viewerPageSize" min="1" max="500" type="number" value="25" />
        </div>
        <div class="form-row">
          <label for="viewerSearch">Search</label>
          <input class="input" id="viewerSearch" placeholder="Поиск..." type="search" />
        </div>
        <button class="button button-primary" id="loadViewerTable" type="button">Table</button>
        <button class="button button-secondary" id="loadViewerSummary" type="button">Summary</button>
        <button class="button button-secondary" id="loadViewerKanban" type="button">Kanban</button>
      </div>
    </article>

    <article class="card" id="viewerOutput" style="margin-top: 16px;">
      <h2>Datasets</h2>
      <pre class="code">${prettyJson(datasets)}</pre>
    </article>
  `;
}