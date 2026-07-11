import { api } from "../api.js";

const STATUSES = ["todo", "in_progress", "review", "done", "blocked", "failed"];
const RECOMMENDATION_STATUSES = ["todo", "in_progress", "review", "blocked"];
const STATUS_LABELS = {
  todo: "К выполнению",
  in_progress: "В работе",
  review: "Проверка",
  done: "Готово",
  blocked: "Заблокировано",
  failed: "Не выполнено",
};
const STATUS_LABELS_EN = {
  todo: "To Do",
  in_progress: "In Progress",
  review: "Review",
  done: "Done",
  blocked: "Blocked",
  failed: "Failed",
};
const PRIORITIES = ["low", "medium", "high", "critical"];
const MODEL_NAMES = [
  "baseline_rule_based",
  "sgd_classifier",
  "logistic_regression",
  "random_forest",
  "hist_gradient_boosting",
  "torch_mlp",
];

const state = {
  datasets: null,
  savedBoards: [],
  testCases: [],
  trainingSessions: [],
  selectedSavedLabId: "",
  currentLabId: "",
  labName: "Kanban lab board",
  selectedDatasetValue: "",
  selectedTestCaseId: "",
  selectedTrainingSessionId: "",
  selectedModelName: "logistic_regression",
  recommendationMode: "balanced",
  topK: 3,
  useLlm: false,
  team: [],
  history: [],
  tasks: [],
  originalTeam: [],
  originalHistory: [],
  originalTasks: [],
  recommendations: {},
  explanations: {},
  selectedTaskId: "",
  draggingTaskId: "",
  root: null,
};

function isEnglishUi() {
  const saved = window.localStorage?.getItem("sandbox:language");
  const language = saved || document.documentElement.lang || navigator.language || "en";
  return String(language).toLowerCase().startsWith("en");
}

function textByLanguage(ru, en) {
  return isEnglishUi() ? en : ru;
}

function statusLabel(status) {
  return isEnglishUi()
    ? STATUS_LABELS_EN[status] || status
    : STATUS_LABELS[status] || status;
}

