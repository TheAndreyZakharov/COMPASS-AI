import { api } from "../api.js";
import { pageNotice, prettyJson } from "../app.js";

export async function renderAssignmentLab() {
  const datasets = await api.datasets();
  const sessions = await api.sessions();

  return `
    ${pageNotice(
      "Assignment Lab будет расширен на этапах 27.21–27.25",
      "Сейчас страница показывает datasets и sessions. После recommendation backend здесь появятся single recommendation, bulk assignment и Qwen explanations.",
      "Frontend route ready",
    )}

    <section class="grid grid-2" style="margin-top: 16px;">
      <article class="card">
        <h2>Datasets</h2>
        <pre class="code">${prettyJson(datasets)}</pre>
      </article>
      <article class="card">
        <h2>Sessions</h2>
        <pre class="code">${prettyJson(sessions)}</pre>
      </article>
    </section>
  `;
}