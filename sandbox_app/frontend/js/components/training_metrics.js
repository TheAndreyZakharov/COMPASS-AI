import { htmlEscape } from "../app.js";
import { renderDataTable } from "./table.js";

const METRIC_COLUMNS = [
  "model_name",
  "roc_auc",
  "f1",
  "precision",
  "recall",
  "accuracy",
  "log_loss",
  "mae_for_score",
  "top_1_accuracy",
  "top_3_accuracy",
];

function formatMetric(value) {
  if (value === null || value === undefined || value === "") {
    return "";
  }

  const numeric = Number(value);

  if (!Number.isFinite(numeric)) {
    return String(value);
  }

  return numeric.toFixed(4);
}

export function normalizeMetricRows(rows) {
  return (rows || []).map((row) => {
    const normalized = {};

    METRIC_COLUMNS.forEach((column) => {
      normalized[column] = column === "model_name"
        ? row[column] || row.model || ""
        : formatMetric(row[column]);
    });

    return normalized;
  });
}

export function bestModelBadge(rows) {
  const normalizedRows = rows || [];
  const rankedRows = normalizedRows
    .filter((row) => Number.isFinite(Number(row.roc_auc)))
    .sort((left, right) => Number(right.roc_auc) - Number(left.roc_auc));

  if (rankedRows.length === 0) {
    return '<span class="badge">лучшая модель пока не определена</span>';
  }

  const best = rankedRows[0];

  return `
    <span class="badge">
      лучшая: ${htmlEscape(best.model_name || "")} · roc_auc ${htmlEscape(best.roc_auc)}
    </span>
  `;
}

export function renderTrainingMetrics(rows) {
  const normalizedRows = normalizeMetricRows(rows);

  if (normalizedRows.length === 0) {
    return `
      <article class="card">
        <h2>Метрики</h2>
        <p class="muted">Метрики пока не рассчитаны.</p>
      </article>
    `;
  }

  return `
    <article class="card">
      <div class="viewer-section-header">
        <div>
          <h2>Сравнение метрик</h2>
          <p class="muted">Сравнение качества моделей в сессии обучения.</p>
        </div>
        ${bestModelBadge(normalizedRows)}
      </div>
      ${renderDataTable(normalizedRows, METRIC_COLUMNS)}
    </article>
  `;
}

export function renderModelMetricCards(rows) {
  const normalizedRows = normalizeMetricRows(rows);

  if (normalizedRows.length === 0) {
    return "";
  }

  return normalizedRows
    .map(
      (row) => `
        <article class="card">
          <h2>${htmlEscape(row.model_name)}</h2>
          <p class="muted">roc_auc: ${htmlEscape(row.roc_auc)}</p>
          <p>f1: <strong>${htmlEscape(row.f1)}</strong></p>
          <p>accuracy: <strong>${htmlEscape(row.accuracy)}</strong></p>
        </article>
      `,
    )
    .join("");
}
