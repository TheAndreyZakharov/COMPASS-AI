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

- [ ] Сделать системный профиль developers.
- [ ] Сделать системный профиль designers.
- [ ] Сделать полностью свободный профиль custom.
- [ ] Поддержать любые domain profiles: медицина, право, продажи, дизайн, разработка, образование, операции.
- [ ] Дать возможность создать профиль через API.
- [ ] Дать возможность обновить профиль через API.
- [ ] Дать возможность удалить несистемный профиль.
- [ ] Защитить системные профили от удаления.
- [ ] Дать возможность добавить employee feature.
- [ ] Дать возможность добавить task feature.
- [ ] Дать возможность добавить outcome feature.
- [ ] Дать возможность переименовать feature.
- [ ] Дать возможность удалить feature.
- [ ] Поддержать numeric feature.
- [ ] Поддержать categorical feature.
- [ ] Поддержать boolean feature.
- [ ] Поддержать text feature.
- [ ] Поддержать skill_list feature.
- [ ] Валидировать profile_id.
- [ ] Валидировать feature names.
- [ ] Валидировать feature types.
- [ ] Показывать preview схемы через API.
- [ ] Сохранять schemas в JSON.
- [ ] Добавить документацию feature schemas.

Файлы:

```text
sandbox_app/config/feature_schemas/developers.json
sandbox_app/config/feature_schemas/designers.json
sandbox_app/config/feature_schemas/custom.json
sandbox_app/backend/features/schema.py
sandbox_app/backend/api/feature_schemas.py
sandbox_app/docs/feature_schemas.md
```

Endpoints:

```text
GET /api/feature-schemas
GET /api/feature-schemas/{profile_id}
POST /api/feature-schemas
PUT /api/feature-schemas/{profile_id}
DELETE /api/feature-schemas/{profile_id}
POST /api/feature-schemas/{profile_id}/features/{group}
PATCH /api/feature-schemas/{profile_id}/features/{group}/{feature_name}
DELETE /api/feature-schemas/{profile_id}/features/{group}/{feature_name}
```

**Ожидаемый результат:** пользователь может настроить признаки под любую команду и домен, а генерация данных использует выбранную схему.

**Примерное время:** 6–10 часов.  
**Коммит:** `Add configurable sandbox feature schemas`

---

## 27.6. Реализовать backend generator команды

- [ ] Создать генератор сотрудников.
- [ ] Использовать выбранный domain_profile.
- [ ] Настраивать employees_count.
- [ ] Настраивать roles.
- [ ] Настраивать grades.
- [ ] Настраивать skills.
- [ ] Настраивать skill_count_per_person_min.
- [ ] Настраивать skill_count_per_person_max.
- [ ] Настраивать seniority distribution.
- [ ] Настраивать workload.
- [ ] Настраивать fatigue.
- [ ] Настраивать learning goals.
- [ ] Генерировать availability_score.
- [ ] Генерировать avg_completion_speed.
- [ ] Генерировать avg_quality_score.
- [ ] Генерировать deadline_reliability.
- [ ] Генерировать mentor_level.
- [ ] Генерировать custom employee features из schema.
- [ ] Поддержать seed.
- [ ] Сохранять employees.json.
- [ ] Сохранять employees.csv.
- [ ] Сохранять team_metadata.json.
- [ ] Добавить endpoint генерации команды.
- [ ] Проверить developers, designers и custom domain.

Файлы:

```text
sandbox_app/backend/data_generation/employees.py
sandbox_app/backend/api/generate_team.py
```

Endpoint:

```text
POST /api/generate/team
```

Результаты:

```text
sandbox_app/data/generated/<dataset_id>/employees.csv
sandbox_app/data/generated/<dataset_id>/employees.json
sandbox_app/data/generated/<dataset_id>/team_metadata.json
```

**Ожидаемый результат:** можно сгенерировать реалистичную команду с ролями, навыками, загрузкой, усталостью и характеристиками.

**Примерное время:** 6–10 часов.  
**Коммит:** `Add sandbox team generator`

---

## 27.7. Реализовать backend generator задач и backlog

