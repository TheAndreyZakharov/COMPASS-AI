import { api } from "../api.js";
import { htmlEscape } from "../app.js";

function metricCard(title, value, subtitle) {
  return `
    <article class="card kpi soft-card">
      <span class="muted">${htmlEscape(title)}</span>
      <strong>${htmlEscape(value)}</strong>
      <small class="muted">${htmlEscape(subtitle)}</small>
    </article>
  `;
}

function stepCard(number, title, text, href, label, ready = false) {
  return `
    <article class="card step-card ${ready ? "is-ready" : ""}">
      <span class="step-number">${htmlEscape(number)}</span>
      <div>
        <h2>${htmlEscape(title)}</h2>
        <p class="muted">${htmlEscape(text)}</p>
        <a class="button ${ready ? "button-secondary" : "button-primary"}" href="${href}" data-link>
          ${htmlEscape(label)}
        </a>
      </div>
    </article>
  `;
}

export async function renderDashboard() {
  const [health, sessions, datasets, models, assignments] = await Promise.all([
    api.health(),
    api.sessions(),
    api.datasets(),
    api.modelsList(),
    api.assignmentSessions(),
  ]);

  const generatedCount = datasets.counts?.generated ?? 0;
  const importedCount = datasets.counts?.imported ?? 0;
  const trainingCount = sessions.training_sessions?.length ?? sessions.total ?? 0;
  const modelCount = models.total ?? models.models?.length ?? 0;
  const assignmentCount = assignments.total ?? assignments.assignment_sessions?.length ?? 0;

  return `
    <section class="hero-panel welcome-panel">
      <div>
        <p class="eyebrow">COMPASS AI Sandbox</p>
        <h1>Рабочий маршрут без кода</h1>
        <p>
          Создайте данные под свой домен, обучите несколько моделей и проверьте,
          кому система рекомендует назначать задачи.
        </p>
      </div>
    </section>

    <section class="grid grid-5">
      ${metricCard("Сервер", health.status === "ok" ? "Работает" : "Проверить", "локальный сервер")}
      ${metricCard("Созданные датасеты", generatedCount, "синтетические данные")}
      ${metricCard("Импортированные", importedCount, "ваши файлы")}
      ${metricCard("Модели", modelCount, "обученные алгоритмы")}
      ${metricCard("Назначения", assignmentCount, "сохраненные результаты")}
    </section>

    <section class="grid grid-3" style="margin-top: 16px;">
      ${stepCard(
        1,
        "Создайте датасет",
        generatedCount || importedCount
          ? "Данные уже есть. Можно создать новый вариант или перейти дальше."
          : "Начните с генерации синтетических данных или импорта своих таблиц.",
        "/generator",
        generatedCount || importedCount ? "Открыть генератор" : "Создать данные",
        Boolean(generatedCount || importedCount),
      )}
      ${stepCard(
        2,
        "Обучите модели",
        trainingCount
          ? "Есть сессии обучения. Можно сравнить модели или обучить новые."
          : "Выберите датасет и запустите обучение всех доступных моделей.",
        "/training",
        trainingCount ? "Открыть обучение" : "Обучить модели",
        Boolean(trainingCount),
      )}
      ${stepCard(
        3,
        "Проверьте назначения",
        assignmentCount
          ? "Есть сохраненные назначения. Можно открыть результаты или запустить новые."
          : "Выберите обученную модель и проверьте одну задачу или весь список.",
        "/assignment-lab",
        assignmentCount ? "Открыть результаты" : "Назначить задачи",
        Boolean(assignmentCount),
      )}
    </section>
  `;
}
