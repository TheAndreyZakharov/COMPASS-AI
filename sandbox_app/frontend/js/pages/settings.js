import { api } from "../api.js";

const FEATURE_TYPES = ["numeric", "categorical", "boolean", "text", "skill_list"];
const FEATURE_GROUPS = ["employee", "task", "outcome"];

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

function prettyJson(value) {
  return htmlEscape(JSON.stringify(value ?? {}, null, 2));
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
    employee: schema?.employee_features || schema?.features?.employee || [],
    task: schema?.task_features || schema?.features?.task || [],
    outcome: schema?.outcome_features || schema?.features?.outcome || [],
  };
}

function renderStatus() {
  if (!state.error) {
    return "";
  }

  return `
    <section class="panel error-panel">
      <h3>Settings warning</h3>
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
          <h3>App settings</h3>
          <p class="muted">Базовые defaults, limits и Qwen/Ollama settings.</p>
        </div>
        <button id="resetSettings" class="button-secondary" type="button">
          Reset settings
        </button>
      </div>

      <div class="form-grid">
        <label>
          Default seed
          <input id="defaultSeed" type="number" value="${htmlEscape(defaults.seed)}">
        </label>

        <label>
          Default domain profile
          <input
            id="defaultDomainProfile"
            type="text"
            value="${htmlEscape(defaults.domain_profile)}"
          >
        </label>

        <label>
          Default dataset mode
          <select id="defaultDatasetMode">
            ${(schema.dataset_modes || [])
              .map((item) => option(item, item, defaults.dataset_mode))
              .join("")}
          </select>
        </label>

        <label>
          Default target mode
          <select id="defaultTargetMode">
            ${(schema.target_modes || [])
              .map((item) => option(item, item, defaults.target_mode))
              .join("")}
          </select>
        </label>

        <label>
          Default recommendation mode
          <select id="defaultRecommendationMode">
            ${(schema.recommendation_modes || [])
              .map((item) => option(item, item, defaults.recommendation_mode))
              .join("")}
          </select>
        </label>

        <label>
          Default assignment mode
          <select id="defaultAssignmentMode">
            ${(schema.recommendation_modes || [])
              .map((item) => option(item, item, defaults.assignment_mode))
              .join("")}
          </select>
        </label>

        <label>
          Training models CSV
          <input
            id="defaultTrainingModels"
            type="text"
            value="${htmlEscape((defaults.training_models || []).join(", "))}"
          >
        </label>

        <label>
          Huge max employees
          <input
            id="hugeMaxEmployees"
            type="number"
            value="${htmlEscape(limits.huge_max_employees)}"
          >
        </label>

        <label>
          Huge max tasks
          <input
            id="hugeMaxTasks"
            type="number"
            value="${htmlEscape(limits.huge_max_tasks)}"
          >
        </label>

        <label>
          Huge max pairs
          <input
            id="hugeMaxPairs"
            type="number"
            value="${htmlEscape(limits.huge_max_pairs)}"
          >
        </label>

        <label>
          Ollama base URL
          <input
            id="ollamaBaseUrl"
            type="text"
            value="${htmlEscape(ollama.base_url)}"
          >
        </label>

        <label>
          Qwen model name
          <input id="ollamaModel" type="text" value="${htmlEscape(ollama.model)}">
        </label>

        <label>
          LLM timeout seconds
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
          <span>Auto pull Ollama model</span>
        </label>
      </div>

      <div class="actions-row">
        <button id="saveAppSettings" type="button">Save app settings</button>
      </div>
    </section>
  `;
}

function renderPathsPanel() {
  const paths = state.settings?.paths || {};

  return `
    <section class="panel">
      <h3>Paths</h3>
      <p class="muted">Все paths должны оставаться внутри sandbox_app.</p>

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
        <button id="savePathSettings" type="button">Save paths</button>
      </div>
    </section>
  `;
}

