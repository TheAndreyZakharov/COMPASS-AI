import { api } from "../api.js";
import { htmlEscape, prettyJson, toast } from "../app.js";
import { renderSummaryCards } from "../components/charts.js";
import { renderDataTable } from "../components/table.js";

const DEFAULT_ROLES = [
  "backend_developer",
  "frontend_developer",
  "fullstack_developer",
  "qa_engineer",
  "data_analyst",
  "team_lead",
];

const DEFAULT_GRADES = ["junior", "middle", "senior", "lead"];

const DEFAULT_SKILLS = [
  "python",
  "fastapi",
  "postgresql",
  "react",
  "typescript",
  "testing",
  "analytics",
  "ml",
  "devops",
  "architecture",
];

const state = {
  testCases: null,
  selectedTestCaseId: "",
};

function splitCsv(value) {
  return String(value || "")
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean);
}

function testCaseOptions(payload) {
  const items = payload?.test_cases || [];

  if (items.length === 0) {
    return '<option value="">Нет test cases</option>';
  }

  return items
    .map((item) => {
      const selected = item.test_case_id === state.selectedTestCaseId ? "selected" : "";

      return `
        <option value="${htmlEscape(item.test_case_id)}" ${selected}>
          ${htmlEscape(item.test_case_id)} · people ${htmlEscape(item.people || 0)}
        </option>
      `;
    })
    .join("");
}

function selectedTestCase() {
  return (state.testCases?.test_cases || []).find(
    (item) => item.test_case_id === state.selectedTestCaseId,
  );
}

function setAssignmentLoading(isLoading, label = "Loading...") {
  const status = document.querySelector("#assignmentStatus");
  const buttons = document.querySelectorAll("[data-assignment-action]");

  buttons.forEach((button) => {
    button.disabled = isLoading;
    button.classList.toggle("loading", isLoading);
  });

  status.className = isLoading ? "status-pill status-pending" : "status-pill status-ok";
  status.innerHTML = isLoading
    ? `<span class="status-dot"></span><span>${htmlEscape(label)}</span>`
    : '<span class="status-dot"></span><span>Готов</span>';
}

function setOutput(html) {
  document.querySelector("#assignmentOutput").innerHTML = html;
}

function renderError(title, error) {
  setOutput(`
    <article class="card">
      <span class="badge">Error</span>
      <h2>${htmlEscape(title)}</h2>
      <p class="muted">${htmlEscape(error.message || String(error))}</p>
    </article>
  `);
}

function readSelectedCase() {
  state.selectedTestCaseId = document.querySelector("#testCaseSelect").value;
}

function readGeneratePayload() {
  const testCaseId = document.querySelector("#testCaseId").value.trim();

  return {
    test_case_id: testCaseId || null,
    active_tasks_count: Number.parseInt(
      document.querySelector("#activeTasksCount").value,
      10,
    ),
    active_tasks_per_person_max: Number.parseInt(
      document.querySelector("#activeTasksPerPersonMax").value,
      10,
    ),
    availability_max: Number.parseFloat(document.querySelector("#availabilityMax").value),
    availability_min: Number.parseFloat(document.querySelector("#availabilityMin").value),
    domain_profile: document.querySelector("#testCaseDomainProfile").value,
    fatigue_max: Number.parseFloat(document.querySelector("#fatigueMax").value),
    fatigue_min: Number.parseFloat(document.querySelector("#fatigueMin").value),
    grades: splitCsv(document.querySelector("#testCaseGrades").value),
    history_depth: Number.parseInt(document.querySelector("#historyDepth").value, 10),
    learning_goals_max: Number.parseInt(
      document.querySelector("#learningGoalsMax").value,
      10,
    ),
    learning_goals_min: Number.parseInt(
      document.querySelector("#learningGoalsMin").value,
      10,
    ),
    people_count: Number.parseInt(document.querySelector("#peopleCount").value, 10),
    roles: splitCsv(document.querySelector("#testCaseRoles").value),
    seed: Number.parseInt(document.querySelector("#testCaseSeed").value, 10),
    skills: splitCsv(document.querySelector("#testCaseSkills").value),
    workload_max: Number.parseFloat(document.querySelector("#workloadMax").value),
    workload_min: Number.parseFloat(document.querySelector("#workloadMin").value),
    overwrite: document.querySelector("#testCaseOverwrite").checked,
  };
}

