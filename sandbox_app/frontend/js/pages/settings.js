import { api } from "../api.js";

const FEATURE_TYPES = ["numeric", "categorical", "boolean", "text", "skill_list"];
const FEATURE_GROUPS = ["employee", "task", "outcome"];
const FEATURE_TYPE_LABELS = {
  numeric: "Число",
  categorical: "Категория",
  boolean: "Да / нет",
  text: "Текст",
  skill_list: "Список тегов",
};
const FEATURE_GROUP_LABELS = {
  employee: "Сотрудник",
  task: "Задача",
  outcome: "Результат",
};

const state = {
  settings: null,
  settingsSchema: null,
  featureSchemas: [],
  selectedProfileId: "",
  selectedFeatureGroup: "employee",
  schemaPreview: null,
  error: "",
};

function htmlEscape(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function toast(title, message = "") {
  window.dispatchEvent(
    new CustomEvent("sandbox-toast", {
      detail: {
        title,
        message,
      },
    }),
  );
}

function selectedValue(id) {
  const element = document.querySelector(`#${id}`);
  return element ? element.value : "";
}

function checkedValue(id) {
  const element = document.querySelector(`#${id}`);
  return Boolean(element?.checked);
}

function numberValue(id, fallback) {
  const value = Number(selectedValue(id));
  return Number.isFinite(value) ? value : fallback;
}

function csvValues(id) {
  return selectedValue(id)
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean);
}

function option(value, label, selected) {
  return `
    <option value="${htmlEscape(value)}" ${value === selected ? "selected" : ""}>
      ${htmlEscape(label)}
    </option>
  `;
}

function typeLabel(type) {
  return FEATURE_TYPE_LABELS[type] || type;
}

function groupLabel(group) {
  return FEATURE_GROUP_LABELS[group] || group;
}

function settingsValue(section, key, fallback = "") {
  return state.settings?.[section]?.[key] ?? fallback;
}

function selectedProfile() {
  return state.featureSchemas.find(
    (schema) => schema.profile_id === state.selectedProfileId,
  );
}

function schemaFeatureGroups(schema) {
  return {
    employee:
      schema?.feature_groups?.employee ||
      schema?.employee_features ||
      schema?.features?.employee ||
      [],
    task:
      schema?.feature_groups?.task ||
      schema?.task_features ||
      schema?.features?.task ||
      [],
    outcome:
      schema?.feature_groups?.outcome ||
      schema?.outcome_features ||
      schema?.features?.outcome ||
      [],
  };
}

function renderStatus() {
  if (!state.error) {
    return "";
  }

  return `
    <section class="panel error-panel">
      <h3>Предупреждение</h3>
      <p>${htmlEscape(state.error)}</p>
    </section>
  `;
}

