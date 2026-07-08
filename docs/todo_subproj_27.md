# 27. Этап 25 — автономный локальный подпроект COMPASS AI Sandbox

Цель этапа: сделать автономную локальную песочницу внутри основного репозитория COMPASS-AI. Песочница должна жить в одной папке sandbox_app, использовать уже созданное окружение проекта .venv с Python 3.11.15, запускаться локально в браузере и не ломать основной COMPASS API.

Песочница нужна для полного цикла экспериментов: настраиваемые domain schemas, генерация реалистичных команд, задач, истории выполненных задач, больших training datasets, просмотр данных в браузере, обучение нескольких моделей, сохранение training sessions, проверка рекомендаций, массовое распределение todo-задач, отчёты, exports и русские Qwen/Ollama explanations.

Главный принцип этапа: не делать MVP, временные заглушки или случайные скрипты. Каждый подпункт должен давать рабочую часть продукта с backend, проверками, понятной структурой файлов и последующей интеграцией во frontend.

---

## 27.1. Создать автономную структуру песочницы

- [x] Создать папку sandbox_app.
- [x] Не смешивать код песочницы с основным src.
- [x] Не использовать напрямую LLM-файлы основного проекта.
- [x] Не использовать напрямую agent-файлы основного проекта.
- [x] Не ломать основной COMPASS API.
- [x] Использовать существующее окружение .venv.
- [x] Зафиксировать Python 3.11.x как целевую версию.
- [x] Создать отдельный README.md внутри sandbox_app.
- [x] Создать отдельный requirements.txt внутри sandbox_app.
- [x] Создать структуру backend, frontend, config, scripts, data, sessions, reports, logs, tests.
- [x] Создать package markers для backend-модулей.
- [x] Создать .gitkeep в пустых runtime-папках.
- [x] Добавить базовые app settings.
- [x] Добавить model presets.
- [x] Добавить feature schemas developers, designers, custom.
- [x] Проверить JSON-конфиги.
- [x] Проверить Python imports через compileall.
- [x] Добавить sandbox_app/.python-version с целевой версией 3.11.15.
- [x] Добавить изоляционные настройки, запрещающие прямой импорт main src, LLM и agents.

Папка подпроекта:

sandbox_app

Что сделано по факту:
sandbox_app создан как отдельный автономный подпроект. Внутри есть отдельные backend, frontend, config, scripts, data, training_sessions, assignment_sessions, reports, logs и tests. Базовые настройки, model presets и feature schemas сохранены в JSON. Python-пакеты размечены через __init__.py. Runtime-папки сохранены через .gitkeep. Основной COMPASS API не трогался.

Проверки:
JSON-конфиги проходят python -m json.tool.
Backend и tests проходят python -m compileall.

Ожидаемый результат:
sandbox_app существует как отдельный автономный подпроект, а не набор временных файлов.

Примерное время: 2–4 часа.
Коммит: Create autonomous sandbox app structure

---

## 27.2. Сделать локальный запуск, остановку и smoke test

- [x] Создать scripts/start.sh.
- [x] Создать scripts/stop.sh.
- [x] Создать scripts/restart.sh.
- [x] Создать scripts/smoke_test.sh.
- [x] Создать scripts/clean_tmp.sh.
- [x] Запускать приложение через активированное .venv.
- [x] Проверять, что python берётся из .venv проекта.
- [x] Запускать backend на 127.0.0.1:8601.
- [x] Сохранять PID в sandbox_app/logs/sandbox_app.pid.
- [x] Сохранять server logs в sandbox_app/logs/server.log.
- [x] Проверять занятость порта.
- [x] Давать понятные terminal messages.
- [x] Добавить Makefile targets.
- [x] Добавить игнорирование runtime logs и pid-файлов.
- [x] Проверить shell scripts через bash -n.
- [x] Проверить start, smoke test, stop, restart.
- [x] Добавить минимальный backend entrypoint для честной проверки запуска до этапа 27.3.
- [x] Добавить sandbox-clean для безопасной очистки runtime-файлов.

Команды запуска:

cd /Users/andrey/Documents/projects/COMPASS-AI
source .venv/bin/activate
bash sandbox_app/scripts/start.sh

Локальный URL:

http://127.0.0.1:8601

Makefile targets:

sandbox-start
sandbox-stop
sandbox-restart
sandbox-test
sandbox-clean

Что сделано по факту:
Приложение запускается через .venv на 127.0.0.1:8601. PID сохраняется в sandbox_app/logs/sandbox_app.pid. Логи пишутся в sandbox_app/logs/server.log. start.sh проверяет Python 3.11.x, принадлежность python к .venv, занятость порта и health endpoint. stop.sh корректно останавливает процесс и чистит PID. restart.sh делает stop плюс start. smoke_test.sh проверяет .venv, PID, /api/health и главную страницу. clean_tmp.sh безопасно чистит runtime-файлы, если сервер не запущен.

Проверки:
Shell scripts проходят bash -n.
Start, smoke test, restart, smoke test, stop проверены.
Makefile targets sandbox-start, sandbox-test, sandbox-restart, sandbox-stop, sandbox-clean добавлены.

Ожидаемый результат:
приложение запускается, останавливается, перезапускается и проверяется одной командой.

Примерное время: 2–3 часа.
Коммит: Add sandbox run scripts

---

## 27.3. Сделать production-ready FastAPI backend foundation

- [x] Создать backend/main.py.
- [x] Подключить FastAPI.
- [x] Подключить health endpoint.
- [x] Подключить API namespace.
- [x] Подключить endpoint /api/status.
- [x] Подключить endpoint /api/config.
- [x] Подключить endpoint /api/sessions.
- [x] Подключить локальный CORS только для 127.0.0.1 и localhost.
- [x] Подключить раздачу frontend из того же backend.
- [x] Подключить раздачу CSS из frontend/css.
- [x] Подключить раздачу JS из frontend/js.
- [x] Подключить раздачу assets из frontend/assets.
- [x] Сделать SPA fallback для frontend.
- [x] Сделать JSON error handler.
- [x] Сделать backend logging.
- [x] Вынести paths в backend/core/paths.py.
- [x] Вынести settings loader в backend/core/settings.py.
- [x] Вынести JSON helpers в backend/utils/json_io.py.
- [x] Проверить endpoints через terminal.
- [x] Проверить, что браузер открывает UI.
- [x] Добавить API docs на /api/docs.
- [x] Добавить frontend shell, который сразу проверяет health, config и sessions.
- [x] Добавить endpoint /api/config/settings.
- [x] Добавить endpoint /api/config/model-presets.
- [x] Добавить endpoint /api/config/feature-schemas.
- [x] Добавить endpoint /api/sessions/training.
- [x] Добавить endpoint /api/sessions/assignment.

Файлы:

sandbox_app/backend/main.py
sandbox_app/backend/api/status.py
sandbox_app/backend/api/config.py
sandbox_app/backend/api/sessions.py
sandbox_app/backend/core/paths.py
sandbox_app/backend/core/settings.py
sandbox_app/backend/core/logging.py
sandbox_app/backend/utils/json_io.py
sandbox_app/frontend/index.html
sandbox_app/frontend/css/styles.css
sandbox_app/frontend/js/app.js

Endpoints:

GET /api/health
GET /api/status
GET /api/config
GET /api/sessions

Дополнительные endpoints:

GET /api/config/settings
GET /api/config/model-presets
GET /api/config/feature-schemas
GET /api/sessions/training
GET /api/sessions/assignment
GET /api/docs

Что сделано по факту:
Backend теперь собирается через create_app, использует lifespan startup, локальный CORS, JSON error handlers, отдельные routers и отдельные core modules. Settings и model presets читаются из JSON. Feature schemas доступны через config API. Sessions API сканирует training_sessions и assignment_sessions. Frontend отдается тем же FastAPI backend без Streamlit. CSS, JS и assets раздаются отдельными static mounts. Browser routes работают через SPA fallback, а неизвестные API routes возвращают JSON error.

