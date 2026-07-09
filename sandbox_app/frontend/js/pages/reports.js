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

function prettyJson(value) {
  return htmlEscape(JSON.stringify(value ?? {}, null, 2));
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
      <h3>Reports page warning</h3>
      <p>${htmlEscape(state.error)}</p>
      <button id="retryReportsData" class="button-secondary" type="button">Retry</button>
    </section>
  `;
}

function renderDatasetOptions() {
  if (!state.datasets.length) {
    return option("", "Нет datasets", "");
  }

  return state.datasets
    .map((item) =>
      option(
        item.dataset_id,
        `${item.dataset_id} · ${item.dataset_kind}`,
        state.selectedDatasetId,
      ),
    )
    .join("");
}

function renderTrainingSessionOptions() {
  if (!state.trainingSessions.length) {
    return option("", "Нет training sessions", "");
  }

  return state.trainingSessions
    .map((item) =>
      option(
        item.session_id,
        `${item.session_id} · ${item.status || "unknown"}`,
        state.selectedTrainingSessionId,
      ),
    )
    .join("");
}

function renderAssignmentSessionOptions() {
  if (!state.assignmentSessions.length) {
    return option("", "Нет assignment sessions", "");
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
    return `<p class="muted">Export files пока не созданы.</p>`;
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
            <h3>Saved report exports</h3>
            <p class="muted">Экспортированные reports пока не созданы.</p>
          </div>
          <button id="refreshReportExports" class="button-secondary" type="button">
            Refresh
          </button>
        </div>
      </section>
    `;
  }

  return `
    <section class="panel">
      <div class="section-heading">
        <div>
          <h3>Saved report exports</h3>
          <p class="muted">JSON, CSV и HTML reports из sandbox_app/reports.</p>
        </div>
        <button id="refreshReportExports" class="button-secondary" type="button">
          Refresh
        </button>
      </div>

      <div class="list-grid">
        ${state.exportReports
          .map(
            (report) => `
              <button
                class="list-card"
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
          <h3>Dataset reports</h3>
          <p class="muted">
            Dataset generation report и dataset quality report.
          </p>
        </div>
      </div>

      <div class="form-grid">
        <label>
          Dataset
          <select id="datasetReportId">
            ${renderDatasetOptions()}
          </select>
        </label>

        <label>
          Dataset kind
          <select id="datasetReportKind">
            ${option("generated", "generated", state.selectedDatasetKind)}
            ${option("imported", "imported", state.selectedDatasetKind)}
          </select>
        </label>
      </div>

      <div class="actions-row">
        <button id="generateDatasetExport" type="button">Generate dataset export</button>
      </div>
    </section>
  `;
}

function renderModelExportPanel() {
  return `
    <section class="panel">
      <div class="section-heading">
        <div>
          <h3>Model comparison reports</h3>
          <p class="muted">
            Export comparison metrics, model artifacts и validation status.
          </p>
        </div>
      </div>

      <div class="form-grid">
        <label>
          Training session
          <select id="modelReportSessionId">
            ${renderTrainingSessionOptions()}
          </select>
        </label>
      </div>

      <div class="actions-row">
        <button id="generateModelExport" type="button">Generate model export</button>
      </div>
    </section>
  `;
}

function renderAssignmentExportPanel() {
  return `
    <section class="panel">
      <div class="section-heading">
        <div>
          <h3>Assignment reports</h3>
          <p class="muted">
            Recommendation, bulk assignment, fairness и workload reports.
          </p>
        </div>
      </div>

      <div class="form-grid">
        <label>
          Assignment session
          <select id="assignmentReportSessionId">
            ${renderAssignmentSessionOptions()}
          </select>
        </label>
      </div>

      <div class="actions-row">
        <button id="generateAssignmentExport" type="button">
          Generate assignment export
        </button>
      </div>
    </section>
  `;
}

function renderSelectedReport() {
  if (!state.selectedReport) {
    return `
      <section class="panel">
        <h3>Report details</h3>
        <p class="muted">Выбери report export, чтобы открыть details и links.</p>
      </section>
    `;
  }

  const manifest = state.selectedReport.manifest || {};
  const report = state.selectedReport.report || {};

  return `
    <section class="panel">
      <div class="section-heading">
        <div>
          <h3>${htmlEscape(manifest.title || manifest.report_id || "Report")}</h3>
          <p class="muted">
            ${htmlEscape(manifest.report_kind || "report")}
            · ${htmlEscape(manifest.generated_at || "")}
          </p>
        </div>
      </div>

      ${renderExportLinks(manifest)}

      <h4>Summary</h4>
      <pre>${prettyJson(report.summary || {})}</pre>

      <h4>Full report JSON</h4>
      <pre>${prettyJson(report)}</pre>
    </section>
  `;
}

function renderTrainingReportsCompatibilityPanel() {
  return `
    <section class="panel">
      <h3>Training reports compatibility</h3>
      <p class="muted">
        Старые training plots и training_report.html из предыдущего этапа остаются
        доступными через training reports API. Новый export layer добавляет
        отдельные JSON, CSV и HTML bundles.
      </p>
    </section>
  `;
}

function renderReportsHtml() {
  return `
    <div class="page-stack">
      <section class="hero-panel">
        <div>
          <p class="eyebrow">Reports</p>
          <h1>Reports and exports</h1>
          <p>
            Dataset, model, recommendation, bulk assignment, fairness и workload
            reports с JSON, CSV и HTML export links.
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
  state.trainingSessions = trainingPayload.training_sessions || [];
  state.assignmentSessions = assignmentPayload.assignment_sessions || [];
  state.exportReports = reportsPayload.reports || [];

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
    toast("Reports", "Dataset не выбран");
    return;
  }

  const result = await api.generateDatasetExport(datasetId, {
    dataset_kind: datasetKind,
  });

  state.selectedReport = {
    manifest: result,
    report: result.payload || {},
  };

  await refreshData();
  toast("Reports", "Dataset export generated");
}

async function generateModelExport() {
  const sessionId = selectedValue("modelReportSessionId");

  if (!sessionId) {
    toast("Reports", "Training session не выбран");
    return;
  }

  const result = await api.generateModelExport(sessionId);

  state.selectedReport = {
    manifest: result,
    report: result.payload || {},
  };

  await refreshData();
  toast("Reports", "Model export generated");
}

async function generateAssignmentExport() {
  const assignmentSessionId = selectedValue("assignmentReportSessionId");

  if (!assignmentSessionId) {
    toast("Reports", "Assignment session не выбран");
    return;
  }

  const result = await api.generateAssignmentExport(assignmentSessionId);

  state.selectedReport = {
    manifest: result,
    report: result.payload || {},
  };

  await refreshData();
  toast("Reports", "Assignment export generated");
}

async function runAction(action) {
  try {
    await action();
  } catch (error) {
    state.error = errorMessage(error);
    toast("Reports error", state.error);
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

  document.querySelectorAll("[data-report-id]").forEach((button) => {
    button.addEventListener("click", () => {
      runAction(async () => {
        const reportId = button.dataset.reportId || "";
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