- [ ] Создать генератор задач.
- [ ] Использовать выбранный domain_profile.
- [ ] Настраивать tasks_count.
- [ ] Настраивать projects_count.
- [ ] Настраивать task_types.
- [ ] Настраивать priorities.
- [ ] Настраивать complexity.
- [ ] Настраивать deadline_days.
- [ ] Настраивать estimated_hours.
- [ ] Настраивать required skills.
- [ ] Настраивать dependencies.
- [ ] Настраивать skill_mismatch_probability.
- [ ] Генерировать статусы todo, in_progress, review, done, blocked, failed.
- [ ] Генерировать backlog из задач в статусе todo.
- [ ] Генерировать kanban summary.
- [ ] Генерировать custom task features из schema.
- [ ] Поддержать seed.
- [ ] Сохранять tasks.json.
- [ ] Сохранять tasks.csv.
- [ ] Сохранять backlog.json.
- [ ] Сохранять backlog.csv.
- [ ] Сохранять task_metadata.json.
- [ ] Добавить endpoint генерации задач.
- [ ] Проверить developers, designers и custom domain.

Файлы:

```text
sandbox_app/backend/data_generation/tasks.py
sandbox_app/backend/data_generation/backlog.py
sandbox_app/backend/api/generate_tasks.py
```

Endpoint:

```text
POST /api/generate/tasks
```

Результаты:

```text
sandbox_app/data/generated/<dataset_id>/tasks.csv
sandbox_app/data/generated/<dataset_id>/tasks.json
sandbox_app/data/generated/<dataset_id>/backlog.csv
sandbox_app/data/generated/<dataset_id>/backlog.json
sandbox_app/data/generated/<dataset_id>/task_metadata.json
```

**Ожидаемый результат:** можно сгенерировать большой backlog задач, похожий на реальный рабочий поток команды.

**Примерное время:** 6–10 часов.  
**Коммит:** `Add sandbox task generator`

---

## 27.8. Реализовать backend generator истории выполненных задач

- [ ] Создать outcome engine.
- [ ] Создать generator assignment_history.
- [ ] Поддержать employees из payload.
- [ ] Поддержать tasks из payload.
- [ ] Поддержать employees из generated dataset.
- [ ] Поддержать tasks из generated dataset.
- [ ] Настраивать history_depth_per_employee.
- [ ] Настраивать good_outcome_share.
- [ ] Настраивать bad_outcome_share.
- [ ] Настраивать late_outcome_share.
- [ ] Настраивать failed_outcome_share.
- [ ] Настраивать rework_probability.
- [ ] Настраивать overload_penalty_strength.
- [ ] Настраивать fatigue_penalty_strength.
- [ ] Настраивать skill_match_bonus_strength.
- [ ] Настраивать learning_task_share.
- [ ] Учитывать skill match.
- [ ] Учитывать workload.
- [ ] Учитывать fatigue.
- [ ] Учитывать complexity.
- [ ] Учитывать grade.
- [ ] Учитывать learning goals.
- [ ] Генерировать planned_hours.
- [ ] Генерировать actual_hours.
- [ ] Генерировать quality_score.
- [ ] Генерировать deadline_status.
- [ ] Генерировать outcome_label.
- [ ] Генерировать was_rework_needed.
- [ ] Генерировать feedback_score.
- [ ] Сохранять assignment_history.json.
- [ ] Сохранять assignment_history.csv.
- [ ] Сохранять history_metadata.json.
- [ ] Добавить endpoint генерации истории.

Файлы:

```text
sandbox_app/backend/data_generation/outcomes.py
sandbox_app/backend/data_generation/history.py
sandbox_app/backend/api/generate_history.py
```

Endpoint:

```text
POST /api/generate/history
```

**Ожидаемый результат:** у каждого сотрудника есть реалистичная история выполненных задач, пригодная для обучения моделей.

**Примерное время:** 8–14 часов.  
**Коммит:** `Add sandbox assignment history generator`

---

## 27.9. Реализовать backend full dataset generator одной кнопкой

