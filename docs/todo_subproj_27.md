# 27. Этап 25 — автономный локальный подпроект COMPASS AI Sandbox

Цель этапа: сделать отдельную локальную песочницу внутри основного репозитория `COMPASS-AI`, где можно генерировать большие синтетические команды и задачи, обучать разные модели, сохранять результаты по сессиям, проверять распределение задач и получать объяснения через локальный Qwen/Ollama.

Песочница должна быть автономной: со своей структурой папок, своим backend, своим frontend на HTML/CSS/JS, своими скриптами запуска, своими данными, моделями, отчётами и LLM-клиентом.

---

## 27.1. Создать автономную папку подпроекта

- [x] Создать папку `sandbox_app`.
- [x] Не смешивать код песочницы с основным `src`.
- [x] Не ломать основной COMPASS API.
- [x] Использовать уже созданное окружение проекта `.venv`.
- [x] Зафиксировать Python `3.11.x` как целевую версию.
- [x] Сделать отдельный `README.md` внутри песочницы.
- [x] Сделать отдельную структуру для backend, frontend, данных, моделей, отчётов и скриптов.
- [x] Сделать основу для локального browser-приложения.
- [x] Не завязывать песочницу напрямую на LLM-файлы основного проекта.
- [x] Не завязывать песочницу напрямую на текущие agent-файлы основного проекта.
- [x] Добавить `requirements.txt` для будущего backend, обучения, графиков, отчётов и тестов.
- [x] Добавить `app_settings.json` с путями, портом, Python-версией и настройками Ollama/Qwen.
- [x] Добавить `model_presets.json` для будущего обучения нескольких моделей.
- [x] Добавить feature schemas: `developers`, `designers`, `custom`.
- [x] Добавить Python package markers для backend-модулей.
- [x] Добавить `.gitkeep` в пустые runtime-папки.
- [x] Проверить JSON-конфиги.
- [x] Проверить Python-пакет через compileall.

Папка подпроекта: `sandbox_app`.

Фактическая структура: есть отдельные папки `config`, `scripts`, `backend`, `frontend`, `data`, `training_sessions`, `assignment_sessions`, `reports`, `logs`, `tests`.

Backend-основа: создан отдельный пакет `sandbox_app.backend`, реальный FastAPI backend будет реализован в 27.3.

Frontend-основа: создан минимальный `frontend/index.html`, полноценный HTML/CSS/JS интерфейс будет реализован в 27.4.

Конфиги: созданы `app_settings.json`, `model_presets.json`, `feature_schemas/developers.json`, `feature_schemas/designers.json`, `feature_schemas/custom.json`.

Проверки: JSON-конфиги валидны, Python-пакет компилируется.

**Ожидаемый результат:** подпроект существует как отдельная локальная песочница внутри репозитория и не является набором случайных скриптов.

**Фактическое время:** 2–4 часа.  
**Коммит:** `Create autonomous sandbox app structure`

---

## 27.2. Сделать локальный запуск и остановку приложения

- [x] Создать sandbox_app/scripts/start.sh.
- [x] Создать sandbox_app/scripts/stop.sh.
- [x] Создать sandbox_app/scripts/restart.sh.
- [x] Создать sandbox_app/scripts/smoke_test.sh.
- [x] Создать безопасный sandbox_app/scripts/clean_tmp.sh.
- [x] Сделать запуск через уже активированное .venv.
- [x] Сделать проверку, что Python берётся из .venv.
- [x] Сделать запуск backend на порту 8601.
- [x] Сделать открытие frontend через тот же FastAPI backend.
- [x] Сохранять PID процесса в sandbox_app/logs/sandbox_app.pid.
- [x] Сохранять логи запуска в sandbox_app/logs/server.log.
- [x] Добавить понятные сообщения в терминал.
- [x] Добавить команды в основной Makefile.
- [x] Добавить игнорирование runtime logs и pid-файлов.
- [x] Добавить минимальный FastAPI bootstrap для запуска приложения.
- [x] Добавить health endpoint для smoke test.
- [x] Проверить shell scripts через bash -n.
- [x] Проверить Python-пакет через compileall.
- [x] Проверить запуск, smoke test и остановку приложения.

Команды запуска:

- cd /Users/andrey/Documents/projects/COMPASS-AI
- source .venv/bin/activate
- bash sandbox_app/scripts/start.sh

Локальный URL: http://127.0.0.1:8601

Makefile targets:

- sandbox-start
- sandbox-stop
- sandbox-restart
- sandbox-test
- sandbox-clean

Фактически работает так: start.sh проверяет активное .venv, проверяет Python из проекта, проверяет FastAPI runtime, проверяет занятость порта, запускает uvicorn, пишет PID и server.log. stop.sh останавливает процесс по PID и чистит pid-файл. restart.sh делает stop и start. smoke_test.sh проверяет /api/health. clean_tmp.sh чистит Python cache внутри sandbox_app.

Корректировка по roadmap: добавлен минимальный FastAPI bootstrap в sandbox_app/backend/main.py, потому что без него пункт 27.2 не мог бы быть рабочим. Полноценный backend API остаётся в 27.3.

Ожидаемый результат: приложение можно запускать, останавливать, перезапускать и проверять одной командой.

Фактическое время: 2–3 часа.  
Коммит: Add sandbox run scripts

---

## 27.3. Сделать базовый backend на FastAPI

- [x] Создать sandbox_app/backend/main.py.
- [x] Подключить раздачу frontend-статики.
- [x] Подключить отдельную раздачу CSS из sandbox_app/frontend/css.
- [x] Подключить отдельную раздачу JS из sandbox_app/frontend/js.
- [x] Подключить отдельную раздачу assets из sandbox_app/frontend/assets.
- [x] Добавить health endpoint.
- [x] Добавить API namespace /api.
- [x] Добавить endpoint /api/status.
- [x] Добавить endpoint /api/config.
- [x] Добавить endpoint /api/sessions.
- [x] Добавить CORS только для локального режима.
- [x] Добавить базовую обработку ошибок.
- [x] Добавить запись backend-логов.
- [x] Вынести paths в sandbox_app/backend/core/paths.py.
- [x] Вынести settings loader в sandbox_app/backend/core/settings.py.
- [x] Вынести JSON helpers в sandbox_app/backend/utils/json_io.py.
- [x] Вынести status routes в sandbox_app/backend/api/status.py.
- [x] Вынести config routes в sandbox_app/backend/api/config.py.
- [x] Вынести sessions routes в sandbox_app/backend/api/sessions.py.
- [x] Проверить импорт FastAPI app.
- [x] Проверить endpoints health, status, config, sessions.
- [x] Проверить, что корневой URL открывает frontend.
- [x] Проверить, что CSS открывается по /css/styles.css.
- [x] Проверить, что JS открывается по /js/app.js.
- [x] Проверить smoke test через sandbox_app/scripts/smoke_test.sh.

