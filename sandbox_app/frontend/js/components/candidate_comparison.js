import { htmlEscape } from "../app.js";

function value(value) {
  const numeric = Number(value);

  if (!Number.isFinite(numeric)) {
    return "—";
  }

  return numeric.toFixed(3);
}

function factor(candidate, key) {
  return candidate?.factors?.[key] ?? candidate?.assignment_score_details?.[key];
}

export function renderCandidateComparison(candidates, options = {}) {
  const rows = Array.isArray(candidates) ? candidates : [];
  const title = options.title || "Candidate comparison";

  if (!rows.length) {
    return `
      <section class="panel">
        <h3>${htmlEscape(title)}</h3>
        <p class="muted">Нет кандидатов для сравнения.</p>
      </section>
    `;
  }

  return `
    <section class="panel">
      <div class="section-heading">
        <div>
          <h3>${htmlEscape(title)}</h3>
          <p class="muted">Сравнение score, факторов и рисков.</p>
        </div>
      </div>

      <div class="table-scroll">
        <table class="data-table compact-table">
          <thead>
            <tr>
              <th>Rank</th>
              <th>Candidate</th>
              <th>Role</th>
              <th>Score</th>
              <th>Model</th>
              <th>Skill</th>
              <th>Quality</th>
              <th>Speed</th>
              <th>Learning</th>
              <th>Risk fit</th>
              <th>Max risk</th>
            </tr>
          </thead>
          <tbody>
            ${rows
              .map(
                (candidate, index) => `
                  <tr>
                    <td>#${index + 1}</td>
                    <td>${htmlEscape(candidate.name || candidate.employee_id)}</td>
                    <td>${htmlEscape(candidate.role || "—")}</td>
                    <td>${value(candidate.score ?? candidate.assignment_score)}</td>
                    <td>${value(candidate.model_score)}</td>
                    <td>${value(factor(candidate, "skill_match_ratio"))}</td>
                    <td>${value(factor(candidate, "quality_fit_score"))}</td>
                    <td>${value(factor(candidate, "speed_fit_score"))}</td>
                    <td>${value(factor(candidate, "learning_fit_score"))}</td>
                    <td>${value(factor(candidate, "risk_fit_score"))}</td>
                    <td>${value(candidate.risk_summary?.max_risk_score)}</td>
                  </tr>
                `,
              )
              .join("")}
          </tbody>
        </table>
      </div>
    </section>
  `;
}