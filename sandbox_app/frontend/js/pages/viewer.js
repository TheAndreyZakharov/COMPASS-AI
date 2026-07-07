export const title = "Data Viewer";

export async function render(container) {
  container.innerHTML = `
    <div class="grid">
      <section class="card">
        <h2>Dataset browser</h2>
        <div class="button-row">
          <button class="secondary-button" type="button" disabled>Employees</button>
          <button class="secondary-button" type="button" disabled>Tasks</button>
          <button class="secondary-button" type="button" disabled>History</button>
          <button class="secondary-button" type="button" disabled>Training pairs</button>
          <button class="secondary-button" type="button" disabled>Kanban</button>
        </div>
      </section>

      <section class="table-shell">
        <table>
          <thead>
            <tr>
              <th>Dataset</th>
              <th>Type</th>
              <th>Status</th>
              <th>Rows</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>No dataset selected</td>
              <td>Generated or imported</td>
              <td><span class="badge warn">Waiting for 27.5+</span></td>
              <td>0</td>
            </tr>
          </tbody>
        </table>
      </section>
    </div>
  `;
}