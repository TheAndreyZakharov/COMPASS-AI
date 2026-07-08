import { api } from "../api.js";
import { htmlEscape, prettyJson, toast } from "../app.js";
import { renderSummaryCards } from "../components/charts.js";
import { renderDataTable } from "../components/table.js";

const state = {
  reports: null,
  selectedSessionId: "",
};

function reportOptions(payload) {
  const reports = payload?.reports || [];

  if (reports.length === 0) {
    return '<option value="">Нет training sessions</option>';
  }

  return reports
    .map((report) => {
      const selected = report.session_id === state.selectedSessionId ? "selected" : "";

      return `
        <option value="${htmlEscape(report.session_id)}" ${selected}>
          ${htmlEscape(report.session_id)} · ${htmlEscape(report.status || "")}
        </option>
      `;
    })
    .join("");
}

function selectedReport() {
  return (state.reports?.reports || []).find(
    (report) => report.session_id === state.selectedSessionId,
  );
}

function readControls() {
  state.selectedSessionId = document.querySelector("#reportsSession").value;
  renderSelectedReport();
}

function setReportsLoading(isLoading, label = "Loading...") {
  const status = document.querySelector("#reportsStatus");
  const buttons = document.querySelectorAll("[data-reports-action]");

  buttons.forEach((button) => {
    button.disabled = isLoading;
    button.classList.toggle("loading", isLoading);
  });

  status.className = isLoading ? "status-pill status-pending" : "status-pill status-ok";
  status.innerHTML = isLoading
    ? `<span class="status-dot"></span><span>${htmlEscape(label)}</span>`
    : '<span class="status-dot"></span><span>Готов</span>';
}

function renderSelectedReport() {
  const element = document.querySelector("#selectedReportJson");

  if (!element) {
    return;
  }

  element.textContent = prettyJson(selectedReport() || {});
}

function renderOutput(html) {
  document.querySelector("#reportsOutput").innerHTML = html;
}

function renderError(error) {
  renderOutput(`
    <article class="card">
      <span class="badge">Error</span>
      <h2>Reports error</h2>
      <p class="muted">${htmlEscape(error.message || String(error))}</p>
    </article>
  `);
}

function renderReportsList() {
  const reports = state.reports?.reports || [];

  if (reports.length === 0) {
    renderOutput(`
      <article class="card">
        <h2>Reports</h2>
        <p class="muted">Training sessions пока не найдены.</p>
      </article>
    `);
    return;
  }

  const rows = reports.map((report) => ({
    session_id: report.session_id,
    dataset_id: report.dataset_id,
    status: report.status,
    generated_at: report.generated_at || "",
    trained_models: (report.trained_models || []).join(", "),
    report_html: report.report_html || "",
  }));

  renderOutput(`
    <section class="grid grid-4">
      ${renderSummaryCards({
        reports: reports.length,
        generated: reports.filter((report) => report.status === "generated").length,
        pending: reports.filter((report) => report.status !== "generated").length,
        latest_models: reports[0]?.trained_models?.length || 0,
      })}
    </section>

    <article class="card" style="margin-top: 16px;">
      <h2>Training reports</h2>
      ${renderDataTable(rows, [
        "session_id",
        "dataset_id",
        "status",
        "generated_at",
        "trained_models",
        "report_html",
      ])}
    </article>
  `);
}

function renderReportManifest(manifest) {
  const plots = manifest.plots || {};
  const sessionPlots = plots.session_plots || {};
  const modelPlots = plots.model_plots || {};
  const artifactRows = (manifest.artifacts || []).map((artifact) => ({
    model_name: artifact.model_name,
    validation_status: artifact.export_validation?.status || "",
    artifact_format: artifact.metadata?.artifact_format || "",
    plot_count: Object.keys(modelPlots[artifact.model_name] || {}).length,
  }));

  const sessionPlotRows = Object.entries(sessionPlots).map(([name, path]) => ({
    plot: name,
    path,
  }));

  renderOutput(`
    <section class="grid grid-4">
      ${renderSummaryCards({
        models: artifactRows.length,
        session_plots: sessionPlotRows.length,
        model_plot_groups: Object.keys(modelPlots).length,
        comparison_rows: manifest.comparison_metrics?.length || 0,
      })}
    </section>

    <article class="card" style="margin-top: 16px;">
      <h2>Report actions</h2>
      <p class="muted">
        HTML report endpoint:
        /api/reports/training/${htmlEscape(manifest.session_id)}/html
      </p>
      <a
        class="button button-primary"
        href="/api/reports/training/${encodeURIComponent(manifest.session_id)}/html"
        target="_blank"
      >
        Open HTML report
      </a>
    </article>

    <article class="card" style="margin-top: 16px;">
      <h2>Session plots</h2>
      ${renderDataTable(sessionPlotRows)}
    </article>

    <article class="card" style="margin-top: 16px;">
      <h2>Model plot groups</h2>
      ${renderDataTable(artifactRows)}
    </article>

    <article class="card" style="margin-top: 16px;">
      <h2>Comparison metrics</h2>
      ${renderDataTable(manifest.comparison_metrics || [])}
    </article>

    <article class="card" style="margin-top: 16px;">
      <h2>Report manifest</h2>
      <pre class="code">${prettyJson(manifest)}</pre>
    </article>
  `);
}

