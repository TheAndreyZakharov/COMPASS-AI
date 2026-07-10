import { api } from "../api.js";
import { htmlEscape, toast } from "../app.js";
import { renderSummaryCards } from "../components/charts.js";
import { renderDataTable } from "../components/table.js";

const state = {
  sessions: null,
  models: null,
  selectedSessionId: "",
  selectedModelName: "",
  exportOnnx: false,
  sampleSize: 100,
};

function sessionOptions(payload) {
  const sessions = payload?.sessions || [];

  if (sessions.length === 0) {
    return '<option value="">Нет сессий обучения</option>';
  }

  return sessions
    .map((session) => {
      const selected = session.session_id === state.selectedSessionId ? "selected" : "";

      return `
        <option value="${htmlEscape(session.session_id)}" ${selected}>
          ${htmlEscape(session.session_id)} · ${htmlEscape(session.status || "")}
        </option>
      `;
    })
    .join("");
}

function modelOptions() {
  const models = filteredModels();

  if (models.length === 0) {
    return '<option value="">Нет моделей</option>';
  }

  return models
    .map((model) => {
      const selected = model.model_name === state.selectedModelName ? "selected" : "";

      return `
        <option value="${htmlEscape(model.model_name)}" ${selected}>
          ${htmlEscape(model.model_name)} · ${htmlEscape(model.artifact_format || "")}
        </option>
      `;
    })
    .join("");
}

function filteredModels() {
  return (state.models?.models || []).filter(
    (model) => model.session_id === state.selectedSessionId,
  );
}

function selectedSession() {
  return (state.sessions?.sessions || []).find(
    (session) => session.session_id === state.selectedSessionId,
  );
}

function selectedModel() {
  return filteredModels().find((model) => model.model_name === state.selectedModelName);
}

function readControls() {
  state.selectedSessionId = document.querySelector("#modelsSession").value;
  state.selectedModelName = document.querySelector("#modelsModel").value;
  state.exportOnnx = document.querySelector("#modelsExportOnnx").checked;
  state.sampleSize = Number.parseInt(
    document.querySelector("#modelsSampleSize").value,
    10,
  ) || 100;
}

function syncModelSelect() {
  const select = document.querySelector("#modelsModel");
  select.innerHTML = modelOptions();

  if (!state.selectedModelName) {
    state.selectedModelName = filteredModels()[0]?.model_name || "";
    select.value = state.selectedModelName;
  }
}

function setModelsLoading(isLoading, label = "Загрузка...") {
  const status = document.querySelector("#modelsStatus");
  const buttons = document.querySelectorAll("[data-models-action]");

  buttons.forEach((button) => {
    button.disabled = isLoading;
    button.classList.toggle("loading", isLoading);
  });

  status.className = isLoading ? "status-pill status-pending" : "status-pill status-ok";
  status.innerHTML = isLoading
    ? `<span class="status-dot"></span><span>${htmlEscape(label)}</span>`
    : '<span class="status-dot"></span><span>Готов</span>';
}

function renderOutput(html) {
  document.querySelector("#modelsOutput").innerHTML = html;
}

function renderError(error) {
  renderOutput(`
    <article class="card">
      <span class="badge">Ошибка</span>
      <h2>Ошибка вкладки моделей</h2>
      <p class="muted">${htmlEscape(error.message || String(error))}</p>
    </article>
  `);
}

function renderSessionsList() {
  const sessions = state.sessions?.sessions || [];
  const models = state.models?.models || [];

  if (sessions.length === 0) {
    renderOutput(`
      <article class="card">
        <h2>Сессии обучения</h2>
        <p class="muted">Модели пока не обучены. Сначала перейдите во вкладку «Обучение».</p>
        <a class="button button-primary" href="/training" data-link>Перейти к обучению</a>
      </article>
    `);
    return;
  }

  const rows = sessions.map((session) => ({
    "Сессия": session.session_id,
    "Статус": session.status,
    "Датасет": session.dataset_id,
    "Цель": session.target_mode,
    "Признаки": session.feature_count,
    "Строки": session.rows,
    "Модели": (session.trained_models || []).join(", "),
    "Завершено": session.completed_at,
  }));

  renderOutput(`
    <section class="grid grid-4">
      ${renderSummaryCards({
        sessions: state.sessions.total || 0,
        models: models.length,
        validated: models.filter(
          (model) => model.export_validation_status === "validated",
        ).length,
        onnx: models.filter((model) => model.onnx_path).length,
      })}
    </section>

    <article class="card" style="margin-top: 16px;">
      <h2>Сессии обучения</h2>
      ${renderDataTable(rows)}
    </article>
  `);
}

