import { api } from "../api.js";

const state = {
  datasets: [],
  trainingSessions: [],
  assignmentSessions: [],
  exportReports: [],
  selectedDatasetId: "",
  selectedDatasetKind: "generated",
  selectedTrainingSessionId: "",
  selectedAssignmentSessionId: "",
  selectedReportId: "",
  selectedReport: null,
  error: "",
};

function htmlEscape(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function toast(title, message = "") {
  window.dispatchEvent(
    new CustomEvent("sandbox-toast", {
      detail: {
        title,
        message,
      },
    }),
  );
}

function startLongTaskToast(options) {
  const detail = { options, controller: null };
  window.dispatchEvent(new CustomEvent("sandbox-long-task-start", { detail }));

  return detail.controller || {
    update() {},
    done(message = "Готово") {
      toast(options?.title || "Отчеты", message);
    },
    error(message = "Ошибка") {
      toast(options?.title || "Отчеты", message);
    },
  };
}

function option(value, label, selected) {
  return `
    <option value="${htmlEscape(value)}" ${value === selected ? "selected" : ""}>
      ${htmlEscape(label)}
    </option>
  `;
}

function selectedValue(id) {
  const element = document.querySelector(`#${id}`);
  return element ? element.value : "";
}

function datasetRows(payload) {
  const generated = payload?.generated || [];
  const imported = payload?.imported || [];

  return [
    ...generated.map((item) => ({ ...item, dataset_kind: "generated" })),
    ...imported.map((item) => ({ ...item, dataset_kind: "imported" })),
  ];
}

function resultValue(result, fallback) {
  return result.status === "fulfilled" ? result.value : fallback;
}

function errorMessage(error) {
  if (!error) {
    return "";
  }

  return error.message || String(error);
}

function renderStatusPanel() {
  if (!state.error) {
    return "";
  }

  return `
    <section class="panel error-panel">
      <h3>Предупреждение</h3>
      <p>${htmlEscape(state.error)}</p>
      <button id="retryReportsData" class="button-secondary" type="button">Повторить</button>
    </section>
  `;
}

function renderDatasetOptions() {
  if (!state.datasets.length) {
    return option("", "Нет датасетов", "");
  }

  return state.datasets
    .map((item) =>
      option(
        item.dataset_id,
        `${item.dataset_id} · ${item.dataset_kind === "imported" ? "импорт" : "генерация"}`,
        state.selectedDatasetId,
      ),
    )
    .join("");
}

function renderTrainingSessionOptions() {
  if (!state.trainingSessions.length) {
    return option("", "Нет обученных сессий", "");
  }

  return state.trainingSessions
    .map((item) =>
      option(
        item.session_id,
        `${item.session_id} · ${item.status || "статус неизвестен"}`,
        state.selectedTrainingSessionId,
      ),
    )
    .join("");
}

function renderAssignmentSessionOptions() {
  if (!state.assignmentSessions.length) {
    return option("", "Нет сессий назначения", "");
  }

  return state.assignmentSessions
    .map((item) =>
      option(
        item.assignment_session_id,
        item.assignment_session_id,
        state.selectedAssignmentSessionId,
      ),
    )
    .join("");
}

function renderExportLinks(report) {
  const files = Array.isArray(report?.files) ? report.files : [];

  if (!report?.report_id || !files.length) {
    return `<p class="muted">Файлы отчета пока не созданы.</p>`;
  }

  return `
    <div class="export-links">
      ${files
        .map(
          (fileName) => `
            <a
              class="button-secondary"
              href="${api.exportReportFileUrl(report.report_id, fileName)}"
              target="_blank"
              rel="noreferrer"
            >
              ${htmlEscape(fileName)}
            </a>
          `,
        )
        .join("")}
    </div>
  `;
}

function renderExportReportsList() {
  if (!state.exportReports.length) {
    return `
      <section class="panel">
        <div class="section-heading">
          <div>
          <h3>Сохраненные отчеты</h3>
          <p class="muted">Экспортированные отчеты пока не созданы.</p>
          </div>
          <button id="refreshReportExports" class="button-secondary" type="button">
            Обновить
          </button>
        </div>
      </section>
    `;
  }

  return `
    <section class="panel">
      <div class="section-heading">
        <div>
          <h3>Сохраненные отчеты</h3>
          <p class="muted">Готовые файлы HTML и CSV для просмотра и выгрузки.</p>
        </div>
        <button id="refreshReportExports" class="button-secondary" type="button">
          Обновить
        </button>
      </div>

      <div class="list-grid">
        ${state.exportReports
          .map(
            (report) => `
              <button
                class="list-card ${
                  report.report_id === state.selectedReportId ? "active" : ""
                }"
                data-report-id="${htmlEscape(report.report_id)}"
                type="button"
              >
                <strong>${htmlEscape(report.title || report.report_id)}</strong>
                <span>
                  ${htmlEscape(report.report_kind || "report")}
                  · ${htmlEscape(report.generated_at || "")}
                </span>
              </button>
            `,
          )
          .join("")}
      </div>
    </section>
  `;
}

