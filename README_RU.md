<div align="center">

<img src="assets/forreadme/logo.png" alt="Логотип COMPASS AI" width="300"/>

# COMPASS AI

**Competency-Oriented Matching & Project Assignment Support System**

**Система поддержки назначения проектов по компетенциям**

[![Русский](https://img.shields.io/badge/README_Language-Русский-brightgreen)](https://github.com/TheAndreyZakharov/COMPASS-AI/blob/main/README_RU.md)
[![English](https://img.shields.io/badge/README_Language-English-blue)](https://github.com/TheAndreyZakharov/COMPASS-AI/blob/main/README.md)

</div>

COMPASS AI — это локальная AI-система для назначения задач по компетенциям сотрудников, загрузке, риску выполнения и целям развития.

Проект содержит два связанных продуктовых слоя:

- **COMPASS AI Sandbox** — автономное локальное browser-приложение для генерации синтетических данных, просмотра датасетов, обучения моделей, проверки рекомендаций, Kanban-экспериментов, отчетов и экспорта моделей.
- **COMPASS AI + Plane** — интеграционный слой для работы с реальной open-source системой управления проектами Plane и применения той же логики назначения к проектным задачам и участникам команды.

Система сделана как серьезный ML/AI-прототип для изучения task-to-employee matching, объяснимости рекомендаций, fairness-рисков, загрузки команды и локальных AI-workflows.

## Основная идея

COMPASS AI помогает тимлиду решить, кому следует назначить задачу.

Система анализирует:

- тип задачи, приоритет, сложность и оценку трудозатрат;
- требуемые навыки и технологические теги;
- проектный контекст и давление дедлайна;
- роль, грейд и навыки сотрудника;
- текущую загрузку и усталость;
- историю прошлых назначений;
- качество, скорость и надежность дедлайнов;
- цели развития и learning potential.

На выходе система формирует ранжированный список кандидатов с числовыми оценками, рисками, контекстом нагрузки и объяснением, которое может быть сгенерировано локальной LLM.

## Основные возможности

COMPASS AI поддерживает:

- настраиваемые domain profiles для разработчиков, дизайнеров или любого custom-домена;
- генерацию сотрудников, задач, истории задач и training pairs;
- хранение датасетов в CSV, JSON и Parquet;
- browser-based просмотр датасетов с таблицами, сводками, графиками и Kanban-видами;
- обучение нескольких моделей на сгенерированных или импортированных данных;
- сравнение моделей, проверку и optional ONNX export;
- рекомендацию по одной задаче и массовое распределение задач;
- локальные LLM-объяснения через Ollama и Qwen;
- отчеты по назначениям, моделям и датасетам;
- Kanban Lab для изолированных экспериментов над копиями данных;
- интеграцию с Plane для реальных project-management workflows;
- Streamlit dashboard для Plane, synthetic data и model metrics.

## AI и модельный слой

Исходное направление проекта — нейронная matching-модель `TaskEmployeeMatchingNet`, которая предсказывает вероятность успешного назначения задачи для пары `task + employee`.

В sandbox также обучаются и сравниваются несколько практических моделей:

- `baseline_rule_based`;
- `sgd_classifier`;
- `logistic_regression`;
- `random_forest`;
- `hist_gradient_boosting`;
- `torch_mlp`.

Локальный слой объяснений использует Ollama. Настроенная модель:

```text
qwen2.5:1.5b-instruct
```

Эта модель выбрана потому, что она компактная, достаточно быстрая для локальной работы, подходит для легких машин и дает приемлемые объяснения на русском языке.

## Как это работает

Общая схема обработки:

```text
Датасет или задача из Plane
        ↓
Признаки задачи и сотрудника
        ↓
Оценка model scoring для пар task-employee
        ↓
Ранжирование кандидатов
        ↓
Проверка нагрузки, риска и fairness
        ↓
Опциональное объяснение Qwen/Ollama
        ↓
Рекомендация, assignment session или отчет
```

## Локальный запуск

### Запуск Sandbox

Sandbox — это автономное локальное приложение внутри `sandbox_app`.

Запуск:

```bash
bash sandbox_app/scripts/start.sh
```

Остановка:

```bash
bash sandbox_app/scripts/stop.sh
```

Скрипты запускают и останавливают локальные сервисы, нужные для sandbox, включая backend и Ollama-flow там, где он используется.

Стандартный URL sandbox:

```text
http://127.0.0.1:8601
```

Документация API sandbox:

```text
http://127.0.0.1:8601/api/docs
```

### Запуск Plane stack

Plane-integrated stack запускается через VS Code tasks.

Открой command palette:

```text
Cmd + Shift + P
```

Затем запусти:

```text
Tasks: Run Task
COMPASS: start stack
```

Остановка:

```text
Tasks: Run Task
COMPASS: stop stack
```

Start task запускает Plane, Ollama, COMPASS API и dashboard. Stop task останавливает локальные процессы и вспомогательные приложения, которые используются stack.

Стандартные URL:

```text
COMPASS API:       http://localhost:8000
COMPASS Dashboard: http://localhost:8501
Plane:             http://localhost
```

## COMPASS AI Sandbox

Sandbox — это основная экспериментальная среда. Она может создать полный synthetic dataset, обучить модели, проверить рекомендации и запускать изолированные Kanban-эксперименты без изменения исходного датасета.

### Главный экран

<div align="center">

<img src="assets/forreadme/1.png" alt="Главный экран COMPASS AI Sandbox" width="600"/>

</div>

Главный экран содержит sidebar с основными разделами и индикатором состояния backend. В верхнем header находятся кнопки смены языка, смены темы, обновления, справки и API. Кнопка API открывает `/api/docs`. В основной области показан рекомендуемый workflow: создать датасет, обучить модели и протестировать назначения. Также отображаются состояние системы, созданные датасеты, модели и другие runtime-счетчики.

### Тема, язык и обновление

<div align="center">

<img src="assets/forreadme/2.png" alt="Темная тема и русский интерфейс COMPASS AI Sandbox" width="600"/>

</div>

Интерфейс поддерживает русский и английский языковые режимы, светлую и темную темы, а также refresh action, который обновляет данные страницы без выхода из текущего раздела.

### Уведомления и прогресс

<div align="center">

<img src="assets/forreadme/3.jpeg" alt="Уведомления и progress bars в COMPASS AI Sandbox" width="600"/>

</div>

Короткие уведомления и уведомления долгих процессов отображаются в правом нижнем углу. Генерация датасета, обучение моделей и другие долгие операции используют закрепленные progress notifications с progress bar и текстом статуса.

### Контекстная справка

<div align="center">

<img src="assets/forreadme/4.png" alt="Панель справки COMPASS AI Sandbox" width="600"/>

</div>

Кнопка информации в header открывает контекстную справку для текущего экрана. Она объясняет назначение раздела и ожидаемые действия пользователя.

### Генерация данных

<div align="center">

<img src="assets/forreadme/5.png" alt="Экран генерации данных COMPASS AI Sandbox" width="600"/>

</div>

Раздел генерации данных может создавать примерные датасеты для разработчиков и дизайнеров. Важный режим — custom domain profile: пользователь может адаптировать роли, грейды, навыки, типы задач и custom fields под конкретную компанию или проект. Размеры датасета включают small preview, medium validation, large training и huge training. Пресет управляет количеством сотрудников, задач, строк истории и training pairs, но пользователь может вручную изменить значения. Для воспроизводимой генерации можно указать seed.

### Custom developer preset

<div align="center">

<img src="assets/forreadme/6.png" alt="Custom developer generation preset в COMPASS AI Sandbox" width="400"/>

</div>

В этом примере показан custom preset для большой команды разработчиков. Такой же preset описан в `docs/sandbox27.md`. Custom preset можно сохранить, редактировать и использовать повторно. Полный датасет создается действием `Создать полный датасет`, а отдельные действия могут создать только сотрудников, задачи или историю.

### Просмотр данных

<div align="center">

<img src="assets/forreadme/7.png" alt="Просмотр данных COMPASS AI Sandbox" width="600"/>

</div>

Data Viewer показывает все generated и imported datasets. Выбранный датасет можно смотреть по типам таблиц: сотрудники, задачи, история назначений и training pairs. В этом же разделе можно удалить датасет.

### Сводка датасета и таблицы

<table>
  <tr>
    <td align="center"><strong>Сводка датасета</strong><br/><img src="assets/forreadme/8.png" alt="Сводка датасета" width="600"/></td>
    <td align="center"><strong>Таблица сотрудников</strong><br/><img src="assets/forreadme/9.png" alt="Таблица сотрудников" width="600"/></td>
  </tr>
  <tr>
    <td align="center"><strong>Таблица задач</strong><br/><img src="assets/forreadme/10.png" alt="Таблица задач" width="600"/></td>
    <td align="center"><strong>История назначений</strong><br/><img src="assets/forreadme/11.png" alt="Таблица истории назначений" width="600"/></td>
  </tr>
</table>

Summary view дает общую картину датасета. Table views позволяют напрямую проверить сотрудников, задачи и историю выполнения задач.

<div align="center">

<img src="assets/forreadme/12.png" alt="Таблица training pairs" width="600"/>

</div>

Training pairs показывают комбинации task-candidate, которые используются для обучения моделей.

### Графики и Kanban в Data Viewer

<div align="center">

<img src="assets/forreadme/13.png" alt="Сотрудники и задачи в виде графиков" width="600"/>

</div>

Chart view помогает проверить распределения сотрудников и задач.

<div align="center">

<img src="assets/forreadme/14.png" alt="Task Kanban и task summary" width="600"/>

</div>

Kanban view группирует задачи по статусам и показывает сводную информацию по задачам.

### Импорт данных

<div align="center">

<img src="assets/forreadme/15.png" alt="Импорт данных COMPASS AI Sandbox" width="600"/>

</div>

Раздел импорта может загружать внешние данные в поддерживаемых форматах. Imported datasets хранятся отдельно от generated datasets и могут использоваться на следующих этапах workflow.

### Обучение моделей

<div align="center">

<img src="assets/forreadme/16.png" alt="Экран обучения моделей COMPASS AI Sandbox" width="600"/>

</div>

Раздел обучения выбирает датасет, лимиты training pairs, split ratios и параметры моделей. Пользователь может обучить все шесть доступных моделей или выбрать часть. Процесс обучения создает session с artifacts, metrics и reports.

### Результаты training session

<div align="center">

<img src="assets/forreadme/17.png" alt="Результаты training session COMPASS AI Sandbox" width="600"/>

</div>

После обучения session можно выбрать, посмотреть и удалить. Интерфейс показывает session metadata, model metrics и model comparison.

### Training plots

<div align="center">

<img src="assets/forreadme/18.png" alt="Сгенерированные model plots COMPASS AI Sandbox" width="600"/>

</div>

Generated plots включают график сравнения моделей и диагностические per-model plots.

<div align="center">

<img src="assets/forreadme/19.png" alt="Детальные generated plots COMPASS AI Sandbox" width="400"/>

</div>

Plots можно просматривать в любое время, пока существует training session.

### Модели

<div align="center">

<img src="assets/forreadme/20.png" alt="Экран моделей COMPASS AI Sandbox" width="600"/>

</div>

Раздел Models показывает детали training session, проверяет сохраненные модели и может экспортировать поддерживаемые модели в ONNX.

### Assignment Lab

<div align="center">

<img src="assets/forreadme/21.png" alt="Assignment Lab COMPASS AI Sandbox" width="600"/>

</div>

Раздел назначений создает test set из датасета, выбирает training session и модель, настраивает recommendation modes и опционально включает LLM explanations. Он может рекомендовать кандидатов для одной задачи или распределить все подходящие задачи по команде с учетом компетенций, загрузки и риска.

### Обзор рекомендации по одной задаче

<div align="center">

<img src="assets/forreadme/22.png" alt="Обзор рекомендации по одной задаче COMPASS AI Sandbox" width="400"/>

</div>

Результат рекомендации начинается с требований задачи, затем показывает top candidates, candidate metrics, numeric comparison, LLM explanation и fit chart, который сравнивает требования задачи с возможностями кандидатов.

### Детали рекомендации

<div align="center">

<img src="assets/forreadme/23.png" alt="Требования задачи и лучшие кандидаты" width="600"/>

</div>

Первый detail block показывает требования задачи и кандидатов с самым высоким ranking.

<div align="center">

<img src="assets/forreadme/24.png" alt="Сравнение кандидатов по числовым характеристикам" width="600"/>

</div>

Comparison section показывает свойства кандидатов, scores и различия.

<div align="center">

<img src="assets/forreadme/25.png" alt="LLM recommendation и fit chart" width="600"/>

</div>

Explanation section показывает структурированный LLM-ответ и график, который сравнивает требуемые свойства задачи с сильными сторонами кандидатов.

## Kanban Lab

Kanban Lab — это изолированное экспериментальное пространство. Оно работает с копией датасета или test set. Исходный generated dataset не изменяется. Пользователь может удалять задачи, добавлять ручные задачи, редактировать команду, сохранять измененные доски и считать рекомендации для текущего состояния доски.

### Источник лаборатории и сохраненные доски

<div align="center">

<img src="assets/forreadme/26.png" alt="Управление источником Kanban Lab COMPASS AI Sandbox" width="600"/>

</div>

Пользователь выбирает датасет, test set, training session, модель, число кандидатов и режим LLM explanation. Новую lab copy можно загрузить из датасета, либо можно загрузить ранее сохраненную измененную доску. Текущие изменения можно сохранить как отдельную lab board. Saved boards хранятся отдельно в `sandbox_app/data/kanban_lab`.

### Ручное создание задачи

<div align="center">

<img src="assets/forreadme/27.png" alt="Ручное создание задачи COMPASS AI Sandbox" width="600"/>

</div>

Ручное создание задачи использует существующие task types, projects и skills из текущего датасета. Это предотвращает invalid tags и сохраняет задачу понятной для обученных моделей.

### Редактирование команды вручную

<div align="center">

<img src="assets/forreadme/28.png" alt="Ручное редактирование команды COMPASS AI Sandbox" width="600"/>

</div>

Команду также можно редактировать внутри lab copy. Пользователь может добавить нового сотрудника с ролью, грейдом, нагрузкой, доступностью, скоростью, качеством и навыками или удалить выбранных сотрудников. Эти изменения влияют только на lab copy.

### Операции с Kanban board

<div align="center">

<img src="assets/forreadme/29.png" alt="Операции с Kanban board COMPASS AI Sandbox" width="600"/>

</div>

Kanban board содержит скопированные задачи. Отдельные карточки можно перетаскивать между колонками. Целые колонки можно переносить в другой статус или очищать. Каждая карточка показывает identifiers задачи, приоритет, effort и required skills.

### Рекомендации на Kanban cards

<div align="center">

<img src="assets/forreadme/30.png" alt="Kanban recommendations COMPASS AI Sandbox" width="600"/>

</div>

После применения состояния Kanban и расчета рекомендаций каждая task card может показать top candidates для этой задачи.

### Детали Kanban recommendation

<div align="center">

<img src="assets/forreadme/31.png" alt="Детальная Kanban recommendation COMPASS AI Sandbox" width="400"/>

</div>

Detailed panel показывает requirements, candidates, numeric comparison, LLM explanation и fit chart для выбранной Kanban task.

<div align="center">

<img src="assets/forreadme/32.png" alt="Требования Kanban task и candidate match" width="600"/>

</div>

Этот view фокусируется на требованиях задачи, совпавших навыках и missing skills.

<div align="center">

<img src="assets/forreadme/33.png" alt="Kanban LLM explanation и fit chart" width="600"/>

</div>

LLM section объясняет пригодность кандидатов обычным языком, а chart визуализирует соответствие.

<div align="center">

<img src="assets/forreadme/34.png" alt="Полный рабочий экран Kanban Lab COMPASS AI Sandbox" width="600"/>

</div>

Kanban Lab предназначен для практических экспериментов с текущими задачами, кадровыми предположениями и поведением моделей.

### Отчеты

<div align="center">

<img src="assets/forreadme/35.png" alt="Экран отчетов COMPASS AI Sandbox" width="600"/>

</div>

Раздел Reports генерирует отчеты по датасетам, обученным моделям и assignment sessions. Отчеты можно открыть и удалить из интерфейса.

<div align="center">

<img src="assets/forreadme/36.png" alt="Сводка отчета COMPASS AI Sandbox" width="600"/>

</div>

Report summaries дают компактный обзор сгенерированных artifacts и results.

### Настройки

<div align="center">

<img src="assets/forreadme/37.png" alt="Экран настроек COMPASS AI Sandbox" width="600"/>

</div>

Settings включают default values, seeds, timeouts, LLM parameters, storage paths, schemas и domain profiles.

## Интеграция с Plane и dashboard

Plane используется потому, что это open source и он предоставляет практическую project-management среду для issues, projects, members и task workflows. Интеграцию можно адаптировать под другую HRM или project-management system, если конкретной организации нужен другой источник данных.

### Главный экран Plane

<div align="center">

<img src="assets/forreadme/101.png" alt="Главный экран Plane" width="600"/>

</div>

Plane хранит projects, issues, members и workflow context.

### COMPASS AI dashboard

<div align="center">

<img src="assets/forreadme/102.jpeg" alt="Главный экран COMPASS AI dashboard" width="600"/>

</div>

COMPASS AI dashboard связывает synthetic data, model metrics, Plane tasks и recommendation workflows.

### Overview

<div align="center">

<img src="assets/forreadme/103.png" alt="Overview COMPASS AI dashboard" width="400"/>

</div>

Overview page показывает статистику synthetic-data, качество назначений и текущее базовое состояние системы.

### Issue recommendations

<div align="center">

<img src="assets/forreadme/104.png" alt="Управление issue recommendations COMPASS AI" width="600"/>

</div>

Recommendation page позволяет выбрать число кандидатов, включить LLM explanations, ввести identifier существующей задачи или создать задачу прямо из dashboard.

<div align="center">

<img src="assets/forreadme/105.jpeg" alt="Рекомендованные исполнители COMPASS AI по score" width="600"/>

</div>

AI ранжирует candidate assignees по score и показывает recommendation result.

<div align="center">

<img src="assets/forreadme/106.png" alt="Пример LLM explanation COMPASS AI" width="600"/>

</div>

LLM explanation описывает, почему кандидаты подходят и какие риски надо учитывать.

### Plane Live

<div align="center">

<img src="assets/forreadme/107.jpeg" alt="Экран Plane Live COMPASS AI" width="600"/>

</div>

Plane Live показывает информацию об active Plane workspace и подключенных project data.

### Team workload

<div align="center">

<img src="assets/forreadme/108.jpeg" alt="Экран team workload COMPASS AI" width="600"/>

</div>

Workload page показывает загрузку сотрудников и помогает находить overload risks.

### Plane team

<div align="center">

<img src="assets/forreadme/109.png" alt="Экран Plane team COMPASS AI" width="600"/>

</div>

Plane team page показывает project members и участие команды в Plane projects.

### Model metrics

<div align="center">

<img src="assets/forreadme/110.png" alt="Экран model metrics COMPASS AI" width="600"/>

</div>

Model metrics page показывает training и ranking metrics для модели, которая используется в Plane workflow.

### Fairness

<div align="center">

<img src="assets/forreadme/111.png" alt="Экран fairness COMPASS AI" width="600"/>

</div>

Fairness page проверяет распределение назначений, концентрацию и fairness risks.

### Dashboard settings

<div align="center">

<img src="assets/forreadme/112.jpeg" alt="Экран dashboard settings COMPASS AI" width="600"/>

</div>

Settings page настраивает параметры dashboard, API connection и local service parameters.

## Хранение данных и artifacts

Sandbox хранит runtime data в изолированных директориях:

```text
sandbox_app/data/generated/       generated datasets
sandbox_app/data/imported/        imported datasets
sandbox_app/data/test_cases/      test cases for assignment checks
sandbox_app/data/kanban_lab/      saved Kanban Lab boards
sandbox_app/training_sessions/    trained model sessions
sandbox_app/assignment_sessions/  saved assignment sessions
sandbox_app/reports/              generated reports
sandbox_app/data/exports/         exported report bundles and model artifacts
```

Основной проект хранит synthetic data, models и reports в root-level директориях `data`, `models`, `reports` и `notebooks`.

## Технологический стек

Backend и ML:

- Python 3.11;
- FastAPI;
- Pydantic;
- Pandas;
- NumPy;
- scikit-learn;
- PyTorch;
- ONNX and ONNX Runtime;
- PyArrow / Parquet;
- Matplotlib and Plotly;
- Jupyter notebooks.

Frontend и dashboards:

- HTML;
- CSS;
- Vanilla JavaScript;
- Streamlit;
- browser-based local UI;
- FastAPI static frontend serving.

Интеграции и локальные сервисы:

- Plane;
- Plane REST API;
- Docker-based local Plane stack;
- Ollama;
- Qwen2.5 1.5B Instruct;
- VS Code tasks for stack orchestration.

## Проверенное окружение

Проект разрабатывался и проверялся на:

```text
MacBook Air
Apple Silicon M2
8 GB RAM
macOS
Python 3.11
Local Ollama runtime
Local Plane stack
```

Это намеренно не high-end workstation. Sandbox workflow, обучение моделей с контролируемыми лимитами, local API и dashboard проверялись на легком ноутбуке. На более мощном desktop-компьютере или на выделенном локальном сервере у этой же системы должен быть значительно более комфортный запас производительности для больших датасетов, тяжелых training sessions, большего числа одновременных пользователей и долгих экспериментов.

Для машин с ограниченной памятью обучение можно ограничивать через количество training pairs. Документированный sandbox workflow использует именно этот подход, чтобы система оставалась пригодной к работе, пока одновременно открыты браузер, редактор и локальные сервисы.

## Архитектурные диаграммы

Исходники диаграмм хранятся в `diagrams/` как Mermaid files. README ссылается на PNG-файлы в `assets/forreadme/`.

### Простая общая схема

<p align="center">
  <img src="assets/forreadme/compass_overview_RU.png" width="600" alt="COMPASS AI simple overview">
</p>

Источник: `diagrams/compass_overview_RU.mmd`.

### Подробная архитектура репозитория

<p align="center">
  <img src="assets/forreadme/repository_architecture_RU.png" width="600" alt="COMPASS AI repository architecture">
</p>

Источник: `diagrams/repository_architecture_RU.mmd`.

### Sandbox pipeline

<p align="center">
  <img src="assets/forreadme/sandbox_pipeline_RU.png" width="600" alt="COMPASS AI sandbox pipeline">
</p>

Источник: `diagrams/sandbox_pipeline_RU.mmd`.

### Plane integration pipeline

<p align="center">
  <img src="assets/forreadme/plane_integration_RU.png" width="600" alt="COMPASS AI Plane integration pipeline">
</p>

Источник: `diagrams/plane_integration_RU.mmd`.

## Структура проекта

Репозиторий является единым проектом. Root-приложение, интеграция с Plane и автономный Sandbox находятся в одном репозитории, но разделены по папкам и runtime-границам данных.

```text
COMPASS-AI/
├── .env.example                       Environment variable template
├── .vscode/
│   ├── settings.json                  Local editor settings
│   └── tasks.json                     VS Code tasks for COMPASS stack control
├── commands.txt                       Short local command reference
├── docker-compose.compass.yml         Root Docker Compose integration file
├── Makefile                           Root maintenance and helper commands
├── pyproject.toml                     Python tooling configuration
├── requirements.txt                   Root runtime dependencies
├── requirements-dev.txt               Root development dependencies
├── app/
│   ├── api.py                         FastAPI entrypoint основного COMPASS API
│   └── dashboard.py                   Streamlit dashboard для Plane и аналитики
├── assets/
│   └── forreadme/                     README screenshots и logo assets
├── config/
│   ├── paths.yaml                     Root project path configuration
│   ├── settings.yaml                  Root project settings
│   ├── synthetic_data.yaml            Synthetic data generation settings
│   └── synthetic_schema.yaml          Synthetic schema configuration
├── data/
│   ├── raw/                           Raw and external input data
│   ├── processed/                     Prepared data and Plane mappings
│   └── synthetic/                     Synthetic employees, tasks and assignments
├── docs/
│   ├── doc.md                         Project concept and architecture
│   ├── plan.md                        Additional planning notes
│   ├── synthetic_data_design.md       Synthetic data design notes
│   ├── todo.md                        Full development roadmap
│   ├── todo_subproj_27.md             Sandbox implementation record
│   └── sandbox27.md                   Manual sandbox pipeline
├── diagrams/
│   ├── compass_overview.mmd           Simple high-level architecture diagram
│   ├── repository_architecture.mmd    Detailed repository architecture diagram
│   ├── sandbox_pipeline.mmd           Sandbox data, training and assignment flow
│   └── plane_integration.mmd          Plane integration and live recommendation flow
├── logs/                              Runtime logs for local services
├── models/
│   ├── compass_matching_model.pt      PyTorch matching model artifact
│   └── task_employee_matcher.onnx     ONNX export artifact
├── notebooks/
│   ├── 01_synthetic_data_generation.ipynb
│   ├── 02_data_analysis.ipynb
│   ├── 03_model_training.ipynb
│   ├── 04_model_evaluation.ipynb
│   ├── 05_fairness_analysis.ipynb
│   ├── 06_plane_integration_demo.ipynb
│   └── 07_business_report.ipynb
├── plane/
│   ├── docker/                        Local Plane source and Docker setup
│   └── seed/                          Plane seed and helper data
├── reports/                           Root model metrics, fairness and notebooks
├── scripts/
│   ├── start_compass_stack.sh         Start main API, dashboard, Plane and Ollama flow
│   ├── stop_compass_stack.sh          Stop the main local stack
│   ├── start_plane.sh                 Start local Plane
│   ├── stop_plane.sh                  Stop local Plane
│   ├── start_ollama.sh                Start Ollama helper
│   └── stop_ollama.sh                 Stop Ollama helper
├── src/
│   ├── __init__.py                    Root Python package marker
│   ├── agents/                        Agentic task, team, matching and explanation logic
│   ├── api/                           API routers for Plane and recommendations
│   ├── data/                          Synthetic data generation and splits
│   ├── features/                      Feature engineering and skill vectorization
│   ├── integration/                   Plane client, mapping and comment formatting
│   ├── llm/                           Ollama client integration
│   ├── models/                        Matching model, training, inference and ONNX export
│   ├── recommendation/                Rule-based ranking, workload and growth scoring
│   ├── reports/                       Notebook and report generation
│   └── utils/                         Shared utilities
├── tests/                             Root project tests
├── sandbox_app/
│   ├── .python-version                Sandbox Python version pin
│   ├── README.md                      Sandbox-specific README
│   ├── requirements.txt               Sandbox runtime dependencies
│   ├── assets/                        Sandbox logo and local assets
│   ├── backend/
│   │   ├── main.py                    Sandbox FastAPI application entrypoint
│   │   ├── api/                       Sandbox API routers
│   │   ├── core/                      Settings, paths, time and contracts
│   │   ├── data_generation/           Employees, tasks, history and training pairs
│   │   ├── features/                  Sandbox feature builders and targets
│   │   ├── inference/                 Recommendations, assignment optimization and ONNX runtime
│   │   ├── llm/                       Qwen/Ollama explanations
│   │   ├── reports/                   Dataset, model and assignment reports
│   │   ├── training/                  Baseline, sklearn and PyTorch training
│   │   └── utils/                     Importers, JSON helpers and validation
│   ├── config/
│   │   ├── app_settings.json          Sandbox settings and limits
│   │   ├── model_presets.json         Available model presets
│   │   ├── data_contracts/            Data contract definitions
│   │   └── feature_schemas/           Developers, designers and custom schemas
│   ├── data/
│   │   ├── generated/                 Generated datasets
│   │   ├── imported/                  Imported datasets
│   │   ├── test_cases/                Assignment test cases
│   │   ├── kanban_lab/                Saved Kanban Lab boards
│   │   └── exports/                   Exported bundles and model artifacts
│   ├── docs/                          Sandbox-specific documentation
│   ├── frontend/
│   │   ├── index.html                 Sandbox browser shell
│   │   ├── css/                       Sandbox styles
│   │   └── js/
│   │       ├── app.js                 Sandbox frontend bootstrap and router
│   │       ├── api.js                 Browser API client
│   │       ├── components/            Shared frontend components
│   │       └── pages/                 Sandbox UI tabs and workflows
│   ├── logs/                          Sandbox runtime logs
│   ├── reports/                       Generated sandbox reports
│   ├── scripts/                       Sandbox start, stop, restart and smoke scripts
│   ├── tests/                         Sandbox tests
│   ├── training_sessions/             Saved training sessions
│   └── assignment_sessions/           Saved assignment sessions
├── README.md
└── README_RU.md
```

## Назначение проекта

COMPASS AI специально сделан на стыке software engineering, team management и AI-assisted decision support. Проект не ограничивается обычной демонстрацией machine learning: он моделирует практическую управленческую задачу, которая каждый день возникает в командах разработки.

Центральный вопрос здесь не только в том, у какого сотрудника есть нужный навык. Полезная система назначения должна также учитывать загрузку, усталость, надежность дедлайнов, сложность задачи, историю качества, риски и долгосрочное развитие сотрудника. Поэтому проект релевантен и для engineering managers, и для разработчиков, которые хотят понимать, как AI-рекомендации могут опираться на прозрачные данные.

Интеграция с Plane представляет operational side системы: задачи, проекты и участники могут приходить из реального project-management tool. Sandbox представляет research and experimentation side: пользователь может генерировать данные, менять схемы, обучать модели, смотреть метрики, запускать Kanban-эксперименты и проверять объяснения, не затрагивая реальные production data.

Такая архитектура делает COMPASS AI удобным для изучения ML-based ranking, AI explainability, local LLM usage, team analytics, fairness risks и reproducible decision-support workflows в software development и project management.

## Примечания

COMPASS AI — это локальный research and educational project. Он сделан так, чтобы логика назначения задач была inspectable: датасеты видны, модели сравнимы, рекомендации объяснимы, а эксперименты воспроизводимы.

Sandbox намеренно отделен от основного Plane-integrated приложения. Это позволяет запускать тяжелые эксперименты, генерировать synthetic data и проверять Kanban scenarios без изменения основного COMPASS API или данных Plane.
