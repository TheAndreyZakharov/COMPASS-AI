import { api } from "../api.js";
import { pageNotice, prettyJson } from "../app.js";

export async function renderTraining() {
  const datasets = await api.datasets();

  return `
    ${pageNotice(
      "Training backend будет подключён на этапе 27.16",
      "Страница уже показывает доступные datasets, чтобы после feature builder и training API сразу выбрать источник обучения.",
      "Frontend route ready",
    )}

    <article class="card" style="margin-top: 16px;">
      <h2>Available datasets</h2>
      <pre class="code">${prettyJson(datasets)}</pre>
    </article>
  `;
}