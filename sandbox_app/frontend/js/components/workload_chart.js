import { htmlEscape } from "../app.js";

function percent(value) {
  const numeric = Number(value);

  if (!Number.isFinite(numeric)) {
    return "0%";
  }

  return `${Math.round(Math.max(0, Math.min(1.5, numeric)) * 100)}%`;
}

function width(value) {
  const numeric = Number(value);

  if (!Number.isFinite(numeric)) {
    return "0%";
  }

  return `${Math.min(100, Math.round((numeric / 1.5) * 100))}%`;
}

export function renderWorkloadChart(rows, options = {}) {
  const items = Array.isArray(rows) ? rows : [];
  const title = options.title || "Workload after assignment";

  if (!items.length) {
    return `
      <section class="panel">
        <h3>${htmlEscape(title)}</h3>
        <p class="muted">Нет данных по загрузке.</p>
      </section>
    `;
  }

  return `
    <section class="panel">
      <div class="section-heading">
        <div>
          <h3>${htmlEscape(title)}</h3>
          <p class="muted">Прогнозная загрузка после batch assignment.</p>
        </div>
      </div>

      <div class="bar-chart-list">
        ${items
          .map(
            (row) => `
              <div class="bar-chart-row">
                <div class="bar-chart-label">
                  <strong>${htmlEscape(row.name || row.employee_id)}</strong>
                  <span>
                    ${htmlEscape(row.role || "—")}
                    · tasks: ${htmlEscape(row.assigned_tasks_count ?? 0)}
                  </span>
                </div>
                <div class="bar-track">
                  <div
                    class="bar-fill"
                    style="width: ${width(row.projected_workload)}"
                  ></div>
                </div>
                <span class="bar-value">${percent(row.projected_workload)}</span>
              </div>
            `,
          )
          .join("")}
      </div>
    </section>
  `;
}