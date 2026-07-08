import { api } from "../api.js";
import { pageNotice, prettyJson } from "../app.js";

export async function renderModels() {
  const sessions = await api.sessions();

  return `
    ${pageNotice(
      "Model artifacts появятся после этапов 27.16–27.19",
      "Страница уже подключена к sessions API и готова показывать training sessions и model export status.",
      "Frontend route ready",
    )}

    <article class="card" style="margin-top: 16px;">
      <h2>Sessions</h2>
      <pre class="code">${prettyJson(sessions)}</pre>
    </article>
  `;
}