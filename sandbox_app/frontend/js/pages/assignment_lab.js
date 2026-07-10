import { api } from "../api.js";
import { renderCandidateComparison } from "../components/candidate_comparison.js";
import { renderFairnessChart } from "../components/fairness_chart.js";
import { renderRecommendationCards } from "../components/recommendation_cards.js";
import { renderWorkloadChart } from "../components/workload_chart.js";

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
  testCases: [],
  testCaseSummaries: {},
  recommendationContexts: {},
  trainingSessions: [],
  assignmentSessions: [],
  selectedTestCaseId: "",
  selectedDatasetValue: "",
  selectedTrainingSessionId: "",
  selectedModelName: "logistic_regression",
  tasks: [],
  selectedTaskId: "",
  singleResult: null,
  bulkResult: null,
  selectedAssignmentSession: null,
  filters: {
    person: "",
    status: "",
    project: "",
    risk: "",
  },
  useLlmExplanations: false,
  llmStatus: null,
  singleExplanation: null,
  bulkExplanation: null,
};

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

function htmlEscape(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
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

    const heading = trimmed.match(/^(#{1,4})\s+(.+)$/);
    if (heading) {
      flushParagraph();
      flushList();
      output.push(`<h4>${renderInlineMarkdown(heading[2])}</h4>`);
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

    const ordered = trimmed.match(/^\d+\.\s+(.+)$/);
    if (ordered) {
      flushParagraph();
      if (listType && listType !== "ol") {
        flushList();
      }
      listType = "ol";
      listItems.push(ordered[1]);
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
        title: type === "error" ? "Ошибка назначений" : "Назначение задач",
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
    update() {},
    done(message = "Готово") {
      toast(message, "success");
    },
    error(message = "Ошибка") {
      toast(message, "error");
    },
  };
}

function numberInput(id, label, value, attrs = "") {
  return `
    <label>
      ${htmlEscape(label)}
      <input id="${id}" type="number" value="${htmlEscape(value)}" ${attrs}>
    </label>
  `;
}

function textInput(id, label, value = "") {
  return `
    <label>
      ${htmlEscape(label)}
      <input id="${id}" type="text" value="${htmlEscape(value)}">
    </label>
  `;
}

function selectInput(id, label, options, selected) {
  return `
    <label>
      ${htmlEscape(label)}
      <select id="${id}">
        ${options
          .map(
            (optionItem) => `
              <option
                value="${htmlEscape(optionItem.value)}"
                ${optionItem.value === selected ? "selected" : ""}
              >
                ${htmlEscape(optionItem.label)}
              </option>
            `,
          )
          .join("")}
      </select>
    </label>
  `;
}

function selectedValue(id) {
  const element = document.getElementById(id);
  return element ? element.value : "";
}

function numericValue(id, fallback) {
  const value = Number(selectedValue(id));
  return Number.isFinite(value) ? value : fallback;
}

function csvValues(id) {
  return selectedValue(id)
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean);
}

function firstValue(...values) {
  return values.find((value) => value !== undefined && value !== null && value !== "");
}

function numberText(value, digits = 2) {
  const numeric = Number(value);

  if (!Number.isFinite(numeric)) {
    return "—";
  }

  return numeric.toFixed(digits);
}

function percentText(value) {
  const numeric = Number(value);

  if (!Number.isFinite(numeric)) {
    return "—";
  }

  return `${Math.round(numeric * 100)}%`;
}

function clamp01(value) {
  const numeric = Number(value);

  if (!Number.isFinite(numeric)) {
    return 0;
  }

  return Math.max(0, Math.min(1, numeric));
}

function normalizedTaskComplexity(task) {
  const complexity = Number(task?.complexity);

  if (!Number.isFinite(complexity)) {
    return 0.5;
  }

  return clamp01(complexity > 1 ? complexity / 10 : complexity);
}

function normalizedPriority(task) {
  return {
    low: 0.25,
    medium: 0.5,
    high: 0.75,
    critical: 1,
  }[String(task?.priority || "").toLowerCase()] || 0.5;
}

function normalizedHours(task) {
  return clamp01(Number(task?.estimated_hours || 0) / 80);
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

function testCaseCounts(item, summary, context) {
  const metadataCounts = summary?.metadata?.counts || {};

  return {
    people: firstValue(
      summary?.people_count,
      summary?.team_size,
      metadataCounts.people,
      item?.people_count,
      item?.people,
    ) || 0,
    tasks: firstValue(
      summary?.active_tasks_count,
      metadataCounts.active_tasks,
      item?.active_tasks_count,
      item?.active_tasks,
    ) || 0,
    history: firstValue(
      summary?.history_count,
      summary?.history_rows,
      metadataCounts.history,
      item?.history_count,
      item?.history,
    ) || 0,
    recommendable: firstValue(
      context?.pending_tasks_count,
      context?.tasks_count,
      context?.pending_tasks?.length,
      context?.active_tasks_count,
    ) || 0,
  };
}

function modelOptions() {
  const selectedSession = state.trainingSessions.find(
    (item) => item.session_id === state.selectedTrainingSessionId,
  );
  const trainedModels = selectedSession?.trained_models || [];
  const names = trainedModels.length ? trainedModels : MODEL_NAMES;

  return names.map((name) => ({
    label: name,
    value: name,
  }));
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

function testCaseSummary(testCaseId) {
  return state.testCaseSummaries[testCaseId] || {};
}

function recommendationContext(testCaseId) {
  return state.recommendationContexts[testCaseId] || {};
}

function testCaseOptions() {
  return state.testCases.map((item) => {
    const summary = testCaseSummary(item.test_case_id);
    const context = recommendationContext(item.test_case_id);
    const counts = testCaseCounts(item, summary, context);

    return {
      label: `${item.test_case_id} · сотрудников: ${counts.people}`,
      value: item.test_case_id,
    };
  });
}

function trainingSessionOptions() {
  return state.trainingSessions.map((item) => ({
    label: `${item.session_id} · ${item.status || "статус неизвестен"}`,
    value: item.session_id,
  }));
}

function taskOptions() {
  return state.tasks.map((task) => ({
    label: `${task.task_id} · ${task.title || "без названия"}`,
    value: task.task_id,
  }));
}

function applyFilters(rows) {
  return rows.filter((row) => {
    const person = state.filters.person.toLowerCase();
    const status = state.filters.status.toLowerCase();
    const project = state.filters.project.toLowerCase();
    const risk = state.filters.risk.toLowerCase();

    const rowPerson = String(
      row.assigned_employee_name || row.name || row.employee_id || "",
    ).toLowerCase();
    const rowStatus = String(row.status || row.task_status || "").toLowerCase();
    const rowProject = String(row.project_id || "").toLowerCase();
    const rowRisk = JSON.stringify(row.risks || row.risk_summary || {})
      .toLowerCase();

    return (
      (!person || rowPerson.includes(person)) &&
      (!status || rowStatus.includes(status)) &&
      (!project || rowProject.includes(project)) &&
      (!risk || rowRisk.includes(risk))
    );
  });
}

function renderFilters() {
  return `
    <section class="panel">
      <div class="section-heading">
        <div>
          <h3>Фильтры результатов</h3>
          <p class="muted">Найдите нужного сотрудника, статус, проект или риск в результатах.</p>
        </div>
        <button id="clearAssignmentFilters" class="button-secondary" type="button">
          Очистить
        </button>
      </div>

      <div class="form-grid">
        ${textInput("filterPerson", "Сотрудник", state.filters.person)}
        ${textInput("filterStatus", "Статус задачи", state.filters.status)}
        ${textInput("filterProject", "Проект", state.filters.project)}
        ${textInput("filterRisk", "Риск", state.filters.risk)}
      </div>
    </section>
  `;
}

function renderTaskRequirementPanel(task) {
  if (!task) {
    return "";
  }

  const customFeatures = objectValue(task.custom_features);
  const customRows = Object.entries(customFeatures).slice(0, 8);

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
        <span class="pill">${htmlEscape(task.status || "статус неизвестен")}</span>
      </div>

      <div class="task-facts-grid">
        <div>
          <span>Проект</span>
          <strong>${htmlEscape(task.project_id || "—")}</strong>
        </div>
        <div>
          <span>Сложность</span>
          <strong>${numberText(task.complexity, 3)}</strong>
        </div>
        <div>
          <span>Оценка часов</span>
          <strong>${numberText(task.estimated_hours, 1)}</strong>
        </div>
        <div>
          <span>Дедлайн</span>
          <strong>${htmlEscape(task.due_at || task.deadline || "—")}</strong>
        </div>
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
  const technicalRisk = firstValue(
    customFeatures.technical_risk,
    customFeatures.risk,
    customFeatures.uncertainty_score,
    normalizedTaskComplexity(task),
  );

  return [
    1,
    normalizedPriority(task),
    clamp01(1 - normalizedHours(task)),
    clamp01(1 - Number(technicalRisk)),
    clamp01(1 - normalizedTaskComplexity(task) * 0.45),
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

  return [
    center + Math.cos(angle) * resolvedRadius,
    center + Math.sin(angle) * resolvedRadius,
  ];
}

function radarPolyline(values) {
  return values
    .map((value, index) => radarPoint(index, values.length, value).join(","))
    .join(" ");
}

function renderTaskCandidateFitChart(task, candidates) {
  const rows = Array.isArray(candidates) ? candidates.slice(0, 5) : [];

  if (!task || !rows.length) {
    return "";
  }

  const labels = ["Навыки", "Качество", "Скорость", "Низкий риск", "Доступность"];
  const colors = ["#007aff", "#34c759", "#ff9500", "#af52de", "#ff3b30"];
  const gridValues = [0.25, 0.5, 0.75, 1];
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
          <p class="muted">
            Пунктир — требования задачи, цветные линии — топ-кандидаты.
          </p>
        </div>
      </div>

      <div class="fit-chart-layout">
        <svg class="fit-radar" viewBox="0 0 220 220" role="img" aria-label="Сравнение требований задачи и кандидатов">
          ${gridValues
            .map(
              (value) => `
                <polygon
                  class="fit-radar-grid"
                  points="${radarPolyline(Array(labels.length).fill(value))}"
                />
              `,
            )
            .join("")}
          ${labels
            .map((label, index) => {
              const [x, y] = radarPoint(index, labels.length, 1.13);
              return `<text class="fit-radar-label" x="${x}" y="${y}">${htmlEscape(label)}</text>`;
            })
            .join("")}
          <polygon
            class="fit-radar-task"
            points="${radarPolyline(taskValues)}"
          />
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
                  <strong>#${index + 1} ${htmlEscape(
                    line.candidate.name || line.candidate.employee_id,
                  )}</strong>
                  <span>
                    score ${numberText(line.candidate.score, 3)}
                    · навыки ${percentText(line.values[0])}
                    · риск-fit ${percentText(line.values[3])}
                  </span>
                </div>
              `,
            )
            .join("")}
        </div>
      </div>
    </section>
  `;
}

function renderRecommendationFacts(recommendation) {
  const candidates = Array.isArray(recommendation?.candidates)
    ? recommendation.candidates
    : [];

  if (!candidates.length) {
    return "";
  }

  return `
    <section class="panel">
      <div class="section-heading">
        <div>
          <h3>Факты для объяснения</h3>
          <p class="muted">
            Эти цифры модель и LLM используют как основу: ranking не меняется, только поясняется.
          </p>
        </div>
      </div>

      <div class="explanation-list">
        ${candidates
          .map((candidate, index) => {
            const factors = candidate.factors || {};
            const snapshot = candidate.employee_snapshot || {};

            return `
              <article class="explanation-card">
                <strong>
                  #${index + 1} ${htmlEscape(candidate.name || candidate.employee_id)}
                </strong>
                <div class="fact-grid">
                  <div><span>Итог</span><strong>${numberText(candidate.score, 3)}</strong></div>
                  <div><span>Модель</span><strong>${numberText(candidate.model_score, 3)}</strong></div>
                  <div><span>Навыки</span><strong>${percentText(factors.skill_match_ratio)}</strong></div>
                  <div><span>Качество</span><strong>${percentText(factors.quality_fit_score)}</strong></div>
                  <div><span>Скорость</span><strong>${percentText(factors.speed_fit_score)}</strong></div>
                  <div><span>Нагрузка</span><strong>${percentText(factors.workload_pressure)}</strong></div>
                  <div><span>Усталость</span><strong>${percentText(snapshot.fatigue_score)}</strong></div>
                  <div><span>Доступность</span><strong>${percentText(snapshot.availability_score)}</strong></div>
                </div>
                <div class="skill-block">
                  <strong>Совпало с задачей</strong>
                  <div>${tagList(candidate.matched_skills, "нет совпадений")}</div>
                </div>
                <div class="skill-block">
                  <strong>Не хватает относительно задачи</strong>
                  <div>${tagList(candidate.missing_skills, "нет пробелов")}</div>
                </div>
              </article>
            `;
          })
          .join("")}
      </div>
    </section>
  `;
}

function renderGeneratorPanel() {
  return `
    <section class="panel">
      <div class="section-heading">
        <div>
          <h2>Проверочный набор вручную</h2>
          <p class="muted">
            Создайте небольшую команду и задачи для быстрой проверки моделей.
          </p>
        </div>
        <button id="refreshAssignmentData" class="button-secondary" type="button">
          Обновить
        </button>
      </div>

      <div class="form-grid">
        ${textInput("testCaseId", "ID проверочного набора", "ui_test_case")}
        ${selectInput(
          "domainProfile",
          "Профиль",
          [
            { label: "Разработчики", value: "developers" },
            { label: "Дизайнеры", value: "designers" },
            { label: "Своя схема", value: "custom" },
          ],
          "developers",
        )}
        ${numberInput("peopleCount", "Сотрудников", 8, "min='1' max='500'")}
        ${numberInput("activeTasksCount", "Активных задач", 12, "min='1' max='5000'")}
        ${numberInput("historyDepth", "Глубина истории", 4, "min='0' max='200'")}
        ${numberInput("seed", "Seed", 27024, "min='1'")}
        ${textInput("roles", "Роли", "Backend Engineer,Frontend Engineer,QA Engineer")}
        ${textInput("grades", "Уровни", "junior,middle,senior,lead")}
        ${textInput("skills", "Теги / навыки", "python,fastapi,react,sql,testing,ml")}
      </div>

      <div class="actions-row">
        <button id="generateTestCase" type="button">Создать проверочный набор</button>
      </div>
    </section>
  `;
}

function renderDatasetPipelinePanel() {
  return `
    <section class="panel pipeline-panel">
      <div class="section-heading">
        <div>
          <h2>Проверка на вашем датасете</h2>
          <p class="muted">
            Превратите созданный или импортированный датасет в набор задач для рекомендаций.
          </p>
        </div>
        <span class="pill">датасет -> набор -> модель -> назначение</span>
      </div>

      <div class="form-grid">
        ${selectInput(
          "pipelineDataset",
          "Датасет",
          datasetOptions(),
          state.selectedDatasetValue,
        )}
        ${textInput(
          "pipelineTestCaseId",
          "ID проверочного набора",
          state.selectedDatasetValue
            ? `${parseDatasetValue(state.selectedDatasetValue).datasetId}_case`
            : "dataset_case",
        )}
        ${selectInput(
          "pipelineTaskStatuses",
          "Статусы задач",
          [
            { label: "Готовые к работе: todo/in_progress/review/blocked", value: "todo,in_progress,review,blocked" },
            { label: "Только todo", value: "todo" },
            { label: "Все, кроме done/failed", value: "todo,in_progress,review,blocked" },
          ],
          "todo,in_progress,review,blocked",
        )}
      </div>

      <div class="actions-row">
        <button id="createCaseFromDataset" type="button">
          Создать набор из датасета
        </button>
      </div>
    </section>
  `;
}

function renderSelectionPanel() {
  return `
    <section class="panel">
      <div class="section-heading">
        <div>
          <h2>Рекомендации и распределение</h2>
          <p class="muted">
            Выберите обученную модель, набор задач и режим расчета.
          </p>
        </div>
      </div>

      <div class="form-grid">
        ${selectInput(
          "trainingSessionId",
          "Сессия обучения",
          trainingSessionOptions(),
          state.selectedTrainingSessionId,
        )}
        ${selectInput("modelName", "Модель", modelOptions(), state.selectedModelName)}
        ${selectInput(
          "testCaseSelect",
          "Проверочный набор",
          testCaseOptions(),
          state.selectedTestCaseId,
        )}
        ${selectInput("taskSelect", "Задача", taskOptions(), state.selectedTaskId)}
        ${selectInput(
          "recommendationMode",
          "Режим рекомендации",
          [
            { label: "Баланс качества и нагрузки", value: "balanced" },
            { label: "Лучшее качество", value: "best_quality" },
            { label: "Быстрее всего", value: "fastest_delivery" },
            { label: "Лучшее обучение сотрудника", value: "best_learning" },
            { label: "Осторожнее к рискам", value: "risk_aware" },
          ],
          "balanced",
        )}
        ${selectInput(
          "assignmentMode",
          "Режим распределения",
          [
            { label: "Баланс качества и нагрузки", value: "balanced" },
            { label: "Лучшее качество", value: "best_quality" },
            { label: "Быстрее всего", value: "fastest_delivery" },
            { label: "Лучшее обучение сотрудника", value: "best_learning" },
            { label: "Осторожнее к рискам", value: "risk_aware" },
          ],
          "balanced",
        )}
        ${selectInput(
          "assignmentTaskStatuses",
          "Какие задачи распределять",
          [
            { label: "Все рабочие: todo/in_progress/review/blocked", value: "todo,in_progress,review,blocked" },
            { label: "Только todo", value: "todo" },
            { label: "Todo и заблокированные", value: "todo,blocked" },
          ],
          "todo,in_progress,review,blocked",
        )}
        ${numberInput("topK", "Сколько кандидатов показать", 3, "min='1' max='100'")}
        ${numberInput(
          "maxWorkload",
          "Мягкий лимит нагрузки на сотрудника",
          1.2,
          "min='0.1' max='1.5' step='0.05'",
        )}
        ${numberInput(
          "fairnessPenalty",
          "Штраф за дисбаланс",
          0.12,
          "min='0' max='2' step='0.01'",
        )}
        ${numberInput(
          "fatiguePenalty",
          "Штраф за усталость",
          0.12,
          "min='0' max='2' step='0.01'",
        )}
        ${numberInput(
          "learningBonus",
          "Бонус за развитие",
          0.08,
          "min='0' max='2' step='0.01'",
        )}
        ${numberInput(
          "workloadPenalty",
          "Штраф за нагрузку",
          0.18,
          "min='0' max='2' step='0.01'",
        )}
        <label class="checkbox-label">
          <input
            id="useLlmExplanations"
            type="checkbox"
            ${state.useLlmExplanations ? "checked" : ""}
          >
          <span>Добавить объяснения через Qwen/Ollama</span>
        </label>
      </div>

      <div class="actions-row">
        <button id="loadRecommendableTasks" class="button-secondary" type="button">
          Загрузить задачи
        </button>
        <button id="runSingleRecommendation" type="button">
          Рекомендовать по одной задаче
        </button>
        <button id="runBulkAssignment" type="button">Распределить все задачи</button>
        <button id="deleteSelectedTestCase" class="button-danger" type="button">
          Удалить набор
        </button>
      </div>
    </section>
  `;
}

function renderTestCasesPanel() {
  if (!state.testCases.length) {
    return `
      <section class="panel">
        <h3>Проверочные наборы</h3>
        <p class="muted">Проверочные наборы пока не созданы. Создайте их из датасета или вручную.</p>
      </section>
    `;
  }

  return `
    <section class="panel">
      <h3>Проверочные наборы</h3>
      <div class="list-grid">
        ${state.testCases
          .map((item) => {
            const summary = testCaseSummary(item.test_case_id);
            const context = recommendationContext(item.test_case_id);
            const counts = testCaseCounts(item, summary, context);

            return `
              <button
                class="list-card ${
                  item.test_case_id === state.selectedTestCaseId ? "active" : ""
                }"
                data-test-case-id="${htmlEscape(item.test_case_id)}"
                type="button"
              >
                <strong>${htmlEscape(item.test_case_id)}</strong>
                <span>
                  сотрудники: ${htmlEscape(counts.people)}
                  · задачи: ${htmlEscape(counts.tasks)}
                  · история: ${htmlEscape(counts.history)}
                  · к рекомендации: ${htmlEscape(counts.recommendable)}
                </span>
              </button>
            `;
          })
          .join("")}
      </div>
    </section>
  `;
}

function renderExplanationPanel(title, explanation) {
  if (!explanation) {
    return "";
  }

  const candidateExplanations = Array.isArray(explanation.candidate_explanations)
    ? explanation.candidate_explanations
    : [];
  const noteCards = [
    ["Справедливость", explanation.fairness_note],
    ["Нагрузка", explanation.workload_note],
    ["Без назначения", explanation.unassigned_note],
    ["Риски", explanation.risks_note],
  ].filter(([_label, value]) => String(value || "").trim());

  return `
    <section class="panel">
      <div class="section-heading">
        <div>
          <h3>${htmlEscape(title)}</h3>
          <p class="muted">
            ${explanation.llm_used ? "Qwen/Ollama" : "Локальное объяснение"}
            · источник ранжирования: ${htmlEscape(
              explanation.ranking_source || "model_output_unchanged",
            )}
          </p>
        </div>
        <span class="pill">${htmlEscape(explanation.status || "ok")}</span>
      </div>

      ${renderMarkdownText(explanation.summary || "")}

      ${
        candidateExplanations.length
          ? `
            <div class="explanation-list">
              ${candidateExplanations
                .map(
                  (item, index) => {
                    const isObject = item && typeof item === "object";
                    const employeeLabel = isObject
                      ? item.employee_id || `Кандидат #${index + 1}`
                      : `Кандидат #${index + 1}`;
                    const explanationText = isObject ? item.explanation : item;
                    const strengths = isObject ? item.strengths : "";
                    const concerns = isObject ? item.concerns : "";

                    return `
                      <article class="explanation-card">
                        <strong>${htmlEscape(employeeLabel)}</strong>
                        ${renderMarkdownText(explanationText || "")}
                        ${
                          strengths
                            ? `
                              <div class="muted">
                                <strong>Сильные стороны:</strong>
                                ${renderMarkdownText(
                                  Array.isArray(strengths)
                                    ? strengths.join(", ")
                                    : strengths,
                                )}
                              </div>
                            `
                            : ""
                        }
                        ${
                          concerns
                            ? `
                              <div class="muted">
                                <strong>Риски:</strong>
                                ${renderMarkdownText(
                                  Array.isArray(concerns)
                                    ? concerns.join(", ")
                                    : concerns,
                                )}
                              </div>
                            `
                            : ""
                        }
                      </article>
                    `;
                  },
                )
                .join("")}
            </div>
          `
          : ""
      }

      ${
        noteCards.length
          ? `
            <div class="explanation-list">
              ${noteCards
                .map(
                  ([label, value]) => `
                    <article class="explanation-card">
                      <strong>${htmlEscape(label)}</strong>
                      ${renderMarkdownText(value)}
                    </article>
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

function renderSingleResult() {
  if (!state.singleResult) {
    return `
      <section class="panel">
        <h3>Рекомендация по одной задаче</h3>
        <p class="muted">Выберите задачу и запустите рекомендацию, чтобы увидеть лучших кандидатов.</p>
      </section>
    `;
  }

  const filteredCandidates = applyFilters(state.singleResult.candidates || []);
  const result = {
    ...state.singleResult,
    candidates: filteredCandidates,
  };
  const task = state.singleResult.task ||
    state.tasks.find((item) => item.task_id === state.selectedTaskId);

  return `
    ${renderTaskRequirementPanel(task)}
    ${renderRecommendationCards(result, { title: "Лучшие кандидаты" })}
    ${renderCandidateComparison(filteredCandidates, { title: "Сравнение кандидатов" })}
    ${renderRecommendationFacts(result)}
    ${renderExplanationPanel("Объяснение рекомендации", state.singleExplanation)}
    ${renderTaskCandidateFitChart(task, filteredCandidates)}
  `;
}

function renderBulkKanban(assignedRows, unassignedRows) {
  const assigned = assignedRows || [];
  const unassigned = unassignedRows || [];

  return `
    <section class="panel">
      <div class="section-heading">
        <div>
          <h3>Доска после распределения</h3>
          <p class="muted">Назначенные и неназначенные задачи после симуляции.</p>
        </div>
      </div>

      <div class="kanban-board">
        <div class="kanban-column">
          <h4>Назначено · ${assigned.length}</h4>
          ${assigned
            .map(
              (row) => `
                <article class="kanban-card">
                  <strong>${htmlEscape(row.task_title || row.task_id)}</strong>
                  <p>
                    ${htmlEscape(row.assigned_employee_name || "—")}
                    · score ${numberText(row.assignment_score, 3)}
                  </p>
                  <span>
                    Задача #${htmlEscape(row.employee_task_number || "—")} в плане сотрудника
                    · ${row.over_soft_limit ? "выше мягкого лимита" : "в мягком лимите"}
                  </span>
                  <span>
                    ${htmlEscape(row.priority || "—")}
                    · ${htmlEscape(row.task_type || "тип не указан")}
                    · ${numberText(row.estimated_hours, 1)} ч
                  </span>
                  <div class="kanban-tags">${tagList(row.required_skills, "теги не указаны")}</div>
                </article>
              `,
            )
            .join("")}
        </div>

        <div class="kanban-column">
          <h4>Без назначения · ${unassigned.length}</h4>
          ${unassigned
            .map(
              (row) => `
                <article class="kanban-card warning">
                  <strong>${htmlEscape(row.task_title || row.task_id)}</strong>
                  <p>${htmlEscape(row.reason || "—")}</p>
                  <span>
                    ${htmlEscape(row.priority || "—")}
                    · ${htmlEscape(row.task_type || "тип не указан")}
                  </span>
                  <div class="kanban-tags">${tagList(row.required_skills, "теги не указаны")}</div>
                </article>
              `,
            )
            .join("")}
        </div>
      </div>
    </section>
  `;
}

function renderExportLinks(result) {
  const sessionId = result?.assignment_session_id;

  if (!sessionId) {
    return "";
  }

  const files = [
    "assignment_report.html",
    "recommendations.json",
    "assigned_tasks.csv",
    "unassigned_tasks.csv",
    "workload_after_assignment.csv",
    "fairness_report.json",
  ];

  return `
    <section class="panel">
      <h3>Файлы результата</h3>
      <div class="export-links">
        ${files
          .map(
            (fileName) => `
              <a
                class="button-secondary"
                href="/api/assignment-sessions/${encodeURIComponent(
                  sessionId,
                )}/files/${encodeURIComponent(fileName)}"
                target="_blank"
                rel="noreferrer"
              >
                ${htmlEscape(fileName)}
              </a>
            `,
          )
          .join("")}
      </div>
    </section>
  `;
}

function renderBulkResult() {
  if (!state.bulkResult) {
    return `
      <section class="panel">
        <h3>Распределение всех задач</h3>
        <p class="muted">Запустите распределение, чтобы модель подобрала исполнителей для доступных задач.</p>
      </section>
    `;
  }

  const assigned = applyFilters(state.bulkResult.assigned_tasks || []);
  const unassigned = applyFilters(state.bulkResult.unassigned_tasks || []);
  const workloadRows = state.bulkResult.workload_after_assignment || [];

  return `
    ${renderBulkKanban(assigned, unassigned)}
    ${renderWorkloadChart(workloadRows)}
    ${renderFairnessChart(state.bulkResult.fairness_report, workloadRows)}
    ${renderExplanationPanel("Объяснение распределения", state.bulkExplanation)}
    ${renderExportLinks(state.bulkResult)}
  `;
}

function renderAssignmentSessionsPanel() {
  if (!state.assignmentSessions.length) {
    return `
      <section class="panel">
        <h3>Сессии назначения</h3>
        <p class="muted">Сохраненных сессий назначения пока нет.</p>
      </section>
    `;
  }

  return `
      <section class="panel">
        <div class="section-heading">
          <div>
            <h3>Сессии назначения</h3>
            <p class="muted">Сохраненные результаты распределения задач.</p>
          </div>
          <button id="deleteSelectedAssignmentSession" class="button-danger" type="button">
            Удалить выбранную
          </button>
        </div>
      <div class="list-grid">
        ${state.assignmentSessions
          .map(
            (item) => `
              <button
                class="list-card ${
                  item.assignment_session_id ===
                  state.selectedAssignmentSession?.assignment_session_id
                    ? "active"
                    : ""
                }"
                data-assignment-session-id="${htmlEscape(
                  item.assignment_session_id,
                )}"
                type="button"
              >
                <strong>${htmlEscape(item.assignment_session_id)}</strong>
                <span>
                  назначено: ${htmlEscape(item.assigned_tasks ?? 0)}
                  · без назначения: ${htmlEscape(item.unassigned_tasks ?? 0)}
                </span>
              </button>
            `,
          )
          .join("")}
      </div>
    </section>
  `;
}

function render() {
  return `
    <div class="page-stack">
      <section class="hero-panel">
        <div>
          <p class="eyebrow">Назначение задач</p>
          <h1>Проверка моделей на задачах</h1>
          <p>
            Выберите обученную модель, проверьте рекомендацию по одной задаче
            или распределите сразу весь набор с учетом нагрузки и рисков.
          </p>
        </div>
      </section>

      ${renderDatasetPipelinePanel()}
      ${renderGeneratorPanel()}
      ${renderSelectionPanel()}
      ${renderFilters()}
      ${renderTestCasesPanel()}
      ${renderSingleResult()}
      ${renderBulkResult()}
      ${renderAssignmentSessionsPanel()}
    </div>
  `;
}

async function loadTestCaseSummaries() {
  const summaryResults = await Promise.allSettled(
    state.testCases.slice(0, 30).map(async (item) => {
      const summary = await api.testCaseSummary(item.test_case_id);
      return [item.test_case_id, summary];
    }),
  );

  state.testCaseSummaries = Object.fromEntries(
    summaryResults
      .filter((result) => result.status === "fulfilled")
      .map((result) => result.value),
  );
}

async function loadRecommendationContexts() {
  const contextResults = await Promise.allSettled(
    state.testCases.slice(0, 30).map(async (item) => {
      const context = await api.testCaseRecommendationContext(item.test_case_id);
      return [item.test_case_id, context];
    }),
  );

  state.recommendationContexts = Object.fromEntries(
    contextResults
      .filter((result) => result.status === "fulfilled")
      .map((result) => result.value),
  );
}

async function refreshAll() {
  const [datasets, testCases, trainingSessions, assignmentSessions] = await Promise.all([
    api.datasets(),
    api.testCases(),
    api.trainingSessions(),
    api.assignmentSessions(),
  ]);

  state.datasets = datasets;
  state.testCases = testCases.test_cases || testCases.items || [];
  state.trainingSessions = trainingSessions.sessions || trainingSessions.training_sessions || [];
  state.assignmentSessions = assignmentSessions.assignment_sessions || [];

  if (!state.selectedDatasetValue) {
    const firstDataset = allDatasets(state.datasets)[0];
    state.selectedDatasetValue = firstDataset ? datasetOptionValue(firstDataset) : "";
  }

  if (!state.selectedTestCaseId && state.testCases.length) {
    state.selectedTestCaseId = state.testCases[0].test_case_id;
  }

  if (!state.selectedTrainingSessionId && state.trainingSessions.length) {
    state.selectedTrainingSessionId = state.trainingSessions[0].session_id;
  }

  const selectedSession = state.trainingSessions.find(
    (item) => item.session_id === state.selectedTrainingSessionId,
  );
  const trainedModels = selectedSession?.trained_models || [];
  if (trainedModels.length && !trainedModels.includes(state.selectedModelName)) {
    state.selectedModelName = trainedModels[0];
  }

  await Promise.all([
    loadTestCaseSummaries(),
    loadRecommendationContexts(),
  ]);
}

async function loadTasks() {
  if (!state.selectedTestCaseId) {
    toast("Сначала выберите проверочный набор", "error");
    return;
  }

  const response = await api.recommendableTasks(state.selectedTestCaseId);
  state.tasks = response.tasks || [];

  if (!state.selectedTaskId && state.tasks.length) {
    state.selectedTaskId = state.tasks[0].task_id;
  }
}

async function generateTestCase() {
  const payload = {
    test_case_id: selectedValue("testCaseId"),
    domain_profile: selectedValue("domainProfile"),
    people_count: numericValue("peopleCount", 8),
    active_tasks_count: numericValue("activeTasksCount", 12),
    history_depth: numericValue("historyDepth", 4),
    seed: numericValue("seed", 27024),
    overwrite: true,
    roles: csvValues("roles"),
    grades: csvValues("grades"),
    skills: csvValues("skills"),
  };

  const result = await api.generateTestCase(payload);
  state.selectedTestCaseId = result.test_case_id || payload.test_case_id;
  await refreshAll();
  await loadTasks();
  toast("Проверочный набор создан", "success");
}

async function createCaseFromDataset() {
  const progress = startLongTaskToast({
    title: "Создаем набор из датасета...",
    message: "Проверяем выбранный датасет...",
    steps: [
      "Проверяем выбранный датасет...",
      "Читаем сотрудников и задачи...",
      "Готовим историю...",
      "Сохраняем проверочный набор...",
      "Обновляем интерфейс...",
    ],
  });

  state.selectedDatasetValue = selectedValue("pipelineDataset");
  const parsed = parseDatasetValue(state.selectedDatasetValue);

  if (!parsed.datasetId) {
    progress.error("Сначала выберите датасет");
    toast("Сначала выберите датасет", "error");
    return false;
  }

  const payload = {
    dataset_id: parsed.datasetId,
    dataset_kind: parsed.datasetKind,
    test_case_id: selectedValue("pipelineTestCaseId") || `${parsed.datasetId}_case`,
    task_statuses: selectedValue("pipelineTaskStatuses")
      .split(",")
      .map((item) => item.trim())
      .filter(Boolean),
    overwrite: true,
  };

  try {
    progress.update({ message: "Читаем сотрудников и задачи...", percent: 30, stepIndex: 1 });
    const result = await api.createTestCaseFromDataset(payload);
    state.selectedTestCaseId = result.test_case_id || payload.test_case_id;
    state.selectedTaskId = "";
    progress.update({ message: "Обновляем интерфейс...", percent: 82, stepIndex: 4 });
    await refreshAll();
    await loadTasks();
    progress.done("Проверочный набор создан");
    toast("Проверочный набор создан из датасета", "success");
    return true;
  } catch (error) {
    const message = error.message || String(error);
    progress.error(message);
    toast(message, "error");
    return false;
  }
}

async function deleteSelectedTestCase() {
  state.selectedTestCaseId = selectedValue("testCaseSelect") || state.selectedTestCaseId;

  if (!state.selectedTestCaseId) {
    toast("Проверочный набор не выбран", "error");
    return;
  }

  if (!window.confirm(`Удалить проверочный набор "${state.selectedTestCaseId}"?`)) {
    return;
  }

  await api.deleteTestCase(state.selectedTestCaseId);
  state.selectedTestCaseId = "";
  state.selectedTaskId = "";
  state.tasks = [];
  await refreshAll();
  toast("Проверочный набор удален", "success");
}

async function deleteSelectedAssignmentSession() {
  const sessionId = state.selectedAssignmentSession?.assignment_session_id ||
    state.bulkResult?.assignment_session_id;

  if (!sessionId) {
    toast("Сессия назначения не выбрана", "error");
    return;
  }

  if (!window.confirm(`Удалить сессию назначения "${sessionId}"?`)) {
    return;
  }

  await api.deleteAssignmentSession(sessionId);
  state.selectedAssignmentSession = null;
  state.bulkResult = null;
  state.bulkExplanation = null;
  await refreshAll();
  toast("Сессия назначения удалена", "success");
}

function syncSelectionControls() {
  state.selectedTrainingSessionId =
    selectedValue("trainingSessionId") || state.selectedTrainingSessionId;
  state.selectedModelName = selectedValue("modelName") || state.selectedModelName;
  state.selectedTestCaseId = selectedValue("testCaseSelect") || state.selectedTestCaseId;
  state.selectedTaskId = selectedValue("taskSelect") || state.selectedTaskId;
  state.selectedDatasetValue = selectedValue("pipelineDataset") || state.selectedDatasetValue;
}

function syncLlmCheckbox() {
  const checkbox = document.getElementById("useLlmExplanations");
  state.useLlmExplanations = Boolean(checkbox?.checked);
}

async function maybeExplainSingleRecommendation() {
  state.singleExplanation = null;

  if (!state.singleResult) {
    return;
  }

  const payload = {
    recommendation: state.singleResult,
    use_llm: state.useLlmExplanations,
  };

  state.singleExplanation = await api.explainRecommendation(payload);
}

async function maybeExplainBulkAssignment() {
  state.bulkExplanation = null;

  if (!state.bulkResult) {
    return;
  }

  const payload = {
    assignment_session: state.bulkResult,
    use_llm: state.useLlmExplanations,
  };

  state.bulkExplanation = await api.explainAssignment(payload);
}

async function runSingleRecommendation() {
  state.selectedTrainingSessionId = selectedValue("trainingSessionId");
  state.selectedModelName = selectedValue("modelName");
  state.selectedTestCaseId = selectedValue("testCaseSelect");
  state.selectedTaskId = selectedValue("taskSelect");

  const payload = {
    session_id: state.selectedTrainingSessionId,
    model_name: state.selectedModelName,
    test_case_id: state.selectedTestCaseId,
    task_id: state.selectedTaskId,
    recommendation_mode: selectedValue("recommendationMode"),
    top_k: numericValue("topK", 3),
    save_result: true,
  };

  state.singleResult = await api.singleRecommendation(payload);
  syncLlmCheckbox();
  await maybeExplainSingleRecommendation();
  toast("Рекомендация готова", "success");
}

async function runBulkAssignment() {
  state.selectedTrainingSessionId = selectedValue("trainingSessionId");
  state.selectedModelName = selectedValue("modelName");
  state.selectedTestCaseId = selectedValue("testCaseSelect");
  const progress = startLongTaskToast({
    title: "Распределяем задачи...",
    message: "Проверяем данные...",
    steps: [
      "Проверяем данные...",
      "Распределяем задачи...",
      "Считаем метрики...",
      "Готовим объяснения...",
      "Сохраняем артефакты...",
    ],
  });

  const payload = {
    session_id: state.selectedTrainingSessionId,
    model_name: state.selectedModelName,
    test_case_id: state.selectedTestCaseId,
    assignment_mode: selectedValue("assignmentMode"),
    recommendation_mode: selectedValue("recommendationMode"),
    top_k: numericValue("topK", 3),
    max_workload_per_person: numericValue("maxWorkload", 1.2),
    fairness_penalty: numericValue("fairnessPenalty", 0.12),
    fatigue_penalty: numericValue("fatiguePenalty", 0.12),
    learning_bonus: numericValue("learningBonus", 0.08),
    workload_penalty: numericValue("workloadPenalty", 0.18),
    task_statuses: selectedValue("assignmentTaskStatuses")
      .split(",")
      .map((item) => item.trim())
      .filter(Boolean),
    save_session: true,
  };

  try {
    progress.update({ message: "Распределяем задачи...", percent: 34, stepIndex: 1 });
    state.bulkResult = await api.runBulkAssignment(payload);
    state.selectedAssignmentSession = state.bulkResult;
    syncLlmCheckbox();
    progress.update({ message: "Готовим объяснения...", percent: 78, stepIndex: 3 });
    await maybeExplainBulkAssignment();
    progress.update({ message: "Сохраняем артефакты...", percent: 96, stepIndex: 4 });
    progress.done("Готово");
    await refreshAll();
    toast("Распределение готово", "success");
  } catch (error) {
    progress.error(error.message || String(error));
    throw error;
  }
}

function syncFilters() {
  state.filters.person = selectedValue("filterPerson");
  state.filters.status = selectedValue("filterStatus");
  state.filters.project = selectedValue("filterProject");
  state.filters.risk = selectedValue("filterRisk");
}

function bindEvents(root) {
  root.querySelector("#refreshAssignmentData")?.addEventListener("click", async () => {
    await refreshAll();

    if (state.selectedTestCaseId) {
      await loadTasks();
    }

    root.innerHTML = render();
    bindEvents(root);
  });

  root.querySelector("#generateTestCase")?.addEventListener("click", async () => {
    await generateTestCase();
    root.innerHTML = render();
    bindEvents(root);
  });

  root.querySelector("#createCaseFromDataset")?.addEventListener("click", async () => {
    const created = await createCaseFromDataset();
    if (created) {
      root.innerHTML = render();
      bindEvents(root);
    }
  });

  root.querySelector("#loadRecommendableTasks")?.addEventListener("click", async () => {
    state.selectedTestCaseId = selectedValue("testCaseSelect");
    await loadTasks();
    root.innerHTML = render();
    bindEvents(root);
  });

  root.querySelector("#runSingleRecommendation")?.addEventListener("click", async () => {
    await runSingleRecommendation();
    root.innerHTML = render();
    bindEvents(root);
  });

  root.querySelector("#runBulkAssignment")?.addEventListener("click", async () => {
    await runBulkAssignment();
    root.innerHTML = render();
    bindEvents(root);
  });

  root.querySelector("#deleteSelectedTestCase")?.addEventListener("click", async () => {
    await deleteSelectedTestCase();
    root.innerHTML = render();
    bindEvents(root);
  });

  root.querySelector("#deleteSelectedAssignmentSession")?.addEventListener(
    "click",
    async () => {
      await deleteSelectedAssignmentSession();
      root.innerHTML = render();
      bindEvents(root);
    },
  );

  root.querySelectorAll(
    "#pipelineDataset, #trainingSessionId, #modelName, #testCaseSelect, #taskSelect",
  ).forEach((input) => {
    input.addEventListener("change", async () => {
      syncSelectionControls();
      if (input.id === "trainingSessionId") {
        const selectedSession = state.trainingSessions.find(
          (item) => item.session_id === state.selectedTrainingSessionId,
        );
        state.selectedModelName = selectedSession?.trained_models?.[0] || state.selectedModelName;
      }
      if (input.id === "testCaseSelect") {
        state.selectedTaskId = "";
        await loadTasks();
      }
      root.innerHTML = render();
      bindEvents(root);
    });
  });

  root.querySelector("#clearAssignmentFilters")?.addEventListener("click", () => {
    state.filters = {
      person: "",
      status: "",
      project: "",
      risk: "",
    };
    root.innerHTML = render();
    bindEvents(root);
  });

  root.querySelectorAll("#filterPerson, #filterStatus, #filterProject, #filterRisk")
    .forEach((input) => {
      input.addEventListener("input", () => {
        syncFilters();
        root.innerHTML = render();
        bindEvents(root);
      });
    });

  root.querySelectorAll("[data-test-case-id]").forEach((button) => {
    button.addEventListener("click", async () => {
      state.selectedTestCaseId = button.dataset.testCaseId || "";
      state.selectedTaskId = "";
      await loadTasks();
      root.innerHTML = render();
      bindEvents(root);
    });
  });

  root.querySelectorAll("[data-assignment-session-id]").forEach((button) => {
    button.addEventListener("click", async () => {
      const sessionId = button.dataset.assignmentSessionId || "";
      state.bulkResult = await api.assignmentSession(sessionId);
      state.selectedAssignmentSession = state.bulkResult;
      syncLlmCheckbox();
      await maybeExplainBulkAssignment();
      root.innerHTML = render();
      bindEvents(root);
    });
  });
}

export async function renderAssignmentLabPage(root) {
  await refreshAll();

  if (state.selectedTestCaseId) {
    await loadTasks();
  }

  root.innerHTML = render();
  bindEvents(root);
}

export async function renderAssignmentLab(root) {
  await renderAssignmentLabPage(root);
}

export async function renderPage(root) {
  await renderAssignmentLabPage(root);
}

export default renderAssignmentLabPage;
