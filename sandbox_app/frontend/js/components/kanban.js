function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

const STATUS_ORDER = ["todo", "in_progress", "review", "done", "blocked", "failed"];
const STATUS_LABELS = {
  todo: "К выполнению",
  in_progress: "В работе",
  review: "Проверка",
  done: "Готово",
  blocked: "Заблокировано",
  failed: "Не выполнено",
};

function taskTitle(task) {
  return task.title || task.name || task.description || task.task_id || "Задача без названия";
}

function renderTaskCard(task) {
  return `
    <article class="kanban-card">
      <div class="kanban-card-title">${escapeHtml(taskTitle(task))}</div>
      <div class="kanban-card-meta">
        <span>${escapeHtml(task.task_id || "")}</span>
        <span>${escapeHtml(task.priority || "")}</span>
      </div>
      <p class="muted">${escapeHtml(task.project_id || "")}</p>
    </article>
  `;
}

export function renderKanbanBoard(kanbanPayload) {
  const columns = kanbanPayload?.columns || {};
  const statusNames = Array.from(new Set([...STATUS_ORDER, ...Object.keys(columns)]));

  const renderedColumns = statusNames
    .map((status) => {
      const tasks = Array.isArray(columns[status]) ? columns[status] : [];
      const cards = tasks.slice(0, 60).map(renderTaskCard).join("");
      const hiddenCount = Math.max(0, tasks.length - 60);

      return `
        <section class="kanban-column">
          <h3>
            <span>${escapeHtml(STATUS_LABELS[status] || status)}</span>
            <strong>${escapeHtml(tasks.length)}</strong>
          </h3>
          ${cards || '<p class="muted">Нет задач</p>'}
          ${
            hiddenCount > 0
              ? `<p class="muted">Скрыто ещё ${escapeHtml(hiddenCount)} задач.</p>`
              : ""
          }
        </section>
      `;
    })
    .join("");

  return `<div class="kanban">${renderedColumns}</div>`;
}
