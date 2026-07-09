import { htmlEscape } from "../app.js";

function numberValue(value) {
  const numeric = Number(value);

  if (!Number.isFinite(numeric)) {
    return "—";
  }

  if (Number.isInteger(numeric)) {
    return String(numeric);
  }

  return numeric.toFixed(3);
}

export function renderFairnessChart(report, workloadRows = []) {
  const fairness = report || {};
  const rows = Array.isArray(workloadRows) ? workloadRows : [];

  const cards = [
    ["People", fairness.people],
    ["Assigned tasks", fairness.assigned_tasks_total],
    ["Max tasks", fairness.max_assigned_tasks],
    ["Min tasks", fairness.min_assigned_tasks],
    ["Spread", fairness.assignment_spread],
    ["Avg workload", fairness.avg_projected_workload],
    ["Max workload", fairness.max_projected_workload],
    ["Overloaded", fairness.overloaded_people],
  ];

  return `
    <section class="panel">
      <div class="section-heading">
        <div>
          <h3>Fairness report</h3>
          <p class="muted">Распределение задач и нагрузки по команде.</p>
        </div>
      </div>

      <div class="summary-grid">
        ${cards
          .map(
            ([label, value]) => `
              <article class="summary-card">
                <span>${htmlEscape(label)}</span>
                <strong>${numberValue(value)}</strong>
              </article>
            `,
          )
          .join("")}
      </div>

      <div class="mini-distribution">
        ${rows
          .map(
            (row) => `
              <div class="mini-distribution-item">
                <span>${htmlEscape(row.name || row.employee_id)}</span>
                <strong>${htmlEscape(row.assigned_tasks_count ?? 0)}</strong>
              </div>
            `,
          )
          .join("")}
      </div>
    </section>
  `;
}