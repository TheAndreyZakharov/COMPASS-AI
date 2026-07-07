export const title = "Assignment Lab";

export async function render(container) {
  container.innerHTML = `
    <div class="grid two">
      <section class="card">
        <h2>Single task recommendation</h2>
        <div class="form-grid">
          <div class="form-row">
            <label for="recommendation-mode">Recommendation mode</label>
            <select id="recommendation-mode">
              <option>balanced</option>
              <option>best_quality</option>
              <option>fastest_delivery</option>
              <option>best_learning</option>
              <option>risk_aware</option>
            </select>
          </div>
          <div class="form-row">
            <label for="llm-explanations">LLM explanations</label>
            <select id="llm-explanations">
              <option>disabled</option>
              <option>enabled</option>
            </select>
          </div>
          <button class="primary-button" type="button" disabled>Run recommendation</button>
        </div>
      </section>

      <section class="card">
        <h2>Bulk todo assignment</h2>
        <p class="empty-state">Bulk assignment simulation will be connected in milestone 27.19.</p>
      </section>
    </div>
  `;
}