async function refreshReports() {
  try {
    setReportsLoading(true, "Reports...");
    state.reports = await api.trainingReports();

    if (!state.selectedSessionId) {
      state.selectedSessionId = state.reports?.reports?.[0]?.session_id || "";
    }

    document.querySelector("#reportsSession").innerHTML = reportOptions(state.reports);
    renderSelectedReport();
    renderReportsList();
  } catch (error) {
    renderError(error);
    toast("Reports", error.message || String(error));
  } finally {
    setReportsLoading(false);
  }
}

async function generateSelectedReport() {
  try {
    readControls();

    if (!state.selectedSessionId) {
      throw new Error("Сначала выбери training session.");
    }

    setReportsLoading(true, "Generating report...");
    const manifest = await api.generateTrainingReport(state.selectedSessionId);
    renderReportManifest(manifest);
    toast("Training report", "Report generated");
    state.reports = await api.trainingReports();
    document.querySelector("#reportsSession").innerHTML = reportOptions(state.reports);
    renderSelectedReport();
  } catch (error) {
    renderError(error);
    toast("Reports", error.message || String(error));
  } finally {
    setReportsLoading(false);
  }
}

async function loadSelectedReport() {
  try {
    readControls();

    if (!state.selectedSessionId) {
      throw new Error("Сначала выбери training session.");
    }

    setReportsLoading(true, "Loading report...");
    const manifest = await api.trainingReport(state.selectedSessionId);
    renderReportManifest(manifest);
  } catch (error) {
    renderError(error);
    toast("Reports", error.message || String(error));
  } finally {
    setReportsLoading(false);
  }
}

function bindEvents() {
  document.querySelector("#reportsSession").addEventListener("change", readControls);

  document.querySelector("[data-reports-action='refresh']").addEventListener("click", () => {
    refreshReports();
  });

  document.querySelector("[data-reports-action='list']").addEventListener("click", () => {
    renderReportsList();
  });

  document.querySelector("[data-reports-action='generate']").addEventListener("click", () => {
    generateSelectedReport();
  });

  document.querySelector("[data-reports-action='load']").addEventListener("click", () => {
    loadSelectedReport();
  });
}

export async function renderReports() {
  state.reports = await api.trainingReports();
  state.selectedSessionId = state.reports?.reports?.[0]?.session_id || "";

  window.setTimeout(() => {
    bindEvents();
    renderSelectedReport();
    renderReportsList();
  }, 0);

  return `
    <section class="grid grid-2">
      <article class="card">
        <div class="viewer-section-header">
          <div>
            <h2>Reports</h2>
            <p class="muted">
              Training plots, model comparison, report manifest and HTML training report.
            </p>
          </div>
          <div class="status-pill status-ok" id="reportsStatus">
            <span class="status-dot"></span>
            <span>Готов</span>
          </div>
        </div>

        <div class="toolbar">
          <div class="form-row">
            <label for="reportsSession">Training session</label>
            <select class="select" id="reportsSession">
              ${reportOptions(state.reports)}
            </select>
          </div>
        </div>

        <div class="toolbar">
          <button class="button button-secondary" data-reports-action="list" type="button">
            Reports
          </button>
          <button class="button button-primary" data-reports-action="generate" type="button">
            Generate report
          </button>
          <button class="button button-secondary" data-reports-action="load" type="button">
            Load manifest
          </button>
          <button class="button button-secondary" data-reports-action="refresh" type="button">
            Refresh
          </button>
        </div>
      </article>

      <article class="card">
        <h2>Selected report</h2>
        <pre class="code" id="selectedReportJson">${prettyJson(selectedReport() || {})}</pre>
      </article>
    </section>

    <section id="reportsOutput" style="margin-top: 16px;">
      <article class="card">
        <h2>Reports</h2>
        <p class="muted">Загрузка reports...</p>
      </article>
    </section>
  `;
}