function renderAppSettingsPanel() {
  const defaults = state.settings?.defaults || {};
  const limits = state.settings?.limits || {};
  const ollama = state.settings?.ollama || {};
  const schema = state.settingsSchema || {};

  return `
    <section class="panel">
      <div class="section-heading">
        <div>
          <h3>Основные настройки</h3>
          <p class="muted">Значения по умолчанию, лимиты генерации и параметры Qwen/Ollama.</p>
        </div>
        <button id="resetSettings" class="button-secondary" type="button">
          Сбросить
        </button>
      </div>

      <div class="form-grid">
        <label>
          Seed по умолчанию
          <input id="defaultSeed" type="number" value="${htmlEscape(defaults.seed)}">
        </label>

        <label>
          Профиль по умолчанию
          <input
            id="defaultDomainProfile"
            type="text"
            value="${htmlEscape(defaults.domain_profile)}"
          >
        </label>

        <label>
          Размер датасета по умолчанию
          <select id="defaultDatasetMode">
            ${(schema.dataset_modes || [])
              .map((item) => option(item, item, defaults.dataset_mode))
              .join("")}
          </select>
        </label>

        <label>
          Цель модели по умолчанию
          <select id="defaultTargetMode">
            ${(schema.target_modes || [])
              .map((item) => option(item, item, defaults.target_mode))
              .join("")}
          </select>
        </label>

        <label>
          Режим рекомендации по умолчанию
          <select id="defaultRecommendationMode">
            ${(schema.recommendation_modes || [])
              .map((item) => option(item, item, defaults.recommendation_mode))
              .join("")}
          </select>
        </label>

        <label>
          Режим распределения по умолчанию
          <select id="defaultAssignmentMode">
            ${(schema.recommendation_modes || [])
              .map((item) => option(item, item, defaults.assignment_mode))
              .join("")}
          </select>
        </label>

        <label>
          Модели для обучения
          <input
            id="defaultTrainingModels"
            type="text"
            value="${htmlEscape((defaults.training_models || []).join(", "))}"
          >
        </label>

        <label>
          Лимит сотрудников для huge
          <input
            id="hugeMaxEmployees"
            type="number"
            value="${htmlEscape(limits.huge_max_employees)}"
          >
        </label>

        <label>
          Лимит задач для huge
          <input
            id="hugeMaxTasks"
            type="number"
            value="${htmlEscape(limits.huge_max_tasks)}"
          >
        </label>

        <label>
          Лимит обучающих пар для huge
          <input
            id="hugeMaxPairs"
            type="number"
            value="${htmlEscape(limits.huge_max_pairs)}"
          >
        </label>

        <label>
          Адрес Ollama
          <input
            id="ollamaBaseUrl"
            type="text"
            value="${htmlEscape(ollama.base_url)}"
          >
        </label>

        <label>
          Модель Qwen/Ollama
          <input id="ollamaModel" type="text" value="${htmlEscape(ollama.model)}">
        </label>

        <label>
          Таймаут LLM, секунды
          <input
            id="ollamaTimeout"
            type="number"
            value="${htmlEscape(ollama.timeout_seconds)}"
          >
        </label>

        <label class="checkbox-label">
          <input
            id="ollamaAutoPull"
            type="checkbox"
            ${ollama.auto_pull ? "checked" : ""}
          >
          <span>Автоматически скачивать модель Ollama</span>
        </label>
      </div>

      <div class="actions-row">
        <button id="saveAppSettings" type="button">Сохранить настройки</button>
      </div>
    </section>
  `;
}

function renderPathsPanel() {
  const paths = state.settings?.paths || {};

  return `
    <details class="disclosure-card">
      <summary>
        <span>
          <strong>Пути хранения</strong>
          <small>Папки внутри sandbox_app для данных, моделей и отчетов</small>
        </span>
        <span class="badge">дополнительно</span>
      </summary>

      <div class="form-grid">
        ${Object.entries(paths)
          .map(
            ([key, value]) => `
              <label>
                ${htmlEscape(key)}
                <input
                  data-path-key="${htmlEscape(key)}"
                  type="text"
                  value="${htmlEscape(value)}"
                >
              </label>
            `,
          )
          .join("")}
      </div>

      <div class="actions-row">
        <button id="savePathSettings" type="button">Сохранить пути</button>
      </div>
    </details>
  `;
}

function renderSchemaSelectorPanel() {
  return `
    <section class="panel">
      <div class="section-heading">
        <div>
          <h3>Схемы данных</h3>
          <p class="muted">Настройте роли, уровни, теги и собственные поля без ручного редактирования файлов.</p>
        </div>
        <button id="refreshSchemas" class="button-secondary" type="button">
          Обновить схемы
        </button>
      </div>

      <div class="form-grid">
        <label>
          Профиль
          <select id="schemaProfileId">
            ${state.featureSchemas
              .map((schema) =>
                option(
                  schema.profile_id,
                  `${schema.profile_id}${schema.system ? " · системный" : " · пользовательский"}`,
                  state.selectedProfileId,
                ),
              )
              .join("")}
          </select>
        </label>

        <label>
          Группа полей
          <select id="schemaFeatureGroup">
            ${FEATURE_GROUPS.map((group) =>
              option(group, groupLabel(group), state.selectedFeatureGroup),
            ).join("")}
          </select>
        </label>
      </div>

      <div class="actions-row">
        <button id="loadSchemaPreview" class="button-secondary" type="button">
          Показать сводку
        </button>
      </div>
    </section>
  `;
}

