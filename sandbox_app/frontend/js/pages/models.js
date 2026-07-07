import { getSessions } from "../api.js";

export const title = "Models";

export async function render(container) {
  container.innerHTML = `<div class="loading-state">Loading model sessions...</div>`;

  const sessions = await getSessions();

  const rows = sessions.training_sessions.length
    ? sessions.training_sessions.map((session) => `
      <tr>
        <td>${session.id}</td>
        <td>${session.path}</td>
        <td><span class="badge ok">available</span></td>
      </tr>
    `).join("")
    : `
      <tr>
        <td>No training sessions</td>
        <td>Train models first</td>
        <td><span class="badge warn">empty</span></td>
      </tr>
    `;

  container.innerHTML = `
    <section class="table-shell">
      <table>
        <thead>
          <tr>
            <th>Session</th>
            <th>Path</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>${rows}</tbody>
      </table>
    </section>
  `;
}