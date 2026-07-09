# COMPASS AI Sandbox

COMPASS AI Sandbox — автономная локальная песочница внутри репозитория COMPASS-AI.

Песочница живёт в папке sandbox_app, запускается локально на FastAPI, открывается в браузере и не должна ломать основной COMPASS API. Она нужна для полного цикла экспериментов с распределением задач: настройка domain schemas, генерация команд и задач, создание истории выполненных задач, сборка training dataset, просмотр данных, обучение моделей, проверка рекомендаций, bulk assignment, reports, exports и русские Qwen/Ollama explanations.

## Главные принципы

- sandbox_app является отдельным подпроектом.
- Код песочницы не должен напрямую импортировать основной src.
- Код песочницы не должен напрямую импортировать основные LLM modules.
- Код песочницы не должен напрямую импортировать основные agents.
- Backend работает локально на 127.0.0.1:8601.
- UI сделан на HTML, CSS и Vanilla JS.
- Streamlit не используется.
- Python берётся из существующего .venv проекта.
- Целевая версия Python: 3.11.15.
- Runtime-файлы сохраняются внутри sandbox_app.
- Сгенерированные dataset, sessions, reports и logs не являются частью основного API.

## Быстрый запуск

Перейти в корень репозитория:

    cd /Users/andrey/Documents/projects/COMPASS-AI

Активировать окружение:

    source .venv/bin/activate

Запустить песочницу:

    bash sandbox_app/scripts/start.sh

Открыть приложение:

    http://127.0.0.1:8601

Остановить песочницу:

    bash sandbox_app/scripts/stop.sh

Перезапустить песочницу:

    bash sandbox_app/scripts/restart.sh

Запустить smoke test:

    bash sandbox_app/scripts/smoke_test.sh

Безопасно очистить runtime temporary files:

    bash sandbox_app/scripts/clean_tmp.sh

## Makefile targets

Доступные targets из корня репозитория:

    make sandbox-start
    make sandbox-stop
    make sandbox-restart
    make sandbox-test
    make sandbox-clean

## Структура папок

Основная структура подпроекта:

    sandbox_app/
      backend/
      frontend/
      config/
      scripts/
      data/
      training_sessions/
      assignment_sessions/
      reports/
      logs/
      docs/
      tests/

Назначение папок:

- backend содержит FastAPI application, API routers, data generation, features, training, inference, reports и LLM modules.
- frontend содержит browser UI на HTML, CSS и Vanilla JS.
- config содержит app settings, model presets, data contracts и feature schemas.
- scripts содержит запуск, остановку, restart, smoke test, очистку и Ollama helpers.
- data/generated содержит generated datasets.
- data/imported содержит imported datasets.
- data/test_cases содержит test cases для Assignment Lab.
- data/exports содержит exported report bundles.
- training_sessions содержит результаты обучения моделей.
- assignment_sessions содержит результаты bulk assignment.
- reports содержит HTML reports, PNG plots и manifests.
- logs содержит server logs, PID files и Ollama logs.
- docs содержит техническую документацию песочницы.
- tests содержит pytest tests для backend, frontend assets и end-to-end pipeline.

## Backend

Backend построен на FastAPI.

Основные endpoints:

    GET /api/health
    GET /api/status
    GET /api/config
    GET /api/sessions
    GET /api/docs

Config endpoints:

    GET /api/config/settings
    GET /api/config/model-presets
    GET /api/config/feature-schemas

Feature schemas endpoints:

    GET /api/feature-schemas
    GET /api/feature-schemas?preview=true
    GET /api/feature-schemas/template
    GET /api/feature-schemas/{profile_id}
    POST /api/feature-schemas
    PUT /api/feature-schemas/{profile_id}
    DELETE /api/feature-schemas/{profile_id}
    POST /api/feature-schemas/{profile_id}/features/{group}
    PATCH /api/feature-schemas/{profile_id}/features/{group}/{feature_name}
    DELETE /api/feature-schemas/{profile_id}/features/{group}/{feature_name}

Generation endpoints:

    POST /api/generate/team
    POST /api/generate/tasks
    POST /api/generate/history
    POST /api/generate/dataset

Data Viewer endpoints:

    GET /api/data-viewer/datasets
    GET /api/data-viewer/datasets/{dataset_id}/summary
    GET /api/data-viewer/datasets/{dataset_id}/{table_name}
    GET /api/data-viewer/datasets/{dataset_id}/employees/{employee_id}
    GET /api/data-viewer/datasets/{dataset_id}/tasks/{task_id}
    GET /api/data-viewer/datasets/{dataset_id}/employees/{employee_id}/history
    GET /api/data-viewer/datasets/{dataset_id}/kanban