function renderDatasetExportPanel() {
  return `
    <section class="panel">
      <div class="section-heading">
        <div>
          <h3>Отчеты по датасету</h3>
          <p class="muted">
            Сводка по составу данных, качеству и базовым распределениям.
          </p>
        </div>
        <button id="deleteSelectedReport" class="button-danger" type="button">
          Удалить отчет
        </button>
      </div>

      <div class="form-grid">
        <label>
          Датасет
          <select id="datasetReportId">
            ${renderDatasetOptions()}
          </select>
        </label>

        <label>
          Тип датасета
          <select id="datasetReportKind">
            ${option("generated", "Сгенерированный", state.selectedDatasetKind)}
            ${option("imported", "Импортированный", state.selectedDatasetKind)}
          </select>
        </label>
      </div>

      <div class="actions-row">
        <button id="generateDatasetExport" type="button">Сформировать отчет</button>
      </div>
    </section>
  `;
}

function renderModelExportPanel() {
  return `
    <section class="panel">
      <div class="section-heading">
        <div>
          <h3>Отчеты по моделям</h3>
          <p class="muted">
            Сравнение метрик, артефактов моделей и статусов проверки.
          </p>
        </div>
      </div>

      <div class="form-grid">
        <label>
          Сессия обучения
          <select id="modelReportSessionId">
            ${renderTrainingSessionOptions()}
          </select>
        </label>
      </div>

      <div class="actions-row">
        <button id="generateModelExport" type="button">Сформировать отчет</button>
      </div>
    </section>
  `;
}

function renderAssignmentExportPanel() {
  return `
    <section class="panel">
      <div class="section-heading">
        <div>
          <h3>Отчеты по назначениям</h3>
          <p class="muted">
            Рекомендации, распределение задач, справедливость и нагрузка.
          </p>
        </div>
      </div>

      <div class="form-grid">
        <label>
          Сессия назначения
          <select id="assignmentReportSessionId">
            ${renderAssignmentSessionOptions()}
          </select>
        </label>
      </div>

      <div class="actions-row">
        <button id="generateAssignmentExport" type="button">
          Сформировать отчет
        </button>
      </div>
    </section>
  `;
}

function renderSelectedReport() {
  if (!state.selectedReport) {
    return `
      <section class="panel">
        <h3>Детали отчета</h3>
        <p class="muted">Выберите отчет из списка, чтобы открыть сводку и ссылки на файлы.</p>
      </section>
    `;
  }

  const manifest = state.selectedReport.manifest || {};
  const report = state.selectedReport.report || {};
  const summary = report.summary || {};
  const summaryRows = Object.entries(summary).slice(0, 14);

  return `
    <section class="panel">
      <div class="section-heading">
        <div>
          <h3>${htmlEscape(manifest.title || manifest.report_id || "Отчет")}</h3>
          <p class="muted">
            ${htmlEscape(manifest.report_kind || "отчет")}
            · ${htmlEscape(manifest.generated_at || "")}
          </p>
        </div>
      </div>

      ${renderExportLinks(manifest)}

      <div class="info-list">
        <p><strong>ID:</strong> ${htmlEscape(manifest.report_id || "")}</p>
        <p><strong>Тип:</strong> ${htmlEscape(manifest.report_kind || "отчет")}</p>
        <p><strong>Создан:</strong> ${htmlEscape(manifest.generated_at || "")}</p>
        <p><strong>Файлов:</strong> ${htmlEscape((manifest.files || []).length)}</p>
      </div>

      <h4>Краткая сводка</h4>
      ${
        summaryRows.length
          ? `
            <div class="table-scroll">
              <table class="data-table compact-table">
                <tbody>
                  ${summaryRows
                    .map(
                      ([key, value]) => `
                        <tr>
                          <th>${htmlEscape(key)}</th>
                          <td>${htmlEscape(
                            typeof value === "object" ? JSON.stringify(value) : value,
                          )}</td>
                        </tr>
                      `,
                    )
                    .join("")}
                </tbody>
              </table>
            </div>
          `
          : '<p class="muted">В этом отчете нет отдельной сводки.</p>'
      }
    </section>
  `;
}

