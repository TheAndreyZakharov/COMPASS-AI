function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function stringifyCell(value) {
  if (value === null || value === undefined) {
    return "";
  }

  if (Array.isArray(value)) {
    return value.join(", ");
  }

  if (typeof value === "object") {
    return JSON.stringify(value);
  }

  return String(value);
}

export function inferColumns(rows, preferredColumns = []) {
  if (!Array.isArray(rows) || rows.length === 0) {
    return preferredColumns;
  }

  const discovered = new Set(preferredColumns);
  rows.slice(0, 20).forEach((row) => {
    Object.keys(row || {}).forEach((key) => discovered.add(key));
  });

  return Array.from(discovered);
}

export function renderDataTable(rows, preferredColumns = []) {
  if (!Array.isArray(rows) || rows.length === 0) {
    return `
      <div class="empty">
        <div>
          <h3>Нет строк</h3>
          <p class="muted">Измени фильтры, search или выбери другой dataset.</p>
        </div>
      </div>
    `;
  }

  const columns = inferColumns(rows, preferredColumns);
  const header = columns.map((column) => `<th>${escapeHtml(column)}</th>`).join("");
  const body = rows
    .map((row) => {
      const cells = columns
        .map((column) => `<td>${escapeHtml(stringifyCell(row[column]))}</td>`)
        .join("");
      return `<tr>${cells}</tr>`;
    })
    .join("");

  return `
    <div class="table-wrap">
      <table class="table">
        <thead>
          <tr>${header}</tr>
        </thead>
        <tbody>${body}</tbody>
      </table>
    </div>
  `;
}

export function renderPagination(pagination) {
  const page = Number(pagination?.page || 1);
  const pages = Number(pagination?.pages || 1);
  const total = Number(pagination?.total || 0);
  const pageSize = Number(pagination?.page_size || 25);
  const hasPrevious = Boolean(pagination?.has_previous);
  const hasNext = Boolean(pagination?.has_next);

  return `
    <div class="pagination">
      <button
        class="button button-secondary"
        data-pagination-action="previous"
        ${hasPrevious ? "" : "disabled"}
        type="button"
      >
        Назад
      </button>
      <div class="pagination-meta">
        <strong>${escapeHtml(page)} / ${escapeHtml(pages || 1)}</strong>
        <span class="muted">total: ${escapeHtml(total)}, page_size: ${escapeHtml(pageSize)}</span>
      </div>
      <button
        class="button button-secondary"
        data-pagination-action="next"
        ${hasNext ? "" : "disabled"}
        type="button"
      >
        Вперёд
      </button>
    </div>
  `;
}

export function preferredColumnsForTable(tableName) {
  const columns = {
    employees: [
      "employee_id",
      "name",
      "role",
      "grade",
      "skills",
      "current_workload",
      "fatigue_score",
      "availability_score",
    ],
    tasks: [
      "task_id",
      "title",
      "project_id",
      "status",
      "priority",
      "complexity",
      "estimated_hours",
      "required_skills",
    ],
    assignment_history: [
      "assignment_id",
      "employee_id",
      "task_id",
      "planned_hours",
      "actual_hours",
      "quality_score",
      "deadline_status",
      "outcome_label",
    ],
    training_pairs: [
      "pair_id",
      "task_id",
      "employee_id",
      "label",
      "target_score",
      "target_mode",
      "split",
    ],
  };

  return columns[tableName] || [];
}