Import endpoints:

    GET /api/import-data/supported-tables
    POST /api/import-data/preview
    POST /api/import-data/datasets

Features endpoints:

    POST /api/features/build
    GET /api/features/datasets/{dataset_id}/metadata

Training endpoints:

    POST /api/training/run
    GET /api/training/sessions
    GET /api/training/sessions/{session_id}
    GET /api/training/sessions/{session_id}/artifacts
    GET /api/training/sessions/{session_id}/models/{model_name}

Models endpoints:

    GET /api/models
    GET /api/models/{session_id}/{model_name}
    GET /api/models/{session_id}/{model_name}/validation
    POST /api/models/{session_id}/{model_name}/validate
    POST /api/models/{session_id}/{model_name}/export
    POST /api/models/{session_id}/{model_name}/predict

Test cases endpoints:

    GET /api/test-cases
    POST /api/test-cases/generate
    POST /api/test-cases/import
    GET /api/test-cases/{test_case_id}
    GET /api/test-cases/{test_case_id}/summary
    GET /api/test-cases/{test_case_id}/tables/{table_name}
    GET /api/test-cases/{test_case_id}/pending-tasks
    GET /api/test-cases/{test_case_id}/recommendation-context
    DELETE /api/test-cases/{test_case_id}

Recommendation endpoints:

    GET /api/recommendations/modes
    GET /api/recommendations/test-cases/{test_case_id}/tasks
    POST /api/recommendations/single
    GET /api/recommendations/test-cases/{test_case_id}
    GET /api/recommendations/test-cases/{test_case_id}/{recommendation_id}

Assignment endpoints:

    GET /api/assignment-sessions/modes
    POST /api/assignment-sessions/run
    GET /api/assignment-sessions
    GET /api/assignment-sessions/{assignment_session_id}
    GET /api/assignment-sessions/{assignment_session_id}/files/{file_name}

LLM endpoints:

    GET /api/llm/status
    POST /api/llm/explain/recommendation
    POST /api/llm/explain/assignment
    POST /api/llm/explain/assignment-sessions/{assignment_session_id}

Reports and exports endpoints:

    GET /api/reports/exports
    GET /api/reports/exports/{report_id}
    GET /api/reports/exports/{report_id}/files/{file_name}
    POST /api/reports/exports/datasets/{dataset_id}
    POST /api/reports/exports/models/{session_id}
    POST /api/reports/exports/assignments/{assignment_session_id}

Settings endpoints:

    GET /api/settings
    PUT /api/settings
    PATCH /api/settings
    POST /api/settings/reset
    GET /api/settings/schema

## Frontend

Frontend находится в sandbox_app/frontend.

Основные страницы:

- Dashboard
- Data Generator
- Data Viewer
- Import Data
- Training
- Models
- Assignment Lab
- Reports
- Settings

Frontend работает как browser UI без Streamlit. Backend отдаёт index.html, CSS, JS, assets и SPA fallback.

## Data contracts

Data contracts описывают форматы данных, которые используются внутри песочницы.

Основные contracts:

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

Contracts фиксируют required fields, optional fields, allowed statuses, outcome labels, recommendation modes, target modes и session statuses.

Документация:

    sandbox_app/docs/data_contracts.md

Config:

    sandbox_app/config/data_contracts/data_contracts.json

## Feature schemas

Feature schemas описывают домен, роли, грейды, навыки, task types и custom features.

Встроенные profiles:

- developers
- designers

Свободный profile:

- custom

Feature schema может содержать:

- roles
- grades
- skills
- task_types
- employee feature definitions
- task feature definitions
- outcome feature definitions

Поддерживаемые feature types:

- numeric
- categorical
- boolean
- text
- skill_list

Документация:

    sandbox_app/docs/feature_schemas.md

Config examples:

    sandbox_app/config/feature_schemas/developers.json
    sandbox_app/config/feature_schemas/designers.json
    sandbox_app/config/feature_schemas/custom.json

## Custom schema editor

Страница Settings содержит editor feature schemas.

Через UI можно:

- создать custom domain profile
- открыть schema preview
- редактировать roles
- редактировать grades
- редактировать skills
- добавлять employee features
- добавлять task features
- добавлять outcome features
- удалять features
- сохранять schemas через API

Системные profiles developers и designers защищены от удаления.

## Генерация команды

Team generator создаёт employees для выбранного domain_profile.

