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

const COLUMN_LABELS = {
  employee_id: "ID сотрудника",
  name: "Сотрудник",
  role: "Роль",
  grade: "Уровень",
  skills: "Навыки",
  current_workload: "Загрузка",
  fatigue_score: "Усталость",
  availability_score: "Доступность",
  task_id: "ID задачи",
  title: "Задача",
  project_id: "Проект",
  status: "Статус",
  priority: "Приоритет",
  complexity: "Сложность",
  estimated_hours: "Оценка часов",
  required_skills: "Требования",
  assignment_id: "ID назначения",
  planned_hours: "План",
  actual_hours: "Факт",
  quality_score: "Качество",
  deadline_status: "Дедлайн",
  outcome_label: "Результат",
  pair_id: "ID пары",
  label: "Метка",
  target_score: "Целевой балл",
  target_mode: "Цель",
  split: "Выборка",
  model_name: "Модель",
  session_id: "Сессия",
  dataset_id: "Датасет",
  dataset_kind: "Тип",
  feature_count: "Признаки",
  rows: "Строки",
  completed_at: "Завершено",
  created_at: "Создано",
};

function columnLabel(column) {
  return COLUMN_LABELS[column] || column;
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
          <p class="muted">Измените фильтры, поиск или выберите другой датасет.</p>
        </div>
      </div>
    `;
  }

  const columns = inferColumns(rows, preferredColumns);
  const header = columns.map((column) => `<th>${escapeHtml(columnLabel(column))}</th>`).join("");
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
        <span class="muted">всего: ${escapeHtml(total)}, на странице: ${escapeHtml(pageSize)}</span>
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
