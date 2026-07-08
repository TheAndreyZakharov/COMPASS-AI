import { api } from "../api.js";
import { prettyJson } from "../app.js";

function metricCard(title, value, subtitle) {
  return `
    <article class="card kpi">
      <span class="muted">${title}</span>
      <strong>${value}</strong>
      <small class="muted">${subtitle}</small>
    </article>
  `;
}

export async function renderDashboard() {
  const [health, status, config, sessions, contracts, schemas, datasets] = await Promise.all([
    api.health(),
    api.status(),
    api.config(),
    api.sessions(),
    api.contractsSummary(),
    api.featureSchemas(),
    api.datasets(),
  ]);

  const generatedCount = datasets.counts?.generated ?? 0;
  const importedCount = datasets.counts?.imported ?? 0;
  const schemaCount = Array.isArray(schemas.items) ? schemas.items.length : 0;
  const contractCount = contracts.counts?.contracts ?? contracts.contracts_count ?? 0;

  return `
    <section class="grid grid-3">
      ${metricCard("Health", health.status || "ok", "FastAPI backend")}
      ${metricCard("Generated datasets", generatedCount, "Data Viewer")}
      ${metricCard("Imported datasets", importedCount, "Data Viewer")}
      ${metricCard("Feature schemas", schemaCount, "Domain profiles")}
      ${metricCard("Data contracts", contractCount, "Validation layer")}
      ${metricCard("Sessions", sessions.total ?? 0, "Training and assignment")}
    </section>

    <section class="grid grid-2" style="margin-top: 16px;">
      <article class="card">
        <h2>Backend status</h2>
        <pre class="code">${prettyJson(status)}</pre>
      </article>
      <article class="card">
        <h2>Config snapshot</h2>
        <pre class="code">${prettyJson(config)}</pre>
      </article>
    </section>
  `;
}