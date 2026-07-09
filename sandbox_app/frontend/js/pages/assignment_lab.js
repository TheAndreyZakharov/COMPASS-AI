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
  testCases: [],
  testCaseSummaries: {},
  recommendationContexts: {},
  trainingSessions: [],
  assignmentSessions: [],
  selectedTestCaseId: "",
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

function htmlEscape(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function prettyJson(value) {
  return htmlEscape(JSON.stringify(value ?? {}, null, 2));
}

function toast(message, type = "info") {
  window.dispatchEvent(
    new CustomEvent("sandbox-toast", {
      detail: {
        title: type === "error" ? "Assignment Lab error" : "Assignment Lab",
        message,
        type,
      },
    }),
  );
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

function modelOptions() {
  return MODEL_NAMES.map((name) => ({
    label: name,
    value: name,
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

    return {
      label: `${item.test_case_id} · ${summary.people_count ?? item.people_count ?? 0} people`,
      value: item.test_case_id,
    };
  });
}

function trainingSessionOptions() {
  return state.trainingSessions.map((item) => ({
    label: `${item.session_id} · ${item.status || "unknown"}`,
    value: item.session_id,
  }));
}

function taskOptions() {
  return state.tasks.map((task) => ({
    label: `${task.task_id} · ${task.title || "Untitled"}`,
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
          <h3>Filters</h3>
          <p class="muted">Фильтры по результатам single и bulk assignment.</p>
        </div>
        <button id="clearAssignmentFilters" class="button-secondary" type="button">
          Clear filters
        </button>
      </div>

      <div class="form-grid">
        ${textInput("filterPerson", "Person", state.filters.person)}
        ${textInput("filterStatus", "Task status", state.filters.status)}
        ${textInput("filterProject", "Project", state.filters.project)}
        ${textInput("filterRisk", "Risk", state.filters.risk)}
      </div>
    </section>
  `;
}

function renderGeneratorPanel() {
  return `
    <section class="panel">
      <div class="section-heading">
        <div>
          <h2>Test case generator</h2>
          <p class="muted">
            Создание отдельной команды для проверки recommendations.
          </p>
        </div>
        <button id="refreshAssignmentData" class="button-secondary" type="button">
          Refresh
        </button>
      </div>

      <div class="form-grid">
        ${textInput("testCaseId", "test_case_id", "ui_test_case")}
        ${selectInput(
          "domainProfile",
          "Domain",
          [
            { label: "developers", value: "developers" },
            { label: "designers", value: "designers" },
            { label: "custom", value: "custom" },
          ],
          "developers",
        )}
        ${numberInput("peopleCount", "People count", 8, "min='1' max='500'")}
        ${numberInput("activeTasksCount", "Active tasks", 12, "min='1' max='5000'")}
        ${numberInput("historyDepth", "History depth", 4, "min='0' max='200'")}
        ${numberInput("seed", "Seed", 27024, "min='1'")}
        ${textInput("roles", "Roles CSV", "Backend Engineer,Frontend Engineer,QA Engineer")}
        ${textInput("grades", "Grades CSV", "junior,middle,senior,lead")}
        ${textInput("skills", "Skills CSV", "python,fastapi,react,sql,testing,ml")}
      </div>

      <div class="actions-row">
        <button id="generateTestCase" type="button">Generate test case</button>
      </div>
    </section>
  `;
}

function renderSelectionPanel() {
  return `
    <section class="panel">
      <div class="section-heading">
        <div>
          <h2>Recommendation controls</h2>
          <p class="muted">
            Выбор saved model, test case, task и режима рекомендации.
          </p>
        </div>
      </div>

      <div class="form-grid">
        ${selectInput(
          "trainingSessionId",
          "Training session",
          trainingSessionOptions(),
          state.selectedTrainingSessionId,
        )}
        ${selectInput("modelName", "Model", modelOptions(), state.selectedModelName)}
        ${selectInput(
          "testCaseSelect",
          "Test case",
          testCaseOptions(),
          state.selectedTestCaseId,
        )}
        ${selectInput("taskSelect", "Task", taskOptions(), state.selectedTaskId)}
        ${selectInput(
          "recommendationMode",
          "Recommendation mode",
          [
            { label: "balanced", value: "balanced" },
            { label: "best_quality", value: "best_quality" },
            { label: "fastest_delivery", value: "fastest_delivery" },
            { label: "best_learning", value: "best_learning" },
            { label: "risk_aware", value: "risk_aware" },
          ],
          "balanced",
        )}
        ${selectInput(
          "assignmentMode",
          "Assignment mode",
          [
            { label: "balanced", value: "balanced" },
            { label: "best_quality", value: "best_quality" },
            { label: "fastest_delivery", value: "fastest_delivery" },
            { label: "best_learning", value: "best_learning" },
            { label: "risk_aware", value: "risk_aware" },
          ],
          "balanced",
        )}
        ${numberInput("topK", "Top K", 3, "min='1' max='100'")}
        ${numberInput(
          "maxWorkload",
          "Max workload per person",
          1.2,
          "min='0.1' max='1.5' step='0.05'",
        )}
        ${numberInput(
          "fairnessPenalty",
          "Fairness penalty",
          0.12,
          "min='0' max='2' step='0.01'",
        )}
        ${numberInput(
          "fatiguePenalty",
          "Fatigue penalty",
          0.12,
          "min='0' max='2' step='0.01'",
        )}
        ${numberInput(
          "learningBonus",
          "Learning bonus",
          0.08,
          "min='0' max='2' step='0.01'",
        )}
        ${numberInput(
          "workloadPenalty",
          "Workload penalty",
          0.18,
          "min='0' max='2' step='0.01'",
        )}
        <label class="checkbox-label">
          <input
            id="useLlmExplanations"
            type="checkbox"
            ${state.useLlmExplanations ? "checked" : ""}
          >
          <span>LLM explanations через Qwen/Ollama</span>
        </label>
      </div>

      <div class="actions-row">
        <button id="loadRecommendableTasks" class="button-secondary" type="button">
          Load tasks
        </button>
        <button id="runSingleRecommendation" type="button">
          Run single recommendation
        </button>
        <button id="runBulkAssignment" type="button">Run bulk assignment</button>
      </div>
    </section>
  `;
}

function renderTestCasesPanel() {
  if (!state.testCases.length) {
    return `
      <section class="panel">
        <h3>Test cases</h3>
        <p class="muted">Test cases пока не созданы.</p>
      </section>
    `;
  }

  return `
    <section class="panel">
      <h3>Test cases</h3>
      <div class="list-grid">
        ${state.testCases
          .map((item) => {
            const summary = testCaseSummary(item.test_case_id);
            const context = recommendationContext(item.test_case_id);
            const peopleCount = summary.people_count ?? item.people_count ?? 0;
            const tasksCount =
              summary.active_tasks_count ?? item.active_tasks_count ?? 0;
            const historyCount = summary.history_count ?? item.history_count ?? 0;
            const contextTasks = context.pending_tasks_count ?? context.tasks_count ?? 0;

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
                  people: ${htmlEscape(peopleCount)}
                  · tasks: ${htmlEscape(tasksCount)}
                  · history: ${htmlEscape(historyCount)}
                  · context tasks: ${htmlEscape(contextTasks)}
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

  return `
    <section class="panel">
      <div class="section-heading">
        <div>
          <h3>${htmlEscape(title)}</h3>
          <p class="muted">
            ${explanation.llm_used ? "Qwen/Ollama" : "Fallback"}
            · ranking source: ${htmlEscape(
              explanation.ranking_source || "model_output_unchanged",
            )}
          </p>
        </div>
        <span class="pill">${htmlEscape(explanation.status || "ok")}</span>
      </div>

      <p>${htmlEscape(explanation.summary || "")}</p>

      ${
        candidateExplanations.length
          ? `
            <div class="explanation-list">
              ${candidateExplanations
                .map(
                  (item) => `
                    <article class="explanation-card">
                      <strong>${htmlEscape(item.employee_id || "")}</strong>
                      <p>${htmlEscape(item.explanation || "")}</p>
                      <p class="muted">
                        Strengths: ${htmlEscape(
                          Array.isArray(item.strengths)
                            ? item.strengths.join(", ")
                            : item.strengths || "",
                        )}
                      </p>
                      <p class="muted">
                        Concerns: ${htmlEscape(
                          Array.isArray(item.concerns)
                            ? item.concerns.join(", ")
                            : item.concerns || "",
                        )}
                      </p>
                    </article>
                  `,
                )
                .join("")}
            </div>
          `
          : ""
      }

      ${
        explanation.fairness_note ||
        explanation.workload_note ||
        explanation.unassigned_note ||
        explanation.risks_note
          ? `
            <div class="explanation-list">
              <article class="explanation-card">
                <strong>Fairness</strong>
                <p>${htmlEscape(explanation.fairness_note || "")}</p>
              </article>
              <article class="explanation-card">
                <strong>Workload</strong>
                <p>${htmlEscape(explanation.workload_note || "")}</p>
              </article>
              <article class="explanation-card">
                <strong>Unassigned</strong>
                <p>${htmlEscape(explanation.unassigned_note || "")}</p>
              </article>
              <article class="explanation-card">
                <strong>Risks</strong>
                <p>${htmlEscape(explanation.risks_note || "")}</p>
              </article>
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
        <h3>Single recommendation</h3>
        <p class="muted">Запусти single recommendation, чтобы увидеть top candidates.</p>
      </section>
    `;
  }

  const filteredCandidates = applyFilters(state.singleResult.candidates || []);
  const result = {
    ...state.singleResult,
    candidates: filteredCandidates,
  };

  return `
    ${renderRecommendationCards(result, { title: "Single recommendation top candidates" })}
    ${renderCandidateComparison(filteredCandidates, { title: "Single candidate comparison" })}
    ${renderExplanationPanel("Qwen explanation", state.singleExplanation)}
    <section class="panel">
      <h3>Single recommendation raw JSON</h3>
      <pre>${prettyJson(state.singleResult)}</pre>
    </section>
  `;
}

function renderBulkKanban(assignedRows, unassignedRows) {
  const assigned = assignedRows || [];
  const unassigned = unassignedRows || [];

  return `
    <section class="panel">
      <div class="section-heading">
        <div>
          <h3>Kanban after assignment</h3>
          <p class="muted">Назначенные и неназначенные задачи после симуляции.</p>
        </div>
      </div>

      <div class="kanban-board">
        <div class="kanban-column">
          <h4>Assigned · ${assigned.length}</h4>
          ${assigned
            .map(
              (row) => `
                <article class="kanban-card">
                  <strong>${htmlEscape(row.task_title || row.task_id)}</strong>
                  <p>${htmlEscape(row.assigned_employee_name || "—")}</p>
                  <span>${htmlEscape(row.priority || "—")}</span>
                </article>
              `,
            )
            .join("")}
        </div>

        <div class="kanban-column">
          <h4>Unassigned · ${unassigned.length}</h4>
          ${unassigned
            .map(
              (row) => `
                <article class="kanban-card warning">
                  <strong>${htmlEscape(row.task_title || row.task_id)}</strong>
                  <p>${htmlEscape(row.reason || "—")}</p>
                  <span>${htmlEscape(row.priority || "—")}</span>
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
      <h3>Export results</h3>
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
        <h3>Bulk assignment</h3>
        <p class="muted">Запусти bulk assignment, чтобы увидеть распределение задач.</p>
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
    ${renderExplanationPanel("Qwen bulk assignment explanation", state.bulkExplanation)}
    ${renderExportLinks(state.bulkResult)}
    <section class="panel">
      <h3>Bulk assignment raw JSON</h3>
      <pre>${prettyJson(state.bulkResult)}</pre>
    </section>
  `;
}

function renderAssignmentSessionsPanel() {
  if (!state.assignmentSessions.length) {
    return `
      <section class="panel">
        <h3>Assignment sessions</h3>
        <p class="muted">Сохранённых assignment sessions пока нет.</p>
      </section>
    `;
  }

  return `
    <section class="panel">
      <h3>Assignment sessions</h3>
      <div class="list-grid">
        ${state.assignmentSessions
          .map(
            (item) => `
              <button
                class="list-card"
                data-assignment-session-id="${htmlEscape(
                  item.assignment_session_id,
                )}"
                type="button"
              >
                <strong>${htmlEscape(item.assignment_session_id)}</strong>
                <span>
                  assigned: ${htmlEscape(item.assigned_tasks ?? 0)}
                  · unassigned: ${htmlEscape(item.unassigned_tasks ?? 0)}
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
          <p class="eyebrow">Assignment Lab</p>
          <h1>Recommendation UI</h1>
          <p>
            Проверка single task recommendation и bulk assignment через saved
            models, test cases, score breakdown, risks, workload и fairness.
          </p>
        </div>
      </section>

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
  const [testCases, trainingSessions, assignmentSessions] = await Promise.all([
    api.testCases(),
    api.trainingSessions(),
    api.assignmentSessions(),
  ]);

  state.testCases = testCases.test_cases || testCases.items || [];
  state.trainingSessions = trainingSessions.training_sessions || [];
  state.assignmentSessions = assignmentSessions.assignment_sessions || [];

  if (!state.selectedTestCaseId && state.testCases.length) {
    state.selectedTestCaseId = state.testCases[0].test_case_id;
  }

  if (!state.selectedTrainingSessionId && state.trainingSessions.length) {
    state.selectedTrainingSessionId = state.trainingSessions[0].session_id;
  }

  await Promise.all([
    loadTestCaseSummaries(),
    loadRecommendationContexts(),
  ]);
}

async function loadTasks() {
  if (!state.selectedTestCaseId) {
    toast("Сначала выбери test case", "error");
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
  toast("Test case generated", "success");
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
  toast("Single recommendation completed", "success");
}

async function runBulkAssignment() {
  state.selectedTrainingSessionId = selectedValue("trainingSessionId");
  state.selectedModelName = selectedValue("modelName");
  state.selectedTestCaseId = selectedValue("testCaseSelect");

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
    task_statuses: ["todo"],
    save_session: true,
  };

  state.bulkResult = await api.runBulkAssignment(payload);
  syncLlmCheckbox();
  await maybeExplainBulkAssignment();
  await refreshAll();
  toast("Bulk assignment completed", "success");
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