Проверки:
JSON-конфиги проходят python -m json.tool.
Backend проходит python -m compileall.
Shell scripts проходят bash -n.
Проверены /api/health, /api/status, /api/config, /api/sessions.
Проверены static mounts /css/styles.css и /js/app.js.
Проверен SPA fallback.
Проверен JSON error handler.
Проверено открытие UI в браузере.
Smoke test проходит.

Ожидаемый результат:
backend автономно работает, отдаёт API и frontend без Streamlit.

Примерное время: 3–5 часов.
Коммит: Add sandbox FastAPI backend

---

## 27.4. Зафиксировать data contracts песочницы

- [x] Определить формат employees.
- [x] Определить формат tasks.
- [x] Определить формат assignment_history.
- [x] Определить формат training_pairs.
- [x] Определить формат current_team.
- [x] Определить формат current_backlog.
- [x] Определить формат recommendations.
- [x] Определить формат training_session.
- [x] Определить формат assignment_session.
- [x] Определить формат dataset_metadata.
- [x] Поддержать CSV для простых таблиц.
- [x] Поддержать JSON для вложенных структур.
- [x] Поддержать Parquet для больших training datasets.
- [x] Зафиксировать required и optional поля.
- [x] Зафиксировать allowed statuses.
- [x] Зафиксировать outcome labels.
- [x] Зафиксировать recommendation candidates.
- [x] Добавить backend loader contracts.
- [x] Добавить API для просмотра contracts.
- [x] Добавить документацию contracts.
- [x] Проверить JSON и endpoints.
- [x] Добавить contracts summary endpoint.
- [x] Добавить backend validation для структуры data_contracts.json.
- [x] Добавить helper для проверки required fields у records.

Файлы:

sandbox_app/config/data_contracts/data_contracts.json
sandbox_app/backend/core/data_contracts.py
sandbox_app/backend/api/contracts.py
sandbox_app/docs/data_contracts.md

Endpoints:

GET /api/contracts
GET /api/contracts/summary
GET /api/contracts/{contract_name}

Что сделано по факту:
Data contracts зафиксированы в одном JSON-файле. Описаны employees, tasks, assignment_history, training_pairs, current_team, current_backlog, recommendations, training_session, assignment_session и dataset_metadata. Для простых таблиц предусмотрены CSV и JSON. Для больших training datasets предусмотрен Parquet. Зафиксированы task statuses, deadline statuses, outcome labels, recommendation modes, target modes и session statuses. Backend loader валидирует структуру contracts и отдаёт contracts через API. Документация добавлена в sandbox_app/docs/data_contracts.md.

Проверки:
data_contracts.json проходит python -m json.tool.
Backend проходит python -m compileall.
Проверены /api/contracts, /api/contracts/summary, /api/contracts/employees, /api/contracts/training_pairs.
Проверен JSON error handler для неизвестного contract.
Smoke test проходит.

Ожидаемый результат:
до генерации и обучения понятно, какие данные живут в системе и как они связаны.

Примерное время: 3–5 часов.
Коммит: Define sandbox data contracts

---

## 27.5. Реализовать настраиваемые feature schemas

- [x] Сделать системный профиль developers.
- [x] Сделать системный профиль designers.
- [x] Сделать полностью свободный профиль custom.
- [x] Поддержать любые domain profiles: медицина, право, продажи, дизайн, разработка, образование, операции.
- [x] Дать возможность создать профиль через API.
- [x] Дать возможность обновить профиль через API.
- [x] Дать возможность удалить несистемный профиль.
- [x] Защитить системные профили от удаления.
- [x] Дать возможность добавить employee feature.
- [x] Дать возможность добавить task feature.
- [x] Дать возможность добавить outcome feature.
- [x] Дать возможность переименовать feature.
- [x] Дать возможность удалить feature.
- [x] Поддержать numeric feature.
- [x] Поддержать categorical feature.
- [x] Поддержать boolean feature.
- [x] Поддержать text feature.
- [x] Поддержать skill_list feature.
- [x] Валидировать profile_id.
- [x] Валидировать feature names.
- [x] Валидировать feature types.
- [x] Показывать preview схемы через API.
- [x] Сохранять schemas в JSON.
- [x] Добавить документацию feature schemas.
- [x] Добавить template endpoint для быстрого создания новых domain profiles.
- [x] Добавить backend validation для feature groups.
- [x] Добавить защиту system=true только для built-in profiles developers и designers.

Файлы:

sandbox_app/config/feature_schemas/developers.json
sandbox_app/config/feature_schemas/designers.json
sandbox_app/config/feature_schemas/custom.json
sandbox_app/backend/features/schema.py
sandbox_app/backend/api/feature_schemas.py
sandbox_app/docs/feature_schemas.md

Endpoints:

GET /api/feature-schemas
GET /api/feature-schemas?preview=true
GET /api/feature-schemas/template
GET /api/feature-schemas/{profile_id}
GET /api/feature-schemas/{profile_id}?preview=true
POST /api/feature-schemas
PUT /api/feature-schemas/{profile_id}
DELETE /api/feature-schemas/{profile_id}
POST /api/feature-schemas/{profile_id}/features/{group}
PATCH /api/feature-schemas/{profile_id}/features/{group}/{feature_name}
DELETE /api/feature-schemas/{profile_id}/features/{group}/{feature_name}

Что сделано по факту:
Feature schemas стали полноценной backend-сущностью. Developers и designers являются системными профилями и защищены от удаления. Custom является свободным редактируемым профилем. Можно создавать новые domain profiles для медицины, права, продаж, дизайна, разработки, образования, операций и любых других доменов. API поддерживает создание, обновление, удаление несистемных профилей, добавление, переименование, изменение и удаление features в группах employee, task и outcome. Поддержаны numeric, categorical, boolean, text и skill_list features. Все schemas сохраняются как JSON.

Проверки:
JSON feature schemas проходят python -m json.tool.
Backend проходит python -m compileall.
Проверены list, preview, get, template endpoints.
Проверено создание medicine profile через API.
Проверено добавление, переименование и удаление feature.
Проверена защита developers от удаления.
Проверено удаление несистемного medicine profile.
Smoke test проходит.

Ожидаемый результат:
пользователь может настроить признаки под любую команду и домен, а генерация данных использует выбранную схему.

Примерное время: 6–10 часов.
Коммит: Add configurable sandbox feature schemas

---

## 27.6. Реализовать backend generator команды

- [x] Создать генератор сотрудников.
- [x] Использовать выбранный domain_profile.
- [x] Настраивать employees_count.
- [x] Настраивать roles.
- [x] Настраивать grades.
- [x] Настраивать skills.
- [x] Настраивать skill_count_per_person_min.
- [x] Настраивать skill_count_per_person_max.
- [x] Настраивать seniority distribution.
- [x] Настраивать workload.
- [x] Настраивать fatigue.
- [x] Настраивать learning goals.
- [x] Генерировать availability_score.
- [x] Генерировать avg_completion_speed.
- [x] Генерировать avg_quality_score.
- [x] Генерировать deadline_reliability.
- [x] Генерировать mentor_level.
- [x] Генерировать custom employee features из schema.
- [x] Поддержать seed.
- [x] Сохранять employees.json.
- [x] Сохранять employees.csv.
- [x] Сохранять team_metadata.json.
- [x] Добавить endpoint генерации команды.
- [x] Проверить developers, designers и custom domain.
- [x] Добавить validation generated employees через data contracts.
- [x] Добавить защиту от случайного overwrite dataset_id.
- [x] Добавить игнорирование generated runtime datasets в gitignore.

Файлы:

sandbox_app/backend/data_generation/employees.py
sandbox_app/backend/api/generate_team.py