Файлы:

- sandbox_app/backend/main.py
- sandbox_app/backend/api/status.py
- sandbox_app/backend/api/config.py
- sandbox_app/backend/api/sessions.py
- sandbox_app/backend/core/settings.py
- sandbox_app/backend/core/paths.py
- sandbox_app/backend/core/logging.py
- sandbox_app/backend/utils/json_io.py
- sandbox_app/frontend/index.html
- sandbox_app/frontend/css/styles.css
- sandbox_app/frontend/js/app.js

Endpoints:

- GET /api/health
- GET /api/status
- GET /api/config
- GET /api/sessions

Фактически работает так: backend стартует через существующий start.sh, отдаёт frontend по корневому URL, отдаёт CSS по /css/styles.css, отдаёт JS по /js/app.js, отдаёт assets по /assets, имеет локальный CORS, возвращает публичный config, показывает training и assignment sessions, проверяет базовый статус приложения и доступность Ollama.

Исправление по факту проверки: изначально страница открывалась без CSS и JS, потому что HTML ссылался на /assets/styles.css и /assets/app.js, а файлы лежали в frontend/css и frontend/js. Исправлено через отдельные mounts /css и /js и обновлённые ссылки в index.html.

Ожидаемый результат: локальный backend работает и отдаёт frontend в браузер.

Фактическое время: 3–5 часов.  
Коммит: Add sandbox FastAPI backend

---

## 27.4. Сделать базовый frontend на HTML/CSS/JS

- [x] Создать sandbox_app/frontend/index.html.
- [x] Создать общий CSS.
- [x] Создать общий JS-клиент для API.
- [x] Сделать layout приложения.
- [x] Сделать sidebar navigation.
- [x] Добавить страницу Dashboard.
- [x] Добавить страницу Data Generator.
- [x] Добавить страницу Data Viewer.
- [x] Добавить страницу Training.
- [x] Добавить страницу Models.
- [x] Добавить страницу Assignment Lab.
- [x] Добавить страницу Reports.
- [x] Добавить страницу Settings.
- [x] Сделать loading states.
- [x] Сделать error states.
- [x] Сделать backend status indicator.
- [x] Сделать refresh button.
- [x] Сделать UI без Streamlit.
- [x] Подключить frontend к backend endpoints health, status, config, sessions.
- [x] Проверить отдачу CSS.
- [x] Проверить отдачу JS.
- [x] Проверить переключение страниц в браузере.

Файлы:

- sandbox_app/frontend/index.html
- sandbox_app/frontend/css/styles.css
- sandbox_app/frontend/js/api.js
- sandbox_app/frontend/js/app.js
- sandbox_app/frontend/js/pages/dashboard.js
- sandbox_app/frontend/js/pages/generator.js
- sandbox_app/frontend/js/pages/viewer.js
- sandbox_app/frontend/js/pages/training.js
- sandbox_app/frontend/js/pages/models.js
- sandbox_app/frontend/js/pages/assignment_lab.js
- sandbox_app/frontend/js/pages/reports.js
- sandbox_app/frontend/js/pages/settings.js

Разделы UI:

- Dashboard
- Data Generator
- Data Viewer
- Training
- Models
- Assignment Lab
- Reports
- Settings

Фактически работает так: приложение открывается в браузере, имеет sidebar navigation, переключает страницы через hash routing, показывает статус backend, читает config и sessions через API, показывает loading и error states. Функциональные кнопки генерации, обучения и assignment simulation пока отключены до соответствующих backend-пунктов roadmap.

Ожидаемый результат: песочница выглядит как нормальное локальное web-приложение, а не как консольный набор утилит.

Фактическое время: 6–10 часов.  
Коммит: Add sandbox browser UI

---

## 27.5. Описать форматы данных песочницы

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
- [x] Поддержать CSV для простого просмотра.
- [x] Поддержать JSON для вложенных структур.
- [x] Поддержать Parquet для больших training datasets.
- [x] Зафиксировать обязательные и optional поля.
- [x] Зафиксировать allowed statuses для задач.
- [x] Зафиксировать outcome labels и deadline statuses для истории.
- [x] Зафиксировать target поля для training pairs.
- [x] Зафиксировать формат recommendation candidates.
- [x] Добавить единый файл data contracts.
- [x] Добавить backend loader для data contracts.
- [x] Добавить API endpoints для просмотра contracts.
- [x] Добавить краткую документацию data contracts.
- [x] Проверить JSON.
- [x] Проверить Python imports.
- [x] Проверить endpoints contracts.

Файлы:

- sandbox_app/config/data_contracts/data_contracts.json
- sandbox_app/backend/core/data_contracts.py
- sandbox_app/backend/api/contracts.py
- sandbox_app/docs/data_contracts.md
- sandbox_app/backend/main.py

Endpoints:

- GET /api/contracts
- GET /api/contracts/{contract_name}

Основные сущности:

- employees
- tasks
- assignment_history
- training_pairs
- current_team
- current_backlog
- recommendations
- training_session
- assignment_session
- dataset_metadata

Форматы хранения:

- CSV для простых таблиц и ручного просмотра
- JSON для вложенных структур, metadata, recommendations, sessions и test cases
- Parquet для больших training datasets и feature matrices

Фактически работает так: data contracts лежат в одном JSON-файле, backend умеет загружать список контрактов и отдельный контракт по имени, API отдаёт contracts через /api/contracts и /api/contracts/{contract_name}. Контракты заранее поддерживают разные домены через роли, грейды, навыки и custom features.

