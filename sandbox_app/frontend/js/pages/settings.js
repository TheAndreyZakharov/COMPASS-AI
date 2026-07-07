import { getConfig } from "../api.js";

export const title = "Settings";

export async function render(container) {
  container.innerHTML = `<div class="loading-state">Loading settings...</div>`;

  const config = await getConfig();

  container.innerHTML = `
    <div class="grid two">
      <section class="card">
        <h2>Application</h2>
        <div class="form-grid">
          <div class="form-row">
            <label>App name</label>
            <input value="${config.app_name || ""}" readonly>
          </div>
          <div class="form-row">
            <label>Version</label>
            <input value="${config.app_version || ""}" readonly>
          </div>
          <div class="form-row">
            <label>Python target</label>
            <input value="${config.python_version || ""}" readonly>
          </div>
        </div>
      </section>

      <section class="card">
        <h2>Ollama</h2>
        <div class="form-grid">
          <div class="form-row">
            <label>Base URL</label>
            <input value="${config.ollama?.base_url || ""}" readonly>
          </div>
          <div class="form-row">
            <label>Model</label>
            <input value="${config.ollama?.model || ""}" readonly>
          </div>
        </div>
      </section>
    </div>
  `;
}