function renderTestCasesList() {
  const rows = state.testCases?.test_cases || [];

  if (rows.length === 0) {
    setOutput(`
      <article class="card">
        <h2>Test cases</h2>
        <p class="muted">Test cases пока не созданы.</p>
      </article>
    `);
    return;
  }

  setOutput(`
    <section class="grid grid-4">
      ${renderSummaryCards({
        test_cases: state.testCases.total || 0,
        people: rows.reduce((sum, item) => sum + Number(item.people || 0), 0),
        active_tasks: rows.reduce((sum, item) => sum + Number(item.active_tasks || 0), 0),
        history: rows.reduce((sum, item) => sum + Number(item.history || 0), 0),
      })}
    </section>

    <article class="card" style="margin-top: 16px;">
      <h2>Saved test cases</h2>
      ${renderDataTable(rows, [
        "test_case_id",
        "created_at",
        "domain_profile",
        "people",
        "active_tasks",
        "history",
        "recommendation_ready",
        "bulk_assignment_ready",
      ])}
    </article>
  `);
}

function renderGenerateResult(result) {
  const metadata = result.metadata || {};
  const counts = metadata.counts || {};
  const summaries = metadata.summaries || {};

  setOutput(`
    <section class="grid grid-4">
      ${renderSummaryCards({
        test_case: result.test_case_id || "",
        people: counts.people || 0,
        active_tasks: counts.active_tasks || 0,
        history: counts.history || 0,
      })}
    </section>

    <article class="card" style="margin-top: 16px;">
      <h2>Workload summary</h2>
      <pre class="code">${prettyJson(summaries.workload || {})}</pre>
    </article>

    <article class="card" style="margin-top: 16px;">
      <h2>Preview team</h2>
      ${renderDataTable(result.preview?.team || [])}
    </article>

    <article class="card" style="margin-top: 16px;">
      <h2>Preview active tasks</h2>
      ${renderDataTable(result.preview?.active_tasks || [])}
    </article>

    <article class="card" style="margin-top: 16px;">
      <h2>Generated payload</h2>
      <pre class="code">${prettyJson(result)}</pre>
    </article>
  `);
}

function renderSummary(summary) {
  const metadata = summary.metadata || {};
  const counts = metadata.counts || {};

  setOutput(`
    <section class="grid grid-4">
      ${renderSummaryCards({
        test_case: summary.test_case_id || "",
        people: counts.people || 0,
        active_tasks: counts.active_tasks || 0,
        history: counts.history || 0,
      })}
    </section>

    <article class="card" style="margin-top: 16px;">
      <h2>Assignment capacity</h2>
      ${renderDataTable(summary.capacity || [], [
        "employee_id",
        "name",
        "role",
        "grade",
        "current_workload",
        "fatigue_score",
        "availability_score",
        "assignment_capacity",
        "active_tasks",
      ])}
    </article>

    <article class="card" style="margin-top: 16px;">
      <h2>Team preview</h2>
      ${renderDataTable(summary.team_preview || [])}
    </article>

    <article class="card" style="margin-top: 16px;">
      <h2>Active tasks preview</h2>
      ${renderDataTable(summary.active_tasks_preview || [])}
    </article>
  `);
}

function renderTable(tableName, payload) {
  const rows = Array.isArray(payload) ? payload : [payload];

  setOutput(`
    <article class="card">
      <h2>${htmlEscape(tableName)}</h2>
      ${renderDataTable(rows)}
    </article>
  `);
}

function renderContext(context) {
  setOutput(`
    <section class="grid grid-4">
      ${renderSummaryCards({
        team_size: context.team_size || 0,
        active_tasks: context.active_tasks_count || 0,
        history_rows: context.history_rows || 0,
        pending_hours: context.estimated_pending_hours || 0,
      })}
    </section>

    <article class="card" style="margin-top: 16px;">
      <h2>Recommendation context</h2>
      <p class="muted">
        Этот payload будет использоваться на следующих этапах для single
        recommendation и bulk assignment.
      </p>
      <pre class="code">${prettyJson(context)}</pre>
    </article>
  `);
}

async function refreshTestCases(render = true) {
  state.testCases = await api.testCases();

  if (!state.selectedTestCaseId) {
    state.selectedTestCaseId = state.testCases?.test_cases?.[0]?.test_case_id || "";
  }

  const select = document.querySelector("#testCaseSelect");
  if (select) {
    select.innerHTML = testCaseOptions(state.testCases);
    select.value = state.selectedTestCaseId;
  }

  if (render) {
    renderTestCasesList();
  }
}

async function generateTestCase() {
  try {
    setAssignmentLoading(true, "Generating test case...");
    const result = await api.generateTestCase(readGeneratePayload());

    state.selectedTestCaseId = result.test_case_id;
    await refreshTestCases(false);
    renderGenerateResult(result);
    toast("Test case generated", result.test_case_id);
  } catch (error) {
    renderError("Test case generation failed", error);
    toast("Test case", error.message || String(error));
  } finally {
    setAssignmentLoading(false);
  }
}