Ожидаемый результат: до генерации и обучения понятно, какие данные живут в системе и как они связаны.

Фактическое время: 3–5 часов.  
Коммит: Define sandbox data contracts

---

## 27.6. Реализовать настраиваемые профили признаков

- [x] Сделать системные профили признаков.
- [x] Добавить профиль developers.
- [x] Добавить профиль designers.
- [x] Добавить полностью свободный профиль custom.
- [x] Добавить возможность создать свой профиль.
- [x] Добавить возможность переименовать признак.
- [x] Добавить возможность удалить признак.
- [x] Добавить возможность добавить числовой признак.
- [x] Добавить возможность добавить категориальный признак.
- [x] Добавить возможность добавить boolean-признак.
- [x] Добавить возможность добавить текстовый признак.
- [x] Добавить возможность добавить список навыков.
- [x] Показывать preview схемы через API.
- [x] Сохранять схемы в JSON.
- [x] Использовать выбранную схему как основу для будущей генерации данных.
- [x] Использовать выбранную схему как основу для будущего feature building.
- [x] Добавить backend validation для profile_id, feature names и feature types.
- [x] Добавить защиту системных профилей от удаления.
- [x] Добавить документацию по feature schemas.
- [x] Проверить JSON.
- [x] Проверить Python imports.
- [x] Проверить API endpoints.
- [x] Проверить создание custom-профиля на примере medical_team.

Файлы:

- sandbox_app/config/feature_schemas/developers.json
- sandbox_app/config/feature_schemas/designers.json
- sandbox_app/config/feature_schemas/custom.json
- sandbox_app/backend/api/feature_schemas.py
- sandbox_app/backend/features/schema.py
- sandbox_app/backend/main.py
- sandbox_app/docs/feature_schemas.md

Endpoints:

- GET /api/feature-schemas
- GET /api/feature-schemas/{profile_id}
- POST /api/feature-schemas
- PUT /api/feature-schemas/{profile_id}
- DELETE /api/feature-schemas/{profile_id}
- POST /api/feature-schemas/{profile_id}/features/{group}
- PATCH /api/feature-schemas/{profile_id}/features/{group}/{feature_name}
- DELETE /api/feature-schemas/{profile_id}/features/{group}/{feature_name}

Поддерживаемые feature types:

- numeric
- categorical
- boolean
- text
- skill_list

Поддерживаемые feature groups:

- employee
- task
- outcome

Фактически работает так: developers и designers являются готовыми системными примерами, custom является свободным шаблоном под любую область. Пользователь может создать профиль для врачей, юристов, дизайнеров, продаж, поддержки или любой другой команды, задать свои роли, грейды, навыки, признаки сотрудников, признаки задач и признаки результата. Backend валидирует схему, сохраняет её в JSON и отдаёт preview через API.

Ожидаемый результат: можно синтетически генерировать не только разработчиков, но и дизайнеров или любую другую команду с собственными признаками.

Фактическое время: 6–10 часов.  
Коммит: Add configurable sandbox feature schemas

---

## 27.7. Реализовать генератор команды

- [x] Создать генератор сотрудников.
- [x] Настраивать количество людей.
- [x] Настраивать роли.
- [x] Настраивать грейды.
- [x] Настраивать набор навыков.
- [x] Настраивать распределение seniority.
- [x] Настраивать среднюю скорость.
- [x] Настраивать среднее качество.
- [x] Настраивать надёжность по дедлайнам.
- [x] Настраивать fatigue и workload.
- [x] Настраивать learning goals.
- [x] Настраивать mentor level.
- [x] Поддержать seed.
- [x] Сохранять generated team.
- [x] Показывать preview команды через API.
- [x] Поддержать domain_profile developers.
- [x] Поддержать domain_profile designers.
- [x] Поддержать любые custom domain profiles.
- [x] Генерировать custom employee features из выбранной схемы.
- [x] Сохранять employees.json.
- [x] Сохранять employees.csv.
- [x] Сохранять team_metadata.json.
- [x] Добавить endpoint генерации команды.
- [x] Проверить генерацию напрямую через Python.
- [x] Проверить генерацию через API.
- [x] Проверить генерацию команды врачей через custom schema.
- [x] Проверить smoke test backend.

Файлы:

- sandbox_app/backend/data_generation/employees.py
- sandbox_app/backend/api/generate_team.py
- sandbox_app/backend/main.py

Endpoint:

- POST /api/generate/team

Параметры:

- seed
- employees_count
- domain_profile
- roles
- grades
- skills
- skill_count_per_person_min
- skill_count_per_person_max
- junior_share
- middle_share
- senior_share
- lead_share
- fatigue_min
- fatigue_max
- workload_min
- workload_max

Результаты:

- sandbox_app/data/generated/<dataset_id>/employees.csv
- sandbox_app/data/generated/<dataset_id>/employees.json
- sandbox_app/data/generated/<dataset_id>/team_metadata.json

Фактически работает так: генератор берёт выбранный feature schema, создаёт реалистичную команду с ролями, грейдами, навыками, learning goals, workload, fatigue, availability, speed, quality, deadline reliability, mentor level и custom employee features. Для developers и designers используются готовые схемы, для любых других областей используется custom schema, например медицинская команда с врачами и собственными признаками.

Ожидаемый результат: можно создать реалистичную команду с людьми, ролями, навыками, загрузкой, усталостью и историческими характеристиками.

Фактическое время: 6–10 часов.  
Коммит: Add sandbox team generator

---

## 27.8. Реализовать генератор задач и backlog