Endpoint:

POST /api/generate/team

Результаты:

sandbox_app/data/generated/<dataset_id>/employees.csv
sandbox_app/data/generated/<dataset_id>/employees.json
sandbox_app/data/generated/<dataset_id>/team_metadata.json

Что сделано по факту:
Генератор команды создаёт реалистичных сотрудников по выбранному domain_profile. Используются roles, grades, skills и employee feature definitions из feature schema. Настраиваются employees_count, seed, роли, грейды, навыки, распределение seniority, диапазоны workload, fatigue и availability, а также learning goals. Генерируются availability_score, current_workload, fatigue_score, avg_completion_speed, avg_quality_score, deadline_reliability, mentor_level и custom_features. Результаты сохраняются в employees.json, employees.csv и team_metadata.json. Endpoint возвращает dataset_id, paths, metadata и preview.

Проверки:
Backend проходит python -m compileall.
JSON-конфиги проходят python -m json.tool.
Проверена генерация developers.
Проверена генерация designers.
Проверена генерация custom.
Проверено сохранение employees.json, employees.csv и team_metadata.json.
Проверено наличие domain_profile в metadata.
Проверено наличие custom_features в employees.json.
Smoke test проходит.

Ожидаемый результат:
можно сгенерировать реалистичную команду с ролями, навыками, загрузкой, усталостью и характеристиками.

Примерное время: 6–10 часов.
Коммит: Add sandbox team generator

---

## 27.7. Реализовать backend generator задач и backlog

- [x] Создать генератор задач.
- [x] Использовать выбранный domain_profile.
- [x] Настраивать tasks_count.
- [x] Настраивать projects_count.
- [x] Настраивать task_types.
- [x] Настраивать priorities.
- [x] Настраивать complexity.
- [x] Настраивать deadline_days.
- [x] Настраивать estimated_hours.
- [x] Настраивать required skills.
- [x] Настраивать dependencies.
- [x] Настраивать skill_mismatch_probability.
- [x] Генерировать статусы todo, in_progress, review, done, blocked, failed.
- [x] Генерировать backlog из задач в статусе todo.
- [x] Генерировать kanban summary.
- [x] Генерировать custom task features из schema.
- [x] Поддержать seed.
- [x] Сохранять tasks.json.
- [x] Сохранять tasks.csv.
- [x] Сохранять backlog.json.
- [x] Сохранять backlog.csv.
- [x] Сохранять task_metadata.json.
- [x] Добавить endpoint генерации задач.
- [x] Проверить developers, designers и custom domain.
- [x] Добавить validation generated tasks через data contracts.
- [x] Добавить защиту от случайного overwrite task-файлов.
- [x] Добавить pytest smoke test генератора задач.

Файлы:

sandbox_app/backend/data_generation/tasks.py
sandbox_app/backend/data_generation/backlog.py
sandbox_app/backend/api/generate_tasks.py
sandbox_app/tests/test_task_generator.py

Endpoint:

POST /api/generate/tasks

Результаты:

sandbox_app/data/generated/<dataset_id>/tasks.csv
sandbox_app/data/generated/<dataset_id>/tasks.json
sandbox_app/data/generated/<dataset_id>/backlog.csv
sandbox_app/data/generated/<dataset_id>/backlog.json
sandbox_app/data/generated/<dataset_id>/task_metadata.json

Что сделано по факту:
Генератор задач создаёт реалистичный набор tasks по выбранному domain_profile. Используются task_types, skills и task feature definitions из feature schema. Настраиваются tasks_count, projects_count, task_types, priorities, complexity, estimated_hours, deadline_days, required skills, dependencies, skill_mismatch_probability, status distribution и priority distribution. Генерируются статусы todo, in_progress, review, done, blocked и failed. Backlog формируется только из todo задач. Kanban summary сохраняет counts по статусам, приоритетам и проектам. Custom task features генерируются из выбранной schema. Результаты сохраняются в tasks.json, tasks.csv, backlog.json, backlog.csv и task_metadata.json.

Проверки:
Backend проходит python -m compileall.
JSON-конфиги проходят python -m json.tool.
Pytest smoke test генератора задач проходит.
Проверена генерация developers.
Проверена генерация designers.
Проверена генерация custom.
Проверено сохранение tasks.json, tasks.csv, backlog.json, backlog.csv и task_metadata.json.
Проверено, что backlog содержит только todo задачи.
Проверено наличие kanban_summary в metadata.
Проверено наличие custom_features в tasks.
Проверена защита от overwrite.
Smoke test проходит.

Ожидаемый результат:
можно сгенерировать большой backlog задач, похожий на реальный рабочий поток команды.

Примерное время: 6–10 часов.
Коммит: Add sandbox task generator

---

## 27.8. Реализовать backend generator истории выполненных задач

- [x] Создать outcome engine.
- [x] Создать generator assignment_history.
- [x] Поддержать employees из payload.
- [x] Поддержать tasks из payload.
- [x] Поддержать employees из generated dataset.
- [x] Поддержать tasks из generated dataset.
- [x] Настраивать history_depth_per_employee.
- [x] Настраивать good_outcome_share.
- [x] Настраивать bad_outcome_share.
- [x] Настраивать late_outcome_share.
- [x] Настраивать failed_outcome_share.
- [x] Настраивать rework_probability.
- [x] Настраивать overload_penalty_strength.
- [x] Настраивать fatigue_penalty_strength.
- [x] Настраивать skill_match_bonus_strength.
- [x] Настраивать learning_task_share.
- [x] Учитывать skill match.
- [x] Учитывать workload.
- [x] Учитывать fatigue.
- [x] Учитывать complexity.
- [x] Учитывать grade.
- [x] Учитывать learning goals.
- [x] Генерировать planned_hours.
- [x] Генерировать actual_hours.
- [x] Генерировать quality_score.
- [x] Генерировать deadline_status.
- [x] Генерировать outcome_label.
- [x] Генерировать was_rework_needed.
- [x] Генерировать feedback_score.
- [x] Сохранять assignment_history.json.
- [x] Сохранять assignment_history.csv.
- [x] Сохранять history_metadata.json.
- [x] Добавить endpoint генерации истории.
- [x] Добавить validation generated assignment_history через data contracts.
- [x] Добавить защиту от случайного overwrite history-файлов.
- [x] Добавить pytest smoke test генератора истории.

Файлы:

sandbox_app/backend/data_generation/outcomes.py
sandbox_app/backend/data_generation/history.py
sandbox_app/backend/api/generate_history.py
sandbox_app/tests/test_history_generator.py

Endpoint:

POST /api/generate/history

Результаты:

sandbox_app/data/generated/<dataset_id>/assignment_history.csv
sandbox_app/data/generated/<dataset_id>/assignment_history.json
sandbox_app/data/generated/<dataset_id>/history_metadata.json

Что сделано по факту:
Outcome engine рассчитывает качество выполнения, риск дедлайна, planned_hours, actual_hours, deadline_status, outcome_label, rework и feedback_score. Генератор истории поддерживает employees и tasks напрямую из payload, а также загрузку employees.json и tasks.json из generated dataset. На outcome влияют skill match, workload, fatigue, complexity, grade и learning goals. Настраиваются history_depth_per_employee, outcome shares, penalties, rework probability и learning_task_share. История сохраняется в assignment_history.json, assignment_history.csv и history_metadata.json. Endpoint возвращает dataset_id, paths, metadata и preview.

Проверки:
Backend проходит python -m compileall.
JSON-конфиги проходят python -m json.tool.
Pytest smoke test генератора истории проходит.
Проверена генерация истории из generated dataset после генерации team и tasks.
Проверено сохранение assignment_history.json, assignment_history.csv и history_metadata.json.
Проверено наличие required outcome fields.
Проверено наличие quality_summary и outcome_counts в metadata.
Проверена защита от overwrite.
Smoke test проходит.

