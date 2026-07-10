import { api } from "../api.js";
import {
  getLastDatasetId,
  htmlEscape,
  setLastDatasetId,
  toast,
} from "../app.js";
import { renderSummaryCards } from "../components/charts.js";
import { renderDataTable } from "../components/table.js";
import {
  normalizeMetricRows,
  renderModelMetricCards,
  renderTrainingMetrics,
} from "../components/training_metrics.js";
import { renderReportLinks, renderTrainingPlots } from "../components/training_plots.js";

const MODEL_NAMES = [
  "baseline_rule_based",
  "sgd_classifier",
  "logistic_regression",
  "random_forest",
  "hist_gradient_boosting",
  "torch_mlp",
];

const MODEL_DESCRIPTIONS = {
  baseline_rule_based: "Быстрый понятный базовый алгоритм без обучения, нужен как контрольная точка.",
  sgd_classifier: "Легкая линейная модель, быстро обучается на больших данных.",
  logistic_regression: "Стабильная интерпретируемая модель для вероятности успешного назначения.",
  random_forest: "Ансамбль деревьев, хорошо ловит нелинейные связи и устойчив к шуму.",
  hist_gradient_boosting: "Бустинг по деревьям, часто дает сильное качество на табличных данных.",
  torch_mlp: "Нейросеть MLP, полезна для сложных зависимостей, но обучается дольше.",
};

const state = {
  datasets: null,
  datasetId: "",
  datasetKind: "generated",
  lastTrainingResult: null,
  sessions: null,
  selectedSessionId: "",
};

