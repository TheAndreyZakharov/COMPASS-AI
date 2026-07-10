import { htmlEscape } from "../app.js";

const PLOT_TITLES = {
  calibration_plot: "Калибровка вероятностей",
  confusion_matrix: "Матрица ошибок",
  feature_importance: "Важность признаков",
  learning_curve: "Кривая обучения",
  loss_curve: "Кривая ошибки",
  model_comparison: "Сравнение моделей",
  precision_recall_curve: "Precision-recall кривая",
  roc_curve: "ROC-кривая",
  score_distribution: "Распределение оценок",
};

function isPlotMap(value) {
  return Boolean(value) && typeof value === "object" && !Array.isArray(value);
}

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
          class="training-plot-image"
          alt="${htmlEscape(title)}"
          src="${htmlEscape(url)}"
        />
      </a>
    </article>
  `;
}

function addPlotGroup(cards, groupName, plotMap) {
  if (!isPlotMap(plotMap)) {
    return;
  }

  Object.entries(plotMap).forEach(([plotName, path]) => {
    if (typeof path !== "string" || !path) {
      return;
    }

    cards.push({
      groupName,
      plotName,
      path,
    });
  });
}

function flattenPlots(manifest) {
  const plots = manifest?.plots || {};
  const cards = [];
  const sessionPlots = plots.session_plots;
  const modelPlots = plots.model_plots;

  addPlotGroup(cards, "Сводные графики", sessionPlots);

  if (isPlotMap(modelPlots)) {
    Object.entries(modelPlots).forEach(([modelName, modelPlotMap]) => {
      addPlotGroup(cards, modelName, modelPlotMap);
    });
  }

  if (!isPlotMap(sessionPlots) && !isPlotMap(modelPlots)) {
    Object.entries(plots).forEach(([groupName, plotMap]) => {
      addPlotGroup(cards, groupName, plotMap);
    });
  }

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
    accumulator[item.groupName] = accumulator[item.groupName] || [];
    accumulator[item.groupName].push(item);
    return accumulator;
  }, {});

  return Object.entries(grouped)
    .map(
      ([groupName, items]) => `
        <article class="card">
          <h2>${htmlEscape(groupName)}</h2>
          <p class="muted">Все сгенерированные графики для этого раздела.</p>
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
      <h2>Файлы отчета</h2>
      <p class="muted">HTML-отчет и служебный файл отчета для выбранной сессии.</p>
      <div class="toolbar">
        <a
          class="button button-secondary"
          href="/api/reports/training/${encodeURIComponent(sessionId)}/html"
          target="_blank"
          rel="noreferrer"
        >
          Открыть HTML-отчет
        </a>
      </div>
      <div class="info-list">
        <p><strong>HTML:</strong> ${htmlEscape(htmlPath || "готовится")}</p>
        <p><strong>Манифест:</strong> ${htmlEscape(manifestPath || "готовится")}</p>
      </div>
    </article>
  `;
}