Ожидаемый результат:
у каждого сотрудника есть реалистичная история выполненных задач, пригодная для обучения моделей.

Примерное время: 8–14 часов.
Коммит: Add sandbox assignment history generator

---

## 27.9. Реализовать backend full dataset generator одной кнопкой

- [x] Сделать режим small_preview.
- [x] Сделать режим medium_validation.
- [x] Сделать режим large_training.
- [x] Сделать режим huge_training.
- [x] Настраивать employees_count.
- [x] Настраивать tasks_count.
- [x] Настраивать history_depth_per_employee.
- [x] Настраивать target_pairs.
- [x] Настраивать candidates_per_task.
- [x] Генерировать employees.
- [x] Генерировать tasks.
- [x] Генерировать assignment_history.
- [x] Генерировать training pairs task-employee.
- [x] Добавлять positive examples.
- [x] Добавлять negative examples.
- [x] Балансировать классы.
- [x] Сохранять training_pairs.parquet.
- [x] Сохранять dataset_metadata.json.
- [x] Сохранять generation_report.json.
- [x] Добавить защиту huge generation через confirm_huge_generation.
- [x] Поддержать custom domain profiles.
- [x] Добавить endpoint генерации полного dataset.
- [x] Добавить scoring engine для task-employee pairs.
- [x] Добавить train, validation и test split для training_pairs.
- [x] Добавить pytest smoke test полного dataset generator.

Файлы:

sandbox_app/backend/data_generation/training_pairs.py
sandbox_app/backend/data_generation/dataset.py
sandbox_app/backend/api/generate_dataset.py
sandbox_app/tests/test_full_dataset_generator.py

Endpoint:

POST /api/generate/dataset

Режимы:

small_preview: 10 people, 100 tasks, 1 000 pairs
medium_validation: 30 people, 1 000 tasks, 30 000 pairs
large_training: 100 people, 10 000 tasks, 1 000 000 pairs
huge_training: custom limits with explicit confirmation

Результаты:

sandbox_app/data/generated/<dataset_id>/employees.csv
sandbox_app/data/generated/<dataset_id>/employees.json
sandbox_app/data/generated/<dataset_id>/tasks.csv
sandbox_app/data/generated/<dataset_id>/tasks.json
sandbox_app/data/generated/<dataset_id>/assignment_history.csv
sandbox_app/data/generated/<dataset_id>/assignment_history.json
sandbox_app/data/generated/<dataset_id>/training_pairs.parquet
sandbox_app/data/generated/<dataset_id>/dataset_metadata.json
sandbox_app/data/generated/<dataset_id>/generation_report.json

Что сделано по факту:
Full dataset generator одной командой запускает генерацию команды, задач, backlog, истории выполненных задач и training pairs. Поддержаны режимы small_preview, medium_validation, large_training и huge_training. Huge generation защищён обязательным confirm_huge_generation. Training pairs строятся как task-employee candidates, содержат positive и negative examples, target_score, target_mode, candidate_rank_hint и split. Классы балансируются. Training pairs сохраняются в Parquet. Dataset metadata и generation report сохраняются рядом с dataset.

Проверки:
Backend проходит python -m compileall.
JSON-конфиги проходят python -m json.tool.
Pytest smoke test полного dataset generator проходит.
Проверен endpoint POST /api/generate/dataset.
Проверено создание employees, tasks, assignment_history, training_pairs.parquet, dataset_metadata.json и generation_report.json.
Проверены metadata counts.
Проверено чтение training_pairs.parquet.
Проверено наличие positive и negative labels.
Проверена защита huge generation.
Проверена защита overwrite.
Smoke test проходит.

Ожидаемый результат:
одной кнопкой можно создать полный training dataset любого нужного размера.

Примерное время: 8–14 часов.
Коммит: Add sandbox training dataset generator

---

## 27.10. Сделать backend Data Viewer API

- [x] Показывать список generated datasets.
- [x] Показывать список imported datasets.
- [x] Читать JSON tables.
- [x] Читать CSV tables.
- [x] Читать Parquet training pairs.
- [x] Отдавать dataset summary.
- [x] Отдавать employees table.
- [x] Отдавать tasks table.
- [x] Отдавать assignment_history table.
- [x] Отдавать training_pairs table с пагинацией.
- [x] Поддержать page и page_size.
- [x] Поддержать search.
- [x] Поддержать фильтры по status, role, grade, project_id, priority.
- [x] Отдавать employee profile.
- [x] Отдавать task profile.
- [x] Отдавать employee history.
- [x] Отдавать kanban board.
- [x] Отдавать summary counts.
- [x] Добавить backend validation dataset_id и table_name.
- [x] Добавить поддержку dataset_kind generated и imported.
- [x] Добавить pytest smoke test Data Viewer API helpers.

Файл:

sandbox_app/backend/api/data_viewer.py
sandbox_app/tests/test_data_viewer_api.py

Endpoints:

GET /api/data-viewer/datasets
GET /api/data-viewer/datasets/{dataset_id}/summary
GET /api/data-viewer/datasets/{dataset_id}/{table_name}
GET /api/data-viewer/datasets/{dataset_id}/employees/{employee_id}
GET /api/data-viewer/datasets/{dataset_id}/tasks/{task_id}
GET /api/data-viewer/datasets/{dataset_id}/employees/{employee_id}/history
GET /api/data-viewer/datasets/{dataset_id}/kanban

Что сделано по факту:
Data Viewer API читает generated и imported datasets. Поддержаны JSON, CSV и Parquet tables. Employees, tasks, assignment_history и training_pairs отдаются через единый table endpoint с pagination, search и фильтрами. Dataset summary показывает metadata, available tables и summary counts. Employee profile, task profile, employee history и kanban board отдаются отдельными endpoints. Training pairs читаются из Parquet. Для dataset_id и table_name добавлена backend validation.

Проверки:
Backend проходит python -m compileall.
JSON-конфиги проходят python -m json.tool.
Pytest smoke test Data Viewer API helpers проходит.
Если ruff установлен, sandbox_app проходит ruff check.
Проверен endpoint списка datasets.
Проверен dataset summary.
Проверены employees, tasks, assignment_history и training_pairs tables.
Проверены pagination, search и status filter.
Проверены employee profile, task profile и employee history.
Проверен kanban endpoint.
Smoke test проходит.

Ожидаемый результат:
backend отдаёт все данные для удобного просмотра без ручного открытия CSV.

Примерное время: 4–6 часов.
Коммит: Add sandbox data viewer API

---

## 27.11. Сделать frontend shell на HTML/CSS/Vanilla JS

- [x] Создать frontend/index.html.
- [x] Создать общий CSS.
- [x] Создать общий JS app router.
- [x] Создать API client.
- [x] Сделать sidebar navigation.
- [x] Сделать topbar.
- [x] Сделать backend status indicator.
- [x] Сделать refresh button.
- [x] Сделать страницы Dashboard, Data Generator, Data Viewer, Training, Models, Assignment Lab, Reports, Settings.
- [x] Не использовать Streamlit.
- [x] Не оставлять заглушки там, где backend уже готов.
- [x] Все готовые backend endpoints подключать сразу к UI.
- [x] Проверить browser routing.
- [x] Проверить browser hard refresh.
- [x] Проверить CSS и JS static mounts.
- [x] Добавить live Dashboard на health, status, config, sessions, contracts, schemas и datasets.
- [x] Добавить рабочий JSON-based Data Generator для уже готовых endpoints.
- [x] Добавить Data Viewer shell с datasets, table loading, summary и kanban.
- [x] Добавить страницы будущих этапов с подключением к уже доступным backend данным.

Файлы:

sandbox_app/frontend/index.html
sandbox_app/frontend/css/styles.css
sandbox_app/frontend/js/api.js
sandbox_app/frontend/js/app.js
sandbox_app/frontend/js/pages/dashboard.js
sandbox_app/frontend/js/pages/generator.js
sandbox_app/frontend/js/pages/viewer.js
sandbox_app/frontend/js/pages/training.js
sandbox_app/frontend/js/pages/models.js
sandbox_app/frontend/js/pages/assignment_lab.js
sandbox_app/frontend/js/pages/reports.js
sandbox_app/frontend/js/pages/settings.js

Что сделано по факту:
Frontend теперь работает как локальное browser-приложение на HTML, CSS и Vanilla JS без Streamlit. Добавлены sidebar navigation, topbar, backend status indicator, refresh button, SPA router и API client. Dashboard показывает live backend данные. Data Generator подключён к готовым endpoints генерации dataset, team, tasks и history через JSON payload. Data Viewer подключён к datasets, summary, table endpoint и kanban. Training, Models, Assignment Lab, Reports и Settings уже имеют маршруты и показывают доступные backend данные, ожидая следующих backend этапов.

Проверки:
Backend проходит python -m compileall.
JSON-конфиги проходят python -m json.tool.
Если Node.js установлен, JS files проходят node --check.
Если ruff установлен, sandbox_app проходит ruff check.
Проверена главная страница.
Проверены CSS и JS static mounts.
Проверен browser fallback для dashboard, generator и viewer routes.
Проверены backend endpoints, которые использует UI.
Smoke test проходит.

Ожидаемый результат:
песочница открывается как нормальное локальное web-приложение в браузере.

Примерное время: 6–10 часов.
Коммит: Add sandbox browser UI

---

## 27.12. Подключить frontend Data Generator

- [x] Подключить форму генерации full dataset к /api/generate/dataset.
- [x] Подключить генерацию команды к /api/generate/team.
- [x] Подключить генерацию задач к /api/generate/tasks.
- [x] Подключить генерацию истории к /api/generate/history.
- [x] Сделать выбор domain_profile.
- [x] Сделать ввод seed.
- [x] Сделать выбор dataset mode.
- [x] Сделать поля employees_count, tasks_count, target_pairs, history_depth_per_employee.
- [x] Сделать confirm_huge_generation.
- [x] Показывать loading state.
- [x] Показывать error state.
- [x] Показывать dataset_id после генерации.
- [x] Показывать dataset_dir после генерации.
- [x] Показывать counts: employees, tasks, history, training_pairs.
- [x] Добавить переход в Data Viewer после генерации.
- [x] Проверить генерацию через браузер.
- [x] Добавить запуск отдельных генераторов team, tasks и history.
- [x] Добавить preview payload для проверки настроек перед запуском.
- [x] Добавить автоподстановку последнего dataset_id.

Файл:

sandbox_app/frontend/js/pages/generator.js
sandbox_app/frontend/css/styles.css

Что сделано по факту:
Страница Data Generator теперь работает как полноценная форма, а не JSON-заглушка. Пользователь выбирает domain_profile, seed, dataset_mode, target_mode и задаёт employees_count, tasks_count, projects_count, history_depth_per_employee, target_pairs и candidates_per_task. Для huge_training есть отдельный confirm_huge_generation. Можно запускать full dataset, team, tasks и history через готовые backend endpoints. После генерации UI показывает dataset_id, dataset_dir, counts и полный response JSON. Последний dataset_id сохраняется и используется для перехода в Data Viewer.

Проверки:
Backend проходит python -m compileall.
JSON-конфиги проходят python -m json.tool.
Если Node.js установлен, generator.js, api.js и app.js проходят node --check.
Если ruff установлен, sandbox_app проходит ruff check.
Проверена страница /generator.
Проверена отдача нового generator.js.
Проверены CSS additions.
Проверены backend endpoints, которые использует форма.
Проверена генерация full dataset payload из UI-формы.
Проверено появление dataset в Data Viewer API.
Проверены metadata counts.
Smoke test проходит.

Ожидаемый результат:
пользователь может в браузере одной кнопкой создать полный dataset и сразу открыть его в Data Viewer.

Примерное время: 4–6 часов.
Коммит: Connect sandbox generator UI

---

## 27.13. Подключить frontend Data Viewer

- [x] Сделать страницу Data Viewer.
- [x] Показывать список generated datasets.
- [x] Показывать список imported datasets.
- [x] Показывать таблицу employees.
- [x] Показывать таблицу tasks.
- [x] Показывать таблицу assignment_history.
- [x] Показывать таблицу training_pairs с пагинацией.
- [x] Показывать карточки summary.
- [x] Показывать простые summary charts.
- [x] Показывать kanban board.
- [x] Добавить фильтры.
- [x] Добавить search.
- [x] Добавить pagination controls.
- [x] Сделать frontend table component.
- [x] Сделать frontend kanban component.
- [x] Сделать frontend charts component.
- [x] Проверить Data Viewer в браузере на реальном generated dataset.
- [x] Добавить переключение tables employees, tasks, assignment_history и training_pairs.
- [x] Добавить refresh datasets.
- [x] Добавить clear filters.
- [x] Добавить сохранение последнего выбранного dataset_id.

Файлы:

sandbox_app/frontend/js/pages/viewer.js
sandbox_app/frontend/js/components/table.js
sandbox_app/frontend/js/components/kanban.js
sandbox_app/frontend/js/components/charts.js
sandbox_app/frontend/css/styles.css

Что сделано по факту:
Data Viewer стал полноценной frontend-страницей. UI показывает generated и imported datasets, summary cards, простые charts, таблицы employees, tasks, assignment_history и training_pairs, pagination controls, search, фильтры status, role, grade, project_id и priority, а также kanban board. Таблица, kanban и charts вынесены в отдельные frontend components. Последний выбранный dataset_id сохраняется и используется при переходе из Data Generator.

Проверки:
Backend проходит python -m compileall.
JSON-конфиги проходят python -m json.tool.
Если Node.js установлен, viewer.js и components проходят node --check.
Если ruff установлен, sandbox_app проходит ruff check.
Проверена страница /viewer.
Проверена отдача viewer.js.
Проверена отдача table, kanban и charts components.
Проверены CSS additions.
Проверен реальный generated dataset.
Проверены datasets, summary, employees, tasks, training_pairs и kanban endpoints.
Проверены pagination, search и filters через Data Viewer API.
Smoke test проходит.

Ожидаемый результат:
пользователь может изучать сгенерированные данные глазами, без ручного открытия CSV.

Примерное время: 6–10 часов.
Коммит: Add sandbox data viewer

---

## 27.14. Реализовать импорт внешних datasets

- [x] Поддержать CSV import.
- [x] Поддержать JSON import.
- [x] Поддержать Parquet import.
- [x] Импортировать employees.
- [x] Импортировать tasks.
- [x] Импортировать assignment_history.
- [x] Импортировать training_pairs.
- [x] Проверять required fields по data contracts.
- [x] Показывать schema errors.
- [x] Показывать warnings.
- [x] Показывать preview.
- [x] Не перезаписывать imported dataset без подтверждения.
- [x] Сохранять imported dataset отдельно.
- [x] Разрешить использовать imported dataset в training.
- [x] Добавить backend supported tables endpoint.
- [x] Добавить frontend Import Data страницу.
- [x] Подключить imported datasets к Data Viewer через существующий API.
- [x] Добавить pytest smoke test importers.

Файлы:

sandbox_app/backend/api/import_data.py
sandbox_app/backend/utils/importers.py
sandbox_app/backend/utils/validation.py
sandbox_app/frontend/js/pages/import_data.js
sandbox_app/frontend/js/api.js
sandbox_app/frontend/js/app.js
sandbox_app/frontend/index.html
sandbox_app/frontend/css/styles.css
sandbox_app/tests/test_importers.py