function renderSchemaSelectorPanel() {
  return `
    <section class="panel">
      <div class="section-heading">
        <div>
          <h3>Feature schemas</h3>
          <p class="muted">Schema editor для roles, grades, skills и features.</p>
        </div>
        <button id="refreshSchemas" class="button-secondary" type="button">
          Refresh schemas
        </button>
      </div>

      <div class="form-grid">
        <label>
          Profile
          <select id="schemaProfileId">
            ${state.featureSchemas
              .map((schema) =>
                option(
                  schema.profile_id,
                  `${schema.profile_id}${schema.system ? " · system" : ""}`,
                  state.selectedProfileId,
                ),
              )
              .join("")}
          </select>
        </label>

        <label>
          Feature group
          <select id="schemaFeatureGroup">
            ${FEATURE_GROUPS.map((group) =>
              option(group, group, state.selectedFeatureGroup),
            ).join("")}
          </select>
        </label>
      </div>

      <div class="actions-row">
        <button id="loadSchemaPreview" class="button-secondary" type="button">
          Load preview
        </button>
      </div>
    </section>
  `;
}

function renderCreateSchemaPanel() {
  return `
    <section class="panel">
      <h3>Create domain profile</h3>

      <div class="form-grid">
        <label>
          Profile id
          <input id="newProfileId" type="text" value="custom_domain">
        </label>

        <label>
          Name
          <input id="newProfileName" type="text" value="Custom Domain">
        </label>

        <label>
          Description
          <input
            id="newProfileDescription"
            type="text"
            value="Custom editable sandbox domain profile"
          >
        </label>
      </div>

      <div class="actions-row">
        <button id="createSchemaProfile" type="button">Create schema</button>
      </div>
    </section>
  `;
}

