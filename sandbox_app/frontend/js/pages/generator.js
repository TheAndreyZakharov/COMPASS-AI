import { api } from "../api.js";
import {
  getLastDatasetId,
  htmlEscape,
  prettyJson,
  setLastDatasetId,
  toast,
} from "../app.js";

const DEFAULTS = {
  datasetId: "ui_full_dataset",
  domainProfile: "developers",
  datasetMode: "small_preview",
  targetMode: "balanced",
  seed: 12001,
  employeesCount: 10,
  tasksCount: 100,
  projectsCount: 5,
  historyDepthPerEmployee: 5,
  targetPairs: 1000,
  candidatesPerTask: 10,
};

const DATASET_MODES = {
  small_preview: {
    employeesCount: 10,
    tasksCount: 100,
    historyDepthPerEmployee: 12,
    targetPairs: 1000,
    candidatesPerTask: 10,
  },
  medium_validation: {
    employeesCount: 30,
    tasksCount: 1000,
    historyDepthPerEmployee: 30,
    targetPairs: 30000,
    candidatesPerTask: 15,
  },
  large_training: {
    employeesCount: 100,
    tasksCount: 10000,
    historyDepthPerEmployee: 60,
    targetPairs: 1000000,
    candidatesPerTask: 20,
  },
  huge_training: {
    employeesCount: 100,
    tasksCount: 10000,
    historyDepthPerEmployee: 60,
    targetPairs: 1000000,
    candidatesPerTask: 20,
  },
};

function numberValue(id, fallback) {
  const element = document.querySelector(`#${id}`);
  const value = Number.parseInt(element?.value || "", 10);
  return Number.isFinite(value) ? value : fallback;
}

function booleanValue(id) {
  return Boolean(document.querySelector(`#${id}`)?.checked);
}

function textValue(id, fallback = "") {
  const value = document.querySelector(`#${id}`)?.value;
  return value === undefined || value === "" ? fallback : value;
}

function modeSettings(modeName) {
  return DATASET_MODES[modeName] || DATASET_MODES.small_preview;
}

function buildCommonPayload() {
  return {
    dataset_id: textValue("generatorDatasetId", DEFAULTS.datasetId),
    domain_profile: textValue("generatorDomainProfile", DEFAULTS.domainProfile),
    seed: numberValue("generatorSeed", DEFAULTS.seed),
    overwrite: booleanValue("generatorOverwrite"),
  };
}

function buildFullDatasetPayload() {
  const datasetMode = textValue("generatorDatasetMode", DEFAULTS.datasetMode);

  return {
    ...buildCommonPayload(),
    dataset_mode: datasetMode,
    employees_count: numberValue("generatorEmployeesCount", DEFAULTS.employeesCount),
    tasks_count: numberValue("generatorTasksCount", DEFAULTS.tasksCount),
    history_depth_per_employee: numberValue(
      "generatorHistoryDepth",
      DEFAULTS.historyDepthPerEmployee,
    ),
    target_pairs: numberValue("generatorTargetPairs", DEFAULTS.targetPairs),
    candidates_per_task: numberValue("generatorCandidatesPerTask", DEFAULTS.candidatesPerTask),
    target_mode: textValue("generatorTargetMode", DEFAULTS.targetMode),
    confirm_huge_generation: booleanValue("generatorConfirmHuge"),
  };
}

function buildTeamPayload() {
  return {
    ...buildCommonPayload(),
    employees_count: numberValue("generatorEmployeesCount", DEFAULTS.employeesCount),
  };
}

function buildTasksPayload() {
  return {
    ...buildCommonPayload(),
    tasks_count: numberValue("generatorTasksCount", DEFAULTS.tasksCount),
    projects_count: numberValue("generatorProjectsCount", DEFAULTS.projectsCount),
  };
}

function buildHistoryPayload() {
  return {
    ...buildCommonPayload(),
    history_depth_per_employee: numberValue(
      "generatorHistoryDepth",
      DEFAULTS.historyDepthPerEmployee,
    ),
  };
}