Папка:

sandbox_app/data/imported

Endpoints:

GET /api/import-data/supported-tables
POST /api/import-data/preview
POST /api/import-data/datasets

Что сделано по факту:
Импорт внешних datasets поддерживает CSV, JSON и Parquet. Employees, tasks и assignment_history сохраняются как JSON и CSV. Training pairs сохраняются как Parquet. Перед сохранением records проходят required fields validation через data contracts с fallback validation. Preview показывает rows, columns, warnings, validation errors и первые records. Imported datasets сохраняются отдельно в sandbox_app/data/imported и видны через Data Viewer. Перезапись защищена overwrite=true. Frontend получил страницу Import Data с выбором файлов, preview, import result, schema errors, warnings и переходом в Data Viewer.

Проверки:
Backend проходит python -m compileall.
JSON-конфиги проходят python -m json.tool.
Pytest smoke test importers проходит.
Если Node.js установлен, import_data.js, api.js и app.js проходят node --check.
Если ruff установлен, sandbox_app проходит ruff check.
Проверен supported tables endpoint.
Проверен preview endpoint.
Проверен import dataset endpoint.
Проверено сохранение imported dataset.
Проверено чтение imported dataset через Data Viewer API.
Проверены employees и training_pairs imported tables.
Проверена страница /import-data.
Smoke test проходит.

Ожидаемый результат:
песочница работает не только с синтетикой, но и с внешними датасетами.

Примерное время: 8–12 часов.
Коммит: Add sandbox dataset import

---

## 27.15. Реализовать feature builder

- [ ] Создать отдельный feature builder песочницы.
- [ ] Не использовать напрямую основной feature pipeline.
- [ ] Поддержать employees.
- [ ] Поддержать tasks.
- [ ] Поддержать assignment_history.
- [ ] Поддержать training_pairs.
- [ ] Поддержать custom employee features.
- [ ] Поддержать custom task features.
- [ ] Поддержать skill vectors.
- [ ] Поддержать pair features.
- [ ] Поддержать workload features.
- [ ] Поддержать fatigue features.
- [ ] Поддержать learning potential features.
- [ ] Поддержать target modes quality, speed, balanced, learning, risk_aware.
- [ ] Сохранять features.parquet.
- [ ] Сохранять targets.parquet.
- [ ] Сохранять feature_metadata.json.
- [ ] Добавить endpoint build features.
- [ ] Показывать feature dimensions в UI.

Файлы:

```text
sandbox_app/backend/features/build_features.py
sandbox_app/backend/features/skill_vectorizer.py
sandbox_app/backend/features/custom_features.py
sandbox_app/backend/features/pair_features.py
sandbox_app/backend/features/targets.py
sandbox_app/backend/api/features.py
```

Результаты:

```text
sandbox_app/data/generated/<dataset_id>/features/features.parquet
sandbox_app/data/generated/<dataset_id>/features/targets.parquet
sandbox_app/data/generated/<dataset_id>/features/feature_metadata.json
```

**Ожидаемый результат:** песочница превращает generated/imported dataset в обучающие признаки для моделей.

**Примерное время:** 10–16 часов.  
**Коммит:** `Add sandbox feature builder`

---

## 27.16. Реализовать multi-model training backend

- [ ] Реализовать baseline rule-based model.
- [ ] Реализовать SGD Classifier.
- [ ] Реализовать Logistic Regression.
- [ ] Реализовать Random Forest.
- [ ] Реализовать HistGradientBoosting.
- [ ] Реализовать PyTorch MLP.
- [ ] Настраивать train/validation/test split.
- [ ] Настраивать random seed.
- [ ] Настраивать model params.
- [ ] Настраивать target mode.
- [ ] Обучать одну или несколько моделей за запуск.
- [ ] Считать metrics.
- [ ] Сохранять predictions.
- [ ] Сохранять model artifacts.
- [ ] Сохранять общий training session.
- [ ] Добавить endpoint запуска обучения.
- [ ] Добавить endpoint списка training sessions.
- [ ] Добавить endpoint деталей training session.

Файлы:

```text
sandbox_app/backend/training/train_session.py
sandbox_app/backend/training/sklearn_models.py
sandbox_app/backend/training/torch_model.py
sandbox_app/backend/training/baseline.py
sandbox_app/backend/training/evaluate.py
sandbox_app/backend/api/training.py
```

Модели:

```text
baseline_rule_based
sgd_classifier
logistic_regression
random_forest
hist_gradient_boosting
torch_mlp
```

Метрики:

```text
roc_auc
f1
precision
recall
accuracy
log_loss
mae_for_score
top_1_accuracy
top_3_accuracy
```

**Ожидаемый результат:** можно обучить несколько разных моделей на одном dataset и сравнить их качество.

**Примерное время:** 14–24 часа.  
**Коммит:** `Add sandbox multi-model training`

---

## 27.17. Сделать формат training sessions и model artifacts

- [ ] При каждом обучении создавать отдельную training session.
- [ ] Называть session по времени и short id.
- [ ] Сохранять session_config.json.
- [ ] Сохранять dataset_metadata.json.
- [ ] Сохранять feature_metadata.json.
- [ ] Сохранять session_summary.json.
- [ ] Сохранять comparison_metrics.csv.
- [ ] Сохранять comparison_metrics.json.
- [ ] Для каждой модели создавать отдельную подпапку.
- [ ] Сохранять sklearn models в joblib.
- [ ] Сохранять PyTorch model в pt.
- [ ] Сохранять predictions.parquet.
- [ ] Сохранять metrics.json.
- [ ] Сохранять export_validation.json.
- [ ] Показывать training sessions в UI.

Структура:

```text
sandbox_app/training_sessions/
└── 2026-07-06_14-30-22_ab12cd/
    ├── session_config.json
    ├── dataset_metadata.json
    ├── feature_metadata.json
    ├── session_summary.json
    ├── comparison_metrics.csv
    ├── comparison_metrics.json
    └── models/
        ├── random_forest/
        ├── sgd_classifier/
        └── torch_mlp/
```

**Ожидаемый результат:** каждое обучение воспроизводимо и сохраняется как отдельная session.

**Примерное время:** 6–10 часов.  
**Коммит:** `Add sandbox training sessions`

---

## 27.18. Реализовать training plots и reports

- [ ] Строить loss curve для PyTorch.
- [ ] Строить learning curve где применимо.
- [ ] Строить ROC curve.
- [ ] Строить precision-recall curve.
- [ ] Строить confusion matrix.
- [ ] Строить feature importance.
- [ ] Строить model comparison chart.
- [ ] Строить score distribution.
- [ ] Строить calibration plot если применимо.
- [ ] Сохранять графики PNG.
- [ ] Показывать графики в UI.
- [ ] Генерировать training_report.html.
- [ ] Добавить reports API.

Файлы:

```text
sandbox_app/backend/reports/training_plots.py
sandbox_app/backend/reports/training_report.py
sandbox_app/backend/api/reports.py
```

Результаты:

```text
loss_curve.png
roc_curve.png
precision_recall_curve.png
confusion_matrix.png
feature_importance.png
model_comparison.png
training_report.html
```

**Ожидаемый результат:** после обучения остаются модели, метрики, predictions и понятные графики.

**Примерное время:** 8–12 часов.  
**Коммит:** `Add sandbox training reports`

---

## 27.19. Реализовать model export

- [ ] Поддержать joblib для sklearn моделей.
- [ ] Поддержать pt для PyTorch модели.
- [ ] Поддержать optional ONNX export.
- [ ] Не делать ONNX обязательным для всей песочницы.
- [ ] Проверять inference после сохранения.
- [ ] Сравнивать output до и после export.
- [ ] Сохранять model_metadata.json.
- [ ] Сохранять export_validation.json.
- [ ] Показывать validation status в UI.
- [ ] Показывать список доступных моделей.

