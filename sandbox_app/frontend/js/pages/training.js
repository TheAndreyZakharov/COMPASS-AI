export const title = "Training";

export async function render(container) {
  container.innerHTML = `
    <div class="grid two">
      <section class="card">
        <h2>Training setup</h2>
        <div class="form-grid">
          <div class="form-row">
            <label for="target-mode">Target mode</label>
            <select id="target-mode">
              <option>balanced</option>
              <option>quality</option>
              <option>speed</option>
              <option>learning</option>
              <option>risk_aware</option>
            </select>
          </div>
          <div class="form-row">
            <label for="models">Models</label>
            <textarea id="models">baseline_rule_based, sgd_classifier, logistic_regression, random_forest, hist_gradient_boosting, torch_mlp</textarea>
          </div>
          <button class="primary-button" type="button" disabled>Start training</button>
        </div>
      </section>

      <section class="card">
        <h2>Training progress</h2>
        <p class="empty-state">Training API and progress events will be connected in milestone 27.13.</p>
      </section>
    </div>
  `;
}