function renderModelsList() {
  const models = state.models?.models || [];

  if (models.length === 0) {
    renderOutput(`
      <article class="card">
        <h2>Обученные модели</h2>
        <p class="muted">Сохраненных моделей пока нет. Запустите обучение на выбранном датасете.</p>
        <a class="button button-primary" href="/training" data-link>Обучить модели</a>
      </article>
    `);
    return;
  }

  const rows = models.map((model) => ({
    "Сессия": model.session_id,
    "Модель": model.model_name,
    "Формат": model.artifact_format,
    "Датасет": model.dataset_id,
    "Цель": model.target_mode,
    "Признаки": model.feature_count,
    "Проверка": model.export_validation_status,
    "ONNX": model.onnx_path ? "да" : "нет",
  }));

  renderOutput(`
    <article class="card">
      <h2>Обученные модели</h2>
      ${renderDataTable(rows)}
    </article>
  `);
}

function renderSessionDetails(details) {
  const artifacts = details.artifacts || [];
  const artifactRows = artifacts.map((artifact) => ({
    "Модель": artifact.model_name,
    "Статус": artifact.export_validation?.status || "",
    "Формат": artifact.metadata?.artifact_format || "",
    "Признаки": artifact.metadata?.feature_count || 0,
    "Обучающие строки": artifact.metadata?.train_rows || 0,
    "Предсказания": artifact.metadata?.prediction_rows || 0,
  }));

  const buttons = artifacts
    .map(
      (artifact) => `
        <button
          class="button button-secondary"
          data-model-name="${htmlEscape(artifact.model_name)}"
          data-models-action="model"
          type="button"
        >
          ${htmlEscape(artifact.model_name)}
        </button>
      `,
    )
    .join("");

  renderOutput(`
    <section class="grid grid-4">
      ${renderSummaryCards({
        models: artifacts.length,
        rows: details.summary?.rows || 0,
        feature_count: details.summary?.feature_count || 0,
        failures: details.summary?.failed_models?.length || 0,
      })}
    </section>

    <article class="card" style="margin-top: 16px;">
      <h2>Сессия</h2>
      <div class="info-list">
        <p><strong>ID:</strong> ${htmlEscape(details.session_id || state.selectedSessionId)}</p>
        <p><strong>Датасет:</strong> ${htmlEscape(details.summary?.dataset_id || "")}</p>
        <p><strong>Статус:</strong> ${htmlEscape(details.summary?.status || "")}</p>
      </div>
    </article>

    <article class="card" style="margin-top: 16px;">
      <h2>Артефакты моделей</h2>
      ${renderDataTable(artifactRows)}
      <div class="toolbar" style="margin-top: 12px;">${buttons}</div>
    </article>

    <article class="card" style="margin-top: 16px;">
      <h2>Сравнение качества</h2>
      ${renderDataTable(details.comparison_metrics || [])}
    </article>
  `);

  bindModelButtons();
}

function renderModelArtifact(details) {
  renderOutput(`
    <section class="grid grid-3">
      <article class="card">
        <h2>${htmlEscape(details.model_name)}</h2>
        <p class="muted">${htmlEscape(details.model_dir || "")}</p>
      </article>
      <article class="card">
        <h2>Проверка</h2>
        <p><strong>${htmlEscape(details.export_validation?.status || "unknown")}</strong></p>
      </article>
      <article class="card">
        <h2>Предсказания</h2>
        <p><strong>${htmlEscape(details.prediction_rows || 0)}</strong> rows</p>
      </article>
    </section>

    <article class="card" style="margin-top: 16px;">
      <h2>Сведения о модели</h2>
      <div class="info-list">
        <p><strong>Формат:</strong> ${htmlEscape(details.metadata?.artifact_format || "")}</p>
        <p><strong>Признаки:</strong> ${htmlEscape(details.metadata?.feature_count || 0)}</p>
        <p><strong>Строк обучения:</strong> ${htmlEscape(details.metadata?.train_rows || 0)}</p>
      </div>
    </article>

    <article class="card" style="margin-top: 16px;">
      <h2>Проверка экспорта</h2>
      ${renderDataTable([details.export_validation || {}])}
    </article>

    <article class="card" style="margin-top: 16px;">
      <h2>Метрики</h2>
      ${renderDataTable(Object.entries(details.metrics || {}).map(([name, value]) => ({ metric: name, value })))}
    </article>

    <article class="card" style="margin-top: 16px;">
      <h2>Пример предсказаний</h2>
      ${renderDataTable(details.predictions_preview || [])}
    </article>
  `);
}

