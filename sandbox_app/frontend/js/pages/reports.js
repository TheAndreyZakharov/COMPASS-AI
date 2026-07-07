export const title = "Reports";

export async function render(container) {
  container.innerHTML = `
    <div class="grid two">
      <section class="card">
        <h2>Available reports</h2>
        <p class="empty-state">Reports will appear after dataset generation, model training, and assignment simulation.</p>
      </section>

      <section class="card">
        <h2>Export formats</h2>
        <p><span class="badge">JSON</span> <span class="badge">CSV</span> <span class="badge">HTML</span></p>
      </section>
    </div>
  `;
}