- [x] Создать генератор задач.
- [x] Настраивать количество задач.
- [x] Настраивать количество проектов.
- [x] Настраивать типы задач.
- [x] Настраивать приоритеты.
- [x] Настраивать сложность.
- [x] Настраивать дедлайны.
- [x] Настраивать required skills.
- [x] Настраивать estimated hours.
- [x] Настраивать зависимости.
- [x] Генерировать задачи в разных статусах.
- [x] Генерировать отдельный backlog задач в статусе todo.
- [x] Генерировать задачи для канбан-доски.
- [x] Поддержать custom task features.
- [x] Поддержать seed.
- [x] Сохранять задачи в dataset folder.
- [x] Сохранять tasks.json.
- [x] Сохранять tasks.csv.
- [x] Сохранять backlog.json.
- [x] Сохранять backlog.csv.
- [x] Сохранять task_metadata.json.
- [x] Добавить endpoint генерации задач.
- [x] Проверить генерацию напрямую через Python.
- [x] Проверить генерацию через API.
- [x] Проверить генерацию медицинских задач через custom schema.
- [x] Проверить smoke test backend.

Файлы:

- sandbox_app/backend/data_generation/tasks.py
- sandbox_app/backend/data_generation/backlog.py
- sandbox_app/backend/api/generate_tasks.py
- sandbox_app/backend/main.py

Endpoint:

- POST /api/generate/tasks

Параметры:

- seed
- tasks_count
- projects_count
- domain_profile
- task_types
- priorities
- skills
- todo_share
- in_progress_share
- review_share
- done_share
- blocked_share
- failed_share
- min_complexity
- max_complexity
- min_deadline_days
- max_deadline_days
- min_estimated_hours
- max_estimated_hours
- skill_count_min
- skill_count_max
- dependency_probability
- skill_mismatch_probability

Статусы:

- todo
- in_progress
- review
- done
- blocked
- failed

Результаты:

- sandbox_app/data/generated/<dataset_id>/tasks.csv
- sandbox_app/data/generated/<dataset_id>/tasks.json
- sandbox_app/data/generated/<dataset_id>/backlog.csv
- sandbox_app/data/generated/<dataset_id>/backlog.json
- sandbox_app/data/generated/<dataset_id>/task_metadata.json

Фактически работает так: генератор берёт выбранный feature schema, создаёт задачи с типами, приоритетами, сложностью, оценкой часов, дедлайнами, required skills, статусами, зависимостями, project_id и custom task features. Backlog отдельно сохраняется из задач со статусом todo. Для developers и designers используются готовые схемы, для любых других областей используется custom schema, например медицинские задачи с emergency_level, requires_surgery и department.

Ожидаемый результат: можно создать большой набор задач, похожий на реальный backlog команды.

Фактическое время: 6–10 часов.  
Коммит: Add sandbox task generator

---

## 27.9. Реализовать генератор истории выполненных задач

- [x] Создать генератор historical assignments.
- [x] Для каждого сотрудника генерировать сотни прошлых задач.
- [x] Настраивать глубину истории на человека.
- [x] Настраивать good/bad outcomes.
- [x] Настраивать late/on-time/failed outcomes.
- [x] Учитывать skill match.
- [x] Учитывать перегруз.
- [x] Учитывать усталость.
- [x] Учитывать сложность задачи.
- [x] Учитывать seniority.
- [x] Учитывать learning tasks.
- [x] Генерировать качество результата.
- [x] Генерировать скорость выполнения.
- [x] Генерировать rework.
- [x] Генерировать feedback score.
- [x] Сохранять assignment history.
- [x] Показывать статистику истории через API.
- [x] Добавить outcome engine.
- [x] Добавить endpoint генерации истории.
- [x] Поддержать employees и tasks из payload.
- [x] Поддержать employees и tasks из generated datasets.
- [x] Сохранять assignment_history.json.
- [x] Сохранять assignment_history.csv.
- [x] Сохранять history_metadata.json.
- [x] Проверить генерацию напрямую через Python.
- [x] Проверить генерацию через API.
- [x] Проверить smoke test backend.

Файлы:

- sandbox_app/backend/data_generation/history.py
- sandbox_app/backend/data_generation/outcomes.py
- sandbox_app/backend/api/generate_history.py
- sandbox_app/backend/main.py

Endpoint:

- POST /api/generate/history

Параметры:

- seed
- employees_dataset_id
- tasks_dataset_id
- employees
- tasks
- history_depth_per_employee
- good_outcome_share
- bad_outcome_share
- late_outcome_share
- failed_outcome_share
- rework_probability
- overload_penalty_strength
- fatigue_penalty_strength
- skill_match_bonus_strength
- learning_task_share

Результаты:

- sandbox_app/data/generated/<dataset_id>/assignment_history.csv
- sandbox_app/data/generated/<dataset_id>/assignment_history.json
- sandbox_app/data/generated/<dataset_id>/history_metadata.json

Фактически работает так: генератор берёт сотрудников и задачи, создаёт историю назначений, выбирает задачи для каждого сотрудника, учитывает совпадение навыков, загрузку, усталость, сложность, грейд и learning goals. Для каждой записи генерируются planned_hours, actual_hours, quality_score, deadline_status, outcome_label, rework, feedback_score, success_score и skill_match_score. Историю можно строить из payload или из уже сохранённых generated datasets.

Ожидаемый результат: у каждого человека есть большая история выполненных задач, по которой можно обучать модели.

Фактическое время: 8–14 часов.  
Коммит: Add sandbox assignment history generator

---

## 27.10. Реализовать генерацию больших training datasets

- [x] Сделать режим small preview.
- [x] Сделать режим medium validation.
- [x] Сделать режим large training.
- [x] Сделать режим huge training.
- [x] Генерировать training pairs task-employee.
- [x] Для каждой задачи создавать пары с несколькими кандидатами.
- [x] Добавлять positive и negative examples.
- [x] Балансировать классы.
- [x] Сохранять большие данные в Parquet.
- [x] Сохранять metadata генерации.
- [x] Показывать размер датасета.
- [x] Показывать class balance.
- [x] Показывать распределение ролей, навыков, outcome.
- [x] Добавить защиту от случайной генерации слишком огромных данных без подтверждения.
- [x] Генерировать employees внутри dataset folder.
- [x] Генерировать tasks внутри dataset folder.
- [x] Генерировать assignment_history внутри dataset folder.
- [x] Сохранять employees.csv и employees.json.
- [x] Сохранять tasks.csv и tasks.json.
- [x] Сохранять assignment_history.csv и assignment_history.json.
- [x] Сохранять training_pairs.parquet.
- [x] Сохранять dataset_metadata.json.
- [x] Сохранять generation_report.json.
- [x] Добавить endpoint генерации training dataset.
- [x] Проверить генерацию напрямую через Python.
- [x] Проверить генерацию через API.
- [x] Проверить чтение Parquet.
- [x] Проверить защиту huge generation.
- [x] Проверить custom domain profile на медицинском примере.
- [x] Проверить smoke test backend.

