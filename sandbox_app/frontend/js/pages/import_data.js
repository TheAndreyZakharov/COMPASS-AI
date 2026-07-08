import { api } from "../api.js";
import { htmlEscape, prettyJson, setLastDatasetId, toast } from "../app.js";
import { renderDataTable } from "../components/table.js";

const TABLES = ["employees", "tasks", "assignment_history", "training_pairs"];

function selectedFile(tableName) {
  return document.querySelector(`#importFile_${tableName}`)?.files?.[0] || null;
}

function extensionFromFile(file) {
  const parts = file.name.split(".");
  return parts.length > 1 ? parts.at(-1).toLowerCase() : "json";
}

function renamedFile(file, tableName) {
  const extension = extensionFromFile(file);
  return new File([file], `${tableName}.${extension}`, {
    type: file.type || "application/octet-stream",
  });
}

function buildDatasetFormData() {
  const formData = new FormData();
  const tableNames = [];

  formData.append("dataset_id", document.querySelector("#importDatasetId").value.trim());
  formData.append("domain_profile", document.querySelector("#importDomainProfile").value.trim());
  formData.append("overwrite", String(document.querySelector("#importOverwrite").checked));

  TABLES.forEach((tableName) => {
    const file = selectedFile(tableName);
    if (!file) {
      return;
    }

    tableNames.push(tableName);
    formData.append("files", renamedFile(file, tableName));
  });

  formData.append("table_names", JSON.stringify(tableNames));
  return formData;
}

function buildPreviewFormData(tableName) {
  const file = selectedFile(tableName);
  if (!file) {
    throw new Error(`Выбери файл для ${tableName}`);
  }

  const formData = new FormData();
  formData.append("table_name", tableName);
  formData.append("file", renamedFile(file, tableName));
  return formData;
}

function setImportLoading(isLoading, label = "Импорт...") {
  const status = document.querySelector("#importStatus");
  const buttons = document.querySelectorAll("[data-import-action], [data-preview-table]");

  buttons.forEach((button) => {
    button.disabled = isLoading;
    button.classList.toggle("loading", isLoading);
  });

  status.className = isLoading ? "status-pill status-pending" : "status-pill status-ok";
  status.innerHTML = isLoading
    ? `<span class="status-dot"></span><span>${htmlEscape(label)}</span>`
    : '<span class="status-dot"></span><span>Готов</span>';
}

function renderValidationBlocks(result) {
  const errors = result.validation_errors || [];
  const warnings = result.warnings || [];

  if (errors.length === 0 && warnings.length === 0) {
    return `
      <article class="card">
        <h3>Validation</h3>
        <p class="muted">Ошибок и предупреждений нет.</p>
      </article>
    `;
  }

  return `
    <section class="grid grid-2">
      <article class="card">
        <h3>Schema errors</h3>
        ${renderDataTable(errors)}
      </article>
      <article class="card">
        <h3>Warnings</h3>
        <pre class="code">${prettyJson(warnings)}</pre>
      </article>
    </section>
  `;
}

function renderPreview(result) {
  const preview = result.preview || [];
  const rows = Array.isArray(preview) ? preview : Object.values(preview).flat();

  document.querySelector("#importResult").innerHTML = `
    <article class="card">
      <h2>Preview: ${htmlEscape(result.table_name || "table")}</h2>
      <p class="muted">
        ${htmlEscape(result.filename || "")} · ${htmlEscape(result.format || "")} ·
        rows: ${htmlEscape(result.rows || 0)}
      </p>
      ${renderDataTable(rows)}
    </article>

    <section style="margin-top: 16px;">
      ${renderValidationBlocks(result)}
    </section>

    <article class="card" style="margin-top: 16px;">
      <h3>Raw preview response</h3>
      <pre class="code">${prettyJson(result)}</pre>
    </article>
  `;
}

