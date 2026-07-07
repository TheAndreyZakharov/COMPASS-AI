import { getStatus, getSessions } from "../api.js";

export const title = "Dashboard";

export async function render(container) {
  container.innerHTML = `<div class="loading-state">Loading dashboard...</div>`;

  const [status, sessions] = await Promise.all([
    getStatus(),
    getSessions(),
  ]);

  container.innerHTML = `
    <div class="grid three">
      <article class="card metric">
        <div class="metric-value">${status.status}</div>
        <div class="metric-label">Backend status</div>
      </article>
      <article class="card metric">
        <div class="metric-value">${sessions.training_sessions.length}</div>
        <div class="metric-label">Training sessions</div>
      </article>
      <article class="card metric">
        <div class="metric-value">${sessions.assignment_sessions.length}</div>
        <div class="metric-label">Assignment sessions</div>
      </article>
    </div>

    <div class="grid two" style="margin-top: 16px;">
      <section class="card">
        <h2>Runtime</h2>
        <p><span class="badge ok">Python ${status.python}</span></p>
        <p>Platform: ${status.platform}</p>
        <p>Ollama available: ${status.ollama_available ? "yes" : "no"}</p>
      </section>

      <section class="card">
        <h2>Next workflow</h2>
        <p>Generate or import data, inspect it, train models, then run assignment simulations with optional Qwen explanations.</p>
        <div class="button-row">
          <a class="primary-button" href="#generator">Open generator</a>
          <a class="secondary-button" href="#training">Open training</a>
        </div>
      </section>
    </div>
  `;
}