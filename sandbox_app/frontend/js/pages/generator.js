import { api } from "../api.js";
import { htmlEscape, prettyJson, setLastDatasetId, toast } from "../app.js";

const defaultPayloads = {
  dataset: {
    dataset_id: "ui_full_dataset",
    domain_profile: "developers",
    dataset_mode: "small_preview",
    employees_count: 10,
    tasks_count: 100,
    history_depth_per_employee: 5,
    target_pairs: 1000,
    candidates_per_task: 10,
    target_mode: "balanced",
    seed: 11101,
    overwrite: true,
  },
  team: {
    dataset_id: "ui_team_dataset",
    domain_profile: "developers",
    employees_count: 12,
    seed: 11102,
    overwrite: true,
  },
  tasks: {
    dataset_id: "ui_tasks_dataset",
    domain_profile: "developers",
    tasks_count: 60,
    projects_count: 4,
    seed: 11103,
    overwrite: true,
  },
  history: {
    dataset_id: "ui_full_dataset",
    domain_profile: "developers",
    history_depth_per_employee: 5,
    seed: 11104,
    overwrite: true,
  },
};

async function submitGenerator(kind) {
  const textarea = document.querySelector(`#${kind}Payload`);
  const output = document.querySelector("#generatorOutput");

  try {
    const payload = JSON.parse(textarea.value);
    output.textContent = "Генерация...";
    const result = await api[`generate${kind[0].toUpperCase()}${kind.slice(1)}`](payload);

    if (result.dataset_id) {
      setLastDatasetId(result.dataset_id);
    }

    output.textContent = JSON.stringify(result, null, 2);
    toast("Готово", `Сгенерирован dataset: ${result.dataset_id || "без dataset_id"}`);
  } catch (error) {
    output.textContent = error.message;
    toast("Ошибка генерации", error.message);
  }
}

function generatorCard(kind, title) {
  return `
    <article class="card">
      <h2>${htmlEscape(title)}</h2>
      <div class="form">
        <div class="form-row">
          <label for="${kind}Payload">JSON payload</label>
          <textarea class="textarea" id="${kind}Payload">${prettyJson(defaultPayloads[kind])}</textarea>
        </div>
        <button class="button button-primary" data-generator="${kind}" type="button">
          Запустить
        </button>
      </div>
    </article>
  `;
}

export async function renderGenerator() {
  window.setTimeout(() => {
    document.querySelectorAll("[data-generator]").forEach((button) => {
      button.addEventListener("click", () => submitGenerator(button.dataset.generator));
    });
  }, 0);

  return `
    <section class="grid grid-2">
      ${generatorCard("dataset", "Full dataset")}
      ${generatorCard("team", "Team")}
      ${generatorCard("tasks", "Tasks")}
      ${generatorCard("history", "History")}
    </section>

    <article class="card" style="margin-top: 16px;">
      <h2>Result</h2>
      <pre class="code" id="generatorOutput">Результат появится здесь.</pre>
    </article>
  `;
}