- [ ] Сделать режим small_preview.
- [ ] Сделать режим medium_validation.
- [ ] Сделать режим large_training.
- [ ] Сделать режим huge_training.
- [ ] Настраивать employees_count.
- [ ] Настраивать tasks_count.
- [ ] Настраивать history_depth_per_employee.
- [ ] Настраивать target_pairs.
- [ ] Настраивать candidates_per_task.
- [ ] Генерировать employees.
- [ ] Генерировать tasks.
- [ ] Генерировать assignment_history.
- [ ] Генерировать training pairs task-employee.
- [ ] Добавлять positive examples.
- [ ] Добавлять negative examples.
- [ ] Балансировать классы.
- [ ] Сохранять training_pairs.parquet.
- [ ] Сохранять dataset_metadata.json.
- [ ] Сохранять generation_report.json.
- [ ] Добавить защиту huge generation через confirm_huge_generation.
- [ ] Поддержать custom domain profiles.
- [ ] Добавить endpoint генерации полного dataset.

Файлы:

```text
sandbox_app/backend/data_generation/training_pairs.py
sandbox_app/backend/api/generate_dataset.py
```

Endpoint:

```text
POST /api/generate/dataset
```

Режимы:

```text
small_preview: 10 people, 100 tasks, 1 000 pairs
medium_validation: 30 people, 1 000 tasks, 30 000 pairs
large_training: 100 people, 10 000 tasks, 1 000 000 pairs
huge_training: custom limits with explicit confirmation
```

Результаты:

```text
sandbox_app/data/generated/<dataset_id>/employees.csv
sandbox_app/data/generated/<dataset_id>/employees.json
sandbox_app/data/generated/<dataset_id>/tasks.csv
sandbox_app/data/generated/<dataset_id>/tasks.json
sandbox_app/data/generated/<dataset_id>/assignment_history.csv
sandbox_app/data/generated/<dataset_id>/assignment_history.json
sandbox_app/data/generated/<dataset_id>/training_pairs.parquet
sandbox_app/data/generated/<dataset_id>/dataset_metadata.json
sandbox_app/data/generated/<dataset_id>/generation_report.json
```

**Ожидаемый результат:** одной кнопкой можно создать полный training dataset любого нужного размера.

**Примерное время:** 8–14 часов.  
**Коммит:** `Add sandbox training dataset generator`

---

## 27.10. Сделать backend Data Viewer API

- [ ] Показывать список generated datasets.
- [ ] Показывать список imported datasets.
- [ ] Читать JSON tables.
- [ ] Читать CSV tables.
- [ ] Читать Parquet training pairs.
- [ ] Отдавать dataset summary.
- [ ] Отдавать employees table.
- [ ] Отдавать tasks table.
- [ ] Отдавать assignment_history table.
- [ ] Отдавать training_pairs table с пагинацией.
- [ ] Поддержать page и page_size.
- [ ] Поддержать search.
- [ ] Поддержать фильтры по status, role, grade, project_id, priority.
- [ ] Отдавать employee profile.
- [ ] Отдавать task profile.
- [ ] Отдавать employee history.
- [ ] Отдавать kanban board.
- [ ] Отдавать summary counts.

Файл:

```text
sandbox_app/backend/api/data_viewer.py
```

Endpoints:

```text
GET /api/data-viewer/datasets
GET /api/data-viewer/datasets/{dataset_id}/summary
GET /api/data-viewer/datasets/{dataset_id}/{table_name}
GET /api/data-viewer/datasets/{dataset_id}/employees/{employee_id}
GET /api/data-viewer/datasets/{dataset_id}/tasks/{task_id}
GET /api/data-viewer/datasets/{dataset_id}/employees/{employee_id}/history
GET /api/data-viewer/datasets/{dataset_id}/kanban
```

**Ожидаемый результат:** backend отдаёт все данные для удобного просмотра без ручного открытия CSV.

**Примерное время:** 4–6 часов.  
**Коммит:** `Add sandbox data viewer API`

---

## 27.11. Сделать frontend shell на HTML/CSS/Vanilla JS

- [ ] Создать frontend/index.html.
- [ ] Создать общий CSS.
- [ ] Создать общий JS app router.
- [ ] Создать API client.
- [ ] Сделать sidebar navigation.
- [ ] Сделать topbar.
- [ ] Сделать backend status indicator.
- [ ] Сделать refresh button.
- [ ] Сделать страницы Dashboard, Data Generator, Data Viewer, Training, Models, Assignment Lab, Reports, Settings.
- [ ] Не использовать Streamlit.
- [ ] Не оставлять заглушки там, где backend уже готов.
- [ ] Все готовые backend endpoints подключать сразу к UI.
- [ ] Проверить browser routing.
- [ ] Проверить browser hard refresh.
- [ ] Проверить CSS и JS static mounts.

