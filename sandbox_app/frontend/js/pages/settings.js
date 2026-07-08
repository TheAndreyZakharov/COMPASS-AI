import { api } from "../api.js";
import { prettyJson } from "../app.js";

export async function renderSettings() {
  const [settings, schemas, contracts] = await Promise.all([
    api.settings(),
    api.featureSchemas(),
    api.contractsSummary(),
  ]);

  return `
    <section class="grid grid-2">
      <article class="card">
        <h2>App settings</h2>
        <pre class="code">${prettyJson(settings)}</pre>
      </article>
      <article class="card">
        <h2>Feature schemas</h2>
        <pre class="code">${prettyJson(schemas)}</pre>
      </article>
      <article class="card">
        <h2>Data contracts</h2>
        <pre class="code">${prettyJson(contracts)}</pre>
      </article>
      <article class="card">
        <h2>Schema editor</h2>
        <p class="muted">
          Backend для feature schemas уже готов. Полный UI редактора будет расширен в этапе 27.27.
          Текущая страница уже показывает активные schemas и contracts без ручного открытия JSON.
        </p>
      </article>
    </section>
  `;
}