function renderImportResult(result) {
  const datasetId = result.dataset_id || "";
  if (datasetId && result.status === "imported") {
    setLastDatasetId(datasetId);
  }

  const openViewerButton =
    result.status === "imported"
      ? '<button class="button button-primary" id="openImportedDataset" type="button">Открыть в Data Viewer</button>'
      : "";

  document.querySelector("#importResult").innerHTML = `
    <section class="grid grid-3">
      <article class="card">
        <h2>Status</h2>
        <p><strong>${htmlEscape(result.status || "unknown")}</strong></p>
        <p class="muted">${htmlEscape(result.dataset_id || "")}</p>
      </article>
      <article class="card">
        <h2>Dataset dir</h2>
        <p class="muted">${htmlEscape(result.dataset_dir || "")}</p>
      </article>
      <article class="card">
        <h2>Next step</h2>
        ${openViewerButton || '<p class="muted">Исправь validation errors и повтори импорт.</p>'}
      </article>
    </section>

    <section style="margin-top: 16px;">
      ${renderValidationBlocks(result)}
    </section>

    <article class="card" style="margin-top: 16px;">
      <h2>Imported tables</h2>
      ${renderDataTable(result.tables || [])}
    </article>

    <article class="card" style="margin-top: 16px;">
      <h2>Raw import response</h2>
      <pre class="code">${prettyJson(result)}</pre>
    </article>
  `;

  const openButton = document.querySelector("#openImportedDataset");
  if (openButton) {
    openButton.addEventListener("click", () => {
      window.history.pushState({}, "", "/viewer");
      window.dispatchEvent(new PopStateEvent("popstate"));
    });
  }
}

function renderImportError(error) {
  document.querySelector("#importResult").innerHTML = `
    <article class="card">
      <span class="badge">Error</span>
      <h2>Import failed</h2>
      <p class="muted">${htmlEscape(error.message || String(error))}</p>
    </article>
  `;
}

async function runPreview(tableName) {
  try {
    setImportLoading(true, `Preview ${tableName}...`);
    const result = await api.importPreview(buildPreviewFormData(tableName));
    renderPreview(result);
  } catch (error) {
    renderImportError(error);
    toast("Preview error", error.message || String(error));
  } finally {
    setImportLoading(false);
  }
}

async function runImport() {
  try {
    setImportLoading(true, "Import dataset...");
    const result = await api.importDataset(buildDatasetFormData());
    renderImportResult(result);

    if (result.status === "imported") {
      toast("Dataset imported", result.dataset_id);
    } else {
      toast("Validation failed", "Исправь schema errors и повтори импорт.");
    }
  } catch (error) {
    renderImportError(error);
    toast("Import error", error.message || String(error));
  } finally {
    setImportLoading(false);
  }
}

function fileInputRow(tableName) {
  return `
    <div class="import-file-row">
      <div>
        <strong>${htmlEscape(tableName)}</strong>
        <p class="muted">CSV, JSON или Parquet</p>
      </div>
      <input
        class="input"
        id="importFile_${tableName}"
        accept=".csv,.json,.parquet"
        type="file"
      />
      <button
        class="button button-secondary"
        data-preview-table="${htmlEscape(tableName)}"
        type="button"
      >
        Preview
      </button>
    </div>
  `;
}

function bindImportEvents() {
  document.querySelectorAll("[data-preview-table]").forEach((button) => {
    button.addEventListener("click", () => runPreview(button.dataset.previewTable));
  });

  document.querySelector("[data-import-action='dataset']").addEventListener("click", runImport);
}

export async function renderImportData() {
  const supported = await api.importSupportedTables();

  window.setTimeout(bindImportEvents, 0);

  return `
    <section class="grid grid-2">
      <article class="card">
        <div class="viewer-section-header">
          <div>
            <h2>Import external dataset</h2>
            <p class="muted">
              Импортирует external CSV, JSON и Parquet в sandbox_app/data/imported.
            </p>
          </div>
          <div class="status-pill status-ok" id="importStatus">
            <span class="status-dot"></span>
            <span>Готов</span>
          </div>
        </div>

        <div class="form">
          <div class="grid grid-2">
            <div class="form-row">
              <label for="importDatasetId">dataset_id</label>
              <input class="input" id="importDatasetId" type="text" value="ui_imported_dataset" />
            </div>

            <div class="form-row">
              <label for="importDomainProfile">domain_profile</label>
              <input class="input" id="importDomainProfile" type="text" value="custom" />
            </div>

            <div class="form-row checkbox-row">
              <label>
                <input id="importOverwrite" type="checkbox" />
                overwrite existing imported dataset
              </label>
            </div>
          </div>

          <div class="import-file-list">
            ${TABLES.map(fileInputRow).join("")}
          </div>

          <div class="toolbar">
            <button class="button button-primary" data-import-action="dataset" type="button">
              Import dataset
            </button>
          </div>
        </div>
      </article>

      <article class="card">
        <h2>Supported import contract</h2>
        <pre class="code">${prettyJson(supported)}</pre>
      </article>
    </section>

    <section id="importResult" style="margin-top: 16px;">
      <article class="card">
        <h2>Result</h2>
        <p class="muted">
          Выбери файлы, запусти Preview для проверки или Import dataset для сохранения.
        </p>
      </article>
    </section>
  `;
}