function renderTrainingReportsCompatibilityPanel() {
  return `
    <section class="panel">
      <h3>Старые отчеты обучения</h3>
      <p class="muted">
        Графики и HTML-отчеты обучения остаются доступны в разделе обучения.
        Здесь собраны новые пользовательские экспорты для датасетов, моделей
        и назначений.
      </p>
    </section>
  `;
}

function renderReportsHtml() {
  return `
    <div class="page-stack">
      <section class="hero-panel">
        <div>
          <p class="eyebrow">Отчеты</p>
          <h1>Отчеты и выгрузки</h1>
          <p>
            Сформируйте понятные отчеты по данным, моделям и назначениям,
            а затем откройте готовые файлы для анализа.
          </p>
        </div>
      </section>

      ${renderStatusPanel()}
      ${renderDatasetExportPanel()}
      ${renderModelExportPanel()}
      ${renderAssignmentExportPanel()}
      ${renderTrainingReportsCompatibilityPanel()}
      ${renderExportReportsList()}
      ${renderSelectedReport()}
    </div>
  `;
}

async function refreshData() {
  state.error = "";

  const [datasetsResult, trainingResult, assignmentResult, reportsResult] =
    await Promise.allSettled([
      api.datasets(),
      api.trainingSessions(),
      api.assignmentSessions(),
      api.exportReports(),
    ]);

  const datasetsPayload = resultValue(datasetsResult, {
    generated: [],
    imported: [],
  });
  const trainingPayload = resultValue(trainingResult, {
    training_sessions: [],
  });
  const assignmentPayload = resultValue(assignmentResult, {
    assignment_sessions: [],
  });
  const reportsPayload = resultValue(reportsResult, {
    reports: [],
  });

  state.datasets = datasetRows(datasetsPayload);
  state.trainingSessions = trainingPayload.sessions || trainingPayload.training_sessions || [];
  state.assignmentSessions = assignmentPayload.assignment_sessions || [];
  state.exportReports = reportsPayload.reports || [];
  if (
    state.selectedReportId &&
    !state.exportReports.some((report) => report.report_id === state.selectedReportId)
  ) {
    state.selectedReportId = "";
    state.selectedReport = null;
  }

  const rejected = [
    datasetsResult,
    trainingResult,
    assignmentResult,
    reportsResult,
  ].filter((result) => result.status === "rejected");

  if (rejected.length) {
    state.error = rejected
      .map((result) => errorMessage(result.reason))
      .filter(Boolean)
      .join("; ");
  }

  if (!state.selectedDatasetId && state.datasets.length) {
    state.selectedDatasetId = state.datasets[0].dataset_id;
    state.selectedDatasetKind = state.datasets[0].dataset_kind;
  }

  if (!state.selectedTrainingSessionId && state.trainingSessions.length) {
    state.selectedTrainingSessionId = state.trainingSessions[0].session_id;
  }

  if (!state.selectedAssignmentSessionId && state.assignmentSessions.length) {
    state.selectedAssignmentSessionId =
      state.assignmentSessions[0].assignment_session_id;
  }
}

function repaint() {
  const root = document.querySelector("#appRoot");

  if (!root) {
    return;
  }

  root.innerHTML = renderReportsHtml();
  bindEvents();
}

async function generateDatasetExport() {
  const datasetId = selectedValue("datasetReportId");
  const datasetKind = selectedValue("datasetReportKind");

  if (!datasetId) {
    toast("Отчеты", "Датасет не выбран");
    return;
  }

  const progress = startLongTaskToast({
    title: "Формируем отчет...",
    message: "Проверяем данные...",
    steps: ["Проверяем данные...", "Формируем отчет...", "Сохраняем файлы..."],
  });

  try {
    progress.update({ message: "Формируем отчет...", percent: 42, stepIndex: 1 });
    const result = await api.generateDatasetExport(datasetId, {
      dataset_kind: datasetKind,
    });

    state.selectedReport = {
      manifest: result,
      report: result.payload || {},
    };
    state.selectedReportId = result.report_id || "";

    progress.update({ message: "Сохраняем файлы...", percent: 96, stepIndex: 2 });
    progress.done("Готово");
    await refreshData();
    toast("Отчеты", "Отчет по датасету готов");
  } catch (error) {
    progress.error(error.message || String(error));
    throw error;
  }
}

