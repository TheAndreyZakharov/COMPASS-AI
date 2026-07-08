import { api } from "../api.js";
import { pageNotice, prettyJson } from "../app.js";

export async function renderReports() {
  const datasets = await api.datasets();
  const sessions = await api.sessions();

  return `
    ${pageNotice(
      "Reports и exports будут подключены на этапах 27.18 и 27.26",
      "Страница готова к отображению dataset reports, training reports, assignment reports и download links.",
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