function renderExportResult(result) {
  renderOutput(`
    <section class="grid grid-3">
      <article class="card">
        <h2>${htmlEscape(result.model_name)}</h2>
        <p class="muted">${htmlEscape(result.session_id)}</p>
      </article>
      <article class="card">
        <h2>Validation</h2>
        <p><strong>${htmlEscape(result.status || "unknown")}</strong></p>
      </article>
      <article class="card">
        <h2>ONNX</h2>
        <p><strong>${htmlEscape(result.onnx?.status || "not_requested")}</strong></p>
      </article>
    </section>

    <article class="card" style="margin-top: 16px;">
      <h2>Результат проверки</h2>
      ${renderDataTable([{
        model: result.model_name,
        status: result.status || "unknown",
        onnx: result.onnx?.status || "не запрошен",
      }])}
    </article>
  `);
}

async function refreshAll() {
  state.sessions = await api.trainingSessions();
  state.models = await api.modelsList();

  if (!state.selectedSessionId) {
    state.selectedSessionId = state.sessions?.sessions?.[0]?.session_id || "";
  }

  if (!state.selectedModelName) {
    state.selectedModelName = filteredModels()[0]?.model_name || "";
  }

  document.querySelector("#modelsSession").innerHTML = sessionOptions(state.sessions);
  syncModelSelect();
}

async function refreshSessions() {
  try {
    setModelsLoading(true, "Загружаем сессии...");
    await refreshAll();
    renderSessionsList();
  } catch (error) {
    renderError(error);
    toast("Модели", error.message || String(error));
  } finally {
    setModelsLoading(false);
  }
}

async function loadSessionDetails() {
  try {
    readControls();

    if (!state.selectedSessionId) {
      throw new Error("Сначала выберите сессию обучения.");
    }

    setModelsLoading(true, "Загружаем детали сессии...");
    const details = await api.trainingSession(state.selectedSessionId);
    renderSessionDetails(details);
  } catch (error) {
    renderError(error);
    toast("Модели", error.message || String(error));
  } finally {
    setModelsLoading(false);
  }
}

async function loadModelArtifact(modelName = null) {
  try {
    readControls();

    const selectedModelName = modelName || state.selectedModelName;

    if (!state.selectedSessionId || !selectedModelName) {
      throw new Error("Сначала выберите сессию обучения и модель.");
    }

    setModelsLoading(true, `${selectedModelName}...`);
    const details = await api.trainingModelArtifact(
      state.selectedSessionId,
      selectedModelName,
    );
    renderModelArtifact(details);
  } catch (error) {
    renderError(error);
    toast("Артефакт модели", error.message || String(error));
  } finally {
    setModelsLoading(false);
  }
}

async function validateSelectedModel(exportOnnx = false) {
  try {
    readControls();

    if (!state.selectedSessionId || !state.selectedModelName) {
      throw new Error("Сначала выберите сессию обучения и модель.");
    }

    setModelsLoading(true, exportOnnx ? "Экспортируем..." : "Проверяем...");
    const payload = {
      export_onnx: exportOnnx,
      sample_size: state.sampleSize,
    };
    const result = exportOnnx
      ? await api.exportModel(state.selectedSessionId, state.selectedModelName, payload)
      : await api.validateModel(state.selectedSessionId, state.selectedModelName, payload);

    renderExportResult(result);
    state.models = await api.modelsList();
    syncModelSelect();
  } catch (error) {
    renderError(error);
    toast("Экспорт модели", error.message || String(error));
  } finally {
    setModelsLoading(false);
  }
}

async function deleteSelectedModel() {
  try {
    readControls();

    if (!state.selectedSessionId || !state.selectedModelName) {
      throw new Error("Сначала выберите сессию обучения и модель.");
    }

    const confirmed = window.confirm(
      `Удалить модель "${state.selectedModelName}" из сессии "${state.selectedSessionId}"?`,
    );

    if (!confirmed) {
      return;
    }

    setModelsLoading(true, "Удаляем модель...");
    await api.deleteModel(state.selectedSessionId, state.selectedModelName);
    state.models = await api.modelsList();
    state.sessions = await api.trainingSessions();
    state.selectedModelName = filteredModels()[0]?.model_name || "";
    syncModelSelect();
    renderModelsList();
    toast("Модели", "Артефакт модели удален");
  } catch (error) {
    renderError(error);
    toast("Модели", error.message || String(error));
  } finally {
    setModelsLoading(false);
  }
}

function bindModelButtons() {
  document.querySelectorAll("[data-models-action='model']").forEach((button) => {
    button.addEventListener("click", () => {
      state.selectedModelName = button.dataset.modelName;
      document.querySelector("#modelsModel").value = state.selectedModelName;
      loadModelArtifact(button.dataset.modelName);
    });
  });
}