function renderSchemaMetaPanel() {
  const schema = selectedProfile();

  if (!schema) {
    return `
      <section class="panel">
        <h3>Schema metadata</h3>
        <p class="muted">Schema не выбрана.</p>
      </section>
    `;
  }

  return `
    <section class="panel">
      <h3>Schema metadata</h3>

      <div class="form-grid">
        <label>
          Roles CSV
          <input
            id="schemaRoles"
            type="text"
            value="${htmlEscape((schema.roles || []).join(", "))}"
          >
        </label>

        <label>
          Grades CSV
          <input
            id="schemaGrades"
            type="text"
            value="${htmlEscape((schema.grades || []).join(", "))}"
          >
        </label>

        <label>
          Skills CSV
          <input
            id="schemaSkills"
            type="text"
            value="${htmlEscape((schema.skills || []).join(", "))}"
          >
        </label>
      </div>

      <div class="actions-row">
        <button id="saveSchemaMeta" type="button">Save schema metadata</button>
        ${
          schema.system
            ? ""
            : `
              <button id="deleteSchemaProfile" class="button-danger" type="button">
                Delete schema
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
      <h3>${htmlEscape(state.selectedFeatureGroup)} features</h3>

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
                        ${htmlEscape(feature.type)}
                        ${feature.required ? " · required" : ""}
                      </span>
                      <span>${htmlEscape(feature.description || "")}</span>
                      <button
                        data-delete-feature="${htmlEscape(feature.name)}"
                        class="button-secondary"
                        type="button"
                      >
                        Delete
                      </button>
                    </article>
                  `,
                )
                .join("")}
            </div>
          `
          : '<p class="muted">Features пока нет.</p>'
      }
    </section>
  `;
}

function renderAddFeaturePanel() {
  return `
    <section class="panel">
      <h3>Add feature</h3>

      <div class="form-grid">
        <label>
          Feature name
          <input id="newFeatureName" type="text" value="custom_score">
        </label>

        <label>
          Feature type
          <select id="newFeatureType">
            ${FEATURE_TYPES.map((type) => option(type, type, "numeric")).join("")}
          </select>
        </label>

        <label>
          Description
          <input id="newFeatureDescription" type="text" value="Custom feature">
        </label>

        <label class="checkbox-label">
          <input id="newFeatureRequired" type="checkbox">
          <span>Required</span>
        </label>
      </div>

      <div class="actions-row">
        <button id="addSchemaFeature" type="button">Add feature</button>
      </div>
    </section>
  `;
}

function renderSchemaPreviewPanel() {
  return `
    <section class="panel">
      <h3>Schema preview</h3>
      <pre>${prettyJson(state.schemaPreview || selectedProfile() || {})}</pre>
    </section>
  `;
}

function renderRawSettingsPanel() {
  return `
    <section class="panel">
      <h3>Raw settings JSON</h3>
      <pre>${prettyJson(state.settings)}</pre>
    </section>
  `;
}

function render() {
  return `
    <div class="page-stack">
      <section class="hero-panel">
        <div>
          <p class="eyebrow">Settings</p>
          <h1>Settings and schema editor</h1>
          <p>
            Управление app settings, defaults, paths, Ollama/Qwen параметрами и
            custom feature schemas без ручной правки JSON.
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
      ${renderRawSettingsPanel()}
    </div>
  `;
}

async function refreshData() {
  state.error = "";

  const [settingsPayload, settingsSchema, featureSchemas] = await Promise.all([
    api.sandboxSettings(),
    api.sandboxSettingsSchema(),
    api.featureSchemas(),
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
  toast("Settings", "App settings saved");
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
  toast("Settings", "Paths saved");
}

async function resetSettings() {
  const response = await api.resetSandboxSettings();
  state.settings = response.settings;
  toast("Settings", "Settings reset");
}

async function createSchemaProfile() {
  const template = await api.featureSchemaTemplate();
  const payload = {
    ...template,
    profile_id: selectedValue("newProfileId"),
    name: selectedValue("newProfileName"),
    description: selectedValue("newProfileDescription"),
    system: false,
  };

  await api.createFeatureSchema(payload);
  state.selectedProfileId = payload.profile_id;
  await refreshData();
  toast("Settings", "Schema created");
}

async function saveSchemaMeta() {
  const schema = selectedProfile();

  if (!schema) {
    throw new Error("Schema не выбрана");
  }

  const payload = {
    ...schema,
    roles: csvValues("schemaRoles"),
    grades: csvValues("schemaGrades"),
    skills: csvValues("schemaSkills"),
  };

  await api.updateFeatureSchema(schema.profile_id, payload);
  await refreshData();
  toast("Settings", "Schema metadata saved");
}

async function deleteSchemaProfile() {
  const schema = selectedProfile();

  if (!schema) {
    throw new Error("Schema не выбрана");
  }

  await api.deleteFeatureSchema(schema.profile_id);
  state.selectedProfileId = "";
  await refreshData();
  toast("Settings", "Schema deleted");
}

async function addSchemaFeature() {
  const profileId = state.selectedProfileId;

  if (!profileId) {
    throw new Error("Schema не выбрана");
  }

  await api.addSchemaFeature(profileId, state.selectedFeatureGroup, {
    name: selectedValue("newFeatureName"),
    type: selectedValue("newFeatureType"),
    description: selectedValue("newFeatureDescription"),
    required: checkedValue("newFeatureRequired"),
  });
  await refreshData();
  toast("Settings", "Feature added");
}

async function deleteSchemaFeature(featureName) {
  await api.deleteSchemaFeature(
    state.selectedProfileId,
    state.selectedFeatureGroup,
    featureName,
  );
  await refreshData();
  toast("Settings", "Feature deleted");
}

async function loadSchemaPreview() {
  state.schemaPreview = await api.featureSchema(state.selectedProfileId, true);
  toast("Settings", "Schema preview loaded");
}

async function runAction(action) {
  try {
    await action();
    repaint();
  } catch (error) {
    state.error = error.message || String(error);
    toast("Settings error", state.error);
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