function profileOptions(featureSchemas) {
  const rawItems = featureSchemas.items || featureSchemas.profiles || featureSchemas || [];
  const items = Array.isArray(rawItems) ? rawItems : [];

  if (items.length === 0) {
    return `<option value="${DEFAULTS.domainProfile}">${DEFAULTS.domainProfile}</option>`;
  }

  return items
    .map((item) => {
      const profileId = item.profile_id || item.id || item.name;
      const label = item.name || item.title || profileId;
      const selected = profileId === DEFAULTS.domainProfile ? "selected" : "";

      return `
        <option value="${htmlEscape(profileId)}" ${selected}>
          ${htmlEscape(label)}
        </option>
      `;
    })
    .join("");
}

function setLoading(isLoading, label = "Генерация...") {
  const buttons = document.querySelectorAll("[data-generator-action]");
  const status = document.querySelector("#generatorStatus");

  buttons.forEach((button) => {
    button.disabled = isLoading;
    button.classList.toggle("loading", isLoading);
  });

  status.className = isLoading ? "status-pill status-pending" : "status-pill status-ok";
  status.innerHTML = isLoading
    ? `<span class="status-dot"></span><span>${htmlEscape(label)}</span>`
    : '<span class="status-dot"></span><span>Готов к запуску</span>';
}

function resultCounts(metadata) {
  const counts = metadata?.counts || {};
  const history = counts.assignment_history || counts.history || 0;
  const pairs = counts.training_pairs || 0;

  return [
    ["employees", counts.employees || 0],
    ["tasks", counts.tasks || 0],
    ["history", history],
    ["training_pairs", pairs],
  ];
}

function renderResult(result, generatorKind) {
  const metadata = result.metadata || {};
  const counts = resultCounts(metadata);
  const datasetId = result.dataset_id || metadata.dataset_id || "";
  const datasetDir = result.dataset_dir || metadata.dataset_dir || "";

  if (datasetId) {
    setLastDatasetId(datasetId);
  }

  const cards = counts
    .map(
      ([name, value]) => `
        <article class="card kpi">
          <span class="muted">${htmlEscape(name)}</span>
          <strong>${htmlEscape(value)}</strong>
          <small class="muted">generated count</small>
        </article>
      `,
    )
    .join("");

  const openViewerButton = datasetId
    ? '<button class="button button-primary" id="openGeneratedDataset" type="button">Открыть в Data Viewer</button>'
    : "";

  const html = `
    <section class="grid grid-3">
      <article class="card">
        <h2>Dataset</h2>
        <p><strong>${htmlEscape(datasetId || "not returned")}</strong></p>
        <p class="muted">${htmlEscape(datasetDir || "dataset_dir not returned")}</p>
      </article>
      <article class="card">
        <h2>Generator</h2>
        <p><strong>${htmlEscape(generatorKind)}</strong></p>
        <p class="muted">Completed successfully</p>
      </article>
      <article class="card">
        <h2>Next step</h2>
        ${openViewerButton}
      </article>
    </section>

    <section class="grid grid-4 generator-counts" style="margin-top: 16px;">
      ${cards}
    </section>

    <article class="card" style="margin-top: 16px;">
      <h2>Response JSON</h2>
      <pre class="code">${prettyJson(result)}</pre>
    </article>
  `;

  document.querySelector("#generatorResult").innerHTML = html;

  const openButton = document.querySelector("#openGeneratedDataset");
  if (openButton) {
    openButton.addEventListener("click", () => {
      window.history.pushState({}, "", "/viewer");
      window.dispatchEvent(new PopStateEvent("popstate"));
    });
  }
}

function renderErrorState(error) {
  const message = error?.message || String(error);

  document.querySelector("#generatorResult").innerHTML = `
    <article class="card">
      <span class="badge">Error</span>
      <h2>Генерация не выполнена</h2>
      <p class="muted">${htmlEscape(message)}</p>
    </article>
  `;
}