Режимы:

- small_preview: 10 people, 100 tasks, 1 000 pairs
- medium_validation: 30 people, 1 000 tasks, 30 000 pairs
- large_training: 100 people, 10 000 tasks, 1 000 000 pairs
- huge_training: custom limits with explicit confirmation

Файлы:

- sandbox_app/backend/data_generation/training_pairs.py
- sandbox_app/backend/api/generate_dataset.py
- sandbox_app/backend/main.py
- sandbox_app/requirements.txt

Endpoint:

- POST /api/generate/dataset

Результаты:

- sandbox_app/data/generated/<dataset_id>/employees.csv
- sandbox_app/data/generated/<dataset_id>/employees.json
- sandbox_app/data/generated/<dataset_id>/tasks.csv
- sandbox_app/data/generated/<dataset_id>/tasks.json
- sandbox_app/data/generated/<dataset_id>/assignment_history.csv
- sandbox_app/data/generated/<dataset_id>/assignment_history.json
- sandbox_app/data/generated/<dataset_id>/training_pairs.parquet
- sandbox_app/data/generated/<dataset_id>/dataset_metadata.json
- sandbox_app/data/generated/<dataset_id>/generation_report.json

Фактически работает так: генератор создаёт полный training dataset в одной папке, генерирует команду, задачи, историю назначений и пары task-employee. Для каждой пары рассчитываются label, target_score, skill_match, параметры задачи и параметры сотрудника. Данные training_pairs сохраняются в Parquet, metadata и generation report сохраняются в JSON. Huge generation требует явного подтверждения, чтобы случайно не создать слишком большой датасет.

Ожидаемый результат: можно генерировать как маленькие проверочные данные, так и большие данные для обучения модели.

Фактическое время: 8–14 часов.  
Коммит: Add sandbox training dataset generator

---

## 27.11. Сделать удобный просмотр данных

- [ ] Сделать страницу `Data Viewer`.
- [ ] Показывать список generated datasets.
- [ ] Показывать список imported datasets.
- [ ] Показывать сотрудников в таблице.
- [ ] Показывать задачи в таблице.
- [ ] Показывать assignment history в таблице.
- [ ] Показывать training pairs в таблице с пагинацией.
- [ ] Показывать карточку сотрудника.
- [ ] Показывать карточку задачи.
- [ ] Показывать историю сотрудника.
- [ ] Показывать канбан-доску для текущих задач.
- [ ] Добавить фильтры по статусу, роли, грейду, проекту, приоритету.
- [ ] Добавить поиск.
- [ ] Добавить summary-графики.
- [ ] Не заставлять смотреть только CSV.

Файлы:

```text
sandbox_app/backend/api/data_viewer.py
sandbox_app/frontend/js/pages/viewer.js
sandbox_app/frontend/js/components/table.js
sandbox_app/frontend/js/components/kanban.js
sandbox_app/frontend/js/components/charts.js
```

Представления:

```text
Team Table
Employee Profile
Tasks Table
Kanban Board
History Table
Training Pairs Table
Dataset Summary
```

**Ожидаемый результат:** сгенерированные данные можно нормально изучить глазами прямо в браузере.

**Примерное время:** 8–12 часов.  
**Коммит:** `Add sandbox data viewer`

---

## 27.12. Реализовать feature builder

- [ ] Создать отдельный feature builder песочницы.
- [ ] Не использовать напрямую основной feature pipeline.
- [ ] Поддержать employees.
- [ ] Поддержать tasks.
- [ ] Поддержать assignment history.
- [ ] Поддержать custom features.
- [ ] Поддержать skill vectors.
- [ ] Поддержать pair features.
- [ ] Поддержать workload features.
- [ ] Поддержать fatigue features.
- [ ] Поддержать learning potential features.
- [ ] Поддержать quality/speed/reliability targets.
- [ ] Поддержать разные target modes.
- [ ] Сохранять feature matrix.
- [ ] Сохранять feature metadata.
- [ ] Показывать feature dimensions в UI.

Файлы:

```text
sandbox_app/backend/features/build_features.py
sandbox_app/backend/features/skill_vectorizer.py
sandbox_app/backend/features/custom_features.py
sandbox_app/backend/features/pair_features.py
sandbox_app/backend/features/targets.py
```

Target modes:

```text
quality
speed
balanced
learning
risk_aware
```

Результаты:

```text
sandbox_app/data/generated/<dataset_id>/features/features.parquet
sandbox_app/data/generated/<dataset_id>/features/targets.parquet
sandbox_app/data/generated/<dataset_id>/features/feature_metadata.json
```

**Ожидаемый результат:** песочница сама превращает сгенерированные данные в обучающий набор для разных моделей.

**Примерное время:** 10–16 часов.  
**Коммит:** `Add sandbox feature builder`

---

## 27.13. Реализовать обучение нескольких моделей

- [ ] Сделать страницу `Training`.
- [ ] Выбирать dataset.
- [ ] Выбирать target mode.
- [ ] Выбирать одну или несколько моделей.
- [ ] Реализовать Logistic Regression / SGD Classifier.
- [ ] Реализовать Random Forest.
- [ ] Реализовать Gradient Boosting или HistGradientBoosting.
- [ ] Реализовать простую PyTorch neural network.
- [ ] Реализовать baseline rule-based модель.
- [ ] Настраивать train/validation/test split.
- [ ] Настраивать random seed.
- [ ] Настраивать параметры моделей.
- [ ] Запускать обучение из UI.
- [ ] Показывать progress.
- [ ] Показывать метрики.
- [ ] Сохранять каждую модель отдельно.
- [ ] Сохранять общий training session.

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

**Ожидаемый результат:** можно обучить несколько моделей на одном датасете и сравнить их поведение.

**Примерное время:** 14–24 часа.  
**Коммит:** `Add sandbox multi-model training`