async function generateModelExport() {
  const sessionId = selectedValue("modelReportSessionId");

  if (!sessionId) {
    toast("Отчеты", "Сессия обучения не выбрана");
    return;
  }

  const progress = startLongTaskToast({
    title: "Формируем отчет...",
    message: "Собираем результаты...",
    steps: ["Собираем результаты...", "Формируем отчет...", "Сохраняем файлы..."],
  });

  try {
    progress.update({ message: "Формируем отчет...", percent: 42, stepIndex: 1 });
    const result = await api.generateModelExport(sessionId);

    state.selectedReport = {
      manifest: result,
      report: result.payload || {},
    };
    state.selectedReportId = result.report_id || "";

    progress.update({ message: "Сохраняем файлы...", percent: 96, stepIndex: 2 });
    progress.done("Готово");
    await refreshData();
    toast("Отчеты", "Отчет по моделям готов");
  } catch (error) {
    progress.error(error.message || String(error));
    throw error;
  }
}

async function generateAssignmentExport() {
  const assignmentSessionId = selectedValue("assignmentReportSessionId");

  if (!assignmentSessionId) {
    toast("Отчеты", "Сессия назначения не выбрана");
    return;
  }

  const progress = startLongTaskToast({
    title: "Формируем отчет...",
    message: "Собираем результаты...",
    steps: ["Собираем результаты...", "Формируем отчет...", "Сохраняем файлы..."],
  });

  try {
    progress.update({ message: "Формируем отчет...", percent: 42, stepIndex: 1 });
    const result = await api.generateAssignmentExport(assignmentSessionId);

    state.selectedReport = {
      manifest: result,
      report: result.payload || {},
    };
    state.selectedReportId = result.report_id || "";

    progress.update({ message: "Сохраняем файлы...", percent: 96, stepIndex: 2 });
    progress.done("Готово");
    await refreshData();
    toast("Отчеты", "Отчет по назначениям готов");
  } catch (error) {
    progress.error(error.message || String(error));
    throw error;
  }
}

async function deleteSelectedReport() {
  const reportId = state.selectedReportId || state.selectedReport?.manifest?.report_id;

  if (!reportId) {
    toast("Отчеты", "Отчет не выбран");
    return;
  }

  if (!window.confirm(`Удалить отчет "${reportId}"?`)) {
    return;
  }

  await api.deleteExportReport(reportId);
  state.selectedReportId = "";
  state.selectedReport = null;
  await refreshData();
  toast("Отчеты", "Отчет удален");
}

async function runAction(action) {
  try {
    await action();
  } catch (error) {
    state.error = errorMessage(error);
    toast("Ошибка отчетов", state.error);
  }

  repaint();
}

function bindEvents() {
  document.querySelector("#generateDatasetExport")?.addEventListener("click", () => {
    runAction(generateDatasetExport);
  });

  document.querySelector("#generateModelExport")?.addEventListener("click", () => {
    runAction(generateModelExport);
  });

  document.querySelector("#generateAssignmentExport")?.addEventListener("click", () => {
    runAction(generateAssignmentExport);
  });

  document.querySelector("#refreshReportExports")?.addEventListener("click", () => {
    runAction(refreshData);
  });

  document.querySelector("#retryReportsData")?.addEventListener("click", () => {
    runAction(refreshData);
  });

  document.querySelector("#deleteSelectedReport")?.addEventListener("click", () => {
    runAction(deleteSelectedReport);
  });

  document.querySelectorAll("[data-report-id]").forEach((button) => {
    button.addEventListener("click", () => {
      runAction(async () => {
        const reportId = button.dataset.reportId || "";
        state.selectedReportId = reportId;
        state.selectedReport = await api.exportReport(reportId);
      });
    });
  });
}

export async function renderReports() {
  await refreshData();
  window.setTimeout(bindEvents, 0);
  return renderReportsHtml();
}

export async function renderReportsPage() {
  return renderReports();
}

export async function renderPage() {
  return renderReports();
}

export default renderReports;