Настраивается:

- employees_count
- seed
- roles
- grades
- skills
- workload
- fatigue
- availability
- learning goals
- skill count per person
- seniority distribution

Результаты:

    sandbox_app/data/generated/<dataset_id>/employees.json
    sandbox_app/data/generated/<dataset_id>/employees.csv
    sandbox_app/data/generated/<dataset_id>/team_metadata.json

Endpoint:

    POST /api/generate/team

## Генерация задач

Task generator создаёт tasks и backlog для выбранного domain_profile.

Настраивается:

- tasks_count
- projects_count
- task_types
- priorities
- complexity
- estimated_hours
- deadline_days
- required skills
- dependencies
- skill mismatch probability
- status distribution
- priority distribution

Результаты:

    sandbox_app/data/generated/<dataset_id>/tasks.json
    sandbox_app/data/generated/<dataset_id>/tasks.csv
    sandbox_app/data/generated/<dataset_id>/backlog.json
    sandbox_app/data/generated/<dataset_id>/backlog.csv
    sandbox_app/data/generated/<dataset_id>/task_metadata.json

Endpoint:

    POST /api/generate/tasks

## Генерация истории

History generator создаёт assignment_history.

Учитывается:

- skill match
- workload
- fatigue
- complexity
- grade
- learning goals
- planned hours
- actual hours
- quality score
- deadline status
- rework
- feedback score

Результаты:

    sandbox_app/data/generated/<dataset_id>/assignment_history.json
    sandbox_app/data/generated/<dataset_id>/assignment_history.csv
    sandbox_app/data/generated/<dataset_id>/history_metadata.json

Endpoint:

    POST /api/generate/history

## Full dataset generation

Full dataset generator одной операцией создаёт:

- employees
- tasks
- backlog
- assignment_history
- training_pairs
- dataset_metadata
- generation_report

Modes:

- small_preview
- medium_validation
- large_training
- huge_training

Huge generation требует явного confirm_huge_generation.

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

Endpoint:

    POST /api/generate/dataset

## Imported datasets

Import Data поддерживает:

- CSV
- JSON
- Parquet

Можно импортировать:

- employees
- tasks
- assignment_history
- training_pairs

Imported datasets сохраняются отдельно:

    sandbox_app/data/imported

Перед сохранением выполняется validation required fields через data contracts. Preview показывает rows, columns, warnings, validation errors и первые records.

## Data Viewer

Data Viewer показывает generated и imported datasets.

Поддерживает:

- summary cards
- simple charts
- employees table
- tasks table
- assignment_history table
- training_pairs table
- pagination
- search
- filters
- employee profile
- task profile
- employee history
- kanban board

Data Viewer нужен, чтобы изучать данные глазами без ручного открытия CSV и Parquet файлов.

## Feature builder

Feature builder превращает dataset в признаки для обучения.

Поддерживает:

- generated datasets
- imported datasets
- employees
- tasks
- assignment_history
- training_pairs
- custom employee features
- custom task features
- skill vectors
- pair features
- workload features
- fatigue features
- learning potential features
- target modes

Результаты:

    sandbox_app/data/generated/<dataset_id>/features/features.parquet
    sandbox_app/data/generated/<dataset_id>/features/targets.parquet
    sandbox_app/data/generated/<dataset_id>/features/feature_metadata.json

Endpoints:

    POST /api/features/build
    GET /api/features/datasets/{dataset_id}/metadata

## Обучение моделей

Training backend обучает несколько моделей за один запуск.

Поддерживаемые models:

- baseline_rule_based
- sgd_classifier
- logistic_regression
- random_forest
- hist_gradient_boosting
- torch_mlp

Метрики:

- roc_auc
- f1
- precision
- recall
- accuracy
- log_loss
- mae_for_score
- top_1_accuracy
- top_3_accuracy

Training может автоматически построить features перед запуском.

Endpoint:

    POST /api/training/run

## Training sessions

Каждый training run создаёт отдельную session.

Структура session:

    sandbox_app/training_sessions/<session_id>/
      session_config.json
      dataset_metadata.json
      feature_metadata.json
      session_summary.json
      comparison_metrics.csv
      comparison_metrics.json
      models/

Для каждой модели сохраняется:

    model.joblib
    model.pt
    predictions.parquet
    metrics.json
    model_metadata.json
    export_validation.json

Конкретный artifact зависит от типа модели.

## Model export

Model export работает поверх saved training sessions.

Поддерживается:

- native joblib для sklearn и baseline models
- native pt для PyTorch MLP
- optional ONNX export
- native validation
- predict endpoint

ONNX не является обязательной зависимостью. Если ONNX runtime или export dependencies не установлены, export корректно помечается как skipped.

## Training plots и reports

Training reports строятся из сохранённых training sessions.

Генерируются:

- loss curve для PyTorch
- learning curve
- ROC curve
- precision-recall curve
- confusion matrix
- feature importance
- model comparison chart
- score distribution
- calibration plot
- training_report.html
- report_manifest.json

Reports доступны на странице Reports.

## Test team

Test team generator создаёт отдельный test case для проверки моделей.

Создаётся:

- team.json
- active_tasks.json
- history.json
- metadata.json

Настраивается:

- people count
- roles
- grades
- current workload
- fatigue
- availability
- history depth
- learning goals
- active tasks count

Test cases сохраняются в:

    sandbox_app/data/test_cases

## Single recommendation

Single recommendation проверяет, кому модель отдаст конкретную задачу.

Пользователь выбирает:

- saved model
- training session
- test case
- task
- recommendation mode

Backend строит task-employee pairs, прогоняет их через модель, пересчитывает score под режим рекомендации и возвращает top candidates.

Результат содержит:

- top candidates
- top-1
- top-3
- score
- factors
- matched skills
- missing skills
- risks
- risk summary

Recommendation modes:

- best_quality
- fastest_delivery
- best_learning
- balanced
- risk_aware

## Bulk assignment

Bulk assignment распределяет пачку todo задач.

Настраивается:

- assignment mode
- top_k
- max workload per person
- fairness penalty
- fatigue penalty
- learning bonus
- workload penalty

Backend обновляет projected workload после каждого назначения и не должен назначать всё одному сильному человеку.

Результаты session:

    assignment_config.json
    recommendations.json
    assigned_tasks.csv
    unassigned_tasks.csv
    workload_after_assignment.csv
    fairness_report.json
    assignment_report.html
    session_summary.json

Папка:

    sandbox_app/assignment_sessions/<session_id>

## Qwen и Ollama explanations

Qwen используется только для объяснений.

Ограничения:

- Qwen не меняет ranking.
- Qwen не меняет scores.
- Qwen не придумывает candidates.
- Qwen не придумывает skills.
- Qwen получает только готовые top-k, factors, risks, assignments и fairness metrics.
- Ответ валидируется.
- Если Ollama недоступен, используется fallback explanation на русском языке.

Настройки:

    SANDBOX_OLLAMA_BASE_URL=http://localhost:11434
    SANDBOX_OLLAMA_MODEL=qwen2.5:1.5b-instruct
    SANDBOX_LLM_TIMEOUT_SECONDS=30
    SANDBOX_OLLAMA_AUTO_PULL=1

Скрипты:

    bash sandbox_app/scripts/start_ollama.sh
    bash sandbox_app/scripts/stop_ollama.sh

Основной start.sh поднимает Ollama перед запуском backend. stop.sh останавливает backend и Ollama.

## Reports и exports

Reports UI показывает export bundles.

Доступные exports:

- dataset report
- dataset quality report
- model report
- model comparison report
- recommendation report
- bulk assignment report
- fairness report
- workload report

Форматы:

- JSON
- CSV
- HTML

Report bundle содержит:

    report.json
    report.html
    report_manifest.json
    CSV tables

Папки:

    sandbox_app/reports
    sandbox_app/data/exports

## Settings

Settings page позволяет редактировать app settings и schemas.

Настраивается:

- paths
- default seed
- default domain profile
- default dataset mode
- default recommendation mode
- default training models
- huge generation limits
- Ollama base URL
- Qwen model name

Settings сохраняются в:

    sandbox_app/config/app_settings.json

Важно: app_settings.json содержит isolation flags, которые защищают основной COMPASS API и сохраняют совместимость с core settings loader.

## Полный browser pipeline

Ручной end-to-end сценарий:

1. Открыть browser app.
2. Создать custom schema.
3. Сгенерировать full dataset.
4. Открыть Data Viewer.
5. Построить features.
6. Обучить models.
7. Сохранить training session.
8. Открыть model session.
9. Сгенерировать test team.
10. Запустить single recommendation.
11. Запустить bulk assignment.
12. Включить Qwen explanations.
13. Сохранить assignment session.
14. Открыть Reports.
15. Сделать exports.

Checklist:

    sandbox_app/docs/end_to_end_pipeline_checklist.md

## Проверки

Полная проверка tests:

    pytest sandbox_app/tests