async function runGenerator(kind) {
  const actions = {
    dataset: {
      label: "Full dataset",
      request: () => api.generateDataset(buildFullDatasetPayload()),
    },
    team: {
      label: "Team",
      request: () => api.generateTeam(buildTeamPayload()),
    },
    tasks: {
      label: "Tasks",
      request: () => api.generateTasks(buildTasksPayload()),
    },
    history: {
      label: "History",
      request: () => api.generateHistory(buildHistoryPayload()),
    },
  };

  const action = actions[kind];
  if (!action) {
    toast("Generator", `Unknown generator: ${kind}`);
    return;
  }

  try {
    setLoading(true, `${action.label}...`);
    const result = await action.request();
    renderResult(result, action.label);
    toast("Готово", `${action.label} успешно выполнен.`);
  } catch (error) {
    renderErrorState(error);
    toast("Ошибка генерации", error.message || String(error));
  } finally {
    setLoading(false);
  }
}

function applyModePreset() {
  const modeName = textValue("generatorDatasetMode", DEFAULTS.datasetMode);
  const settings = modeSettings(modeName);

  document.querySelector("#generatorEmployeesCount").value = settings.employeesCount;
  document.querySelector("#generatorTasksCount").value = settings.tasksCount;
  document.querySelector("#generatorHistoryDepth").value = settings.historyDepthPerEmployee;
  document.querySelector("#generatorTargetPairs").value = settings.targetPairs;
  document.querySelector("#generatorCandidatesPerTask").value = settings.candidatesPerTask;

  const hugePanel = document.querySelector("#hugeGenerationPanel");
  hugePanel.hidden = modeName !== "huge_training";
}

function bindGeneratorEvents() {
  document.querySelectorAll("[data-generator-action]").forEach((button) => {
    button.addEventListener("click", () => {
      runGenerator(button.dataset.generatorAction);
    });
  });

  document.querySelector("#generatorDatasetMode").addEventListener("change", applyModePreset);

  document.querySelector("#fillLastDataset").addEventListener("click", () => {
    const lastDatasetId = getLastDatasetId();
    if (lastDatasetId) {
      document.querySelector("#generatorDatasetId").value = lastDatasetId;
      toast("Dataset выбран", lastDatasetId);
    } else {
      toast("Dataset не найден", "Сначала сгенерируй dataset.");
    }
  });

  document.querySelector("#previewPayload").addEventListener("click", () => {
    const payload = buildFullDatasetPayload();

    document.querySelector("#generatorResult").innerHTML = `
      <article class="card">
        <h2>Full dataset payload preview</h2>
        <pre class="code">${prettyJson(payload)}</pre>
      </article>
    `;
  });

  applyModePreset();
}