---

## 27.14. Сделать формат training sessions

- [ ] При каждом запуске обучения создавать отдельную папку сессии.
- [ ] Называть сессии по времени и короткому id.
- [ ] Сохранять config сессии.
- [ ] Сохранять dataset metadata.
- [ ] Сохранять feature metadata.
- [ ] Для каждой модели создавать отдельную подпапку.
- [ ] Сохранять model artifact.
- [ ] Сохранять metrics.
- [ ] Сохранять predictions на test split.
- [ ] Сохранять графики обучения.
- [ ] Сохранять confusion matrix.
- [ ] Сохранять feature importance, если модель поддерживает.
- [ ] Сохранять session summary.
- [ ] Показывать список training sessions в UI.

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
        │   ├── model.joblib
        │   ├── metrics.json
        │   ├── predictions.parquet
        │   ├── confusion_matrix.png
        │   └── feature_importance.png
        ├── sgd_classifier/
        │   ├── model.joblib
        │   ├── metrics.json
        │   └── learning_curve.png
        └── torch_mlp/
            ├── model.pt
            ├── metrics.json
            ├── training_history.csv
            ├── loss_curve.png
            └── roc_curve.png
```

**Ожидаемый результат:** каждое обучение сохраняется как отдельная воспроизводимая сессия.

**Примерное время:** 6–10 часов.  
**Коммит:** `Add sandbox training sessions`

---

## 27.15. Реализовать графики и отчёты обучения

- [ ] Строить loss curve для neural network.
- [ ] Строить learning curve для моделей, где это возможно.
- [ ] Строить ROC curve.
- [ ] Строить precision-recall curve.
- [ ] Строить confusion matrix.
- [ ] Строить feature importance.
- [ ] Строить comparison chart по моделям.
- [ ] Строить распределение score.
- [ ] Строить calibration plot, если применимо.
- [ ] Сохранять графики PNG.
- [ ] Показывать графики в UI.
- [ ] Добавить export отчёта в HTML.

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

**Ожидаемый результат:** после обучения остаются не только модели, но и нормальные визуальные артефакты для анализа.

**Примерное время:** 8–12 часов.  
**Коммит:** `Add sandbox training reports`

---

## 27.16. Реализовать экспорт моделей

- [ ] Поддержать сохранение sklearn-моделей в `joblib`.
- [ ] Поддержать сохранение PyTorch-модели в `.pt`.
- [ ] Поддержать optional export PyTorch модели в ONNX.
- [ ] Поддержать optional export sklearn моделей в ONNX, если зависимости доступны.
- [ ] Сохранять export metadata.
- [ ] Проверять inference после сохранения.
- [ ] Сравнивать output до и после экспорта.
- [ ] Показывать validation status.
- [ ] Показывать список доступных моделей в UI.
- [ ] Не делать ONNX обязательным для всей песочницы.

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

**Ожидаемый результат:** модели всегда сохраняются, а ONNX используется как полезный экспорт, но не блокирует работу песочницы.

**Примерное время:** 6–10 часов.  
**Коммит:** `Add sandbox model export`

---

## 27.17. Реализовать генерацию тестовой команды

- [ ] Сделать страницу `Assignment Lab`.
- [ ] Генерировать отдельную текущую команду для проверки.
- [ ] Настраивать количество людей.
- [ ] Настраивать роли.
- [ ] Настраивать грейды.
- [ ] Настраивать текущую загрузку.
- [ ] Настраивать fatigue.
- [ ] Настраивать availability.
- [ ] Настраивать историю каждого сотрудника.
- [ ] Настраивать learning goals.
- [ ] Настраивать текущие активные задачи.
- [ ] Сохранять test case.
- [ ] Загружать test case из файла.
- [ ] Показывать команду в UI.

Файлы:

```text
sandbox_app/backend/data_generation/test_team.py
sandbox_app/backend/api/test_cases.py
```

Папка:

```text
sandbox_app/data/test_cases
```

Результат:

```text
sandbox_app/data/test_cases/<test_case_id>/team.json
sandbox_app/data/test_cases/<test_case_id>/active_tasks.json
sandbox_app/data/test_cases/<test_case_id>/history.json
sandbox_app/data/test_cases/<test_case_id>/metadata.json
```

**Ожидаемый результат:** можно создать отдельную реалистичную команду для проверки уже обученных моделей.

**Примерное время:** 6–10 часов.  
**Коммит:** `Add sandbox test team generator`

---

## 27.18. Реализовать проверку одной задачи

- [ ] Выбирать сохранённую модель.
- [ ] Выбирать test case.
- [ ] Выбирать одну задачу.
- [ ] Выбирать режим рекомендации.
- [ ] Строить пары task-employee.
- [ ] Прогонять пары через выбранную модель.
- [ ] Получать top candidates.
- [ ] Показывать top-1.
- [ ] Показывать top-3.
- [ ] Показывать score.
- [ ] Показывать факторы.
- [ ] Показывать риски.
- [ ] Показывать разные рекомендации для quality/speed/learning/balanced.
- [ ] Сохранять результат проверки.

Файлы:

```text
sandbox_app/backend/inference/recommend.py
sandbox_app/backend/inference/scoring.py
sandbox_app/backend/inference/risk_factors.py
sandbox_app/backend/api/recommendations.py
```

Recommendation modes:

```text
best_quality
fastest_delivery
best_learning
balanced
risk_aware
```

Результат:

```json
{
  "task_id": "TASK-001",
  "mode": "balanced",
  "top_candidates": [
    {
      "rank": 1,
      "employee_id": "EMP-001",
      "name": "Andrey",
      "score": 0.91,
      "factors": {
        "skill_match": 0.88,
        "quality": 0.92,
        "speed": 0.74,
        "fatigue_risk": 0.18,
        "workload_pressure": 0.22
      },
      "risks": []
    }
  ]
}
```

**Ожидаемый результат:** можно проверить, кому модель отдаст конкретную задачу и почему.

**Примерное время:** 8–12 часов.  
**Коммит:** `Add sandbox single task recommendation`

---

## 27.19. Реализовать массовое распределение todo-задач

- [ ] Выбирать модель.
- [ ] Выбирать test case.
- [ ] Брать все задачи в статусе `todo`.
- [ ] Настраивать режим распределения.
- [ ] Настраивать top-k.
- [ ] Настраивать максимальную загрузку на человека.
- [ ] Настраивать fairness penalty.
- [ ] Настраивать fatigue penalty.
- [ ] Настраивать learning bonus.
- [ ] Распределять задачи пачкой.
- [ ] Обновлять прогнозную загрузку после каждого назначения.
- [ ] Не назначать всё одному сильному человеку.
- [ ] Показывать итоговое распределение.
- [ ] Показывать перегруз.
- [ ] Показывать fairness.
- [ ] Показывать задачи без хорошего кандидата.
- [ ] Сохранять assignment session.

Файлы:

```text
sandbox_app/backend/inference/bulk_assignment.py
sandbox_app/backend/inference/assignment_optimizer.py
sandbox_app/backend/api/assignment_sessions.py
```

Режимы:

```text
maximize_quality
minimize_delivery_time
maximize_learning
balanced_distribution
risk_aware_distribution
```

Структура сессии:

```text
sandbox_app/assignment_sessions/
└── 2026-07-06_15-40-10_cd34ef/
    ├── assignment_config.json
    ├── recommendations.json
    ├── assigned_tasks.csv
    ├── unassigned_tasks.csv
    ├── workload_after_assignment.csv
    ├── fairness_report.json
    └── assignment_report.html
