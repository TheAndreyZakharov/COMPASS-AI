import { htmlEscape } from "../app.js";

const PLOT_TITLES = {
  calibration_plot: "Calibration plot",
  confusion_matrix: "Confusion matrix",
  feature_importance: "Feature importance",
  learning_curve: "Learning curve",
  loss_curve: "Loss curve",
  model_comparison: "Model comparison",
  precision_recall_curve: "Precision-recall curve",
  roc_curve: "ROC curve",
  score_distribution: "Score distribution",
};

function pathToReportRelative(path) {
  if (!path) {
    return "";
  }

  const normalized = String(path).replaceAll("\\", "/");
  const marker = "/reports/";

  if (normalized.includes(marker)) {
    return normalized.split(marker).slice(1).join(marker);
  }

  if (normalized.startsWith("reports/")) {
    return normalized.slice("reports/".length);
  }

  return normalized;
}

function plotUrl(sessionId, path) {
  const relativePath = pathToReportRelative(path);

  if (!relativePath) {
    return "";
  }

  return (
    `/api/reports/training/${encodeURIComponent(sessionId)}/files/` +
    encodeURIComponent(relativePath).replaceAll("%2F", "/")
  );
}

function renderPlotCard(sessionId, plotName, path) {
  const url = plotUrl(sessionId, path);
  const title = PLOT_TITLES[plotName] || plotName;

  if (!url) {
    return "";
  }

  return `
    <article class="card">
      <h2>${htmlEscape(title)}</h2>
      <a href="${htmlEscape(url)}" target="_blank" rel="noreferrer">
        <img
          alt="${htmlEscape(title)}"
          src="${htmlEscape(url)}"
          style="border-radius: 12px; max-width: 100%; width: 100%;"
        />
      </a>
    </article>
  `;
}

function flattenPlots(manifest) {
  const plots = manifest?.plots || {};
  const cards = [];

  Object.entries(plots).forEach(([modelName, modelPlots]) => {
    if (!modelPlots || typeof modelPlots !== "object") {
      return;
    }

    Object.entries(modelPlots).forEach(([plotName, path]) => {
      cards.push({
        modelName,
        plotName,
        path,
      });
    });
  });

  return cards;
}

export function renderTrainingPlots(sessionId, manifest) {
  const cards = flattenPlots(manifest);

  if (cards.length === 0) {
    return `
      <article class="card">
        <h2>Training plots</h2>
        <p class="muted">Графики пока не сгенерированы.</p>
      </article>
    `;
  }

  const grouped = cards.reduce((accumulator, item) => {
    accumulator[item.modelName] = accumulator[item.modelName] || [];
    accumulator[item.modelName].push(item);
    return accumulator;
  }, {});

  return Object.entries(grouped)
    .map(
      ([modelName, items]) => `
        <article class="card">
          <h2>${htmlEscape(modelName)}</h2>
          <p class="muted">Training plots для модели.</p>
        </article>
        <section class="grid grid-2">
          ${items
            .map((item) => renderPlotCard(sessionId, item.plotName, item.path))
            .join("")}
        </section>
      `,
    )
    .join("");
}

export function renderReportLinks(sessionId, manifest) {
  const htmlPath = manifest?.html_path || "";
  const manifestPath = manifest?.manifest_path || "";

  return `
    <article class="card">
      <h2>Report artifacts</h2>
      <p class="muted">Training report и manifest для выбранной session.</p>
      <div class="toolbar">
        <a
          class="button button-secondary"
          href="/api/reports/training/${encodeURIComponent(sessionId)}/html"
          target="_blank"
          rel="noreferrer"
        >
          Open HTML report
        </a>
      </div>
      <pre class="code">${htmlEscape(
        JSON.stringify(
          {
            html_path: htmlPath,
            manifest_path: manifestPath,
          },
          null,
          2,
        ),
      )}</pre>
    </article>
  `;
}