Файлы:

```text
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
```

**Ожидаемый результат:** песочница открывается как нормальное локальное web-приложение в браузере.

**Примерное время:** 6–10 часов.  
**Коммит:** `Add sandbox browser UI`

---

## 27.12. Подключить frontend Data Generator

- [ ] Подключить форму генерации full dataset к /api/generate/dataset.
- [ ] Подключить генерацию команды к /api/generate/team.
- [ ] Подключить генерацию задач к /api/generate/tasks.
- [ ] Подключить генерацию истории к /api/generate/history.
- [ ] Сделать выбор domain_profile.
- [ ] Сделать ввод seed.
- [ ] Сделать выбор dataset mode.
- [ ] Сделать поля employees_count, tasks_count, target_pairs, history_depth_per_employee.
- [ ] Сделать confirm_huge_generation.
- [ ] Показывать loading state.
- [ ] Показывать error state.
- [ ] Показывать dataset_id после генерации.
- [ ] Показывать dataset_dir после генерации.
- [ ] Показывать counts: employees, tasks, history, training_pairs.
- [ ] Добавить переход в Data Viewer после генерации.
- [ ] Проверить генерацию через браузер.

Файл:

```text
sandbox_app/frontend/js/pages/generator.js
```

**Ожидаемый результат:** пользователь может в браузере одной кнопкой создать полный dataset и сразу открыть его в Data Viewer.

**Примерное время:** 4–6 часов.  
**Коммит:** `Connect sandbox generator UI`

---

## 27.13. Подключить frontend Data Viewer

- [ ] Сделать страницу Data Viewer.
- [ ] Показывать список generated datasets.
- [ ] Показывать список imported datasets.
- [ ] Показывать таблицу employees.
- [ ] Показывать таблицу tasks.
- [ ] Показывать таблицу assignment_history.
- [ ] Показывать таблицу training_pairs с пагинацией.
- [ ] Показывать карточки summary.
- [ ] Показывать простые summary charts.
- [ ] Показывать kanban board.
- [ ] Добавить фильтры.
- [ ] Добавить search.
- [ ] Добавить pagination controls.
- [ ] Сделать frontend table component.
- [ ] Сделать frontend kanban component.
- [ ] Сделать frontend charts component.
- [ ] Проверить Data Viewer в браузере на реальном generated dataset.

Файлы:

```text
sandbox_app/frontend/js/pages/viewer.js
sandbox_app/frontend/js/components/table.js
sandbox_app/frontend/js/components/kanban.js
sandbox_app/frontend/js/components/charts.js
sandbox_app/frontend/css/styles.css
```

**Ожидаемый результат:** пользователь может изучать сгенерированные данные глазами, без ручного открытия CSV.

**Примерное время:** 6–10 часов.  
**Коммит:** `Add sandbox data viewer`

---

## 27.14. Реализовать импорт внешних datasets

- [ ] Поддержать CSV import.
- [ ] Поддержать JSON import.
- [ ] Поддержать Parquet import.
- [ ] Импортировать employees.
- [ ] Импортировать tasks.
- [ ] Импортировать assignment_history.
- [ ] Импортировать training_pairs.
- [ ] Проверять required fields по data contracts.
- [ ] Показывать schema errors.
- [ ] Показывать warnings.
- [ ] Показывать preview.
- [ ] Не перезаписывать imported dataset без подтверждения.
- [ ] Сохранять imported dataset отдельно.
- [ ] Разрешить использовать imported dataset в training.

Файлы:

```text
sandbox_app/backend/api/import_data.py
sandbox_app/backend/utils/importers.py
sandbox_app/backend/utils/validation.py
sandbox_app/frontend/js/pages/import_data.js
```

Папка:

```text
sandbox_app/data/imported
```

**Ожидаемый результат:** песочница работает не только с синтетикой, но и с внешними датасетами.

**Примерное время:** 8–12 часов.  
**Коммит:** `Add sandbox dataset import`

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