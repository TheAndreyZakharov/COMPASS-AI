import { api } from "../api.js";
import {
  getLastDatasetId,
  htmlEscape,
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

const FEATURE_GROUPS = ["employee", "task", "outcome"];
const FEATURE_TYPES = ["numeric", "categorical", "boolean", "text", "skill_list"];

const state = {
  featureSchemas: [],
  selectedProfileId: DEFAULTS.domainProfile,
  isGenerating: false,
};

function startLongTaskToast(options) {
  const detail = { options, controller: null };
  window.dispatchEvent(new CustomEvent("sandbox-long-task-start", { detail }));

  return detail.controller || {
    update() {},
    done(message = "Готово") {
      toast(options?.title || "Генерация данных", message);
    },
    error(message = "Ошибка") {
      toast(options?.title || "Генерация данных", message);
    },
  };
}

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

function csvValues(id) {
  return textValue(id)
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean);
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

function buildCustomSettingsPayload() {
  const profile = selectedProfile();
  const editableControls = document.querySelector("#customRoles");

  if (!profile || !editableControls) {
    return {};
  }

  const roles = csvValues("customRoles");
  const grades = csvValues("customGrades");
  const skills = csvValues("customSkills");
  const taskTypes = csvValues("customTaskTypes");

  return {
    team_settings: {
      roles,
      grades,
      skills,
      timezone: "Europe/Moscow",
    },
    task_settings: {
      skills,
      task_types: taskTypes,
    },
  };
}

function buildFullDatasetPayload() {
  const datasetMode = textValue("generatorDatasetMode", DEFAULTS.datasetMode);

  return {
    ...buildCommonPayload(),
    ...buildCustomSettingsPayload(),
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
    ...buildCustomSettingsPayload().team_settings,
    employees_count: numberValue("generatorEmployeesCount", DEFAULTS.employeesCount),
  };
}

function buildTasksPayload() {
  return {
    ...buildCommonPayload(),
    ...buildCustomSettingsPayload().task_settings,
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

function selectedProfile() {
  return state.featureSchemas.find(
    (schema) => schema.profile_id === state.selectedProfileId,
  );
}

function schemaFeatureGroups(schema) {
  return {
    employee: schema?.feature_groups?.employee || [],
    task: schema?.feature_groups?.task || [],
    outcome: schema?.feature_groups?.outcome || [],
  };
}

function featureDefaults(group) {
  if (group === "employee") {
    return [
      { name: "availability_score", type: "numeric", required: true, min: 0, max: 1 },
      { name: "current_workload", type: "numeric", required: true, min: 0, max: 1 },
      { name: "fatigue_score", type: "numeric", required: true, min: 0, max: 1 },
    ];
  }

  if (group === "task") {
    return [
      { name: "priority", type: "categorical", required: true, values: ["low", "medium", "high", "critical"] },
      { name: "complexity", type: "numeric", required: true, min: 1, max: 10 },
      { name: "required_skills", type: "skill_list", required: true },
    ];
  }

  return [
    { name: "quality_score", type: "numeric", required: true, min: 0, max: 1 },
    { name: "deadline_status", type: "categorical", required: true, values: ["early", "on_time", "late", "missed"] },
    { name: "outcome_label", type: "categorical", required: true, values: ["success", "good", "acceptable", "late", "failed", "rework"] },
  ];
}

function renderFeatureRows(group, features) {
  const rows = features.length ? features : featureDefaults(group);

  return rows
    .map(
      (feature, index) => `
        <div class="schema-feature-row" data-feature-group="${htmlEscape(group)}">
          <input
            class="input"
            data-feature-field="name"
            placeholder="field_name"
            type="text"
            value="${htmlEscape(feature.name || "")}"
          />
          <select class="select" data-feature-field="type">
            ${FEATURE_TYPES.map(
              (type) => `
                <option value="${htmlEscape(type)}" ${
                  type === feature.type ? "selected" : ""
                }>${htmlEscape(type)}</option>
              `,
            ).join("")}
          </select>
          <input
            class="input"
            data-feature-field="values"
            placeholder="values CSV"
            type="text"
            value="${htmlEscape((feature.values || []).join(", "))}"
          />
          <input
            class="input"
            data-feature-field="min"
            placeholder="min"
            type="number"
            step="0.01"
            value="${htmlEscape(feature.min ?? "")}"
          />
          <input
            class="input"
            data-feature-field="max"
            placeholder="max"
            type="number"
            step="0.01"
            value="${htmlEscape(feature.max ?? "")}"
          />
          <label class="checkbox-inline compact-checkbox">
            <input data-feature-field="required" type="checkbox" ${
              feature.required ? "checked" : ""
            } />
            обязательно
          </label>
          <button
            class="button button-secondary icon-button"
            data-remove-feature-row
            type="button"
            title="Удалить поле"
            ${rows.length <= 1 && index === 0 ? "disabled" : ""}
          >
            ×
          </button>
        </div>
      `,
    )
    .join("");
}

function renderCustomSchemaPanel(featureSchemas) {
  const profile = selectedProfile() || {};
  const groups = schemaFeatureGroups(profile);
  const editable = profile.system !== true;

  return `
    <details class="disclosure-card" id="customSchemaDetails" ${
      state.selectedProfileId === "custom" ? "open" : ""
    }>
      <summary>
        <span>
          <strong>Поля своей предметной области</strong>
          <small>Роли, уровни, теги, поля задач и поля результата</small>
        </span>
        <span class="badge">${editable ? "можно менять" : "системный профиль"}</span>
      </summary>

      <div class="schema-editor ${editable ? "" : "is-disabled"}">
        <div class="grid grid-2">
          <div class="form-row">
            <label for="customRoles">Роли</label>
            <input
              class="input"
              id="customRoles"
              type="text"
              value="${htmlEscape((profile.roles || []).join(", "))}"
              ${editable ? "" : "disabled"}
            />
          </div>
          <div class="form-row">
            <label for="customGrades">Уровни / грейды</label>
            <input
              class="input"
              id="customGrades"
              type="text"
              value="${htmlEscape((profile.grades || []).join(", "))}"
              ${editable ? "" : "disabled"}
            />
          </div>
          <div class="form-row">
            <label for="customSkills">Навыки / теги</label>
            <input
              class="input"
              id="customSkills"
              type="text"
              value="${htmlEscape((profile.skills || []).join(", "))}"
              ${editable ? "" : "disabled"}
            />
          </div>
          <div class="form-row">
            <label for="customTaskTypes">Типы задач</label>
            <input
              class="input"
              id="customTaskTypes"
              type="text"
              value="${htmlEscape((profile.task_types || []).join(", "))}"
              ${editable ? "" : "disabled"}
            />
          </div>
        </div>

        ${FEATURE_GROUPS.map(
          (group) => `
            <section class="schema-group" data-schema-group="${htmlEscape(group)}">
              <div class="schema-group-header">
                <h3>${htmlEscape(
                  group === "employee" ? "Поля сотрудников" : group === "task" ? "Поля задач" : "Поля результата",
                )}</h3>
                <button
                  class="button button-secondary"
                  data-add-feature-row="${htmlEscape(group)}"
                  type="button"
                  ${editable ? "" : "disabled"}
                >
                  Добавить поле
                </button>
              </div>
              <div class="schema-feature-list">
                ${renderFeatureRows(group, groups[group] || [])}
              </div>
            </section>
          `,
        ).join("")}

        <div class="toolbar">
          <button
            class="button button-secondary"
            id="saveCustomSchema"
            type="button"
            ${editable ? "" : "disabled"}
          >
            Сохранить поля
          </button>
          <button
            class="button button-secondary"
            id="resetCustomSchemaRows"
            type="button"
            ${editable ? "" : "disabled"}
          >
            Сбросить к общим полям
          </button>
        </div>
      </div>
    </details>
  `;
}

function featureRowsFromDom(group) {
  return Array.from(
    document.querySelectorAll(`[data-feature-group="${group}"]`),
  )
    .map((row) => {
      const valueFor = (field) =>
        row.querySelector(`[data-feature-field="${field}"]`)?.value?.trim() || "";
      const type = valueFor("type") || "text";
      const feature = {
        name: valueFor("name"),
        type,
        required: Boolean(
          row.querySelector('[data-feature-field="required"]')?.checked,
        ),
      };

      if (type === "categorical") {
        feature.values = valueFor("values")
          .split(",")
          .map((item) => item.trim())
          .filter(Boolean);
      }

      if (type === "numeric") {
        const min = Number.parseFloat(valueFor("min"));
        const max = Number.parseFloat(valueFor("max"));
        if (Number.isFinite(min)) {
          feature.min = min;
        }
        if (Number.isFinite(max)) {
          feature.max = max;
        }
      }

      return feature;
    })
    .filter((feature) => feature.name);
}

function buildSchemaFromControls(useDefaults = false) {
  const profile = selectedProfile();

  if (!profile) {
    throw new Error("Профиль предметной области не найден.");
  }

  const featureGroups = Object.fromEntries(
    FEATURE_GROUPS.map((group) => [
      group,
      useDefaults ? featureDefaults(group) : featureRowsFromDom(group),
    ]),
  );

  return {
    ...profile,
    roles: useDefaults ? ["specialist", "operator", "analyst", "manager", "lead"] : csvValues("customRoles"),
    grades: useDefaults ? ["junior", "middle", "senior", "lead"] : csvValues("customGrades"),
    skills: useDefaults
      ? ["domain_knowledge", "communication", "analysis", "execution", "quality_control", "planning"]
      : csvValues("customSkills"),
    task_types: useDefaults
      ? ["task", "review", "analysis", "support", "research", "delivery"]
      : csvValues("customTaskTypes"),
    feature_groups: featureGroups,
    system: false,
  };
}

async function saveSelectedSchema(useDefaults = false) {
  const profile = selectedProfile();

  if (!profile || profile.system === true) {
    return null;
  }

  const payload = buildSchemaFromControls(useDefaults);
  const response = await api.updateFeatureSchema(profile.profile_id, payload);
  const updated = response.schema || payload;
  state.featureSchemas = state.featureSchemas.map((schema) =>
    schema.profile_id === updated.profile_id ? updated : schema,
  );
  toast("Схема сохранена", updated.profile_id);
  return updated;
}

async function prepareCustomSchemaForGeneration() {
  const profile = selectedProfile();
  const controlsExist = Boolean(document.querySelector("#customRoles"));

  if (profile && profile.system !== true && controlsExist) {
    await saveSelectedSchema(false);
  }
}

function setLoading(isLoading, label = "Генерация...") {
  const buttons = document.querySelectorAll("[data-generator-action]");
  const status = document.querySelector("#generatorStatus");

  buttons.forEach((button) => {
    button.disabled = isLoading;
    button.classList.toggle("loading", isLoading);
  });

  if (!status) {
    return;
  }

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
    ? '<button class="button button-primary" id="openGeneratedDataset" type="button">Открыть в просмотре данных</button>'
    : "";

  const html = `
    <section class="grid grid-3">
      <article class="card">
        <h2>Датасет</h2>
        <p><strong>${htmlEscape(datasetId || "not returned")}</strong></p>
        <p class="muted">${htmlEscape(datasetDir || "dataset_dir not returned")}</p>
      </article>
      <article class="card">
        <h2>Генератор</h2>
        <p><strong>${htmlEscape(generatorKind)}</strong></p>
        <p class="muted">Готово, данные сохранены.</p>
      </article>
      <article class="card">
        <h2>Следующий шаг</h2>
        ${openViewerButton}
      </article>
    </section>

    <section class="grid grid-4 generator-counts" style="margin-top: 16px;">
      ${cards}
    </section>

    <article class="card next-step-card" style="margin-top: 16px;">
      <h2>Что дальше</h2>
      <p class="muted">
        Проверьте данные в просмотре, затем перейдите в обучение и запустите модели
        на этом датасете.
      </p>
      <div class="toolbar">
        <a class="button button-secondary" href="/training" data-link>Перейти к обучению</a>
        <a class="button button-secondary" href="/assignment-lab" data-link>Перейти к назначению задач</a>
      </div>
    </article>
  `;

  const resultContainer = document.querySelector("#generatorResult");
  if (!resultContainer) {
    return;
  }

  resultContainer.innerHTML = html;

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
  const resultContainer = document.querySelector("#generatorResult");

  if (!resultContainer) {
    return;
  }

  resultContainer.innerHTML = `
    <article class="card">
      <span class="badge">Ошибка</span>
      <h2>Генерация не выполнена</h2>
      <p class="muted">${htmlEscape(message)}</p>
    </article>
  `;
}

function generatorVerification(kind) {
  if (kind !== "dataset") {
    return null;
  }

  const payload = buildFullDatasetPayload();

  return {
    type: "dataset",
    datasetId: payload.dataset_id,
    datasetKind: "generated",
    expectedCounts: {
      employees: payload.employees_count,
      tasks: payload.tasks_count,
      assignment_history: payload.employees_count * payload.history_depth_per_employee,
      training_pairs: payload.target_pairs,
    },
    doneMessage: "Готово",
  };
}

async function runGenerator(kind) {
  if (state.isGenerating) {
    toast("Генерация данных", "Генерация уже выполняется.");
    return;
  }

  const actions = {
    dataset: {
      label: "Полный датасет",
      progressTitle: "Генерация данных",
      progressSteps: [
        "Сохранение схемы...",
        "Генерация сотрудников...",
        "Генерация задач...",
        "Генерация истории...",
        "Создание пар для обучения...",
        "Сохранение файлов...",
      ],
      request: () => api.generateDataset(buildFullDatasetPayload()),
    },
    team: {
      label: "Сотрудники",
      progressTitle: "Генерация сотрудников...",
      progressSteps: ["Сохранение схемы...", "Генерация сотрудников...", "Сохранение файлов..."],
      request: () => api.generateTeam(buildTeamPayload()),
    },
    tasks: {
      label: "Задачи",
      progressTitle: "Генерация задач...",
      progressSteps: ["Сохранение схемы...", "Генерация задач...", "Сохранение файлов..."],
      request: () => api.generateTasks(buildTasksPayload()),
    },
    history: {
      label: "История",
      progressTitle: "Генерация истории...",
      progressSteps: ["Сохранение схемы...", "Генерация истории...", "Сохранение файлов..."],
      request: () => api.generateHistory(buildHistoryPayload()),
    },
  };

  const action = actions[kind];
  if (!action) {
    toast("Generator", `Unknown generator: ${kind}`);
    return;
  }

  const progress = startLongTaskToast({
    title: action.progressTitle || "Генерация данных",
    message: "Подготовка...",
    steps: action.progressSteps,
    verify: generatorVerification(kind),
  });

  try {
    state.isGenerating = true;
    setLoading(true, `${action.label}...`);
    progress.update({ message: "Сохранение схемы...", percent: 12, stepIndex: 0 });
    await prepareCustomSchemaForGeneration();
    progress.update({ message: action.progressSteps?.[1] || "Генерация данных...", percent: 28, stepIndex: 1 });
    const result = await action.request();
    progress.update({ message: "Сохранение файлов...", percent: 96 });
    progress.done("Готово");
    renderResult(result, action.label);
    toast("Готово", "Готово, данные сохранены.");
  } catch (error) {
    progress.error(error.message || String(error));
    renderErrorState(error);
    toast("Ошибка генерации", error.message || String(error));
  } finally {
    state.isGenerating = false;
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

function rerenderSchemaPanel() {
  const container = document.querySelector("#generatorCustomSchemaPanel");
  if (!container) {
    return;
  }
  container.innerHTML = renderCustomSchemaPanel(state.featureSchemas);
  bindSchemaEditorEvents();
  syncAllFeatureRemoveButtons();
}

function syncFeatureRemoveButtons(group) {
  const rows = Array.from(
    document.querySelectorAll(`[data-feature-group="${group}"]`),
  );
  rows.forEach((row) => {
    const button = row.querySelector("[data-remove-feature-row]");
    if (button) {
      button.disabled = rows.length <= 1;
    }
  });
}

function syncAllFeatureRemoveButtons() {
  FEATURE_GROUPS.forEach(syncFeatureRemoveButtons);
}

function addFeatureRow(group) {
  const list = document.querySelector(
    `[data-schema-group="${group}"] .schema-feature-list`,
  );
  if (!list) {
    return;
  }

  const wrapper = document.createElement("div");
  wrapper.innerHTML = renderFeatureRows(group, [
    { name: `custom_${group}_field`, type: "text", required: false },
  ]);
  list.append(...Array.from(wrapper.children));
  bindSchemaEditorEvents();
  syncFeatureRemoveButtons(group);
}

function bindSchemaEditorEvents() {
  const profileSelect = document.querySelector("#generatorDomainProfile");
  if (profileSelect && profileSelect.dataset.bound !== "true") {
    profileSelect.dataset.bound = "true";
    profileSelect.addEventListener("change", () => {
      state.selectedProfileId = textValue("generatorDomainProfile", DEFAULTS.domainProfile);
      rerenderSchemaPanel();
    });
  }

  document.querySelectorAll("[data-add-feature-row]").forEach((button) => {
    if (button.dataset.bound === "true") {
      return;
    }
    button.dataset.bound = "true";
    button.addEventListener("click", () => addFeatureRow(button.dataset.addFeatureRow));
  });

  document.querySelectorAll("[data-remove-feature-row]").forEach((button) => {
    if (button.dataset.bound === "true") {
      return;
    }
    button.dataset.bound = "true";
    button.addEventListener("click", () => {
      const group = button.closest(".schema-feature-row")?.dataset.featureGroup;
      button.closest(".schema-feature-row")?.remove();
      if (group) {
        syncFeatureRemoveButtons(group);
      }
    });
  });

  const saveButton = document.querySelector("#saveCustomSchema");
  if (saveButton && saveButton.dataset.bound !== "true") {
    saveButton.dataset.bound = "true";
    saveButton.addEventListener("click", async () => {
      try {
        await saveSelectedSchema(false);
        rerenderSchemaPanel();
      } catch (error) {
        toast("Ошибка схемы", error.message || String(error));
      }
    });
  }

  const resetButton = document.querySelector("#resetCustomSchemaRows");
  if (resetButton && resetButton.dataset.bound !== "true") {
    resetButton.dataset.bound = "true";
    resetButton.addEventListener("click", async () => {
      try {
        await saveSelectedSchema(true);
        rerenderSchemaPanel();
      } catch (error) {
        toast("Ошибка схемы", error.message || String(error));
      }
    });
  }

  syncAllFeatureRemoveButtons();
}

function bindGeneratorEvents() {
  document.querySelectorAll("[data-generator-action]").forEach((button) => {
    if (button.dataset.bound === "true") {
      return;
    }
    button.dataset.bound = "true";
    button.addEventListener("click", () => {
      runGenerator(button.dataset.generatorAction);
    });
  });

  const datasetMode = document.querySelector("#generatorDatasetMode");
  if (datasetMode && datasetMode.dataset.bound !== "true") {
    datasetMode.dataset.bound = "true";
    datasetMode.addEventListener("change", applyModePreset);
  }
  bindSchemaEditorEvents();

  const fillLastDataset = document.querySelector("#fillLastDataset");
  if (fillLastDataset && fillLastDataset.dataset.bound !== "true") {
    fillLastDataset.dataset.bound = "true";
    fillLastDataset.addEventListener("click", () => {
      const lastDatasetId = getLastDatasetId();
      if (lastDatasetId) {
        document.querySelector("#generatorDatasetId").value = lastDatasetId;
        toast("Датасет выбран", lastDatasetId);
      } else {
        toast("Датасет не найден", "Сначала сгенерируйте датасет.");
      }
    });
  }

  const previewPayload = document.querySelector("#previewPayload");
  if (previewPayload && previewPayload.dataset.bound !== "true") {
    previewPayload.dataset.bound = "true";
    previewPayload.addEventListener("click", () => {
      const payload = buildFullDatasetPayload();

      document.querySelector("#generatorResult").innerHTML = `
        <article class="card">
          <h2>Проверка настроек</h2>
          <div class="info-list">
            <p><strong>Датасет:</strong> ${htmlEscape(payload.dataset_id)}</p>
            <p><strong>Профиль:</strong> ${htmlEscape(payload.domain_profile)}</p>
            <p><strong>Сотрудники:</strong> ${htmlEscape(payload.employees_count)}</p>
            <p><strong>Задачи:</strong> ${htmlEscape(payload.tasks_count)}</p>
            <p><strong>История на сотрудника:</strong> ${htmlEscape(payload.history_depth_per_employee)}</p>
            <p><strong>Пар для обучения:</strong> ${htmlEscape(payload.target_pairs)}</p>
          </div>
        </article>
      `;
    });
  }

  applyModePreset();
  syncAllFeatureRemoveButtons();
}

export async function renderGenerator() {
  const featureSchemas = await api.featureSchemas(false);
  const rawSchemas = featureSchemas.items || featureSchemas.profiles || featureSchemas || [];
  state.featureSchemas = Array.isArray(rawSchemas) ? rawSchemas : [];
  state.selectedProfileId = DEFAULTS.domainProfile;

  window.setTimeout(bindGeneratorEvents, 0);

  return `
    <section class="grid">
      <article class="card">
        <div class="generator-header">
          <div>
            <h2>Генерация данных</h2>
            <p class="muted">
              Создайте датасет под свой домен: людей, задачи, историю выполнений
              и пары для обучения моделей.
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
              <label for="generatorDatasetId">ID датасета</label>
              <input
                class="input"
                id="generatorDatasetId"
                type="text"
                value="${htmlEscape(getLastDatasetId() || DEFAULTS.datasetId)}"
              />
            </div>

            <div class="form-row">
              <label for="generatorDomainProfile">Профиль предметной области</label>
              <select class="select" id="generatorDomainProfile">
                ${profileOptions(featureSchemas)}
              </select>
            </div>

            <div class="form-row">
              <label for="generatorSeed">Seed для повторяемости</label>
              <input class="input" id="generatorSeed" type="number" value="${DEFAULTS.seed}" />
            </div>

            <div class="form-row">
              <label for="generatorDatasetMode">Размер датасета</label>
              <select class="select" id="generatorDatasetMode">
                <option value="small_preview">Маленький предпросмотр</option>
                <option value="medium_validation">Средний для проверки</option>
                <option value="large_training">Большой для обучения</option>
                <option value="huge_training">Очень большой</option>
              </select>
            </div>

            <div class="form-row">
              <label for="generatorEmployeesCount">Количество сотрудников</label>
              <input
                class="input"
                id="generatorEmployeesCount"
                min="1"
                type="number"
                value="${DEFAULTS.employeesCount}"
              />
            </div>

            <div class="form-row">
              <label for="generatorTasksCount">Количество задач</label>
              <input
                class="input"
                id="generatorTasksCount"
                min="1"
                type="number"
                value="${DEFAULTS.tasksCount}"
              />
            </div>

            <div class="form-row">
              <label for="generatorProjectsCount">Количество проектов</label>
              <input
                class="input"
                id="generatorProjectsCount"
                min="1"
                type="number"
                value="${DEFAULTS.projectsCount}"
              />
            </div>

            <div class="form-row">
              <label for="generatorHistoryDepth">История на сотрудника</label>
              <input
                class="input"
                id="generatorHistoryDepth"
                min="1"
                type="number"
                value="${DEFAULTS.historyDepthPerEmployee}"
              />
            </div>

            <div class="form-row">
              <label for="generatorTargetPairs">Пар для обучения</label>
              <input
                class="input"
                id="generatorTargetPairs"
                min="1"
                type="number"
                value="${DEFAULTS.targetPairs}"
              />
            </div>

            <div class="form-row">
              <label for="generatorCandidatesPerTask">Кандидатов на задачу</label>
              <input
                class="input"
                id="generatorCandidatesPerTask"
                min="1"
                type="number"
                value="${DEFAULTS.candidatesPerTask}"
              />
            </div>

            <div class="form-row">
              <label for="generatorTargetMode">Цель оптимизации</label>
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
                заменить существующий датасет
              </label>
            </div>
          </div>

          <div class="card nested-card" id="hugeGenerationPanel" hidden>
            <h3>Подтверждение большого запуска</h3>
            <p class="muted">
              Очень большой датасет может занять заметное время и место на диске.
            </p>
            <label class="checkbox-inline">
              <input id="generatorConfirmHuge" type="checkbox" />
              я понимаю размер запуска
            </label>
          </div>

          <div id="generatorCustomSchemaPanel">
            ${renderCustomSchemaPanel(featureSchemas)}
          </div>

          <div class="toolbar">
            <button
              class="button button-primary"
              data-generator-action="dataset"
              type="button"
            >
              Создать полный датасет
            </button>
            <button
              class="button button-secondary"
              data-generator-action="team"
              type="button"
            >
              Только сотрудники
            </button>
            <button
              class="button button-secondary"
              data-generator-action="tasks"
              type="button"
            >
              Только задачи
            </button>
            <button
              class="button button-secondary"
              data-generator-action="history"
              type="button"
            >
              Только история
            </button>
            <button class="button button-secondary" id="previewPayload" type="button">
              Проверить настройки
            </button>
            <button class="button button-secondary" id="fillLastDataset" type="button">
              Последний датасет
            </button>
          </div>
        </form>
      </article>

    </section>

    <section id="generatorResult" style="margin-top: 16px;">
      <article class="card">
        <h2>Результат</h2>
        <p class="muted">
          После генерации здесь появятся счетчики и быстрые кнопки следующих шагов.
        </p>
      </article>
    </section>
  `;
}