function renderCreateSchemaPanel() {
  return `
    <section class="panel">
      <h3>Создать профиль предметной области</h3>

      <div class="form-grid">
        <label>
          ID профиля
          <input id="newProfileId" type="text" value="custom_domain">
        </label>

        <label>
          Название
          <input id="newProfileName" type="text" value="Своя область">
        </label>

        <label>
          Описание
          <input
            id="newProfileDescription"
            type="text"
            value="Редактируемый профиль для своей предметной области"
          >
        </label>
      </div>

      <div class="actions-row">
        <button id="createSchemaProfile" type="button">Создать схему</button>
      </div>
    </section>
  `;
}

function renderSchemaMetaPanel() {
  const schema = selectedProfile();

  if (!schema) {
    return `
      <section class="panel">
        <h3>Параметры схемы</h3>
        <p class="muted">Схема не выбрана.</p>
      </section>
    `;
  }

  return `
    <section class="panel">
      <h3>Параметры схемы</h3>

      <div class="form-grid">
        <label>
          Роли
          <input
            id="schemaRoles"
            type="text"
            value="${htmlEscape((schema.roles || []).join(", "))}"
          >
        </label>

        <label>
          Уровни
          <input
            id="schemaGrades"
            type="text"
            value="${htmlEscape((schema.grades || []).join(", "))}"
          >
        </label>

        <label>
          Теги / навыки
          <input
            id="schemaSkills"
            type="text"
            value="${htmlEscape((schema.skills || []).join(", "))}"
          >
        </label>
      </div>

      <div class="actions-row">
        <button id="saveSchemaMeta" type="button">Сохранить схему</button>
        ${
          schema.system
            ? ""
            : `
              <button id="deleteSchemaProfile" class="button-danger" type="button">
                Удалить схему
              </button>
            `
        }
      </div>
    </section>
  `;
}

function renderFeatureListPanel() {
  const schema = selectedProfile();
  const features = schemaFeatureGroups(schema)[state.selectedFeatureGroup] || [];

  return `
    <section class="panel">
      <h3>Поля: ${htmlEscape(groupLabel(state.selectedFeatureGroup))}</h3>

      ${
        features.length
          ? `
            <div class="list-grid">
              ${features
                .map(
                  (feature) => `
                    <article class="list-card">
                      <strong>${htmlEscape(feature.name)}</strong>
                      <span>
                        ${htmlEscape(typeLabel(feature.type))}
                        ${feature.required ? " · обязательно" : ""}
                      </span>
                      <span>${htmlEscape(feature.description || "")}</span>
                      <button
                        data-delete-feature="${htmlEscape(feature.name)}"
                        class="button-secondary"
                        type="button"
                      >
                        Удалить
                      </button>
                    </article>
                  `,
                )
                .join("")}
            </div>
          `
          : '<p class="muted">Поля пока не добавлены.</p>'
      }
    </section>
  `;
}

function renderAddFeaturePanel() {
  return `
    <section class="panel">
      <h3>Добавить поле</h3>

      <div class="form-grid">
        <label>
          Название поля
          <input id="newFeatureName" type="text" value="custom_score">
        </label>

        <label>
          Тип поля
          <select id="newFeatureType">
            ${FEATURE_TYPES.map((type) => option(type, typeLabel(type), "numeric")).join("")}
          </select>
        </label>

        <label>
          Описание
          <input id="newFeatureDescription" type="text" value="Пользовательское поле">
        </label>

        <label class="checkbox-label">
          <input id="newFeatureRequired" type="checkbox">
          <span>Обязательное поле</span>
        </label>
      </div>

      <div class="actions-row">
        <button id="addSchemaFeature" type="button">Добавить поле</button>
      </div>
    </section>
  `;
}

function renderSchemaPreviewPanel() {
  const schema = state.schemaPreview || selectedProfile();
  const groups = schemaFeatureGroups(schema);

  return `
    <details class="disclosure-card">
      <summary>
        <span>
          <strong>Сводка схемы</strong>
          <small>Количество словарей и пользовательских полей</small>
        </span>
        <span class="badge">сводка</span>
      </summary>
      <div class="info-list">
        <p><strong>Профиль:</strong> ${htmlEscape(schema?.profile_id || "не выбран")}</p>
        <p><strong>Роли:</strong> ${htmlEscape((schema?.roles || []).length)}</p>
        <p><strong>Уровни:</strong> ${htmlEscape((schema?.grades || []).length)}</p>
        <p><strong>Теги:</strong> ${htmlEscape((schema?.skills || []).length)}</p>
        <p><strong>Поля сотрудников:</strong> ${htmlEscape((groups.employee || []).length)}</p>
        <p><strong>Поля задач:</strong> ${htmlEscape((groups.task || []).length)}</p>
        <p><strong>Поля результата:</strong> ${htmlEscape((groups.outcome || []).length)}</p>
      </div>
    </details>
  `;
}