export async function renderGenerator() {
  const featureSchemas = await api.featureSchemas();

  window.setTimeout(bindGeneratorEvents, 0);

  return `
    <section class="grid grid-2">
      <article class="card">
        <div class="generator-header">
          <div>
            <h2>Data Generator</h2>
            <p class="muted">
              Генерирует full dataset, team, tasks и history через готовые backend endpoints.
            </p>
          </div>
          <div class="status-pill status-ok" id="generatorStatus">
            <span class="status-dot"></span>
            <span>Готов к запуску</span>
          </div>
        </div>

        <form class="form" id="generatorForm">
          <div class="grid grid-2">
            <div class="form-row">
              <label for="generatorDatasetId">dataset_id</label>
              <input
                class="input"
                id="generatorDatasetId"
                type="text"
                value="${htmlEscape(getLastDatasetId() || DEFAULTS.datasetId)}"
              />
            </div>

            <div class="form-row">
              <label for="generatorDomainProfile">domain_profile</label>
              <select class="select" id="generatorDomainProfile">
                ${profileOptions(featureSchemas)}
              </select>
            </div>

            <div class="form-row">
              <label for="generatorSeed">seed</label>
              <input class="input" id="generatorSeed" type="number" value="${DEFAULTS.seed}" />
            </div>

            <div class="form-row">
              <label for="generatorDatasetMode">dataset_mode</label>
              <select class="select" id="generatorDatasetMode">
                <option value="small_preview">small_preview</option>
                <option value="medium_validation">medium_validation</option>
                <option value="large_training">large_training</option>
                <option value="huge_training">huge_training</option>
              </select>
            </div>

            <div class="form-row">
              <label for="generatorEmployeesCount">employees_count</label>
              <input
                class="input"
                id="generatorEmployeesCount"
                min="1"
                type="number"
                value="${DEFAULTS.employeesCount}"
              />
            </div>

            <div class="form-row">
              <label for="generatorTasksCount">tasks_count</label>
              <input
                class="input"
                id="generatorTasksCount"
                min="1"
                type="number"
                value="${DEFAULTS.tasksCount}"
              />
            </div>

            <div class="form-row">
              <label for="generatorProjectsCount">projects_count</label>
              <input
                class="input"
                id="generatorProjectsCount"
                min="1"
                type="number"
                value="${DEFAULTS.projectsCount}"
              />
            </div>

            <div class="form-row">
              <label for="generatorHistoryDepth">history_depth_per_employee</label>
              <input
                class="input"
                id="generatorHistoryDepth"
                min="1"
                type="number"
                value="${DEFAULTS.historyDepthPerEmployee}"
              />
            </div>

            <div class="form-row">
              <label for="generatorTargetPairs">target_pairs</label>
              <input
                class="input"
                id="generatorTargetPairs"
                min="1"
                type="number"
                value="${DEFAULTS.targetPairs}"
              />
            </div>

            <div class="form-row">
              <label for="generatorCandidatesPerTask">candidates_per_task</label>
              <input
                class="input"
                id="generatorCandidatesPerTask"
                min="1"
                type="number"
                value="${DEFAULTS.candidatesPerTask}"
              />
            </div>

            <div class="form-row">
              <label for="generatorTargetMode">target_mode</label>
              <select class="select" id="generatorTargetMode">
                <option value="balanced">balanced</option>
                <option value="quality">quality</option>
                <option value="speed">speed</option>
                <option value="learning">learning</option>
                <option value="risk_aware">risk_aware</option>
              </select>
            </div>

            <div class="form-row checkbox-row">
              <label>
                <input checked id="generatorOverwrite" type="checkbox" />
                overwrite
              </label>
            </div>
          </div>

          <div class="card nested-card" id="hugeGenerationPanel" hidden>
            <h3>Huge generation protection</h3>
            <p class="muted">
              huge_training может создать очень большой dataset. Backend требует явное
              подтверждение confirm_huge_generation.
            </p>
            <label class="checkbox-inline">
              <input id="generatorConfirmHuge" type="checkbox" />
              confirm_huge_generation
            </label>
          </div>

          <div class="toolbar">
            <button
              class="button button-primary"
              data-generator-action="dataset"
              type="button"
            >
              Generate full dataset
            </button>
            <button
              class="button button-secondary"
              data-generator-action="team"
              type="button"
            >
              Generate team
            </button>
            <button
              class="button button-secondary"
              data-generator-action="tasks"
              type="button"
            >
              Generate tasks
            </button>
            <button
              class="button button-secondary"
              data-generator-action="history"
              type="button"
            >
              Generate history
            </button>
            <button class="button button-secondary" id="previewPayload" type="button">
              Preview payload
            </button>
            <button class="button button-secondary" id="fillLastDataset" type="button">
              Use last dataset
            </button>
          </div>
        </form>
      </article>

      <article class="card">
        <h2>Как работает</h2>
        <p class="muted">
          Full dataset запускает backend orchestration: employees, tasks, backlog,
          assignment_history, training_pairs.parquet, dataset_metadata и generation_report.
        </p>
        <p class="muted">
          Team, Tasks и History можно запускать отдельно для быстрой проверки и настройки.
          History требует dataset_id, где уже есть employees.json и tasks.json.
        </p>
        <pre class="code">${prettyJson({
          endpoints: [
            "POST /api/generate/dataset",
            "POST /api/generate/team",
            "POST /api/generate/tasks",
            "POST /api/generate/history",
          ],
          last_dataset_id: getLastDatasetId() || null,
        })}</pre>
      </article>
    </section>

    <section id="generatorResult" style="margin-top: 16px;">
      <article class="card">
        <h2>Result</h2>
        <p class="muted">
          После генерации здесь появятся dataset_id, dataset_dir, counts и response JSON.
        </p>
      </article>
    </section>
  `;
}