Файлы:

```text
sandbox_app/backend/training/export_models.py
sandbox_app/backend/inference/model_loader.py
sandbox_app/backend/inference/onnx_runtime.py
sandbox_app/backend/api/models.py
```

Форматы:

```text
model.joblib
model.pt
model.onnx
model_metadata.json
export_validation.json
```

**Ожидаемый результат:** модели всегда сохраняются, а ONNX доступен как дополнительный переносимый export.

**Примерное время:** 6–10 часов.  
**Коммит:** `Add sandbox model export`

---

## 27.20. Подключить frontend Training и Models

- [ ] Сделать страницу Training рабочей.
- [ ] Выбирать generated/imported dataset.
- [ ] Выбирать target mode.
- [ ] Выбирать models.
- [ ] Настраивать split.
- [ ] Настраивать seed.
- [ ] Настраивать базовые model params.
- [ ] Запускать training через API.
- [ ] Показывать progress/status.
- [ ] Показывать metrics.
- [ ] Показывать comparison table.
- [ ] Показывать графики.
- [ ] Сделать страницу Models рабочей.
- [ ] Показывать training sessions.
- [ ] Показывать model artifacts.
- [ ] Показывать export status.

Файлы:

```text
sandbox_app/frontend/js/pages/training.js
sandbox_app/frontend/js/pages/models.js
sandbox_app/frontend/js/components/training_metrics.js
sandbox_app/frontend/js/components/training_plots.js
```

**Ожидаемый результат:** пользователь может обучать и сравнивать модели из браузера.

**Примерное время:** 8–12 часов.  
**Коммит:** `Add sandbox training UI`

---

## 27.21. Реализовать test team generator

- [ ] Создать generator отдельной текущей команды.
- [ ] Генерировать team.json.
- [ ] Генерировать active_tasks.json.
- [ ] Генерировать history.json.
- [ ] Генерировать metadata.json.
- [ ] Настраивать people count.
- [ ] Настраивать roles.
- [ ] Настраивать grades.
- [ ] Настраивать current workload.
- [ ] Настраивать fatigue.
- [ ] Настраивать availability.
- [ ] Настраивать history depth.
- [ ] Настраивать learning goals.
- [ ] Настраивать current active tasks.
- [ ] Сохранять test case.
- [ ] Загружать test case из файла.
- [ ] Показывать test case в UI.

Файлы:

```text
sandbox_app/backend/data_generation/test_team.py
sandbox_app/backend/api/test_cases.py
sandbox_app/frontend/js/pages/assignment_lab.js
```

Папка:

```text
sandbox_app/data/test_cases
```

**Ожидаемый результат:** можно создать отдельную реалистичную команду для проверки обученных моделей.

**Примерное время:** 6–10 часов.  
**Коммит:** `Add sandbox test team generator`

---

## 27.22. Реализовать single task recommendation

- [ ] Выбирать saved model.
- [ ] Выбирать test case.
- [ ] Выбирать task.
- [ ] Выбирать recommendation mode.
- [ ] Строить пары task-employee.
- [ ] Прогонять пары через выбранную модель.
- [ ] Получать top candidates.
- [ ] Показывать top-1.
- [ ] Показывать top-3.
- [ ] Показывать score.
- [ ] Показывать factors.
- [ ] Показывать risks.
- [ ] Поддержать режимы best_quality, fastest_delivery, best_learning, balanced, risk_aware.
- [ ] Сохранять recommendation result.

Файлы:

```text
sandbox_app/backend/inference/recommend.py
sandbox_app/backend/inference/scoring.py
sandbox_app/backend/inference/risk_factors.py
sandbox_app/backend/api/recommendations.py
```

**Ожидаемый результат:** можно проверить, кому модель отдаст конкретную задачу и почему.

**Примерное время:** 8–12 часов.  
**Коммит:** `Add sandbox single task recommendation`

---

## 27.23. Реализовать bulk assignment simulation

- [ ] Выбирать saved model.
- [ ] Выбирать test case.
- [ ] Брать все todo задачи.
- [ ] Настраивать assignment mode.
- [ ] Настраивать top_k.
- [ ] Настраивать max workload per person.
- [ ] Настраивать fairness penalty.
- [ ] Настраивать fatigue penalty.
- [ ] Настраивать learning bonus.
- [ ] Распределять задачи пачкой.
- [ ] Обновлять прогнозную загрузку после каждого назначения.
- [ ] Не назначать всё одному сильному человеку.
- [ ] Показывать assigned tasks.
- [ ] Показывать unassigned tasks.
- [ ] Показывать workload after assignment.
- [ ] Показывать fairness report.
- [ ] Сохранять assignment session.

Файлы:

```text
sandbox_app/backend/inference/bulk_assignment.py
sandbox_app/backend/inference/assignment_optimizer.py
sandbox_app/backend/api/assignment_sessions.py
```

Результат:

```text
sandbox_app/assignment_sessions/<session_id>/assignment_config.json
sandbox_app/assignment_sessions/<session_id>/recommendations.json
sandbox_app/assignment_sessions/<session_id>/assigned_tasks.csv
sandbox_app/assignment_sessions/<session_id>/unassigned_tasks.csv
sandbox_app/assignment_sessions/<session_id>/workload_after_assignment.csv
sandbox_app/assignment_sessions/<session_id>/fairness_report.json
sandbox_app/assignment_sessions/<session_id>/assignment_report.html
```

**Ожидаемый результат:** модель может разом распределить все todo-задачи с учётом качества, скорости, обучения, усталости и загрузки.

**Примерное время:** 12–20 часов.  
**Коммит:** `Add sandbox bulk assignment simulation`

---

## 27.24. Сделать recommendation UI

- [ ] Показывать top candidates карточками.
- [ ] Показывать score breakdown.
- [ ] Показывать risks.
- [ ] Показывать recommendation mode.
- [ ] Показывать candidate comparison.
- [ ] Показывать kanban после распределения.
- [ ] Показывать workload chart.
- [ ] Показывать fatigue chart.
- [ ] Показывать fairness chart.
- [ ] Показывать unassigned tasks.
- [ ] Добавить фильтры по человеку, статусу, проекту, риску.
- [ ] Добавить export results.

Файлы:

```text
sandbox_app/frontend/js/components/recommendation_cards.js
sandbox_app/frontend/js/components/candidate_comparison.js
sandbox_app/frontend/js/components/workload_chart.js
sandbox_app/frontend/js/components/fairness_chart.js
sandbox_app/frontend/js/pages/assignment_lab.js
```

**Ожидаемый результат:** вывод модели понятен человеку и не выглядит как сырой JSON.

**Примерное время:** 8–12 часов.  
**Коммит:** `Add sandbox recommendation UI`

---

## 27.25. Подключить Qwen/Ollama explanations

- [ ] Создать отдельный Ollama client внутри sandbox_app.
- [ ] Не использовать src/llm/ollama_client.py напрямую.
- [ ] Добавить settings для Ollama base URL.
- [ ] Добавить settings для model name.
- [ ] Добавить settings для timeout.
- [ ] Проверять доступность Ollama.
- [ ] Использовать Qwen только для объяснения.
- [ ] Запретить Qwen менять ranking.
- [ ] Запретить Qwen придумывать кандидатов.
- [ ] Запретить Qwen придумывать навыки.
- [ ] Передавать Qwen только готовый top-k и factors.
- [ ] Валидировать, что explanation упоминает только разрешённых кандидатов.
- [ ] Сделать fallback explanation без LLM.
- [ ] Добавить checkbox LLM explanations в UI.
- [ ] Объяснять на русском языке.
- [ ] Проверить сценарий Ollama unavailable.
- [ ] Проверить сценарий Qwen available.

Файлы:

```text
sandbox_app/backend/llm/ollama_client.py
sandbox_app/backend/llm/qwen_explainer.py
sandbox_app/backend/api/llm.py
sandbox_app/frontend/js/pages/assignment_lab.js
```

Настройки:

```text
SANDBOX_OLLAMA_BASE_URL=http://localhost:11434
SANDBOX_OLLAMA_MODEL=qwen2.5:1.5b-instruct
SANDBOX_LLM_TIMEOUT_SECONDS=30
```

**Ожидаемый результат:** по checkbox можно включить русские Qwen explanations, но Qwen не влияет на ranking.

**Примерное время:** 6–10 часов.  
**Коммит:** `Add sandbox Qwen explanations`

---

## 27.26. Добавить reports и exports

- [ ] Делать dataset generation report.
- [ ] Делать dataset quality report.
- [ ] Делать training report.
- [ ] Делать model comparison report.
- [ ] Делать recommendation report.
- [ ] Делать bulk assignment report.
- [ ] Делать fairness report.
- [ ] Делать workload report.
- [ ] Экспортировать JSON.
- [ ] Экспортировать CSV.
- [ ] Экспортировать HTML.
- [ ] Показывать список reports в UI.
- [ ] Добавить download links.

Файлы:

```text
sandbox_app/backend/reports/dataset_report.py
sandbox_app/backend/reports/model_report.py
sandbox_app/backend/reports/assignment_report.py
sandbox_app/backend/reports/html_export.py
sandbox_app/backend/api/reports.py
sandbox_app/frontend/js/pages/reports.js
```

Папки:

```text
sandbox_app/reports
sandbox_app/data/exports
```

**Ожидаемый результат:** результаты экспериментов можно сохранить, открыть и показать отдельно.

**Примерное время:** 8–12 часов.  
**Коммит:** `Add sandbox reports and exports`

---

## 27.27. Добавить Settings UI и schema editor

- [ ] Сделать страницу Settings рабочей.
- [ ] Показывать app settings.
- [ ] Настраивать paths.
- [ ] Настраивать default seed.
- [ ] Настраивать default domain profile.
- [ ] Настраивать default dataset mode.
- [ ] Настраивать default recommendation mode.
- [ ] Настраивать default training models.
- [ ] Настраивать huge generation limits.
- [ ] Настраивать Ollama base URL.
- [ ] Настраивать Qwen model name.
- [ ] Сохранять settings в JSON.
- [ ] Добавить reset settings.
- [ ] Сделать editor feature schemas.
- [ ] Добавлять roles через UI.
- [ ] Добавлять grades через UI.
- [ ] Добавлять skills через UI.
- [ ] Добавлять employee features через UI.
- [ ] Добавлять task features через UI.
- [ ] Добавлять outcome features через UI.
- [ ] Удалять и переименовывать features через UI.
- [ ] Показывать schema preview.
- [ ] Сохранять schemas через API.

Файлы:

```text
sandbox_app/backend/api/settings.py
sandbox_app/frontend/js/pages/settings.js
sandbox_app/config/app_settings.json
```

**Ожидаемый результат:** пользователь может настраивать песочницу и custom schemas без ручной правки JSON.

**Примерное время:** 8–14 часов.  
**Коммит:** `Add sandbox settings`

---

## 27.28. Протестировать полный pipeline

- [ ] Написать tests для feature schemas.
- [ ] Написать tests для team generator.
- [ ] Написать tests для task generator.
- [ ] Написать tests для history generator.
- [ ] Написать tests для full dataset generator.
- [ ] Написать tests для data viewer API.
- [ ] Написать tests для import validation.
- [ ] Написать tests для feature builder.
- [ ] Написать training smoke test.
- [ ] Написать tests для training sessions.
- [ ] Написать tests для model loading.
- [ ] Написать tests для single recommendation.
- [ ] Написать tests для bulk assignment.
- [ ] Написать tests для Qwen fallback explanation.
- [ ] Написать smoke test запуска backend.
- [ ] Проверить end-to-end сценарий вручную в браузере.
- [ ] Проверить, что основной COMPASS API не сломан.

Команда:

```bash
pytest sandbox_app/tests
```

End-to-end сценарий:

```text
open browser app
create custom schema
generate full dataset
open Data Viewer
build features
train models
save training session
open model session
generate test team
run single recommendation
run bulk assignment
enable Qwen explanations
save assignment session
open reports
export results
```

**Ожидаемый результат:** песочница проходит полный цикл от генерации данных до объяснённого распределения задач.

**Примерное время:** 12–20 часов.  
**Коммит:** `Test sandbox end to end pipeline`

---

## 27.29. Задокументировать песочницу

- [ ] Создать полноценный sandbox_app/README.md.
- [ ] Описать назначение песочницы.
- [ ] Описать запуск.
- [ ] Описать остановку.
- [ ] Описать структуру папок.
- [ ] Описать data contracts.
- [ ] Описать feature schemas.
- [ ] Описать custom schema editor.
- [ ] Описать генерацию команды.
- [ ] Описать генерацию задач.
- [ ] Описать генерацию истории.
- [ ] Описать full dataset generation.
- [ ] Описать imported datasets.
- [ ] Описать Data Viewer.
- [ ] Описать feature builder.
- [ ] Описать обучение моделей.
- [ ] Описать training sessions.
- [ ] Описать model export.
- [ ] Описать test team.
- [ ] Описать single recommendation.
- [ ] Описать bulk assignment.
- [ ] Описать Qwen explanations.
- [ ] Описать reports.
- [ ] Описать ограничения.
- [ ] Добавить troubleshooting.

Troubleshooting:

```text
Port 8601 is busy
Python is not from .venv
FastAPI is not installed
PyArrow is not installed
Dataset is too large
Feature schema is invalid
Training session failed
Model cannot be loaded
ONNX Runtime is not installed
Ollama is not running
Qwen model not found
Browser shows old JS after cache
```

**Ожидаемый результат:** подпроект можно открыть отдельно и понять, как им пользоваться без чтения всего кода.

**Примерное время:** 5–8 часов.  
**Коммит:** `Document sandbox app`

---

## 27.30. Финальная проверка готовности этапа

- [ ] Папка sandbox_app полностью автономна.
- [ ] Приложение запускается через scripts/start.sh.
- [ ] Приложение останавливается через scripts/stop.sh.
- [ ] Приложение открывается в браузере.
- [ ] UI сделан на HTML/CSS/Vanilla JS.
- [ ] Backend работает на FastAPI.
- [ ] Основной COMPASS API не сломан.
- [ ] Можно создавать custom schemas.
- [ ] Можно генерировать команды.
- [ ] Можно генерировать задачи.
- [ ] Можно генерировать историю выполненных задач.
- [ ] Можно генерировать полный training dataset одной кнопкой.
- [ ] Можно генерировать большие training datasets.
- [ ] Можно просматривать данные в таблицах.
- [ ] Можно просматривать задачи в kanban.
- [ ] Можно импортировать внешние datasets.
- [ ] Можно строить features.
- [ ] Можно обучать несколько моделей.
- [ ] Каждое обучение сохраняется как session.
- [ ] Модели сохраняются.
- [ ] Графики сохраняются PNG.
- [ ] Reports сохраняются.
- [ ] Можно создать test team.
- [ ] Можно проверить single task recommendation.
- [ ] Можно выполнить bulk todo assignment.
- [ ] Можно включить Qwen explanations.
- [ ] Есть fallback explanation без LLM.
- [ ] Есть exports.
- [ ] Есть tests.
- [ ] Есть README.

**Ожидаемый результат:** этап считается завершённым, когда песочница позволяет пройти полный рабочий цикл: настроить domain schema, сгенерировать данные, обучить модели, создать тестовую команду, распределить задачи и получить понятные объяснения.

**Примерное время:** 2–4 часа.  
**Коммит:** `Finalize sandbox app milestone`