function render() {
  return `
    <div class="page-stack">
      <section class="hero-panel">
        <div>
          <p class="eyebrow">Настройки</p>
          <h1>Настройки и схемы данных</h1>
          <p>
            Управляйте профилями предметной области, лимитами генерации,
            моделями по умолчанию и подключением LLM в одном месте.
          </p>
        </div>
      </section>

      ${renderStatus()}
      ${renderAppSettingsPanel()}
      ${renderPathsPanel()}
      ${renderSchemaSelectorPanel()}
      ${renderCreateSchemaPanel()}
      ${renderSchemaMetaPanel()}
      ${renderFeatureListPanel()}
      ${renderAddFeaturePanel()}
      ${renderSchemaPreviewPanel()}
    </div>
  `;
}

async function refreshData() {
  state.error = "";

  const [settingsPayload, settingsSchema, featureSchemas] = await Promise.all([
    api.sandboxSettings(),
    api.sandboxSettingsSchema(),
    api.featureSchemas(false),
  ]);

  state.settings = settingsPayload.settings || {};
  state.settingsSchema = settingsSchema || {};
  state.featureSchemas = Array.isArray(featureSchemas)
    ? featureSchemas
    : featureSchemas.schemas || featureSchemas.profiles || [];

  if (!state.selectedProfileId && state.featureSchemas.length) {
    const custom = state.featureSchemas.find((schema) => !schema.system);
    state.selectedProfileId = (custom || state.featureSchemas[0]).profile_id;
  }
}

async function saveAppSettings() {
  const values = {
    defaults: {
      seed: numberValue("defaultSeed", 27027),
      domain_profile: selectedValue("defaultDomainProfile"),
      dataset_mode: selectedValue("defaultDatasetMode"),
      target_mode: selectedValue("defaultTargetMode"),
      recommendation_mode: selectedValue("defaultRecommendationMode"),
      assignment_mode: selectedValue("defaultAssignmentMode"),
      training_models: csvValues("defaultTrainingModels"),
    },
    limits: {
      huge_max_employees: numberValue("hugeMaxEmployees", 1000),
      huge_max_tasks: numberValue("hugeMaxTasks", 100000),
      huge_max_pairs: numberValue("hugeMaxPairs", 10000000),
    },
    ollama: {
      base_url: selectedValue("ollamaBaseUrl"),
      model: selectedValue("ollamaModel"),
      timeout_seconds: numberValue("ollamaTimeout", 30),
      auto_pull: checkedValue("ollamaAutoPull"),
    },
  };

  const merged = {
    ...state.settings,
    defaults: {
      ...state.settings.defaults,
      ...values.defaults,
    },
    limits: {
      ...state.settings.limits,
      ...values.limits,
    },
    ollama: {
      ...state.settings.ollama,
      ...values.ollama,
    },
  };

  const response = await api.updateSandboxSettings({ settings: merged });
  state.settings = response.settings;
  toast("Настройки", "Основные настройки сохранены");
}

async function savePathSettings() {
  const paths = {};

  document.querySelectorAll("[data-path-key]").forEach((input) => {
    paths[input.dataset.pathKey] = input.value;
  });

  const response = await api.patchSandboxSettings({
    section: "paths",
    values: paths,
  });
  state.settings = response.settings;
  toast("Настройки", "Пути сохранены");
}

async function resetSettings() {
  const response = await api.resetSandboxSettings();
  state.settings = response.settings;
  toast("Настройки", "Настройки сброшены");
}

async function createSchemaProfile() {
  const template = await api.featureSchemaTemplate();
  const baseSchema = template.template || template.schema || {};
  const payload = {
    ...baseSchema,
    profile_id: selectedValue("newProfileId"),
    name: selectedValue("newProfileName"),
    description: selectedValue("newProfileDescription"),
    system: false,
  };

  await api.createFeatureSchema(payload);
  state.selectedProfileId = payload.profile_id;
  await refreshData();
  toast("Настройки", "Схема создана");
}