Проверка Python imports:

    python -m compileall -q sandbox_app/backend sandbox_app/tests

Проверка JSON settings:

    python -m json.tool sandbox_app/config/app_settings.json >/dev/null

Проверка ruff, если установлен:

    python -m ruff check sandbox_app

Проверка JavaScript, если установлен Node.js:

    node --check sandbox_app/frontend/js/app.js
    node --check sandbox_app/frontend/js/api.js

Smoke test:

    bash sandbox_app/scripts/smoke_test.sh

## Ограничения

- Песочница предназначена для локального использования.
- Backend должен быть доступен только на 127.0.0.1.
- Huge datasets могут занимать много времени, памяти и места на диске.
- ONNX export optional.
- Ollama и Qwen optional для объяснений.
- Без Ollama работает fallback explanation.
- Browser может показывать старый JS из cache.
- Generated runtime files не должны попадать в основной код приложения.
- Sandbox не является заменой основного COMPASS API.
- Sandbox не должен менять основной COMPASS API.

## Troubleshooting

### Port 8601 is busy

Порт занят другим процессом.

Что сделать:

    bash sandbox_app/scripts/stop.sh

Потом снова:

    bash sandbox_app/scripts/start.sh

Если процесс не относится к sandbox, остановить его вручную и повторить запуск.

### Python is not from .venv

start.sh требует Python из окружения проекта.

Что сделать:

    source .venv/bin/activate

Потом:

    bash sandbox_app/scripts/start.sh

### FastAPI is not installed

Окружение не содержит backend dependency.

Что сделать:

    python -c "import fastapi"

Если import падает, установить зависимости sandbox_app из существующего окружения проекта по правилам проекта.

### PyArrow is not installed

Parquet требует PyArrow.

Что проверить:

    python -c "import pyarrow"

Если import падает, training_pairs.parquet, features.parquet и predictions.parquet работать не будут.

### Dataset is too large

Huge generation может быть тяжёлой.

Что сделать:

- использовать small_preview для проверки
- использовать medium_validation для обычной validation
- запускать huge_training только с confirm_huge_generation
- проверить свободное место на диске
- не открывать большие Parquet файлы вручную

### Feature schema is invalid

Schema должна иметь валидный profile_id, roles, grades, skills, task_types и feature_groups.

Что сделать:

- открыть Settings
- открыть schema preview
- проверить feature names
- проверить feature types
- проверить categorical values
- сохранить schema через UI

### Training session failed

Training зависит от dataset, features и selected models.

Что сделать:

- открыть Data Viewer и проверить dataset
- построить features на странице Training
- проверить feature_metadata
- запустить baseline_rule_based отдельно
- потом добавить другие models

### Model cannot be loaded

Model loader требует сохранённые artifacts и metadata.

Что сделать:

- открыть Models
- выбрать training session
- проверить model_metadata.json
- нажать Validate model
- проверить export_validation status

### ONNX Runtime is not installed

ONNX optional.

Что сделать:

- использовать native joblib или pt artifact
- запускать ONNX export только если dependencies установлены
- считать skipped нормальным статусом для optional ONNX

### Ollama is not running

Qwen explanations требуют Ollama.

Что сделать:

    bash sandbox_app/scripts/start_ollama.sh

Проверить:

    curl -fsS http://127.0.0.1:8601/api/llm/status

Если Ollama недоступен, sandbox вернёт fallback explanation.

### Qwen model not found

Нужна модель qwen2.5:1.5b-instruct.

Что сделать:

    bash sandbox_app/scripts/start_ollama.sh

start_ollama.sh проверяет модель и при включённом auto pull пытается скачать её через Ollama CLI.

### Browser shows old JS after cache

Браузер может держать старую версию app.js или page module.

Что сделать:

- открыть URL с query параметром v
- сделать hard reload
- очистить cache для 127.0.0.1:8601
- перезапустить backend

Пример URL:

    http://127.0.0.1:8601/?v=sandbox-readme-refresh

## Статус готовности

Sandbox считается рабочим, когда можно пройти полный цикл:

1. Настроить domain schema.
2. Сгенерировать dataset.
3. Открыть dataset в Data Viewer.
4. Построить features.
5. Обучить несколько models.
6. Сохранить training session.
7. Создать test team.
8. Запустить single recommendation.
9. Запустить bulk assignment.
10. Включить Qwen explanations.
11. Открыть reports.
12. Экспортировать results.
13. Пройти pytest sandbox_app/tests.
14. Пройти smoke_test.sh.