async function loadSummary() {
  try {
    readSelectedCase();

    if (!state.selectedTestCaseId) {
      throw new Error("Сначала выбери test case.");
    }

    setAssignmentLoading(true, "Loading summary...");
    const summary = await api.testCaseSummary(state.selectedTestCaseId);
    renderSummary(summary);
  } catch (error) {
    renderError("Test case summary failed", error);
    toast("Test case", error.message || String(error));
  } finally {
    setAssignmentLoading(false);
  }
}

async function loadTable(tableName) {
  try {
    readSelectedCase();

    if (!state.selectedTestCaseId) {
      throw new Error("Сначала выбери test case.");
    }

    setAssignmentLoading(true, `Loading ${tableName}...`);
    const table = await api.testCaseTable(state.selectedTestCaseId, tableName);
    renderTable(tableName, table);
  } catch (error) {
    renderError(`${tableName} loading failed`, error);
    toast("Test case table", error.message || String(error));
  } finally {
    setAssignmentLoading(false);
  }
}

async function loadContext() {
  try {
    readSelectedCase();

    if (!state.selectedTestCaseId) {
      throw new Error("Сначала выбери test case.");
    }

    setAssignmentLoading(true, "Loading context...");
    const context = await api.testCaseRecommendationContext(state.selectedTestCaseId);
    renderContext(context);
  } catch (error) {
    renderError("Recommendation context failed", error);
    toast("Recommendation context", error.message || String(error));
  } finally {
    setAssignmentLoading(false);
  }
}

async function deleteSelectedCase() {
  try {
    readSelectedCase();

    if (!state.selectedTestCaseId) {
      throw new Error("Сначала выбери test case.");
    }

    const testCaseId = state.selectedTestCaseId;
    setAssignmentLoading(true, "Deleting test case...");
    const result = await api.deleteTestCase(testCaseId);

    state.selectedTestCaseId = "";
    await refreshTestCases(true);
    toast("Test case deleted", result.test_case_id);
  } catch (error) {
    renderError("Delete test case failed", error);
    toast("Delete test case", error.message || String(error));
  } finally {
    setAssignmentLoading(false);
  }
}

function bindEvents() {
  document.querySelector("#testCaseSelect").addEventListener("change", readSelectedCase);

  document.querySelector("[data-assignment-action='generate']").addEventListener(
    "click",
    () => {
      generateTestCase();
    },
  );

  document.querySelector("[data-assignment-action='list']").addEventListener("click", () => {
    refreshTestCases(true);
  });

  document.querySelector("[data-assignment-action='summary']").addEventListener(
    "click",
    () => {
      loadSummary();
    },
  );

  document.querySelector("[data-assignment-action='team']").addEventListener("click", () => {
    loadTable("team");
  });

  document.querySelector("[data-assignment-action='active-tasks']").addEventListener(
    "click",
    () => {
      loadTable("active_tasks");
    },
  );

  document.querySelector("[data-assignment-action='history']").addEventListener("click", () => {
    loadTable("history");
  });

  document.querySelector("[data-assignment-action='context']").addEventListener("click", () => {
    loadContext();
  });

  document.querySelector("[data-assignment-action='delete']").addEventListener("click", () => {
    deleteSelectedCase();
  });
}