async function saveSchemaMeta() {
  const schema = selectedProfile();

  if (!schema) {
    throw new Error("Схема не выбрана");
  }

  const payload = {
    ...schema,
    roles: csvValues("schemaRoles"),
    grades: csvValues("schemaGrades"),
    skills: csvValues("schemaSkills"),
  };

  await api.updateFeatureSchema(schema.profile_id, payload);
  await refreshData();
  toast("Настройки", "Схема сохранена");
}

async function deleteSchemaProfile() {
  const schema = selectedProfile();

  if (!schema) {
    throw new Error("Схема не выбрана");
  }

  await api.deleteFeatureSchema(schema.profile_id);
  state.selectedProfileId = "";
  await refreshData();
  toast("Настройки", "Схема удалена");
}

async function addSchemaFeature() {
  const profileId = state.selectedProfileId;

  if (!profileId) {
    throw new Error("Схема не выбрана");
  }

  await api.addSchemaFeature(profileId, state.selectedFeatureGroup, {
    name: selectedValue("newFeatureName"),
    type: selectedValue("newFeatureType"),
    description: selectedValue("newFeatureDescription"),
    required: checkedValue("newFeatureRequired"),
  });
  await refreshData();
  toast("Настройки", "Поле добавлено");
}

async function deleteSchemaFeature(featureName) {
  await api.deleteSchemaFeature(
    state.selectedProfileId,
    state.selectedFeatureGroup,
    featureName,
  );
  await refreshData();
  toast("Настройки", "Поле удалено");
}

async function loadSchemaPreview() {
  state.schemaPreview = await api.featureSchema(state.selectedProfileId, true);
  toast("Настройки", "Сводка схемы обновлена");
}

async function runAction(action) {
  try {
    await action();
    repaint();
  } catch (error) {
    state.error = error.message || String(error);
    toast("Ошибка настроек", state.error);
    repaint();
  }
}

function bindEvents() {
  document.querySelector("#saveAppSettings")?.addEventListener("click", () => {
    runAction(saveAppSettings);
  });

  document.querySelector("#savePathSettings")?.addEventListener("click", () => {
    runAction(savePathSettings);
  });

  document.querySelector("#resetSettings")?.addEventListener("click", () => {
    runAction(resetSettings);
  });

  document.querySelector("#refreshSchemas")?.addEventListener("click", () => {
    runAction(refreshData);
  });

  document.querySelector("#createSchemaProfile")?.addEventListener("click", () => {
    runAction(createSchemaProfile);
  });

  document.querySelector("#saveSchemaMeta")?.addEventListener("click", () => {
    runAction(saveSchemaMeta);
  });

  document.querySelector("#deleteSchemaProfile")?.addEventListener("click", () => {
    runAction(deleteSchemaProfile);
  });

  document.querySelector("#addSchemaFeature")?.addEventListener("click", () => {
    runAction(addSchemaFeature);
  });

  document.querySelector("#loadSchemaPreview")?.addEventListener("click", () => {
    runAction(loadSchemaPreview);
  });

  document.querySelector("#schemaProfileId")?.addEventListener("change", () => {
    state.selectedProfileId = selectedValue("schemaProfileId");
    state.schemaPreview = null;
    repaint();
  });

  document.querySelector("#schemaFeatureGroup")?.addEventListener("change", () => {
    state.selectedFeatureGroup = selectedValue("schemaFeatureGroup");
    repaint();
  });

  document.querySelectorAll("[data-delete-feature]").forEach((button) => {
    button.addEventListener("click", () => {
      runAction(async () => {
        await deleteSchemaFeature(button.dataset.deleteFeature || "");
      });
    });
  });
}

function repaint() {
  const root = document.querySelector("#appRoot");

  if (!root) {
    return;
  }

  root.innerHTML = render();
  bindEvents();
}

export async function renderSettings() {
  await refreshData();
  window.setTimeout(bindEvents, 0);
  return render();
}

export async function renderPage() {
  return renderSettings();
}

export default renderSettings;