```

**Ожидаемый результат:** модель может разом распределить все todo-задачи среди команды с учётом качества, скорости, обучения, усталости и загрузки.

**Примерное время:** 12–20 часов.  
**Коммит:** `Add sandbox bulk assignment simulation`

---

## 27.20. Сделать визуальный вывод рекомендаций

- [ ] Показывать top candidates карточками.
- [ ] Показывать score breakdown.
- [ ] Показывать риски.
- [ ] Показывать режим рекомендации.
- [ ] Показывать сравнение кандидатов.
- [ ] Показывать канбан-доску после распределения.
- [ ] Показывать workload chart.
- [ ] Показывать fatigue chart.
- [ ] Показывать fairness chart.
- [ ] Показывать список задач без кандидата.
- [ ] Добавить фильтры по человеку, статусу, проекту, риску.
- [ ] Добавить export результатов.

UI blocks:

```text
Recommendation Cards
Candidate Comparison
Kanban Board
Workload After Assignment
Risks Panel
Fairness Panel
Unassigned Tasks
```

Файлы:

```text
sandbox_app/frontend/js/components/recommendation_cards.js
sandbox_app/frontend/js/components/candidate_comparison.js
sandbox_app/frontend/js/components/workload_chart.js
sandbox_app/frontend/js/components/fairness_chart.js
```

**Ожидаемый результат:** результаты работы модели понятны человеку, а не выглядят как сырой JSON.

**Примерное время:** 8–12 часов.  
**Коммит:** `Add sandbox recommendation UI`

---

## 27.21. Подключить Qwen/Ollama для объяснений

- [ ] Создать отдельный Ollama client внутри песочницы.
- [ ] Не использовать `src/llm/ollama_client.py` напрямую.
- [ ] Добавить настройки Ollama в `Settings`.
- [ ] Поддержать base URL.
- [ ] Поддержать model name.
- [ ] Поддержать timeout.
- [ ] Проверять доступность Ollama.
- [ ] Использовать Qwen только для объяснения.
- [ ] Запретить Qwen менять ranking.
- [ ] Запретить Qwen придумывать кандидатов.
- [ ] Передавать Qwen только готовый top-k и факторы.
- [ ] Добавить checkbox `LLM explanations`.
- [ ] Сделать fallback explanation без LLM.
- [ ] Валидировать, что объяснение упоминает только разрешённых кандидатов.
- [ ] Объяснять на русском языке.

Файлы:

```text
sandbox_app/backend/llm/ollama_client.py
sandbox_app/backend/llm/qwen_explainer.py
sandbox_app/backend/api/llm.py
```

Настройки:

```text
SANDBOX_OLLAMA_BASE_URL=http://localhost:11434
SANDBOX_OLLAMA_MODEL=qwen2.5:1.5b-instruct
SANDBOX_LLM_TIMEOUT_SECONDS=30
```

Правила prompt:

```text
Qwen не выбирает исполнителя.
Qwen не меняет ranking.
Qwen не придумывает людей.
Qwen не придумывает навыки.
Qwen объясняет только данные из top_candidates.
Qwen обязан объяснить top-1 и альтернативы.
```

**Ожидаемый результат:** по галочке можно включить русские LLM-объяснения рекомендаций через локальный Qwen.

**Примерное время:** 6–10 часов.  
**Коммит:** `Add sandbox Qwen explanations`

---

## 27.22. Реализовать импорт внешних данных

- [ ] Поддержать импорт CSV.
- [ ] Поддержать импорт JSON.
- [ ] Поддержать импорт Parquet.
- [ ] Импортировать employees.
- [ ] Импортировать tasks.
- [ ] Импортировать assignment history.
- [ ] Импортировать training pairs.
- [ ] Проверять обязательные поля.
- [ ] Показывать preview.
- [ ] Показывать warnings.
- [ ] Показывать ошибки схемы.
- [ ] Не перезаписывать файлы без подтверждения.
- [ ] Сохранять imported dataset отдельно.
- [ ] Позволять обучать модели на imported dataset.

Файлы:

```text
sandbox_app/backend/api/import_data.py
sandbox_app/backend/utils/importers.py
sandbox_app/backend/utils/validation.py
```

Папка:

```text
sandbox_app/data/imported
```

**Ожидаемый результат:** песочница работает не только с синтетикой, но и с внешними датасетами.

**Примерное время:** 8–12 часов.  
**Коммит:** `Add sandbox dataset import`

---

## 27.23. Добавить reports и exports

- [ ] Делать отчёт по генерации датасета.
- [ ] Делать отчёт по качеству датасета.
- [ ] Делать отчёт по обучению.
- [ ] Делать отчёт по сравнению моделей.
- [ ] Делать отчёт по рекомендациям.
- [ ] Делать отчёт по массовому распределению.
- [ ] Делать fairness report.
- [ ] Делать workload report.
- [ ] Экспортировать JSON.
- [ ] Экспортировать CSV.
- [ ] Экспортировать HTML.
- [ ] Показывать список отчётов в UI.

Папки:

```text
sandbox_app/reports
sandbox_app/data/exports
```

Файлы:

```text
sandbox_app/backend/reports/dataset_report.py
sandbox_app/backend/reports/model_report.py
sandbox_app/backend/reports/assignment_report.py
sandbox_app/backend/reports/html_export.py
```

**Ожидаемый результат:** результаты экспериментов можно сохранить, открыть и показать отдельно.

**Примерное время:** 8–12 часов.  
**Коммит:** `Add sandbox reports and exports`

---

## 27.24. Добавить настройки приложения

- [ ] Сделать страницу `Settings`.
- [ ] Настраивать пути хранения данных.
- [ ] Настраивать Ollama base URL.
- [ ] Настраивать Qwen model name.
- [ ] Настраивать default dataset size.
- [ ] Настраивать default recommendation mode.
- [ ] Настраивать default training models.
- [ ] Настраивать лимиты huge generation.
- [ ] Настраивать seed по умолчанию.
- [ ] Сохранять настройки в JSON.
- [ ] Добавить reset settings.

Файл:

```text
sandbox_app/config/app_settings.json
```

Пример настроек:

```json
{
  "server_port": 8601,
  "default_seed": 42,
  "default_domain_profile": "developers",
  "default_recommendation_mode": "balanced",
  "ollama_base_url": "http://localhost:11434",
  "ollama_model": "qwen2.5:1.5b-instruct",
  "max_preview_rows": 200,
  "huge_generation_requires_confirm": true
}
```

**Ожидаемый результат:** основные параметры песочницы можно менять без правки кода.

**Примерное время:** 4–6 часов.  
**Коммит:** `Add sandbox settings`

---

## 27.25. Протестировать полный pipeline

- [ ] Написать unit tests для генератора команды.
- [ ] Написать unit tests для генератора задач.
- [ ] Написать unit tests для генератора истории.
- [ ] Написать tests для custom feature schemas.
- [ ] Написать tests для feature builder.
- [ ] Написать training smoke test.
- [ ] Написать tests для сохранения training session.
- [ ] Написать tests для model loading.
- [ ] Написать tests для single recommendation.
- [ ] Написать tests для bulk assignment.
- [ ] Написать tests для Qwen fallback explanation.
- [ ] Написать smoke test запуска backend.
- [ ] Проверить сценарий end-to-end.

Файлы:

```text
sandbox_app/tests/test_team_generator.py
sandbox_app/tests/test_task_generator.py
sandbox_app/tests/test_history_generator.py
sandbox_app/tests/test_feature_schemas.py
sandbox_app/tests/test_feature_builder.py
sandbox_app/tests/test_training_smoke.py
sandbox_app/tests/test_model_loading.py
sandbox_app/tests/test_single_recommendation.py
sandbox_app/tests/test_bulk_assignment.py
sandbox_app/tests/test_llm_fallback.py
sandbox_app/tests/test_api_status.py
```

Команда:

```bash
pytest sandbox_app/tests
```

End-to-end сценарий:

```text
generate dataset
build features
train models
save training session
generate test team
run single recommendation
run bulk assignment
enable Qwen explanations
save assignment session
open reports
```

**Ожидаемый результат:** песочница работает автономно от генерации данных до объяснённого распределения задач.

**Примерное время:** 10–18 часов.  
**Коммит:** `Test sandbox end to end pipeline`

---

## 27.26. Задокументировать песочницу

- [ ] Создать полноценный `sandbox_app/README.md`.
- [ ] Описать назначение песочницы.
- [ ] Описать запуск.
- [ ] Описать остановку.
- [ ] Описать структуру папок.
- [ ] Описать генерацию команды.
- [ ] Описать генерацию задач.
- [ ] Описать custom feature schemas.
- [ ] Описать training datasets.
- [ ] Описать обучение моделей.
- [ ] Описать training sessions.
- [ ] Описать проверку одной задачи.
- [ ] Описать массовое распределение задач.
- [ ] Описать Qwen explanations.
- [ ] Описать reports.
- [ ] Описать ограничения.
- [ ] Добавить troubleshooting.

Файл:

```text
sandbox_app/README.md
```

Troubleshooting:

```text
Ollama is not running
Qwen model not found
Port 8601 is busy
Dataset is too large
Training session failed
Model cannot be loaded
ONNX Runtime is not installed
```

**Ожидаемый результат:** подпроект можно открыть отдельно и понять, как им пользоваться без чтения всего кода.

**Примерное время:** 5–8 часов.  
**Коммит:** `Document sandbox app`

---

## 27.27. Финальная проверка готовности этапа

- [ ] Папка `sandbox_app` полностью автономна.
- [ ] Приложение запускается через `scripts/start.sh`.
- [ ] Приложение открывается в браузере.
- [ ] UI сделан на HTML/CSS/JS.
- [ ] Backend работает на FastAPI.
- [ ] Можно генерировать команды.
- [ ] Можно генерировать задачи.
- [ ] Можно менять наборы признаков.
- [ ] Можно генерировать большие training datasets.
- [ ] Можно просматривать данные в таблицах и канбане.
- [ ] Можно обучать несколько моделей.
- [ ] Каждое обучение сохраняется как session.
- [ ] Модели сохраняются.
- [ ] Графики сохраняются PNG-файлами.
- [ ] Можно проверить одну задачу.
- [ ] Можно распределить все todo-задачи.
- [ ] Можно включить Qwen explanations по checkbox.
- [ ] Есть fallback explanation без LLM.
- [ ] Есть reports и exports.
- [ ] Есть tests.
- [ ] Есть README.

**Ожидаемый результат:** этап считается завершённым, когда песочница позволяет пройти полный цикл: сгенерировать данные, обучить модели, создать тестовую команду, распределить задачи и получить понятные объяснения.

**Примерное время:** 2–4 часа.  
**Коммит:** `Finalize sandbox app milestone`

---