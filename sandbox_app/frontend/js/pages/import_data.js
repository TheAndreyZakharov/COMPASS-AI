import { api } from "../api.js";
import { htmlEscape, setLastDatasetId, toast } from "../app.js";
import { renderDataTable } from "../components/table.js";

const TABLES = ["employees", "tasks", "assignment_history", "training_pairs"];

function startLongTaskToast(options) {
  const detail = { options, controller: null };
  window.dispatchEvent(new CustomEvent("sandbox-long-task-start", { detail }));

  return detail.controller || {
    update() {},
    done(message = "Готово") {
      toast(options?.title || "Импорт данных", message);
    },
    error(message = "Ошибка") {
      toast(options?.title || "Импорт данных", message);
    },
  };
}

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
    throw new Error(`Выберите файл для ${tableName}`);
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

  if (!status) {
    return;
  }

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
        <h3>Проверка</h3>
        <p class="muted">Ошибок и предупреждений нет.</p>
      </article>
    `;
  }

  return `
    <section class="grid grid-2">
      <article class="card">
        <h3>Ошибки структуры</h3>
        ${renderDataTable(errors)}
      </article>
      <article class="card">
        <h3>Предупреждения</h3>
        ${renderDataTable(warnings.map((warning) => ({ warning })))}
      </article>
    </section>
  `;
}

function renderPreview(result) {
  const preview = result.preview || [];
  const rows = Array.isArray(preview) ? preview : Object.values(preview).flat();
  const resultContainer = document.querySelector("#importResult");

  if (!resultContainer) {
    return;
  }

  resultContainer.innerHTML = `
    <article class="card">
      <h2>Предпросмотр: ${htmlEscape(result.table_name || "таблица")}</h2>
      <p class="muted">
        ${htmlEscape(result.filename || "")} · ${htmlEscape(result.format || "")} ·
        rows: ${htmlEscape(result.rows || 0)}
      </p>
      ${renderDataTable(rows)}
    </article>

    <section style="margin-top: 16px;">
      ${renderValidationBlocks(result)}
    </section>
  `;
}

function renderImportResult(result) {
  const datasetId = result.dataset_id || "";
  if (datasetId && result.status === "imported") {
    setLastDatasetId(datasetId);
  }

  const openViewerButton =
    result.status === "imported"
      ? '<button class="button button-primary" id="openImportedDataset" type="button">Открыть в просмотре данных</button>'
      : "";
  const resultContainer = document.querySelector("#importResult");

  if (!resultContainer) {
    return;
  }

  resultContainer.innerHTML = `
    <section class="grid grid-3">
      <article class="card">
        <h2>Статус</h2>
        <p><strong>${result.status === "imported" ? "Импортировано" : "Требуется проверка"}</strong></p>
        <p class="muted">${htmlEscape(result.dataset_id || "")}</p>
      </article>
      <article class="card">
        <h2>Таблицы</h2>
        <p><strong>${htmlEscape((result.tables || []).length)}</strong></p>
        <p class="muted">файлов принято</p>
      </article>
      <article class="card">
        <h2>Следующий шаг</h2>
        ${openViewerButton || '<p class="muted">Исправьте ошибки проверки и повторите импорт.</p>'}
      </article>
    </section>

    <section style="margin-top: 16px;">
      ${renderValidationBlocks(result)}
    </section>

    <article class="card" style="margin-top: 16px;">
      <h2>Импортированные таблицы</h2>
      ${renderDataTable(result.tables || [])}
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
  const resultContainer = document.querySelector("#importResult");

  if (!resultContainer) {
    return;
  }

  resultContainer.innerHTML = `
    <article class="card">
      <span class="badge">Ошибка</span>
      <h2>Импорт не выполнен</h2>
      <p class="muted">${htmlEscape(error.message || String(error))}</p>
    </article>
  `;
}

async function runPreview(tableName) {
  try {
    setImportLoading(true, `Предпросмотр ${tableName}...`);
    const result = await api.importPreview(buildPreviewFormData(tableName));
    renderPreview(result);
  } catch (error) {
    renderImportError(error);
    toast("Ошибка предпросмотра", error.message || String(error));
  } finally {
    setImportLoading(false);
  }
}

async function runImport() {
  const progress = startLongTaskToast({
    title: "Импортируем файлы...",
    message: "Проверяем таблицы...",
    steps: ["Проверяем таблицы...", "Импортируем файлы...", "Сохраняем датасет..."],
  });

  try {
    setImportLoading(true, "Импортируем датасет...");
    progress.update({ message: "Импортируем файлы...", percent: 32, stepIndex: 1 });
    const result = await api.importDataset(buildDatasetFormData());
    progress.update({ message: "Сохраняем датасет...", percent: 94, stepIndex: 2 });

    if (result.status === "imported") {
      progress.done("Готово");
      renderImportResult(result);
      toast("Датасет импортирован", result.dataset_id);
    } else {
      progress.error("Проверка не пройдена");
      renderImportResult(result);
      toast("Проверка не пройдена", "Исправьте ошибки структуры и повторите импорт.");
    }
  } catch (error) {
    progress.error(error.message || String(error));
    renderImportError(error);
    toast("Ошибка импорта", error.message || String(error));
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
        Предпросмотр
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
  window.setTimeout(bindImportEvents, 0);

  return `
    <section class="grid">
      <article class="card">
        <div class="viewer-section-header">
          <div>
            <h2>Импорт своих данных</h2>
            <p class="muted">
              Загрузите свои таблицы вместо синтетической генерации. Сначала можно
              проверить файл через предпросмотр, затем сохранить датасет.
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
              <label for="importDatasetId">ID датасета</label>
              <input class="input" id="importDatasetId" type="text" value="ui_imported_dataset" />
            </div>

            <div class="form-row">
              <label for="importDomainProfile">Профиль предметной области</label>
              <input class="input" id="importDomainProfile" type="text" value="custom" />
            </div>

            <div class="form-row checkbox-row">
              <label>
                <input id="importOverwrite" type="checkbox" />
                заменить существующий импортированный датасет
              </label>
            </div>
          </div>

          <div class="import-file-list">
            ${TABLES.map(fileInputRow).join("")}
          </div>

          <div class="toolbar">
            <button class="button button-primary" data-import-action="dataset" type="button">
              Импортировать датасет
            </button>
          </div>
        </div>
      </article>
    </section>

    <section id="importResult" style="margin-top: 16px;">
      <article class="card">
        <h2>Результат</h2>
        <p class="muted">
          Выберите файлы, нажмите «Предпросмотр» для проверки или «Импортировать датасет» для сохранения.
        </p>
      </article>
    </section>
  `;
}
