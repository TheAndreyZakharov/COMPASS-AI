import { htmlEscape } from "../app.js";

const RISK_CLASS = {
  high: "risk-high",
  medium: "risk-medium",
      low: "risk-low",
};

function percent(value) {
  const numeric = Number(value);

  if (!Number.isFinite(numeric)) {
    return "—";
  }

  return `${Math.round(numeric * 100)}%`;
}

function fixed(value, digits = 3) {
  const numeric = Number(value);

  if (!Number.isFinite(numeric)) {
    return "—";
  }

  return numeric.toFixed(digits);
}

function riskBadge(risk) {
  const level = String(risk?.level || "low");
  const className = RISK_CLASS[level] || "risk-low";

  return `
    <span class="risk-badge ${className}">
      ${htmlEscape(level === "high" ? "высокий" : level === "medium" ? "средний" : "низкий")}
    </span>
  `;
}

function renderSkillList(items, emptyLabel) {
  const values = Array.isArray(items) ? items : [];

  if (!values.length) {
    return `<span class="muted">${htmlEscape(emptyLabel)}</span>`;
  }

  return values
    .map((item) => `<span class="tag">${htmlEscape(item)}</span>`)
    .join("");
}

export function renderScoreBreakdown(candidate) {
  const factors = candidate?.factors || {};

  return `
    <div class="score-breakdown">
      <div>
        <span>Оценка модели</span>
        <strong>${fixed(factors.model_score ?? candidate?.model_score)}</strong>
      </div>
      <div>
        <span>Итоговая оценка</span>
        <strong>${fixed(factors.adjusted_score ?? candidate?.score)}</strong>
      </div>
      <div>
        <span>Совпадение навыков</span>
        <strong>${percent(factors.skill_match_ratio)}</strong>
      </div>
      <div>
        <span>Качество</span>
        <strong>${percent(factors.quality_fit_score)}</strong>
      </div>
      <div>
        <span>Скорость</span>
        <strong>${percent(factors.speed_fit_score)}</strong>
      </div>
      <div>
        <span>Развитие</span>
        <strong>${percent(factors.learning_fit_score)}</strong>
      </div>
      <div>
        <span>Учет рисков</span>
        <strong>${percent(factors.risk_fit_score)}</strong>
      </div>
      <div>
        <span>Нагрузка</span>
        <strong>${percent(factors.workload_pressure)}</strong>
      </div>
    </div>
  `;
}

export function renderRiskList(candidate) {
  const risks = Array.isArray(candidate?.risks) ? candidate.risks : [];

  if (!risks.length) {
    return `<p class="muted">Риски не обнаружены.</p>`;
  }

  return `
    <div class="risk-list">
      ${risks
        .map(
          (risk) => `
            <div class="risk-item">
              ${riskBadge(risk)}
              <div>
                <strong>${htmlEscape(risk.type || "риск")}</strong>
                <p>${htmlEscape(risk.message || "")}</p>
              </div>
              <span>${fixed(risk.score)}</span>
            </div>
          `,
        )
        .join("")}
    </div>
  `;
}

export function renderRecommendationCards(recommendation, options = {}) {
  const candidates = Array.isArray(recommendation?.candidates)
    ? recommendation.candidates
    : [];
  const title = options.title || "Лучшие кандидаты";

  if (!candidates.length) {
    return `
      <section class="panel">
        <h3>${htmlEscape(title)}</h3>
        <p class="muted">Нет кандидатов для отображения.</p>
      </section>
    `;
  }

  return `
    <section class="panel">
      <div class="section-heading">
        <div>
          <h3>${htmlEscape(title)}</h3>
          <p class="muted">
            Режим: ${htmlEscape(recommendation?.recommendation_mode || "—")}
          </p>
        </div>
        <span class="pill">топ ${candidates.length}</span>
      </div>

      <div class="recommendation-card-grid">
        ${candidates
          .map(
            (candidate, index) => `
              <article class="recommendation-card">
                <div class="candidate-rank">#${index + 1}</div>
                <div class="candidate-main">
                  <div>
                    <h4>${htmlEscape(candidate.name || candidate.employee_id)}</h4>
                    <p class="muted">
                      ${htmlEscape(candidate.role || "—")}
                      · ${htmlEscape(candidate.grade || "—")}
                    </p>
                  </div>
                  <div class="candidate-score">${fixed(candidate.score)}</div>
                </div>

                ${renderScoreBreakdown(candidate)}

                <div class="skill-block">
                  <strong>Совпавшие навыки</strong>
                  <div>${renderSkillList(candidate.matched_skills, "нет")}</div>
                </div>

                <div class="skill-block">
                  <strong>Недостающие навыки</strong>
                  <div>${renderSkillList(candidate.missing_skills, "нет")}</div>
                </div>

                ${renderRiskList(candidate)}
              </article>
            `,
          )
          .join("")}
      </div>
    </section>
  `;
}