export async function renderAssignmentLab() {
  state.testCases = await api.testCases();
  state.selectedTestCaseId = state.testCases?.test_cases?.[0]?.test_case_id || "";

  window.setTimeout(() => {
    bindEvents();
    renderTestCasesList();
  }, 0);

  return `
    <section class="grid grid-2">
      <article class="card">
        <div class="viewer-section-header">
          <div>
            <h2>Assignment Lab</h2>
            <p class="muted">
              Генерация отдельной текущей команды для проверки обученных моделей.
            </p>
          </div>
          <div class="status-pill status-ok" id="assignmentStatus">
            <span class="status-dot"></span>
            <span>Готов</span>
          </div>
        </div>

        <div class="grid grid-2">
          <div class="form-row">
            <label for="testCaseId">test_case_id</label>
            <input
              class="input"
              id="testCaseId"
              placeholder="empty = auto id"
              type="text"
            />
          </div>

          <div class="form-row">
            <label for="testCaseDomainProfile">domain_profile</label>
            <select class="select" id="testCaseDomainProfile">
              <option value="developers">developers</option>
              <option value="designers">designers</option>
              <option value="custom">custom</option>
            </select>
          </div>

          <div class="form-row">
            <label for="peopleCount">people_count</label>
            <input class="input" id="peopleCount" min="1" type="number" value="10" />
          </div>

          <div class="form-row">
            <label for="activeTasksCount">active_tasks_count</label>
            <input class="input" id="activeTasksCount" min="0" type="number" value="16" />
          </div>

          <div class="form-row">
            <label for="historyDepth">history_depth</label>
            <input class="input" id="historyDepth" min="0" type="number" value="8" />
          </div>

          <div class="form-row">
            <label for="testCaseSeed">seed</label>
            <input class="input" id="testCaseSeed" type="number" value="21001" />
          </div>
        </div>

        <div class="grid grid-2">
          <div class="form-row">
            <label for="workloadMin">workload_min</label>
            <input class="input" id="workloadMin" step="0.01" type="number" value="0.10" />
          </div>
          <div class="form-row">
            <label for="workloadMax">workload_max</label>
            <input class="input" id="workloadMax" step="0.01" type="number" value="0.85" />
          </div>
          <div class="form-row">
            <label for="fatigueMin">fatigue_min</label>
            <input class="input" id="fatigueMin" step="0.01" type="number" value="0.05" />
          </div>
          <div class="form-row">
            <label for="fatigueMax">fatigue_max</label>
            <input class="input" id="fatigueMax" step="0.01" type="number" value="0.80" />
          </div>
          <div class="form-row">
            <label for="availabilityMin">availability_min</label>
            <input
              class="input"
              id="availabilityMin"
              step="0.01"
              type="number"
              value="0.15"
            />
          </div>
          <div class="form-row">
            <label for="availabilityMax">availability_max</label>
            <input
              class="input"
              id="availabilityMax"
              step="0.01"
              type="number"
              value="1.00"
            />
          </div>
        </div>

        <label class="checkbox-row">
          <input id="testCaseOverwrite" type="checkbox" />
          <span>overwrite existing test case</span>
        </label>

        <div class="toolbar">
          <button class="button button-primary" data-assignment-action="generate" type="button">
            Generate test case
          </button>
          <button class="button button-secondary" data-assignment-action="list" type="button">
            Refresh list
          </button>
        </div>
      </article>

      <article class="card">
        <h2>Domain options</h2>
        <div class="form-row">
          <label for="testCaseRoles">roles CSV</label>
          <textarea class="textarea" id="testCaseRoles" rows="3">${
            DEFAULT_ROLES.join(", ")
          }</textarea>
        </div>

        <div class="form-row">
          <label for="testCaseGrades">grades CSV</label>
          <textarea class="textarea" id="testCaseGrades" rows="2">${
            DEFAULT_GRADES.join(", ")
          }</textarea>
        </div>

        <div class="form-row">
          <label for="testCaseSkills">skills CSV</label>
          <textarea class="textarea" id="testCaseSkills" rows="5">${
            DEFAULT_SKILLS.join(", ")
          }</textarea>
        </div>

        <div class="grid grid-3">
          <div class="form-row">
            <label for="learningGoalsMin">learning_goals_min</label>
            <input class="input" id="learningGoalsMin" min="0" type="number" value="1" />
          </div>
          <div class="form-row">
            <label for="learningGoalsMax">learning_goals_max</label>
            <input class="input" id="learningGoalsMax" min="0" type="number" value="3" />
          </div>
          <div class="form-row">
            <label for="activeTasksPerPersonMax">active_tasks_per_person_max</label>
            <input
              class="input"
              id="activeTasksPerPersonMax"
              min="0"
              type="number"
              value="4"
            />
          </div>
        </div>
      </article>
    </section>

    <section class="grid grid-2" style="margin-top: 16px;">
      <article class="card">
        <h2>Saved test cases</h2>
        <div class="toolbar">
          <select class="select" id="testCaseSelect">
            ${testCaseOptions(state.testCases)}
          </select>
          <button class="button button-secondary" data-assignment-action="summary" type="button">
            Summary
          </button>
          <button class="button button-secondary" data-assignment-action="team" type="button">
            Team
          </button>
          <button
            class="button button-secondary"
            data-assignment-action="active-tasks"
            type="button"
          >
            Active tasks
          </button>
          <button class="button button-secondary" data-assignment-action="history" type="button">
            History
          </button>
          <button class="button button-secondary" data-assignment-action="context" type="button">
            Context
          </button>
          <button class="button button-danger" data-assignment-action="delete" type="button">
            Delete
          </button>
        </div>
      </article>

      <article class="card">
        <h2>Selected test case</h2>
        <pre class="code">${prettyJson(selectedTestCase() || {})}</pre>
      </article>
    </section>

    <section id="assignmentOutput" style="margin-top: 16px;">
      <article class="card">
        <h2>Assignment Lab</h2>
        <p class="muted">
          Создай test case, чтобы на следующих этапах проверить single
          recommendation и bulk assignment.
        </p>
      </article>
    </section>
  `;
}