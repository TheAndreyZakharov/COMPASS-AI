function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function numericEntries(payload) {
  return Object.entries(payload || {})
    .filter(([, value]) => Number.isFinite(Number(value)))
    .map(([key, value]) => [key, Number(value)]);
}

export function renderSummaryCards(counts) {
  const entries = numericEntries(counts);

  if (entries.length === 0) {
    return `
      <article class="card">
        <h3>Summary counts</h3>
        <p class="muted">Counts пока не найдены.</p>
      </article>
    `;
  }

  return entries
    .map(
      ([name, value]) => `
        <article class="card kpi">
          <span class="muted">${escapeHtml(name)}</span>
          <strong>${escapeHtml(value)}</strong>
          <small class="muted">records</small>
        </article>
      `,
    )
    .join("");
}

export function renderBarChart(title, values) {
  const entries = numericEntries(values);
  const maxValue = Math.max(...entries.map(([, value]) => value), 1);

  if (entries.length === 0) {
    return `
      <article class="card">
        <h3>${escapeHtml(title)}</h3>
        <p class="muted">Нет числовых данных для chart.</p>
      </article>
    `;
  }

  const bars = entries
    .map(([name, value]) => {
      const width = Math.max(4, Math.round((value / maxValue) * 100));

      return `
        <div class="chart-row">
          <div class="chart-label">${escapeHtml(name)}</div>
          <div class="chart-track">
            <div class="chart-bar" style="width: ${escapeHtml(width)}%;"></div>
          </div>
          <div class="chart-value">${escapeHtml(value)}</div>
        </div>
      `;
    })
    .join("");

  return `
    <article class="card">
      <h3>${escapeHtml(title)}</h3>
      <div class="chart">${bars}</div>
    </article>
  `;
}

export function countByField(rows, fieldName) {
  return (rows || []).reduce((accumulator, row) => {
    const key = row?.[fieldName] || "unknown";
    accumulator[key] = (accumulator[key] || 0) + 1;
    return accumulator;
  }, {});
}