function startLongTaskToast(options) {
  const detail = { options, controller: null };
  window.dispatchEvent(new CustomEvent("sandbox-long-task-start", { detail }));

  return detail.controller || {
    update() {},
    done(message = "Готово") {
      toast(options?.title || "Обучение", message);
    },
    error(message = "Ошибка") {
      toast(options?.title || "Обучение", message);
    },
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
  const [datasetKind, ...datasetIdParts] = value.split(":");

  return {
    datasetKind: datasetKind || "generated",
    datasetId: datasetIdParts.join(":"),
  };
}

function datasetOptions(payload) {
  const datasets = allDatasets(payload);

  if (datasets.length === 0) {
    return '<option value="">Нет datasets</option>';
  }

  return datasets
    .map((dataset) => {
      const selected =
        dataset.dataset_id === state.datasetId &&
        dataset.dataset_kind === state.datasetKind
          ? "selected"
          : "";

      return `
        <option value="${htmlEscape(datasetOptionValue(dataset))}" ${selected}>
          ${htmlEscape(dataset.dataset_id)} · ${htmlEscape(dataset.dataset_kind)}
        </option>
      `;
    })
    .join("");
}

function sessionOptions(payload) {
  const sessions = payload?.sessions || [];

  if (sessions.length === 0) {
    return '<option value="">Нет sessions</option>';
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

function selectInitialDataset() {
  const datasets = allDatasets(state.datasets);
  const lastDatasetId = getLastDatasetId();
  const lastDataset = datasets.find((dataset) => dataset.dataset_id === lastDatasetId);
  const selectedDataset = lastDataset || datasets[0] || null;

  state.datasetId = selectedDataset?.dataset_id || "";
  state.datasetKind = selectedDataset?.dataset_kind || "generated";
}

function selectedDataset() {
  return allDatasets(state.datasets).find(
    (dataset) =>
      dataset.dataset_id === state.datasetId &&
      dataset.dataset_kind === state.datasetKind,
  );
}

function selectedModels() {
  return MODEL_NAMES.filter((modelName) => {
    const checkbox = document.querySelector(`[data-training-model="${modelName}"]`);
    return checkbox?.checked;
  });
}

function readDatasetControls() {
  const parsed = parseDatasetValue(document.querySelector("#trainingDataset").value);
  state.datasetId = parsed.datasetId;
  state.datasetKind = parsed.datasetKind;

  if (state.datasetId) {
    setLastDatasetId(state.datasetId);
  }
}

function readSessionControls() {
  state.selectedSessionId = document.querySelector("#trainingSessionSelect").value;
}

function numberValue(selector, fallback) {
  const value = Number.parseFloat(document.querySelector(selector).value);

  if (!Number.isFinite(value)) {
    return fallback;
  }

  return value;
}

function integerValue(selector, fallback) {
  const value = Number.parseInt(document.querySelector(selector).value, 10);

  if (!Number.isFinite(value)) {
    return fallback;
  }

  return value;
}

function setTrainingLoading(isLoading, label = "Training...") {
  const status = document.querySelector("#trainingStatus");
  const buttons = document.querySelectorAll("[data-training-action]");

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
    : '<span class="status-dot"></span><span>Готов</span>';
}

function setOutput(html) {
  const output = document.querySelector("#trainingOutput");
  if (output) {
    output.innerHTML = html;
  }
}

function renderError(title, error) {
  setOutput(`
    <article class="card">
      <span class="badge">Ошибка</span>
      <h2>${htmlEscape(title)}</h2>
      <p class="muted">${htmlEscape(error.message || String(error))}</p>
    </article>
  `);
}

function buildFeaturePayload() {
  readDatasetControls();

  const payload = {
    dataset_id: state.datasetId,
    dataset_kind: state.datasetKind,
    target_mode: document.querySelector("#trainingTargetMode").value,
    overwrite: document.querySelector("#featureOverwrite").checked,
  };

  const maxPairs = integerValue("#featureMaxPairs", 0);
  if (maxPairs > 0) {
    payload.max_pairs = maxPairs;
  }

  return payload;
}

function buildModelParams() {
  return {
    logistic_regression: {
      max_iter: integerValue("#paramLogisticMaxIter", 500),
    },
    random_forest: {
      max_depth: integerValue("#paramRandomForestDepth", 0) || null,
      n_estimators: integerValue("#paramRandomForestEstimators", 120),
    },
    sgd_classifier: {
      alpha: numberValue("#paramSgdAlpha", 0.0001),
      max_iter: integerValue("#paramSgdMaxIter", 1000),
    },
    torch_mlp: {
      batch_size: integerValue("#paramTorchBatchSize", 128),
      dropout: numberValue("#paramTorchDropout", 0.1),
      epochs: integerValue("#paramTorchEpochs", 12),
      hidden_size: integerValue("#paramTorchHidden", 64),
      learning_rate: numberValue("#paramTorchLr", 0.001),
    },
  };
}

function buildTrainingPayload() {
  readDatasetControls();

  const modelNames = selectedModels();
  const maxPairs = integerValue("#featureMaxPairs", 0);

  if (modelNames.length === 0) {
    throw new Error("Выбери хотя бы одну модель.");
  }

  const payload = {
    auto_build_features: document.querySelector("#trainingAutoBuild").checked,
    dataset_id: state.datasetId,
    dataset_kind: state.datasetKind,
    model_names: modelNames,
    model_params: buildModelParams(),
    seed: integerValue("#trainingSeed", 19001),
    split: {
      test_size: numberValue("#splitTest", 0.15),
      train_size: numberValue("#splitTrain", 0.7),
      validation_size: numberValue("#splitValidation", 0.15),
    },
    target_mode: document.querySelector("#trainingTargetMode").value,
    overwrite_features: document.querySelector("#featureOverwrite").checked,
  };

  if (maxPairs > 0) {
    payload.max_pairs = maxPairs;
  }

  return payload;
}

function renderFeatureResult(result) {
  const metadata = result.metadata || result;
  const dimensions = metadata.feature_dimensions || {};
  const counts = metadata.output_counts || {};
  const featureRows = [
    {
      feature_count: dimensions.feature_count || 0,
      feature_rows: counts.feature_rows || 0,
      skipped_pairs: counts.skipped_pairs || 0,
      skill_vocabulary_size: dimensions.skill_vocabulary_size || 0,
      target_mode: metadata.target_mode || "",
      target_rows: counts.target_rows || 0,
    },
  ];

  setOutput(`
    <section class="grid grid-4">
      ${renderSummaryCards({
        feature_count: dimensions.feature_count || 0,
        skill_vocabulary_size: dimensions.skill_vocabulary_size || 0,
        feature_rows: counts.feature_rows || 0,
        target_rows: counts.target_rows || 0,
      })}
    </section>

    <article class="card" style="margin-top: 16px;">
      <h2>Feature dimensions</h2>
      ${renderDataTable(featureRows)}
    </article>

    <article class="card" style="margin-top: 16px;">
      <h2>Готово к обучению</h2>
      <p class="muted">
        Признаки построены. Теперь можно запускать обучение выбранных моделей.
      </p>
    </article>
  `);
}

function renderTrainingResult(result) {
  const comparison = result.comparison_metrics || result.metrics || [];
  const normalizedMetrics = normalizeMetricRows(comparison);
  const sessionId = result.session_id || result.summary?.session_id || "";

  state.lastTrainingResult = result;
  state.selectedSessionId = sessionId || state.selectedSessionId;

  setOutput(`
    <section class="grid grid-4">
      ${renderSummaryCards({
        session: sessionId || "created",
        status: result.status || "",
        models: normalizedMetrics.length,
        failed: result.failed_models?.length || 0,
      })}
    </section>

    <section class="grid grid-3" style="margin-top: 16px;">
      ${renderModelMetricCards(normalizedMetrics)}
    </section>

    <section style="margin-top: 16px;">
      ${renderTrainingMetrics(normalizedMetrics)}
    </section>

    <article class="card next-step-card" style="margin-top: 16px;">
      <h2>Следующий шаг</h2>
      <p class="muted">
        Модели обучены. Откройте вкладку «Модели» для просмотра артефактов
        или перейдите к назначению задач.
      </p>
      <div class="toolbar">
        <a class="button button-secondary" href="/models" data-link>Открыть модели</a>
        <a class="button button-secondary" href="/assignment-lab" data-link>Назначить задачи</a>
      </div>
    </article>
  `);
}

function renderSessionDetails(details) {
  const comparison = details.comparison_metrics || [];
  const artifacts = details.artifacts || [];
  const artifactRows = artifacts.map((artifact) => ({
    artifact_format: artifact.metadata?.artifact_format || "",
    export_status: artifact.export_validation?.status || "",
    files: (artifact.files || []).join(", "),
    model_name: artifact.model_name,
    prediction_rows: artifact.prediction_rows || artifact.metadata?.prediction_rows || 0,
  }));

  setOutput(`
    <section class="grid grid-4">
      ${renderSummaryCards({
        session: details.session_id || state.selectedSessionId,
        status: details.summary?.status || "",
        models: artifacts.length,
        failures: details.summary?.failed_models?.length || 0,
      })}
    </section>

    <section style="margin-top: 16px;">
      ${renderTrainingMetrics(comparison)}
    </section>

    <article class="card" style="margin-top: 16px;">
      <h2>Model artifacts</h2>
      ${renderDataTable(artifactRows)}
    </article>

    <article class="card" style="margin-top: 16px;">
      <h2>Сессия обучения</h2>
      <div class="info-list">
        <p><strong>ID:</strong> ${htmlEscape(details.session_id || state.selectedSessionId)}</p>
        <p><strong>Датасет:</strong> ${htmlEscape(details.summary?.dataset_id || "")}</p>
        <p><strong>Статус:</strong> ${htmlEscape(details.summary?.status || "")}</p>
      </div>
    </article>
  `);
}

function renderReport(sessionId, manifest) {
  setOutput(`
    ${renderReportLinks(sessionId, manifest)}
    <section style="margin-top: 16px;">
      ${renderTrainingPlots(sessionId, manifest)}
    </section>
    <article class="card" style="margin-top: 16px;">
      <h2>Отчет готов</h2>
      <p class="muted">Графики и HTML-отчет доступны по ссылкам выше.</p>
    </article>
  `);
}

async function buildFeatures() {
  const progress = startLongTaskToast({
    title: "Строим признаки...",
    message: "Проверяем данные...",
    steps: ["Проверяем данные...", "Строим признаки...", "Сохраняем артефакты..."],
  });

  try {
    setTrainingLoading(true, "Строим признаки...");
    progress.update({ message: "Строим признаки...", percent: 35, stepIndex: 1 });
    const result = await api.buildFeatures(buildFeaturePayload());
    progress.update({ message: "Сохраняем артефакты...", percent: 94, stepIndex: 2 });
    progress.done("Готово");
    renderFeatureResult(result);
    toast("Признаки готовы", `${state.datasetId}`);
  } catch (error) {
    progress.error(error.message || String(error));
    renderError("Не удалось построить признаки", error);
    toast("Ошибка признаков", error.message || String(error));
  } finally {
    setTrainingLoading(false);
  }
}

async function loadFeatureMetadata() {
  try {
    readDatasetControls();
    setTrainingLoading(true, "Загружаем метаданные...");
    const query = `?dataset_kind=${encodeURIComponent(state.datasetKind)}`;
    const result = await api.featureMetadata(state.datasetId, query);
    renderFeatureResult(result);
  } catch (error) {
    renderError("Не удалось загрузить метаданные признаков", error);
    toast("Метаданные признаков", error.message || String(error));
  } finally {
    setTrainingLoading(false);
  }
}

async function runTraining() {
  const progress = startLongTaskToast({
    title: "Обучаем модели...",
    message: "Проверяем данные...",
    steps: [
      "Проверяем данные...",
      "Строим признаки...",
      "Делим данные...",
      "Обучаем модели...",
      "Считаем метрики...",
      "Сохраняем артефакты...",
    ],
  });

  try {
    setTrainingLoading(true, "Обучаем модели...");
    progress.update({ message: "Строим признаки...", percent: 20, stepIndex: 1 });
    const result = await api.runTraining(buildTrainingPayload());
    progress.update({ message: "Сохраняем артефакты...", percent: 96, stepIndex: 5 });
    progress.done("Завершено");
    renderTrainingResult(result);
    await refreshSessions(false);
    toast("Обучение завершено", result.session_id || state.datasetId);
  } catch (error) {
    progress.error(error.message || String(error));
    renderError("Обучение не удалось", error);
    toast("Обучение", error.message || String(error));
  } finally {
    setTrainingLoading(false);
  }
}

async function refreshSessions(render = true) {
  state.sessions = await api.trainingSessions();

  if (!state.selectedSessionId) {
    state.selectedSessionId = state.sessions?.sessions?.[0]?.session_id || "";
  }

  const select = document.querySelector("#trainingSessionSelect");
  if (select) {
    select.innerHTML = sessionOptions(state.sessions);
    select.value = state.selectedSessionId;
  }

  if (render) {
    const rows = state.sessions?.sessions || [];
    setOutput(`
      <article class="card">
        <h2>Сессии обучения</h2>
        ${renderDataTable(rows)}
      </article>
    `);
  }
}

async function loadSessionDetails() {
  try {
    readSessionControls();

    if (!state.selectedSessionId) {
      throw new Error("Сессия обучения не выбрана.");
    }

    setTrainingLoading(true, "Загружаем сессию...");
    const details = await api.trainingSession(state.selectedSessionId);
    renderSessionDetails(details);
  } catch (error) {
    renderError("Не удалось открыть сессию", error);
    toast("Сессия обучения", error.message || String(error));
  } finally {
    setTrainingLoading(false);
  }
}

async function generateReport() {
  try {
    readSessionControls();

    if (!state.selectedSessionId) {
      throw new Error("Сессия обучения не выбрана.");
    }

    setTrainingLoading(true, "Готовим отчет...");
    const manifest = await api.generateTrainingReport(state.selectedSessionId);
    renderReport(state.selectedSessionId, manifest);
    toast("Отчет готов", state.selectedSessionId);
  } catch (error) {
    renderError("Не удалось создать отчет", error);
    toast("Отчет обучения", error.message || String(error));
  } finally {
    setTrainingLoading(false);
  }
}

async function loadReport() {
  try {
    readSessionControls();

    if (!state.selectedSessionId) {
      throw new Error("Сессия обучения не выбрана.");
    }

    setTrainingLoading(true, "Загружаем отчет...");
    const manifest = await api.trainingReport(state.selectedSessionId);
    renderReport(state.selectedSessionId, manifest);
  } catch (error) {
    renderError("Не удалось загрузить отчет", error);
    toast("Отчет обучения", error.message || String(error));
  } finally {
    setTrainingLoading(false);
  }
}

async function deleteSelectedSession() {
  try {
    readSessionControls();

    if (!state.selectedSessionId) {
      throw new Error("Сессия обучения не выбрана.");
    }

    const confirmed = window.confirm(
      `Удалить сессию обучения "${state.selectedSessionId}" вместе с моделями и отчетами?`,
    );

    if (!confirmed) {
      return;
    }

    setTrainingLoading(true, "Удаляем сессию...");
    await api.deleteTrainingSession(state.selectedSessionId);
    state.selectedSessionId = "";
    await refreshSessions(false);
    setOutput(`
      <article class="card">
        <h2>Сессия обучения удалена</h2>
        <p class="muted">Сессия обучения и ее модели удалены.</p>
      </article>
    `);
    toast("Сессия обучения удалена", "Артефакты удалены");
  } catch (error) {
    renderError("Не удалось удалить сессию", error);
    toast("Сессия обучения", error.message || String(error));
  } finally {
    setTrainingLoading(false);
  }
}

function toggleAllModels(checked) {
  MODEL_NAMES.forEach((modelName) => {
    const checkbox = document.querySelector(`[data-training-model="${modelName}"]`);
    if (checkbox) {
      checkbox.checked = checked;
    }
  });
}

function bindEvents() {
  document.querySelector("#trainingDataset").addEventListener("change", readDatasetControls);
  document.querySelector("#trainingSessionSelect").addEventListener("change", readSessionControls);

  document.querySelector("[data-training-action='features']").addEventListener("click", () => {
    buildFeatures();
  });

  document.querySelector("[data-training-action='metadata']").addEventListener("click", () => {
    loadFeatureMetadata();
  });

  document.querySelector("[data-training-action='run']").addEventListener("click", () => {
    runTraining();
  });

  document.querySelector("[data-training-action='sessions']").addEventListener("click", () => {
    refreshSessions(true);
  });

  document.querySelector("[data-training-action='session-details']").addEventListener(
    "click",
    () => {
      loadSessionDetails();
    },
  );

  document.querySelector("[data-training-action='report-generate']").addEventListener(
    "click",
    () => {
      generateReport();
    },
  );

  document.querySelector("[data-training-action='report-load']").addEventListener("click", () => {
    loadReport();
  });

  document.querySelector("[data-training-action='delete-session']").addEventListener(
    "click",
    () => {
      deleteSelectedSession();
    },
  );

  document.querySelector("[data-training-action='select-all']").addEventListener("click", () => {
    toggleAllModels(true);
  });

  document.querySelector("[data-training-action='select-core']").addEventListener("click", () => {
    toggleAllModels(false);
    ["baseline_rule_based", "logistic_regression", "random_forest"].forEach((modelName) => {
      const checkbox = document.querySelector(`[data-training-model="${modelName}"]`);
      if (checkbox) {
        checkbox.checked = true;
      }
    });
  });
}

function renderModelCheckboxes() {
  return MODEL_NAMES.map((modelName) => {
    return `
      <label class="checkbox-row model-choice">
        <input checked data-training-model="${htmlEscape(modelName)}" type="checkbox" />
        <span>
          <strong>${htmlEscape(modelName)}</strong>
          <small>${htmlEscape(MODEL_DESCRIPTIONS[modelName] || "")}</small>
        </span>
      </label>
    `;
  }).join("");
}

export async function renderTraining() {
  state.datasets = await api.datasets();
  state.sessions = await api.trainingSessions();
  selectInitialDataset();
  state.selectedSessionId = state.sessions?.sessions?.[0]?.session_id || "";

  window.setTimeout(bindEvents, 0);

  return `
    <section class="grid grid-2">
      <article class="card">
        <div class="viewer-section-header">
          <div>
            <h2>Обучение моделей</h2>
            <p class="muted">
              Выберите датасет и запустите обучение. По умолчанию включены все
              доступные методы, чтобы их можно было сравнить между собой.
            </p>
          </div>
          <div class="status-pill status-ok" id="trainingStatus">
            <span class="status-dot"></span>
            <span>Готов</span>
          </div>
        </div>

        <div class="form">
          <div class="grid grid-2">
            <div class="form-row">
              <label for="trainingDataset">Датасет</label>
              <select class="select" id="trainingDataset">
                ${datasetOptions(state.datasets)}
              </select>
            </div>

            <div class="form-row">
              <label for="trainingTargetMode">Цель модели</label>
              <select class="select" id="trainingTargetMode">
                <option value="balanced">balanced</option>
                <option value="quality">quality</option>
                <option value="speed">speed</option>
                <option value="learning">learning</option>
                <option value="risk_aware">risk_aware</option>
              </select>
            </div>

            <div class="form-row">
              <label for="trainingSeed">Seed</label>
              <input class="input" id="trainingSeed" type="number" value="19001" />
            </div>

            <div class="form-row">
              <label for="featureMaxPairs">Максимум пар</label>
              <input
                class="input"
                id="featureMaxPairs"
                min="1"
                placeholder="120000"
                type="number"
                value="120000"
              />
              <p class="muted">120000 — безопасный режим для 8 ГБ памяти.</p>
            </div>
          </div>

          <div class="grid grid-3">
            <div class="form-row">
              <label for="splitTrain">Доля обучения</label>
              <input class="input" id="splitTrain" step="0.01" type="number" value="0.70" />
            </div>
            <div class="form-row">
              <label for="splitValidation">Доля проверки</label>
              <input
                class="input"
                id="splitValidation"
                step="0.01"
                type="number"
                value="0.15"
              />
            </div>
            <div class="form-row">
              <label for="splitTest">Доля теста</label>
              <input class="input" id="splitTest" step="0.01" type="number" value="0.15" />
            </div>
          </div>

          <div class="grid grid-2">
            <label class="checkbox-row">
              <input checked id="featureOverwrite" type="checkbox" />
              <span>перестроить признаки</span>
            </label>
            <label class="checkbox-row">
              <input checked id="trainingAutoBuild" type="checkbox" />
              <span>автоматически построить признаки перед обучением</span>
            </label>
          </div>

          <h3>Модели для обучения</h3>
          <div class="grid grid-2">
            ${renderModelCheckboxes()}
          </div>

          <div class="toolbar">
            <button class="button button-secondary" data-training-action="select-core" type="button">
              Выбрать базовые
            </button>
            <button class="button button-secondary" data-training-action="select-all" type="button">
              Выбрать все
            </button>
            <button class="button button-secondary" data-training-action="features" type="button">
              Построить признаки
            </button>
            <button class="button button-secondary" data-training-action="metadata" type="button">
              Проверить признаки
            </button>
            <button class="button button-primary" data-training-action="run" type="button">
              Запустить обучение
            </button>
          </div>
        </div>
      </article>

      <article class="card">
        <h2>Параметры моделей</h2>
        <p class="muted">Оставьте значения по умолчанию, если не хотите тонко настраивать обучение.</p>
        <div class="grid grid-2">
          <div class="form-row">
            <label for="paramLogisticMaxIter">logistic max_iter</label>
            <input class="input" id="paramLogisticMaxIter" type="number" value="500" />
          </div>
          <div class="form-row">
            <label for="paramRandomForestEstimators">rf n_estimators</label>
            <input class="input" id="paramRandomForestEstimators" type="number" value="80" />
          </div>
          <div class="form-row">
            <label for="paramRandomForestDepth">rf max_depth</label>
            <input class="input" id="paramRandomForestDepth" placeholder="empty" type="number" />
          </div>
          <div class="form-row">
            <label for="paramSgdAlpha">sgd alpha</label>
            <input class="input" id="paramSgdAlpha" step="0.0001" type="number" value="0.0001" />
          </div>
          <div class="form-row">
            <label for="paramSgdMaxIter">sgd max_iter</label>
            <input class="input" id="paramSgdMaxIter" type="number" value="1000" />
          </div>
          <div class="form-row">
            <label for="paramTorchEpochs">torch epochs</label>
            <input class="input" id="paramTorchEpochs" type="number" value="8" />
          </div>
          <div class="form-row">
            <label for="paramTorchHidden">torch hidden</label>
            <input class="input" id="paramTorchHidden" type="number" value="64" />
          </div>
          <div class="form-row">
            <label for="paramTorchDropout">torch dropout</label>
            <input class="input" id="paramTorchDropout" step="0.01" type="number" value="0.10" />
          </div>
          <div class="form-row">
            <label for="paramTorchLr">torch lr</label>
            <input class="input" id="paramTorchLr" step="0.0001" type="number" value="0.001" />
          </div>
          <div class="form-row">
            <label for="paramTorchBatchSize">torch batch_size</label>
            <input class="input" id="paramTorchBatchSize" type="number" value="64" />
          </div>
        </div>
      </article>
    </section>

    <section class="grid grid-2" style="margin-top: 16px;">
      <article class="card">
        <h2>Сессии обучения</h2>
        <div class="toolbar">
          <select class="select" id="trainingSessionSelect">
            ${sessionOptions(state.sessions)}
          </select>
          <button class="button button-secondary" data-training-action="sessions" type="button">
            Обновить
          </button>
          <button
            class="button button-secondary"
            data-training-action="session-details"
            type="button"
          >
            Детали сессии
          </button>
          <button
            class="button button-secondary"
            data-training-action="report-generate"
            type="button"
          >
            Создать графики
          </button>
          <button class="button button-secondary" data-training-action="report-load" type="button">
            Открыть графики
          </button>
          <button class="button button-danger" data-training-action="delete-session" type="button">
            Удалить сессию
          </button>
        </div>
      </article>

      <article class="card">
        <h2>Выбранный датасет</h2>
        <div class="info-list">
          <p><strong>ID:</strong> ${htmlEscape(selectedDataset()?.dataset_id || "не выбран")}</p>
          <p><strong>Тип:</strong> ${htmlEscape(selectedDataset()?.dataset_kind || "")}</p>
          <p><strong>Задачи:</strong> ${htmlEscape(selectedDataset()?.counts?.tasks || 0)}</p>
          <p><strong>Пары:</strong> ${htmlEscape(selectedDataset()?.counts?.training_pairs || 0)}</p>
        </div>
      </article>
    </section>

    <section id="trainingOutput" style="margin-top: 16px;">
      <article class="card">
        <h2>Готово к запуску</h2>
        <p class="muted">
          Выберите датасет, цель и модели. Затем нажмите «Запустить обучение».
        </p>
      </article>
    </section>
  `;
}