function bindEvents() {
  document.querySelector("#modelsSession").addEventListener("change", () => {
    readControls();
    state.selectedModelName = filteredModels()[0]?.model_name || "";
    syncModelSelect();
  });

  document.querySelector("#modelsModel").addEventListener("change", readControls);
  document.querySelector("#modelsExportOnnx").addEventListener("change", readControls);
  document.querySelector("#modelsSampleSize").addEventListener("change", readControls);

  document.querySelector("[data-models-action='refresh']").addEventListener("click", () => {
    refreshSessions();
  });

  document.querySelector("[data-models-action='sessions']").addEventListener("click", () => {
    renderSessionsList();
  });

  document.querySelector("[data-models-action='models']").addEventListener("click", () => {
    renderModelsList();
  });

  document.querySelector("[data-models-action='details']").addEventListener("click", () => {
    loadSessionDetails();
  });

  document.querySelector("[data-models-action='selected-model']").addEventListener(
    "click",
    () => {
      loadModelArtifact();
    },
  );

  document.querySelector("[data-models-action='validate']").addEventListener("click", () => {
    validateSelectedModel(false);
  });

  document.querySelector("[data-models-action='export']").addEventListener("click", () => {
    validateSelectedModel(state.exportOnnx);
  });

  document.querySelector("[data-models-action='delete-model']").addEventListener("click", () => {
    deleteSelectedModel();
  });
}

export async function renderModels() {
  state.sessions = await api.trainingSessions();
  state.models = await api.modelsList();
  state.selectedSessionId = state.sessions?.sessions?.[0]?.session_id || "";
  state.selectedModelName = filteredModels()[0]?.model_name || "";

  window.setTimeout(() => {
    bindEvents();
    renderSessionsList();
  }, 0);

  return `
    <section class="grid grid-2">
      <article class="card">
        <div class="viewer-section-header">
          <div>
            <h2>Модели</h2>
            <p class="muted">
              Просматривайте обученные модели, сравнивайте метрики и проверяйте,
              что выбранный артефакт готов к использованию.
            </p>
          </div>
          <div class="status-pill status-ok" id="modelsStatus">
            <span class="status-dot"></span>
            <span>Готов</span>
          </div>
        </div>

        <div class="toolbar">
          <div class="form-row">
            <label for="modelsSession">Сессия обучения</label>
            <select class="select" id="modelsSession">
              ${sessionOptions(state.sessions)}
            </select>
          </div>

          <div class="form-row">
            <label for="modelsModel">Модель</label>
            <select class="select" id="modelsModel">
              ${modelOptions()}
            </select>
          </div>

          <div class="form-row">
            <label for="modelsSampleSize">Размер проверки</label>
            <input
              class="input"
              id="modelsSampleSize"
              min="1"
              max="10000"
              type="number"
              value="100"
            />
          </div>
        </div>

        <label class="checkbox-row">
          <input id="modelsExportOnnx" type="checkbox" />
          <span>попробовать экспорт в ONNX</span>
        </label>

        <div class="toolbar">
          <button class="button button-secondary" data-models-action="sessions" type="button">
            Сессии
          </button>
          <button class="button button-secondary" data-models-action="models" type="button">
            Модели
          </button>
          <button class="button button-primary" data-models-action="details" type="button">
            Детали сессии
          </button>
          <button
            class="button button-secondary"
            data-models-action="selected-model"
            type="button"
          >
            Детали модели
          </button>
          <button class="button button-secondary" data-models-action="validate" type="button">
            Проверить
          </button>
          <button class="button button-secondary" data-models-action="export" type="button">
            Экспорт / проверка
          </button>
          <button class="button button-danger" data-models-action="delete-model" type="button">
            Удалить модель
          </button>
          <button class="button button-secondary" data-models-action="refresh" type="button">
            Обновить
          </button>
        </div>
      </article>

      <article class="card">
        <h2>Что выбрано</h2>
        <div class="info-list">
          <p><strong>Сессия:</strong> ${htmlEscape(selectedSession()?.session_id || "не выбрана")}</p>
          <p><strong>Модель:</strong> ${htmlEscape(selectedModel()?.model_name || "не выбрана")}</p>
          <p><strong>Датасет:</strong> ${htmlEscape(selectedSession()?.dataset_id || selectedModel()?.dataset_id || "")}</p>
        </div>
      </article>
    </section>

    <section id="modelsOutput" style="margin-top: 16px;">
      <article class="card">
        <h2>Сессии обучения</h2>
        <p class="muted">Загрузка списка...</p>
      </article>
    </section>
  `;
}
