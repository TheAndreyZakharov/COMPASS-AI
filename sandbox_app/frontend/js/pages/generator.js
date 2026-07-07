export const title = "Data Generator";

export async function render(container) {
  container.innerHTML = `
    <div class="grid two">
      <section class="card">
        <h2>Dataset preset</h2>
        <div class="form-grid">
          <div class="form-row">
            <label for="domain-profile">Domain profile</label>
            <select id="domain-profile">
              <option>developers</option>
              <option>designers</option>
              <option>custom</option>
            </select>
          </div>
          <div class="form-row">
            <label for="seed">Seed</label>
            <input id="seed" type="number" value="42">
          </div>
          <div class="form-row">
            <label for="employees-count">Employees count</label>
            <input id="employees-count" type="number" value="30">
          </div>
          <div class="form-row">
            <label for="tasks-count">Tasks count</label>
            <input id="tasks-count" type="number" value="1000">
          </div>
          <button class="primary-button" type="button" disabled>Generate dataset</button>
        </div>
      </section>

      <section class="card">
        <h2>Status</h2>
        <p class="empty-state">Generation API will be connected in milestone 27.7-27.10.</p>
      </section>
    </div>
  `;
}