function htmlEscape(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function clone(value) {
  return JSON.parse(JSON.stringify(value ?? null));
}

function numberText(value, digits = 2) {
  const numeric = Number(value);
  return Number.isFinite(numeric) ? numeric.toFixed(digits) : "—";
}

function percentText(value) {
  const numeric = Number(value);
  return Number.isFinite(numeric) ? `${Math.round(numeric * 100)}%` : "—";
}

function clamp01(value) {
  const numeric = Number(value);
  if (!Number.isFinite(numeric)) {
    return 0;
  }
  return Math.max(0, Math.min(1, numeric));
}

function listValue(value) {
  if (Array.isArray(value)) {
    return value.map((item) => String(item).trim()).filter(Boolean);
  }

  if (typeof value === "string") {
    const trimmed = value.trim();
    if (!trimmed) {
      return [];
    }

    try {
      const parsed = JSON.parse(trimmed);
      if (Array.isArray(parsed)) {
        return parsed.map((item) => String(item).trim()).filter(Boolean);
      }
    } catch (_error) {
      return trimmed.split(",").map((item) => item.trim()).filter(Boolean);
    }

    return trimmed.split(",").map((item) => item.trim()).filter(Boolean);
  }

  return [];
}

function uniqueSorted(values) {
  return [...new Set(values.map((item) => String(item ?? "").trim()).filter(Boolean))].sort(
    (left, right) => left.localeCompare(right, undefined, { numeric: true, sensitivity: "base" }),
  );
}

function objectValue(value) {
  if (value && typeof value === "object" && !Array.isArray(value)) {
    return value;
  }

  if (typeof value === "string" && value.trim()) {
    try {
      const parsed = JSON.parse(value);
      return parsed && typeof parsed === "object" && !Array.isArray(parsed)
        ? parsed
        : {};
    } catch (_error) {
      return {};
    }
  }

  return {};
}

function tagList(values, emptyLabel = "нет") {
  const items = listValue(values);

  if (!items.length) {
    return `<span class="muted">${htmlEscape(emptyLabel)}</span>`;
  }

  return items.map((item) => `<span class="tag">${htmlEscape(item)}</span>`).join("");
}

function renderInlineMarkdown(value) {
  return htmlEscape(value)
    .replace(/`([^`]+)`/g, "<code>$1</code>")
    .replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>")
    .replace(/__([^_]+)__/g, "<strong>$1</strong>")
    .replace(/\*([^*]+)\*/g, "<em>$1</em>");
}

function readableMarkdownValue(value) {
  if (Array.isArray(value)) {
    return value
      .map((item) => {
        if (item && typeof item === "object") {
          return item.message || item.text || item.explanation || JSON.stringify(item);
        }
        return item;
      })
      .map((item) => String(item ?? "").trim())
      .filter(Boolean)
      .map((item) => `- ${item}`)
      .join("\n");
  }

  if (value && typeof value === "object") {
    return Object.entries(value)
      .map(([key, item]) => `${key}: ${item}`)
      .join("\n");
  }

  return String(value ?? "");
}

function renderMarkdownText(value) {
  const lines = readableMarkdownValue(value).replaceAll("\r\n", "\n").split("\n");
  const output = [];
  let paragraph = [];
  let listType = "";
  let listItems = [];

  const flushParagraph = () => {
    if (!paragraph.length) {
      return;
    }
    output.push(`<p>${renderInlineMarkdown(paragraph.join(" "))}</p>`);
    paragraph = [];
  };

  const flushList = () => {
    if (!listItems.length || !listType) {
      return;
    }
    output.push(
      `<${listType}>${listItems
        .map((item) => `<li>${renderInlineMarkdown(item)}</li>`)
        .join("")}</${listType}>`,
    );
    listType = "";
    listItems = [];
  };

  lines.forEach((line) => {
    const trimmed = line.trim();
    if (!trimmed) {
      flushParagraph();
      flushList();
      return;
    }

    const unordered = trimmed.match(/^[-*]\s+(.+)$/);
    if (unordered) {
      flushParagraph();
      if (listType && listType !== "ul") {
        flushList();
      }
      listType = "ul";
      listItems.push(unordered[1]);
      return;
    }

    flushList();
    paragraph.push(trimmed);
  });

  flushParagraph();
  flushList();
  return `<div class="markdown-text">${output.join("")}</div>`;
}

function toast(message, type = "info") {
  window.dispatchEvent(
    new CustomEvent("sandbox-toast", {
      detail: {
        title: type === "error" ? "Ошибка канбан-лаборатории" : "Канбан-лаборатория",
        message,
        type,
      },
    }),
  );
}

function startLongTaskToast(options) {
  const detail = { options, controller: null };
  window.dispatchEvent(new CustomEvent("sandbox-long-task-start", { detail }));
  return detail.controller || {
    update: () => {},
    done: () => {},
    error: () => {},
  };
}

function allDatasets(payload) {
  return [
    ...(payload?.generated || []).map((item) => ({ ...item, dataset_kind: "generated" })),
    ...(payload?.imported || []).map((item) => ({ ...item, dataset_kind: "imported" })),
  ];
}

function datasetOptionValue(dataset) {
  return `${dataset.dataset_kind}:${dataset.dataset_id}`;
}

function parseDatasetValue(value) {
  const [datasetKind, ...datasetIdParts] = String(value || "").split(":");
  return {
    datasetKind: datasetKind || "generated",
    datasetId: datasetIdParts.join(":"),
  };
}

function selectedValue(id) {
  return document.getElementById(id)?.value || "";
}

function selectedValues(id) {
  const element = document.getElementById(id);

  if (element?.selectedOptions) {
    return [...element.selectedOptions].map((option) => option.value).filter(Boolean);
  }

  const group = [...document.querySelectorAll("[data-checkbox-group]")].find(
    (item) => item.dataset.checkboxGroup === id,
  );

  return [...(group?.querySelectorAll('input[type="checkbox"]:checked') || [])]
    .map((input) => input.value)
    .filter(Boolean);
}

function numericValue(id, fallback) {
  const value = Number(selectedValue(id));
  return Number.isFinite(value) ? value : fallback;
}

function checkboxValue(id) {
  return Boolean(document.getElementById(id)?.checked);
}

function selectInput(id, label, options, value = "") {
  return `
    <label>
      <span>${htmlEscape(label)}</span>
      <select id="${htmlEscape(id)}">
        ${options
          .map(
            (option) => `
              <option value="${htmlEscape(option.value)}" ${
                String(option.value) === String(value) ? "selected" : ""
              }>
                ${htmlEscape(option.label)}
              </option>
            `,
          )
          .join("")}
      </select>
    </label>
  `;
}

function textInput(id, label, value = "", placeholder = "") {
  return `
    <label>
      <span>${htmlEscape(label)}</span>
      <input id="${htmlEscape(id)}" value="${htmlEscape(value)}" placeholder="${htmlEscape(placeholder)}">
    </label>
  `;
}

function numberInput(id, label, value, attrs = "") {
  return `
    <label>
      <span>${htmlEscape(label)}</span>
      <input id="${htmlEscape(id)}" type="number" value="${htmlEscape(value)}" ${attrs}>
    </label>
  `;
}

function checkboxGroupInput(id, label, options, values = [], disabled = false) {
  const selectedValues = new Set(values.map((item) => String(item)));
  const disabledAttr = disabled ? "disabled" : "";
  return `
    <fieldset class="checkbox-picker" data-checkbox-group="${htmlEscape(id)}" id="${htmlEscape(id)}">
      <legend>${htmlEscape(label)}</legend>
      <div class="checkbox-picker-list">
        ${options
          .map(
            (option) => `
              <label class="checkbox-pill">
                <input
                  type="checkbox"
                  value="${htmlEscape(option.value)}"
                  ${selectedValues.has(String(option.value)) ? "checked" : ""}
                  ${disabledAttr}
                >
                <span>${htmlEscape(option.label)}</span>
              </label>
            `,
          )
          .join("")}
      </div>
      <small class="muted">Выберите один или несколько пунктов из словаря текущего набора.</small>
    </fieldset>
  `;
}

function datasetOptions() {
  const datasets = allDatasets(state.datasets);
  if (!datasets.length) {
    return [{ label: "Нет датасетов", value: "" }];
  }
  return datasets.map((dataset) => ({
    label: `${dataset.dataset_id} · ${dataset.dataset_kind}`,
    value: datasetOptionValue(dataset),
  }));
}

function testCaseOptions() {
  if (!state.testCases.length) {
    return [{ label: "Нет проверочных наборов", value: "" }];
  }
  return state.testCases.map((item) => ({
    label: `${item.test_case_id} · ${textByLanguage("задач", "tasks")}: ${
      item.active_tasks_count ?? item.active_tasks ?? "—"
    }`,
    value: item.test_case_id,
  }));
}

function savedBoardOptions() {
  if (!state.savedBoards.length) {
    return [{ label: "Нет сохраненных досок", value: "" }];
  }

  return state.savedBoards.map((item) => ({
    label: `${item.name || item.lab_id} · ${textByLanguage("задач", "tasks")}: ${
      item.task_count ?? "—"
    }`,
    value: item.lab_id,
  }));
}

function trainingSessionOptions() {
  if (!state.trainingSessions.length) {
    return [{ label: "Нет обученных сессий", value: "" }];
  }
  return state.trainingSessions.map((item) => ({
    label: `${item.session_id} · ${item.status || textByLanguage("статус неизвестен", "status unknown")}`,
    value: item.session_id,
  }));
}

function modelOptions() {
  return MODEL_NAMES.map((name) => ({ label: name, value: name }));
}

function manualTaskDictionaries() {
  const projectIds = uniqueSorted([
    ...state.tasks.map((task) => task.project_id),
    ...state.originalTasks.map((task) => task.project_id),
    ...state.history.map((item) => item.project_id),
    ...state.originalHistory.map((item) => item.project_id),
  ]);
  const taskTypes = uniqueSorted([
    ...state.tasks.map((task) => task.task_type),
    ...state.originalTasks.map((task) => task.task_type),
    ...state.history.map((item) => item.task_type),
    ...state.originalHistory.map((item) => item.task_type),
    ...state.team.map((employee) => objectValue(employee.custom_features).preferred_task_type),
    ...state.originalTeam.map((employee) => objectValue(employee.custom_features).preferred_task_type),
  ]);
  const skills = uniqueSorted([
    ...state.tasks.flatMap((task) => listValue(task.required_skills)),
    ...state.originalTasks.flatMap((task) => listValue(task.required_skills)),
    ...state.history.flatMap((item) => listValue(item.required_skills)),
    ...state.originalHistory.flatMap((item) => listValue(item.required_skills)),
    ...state.team.flatMap((employee) => listValue(employee.skills)),
    ...state.originalTeam.flatMap((employee) => listValue(employee.skills)),
    ...state.team.flatMap((employee) => listValue(employee.learning_goals)),
    ...state.originalTeam.flatMap((employee) => listValue(employee.learning_goals)),
  ]);
  const roles = uniqueSorted([
    ...state.team.map((employee) => employee.role),
    ...state.originalTeam.map((employee) => employee.role),
  ]);
  const grades = uniqueSorted([
    ...state.team.map((employee) => employee.grade),
    ...state.originalTeam.map((employee) => employee.grade),
  ]);

  return { projectIds, taskTypes, skills, roles, grades };
}

function recommendationModeOptions() {
  return [
    { label: "Сбалансированно", value: "balanced" },
    { label: "Лучшее качество", value: "best_quality" },
    { label: "Быстрее доставка", value: "fastest_delivery" },
    { label: "Развитие сотрудника", value: "best_learning" },
    { label: "Осторожнее к рискам", value: "risk_aware" },
  ];
}

function taskTitle(task) {
  return task.title || task.name || task.description || task.task_id || "Задача без названия";
}

function tasksByStatus() {
  const columns = Object.fromEntries(STATUSES.map((status) => [status, []]));
  state.tasks.forEach((task) => {
    const status = STATUSES.includes(String(task.status)) ? String(task.status) : "todo";
    columns[status].push(task);
  });
  return columns;
}

function sourceStats() {
  const columns = tasksByStatus();
  const recommendable = RECOMMENDATION_STATUSES.reduce(
    (total, status) => total + (columns[status]?.length || 0),
    0,
  );
  return {
    tasks: state.tasks.length,
    people: state.team.length,
    recommendable,
  };
}

function renderSourcePanel() {
  return `
    <section class="panel">
      <div class="section-heading">
        <div>
          <h3>Источник лаборатории</h3>
          <p class="muted">
            Загружается копия задач и команды. Все перемещения и ручные задачи живут только в этой вкладке.
          </p>
        </div>
        <span class="pill">оригинал не меняется</span>
      </div>

      <div class="form-grid">
        ${textInput("labBoardName", "Название лабораторной доски", state.labName)}
        ${selectInput("savedLabBoardId", "Сохраненная доска", savedBoardOptions(), state.selectedSavedLabId)}
        ${selectInput("labTestCaseId", "Проверочный набор", testCaseOptions(), state.selectedTestCaseId)}
        ${selectInput("labDatasetValue", "Датасет для новой копии", datasetOptions(), state.selectedDatasetValue)}
        ${selectInput("labTrainingSessionId", "Сессия обучения", trainingSessionOptions(), state.selectedTrainingSessionId)}
        ${selectInput("labModelName", "Модель", modelOptions(), state.selectedModelName)}
        ${selectInput("labRecommendationMode", "Режим рекомендации", recommendationModeOptions(), state.recommendationMode)}
        ${numberInput("labTopK", "Кандидатов на задачу", state.topK, "min='1' max='25'")}
      </div>

      <label class="checkbox-label">
        <input id="labUseLlm" type="checkbox" ${state.useLlm ? "checked" : ""}>
        <span>Добавлять LLM-объяснение при раскрытии задачи</span>
      </label>

      <div class="actions-row">
        <button id="loadLabSource" type="button">Загрузить копию набора</button>
        <button id="loadSavedLabBoard" class="button-secondary" type="button">
          Загрузить сохраненную доску
        </button>
        <button id="saveLabBoard" class="button-secondary" type="button">
          Сохранить текущую доску
        </button>
        <button id="deleteSavedLabBoard" class="button-danger" type="button">
          Удалить сохраненную
        </button>
        <button id="createLabCopyFromDataset" class="button-secondary" type="button">
          Создать лабораторную копию из датасета
        </button>
        <button id="resetLabBoard" class="button-secondary" type="button">
          Сбросить изменения
        </button>
        <button id="runKanbanRecommendations" type="button">
          Принять канбан и рассчитать рекомендации
        </button>
      </div>
    </section>
  `;
}

function renderStatsPanel() {
  const stats = sourceStats();
  return `
    <section class="summary-grid kanban-lab-summary">
      <div class="summary-card">
        <span>Сотрудники</span>
        <strong>${htmlEscape(stats.people)}</strong>
      </div>
      <div class="summary-card">
        <span>Задачи на доске</span>
        <strong>${htmlEscape(stats.tasks)}</strong>
      </div>
      <div class="summary-card">
        <span>К рекомендации</span>
        <strong>${htmlEscape(stats.recommendable)}</strong>
      </div>
      <div class="summary-card">
        <span>Рекомендации</span>
        <strong>${htmlEscape(Object.keys(state.recommendations).length)}</strong>
      </div>
    </section>
  `;
}

function recommendationMini(taskId) {
  const recommendation = state.recommendations[taskId];
  const candidates = recommendation?.candidates || [];

  if (!candidates.length) {
    return '<span class="muted">кандидаты не рассчитаны</span>';
  }

  return candidates
    .slice(0, 3)
    .map(
      (candidate, index) => `
        <span class="candidate-chip">
          #${index + 1} ${htmlEscape(candidate.employee_id)}
        </span>
      `,
    )
    .join("");
}

function renderTaskCard(task) {
  return `
    <article
      class="kanban-lab-card ${state.selectedTaskId === task.task_id ? "active" : ""}"
      draggable="true"
      data-task-id="${htmlEscape(task.task_id)}"
      role="button"
      tabindex="0"
    >
      <div class="kanban-card-title">${htmlEscape(taskTitle(task))}</div>
      <div class="kanban-card-meta">
        <span>${htmlEscape(task.task_id)}</span>
        <span>${htmlEscape(task.priority || "medium")}</span>
      </div>
      <div class="kanban-card-meta">
        <span>${htmlEscape(task.task_type || "task")}</span>
        <span>${numberText(task.estimated_hours, 1)} ${textByLanguage("ч", "h")}</span>
      </div>
      <div class="kanban-tags">${tagList(task.required_skills, "теги не указаны")}</div>
      <div class="candidate-chip-row">${recommendationMini(task.task_id)}</div>
    </article>
  `;
}

function renderColumnControls(status) {
  return `
    <div class="kanban-column-tools">
      <select data-column-target="${htmlEscape(status)}">
        ${STATUSES.filter((item) => item !== status)
          .map(
            (item) => `
              <option value="${htmlEscape(item)}">${htmlEscape(statusLabel(item))}</option>
            `,
          )
          .join("")}
      </select>
      <button class="button-secondary" type="button" data-move-column="${htmlEscape(status)}">
        Перенести столбец
      </button>
      <button class="button-danger" type="button" data-clear-column="${htmlEscape(status)}">
        Очистить
      </button>
    </div>
  `;
}

function renderBoard() {
  if (!state.tasks.length) {
    return `
      <section class="panel">
        <h3>Канбан-доска</h3>
        <p class="muted">Загрузите проверочный набор или создайте лабораторную копию из датасета.</p>
      </section>
    `;
  }

  const columns = tasksByStatus();
  return `
    <section class="panel kanban-lab-panel">
      <div class="section-heading">
        <div>
          <h3>Канбан-доска эксперимента</h3>
          <p class="muted">
            Перетаскивайте карточки между столбцами или переносите/очищайте столбец целиком.
          </p>
        </div>
      </div>

      <div class="kanban-lab-board">
        ${STATUSES
          .map(
            (status) => `
              <section class="kanban-lab-column" data-status="${htmlEscape(status)}">
                <h3>
                  <span>${htmlEscape(statusLabel(status))}</span>
                  <strong title="${htmlEscape(columns[status].length)}">${htmlEscape(columns[status].length)}</strong>
                </h3>
                ${renderColumnControls(status)}
                <div class="kanban-dropzone">
                  ${
                    columns[status].length
                      ? columns[status].map(renderTaskCard).join("")
                      : '<p class="muted empty-column">Нет задач</p>'
                  }
                </div>
              </section>
            `,
          )
          .join("")}
      </div>
    </section>
  `;
}

function renderManualTaskPanel() {
  const dictionaries = manualTaskDictionaries();
  const hasDictionary =
    Boolean(state.tasks.length) &&
    Boolean(dictionaries.projectIds.length) &&
    Boolean(dictionaries.taskTypes.length) &&
    Boolean(dictionaries.skills.length);
  const projectOptions = hasDictionary
    ? dictionaries.projectIds.map((item) => ({ label: item, value: item }))
    : [{ label: "Сначала загрузите набор", value: "" }];
  const taskTypeOptions = hasDictionary
    ? dictionaries.taskTypes.map((item) => ({ label: item, value: item }))
    : [{ label: "Сначала загрузите набор", value: "" }];
  const skillOptions = hasDictionary
    ? dictionaries.skills.map((item) => ({ label: item, value: item }))
    : [{ label: "Сначала загрузите набор", value: "" }];
  const disabledAttr = hasDictionary ? "" : "disabled";

  return `
    <section class="panel">
      <div class="section-heading">
        <div>
          <h3>Добавить ручную задачу</h3>
          <p class="muted">
            Заполните поля из словаря текущего набора, чтобы модель видела знакомые проекты, типы и навыки.
          </p>
        </div>
      </div>

      <div class="form-grid">
        ${textInput("manualTaskTitle", "Название", "", "например: Срочный security review")}
        ${selectInput("manualTaskType", "Тип задачи", taskTypeOptions, taskTypeOptions[0]?.value || "")}
        ${selectInput("manualTaskPriority", "Приоритет", PRIORITIES.map((item) => ({ label: item, value: item })), "medium")}
        ${numberInput("manualTaskComplexity", "Сложность 0..1", 0.55, "min='0' max='1' step='0.01'")}
        ${numberInput("manualTaskHours", "Оценка часов", 8, "min='1' max='240' step='1'")}
        ${selectInput("manualTaskProject", "Проект", projectOptions, projectOptions[0]?.value || "")}
        ${checkboxGroupInput("manualTaskSkills", "Теги / навыки", skillOptions, [], !hasDictionary)}
      </div>

      <div class="actions-row">
        <button id="addManualTask" type="button" ${disabledAttr}>Добавить в To Do</button>
      </div>
    </section>
  `;
}

function renderEmployeePreview() {
  if (!state.team.length) {
    return `<p class="muted">В лабораторной копии пока нет сотрудников.</p>`;
  }

  return `
    <div class="employee-grid">
      ${state.team
        .map(
          (employee) => `
            <article class="employee-preview-card">
              <div class="employee-card-head">
                <div>
                  <strong>${htmlEscape(employee.employee_id || employee.name)}</strong>
                  <span>${htmlEscape(employee.role || "роль не указана")} · ${htmlEscape(employee.grade || "grade")}</span>
                </div>
                <button
                  class="button-danger icon-text-button"
                  type="button"
                  data-delete-employee-card="${htmlEscape(employee.employee_id)}"
                >
                  Удалить
                </button>
              </div>
              <div class="kanban-tags">${tagList(employee.skills, "навыки не указаны")}</div>
            </article>
          `,
        )
        .join("")}
    </div>
  `;
}

function renderTeamPanel() {
  const dictionaries = manualTaskDictionaries();
  const hasDictionary =
    Boolean(dictionaries.roles.length) &&
    Boolean(dictionaries.grades.length) &&
    Boolean(dictionaries.skills.length);
  const roleOptions = hasDictionary
    ? dictionaries.roles.map((item) => ({ label: item, value: item }))
    : [{ label: "Сначала загрузите набор", value: "" }];
  const gradeOptions = hasDictionary
    ? dictionaries.grades.map((item) => ({ label: item, value: item }))
    : [{ label: "Сначала загрузите набор", value: "" }];
  const skillOptions = hasDictionary
    ? dictionaries.skills.map((item) => ({ label: item, value: item }))
    : [{ label: "Сначала загрузите набор", value: "" }];
  const disabledAttr = hasDictionary ? "" : "disabled";
  const noTeamAttr = state.team.length ? "" : "disabled";

  return `
    <section class="panel">
      <div class="section-heading">
        <div>
          <h3>Персонал лаборатории</h3>
          <p class="muted">
            Меняйте сотрудников только в копии: удаляйте лишних и добавляйте новых с навыками из текущего набора.
          </p>
        </div>
        <span class="pill">${htmlEscape(state.team.length)} ${textByLanguage("сотрудников", "employees")}</span>
      </div>

      <div class="form-grid">
        ${textInput("manualEmployeeName", "ID / название нового сотрудника", "", "например: emp_lab_security_001")}
        ${selectInput("manualEmployeeRole", "Роль", roleOptions, roleOptions[0]?.value || "")}
        ${selectInput("manualEmployeeGrade", "Грейд", gradeOptions, gradeOptions[0]?.value || "")}
        ${numberInput("manualEmployeeAvailability", "Доступность 0..1", 0.85, "min='0' max='1' step='0.01'")}
        ${numberInput("manualEmployeeWorkload", "Текущая нагрузка 0..1", 0.25, "min='0' max='1' step='0.01'")}
        ${numberInput("manualEmployeeFatigue", "Усталость 0..1", 0.2, "min='0' max='1' step='0.01'")}
        ${numberInput("manualEmployeeQuality", "Качество 0..1", 0.8, "min='0' max='1' step='0.01'")}
        ${numberInput("manualEmployeeSpeed", "Скорость 0..1", 0.75, "min='0' max='1' step='0.01'")}
        ${numberInput("manualEmployeeReliability", "Надежность дедлайнов 0..1", 0.8, "min='0' max='1' step='0.01'")}
        ${checkboxGroupInput("manualEmployeeSkills", "Навыки сотрудника", skillOptions, [], !hasDictionary)}
      </div>

      <div class="actions-row">
        <button id="addManualEmployee" type="button" ${disabledAttr}>Добавить сотрудника</button>
        <button id="clearTeam" class="button-danger" type="button" ${noTeamAttr}>Удалить всех сотрудников</button>
      </div>

      ${renderEmployeePreview()}
    </section>
  `;
}

function renderTaskRequirementPanel(task) {
  if (!task) {
    return "";
  }

  const customRows = Object.entries(objectValue(task.custom_features)).slice(0, 8);
  return `
    <section class="panel task-requirement-panel">
      <div class="section-heading">
        <div>
          <h3>Что требуется в задаче</h3>
          <p class="muted">
            ${htmlEscape(task.task_id || "задача")}
            · ${htmlEscape(task.task_type || "тип не указан")}
            · ${htmlEscape(task.priority || "приоритет не указан")}
          </p>
        </div>
        <span class="pill">${htmlEscape(statusLabel(task.status) || task.status || textByLanguage("статус неизвестен", "status unknown"))}</span>
      </div>

      <div class="task-facts-grid">
        <div><span>Проект</span><strong>${htmlEscape(task.project_id || "—")}</strong></div>
        <div><span>Сложность</span><strong>${numberText(task.complexity, 3)}</strong></div>
        <div><span>Оценка часов</span><strong>${numberText(task.estimated_hours, 1)}</strong></div>
        <div><span>Дедлайн</span><strong>${htmlEscape(task.due_at || task.deadline || "—")}</strong></div>
      </div>

      <div class="skill-block">
        <strong>Требуемые навыки / теги</strong>
        <div>${tagList(task.required_skills, "теги не указаны")}</div>
      </div>

      ${
        customRows.length
          ? `
            <div class="task-custom-grid">
              ${customRows
                .map(
                  ([key, value]) => `
                    <div>
                      <span>${htmlEscape(key)}</span>
                      <strong>${htmlEscape(value)}</strong>
                    </div>
                  `,
                )
                .join("")}
            </div>
          `
          : ""
      }
    </section>
  `;
}

function taskChartValues(task) {
  const customFeatures = objectValue(task?.custom_features);
  const technicalRisk = customFeatures.technical_risk ?? customFeatures.risk ?? task?.complexity ?? 0.5;
  const priority = {
    low: 0.25,
    medium: 0.5,
    high: 0.75,
    critical: 1,
  }[String(task?.priority || "").toLowerCase()] || 0.5;

  return [
    1,
    priority,
    clamp01(1 - Number(task?.estimated_hours || 0) / 80),
    clamp01(1 - Number(technicalRisk || 0.5)),
    clamp01(1 - Number(task?.complexity || 0.5) * 0.45),
  ];
}

function candidateChartValues(candidate) {
  const factors = candidate?.factors || {};
  return [
    clamp01(factors.skill_match_ratio),
    clamp01(factors.quality_fit_score),
    clamp01(factors.speed_fit_score),
    clamp01(factors.risk_fit_score),
    clamp01(1 - Number(factors.availability_gap || 0)),
  ];
}

function radarPoint(index, total, value, center = 110, radius = 78) {
  const angle = -Math.PI / 2 + (Math.PI * 2 * index) / total;
  const resolvedRadius = radius * clamp01(value);
  return [center + Math.cos(angle) * resolvedRadius, center + Math.sin(angle) * resolvedRadius];
}

function radarPolyline(values) {
  return values.map((value, index) => radarPoint(index, values.length, value).join(",")).join(" ");
}

function renderTaskCandidateFitChart(task, candidates) {
  const rows = Array.isArray(candidates) ? candidates.slice(0, 5) : [];
  if (!task || !rows.length) {
    return "";
  }

  const labels = ["Навыки", "Качество", "Скорость", "Низкий риск", "Доступность"];
  const colors = ["#007aff", "#34c759", "#ff9500", "#af52de", "#ff3b30"];
  const taskValues = taskChartValues(task);
  const candidateLines = rows.map((candidate, index) => ({
    candidate,
    color: colors[index % colors.length],
    values: candidateChartValues(candidate),
  }));

  return `
    <section class="panel">
      <div class="section-heading">
        <div>
          <h3>График соответствия задаче</h3>
          <p class="muted">Пунктир — требования задачи, цветные линии — кандидаты.</p>
        </div>
      </div>
      <div class="fit-chart-layout">
        <svg class="fit-radar" viewBox="0 0 220 220" role="img" aria-label="Сравнение задачи и кандидатов">
          ${[0.25, 0.5, 0.75, 1]
            .map(
              (value) => `
                <polygon class="fit-radar-grid" points="${radarPolyline(Array(labels.length).fill(value))}" />
              `,
            )
            .join("")}
          ${labels
            .map((label, index) => {
              const [x, y] = radarPoint(index, labels.length, 1.13);
              return `<text class="fit-radar-label" x="${x}" y="${y}">${htmlEscape(label)}</text>`;
            })
            .join("")}
          <polygon class="fit-radar-task" points="${radarPolyline(taskValues)}" />
          ${candidateLines
            .map(
              (line) => `
                <polyline
                  class="fit-radar-line"
                  points="${radarPolyline(line.values)} ${radarPoint(0, line.values.length, line.values[0]).join(",")}"
                  style="stroke: ${line.color};"
                />
              `,
            )
            .join("")}
        </svg>
        <div class="fit-chart-legend">
          <div class="fit-legend-row">
            <span class="fit-legend-line task"></span>
            <strong>Требования задачи</strong>
          </div>
          ${candidateLines
            .map(
              (line, index) => `
                <div class="fit-legend-row">
                  <span class="fit-legend-line" style="background: ${line.color};"></span>
                  <strong>#${index + 1} ${htmlEscape(line.candidate.name || line.candidate.employee_id)}</strong>
                  <span>score ${numberText(line.candidate.score, 3)} · ${textByLanguage("навыки", "skills")} ${percentText(line.values[0])}</span>
                </div>
              `,
            )
            .join("")}
        </div>
      </div>
    </section>
  `;
}

function renderCandidates(recommendation) {
  const candidates = recommendation?.candidates || [];
  if (!candidates.length) {
    return `
      <section class="panel">
        <h3>Кандидаты</h3>
        <p class="muted">Для этой задачи рекомендации еще не рассчитаны.</p>
      </section>
    `;
  }

  return `
    <section class="panel">
      <div class="section-heading">
        <div>
          <h3>Кандидаты модели</h3>
          <p class="muted">Мини-рейтинг по текущему состоянию канбан-доски.</p>
        </div>
      </div>
      <div class="recommendation-card-grid">
        ${candidates
          .map(
            (candidate, index) => {
              const factors = candidate.factors || {};
              return `
                <article class="recommendation-card">
                  <span class="candidate-rank">#${index + 1}</span>
                  <div class="candidate-main">
                    <div>
                      <h4>${htmlEscape(candidate.name || candidate.employee_id)}</h4>
                      <p class="muted">${htmlEscape(candidate.role || "роль не указана")} · ${htmlEscape(candidate.grade || "grade")}</p>
                    </div>
                    <strong class="candidate-score">${numberText(candidate.score, 3)}</strong>
                  </div>
                  <div class="score-breakdown">
                    <div><span>Навыки</span><strong>${percentText(factors.skill_match_ratio)}</strong></div>
                    <div><span>Качество</span><strong>${percentText(factors.quality_fit_score)}</strong></div>
                    <div><span>Скорость</span><strong>${percentText(factors.speed_fit_score)}</strong></div>
                    <div><span>Риск-fit</span><strong>${percentText(factors.risk_fit_score)}</strong></div>
                  </div>
                  <div class="skill-block">
                    <strong>Совпало</strong>
                    <div>${tagList(candidate.matched_skills, "нет совпадений")}</div>
                  </div>
                  <div class="skill-block">
                    <strong>Не хватает</strong>
                    <div>${tagList(candidate.missing_skills, "нет пробелов")}</div>
                  </div>
                </article>
              `;
            },
          )
          .join("")}
      </div>
    </section>
  `;
}

function renderExplanation(explanation) {
  if (!explanation) {
    return "";
  }

  const candidateExplanations = Array.isArray(explanation.candidate_explanations)
    ? explanation.candidate_explanations
    : [];

  return `
    <section class="panel">
      <div class="section-heading">
        <div>
          <h3>LLM-объяснение</h3>
          <p class="muted">${explanation.llm_used ? "Qwen/Ollama" : "Локальное объяснение"}</p>
        </div>
      </div>
      ${renderMarkdownText(explanation.summary || "")}
      ${
        candidateExplanations.length
          ? `
            <div class="explanation-list">
              ${candidateExplanations
                .map(
                  (item, index) => `
                    <article class="explanation-card">
                      <strong>${htmlEscape(item.employee_id || `${textByLanguage("Кандидат", "Candidate")} #${index + 1}`)}</strong>
                      ${renderMarkdownText(item.explanation || item)}
                      ${
                        item.strengths
                          ? `<strong>Сильные стороны</strong>${renderMarkdownText(item.strengths)}`
                          : ""
                      }
                      ${
                        item.concerns
                          ? `<strong>Риски</strong>${renderMarkdownText(item.concerns)}`
                          : ""
                      }
                    </article>
                  `,
                )
                .join("")}
            </div>
          `
          : ""
      }
      ${explanation.risks_note ? `<h4>Риски</h4>${renderMarkdownText(explanation.risks_note)}` : ""}
    </section>
  `;
}

function renderSelectedTaskPanel() {
  const task = state.tasks.find((item) => item.task_id === state.selectedTaskId);
  if (!task) {
    return `
      <section class="panel">
        <h3>Детали задачи</h3>
        <p class="muted">Выберите карточку на канбан-доске, чтобы увидеть требования, кандидатов, график и объяснение.</p>
      </section>
    `;
  }

  const recommendation = state.recommendations[task.task_id];
  const explanation = state.explanations[task.task_id];

  return `
    <div class="kanban-detail-stack">
      <section class="panel">
        <div class="section-heading">
          <div>
            <h3>${htmlEscape(taskTitle(task))}</h3>
            <p class="muted">${htmlEscape(task.task_id)} · ${htmlEscape(statusLabel(task.status))}</p>
          </div>
          <div class="actions-row compact-actions">
            <button class="button-secondary" type="button" data-task-status-cycle="${htmlEscape(task.task_id)}">
              Следующий статус
            </button>
            <button class="button-danger" type="button" data-delete-task="${htmlEscape(task.task_id)}">
              Удалить задачу
            </button>
          </div>
        </div>
      </section>
      ${renderTaskRequirementPanel(task)}
      ${renderCandidates(recommendation)}
      ${renderExplanation(explanation)}
      ${renderTaskCandidateFitChart(task, recommendation?.candidates || [])}
    </div>
  `;
}

function renderLayout() {
  return `
    <div class="page-grid">
      ${renderSourcePanel()}
      ${renderStatsPanel()}
      ${renderManualTaskPanel()}
      ${renderTeamPanel()}
      <div class="kanban-lab-layout">
        <div>${renderBoard()}</div>
        <aside>${renderSelectedTaskPanel()}</aside>
      </div>
    </div>
  `;
}

function rerender() {
  const root = state.root || document.getElementById("appRoot");
  if (!root) {
    return;
  }
  root.innerHTML = renderLayout();
  bindEvents(root);
  window.__compassAiApplyLanguage?.(root);
}

function syncControls() {
  state.labName = selectedValue("labBoardName") || state.labName;
  state.selectedSavedLabId = selectedValue("savedLabBoardId") || state.selectedSavedLabId;
  state.selectedTestCaseId = selectedValue("labTestCaseId") || state.selectedTestCaseId;
  state.selectedDatasetValue = selectedValue("labDatasetValue") || state.selectedDatasetValue;
  state.selectedTrainingSessionId =
    selectedValue("labTrainingSessionId") || state.selectedTrainingSessionId;
  state.selectedModelName = selectedValue("labModelName") || state.selectedModelName;
  state.recommendationMode =
    selectedValue("labRecommendationMode") || state.recommendationMode;
  state.topK = numericValue("labTopK", state.topK);
  state.useLlm = checkboxValue("labUseLlm");
}

async function refreshSources() {
  const [datasets, testCases, trainingSessions, savedBoards] = await Promise.all([
    api.datasets(),
    api.testCases(),
    api.trainingSessions(),
    api.kanbanLabBoards(),
  ]);

  state.datasets = datasets;
  state.testCases = testCases.test_cases || [];
  state.trainingSessions = trainingSessions.sessions || [];
  state.savedBoards = savedBoards.boards || [];
  state.selectedDatasetValue ||= datasetOptions()[0]?.value || "";
  state.selectedTestCaseId ||= testCaseOptions()[0]?.value || "";
  state.selectedTrainingSessionId ||= trainingSessionOptions()[0]?.value || "";
  state.selectedSavedLabId ||= savedBoardOptions()[0]?.value || "";
}

async function loadTestCaseById(testCaseId) {
  if (!testCaseId) {
    toast("Выберите проверочный набор", "error");
    return;
  }

  const payload = await api.testCase(testCaseId);
  state.team = clone(payload.team || []);
  state.history = clone(payload.history || []);
  state.tasks = clone(payload.active_tasks || []);
  state.originalTeam = clone(state.team);
  state.originalHistory = clone(state.history);
  state.originalTasks = clone(state.tasks);
  state.recommendations = {};
  state.explanations = {};
  state.selectedTaskId = state.tasks[0]?.task_id || "";
  state.selectedTestCaseId = testCaseId;
  state.currentLabId = "";
  state.labName = `${testCaseId}_lab`;
  toast("Копия набора загружена", "success");
  rerender();
}

async function loadSelectedTestCase() {
  syncControls();
  await loadTestCaseById(state.selectedTestCaseId);
}

async function createLabCopyFromDataset() {
  syncControls();
  const { datasetKind, datasetId } = parseDatasetValue(state.selectedDatasetValue);

  if (!datasetId) {
    toast("Выберите датасет", "error");
    return;
  }

  const result = await api.createTestCaseFromDataset({
    dataset_id: datasetId,
    dataset_kind: datasetKind,
    test_case_id: `${datasetId}_kanban_lab`,
    task_statuses: RECOMMENDATION_STATUSES,
    overwrite: true,
  });

  state.selectedTestCaseId = result.test_case_id;
  await refreshSources();
  await loadTestCaseById(result.test_case_id);
}

async function loadSavedLabBoard() {
  syncControls();

  if (!state.selectedSavedLabId) {
    toast("Выберите сохраненную доску", "error");
    return;
  }

  const payload = await api.kanbanLabBoard(state.selectedSavedLabId);
  state.currentLabId = payload.lab_id || state.selectedSavedLabId;
  state.labName = payload.name || state.currentLabId;
  state.selectedTestCaseId = payload.source_test_case_id || state.selectedTestCaseId;
  state.selectedDatasetValue = payload.source_dataset_value || state.selectedDatasetValue;
  state.team = clone(payload.team || []);
  state.history = clone(payload.history || []);
  state.tasks = clone(payload.tasks || []);
  state.originalTeam = clone(state.team);
  state.originalHistory = clone(state.history);
  state.originalTasks = clone(state.tasks);
  state.recommendations = {};
  state.explanations = {};
  state.selectedTaskId = state.tasks[0]?.task_id || "";
  toast("Сохраненная доска загружена", "success");
  rerender();
}

async function saveLabBoard() {
  syncControls();

  if (!state.team.length && !state.tasks.length) {
    toast("Сначала загрузите копию набора", "error");
    return;
  }

  const result = await api.saveKanbanLabBoard({
    lab_id: state.currentLabId || null,
    name: state.labName || "Kanban lab board",
    source_test_case_id: state.selectedTestCaseId || null,
    source_dataset_value: state.selectedDatasetValue || null,
    team: state.team,
    history: state.history,
    tasks: state.tasks,
    config: {
      training_session_id: state.selectedTrainingSessionId,
      model_name: state.selectedModelName,
      recommendation_mode: state.recommendationMode,
      top_k: state.topK,
    },
    overwrite: true,
  });

  state.currentLabId = result.board?.lab_id || state.currentLabId;
  state.selectedSavedLabId = state.currentLabId;
  await refreshSources();
  toast("Лабораторная доска сохранена", "success");
  rerender();
}

async function deleteSavedLabBoard() {
  syncControls();

  if (!state.selectedSavedLabId) {
    toast("Выберите сохраненную доску", "error");
    return;
  }

  if (
    !window.confirm(
      textByLanguage(
        `Удалить сохраненную доску "${state.selectedSavedLabId}"?`,
        `Delete saved board "${state.selectedSavedLabId}"?`,
      ),
    )
  ) {
    return;
  }

  await api.deleteKanbanLabBoard(state.selectedSavedLabId);

  if (state.currentLabId === state.selectedSavedLabId) {
    state.currentLabId = "";
  }

  state.selectedSavedLabId = "";
  await refreshSources();
  toast("Сохраненная доска удалена", "success");
  rerender();
}

function resetBoard() {
  state.team = clone(state.originalTeam);
  state.history = clone(state.originalHistory);
  state.tasks = clone(state.originalTasks);
  state.recommendations = {};
  state.explanations = {};
  state.selectedTaskId = state.tasks[0]?.task_id || "";
  toast("Доска и персонал возвращены к исходной копии", "success");
  rerender();
}

function moveTask(taskId, status) {
  const task = state.tasks.find((item) => item.task_id === taskId);
  if (!task || !STATUSES.includes(status)) {
    return;
  }
  task.status = status;
  state.recommendations = {};
  state.explanations = {};
  rerender();
}

function moveColumn(fromStatus, toStatus) {
  if (!STATUSES.includes(fromStatus) || !STATUSES.includes(toStatus) || fromStatus === toStatus) {
    return;
  }

  state.tasks.forEach((task) => {
    if (String(task.status) === fromStatus) {
      task.status = toStatus;
    }
  });
  state.recommendations = {};
  state.explanations = {};
  toast(
    `${textByLanguage("Столбец перенесен", "Column moved")}: ${
      statusLabel(fromStatus)
    } -> ${statusLabel(toStatus)}`,
    "success",
  );
  rerender();
}

function clearColumn(status) {
  if (!STATUSES.includes(status)) {
    return;
  }

  if (
    !window.confirm(
      textByLanguage(
        `Удалить из копии все задачи в столбце "${statusLabel(status)}"?`,
        `Delete all copied tasks in "${statusLabel(status)}"?`,
      ),
    )
  ) {
    return;
  }

  state.tasks = state.tasks.filter((task) => String(task.status) !== status);
  state.recommendations = {};
  state.explanations = {};
  state.selectedTaskId = state.tasks[0]?.task_id || "";
  toast("Столбец очищен в лабораторной копии", "success");
  rerender();
}

function addManualTask() {
  const dictionaries = manualTaskDictionaries();
  const allowedProjects = new Set(dictionaries.projectIds);
  const allowedTaskTypes = new Set(dictionaries.taskTypes);
  const allowedSkills = new Set(dictionaries.skills);
  const title = selectedValue("manualTaskTitle").trim() ||
    textByLanguage("Лабораторная задача", "Lab Task");
  const taskType = selectedValue("manualTaskType");
  const projectId = selectedValue("manualTaskProject");
  const requiredSkills = selectedValues("manualTaskSkills");

  if (!state.tasks.length || !allowedProjects.size || !allowedTaskTypes.size || !allowedSkills.size) {
    toast("Сначала загрузите набор, чтобы появились существующие проекты, типы и навыки", "error");
    return;
  }

  if (!allowedTaskTypes.has(taskType) || !allowedProjects.has(projectId)) {
    toast("Выберите тип задачи и проект из текущего набора", "error");
    return;
  }

  if (!requiredSkills.length) {
    toast("Выберите хотя бы один существующий тег или навык для ручной задачи", "error");
    return;
  }

  if (requiredSkills.some((skill) => !allowedSkills.has(skill))) {
    toast("В ручной задаче можно использовать только существующие теги и навыки", "error");
    return;
  }

  const taskId = `lab_task_${Date.now()}`;
  const task = {
    task_id: taskId,
    title,
    status: "todo",
    priority: selectedValue("manualTaskPriority") || "medium",
    task_type: taskType,
    project_id: projectId,
    complexity: numericValue("manualTaskComplexity", 0.5),
    estimated_hours: numericValue("manualTaskHours", 8),
    required_skills: requiredSkills,
    custom_features: {
      source: "manual_kanban_lab",
    },
  };

  state.tasks.unshift(task);
  state.selectedTaskId = taskId;
  state.recommendations = {};
  state.explanations = {};
  toast("Ручная задача добавлена в To Do", "success");
  rerender();
}

function deleteTask(taskId) {
  state.tasks = state.tasks.filter((task) => task.task_id !== taskId);
  delete state.recommendations[taskId];
  delete state.explanations[taskId];
  state.selectedTaskId = state.tasks[0]?.task_id || "";
  toast("Задача удалена из копии", "success");
  rerender();
}

function nextEmployeeId() {
  const existing = new Set(state.team.map((employee) => String(employee.employee_id || "")));
  let index = state.team.length + 1;

  while (existing.has(`emp_lab_${String(index).padStart(4, "0")}`)) {
    index += 1;
  }

  return `emp_lab_${String(index).padStart(4, "0")}`;
}

function normalizeEmployeeId(value) {
  const normalized = String(value || "")
    .trim()
    .replace(/\s+/g, "_")
    .replace(/[^a-zA-Z0-9_-]/g, "");
  return normalized || nextEmployeeId();
}

function clearRecommendationsAfterTeamChange() {
  state.recommendations = {};
  state.explanations = {};
}

function historyEmployeeId(item) {
  return item?.employee_id || item?.assignee_id || item?.assigned_employee_id || item?.worker_id || "";
}

function addManualEmployee() {
  const dictionaries = manualTaskDictionaries();
  const allowedRoles = new Set(dictionaries.roles);
  const allowedGrades = new Set(dictionaries.grades);
  const allowedSkills = new Set(dictionaries.skills);
  const role = selectedValue("manualEmployeeRole");
  const grade = selectedValue("manualEmployeeGrade");
  const skills = selectedValues("manualEmployeeSkills");
  const employeeId = normalizeEmployeeId(selectedValue("manualEmployeeName"));

  if (!allowedRoles.size || !allowedGrades.size || !allowedSkills.size) {
    toast("Сначала загрузите набор, чтобы появились роли, грейды и навыки", "error");
    return;
  }

  if (!allowedRoles.has(role) || !allowedGrades.has(grade)) {
    toast("Выберите роль и грейд из текущего набора", "error");
    return;
  }

  if (!skills.length) {
    toast("Выберите хотя бы один навык для нового сотрудника", "error");
    return;
  }

  if (skills.some((skill) => !allowedSkills.has(skill))) {
    toast("Новому сотруднику можно назначать только существующие навыки", "error");
    return;
  }

  if (state.team.some((employee) => employee.employee_id === employeeId)) {
    toast("Сотрудник с таким ID уже есть в лабораторной копии", "error");
    return;
  }

  const employee = {
    employee_id: employeeId,
    name: employeeId,
    role,
    grade,
    skills,
    availability_score: clamp01(numericValue("manualEmployeeAvailability", 0.85)),
    current_workload: clamp01(numericValue("manualEmployeeWorkload", 0.25)),
    fatigue_score: clamp01(numericValue("manualEmployeeFatigue", 0.2)),
    avg_quality_score: clamp01(numericValue("manualEmployeeQuality", 0.8)),
    avg_completion_speed: clamp01(numericValue("manualEmployeeSpeed", 0.75)),
    deadline_reliability: clamp01(numericValue("manualEmployeeReliability", 0.8)),
    mentor_level: 0.5,
    learning_goals: [],
    timezone: "Europe/Moscow",
    team_id: state.team[0]?.team_id || "kanban_lab_team",
    custom_features: {
      source: "manual_kanban_lab",
    },
    active_task_ids: [],
  };

  state.team.unshift(employee);
  clearRecommendationsAfterTeamChange();
  toast("Сотрудник добавлен в лабораторную копию", "success");
  rerender();
}

function deleteEmployee(employeeId) {
  if (!employeeId) {
    toast("Выберите сотрудника для удаления", "error");
    return;
  }

  state.team = state.team.filter((employee) => employee.employee_id !== employeeId);
  state.history = state.history.filter((item) => historyEmployeeId(item) !== employeeId);
  clearRecommendationsAfterTeamChange();
  toast("Сотрудник удален из лабораторной копии", "success");
  rerender();
}

function clearTeam() {
  if (!state.team.length) {
    return;
  }

  if (
    !window.confirm(
      textByLanguage(
        "Удалить из лабораторной копии всех сотрудников?",
        "Delete all employees from the lab copy?",
      ),
    )
  ) {
    return;
  }

  state.team = [];
  state.history = [];
  clearRecommendationsAfterTeamChange();
  toast("Все сотрудники удалены из лабораторной копии", "success");
  rerender();
}

function cycleTaskStatus(taskId) {
  const task = state.tasks.find((item) => item.task_id === taskId);
  if (!task) {
    return;
  }

  const currentIndex = STATUSES.indexOf(String(task.status));
  task.status = STATUSES[(currentIndex + 1) % STATUSES.length];
  state.recommendations = {};
  state.explanations = {};
  rerender();
}

async function explainTask(taskId) {
  if (!state.useLlm || state.explanations[taskId] || !state.recommendations[taskId]) {
    return;
  }

  state.explanations[taskId] = await api.explainRecommendation({
    recommendation: state.recommendations[taskId],
    use_llm: true,
  });
}

async function selectTask(taskId) {
  state.selectedTaskId = taskId;
  await explainTask(taskId);
  rerender();
}

async function runRecommendations() {
  syncControls();

  if (!state.team.length || !state.tasks.length) {
    toast("Сначала загрузите копию набора", "error");
    return;
  }

  const progress = startLongTaskToast({
    title: "Канбан-рекомендации",
    message: "Передаем текущую копию доски модели...",
    steps: [
      "Проверяем доску...",
      "Считаем рекомендации...",
      "Обновляем карточки...",
      "Готово",
    ],
  });

  try {
    progress.update({ message: "Считаем рекомендации...", percent: 35, stepIndex: 1 });
    const result = await api.recommendKanbanBoard({
      session_id: state.selectedTrainingSessionId,
      model_name: state.selectedModelName,
      source_id: state.selectedTestCaseId || "kanban_lab",
      recommendation_mode: state.recommendationMode,
      top_k: state.topK,
      team: state.team,
      tasks: state.tasks,
      statuses_for_recommendation: RECOMMENDATION_STATUSES,
    });

    state.recommendations = Object.fromEntries(
      (result.recommendations || []).map((item) => [String(item.task_id), item]),
    );
    state.explanations = {};
    progress.done("Рекомендации готовы");
    toast(`${textByLanguage("Рассчитано задач", "Tasks calculated")}: ${result.total}`, "success");

    if (state.selectedTaskId) {
      await explainTask(state.selectedTaskId);
    }
    rerender();
  } catch (error) {
    progress.error(error.message || String(error));
    throw error;
  }
}

function bindEvents(root) {
  root.querySelector("#loadLabSource")?.addEventListener("click", loadSelectedTestCase);
  root.querySelector("#loadSavedLabBoard")?.addEventListener("click", loadSavedLabBoard);
  root.querySelector("#saveLabBoard")?.addEventListener("click", saveLabBoard);
  root.querySelector("#deleteSavedLabBoard")?.addEventListener("click", deleteSavedLabBoard);
  root.querySelector("#createLabCopyFromDataset")?.addEventListener("click", createLabCopyFromDataset);
  root.querySelector("#resetLabBoard")?.addEventListener("click", resetBoard);
  root.querySelector("#runKanbanRecommendations")?.addEventListener("click", runRecommendations);
  root.querySelector("#addManualTask")?.addEventListener("click", addManualTask);
  root.querySelector("#addManualEmployee")?.addEventListener("click", addManualEmployee);
  root.querySelector("#clearTeam")?.addEventListener("click", clearTeam);

  root.querySelectorAll("[data-delete-employee-card]").forEach((button) => {
    button.addEventListener("click", () => deleteEmployee(button.dataset.deleteEmployeeCard));
  });

  root.querySelectorAll("select, input").forEach((control) => {
    control.addEventListener("change", syncControls);
  });

  root.querySelectorAll("[data-move-column]").forEach((button) => {
    button.addEventListener("click", () => {
      const fromStatus = button.dataset.moveColumn;
      const target = root.querySelector(`[data-column-target="${fromStatus}"]`);
      moveColumn(fromStatus, target?.value || "");
    });
  });

  root.querySelectorAll("[data-clear-column]").forEach((button) => {
    button.addEventListener("click", () => clearColumn(button.dataset.clearColumn));
  });

  root.querySelectorAll("[data-delete-task]").forEach((button) => {
    button.addEventListener("click", () => deleteTask(button.dataset.deleteTask));
  });

  root.querySelectorAll("[data-task-status-cycle]").forEach((button) => {
    button.addEventListener("click", () => cycleTaskStatus(button.dataset.taskStatusCycle));
  });

  root.querySelectorAll(".kanban-lab-card").forEach((card) => {
    card.addEventListener("click", () => selectTask(card.dataset.taskId));
    card.addEventListener("keydown", (event) => {
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        selectTask(card.dataset.taskId);
      }
    });
    card.addEventListener("dragstart", (event) => {
      state.draggingTaskId = card.dataset.taskId;
      event.dataTransfer?.setData("text/plain", state.draggingTaskId);
      event.dataTransfer?.setDragImage(card, 12, 12);
    });
  });

  root.querySelectorAll(".kanban-lab-column").forEach((column) => {
    column.addEventListener("dragover", (event) => {
      event.preventDefault();
      column.classList.add("drag-over");
    });
    column.addEventListener("dragleave", () => {
      column.classList.remove("drag-over");
    });
    column.addEventListener("drop", (event) => {
      event.preventDefault();
      column.classList.remove("drag-over");
      const taskId = event.dataTransfer?.getData("text/plain") || state.draggingTaskId;
      moveTask(taskId, column.dataset.status);
    });
  });
}

export async function renderKanbanLab(root) {
  state.root = root;
  root.innerHTML = `
    <section class="panel">
      <h3>Канбан-лаборатория</h3>
      <p class="muted">Загружаем датасеты, наборы и модели...</p>
    </section>
  `;

  await refreshSources();
  root.innerHTML = renderLayout();
  bindEvents(root);
}

export async function renderPage(root) {
  return renderKanbanLab(root);
}

export default renderKanbanLab;
