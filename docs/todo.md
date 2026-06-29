# COMPASS AI — полный roadmap разработки

**Репозиторий:** `COMPASS-AI`  
**Локальный путь:** `/Users/andrey/Documents/projects/COMPASS-AI`  
**Основная машина:** MacBook M2  
**Файл:** `docs/todo.md`

---

# 0. Целевой результат проекта

К финалу проекта должна работать система **COMPASS AI**:

- Plane используется как готовая система управления задачами.
- В Plane есть синтетическая команда, проекты и задачи.
- COMPASS AI получает задачу из Plane.
- COMPASS AI анализирует задачу, команду, навыки, загрузку и историю назначений.
- Собственная нейронная сеть `TaskEmployeeMatchingNet` ранжирует сотрудников.
- Агентная связка формирует рекомендацию и объяснение на русском языке.
- Рекомендация возвращается в Plane как комментарий к задаче или через отдельный dashboard/API.
- Модель экспортируется в ONNX.
- Jupyter-ноутбуки автоматически генерируют отчёты, метрики, fairness-анализ и бизнес-аналитику.
- В конце оформлена документация, скриншоты, примеры работы и финальный README.

---

# 1. Общая логика разработки

Разработка идёт строго по этапам:

1. Подготовить репозиторий и окружение.
2. Развернуть Plane локально.
3. Изучить структуру данных Plane.
4. Определить, какие поля Plane реально используем.
5. Спроектировать внутреннюю схему данных COMPASS AI.
6. Сгенерировать синтетические данные.
7. Написать интеграционный слой с Plane.
8. Сделать базовый API COMPASS AI.
9. Реализовать анализ задачи и команды.
10. Реализовать ML pipeline.
11. Обучить собственную нейронную сеть.
12. Экспортировать модель в ONNX.
13. Реализовать agentic pipeline.
14. Подключить русскоязычную LLM для объяснений.
15. Вернуть рекомендации в Plane.
16. Сделать analytics/dashboard слой.
17. Сгенерировать Jupyter-отчёты.
18. Провести тестирование.
19. Подготовить финальную документацию и демо.

---

# 2. Важные внешние ссылки

## Plane

- GitHub Plane: `https://github.com/makeplane/plane`
- Plane self-hosting docs: `https://developers.plane.so/self-hosting`
- Plane Docker Compose docs: `https://developers.plane.so/self-hosting/methods/docker-compose`

## Plane MCP Server

- GitHub Plane MCP Server: `https://github.com/makeplane/plane-mcp-server`

## Text embeddings

- Hugging Face model: `https://huggingface.co/sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`

## LLM для русскоязычных объяснений

- Hugging Face Qwen2.5-1.5B-Instruct: `https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct`
- Ollama Qwen2.5 1.5B: `https://ollama.com/library/qwen2.5:1.5b-instruct`
- Ollama: `https://ollama.com`

---

# 3. Этап 1 — первичная подготовка репозитория

## 3.1. Проверить текущую структуру проекта

- [x] Открыть терминал.
- [x] Перейти в папку проекта.
- [x] Проверить, что путь проекта правильный.
- [x] Проверить, что в проекте сейчас есть `README.md`, `LICENSE`, `docs/doc.md`, `docs/todo.md`.
- [x] Убедиться, что репозиторий называется `COMPASS-AI`.

Команды:

```bash
cd /Users/andrey/Documents/projects/COMPASS-AI
```

```bash
pwd
```

```bash
ls -la
```

```bash
find . -maxdepth 3 -type f
```

**Ожидаемый результат:** ты находишься в корне `COMPASS-AI`, структура совпадает с текущей.

**Примерное время:** 10 минут.  
**Коммит:** `Add project roadmap draft`

---

## 3.2. Создать базовую структуру папок

- [x] Создать папку `app` для FastAPI-приложения.
- [x] Создать папку `config` для конфигураций.
- [x] Создать папку `data` для данных.
- [x] Создать папку `data/raw` для исходных выгрузок.
- [x] Создать папку `data/synthetic` для синтетических данных.
- [x] Создать папку `data/processed` для подготовленных датасетов.
- [x] Создать папку `models` для обученных моделей.
- [x] Создать папку `notebooks` для Jupyter-ноутбуков.
- [x] Создать папку `reports` для HTML/PDF-отчётов.
- [x] Создать папку `scripts` для CLI-скриптов.
- [x] Создать папку `src` для основного Python-кода.
- [x] Создать папку `src/agents` для агентов.
- [x] Создать папку `src/data` для генерации и обработки данных.
- [x] Создать папку `src/features` для feature engineering.
- [x] Создать папку `src/integration` для интеграции с Plane.
- [x] Создать папку `src/llm` для LLM-объяснений.
- [x] Создать папку `src/models` для ML-моделей.
- [x] Создать папку `src/recommendation` для ranking/recommendation logic.
- [x] Создать папку `src/reports` для генерации отчётов.
- [x] Создать папку `src/utils` для общих утилит.
- [x] Создать папку `tests` для тестов.
- [x] Создать папку `tools` для локальных вспомогательных инструментов.
- [x] Создать папку `plane` для локальных файлов, связанных с Plane.
- [x] Создать папку `plane/docker` для конфигураций запуска Plane.
- [x] Создать папку `plane/seed` для подготовки данных Plane.

Команды:

```bash
mkdir -p app config data/raw data/synthetic data/processed models notebooks reports scripts src/agents src/data src/features src/integration src/llm src/models src/recommendation src/reports src/utils tests tools plane/docker plane/seed
```

```bash
touch src/__init__.py src/agents/__init__.py src/data/__init__.py src/features/__init__.py src/integration/__init__.py src/llm/__init__.py src/models/__init__.py src/recommendation/__init__.py src/reports/__init__.py src/utils/__init__.py
```

**Ожидаемый результат:** проект уже выглядит как нормальный ML/backend репозиторий.

**Примерное время:** 15 минут.  
**Коммит:** `Create project folder structure`

---

## 3.3. Создать служебные файлы проекта

- [x] Создать `.gitignore`.
- [x] Создать `.env.example`.
- [x] Создать `requirements.txt`.
- [x] Создать `requirements-dev.txt`.
- [x] Создать `pyproject.toml`.
- [x] Создать `Makefile`.
- [x] Создать `docker-compose.compass.yml`.
- [x] Создать `config/settings.yaml`.
- [x] Создать `config/paths.yaml`.

Команды:

```bash
touch .gitignore .env.example requirements.txt requirements-dev.txt pyproject.toml Makefile docker-compose.compass.yml config/settings.yaml config/paths.yaml
```

**Что добавить в `.gitignore`:**

- `.venv/`
- `__pycache__/`
- `.DS_Store`
- `.env`
- `data/raw/*`
- `data/processed/*`
- `models/*.pt`
- `models/*.onnx`
- `reports/*.html`
- `reports/*.pdf`
- `.ipynb_checkpoints/`

**Что оставить отслеживаемым в данных:**

- `data/synthetic/.gitkeep`
- `data/raw/.gitkeep`
- `data/processed/.gitkeep`

Команды:

```bash
touch data/raw/.gitkeep data/synthetic/.gitkeep data/processed/.gitkeep models/.gitkeep reports/.gitkeep
```

**Ожидаемый результат:** репозиторий готов к нормальной разработке и не будет случайно коммитить тяжёлые модели/данные.

**Примерное время:** 30 минут.  
**Коммит:** `Add project configuration files`

---

# 4. Этап 2 — Python-окружение на MacBook M2

## 4.1. Проверить Python

- [x] Проверить установленную версию Python.
- [x] Убедиться, что используется Python 3.11 или 3.12.
- [x] Если Python не установлен, установить через Homebrew.
- [x] Проверить, что `pip` работает.

Команды:

```bash
python3 --version
```

```bash
pip3 --version
```

Команда установки Python через Homebrew, если надо:

```bash
brew install python@3.11
```

**Ожидаемый результат:** доступен Python 3.11+.

**Примерное время:** 20 минут.  
**Коммит:** коммит не нужен, если файлы не менялись.

---

## 4.2. Создать виртуальное окружение

- [x] Создать `.venv` в корне проекта.
- [x] Активировать окружение.
- [x] Обновить `pip`.
- [x] Проверить, что Python берётся из `.venv`.

Команды:

```bash
python3 -m venv .venv
```

```bash
source .venv/bin/activate
```

```bash
python -m pip install --upgrade pip setuptools wheel
```

```bash
which python
```

**Ожидаемый результат:** путь к Python должен быть внутри `/Users/andrey/Documents/projects/COMPASS-AI/.venv`.

**Примерное время:** 15 минут.  
**Коммит:** коммит не нужен.

---

## 4.3. Заполнить `requirements.txt`

- [x] Добавить библиотеки для данных.
- [x] Добавить библиотеки для ML.
- [x] Добавить библиотеки для ONNX.
- [x] Добавить библиотеки для API.
- [x] Добавить библиотеки для Jupyter.
- [x] Добавить библиотеки для отчётов.
- [x] Добавить библиотеки для интеграции.
- [x] Добавить библиотеки для LLM/embeddings.

Минимальный набор:

```text
numpy
pandas
scikit-learn
torch
torchvision
torchaudio
sentence-transformers
transformers
accelerate
onnx
onnxruntime
fastapi
uvicorn
pydantic
pydantic-settings
httpx
requests
python-dotenv
pyyaml
jupyter
ipykernel
nbformat
nbconvert
papermill
matplotlib
plotly
rich
typer
tqdm
```

Команда установки:

```bash
pip install -r requirements.txt
```

**Ожидаемый результат:** все основные зависимости установлены.

**Примерное время:** 30–60 минут.  
**Коммит:** `Add Python dependencies`

---

## 4.4. Заполнить `requirements-dev.txt`

- [x] Добавить инструменты форматирования.
- [x] Добавить инструменты тестирования.
- [x] Добавить инструменты проверки типов.

Минимальный набор:

```text
pytest
pytest-cov
ruff
black
mypy
pre-commit
```

Команда установки:

```bash
pip install -r requirements-dev.txt
```

**Ожидаемый результат:** можно запускать тесты, форматирование и линтер.

**Примерное время:** 20 минут.  
**Коммит:** `Add development dependencies`

---

## 4.5. Настроить `pyproject.toml`

- [x] Указать настройки `black`.
- [x] Указать настройки `ruff`.
- [x] Указать настройки `pytest`.
- [x] Указать настройки `mypy`.
- [x] Указать версию Python.
- [x] Указать, что основной пакет находится в `src`.

Что должно быть настроено:

- длина строки: `100`;
- Python target: `py311`;
- тесты ищутся в `tests`;
- исходники ищутся в `src`.

**Ожидаемый результат:** проект можно проверять единым набором команд.

**Примерное время:** 40 минут.  
**Коммит:** `Configure code quality tools`

---

## 4.6. Настроить `Makefile`

- [x] Добавить команду `make install`.
- [x] Добавить команду `make dev`.
- [x] Добавить команду `make test`.
- [x] Добавить команду `make lint`.
- [x] Добавить команду `make format`.
- [x] Добавить команду `make api`.
- [x] Добавить команду `make notebooks`.
- [x] Добавить команду `make train`.
- [x] Добавить команду `make export-onnx`.
- [x] Добавить команду `make reports`.

Пример команд, которые должны вызываться:

```bash
make test
```

```bash
make lint
```

```bash
make api
```

**Ожидаемый результат:** все частые действия проекта запускаются одной короткой командой.

**Примерное время:** 40 минут.  
**Коммит:** `Add project automation commands`

---

# 5. Этап 3 — установка Docker и подготовка Plane

## 5.1. Проверить Docker Desktop

- [ ] Установить Docker Desktop для Mac, если не установлен.
- [ ] Запустить Docker Desktop.
- [ ] Проверить работу Docker.
- [ ] Проверить работу Docker Compose.
- [ ] Убедиться, что Docker использует достаточно ресурсов.

Команды:

```bash
docker --version
```

```bash
docker compose version
```

```bash
docker ps
```

**Рекомендации для MacBook M2:**

- CPU: 4 ядра.
- RAM для Docker: 6–8 GB.
- Disk limit: минимум 30 GB.
- Если MacBook с 8 GB RAM, не запускать одновременно тяжёлую LLM и много контейнеров.

**Ожидаемый результат:** Docker работает.

**Примерное время:** 30–60 минут.  
**Коммит:** коммит не нужен.

---

## 5.2. Изучить официальный способ запуска Plane

- [ ] Открыть `https://github.com/makeplane/plane`.
- [ ] Открыть `https://developers.plane.so/self-hosting`.
- [ ] Открыть Docker Compose guide.
- [ ] Зафиксировать, какой способ запуска актуален.
- [ ] Не копировать слепо старые compose-файлы из чужих гайдов.
- [ ] Использовать официальный self-hosting способ Plane.

**Важно:** сначала поднять Plane отдельно, без COMPASS AI. Не надо сразу смешивать Plane и свой backend.

**Ожидаемый результат:** понятно, как локально запускать Plane.

**Примерное время:** 1–2 часа.  
**Коммит:** коммит не нужен, если ничего не добавлялось.

---

## 5.3. Установить Plane локально

- [ ] Создать отдельную папку вне основного кода или внутри `plane/docker`.
- [ ] Скачать/склонировать нужные self-hosting файлы Plane по официальной инструкции.
- [ ] Создать `.env` для Plane.
- [ ] Проверить порты Plane.
- [ ] Запустить Plane через Docker Compose.
- [ ] Открыть Plane в браузере.
- [ ] Создать локальный workspace.
- [ ] Создать первого пользователя-админа.

Примерная команда, если официальный способ требует клонирование репозитория:

```bash
git clone https://github.com/makeplane/plane.git plane/docker/plane-source
```

Примерная команда запуска, если используется docker compose:

```bash
docker compose up -d
```

**Важно:** точные команды Plane брать из актуальной официальной документации, потому что структура self-hosting может меняться.

**Ожидаемый результат:** Plane доступен в браузере локально.

**Примерное время:** 2–4 часа.  
**Коммит:** `Add Plane local setup notes`

---

## 5.4. Создать тестовый workspace в Plane

- [ ] Открыть локальный Plane.
- [ ] Создать workspace `compass-ai-lab`.
- [ ] Создать проект `Backend Platform`.
- [ ] Создать проект `Frontend Platform`.
- [ ] Создать проект `Data Platform`.
- [ ] Создать проект `Internal Tools`.
- [ ] Создать несколько статусов задач.
- [ ] Создать несколько labels.
- [ ] Создать несколько cycles/sprints, если Plane это поддерживает в установленной версии.

Статусы:

- `Backlog`
- `Ready`
- `In Progress`
- `Review`
- `Done`
- `Blocked`

Labels:

- `backend`
- `frontend`
- `ml`
- `data`
- `devops`
- `bug`
- `feature`
- `refactoring`
- `urgent`
- `growth-task`

**Ожидаемый результат:** в Plane есть учебная рабочая область, похожая на настоящую команду.

**Примерное время:** 1 час.  
**Коммит:** коммит не нужен, если всё делалось только в Plane UI.

---

# 6. Этап 4 — изучение данных Plane перед разработкой интеграции

## 6.1. Получить доступ к Plane API

- [ ] Найти в Plane настройки API/token.
- [ ] Создать API token, если Plane это поддерживает в установленной версии.
- [ ] Сохранить токен только в локальный `.env`.
- [ ] Добавить пример переменных в `.env.example` без секретов.
- [ ] Проверить доступ к API через `curl` или `httpx`.

Поля в `.env.example`:

```text
PLANE_BASE_URL=http://localhost:3000
PLANE_API_KEY=replace_with_your_token
PLANE_WORKSPACE_SLUG=compass-ai-lab
COMPASS_API_URL=http://localhost:8000
OLLAMA_BASE_URL=http://localhost:11434
```

**Ожидаемый результат:** понятно, как COMPASS AI будет авторизоваться в Plane.

**Примерное время:** 1–2 часа.  
**Коммит:** `Add environment configuration template`

---

## 6.2. Исследовать сущности Plane

- [ ] Выяснить, как Plane называет задачи в текущей версии: `issues` или `work items`.
- [ ] Выяснить, какие поля есть у задачи.
- [ ] Выяснить, как получить список проектов.
- [ ] Выяснить, как получить список участников workspace/project.
- [ ] Выяснить, как получить статусы.
- [ ] Выяснить, как получить labels.
- [ ] Выяснить, как добавить комментарий к задаче.
- [ ] Выяснить, как обновить assignee.
- [ ] Зафиксировать найденные поля в локальном техническом файле, но не в финальной документации.

Рабочий файл для заметок:

```text
plane/seed/plane_schema_notes.md
```

Команда:

```bash
touch plane/seed/plane_schema_notes.md
```

Минимально нужно узнать поля задачи:

```text
id
identifier
title
description
priority
state
labels
assignees
project
created_at
updated_at
target_date
estimate
```

Минимально нужно узнать поля пользователя:

```text
id
display_name
email
avatar
role
```

**Ожидаемый результат:** ты не придумываешь интеграцию вслепую, а опираешься на реальные поля Plane.

**Примерное время:** 2–3 часа.  
**Коммит:** `Document Plane data model notes`

---

## 6.3. Написать минимальный Plane client

- [ ] Создать файл `src/integration/plane_client.py`.
- [ ] Реализовать класс `PlaneClient`.
- [ ] Добавить чтение настроек из `.env`.
- [ ] Добавить метод проверки соединения.
- [ ] Добавить метод получения workspace.
- [ ] Добавить метод получения projects.
- [ ] Добавить метод получения issues/work items.
- [ ] Добавить метод получения project members.
- [ ] Добавить метод получения labels.
- [ ] Добавить метод добавления комментария.
- [ ] Добавить метод обновления assignee, если API позволяет.
- [ ] Не добавлять ML-логику в этот файл.

Файл:

```text
src/integration/plane_client.py
```

Класс:

```text
PlaneClient
```

Методы:

```text
healthcheck()
get_workspace()
list_projects()
list_project_members(project_id)
list_issues(project_id)
get_issue(project_id, issue_id)
create_issue_comment(project_id, issue_id, text)
update_issue_assignee(project_id, issue_id, assignee_id)
```

**Ожидаемый результат:** есть отдельный слой для общения с Plane.

**Примерное время:** 3–5 часов.  
**Коммит:** `Add Plane API client`

---

## 6.4. Написать CLI для проверки Plane client

- [ ] Создать `scripts/check_plane_connection.py`.
- [ ] Скрипт должен загружать `.env`.
- [ ] Скрипт должен вызывать `PlaneClient.healthcheck()`.
- [ ] Скрипт должен вывести список проектов.
- [ ] Скрипт должен вывести количество задач в каждом проекте.
- [ ] Скрипт должен завершаться понятной ошибкой, если Plane недоступен.

Файл:

```text
scripts/check_plane_connection.py
```

Команда запуска:

```bash
python scripts/check_plane_connection.py
```

**Ожидаемый результат:** можно быстро проверить, что Plane и COMPASS AI видят друг друга.

**Примерное время:** 1–2 часа.  
**Коммит:** `Add Plane connection checker`

---

# 7. Этап 5 — проектирование синтетической команды и данных

## 7.1. Определить состав синтетической команды

- [ ] Создать список сотрудников.
- [ ] Сделать команду реалистичной, не слишком большой.
- [ ] Использовать 12–20 сотрудников.
- [ ] Добавить разные роли.
- [ ] Добавить разные грейды.
- [ ] Добавить разные навыки.
- [ ] Добавить разные цели развития.
- [ ] Добавить разную текущую загрузку.
- [ ] Не использовать реальные персональные данные.

Рекомендуемый состав:

```text
Backend Developer Junior — 2 человека
Backend Developer Middle — 3 человека
Backend Developer Senior — 2 человека
Frontend Developer Junior — 2 человека
Frontend Developer Middle — 2 человека
Frontend Developer Senior — 1 человек
QA Engineer — 2 человека
Data/ML Engineer — 2 человека
DevOps Engineer — 1 человек
Team Lead — 1 человек
```

Поля сотрудника:

```text
employee_id
plane_user_id
name
role
grade
experience_years
primary_stack
skills
current_workload
avg_completion_speed
avg_quality_score
deadline_reliability
learning_goals
mentor_level
```

**Ожидаемый результат:** есть понятная учебная команда, для которой можно генерировать задачи и историю.

**Примерное время:** 1–2 часа.  
**Коммит:** `Define synthetic team schema`

---

## 7.2. Определить словари навыков

- [ ] Создать список технических навыков.
- [ ] Создать список soft/management навыков.
- [ ] Создать список доменных навыков.
- [ ] Создать шкалу уровней навыков от 0 до 5.
- [ ] Привязать навыки к ролям.

Технические навыки:

```text
Python
FastAPI
Django
PostgreSQL
Redis
Docker
Kubernetes
React
TypeScript
Next.js
HTML/CSS
Testing
CI/CD
Data Analysis
Machine Learning
PyTorch
API Design
System Design
Monitoring
Security
```

Soft/management навыки:

```text
communication
ownership
mentoring
documentation
code_review
planning
risk_management
```

Уровни:

```text
0 — нет навыка
1 — базовое знакомство
2 — выполняет простые задачи
3 — уверенный рабочий уровень
4 — сильный уровень
5 — эксперт
```

**Ожидаемый результат:** skills можно превратить в вектор для модели.

**Примерное время:** 1 час.  
**Коммит:** `Define skills taxonomy`

---

## 7.3. Определить типы задач

- [ ] Создать список типов задач.
- [ ] Для каждого типа определить частые навыки.
- [ ] Для каждого типа определить среднюю сложность.
- [ ] Для каждого типа определить среднее время выполнения.
- [ ] Добавить задачи для развития junior/middle сотрудников.

Типы задач:

```text
backend_feature
frontend_feature
bugfix
refactoring
database_migration
api_integration
ml_pipeline
analytics_report
devops_task
testing_task
security_task
documentation_task
```

Поля задачи:

```text
task_id
plane_issue_id
title
description
task_type
required_stack
required_skills
complexity
priority
business_criticality
deadline_days
estimated_hours
dependencies_count
is_growth_task
```

**Ожидаемый результат:** задачи можно генерировать системно, а не случайным хаосом.

**Примерное время:** 1 час.  
**Коммит:** `Define task schema`

---

## 7.4. Определить историю назначений

- [ ] Описать, как будет выглядеть историческое назначение.
- [ ] Каждое назначение — это пара `task_id + employee_id`.
- [ ] Для каждой пары хранить результат выполнения.
- [ ] Добавить признаки качества, скорости и просрочки.
- [ ] Добавить целевую метку `success_label`.

Поля истории:

```text
assignment_id
task_id
employee_id
assigned_at
completed_at
completed_on_time
estimated_hours
actual_hours
quality_score
reopened_count
manager_rating
employee_workload_at_assignment
skill_match_score
growth_match_score
success_label
```

Правила label:

```text
success_label = 1, если completed_on_time = true, quality_score >= 0.75, reopened_count <= 1, employee_workload_at_assignment <= 0.85
success_label = 0, если задача просрочена, quality_score < 0.6, reopened_count >= 3 или workload > 0.95
```

**Ожидаемый результат:** данные подходят для supervised learning.

**Примерное время:** 1–2 часа.  
**Коммит:** `Define assignment history schema`

---

# 8. Этап 6 — генератор синтетических данных

## 8.1. Создать конфиг генерации данных

- [ ] Создать `config/synthetic_data.yaml`.
- [ ] Указать seed генерации.
- [ ] Указать количество сотрудников.
- [ ] Указать количество задач.
- [ ] Указать количество исторических назначений.
- [ ] Указать диапазоны сложности.
- [ ] Указать диапазоны загрузки.
- [ ] Указать список ролей.
- [ ] Указать список навыков.
- [ ] Указать распределения грейдов.

Файл:

```text
config/synthetic_data.yaml
```

Параметры:

```text
random_seed
employees_count
tasks_count
assignments_count
skills
roles
grades
projects
task_types
date_range_start
date_range_end
```

**Ожидаемый результат:** генератор данных настраивается без изменения кода.

**Примерное время:** 1 час.  
**Коммит:** `Add synthetic data configuration`

---

## 8.2. Реализовать генерацию сотрудников

- [ ] Создать `src/data/generate_employees.py`.
- [ ] Сгенерировать `employee_id`.
- [ ] Сгенерировать русские имена.
- [ ] Сгенерировать роли.
- [ ] Сгенерировать грейды.
- [ ] Сгенерировать опыт.
- [ ] Сгенерировать skills vector.
- [ ] Сгенерировать текущую загрузку.
- [ ] Сгенерировать среднюю скорость.
- [ ] Сгенерировать среднее качество.
- [ ] Сгенерировать reliability.
- [ ] Сгенерировать learning goals.
- [ ] Сохранить результат в `data/synthetic/employees.csv`.
- [ ] Сохранить JSON-версию в `data/synthetic/employees.json`.

Файлы результата:

```text
data/synthetic/employees.csv
data/synthetic/employees.json
```

Команда запуска:

```bash
python src/data/generate_employees.py
```

**Ожидаемый результат:** есть синтетическая команда.

**Примерное время:** 3–5 часов.  
**Коммит:** `Generate synthetic employees`

---

## 8.3. Реализовать генерацию задач

- [ ] Создать `src/data/generate_tasks.py`.
- [ ] Сгенерировать задачи на русском языке.
- [ ] Сгенерировать реалистичные заголовки.
- [ ] Сгенерировать реалистичные описания.
- [ ] Сгенерировать тип задачи.
- [ ] Сгенерировать требуемый стек.
- [ ] Сгенерировать требуемые навыки.
- [ ] Сгенерировать сложность от 1 до 5.
- [ ] Сгенерировать priority.
- [ ] Сгенерировать business criticality.
- [ ] Сгенерировать дедлайн в днях.
- [ ] Сгенерировать estimated hours.
- [ ] Сгенерировать dependencies count.
- [ ] Сохранить результат в `data/synthetic/tasks.csv`.
- [ ] Сохранить JSON-версию в `data/synthetic/tasks.json`.

Примеры заголовков:

```text
Реализовать JWT-авторизацию
Добавить фильтрацию задач по статусу
Оптимизировать SQL-запросы в отчётах
Настроить Docker Compose для dev-окружения
Добавить экспорт аналитики в CSV
Починить ошибку при смене assignee
Реализовать endpoint для статистики команды
```

Команда запуска:

```bash
python src/data/generate_tasks.py
```

**Ожидаемый результат:** есть синтетический backlog задач.

**Примерное время:** 3–5 часов.  
**Коммит:** `Generate synthetic tasks`

---

## 8.4. Реализовать генерацию истории назначений

- [ ] Создать `src/data/generate_assignments.py`.
- [ ] Загружать сотрудников из `employees.csv`.
- [ ] Загружать задачи из `tasks.csv`.
- [ ] Для каждой исторической задачи выбирать сотрудника не полностью случайно, а с учётом навыков и загрузки.
- [ ] Рассчитывать `skill_match_score`.
- [ ] Рассчитывать `growth_match_score`.
- [ ] Рассчитывать вероятность успешного выполнения.
- [ ] Генерировать `completed_on_time`.
- [ ] Генерировать `actual_hours`.
- [ ] Генерировать `quality_score`.
- [ ] Генерировать `reopened_count`.
- [ ] Генерировать `manager_rating`.
- [ ] Генерировать `success_label`.
- [ ] Сохранить результат в `data/synthetic/assignments.csv`.
- [ ] Сохранить JSON-версию в `data/synthetic/assignments.json`.

Команда запуска:

```bash
python src/data/generate_assignments.py
```

**Ожидаемый результат:** есть обучающая история назначений.

**Примерное время:** 5–8 часов.  
**Коммит:** `Generate synthetic assignment history`

---

## 8.5. Создать общий pipeline генерации данных

- [ ] Создать `scripts/generate_synthetic_data.py`.
- [ ] Скрипт должен запускать генерацию сотрудников.
- [ ] Скрипт должен запускать генерацию задач.
- [ ] Скрипт должен запускать генерацию истории назначений.
- [ ] Скрипт должен проверять, что все CSV-файлы созданы.
- [ ] Скрипт должен печатать краткую статистику.
- [ ] Добавить команду в `Makefile`.

Команда запуска:

```bash
python scripts/generate_synthetic_data.py
```

Команда через Makefile:

```bash
make generate-data
```

**Ожидаемый результат:** все данные генерируются одной командой.

**Примерное время:** 2–3 часа.  
**Коммит:** `Add synthetic data generation pipeline`

---

# 9. Этап 7 — загрузка синтетических данных в Plane

## 9.1. Подготовить mapping между COMPASS AI и Plane

- [ ] Создать `src/integration/plane_mapping.py`.
- [ ] Определить, как поля COMPASS AI превращаются в поля Plane.
- [ ] Сопоставить `task.title` с Plane issue title.
- [ ] Сопоставить `task.description` с Plane issue description.
- [ ] Сопоставить `priority` с Plane priority.
- [ ] Сопоставить `required_stack` с labels.
- [ ] Сопоставить `task_type` с labels.
- [ ] Сопоставить `deadline_days` с target date.
- [ ] Сопоставить `estimated_hours` с estimate, если поле доступно.
- [ ] Сопоставить `employee_id` с `plane_user_id`.

Файл:

```text
src/integration/plane_mapping.py
```

**Ожидаемый результат:** понятно, какие данные можно реально положить в Plane.

**Примерное время:** 2–3 часа.  
**Коммит:** `Map COMPASS data to Plane fields`

---

## 9.2. Создать seed-скрипт для Plane labels

- [ ] Создать `plane/seed/create_labels.py`.
- [ ] Скрипт должен создать labels для технологий.
- [ ] Скрипт должен создать labels для типов задач.
- [ ] Скрипт должен не создавать дубликаты.
- [ ] Скрипт должен печатать список созданных labels.

Labels:

```text
python
fastapi
postgresql
react
typescript
docker
ml
data
devops
bug
feature
refactoring
growth-task
urgent
```

Команда:

```bash
python plane/seed/create_labels.py
```

**Ожидаемый результат:** в Plane есть labels, которые нужны для задач.

**Примерное время:** 2–4 часа.  
**Коммит:** `Add Plane labels seeding`

---

## 9.3. Создать seed-скрипт для Plane задач

- [ ] Создать `plane/seed/create_tasks.py`.
- [ ] Скрипт должен читать `data/synthetic/tasks.csv`.
- [ ] Скрипт должен создавать задачи в нужном проекте Plane.
- [ ] Скрипт должен добавлять labels.
- [ ] Скрипт должен добавлять priority.
- [ ] Скрипт должен добавлять target date, если поле доступно.
- [ ] Скрипт должен сохранить mapping `task_id → plane_issue_id`.
- [ ] Mapping сохранить в `data/processed/task_plane_mapping.csv`.

Команда:

```bash
python plane/seed/create_tasks.py
```

Результат:

```text
data/processed/task_plane_mapping.csv
```

**Ожидаемый результат:** в Plane появляется синтетический backlog.

**Примерное время:** 4–8 часов.  
**Коммит:** `Seed Plane with synthetic tasks`

---

## 9.4. Создать seed-скрипт для пользователей Plane

- [ ] Проверить, можно ли создавать пользователей через API.
- [ ] Если можно, создать синтетических пользователей автоматически.
- [ ] Если нельзя, создать пользователей вручную в UI.
- [ ] После создания пользователей выгрузить их IDs.
- [ ] Сопоставить `employee_id` с `plane_user_id`.
- [ ] Сохранить mapping в `data/processed/employee_plane_mapping.csv`.

Файл:

```text
data/processed/employee_plane_mapping.csv
```

Поля:

```text
employee_id
plane_user_id
name
email
role
```

**Важно:** если Plane self-hosted не даёт удобно создавать пользователей через API, это не критично. Для учебного проекта можно вручную создать 5–8 пользователей и сопоставить их с синтетическими сотрудниками.

**Ожидаемый результат:** COMPASS AI знает, как связать своего сотрудника с пользователем Plane.

**Примерное время:** 2–5 часов.  
**Коммит:** `Map synthetic employees to Plane users`

---

# 10. Этап 8 — базовый backend COMPASS AI

## 10.1. Создать FastAPI-приложение

- [ ] Создать `app/api.py`.
- [ ] Создать endpoint `/health`.
- [ ] Создать endpoint `/version`.
- [ ] Создать endpoint `/recommendations/demo`.
- [ ] Создать endpoint `/recommendations/issue/{issue_id}`.
- [ ] Создать endpoint `/reports/summary`.
- [ ] Подключить CORS, если нужен локальный dashboard.
- [ ] Подключить чтение `.env`.
- [ ] Добавить запуск через `uvicorn`.

Файл:

```text
app/api.py
```

Команда запуска:

```bash
uvicorn app.api:app --reload --host 0.0.0.0 --port 8000
```

Проверка:

```bash
curl http://localhost:8000/health
```

**Ожидаемый результат:** локальный backend COMPASS AI работает.

**Примерное время:** 3–5 часов.  
**Коммит:** `Add COMPASS FastAPI service`

---

## 10.2. Создать Pydantic-схемы API

- [ ] Создать `src/models/schemas.py`.
- [ ] Описать `TaskInput`.
- [ ] Описать `EmployeeInput`.
- [ ] Описать `RecommendationRequest`.
- [ ] Описать `CandidateRecommendation`.
- [ ] Описать `RecommendationResponse`.
- [ ] Описать `ExplanationResponse`.
- [ ] Описать `AnalyticsSummary`.

Файл:

```text
src/models/schemas.py
```

Основные структуры:

```text
TaskInput
EmployeeInput
RecommendationRequest
CandidateRecommendation
RecommendationResponse
```

**Ожидаемый результат:** API возвращает строго структурированные данные.

**Примерное время:** 2–3 часа.  
**Коммит:** `Add API data schemas`

---

## 10.3. Добавить demo endpoint без ML

- [ ] Endpoint `/recommendations/demo` должен брать тестовую задачу.
- [ ] Endpoint должен брать список сотрудников из `employees.csv`.
- [ ] Endpoint должен возвращать top-3 по простому rule-based правилу.
- [ ] Пока не использовать нейросеть.
- [ ] Вернуть JSON с кандидатом, score и причиной.
- [ ] Проверить ответ через браузер или curl.

Команда:

```bash
curl http://localhost:8000/recommendations/demo
```

**Ожидаемый результат:** до ML уже есть end-to-end форма ответа.

**Примерное время:** 2–4 часа.  
**Коммит:** `Add demo recommendation endpoint`

---

# 11. Этап 9 — базовые эвристики до нейронной сети

## 11.1. Реализовать skill matching

- [ ] Создать `src/recommendation/skill_matching.py`.
- [ ] Реализовать расчёт совпадения навыков задачи и сотрудника.
- [ ] Учитывать required skills.
- [ ] Учитывать stack.
- [ ] Учитывать уровень владения навыком.
- [ ] Вернуть score от 0 до 1.
- [ ] Написать тесты.

Файл:

```text
src/recommendation/skill_matching.py
```

Тест:

```text
tests/test_skill_matching.py
```

**Ожидаемый результат:** можно понять, насколько сотрудник технически подходит к задаче.

**Примерное время:** 3–5 часов.  
**Коммит:** `Add skill matching baseline`

---

## 11.2. Реализовать workload scoring

- [ ] Создать `src/recommendation/workload_scoring.py`.
- [ ] Реализовать penalty за высокую загрузку.
- [ ] Нормализовать загрузку от 0 до 1.
- [ ] Считать загрузку выше 0.85 рискованной.
- [ ] Считать загрузку выше 0.95 критической.
- [ ] Написать тесты.

Файл:

```text
src/recommendation/workload_scoring.py
```

**Ожидаемый результат:** система не рекомендует автоматически самого сильного, если он перегружен.

**Примерное время:** 2–3 часа.  
**Коммит:** `Add workload scoring baseline`

---

## 11.3. Реализовать growth scoring

- [ ] Создать `src/recommendation/growth_scoring.py`.
- [ ] Сравнивать required skills задачи с learning goals сотрудника.
- [ ] Повышать score, если задача подходит для развития.
- [ ] Понижать score, если задача слишком сложная для текущего уровня.
- [ ] Добавить параметр `mentor_available`.
- [ ] Написать тесты.

Файл:

```text
src/recommendation/growth_scoring.py
```

**Ожидаемый результат:** система может рекомендовать не только “самого быстрого”, но и “кому полезно дать задачу”.

**Примерное время:** 3–5 часов.  
**Коммит:** `Add growth scoring baseline`

---

## 11.4. Собрать rule-based baseline

- [ ] Создать `src/recommendation/rule_based_ranker.py`.
- [ ] Объединить skill score.
- [ ] Объединить workload score.
- [ ] Объединить growth score.
- [ ] Добавить speed score.
- [ ] Добавить quality score.
- [ ] Реализовать режимы: `fast_delivery`, `balanced_workload`, `growth`, `risk_minimization`.
- [ ] Возвращать top-3 кандидатов.
- [ ] Написать тесты.

Файл:

```text
src/recommendation/rule_based_ranker.py
```

**Ожидаемый результат:** есть baseline, с которым потом сравнивается нейросеть.

**Примерное время:** 5–8 часов.  
**Коммит:** `Add rule based recommendation baseline`

---

# 12. Этап 10 — feature engineering для нейронной сети

## 12.1. Реализовать skill vectors

- [ ] Создать `src/features/skill_vectorizer.py`.
- [ ] Определить фиксированный список навыков.
- [ ] Превращать skills сотрудника в числовой вектор.
- [ ] Превращать required skills задачи в числовой вектор.
- [ ] Проверить одинаковую длину векторов.
- [ ] Сохранить словарь навыков в `data/processed/skill_vocab.json`.

Файл:

```text
src/features/skill_vectorizer.py
```

Результат:

```text
data/processed/skill_vocab.json
```

**Ожидаемый результат:** навыки можно подавать в нейронную сеть.

**Примерное время:** 3–5 часов.  
**Коммит:** `Add skill vectorization`

---

## 12.2. Реализовать text embeddings для задач

- [ ] Создать `src/features/text_embeddings.py`.
- [ ] Подключить `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`.
- [ ] Загружать модель локально.
- [ ] Превращать `title + description` в embedding.
- [ ] Проверить размерность 384.
- [ ] Кешировать embeddings в `data/processed/task_text_embeddings.npy`.
- [ ] Сделать fallback, если модель не скачалась.

Файл:

```text
src/features/text_embeddings.py
```

Модель:

```text
sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
```

Результат:

```text
data/processed/task_text_embeddings.npy
```

Команда проверки:

```bash
python src/features/text_embeddings.py
```

**Ожидаемый результат:** русскоязычные описания задач превращаются в векторы.

**Примерное время:** 4–6 часов.  
**Коммит:** `Add multilingual task embeddings`

---

## 12.3. Реализовать numeric feature builder

- [ ] Создать `src/features/build_features.py`.
- [ ] Загружать employees, tasks, assignments.
- [ ] Строить task numeric features.
- [ ] Строить employee numeric features.
- [ ] Строить pair features для каждой пары `task + employee`.
- [ ] Добавить признаки разницы навыков.
- [ ] Добавить признаки загрузки.
- [ ] Добавить признаки опыта.
- [ ] Добавить признаки дедлайна.
- [ ] Добавить признаки бизнес-критичности.
- [ ] Сохранять итоговый датасет в `data/processed/training_pairs.parquet`.

Файл:

```text
src/features/build_features.py
```

Результат:

```text
data/processed/training_pairs.parquet
```

Команда:

```bash
python src/features/build_features.py
```

**Ожидаемый результат:** создан датасет для обучения нейросети.

**Примерное время:** 6–10 часов.  
**Коммит:** `Build training features`

---

## 12.4. Разделить данные на train/validation/test

- [ ] Создать `src/data/split_dataset.py`.
- [ ] Использовать train/validation/test split.
- [ ] Не допустить утечку данных, если одна и та же задача встречается в разных split.
- [ ] Разделять лучше по `task_id`, а не по отдельным парам.
- [ ] Сохранить `train.parquet`.
- [ ] Сохранить `val.parquet`.
- [ ] Сохранить `test.parquet`.

Файлы:

```text
data/processed/train.parquet
data/processed/val.parquet
data/processed/test.parquet
```

Команда:

```bash
python src/data/split_dataset.py
```

**Ожидаемый результат:** данные готовы к честному обучению и оценке.

**Примерное время:** 2–4 часа.  
**Коммит:** `Split training dataset`

---

# 13. Этап 11 — собственная нейронная сеть

## 13.1. Реализовать Dataset и DataLoader

- [ ] Создать `src/models/dataset.py`.
- [ ] Реализовать `AssignmentPairDataset`.
- [ ] Dataset должен возвращать task features.
- [ ] Dataset должен возвращать employee features.
- [ ] Dataset должен возвращать pair features.
- [ ] Dataset должен возвращать label.
- [ ] Проверить batch shapes.
- [ ] Написать простой тест.

Файл:

```text
src/models/dataset.py
```

**Ожидаемый результат:** PyTorch может читать обучающие данные.

**Примерное время:** 4–6 часов.  
**Коммит:** `Add PyTorch dataset for assignment pairs`

---

## 13.2. Реализовать `TaskEmployeeMatchingNet`

- [ ] Создать `src/models/matching_net.py`.
- [ ] Реализовать `TaskEncoder`.
- [ ] Реализовать `EmployeeEncoder`.
- [ ] Реализовать `MatchingBlock`.
- [ ] Реализовать общий класс `TaskEmployeeMatchingNet`.
- [ ] На вход принимать task tensor.
- [ ] На вход принимать employee tensor.
- [ ] На вход принимать pair tensor.
- [ ] На выход отдавать `success_probability`.
- [ ] Дополнительно подготовить выходы для `speed_score`, `quality_score`, `learning_score`, `overload_risk`, если делаешь multi-task вариант.
- [ ] Для MVP сначала сделать один главный выход `success_probability`.
- [ ] После MVP расширить до multi-output.

Файл:

```text
src/models/matching_net.py
```

Архитектура MVP:

```text
TaskEncoder → task_embedding
EmployeeEncoder → employee_embedding
concat(task_embedding, employee_embedding, abs_diff, multiply, pair_features) → MLP → sigmoid
```

**Ожидаемый результат:** собственная нейронная сеть создана.

**Примерное время:** 6–10 часов.  
**Коммит:** `Add task employee matching network`

---

## 13.3. Реализовать training loop

- [ ] Создать `src/models/train.py`.
- [ ] Загружать train/val датасеты.
- [ ] Создавать модель.
- [ ] Использовать BCE loss для binary classification.
- [ ] Использовать Adam или AdamW.
- [ ] Логировать train loss.
- [ ] Логировать validation loss.
- [ ] Логировать ROC-AUC.
- [ ] Сохранять лучший checkpoint.
- [ ] Сохранять config обучения.
- [ ] Сохранять training history в CSV.

Файл:

```text
src/models/train.py
```

Результаты:

```text
models/compass_matching_model.pt
reports/training_history.csv
```

Команда:

```bash
python src/models/train.py
```

**Ожидаемый результат:** модель обучается и сохраняется.

**Примерное время:** 8–14 часов.  
**Коммит:** `Train matching neural network`

---

## 13.4. Добавить поддержку Apple Silicon MPS

- [ ] Проверить доступность `mps`.
- [ ] Если `mps` доступен, использовать его.
- [ ] Если `mps` недоступен, использовать CPU.
- [ ] Не делать CUDA обязательной.
- [ ] Добавить лог устройства обучения.
- [ ] Проверить обучение на MacBook M2.

Проверка:

```bash
python -c "import torch; print(torch.backends.mps.is_available())"
```

**Ожидаемый результат:** обучение работает на MacBook M2 без CUDA.

**Примерное время:** 1–2 часа.  
**Коммит:** `Support Apple Silicon training`

---

## 13.5. Реализовать evaluation

- [ ] Создать `src/models/evaluate.py`.
- [ ] Загрузить test dataset.
- [ ] Загрузить лучший checkpoint.
- [ ] Рассчитать accuracy.
- [ ] Рассчитать precision.
- [ ] Рассчитать recall.
- [ ] Рассчитать F1.
- [ ] Рассчитать ROC-AUC.
- [ ] Рассчитать PR-AUC.
- [ ] Сохранить метрики в `reports/model_metrics.json`.
- [ ] Сохранить предсказания в `reports/test_predictions.csv`.

Файл:

```text
src/models/evaluate.py
```

Команда:

```bash
python src/models/evaluate.py
```

Результаты:

```text
reports/model_metrics.json
reports/test_predictions.csv
```

**Ожидаемый результат:** можно доказать качество модели цифрами.

**Примерное время:** 4–6 часов.  
**Коммит:** `Evaluate matching model`

---

## 13.6. Реализовать ranking metrics

- [ ] Создать `src/models/ranking_metrics.py`.
- [ ] Рассчитать Precision@1.
- [ ] Рассчитать Precision@3.
- [ ] Рассчитать NDCG@3.
- [ ] Рассчитать MRR.
- [ ] Сравнить ML-модель с random baseline.
- [ ] Сравнить ML-модель с rule-based baseline.
- [ ] Сохранить результат в `reports/ranking_metrics.json`.

Файл:

```text
src/models/ranking_metrics.py
```

Результат:

```text
reports/ranking_metrics.json
```

**Ожидаемый результат:** проект оценивает не только классификацию, но и качество рекомендаций.

**Примерное время:** 5–8 часов.  
**Коммит:** `Add recommendation ranking metrics`

---

# 14. Этап 12 — inference и ONNX

## 14.1. Реализовать inference wrapper

- [ ] Создать `src/models/inference.py`.
- [ ] Загружать PyTorch checkpoint.
- [ ] Принимать одну задачу и список сотрудников.
- [ ] Строить features.
- [ ] Считать score для каждого сотрудника.
- [ ] Сортировать кандидатов.
- [ ] Возвращать top-3.
- [ ] Добавить режимы рекомендации.
- [ ] Вернуть структурированный JSON.

Файл:

```text
src/models/inference.py
```

**Ожидаемый результат:** модель можно использовать в backend.

**Примерное время:** 5–8 часов.  
**Коммит:** `Add model inference wrapper`

---

## 14.2. Экспортировать модель в ONNX

- [ ] Создать `src/models/export_onnx.py`.
- [ ] Загрузить checkpoint.
- [ ] Создать dummy input нужной формы.
- [ ] Экспортировать модель.
- [ ] Проверить, что файл создан.
- [ ] Сохранить в `models/task_employee_matcher.onnx`.

Файл:

```text
src/models/export_onnx.py
```

Команда:

```bash
python src/models/export_onnx.py
```

Результат:

```text
models/task_employee_matcher.onnx
```

**Ожидаемый результат:** есть ONNX-файл как production-ready артефакт.

**Примерное время:** 3–5 часов.  
**Коммит:** `Export matching model to ONNX`

---

## 14.3. Проверить ONNX Runtime

- [ ] Создать `src/models/onnx_inference.py`.
- [ ] Загрузить `task_employee_matcher.onnx`.
- [ ] Подать тот же dummy input.
- [ ] Сравнить PyTorch output и ONNX output.
- [ ] Проверить, что разница мала.
- [ ] Сохранить результат проверки в `reports/onnx_validation.json`.

Файл:

```text
src/models/onnx_inference.py
```

Команда:

```bash
python src/models/onnx_inference.py
```

Результат:

```text
reports/onnx_validation.json
```

**Ожидаемый результат:** ONNX-модель реально запускается.

**Примерное время:** 3–5 часов.  
**Коммит:** `Validate ONNX inference`

---

# 15. Этап 13 — agentic pipeline

## 15.1. Создать общий формат состояния агентов

- [ ] Создать `src/agents/state.py`.
- [ ] Описать `AgentState`.
- [ ] В state хранить исходную задачу.
- [ ] В state хранить сотрудников.
- [ ] В state хранить features.
- [ ] В state хранить результаты модели.
- [ ] В state хранить объяснение.
- [ ] В state хранить финальную рекомендацию.
- [ ] Не хранить секреты API в state.

Файл:

```text
src/agents/state.py
```

Поля:

```text
issue
task_features
employees
employee_features
candidate_scores
top_candidates
recommendation_mode
explanation
final_response
errors
```

**Ожидаемый результат:** агенты передают данные друг другу предсказуемо.

**Примерное время:** 2–3 часа.  
**Коммит:** `Add agent pipeline state`

---

## 15.2. Реализовать Task Analyzer Agent

- [ ] Создать `src/agents/task_analyzer.py`.
- [ ] Агент принимает задачу из Plane.
- [ ] Извлекает title.
- [ ] Извлекает description.
- [ ] Извлекает labels.
- [ ] Определяет task type.
- [ ] Определяет required skills.
- [ ] Определяет required stack.
- [ ] Определяет complexity.
- [ ] Определяет urgency по deadline/priority.
- [ ] Возвращает task features.
- [ ] Сначала реализовать rule-based parsing.
- [ ] Позже можно добавить LLM-assisted parsing.

Файл:

```text
src/agents/task_analyzer.py
```

**Ожидаемый результат:** сырая задача Plane превращается в признаки для модели.

**Примерное время:** 5–8 часов.  
**Коммит:** `Add task analyzer agent`

---

## 15.3. Реализовать Team State Analyzer Agent

- [ ] Создать `src/agents/team_analyzer.py`.
- [ ] Агент принимает список сотрудников.
- [ ] Загружает их профили из `employees.csv`.
- [ ] Подтягивает текущие задачи из Plane.
- [ ] Считает текущую загрузку.
- [ ] Считает активные задачи.
- [ ] Считает перегруз.
- [ ] Считает доступность.
- [ ] Формирует employee features.
- [ ] Возвращает список кандидатов.

Файл:

```text
src/agents/team_analyzer.py
```

**Ожидаемый результат:** состояние команды считается перед каждой рекомендацией.

**Примерное время:** 6–10 часов.  
**Коммит:** `Add team state analyzer agent`

---

## 15.4. Реализовать Matching Model Agent

- [ ] Создать `src/agents/matching_agent.py`.
- [ ] Агент получает task features.
- [ ] Агент получает employee features.
- [ ] Агент вызывает PyTorch или ONNX inference.
- [ ] Агент получает scores.
- [ ] Агент сортирует сотрудников.
- [ ] Агент возвращает top-3.
- [ ] Агент добавляет технические причины: skill match, workload, risk, growth.

Файл:

```text
src/agents/matching_agent.py
```

**Ожидаемый результат:** отдельный агент отвечает только за ML-рекомендацию.

**Примерное время:** 4–6 часов.  
**Коммит:** `Add matching model agent`

---

## 15.5. Установить Ollama

- [ ] Скачать Ollama с `https://ollama.com`.
- [ ] Установить Ollama на Mac.
- [ ] Запустить Ollama.
- [ ] Проверить, что сервер доступен.
- [ ] Скачать `qwen2.5:1.5b-instruct`.
- [ ] Проверить генерацию русского текста.

Команды:

```bash
ollama --version
```

```bash
ollama pull qwen2.5:1.5b-instruct
```

```bash
ollama run qwen2.5:1.5b-instruct
```

Проверочный prompt:

```text
Кратко объясни на русском, почему задачу лучше назначить middle backend-разработчику с низкой загрузкой.
```

**Ожидаемый результат:** локальная LLM отвечает на русском.

**Примерное время:** 1–2 часа.  
**Коммит:** коммит не нужен.

---

## 15.6. Реализовать LLM client

- [ ] Создать `src/llm/ollama_client.py`.
- [ ] Добавить базовый URL из `.env`.
- [ ] Добавить имя модели из `.env`.
- [ ] Реализовать метод `generate()`.
- [ ] Добавить timeout.
- [ ] Добавить обработку ошибок.
- [ ] Добавить fallback-ответ, если Ollama недоступна.
- [ ] Не использовать LLM для принятия решения.
- [ ] Использовать LLM только для объяснения.

Файл:

```text
src/llm/ollama_client.py
```

Переменная `.env.example`:

```text
OLLAMA_MODEL=qwen2.5:1.5b-instruct
```

**Ожидаемый результат:** backend может обращаться к локальной LLM.

**Примерное время:** 3–5 часов.  
**Коммит:** `Add Ollama LLM client`

---

## 15.7. Реализовать Explanation Agent

- [ ] Создать `src/agents/explanation_agent.py`.
- [ ] Агент получает top-3 кандидатов.
- [ ] Агент получает факторы решения.
- [ ] Агент формирует prompt на русском.
- [ ] Агент вызывает Ollama.
- [ ] Агент возвращает краткое объяснение.
- [ ] Агент возвращает fallback template, если LLM не отвечает.
- [ ] Ограничить длину ответа.
- [ ] Запретить LLM менять ranking.
- [ ] Запретить LLM придумывать данные, которых нет в input.

Файл:

```text
src/agents/explanation_agent.py
```

Структура объяснения:

```text
Рекомендованный исполнитель
Почему он подходит
Риски
Альтернативы
Режим рекомендации
```

**Ожидаемый результат:** рекомендации выглядят понятно для тимлида.

**Примерное время:** 5–8 часов.  
**Коммит:** `Add Russian explanation agent`

---

## 15.8. Реализовать Plane Integration Agent

- [ ] Создать `src/agents/plane_agent.py`.
- [ ] Агент получает issue ID.
- [ ] Загружает задачу из Plane.
- [ ] Загружает команду проекта.
- [ ] Передаёт данные в agent pipeline.
- [ ] Получает финальную рекомендацию.
- [ ] Добавляет комментарий в Plane.
- [ ] Опционально назначает recommended assignee.
- [ ] Логирует результат.

Файл:

```text
src/agents/plane_agent.py
```

**Ожидаемый результат:** COMPASS AI начинает реально работать с Plane.

**Примерное время:** 6–10 часов.  
**Коммит:** `Add Plane integration agent`

---

## 15.9. Собрать общий agentic orchestrator

- [ ] Создать `src/agents/orchestrator.py`.
- [ ] Оркестратор запускает Task Analyzer.
- [ ] Оркестратор запускает Team State Analyzer.
- [ ] Оркестратор запускает Matching Model Agent.
- [ ] Оркестратор запускает Explanation Agent.
- [ ] Оркестратор запускает Plane Integration Agent только при необходимости.
- [ ] Оркестратор возвращает единый response.
- [ ] Добавить логирование каждого шага.
- [ ] Добавить обработку ошибок.

Файл:

```text
src/agents/orchestrator.py
```

Pipeline:

```text
Plane Issue → Task Analyzer → Team Analyzer → Matching Agent → Explanation Agent → Plane Comment
```

**Ожидаемый результат:** есть настоящая агентная связка из нескольких компонентов.

**Примерное время:** 6–10 часов.  
**Коммит:** `Add agentic recommendation orchestrator`

---

# 16. Этап 14 — интеграция recommendations API с агентами

## 16.1. Подключить orchestrator к FastAPI

- [ ] Endpoint `/recommendations/issue/{issue_id}` должен вызвать orchestrator.
- [ ] Endpoint должен принять режим рекомендации.
- [ ] Endpoint должен вернуть JSON.
- [ ] Endpoint должен опционально добавить комментарий в Plane.
- [ ] Добавить query parameter `write_back=true/false`.
- [ ] Добавить query parameter `mode`.
- [ ] Добавить обработку ошибок.

Пример endpoint:

```text
GET /recommendations/issue/{issue_id}?mode=balanced_workload&write_back=true
```

Команда проверки:

```bash
curl "http://localhost:8000/recommendations/issue/test-id?mode=balanced_workload&write_back=false"
```

**Ожидаемый результат:** backend умеет рекомендовать исполнителя для конкретной задачи Plane.

**Примерное время:** 4–6 часов.  
**Коммит:** `Connect recommendation API to agents`

---

## 16.2. Добавить endpoint для пакетного анализа задач

- [ ] Создать endpoint `/recommendations/project/{project_id}/open-issues`.
- [ ] Endpoint получает все открытые задачи проекта.
- [ ] Для каждой задачи запускает recommendation pipeline.
- [ ] Возвращает список рекомендаций.
- [ ] Не писать комментарии в Plane по умолчанию.
- [ ] Добавить `limit`, чтобы не обрабатывать слишком много задач.

Пример:

```text
GET /recommendations/project/{project_id}/open-issues?limit=10&mode=balanced_workload
```

**Ожидаемый результат:** можно анализировать сразу backlog проекта.

**Примерное время:** 5–8 часов.  
**Коммит:** `Add batch issue recommendations`

---

## 16.3. Добавить endpoint для ручной задачи без Plane

- [ ] Создать endpoint `/recommendations/manual`.
- [ ] Endpoint принимает JSON с задачей.
- [ ] Endpoint принимает список сотрудников или использует synthetic team.
- [ ] Endpoint возвращает top-3.
- [ ] Это нужно для тестирования без Plane.

Пример:

```text
POST /recommendations/manual
```

**Ожидаемый результат:** COMPASS AI можно тестировать независимо от Plane.

**Примерное время:** 3–5 часов.  
**Коммит:** `Add manual recommendation endpoint`

---

# 17. Этап 15 — запись рекомендаций обратно в Plane

## 17.1. Сделать формат комментария COMPASS AI

- [ ] Создать `src/integration/plane_comment_formatter.py`.
- [ ] Форматировать рекомендацию в Markdown.
- [ ] Указать recommended assignee.
- [ ] Указать score.
- [ ] Указать top-3.
- [ ] Указать режим.
- [ ] Указать риски.
- [ ] Указать объяснение LLM.
- [ ] Указать, что решение является рекомендацией, а не автоматическим приказом.

Файл:

```text
src/integration/plane_comment_formatter.py
```

Пример комментария:

```text
## COMPASS AI Recommendation

Recommended assignee: Анна Смирнова  
Mode: Balanced Workload  
Score: 0.82

Why:
Анна имеет хороший опыт с FastAPI и отчётами, текущая загрузка 45%, похожие задачи выполнялись успешно.

Alternatives:
1. Иван Петров — 0.79, high skill match, workload risk 85%
2. Максим Орлов — 0.71, growth option, needs review

Note:
This is a decision-support recommendation. Final assignment is made by the team lead.
```

**Ожидаемый результат:** в Plane комментарий выглядит аккуратно.

**Примерное время:** 2–4 часа.  
**Коммит:** `Format Plane recommendation comments`

---

## 17.2. Добавить write-back в Plane

- [ ] В `PlaneClient` проверить метод создания комментария.
- [ ] Добавить запись комментария через API.
- [ ] Проверить на одной тестовой задаче.
- [ ] Убедиться, что комментарий не дублируется при повторном запуске.
- [ ] Добавить защиту от повторной записи.
- [ ] Добавить marker `Generated by COMPASS AI`.

**Ожидаемый результат:** после анализа задачи в Plane появляется комментарий от COMPASS AI.

**Примерное время:** 4–8 часов.  
**Коммит:** `Write recommendations back to Plane`

---

## 17.3. Добавить опциональное автоматическое назначение

- [ ] Добавить параметр `auto_assign=false`.
- [ ] По умолчанию не назначать автоматически.
- [ ] Если `auto_assign=true`, назначать top-1 кандидата.
- [ ] Перед назначением проверять, что `score >= threshold`.
- [ ] Threshold по умолчанию: `0.75`.
- [ ] Если score ниже threshold, только писать комментарий.
- [ ] Логировать автоматические назначения.

Пример:

```text
GET /recommendations/issue/{issue_id}?write_back=true&auto_assign=true&threshold=0.75
```

**Ожидаемый результат:** можно показать более продвинутый сценарий, но безопасно.

**Примерное время:** 4–8 часов.  
**Коммит:** `Add optional auto assignment`

---

# 18. Этап 16 — простое окно AI-помощника и dashboard

## 18.1. Принять решение по интерфейсу

- [ ] Не переписывать Plane полностью.
- [ ] Сделать отдельный лёгкий COMPASS dashboard.
- [ ] Dashboard должен ссылаться на задачи Plane.
- [ ] В Plane рекомендации живут в комментариях.
- [ ] В COMPASS dashboard живут метрики, топ задач, fairness и нагрузка.
- [ ] Если будет желание глубже интегрироваться в UI Plane, делать это только после MVP.

**Причина:** менять фронтенд Plane сложнее, чем сделать внешний dashboard. Для учебного проекта внешний dashboard + комментарии в Plane достаточно выглядят как интеграция.

**Ожидаемый результат:** понятная стратегия UI.

**Примерное время:** 30 минут.  
**Коммит:** коммит не нужен.

---

## 18.2. Сделать dashboard на FastAPI HTML или Streamlit

- [ ] Выбрать простой вариант.
- [ ] Рекомендуемый вариант для студенческого проекта: Streamlit.
- [ ] Создать `app/dashboard.py`.
- [ ] Показать список открытых задач.
- [ ] Показать top recommendation по каждой задаче.
- [ ] Показать team workload.
- [ ] Показать model metrics.
- [ ] Показать fairness metrics.
- [ ] Добавить кнопку/действие “Analyze issue”.
- [ ] Добавить кнопку/действие “Write recommendation to Plane”.

Файл:

```text
app/dashboard.py
```

Дополнительная зависимость:

```text
streamlit
```

Команда установки:

```bash
pip install streamlit
```

Команда запуска:

```bash
streamlit run app/dashboard.py
```

**Ожидаемый результат:** есть отдельная “менюшка” COMPASS AI для аналитики и управления рекомендациями.

**Примерное время:** 8–14 часов.  
**Коммит:** `Add COMPASS analytics dashboard`

---

## 18.3. Добавить страницы dashboard

- [ ] Страница `Overview`.
- [ ] Страница `Issue Recommendations`.
- [ ] Страница `Team Workload`.
- [ ] Страница `Model Metrics`.
- [ ] Страница `Fairness`.
- [ ] Страница `Settings`.

Что показывать на `Overview`:

```text
количество открытых задач
количество сотрудников
средняя загрузка команды
количество задач с высоким риском
средний recommendation score
```

Что показывать на `Issue Recommendations`:

```text
issue title
priority
deadline
recommended assignee
score
mode
button: analyze
button: write to Plane
```

Что показывать на `Team Workload`:

```text
employee
role
grade
current workload
active issues
overload risk
```

Что показывать на `Model Metrics`:

```text
ROC-AUC
F1
Precision@3
NDCG@3
comparison with random baseline
comparison with rule-based baseline
```

Что показывать на `Fairness`:

```text
assignment distribution
senior overload risk
junior underuse risk
workload balance
growth task distribution
```

**Ожидаемый результат:** интерфейс показывает не только рекомендации, но и управленческую аналитику.

**Примерное время:** 10–18 часов.  
**Коммит:** `Add dashboard pages`

---

# 19. Этап 17 — Jupyter notebooks и автоматические отчёты

## 19.1. Создать notebook-шаблоны

- [ ] Создать `notebooks/01_synthetic_data_generation.ipynb`.
- [ ] Создать `notebooks/02_data_analysis.ipynb`.
- [ ] Создать `notebooks/03_model_training.ipynb`.
- [ ] Создать `notebooks/04_model_evaluation.ipynb`.
- [ ] Создать `notebooks/05_fairness_analysis.ipynb`.
- [ ] Создать `notebooks/06_plane_integration_demo.ipynb`.
- [ ] Создать `notebooks/07_business_report.ipynb`.

Команда:

```bash
touch notebooks/01_synthetic_data_generation.ipynb notebooks/02_data_analysis.ipynb notebooks/03_model_training.ipynb notebooks/04_model_evaluation.ipynb notebooks/05_fairness_analysis.ipynb notebooks/06_plane_integration_demo.ipynb notebooks/07_business_report.ipynb
```

**Ожидаемый результат:** есть структура ноутбуков.

**Примерное время:** 30 минут.  
**Коммит:** `Add notebook structure`

---

## 19.2. Ноутбук генерации данных

- [ ] В `01_synthetic_data_generation.ipynb` показать параметры генерации.
- [ ] Показать таблицу сотрудников.
- [ ] Показать таблицу задач.
- [ ] Показать таблицу назначений.
- [ ] Показать распределение ролей.
- [ ] Показать распределение сложности задач.
- [ ] Показать распределение success label.
- [ ] Не писать финальную документацию, только рабочий notebook.

**Ожидаемый результат:** можно визуально проверить, что synthetic data выглядит реалистично.

**Примерное время:** 4–6 часов.  
**Коммит:** `Add synthetic data notebook`

---

## 19.3. Ноутбук EDA

- [ ] В `02_data_analysis.ipynb` загрузить все датасеты.
- [ ] Проверить пропуски.
- [ ] Проверить распределения.
- [ ] Проверить корреляции.
- [ ] Проверить связь skill match и success.
- [ ] Проверить связь workload и success.
- [ ] Проверить связь complexity и success.
- [ ] Построить графики.
- [ ] Сохранить основные графики в `reports/figures`.

Папка:

```text
reports/figures
```

Команда:

```bash
mkdir -p reports/figures
```

**Ожидаемый результат:** понятна структура данных и зависимости.

**Примерное время:** 5–8 часов.  
**Коммит:** `Add exploratory data analysis notebook`

---

## 19.4. Ноутбук обучения модели

- [ ] В `03_model_training.ipynb` показать конфиг обучения.
- [ ] Показать размер train/val/test.
- [ ] Показать архитектуру модели.
- [ ] Запустить обучение или загрузить историю обучения.
- [ ] Показать train/val loss.
- [ ] Показать ROC-AUC на validation.
- [ ] Показать сохранённый checkpoint.

**Ожидаемый результат:** обучение модели воспроизводимо и наглядно.

**Примерное время:** 5–8 часов.  
**Коммит:** `Add model training notebook`

---

## 19.5. Ноутбук оценки модели

- [ ] В `04_model_evaluation.ipynb` загрузить test predictions.
- [ ] Показать classification metrics.
- [ ] Показать confusion matrix.
- [ ] Показать ROC curve.
- [ ] Показать PR curve.
- [ ] Показать Precision@3.
- [ ] Показать NDCG@3.
- [ ] Сравнить ML model с random baseline.
- [ ] Сравнить ML model с rule-based baseline.

**Ожидаемый результат:** качество модели подтверждено метриками.

**Примерное время:** 5–8 часов.  
**Коммит:** `Add model evaluation notebook`

---

## 19.6. Ноутбук fairness analysis

- [ ] В `05_fairness_analysis.ipynb` анализировать распределение рекомендаций.
- [ ] Проверить, не выбираются ли почти всегда senior.
- [ ] Проверить, не игнорируются ли junior.
- [ ] Проверить среднюю загрузку рекомендованных сотрудников.
- [ ] Проверить распределение growth-задач.
- [ ] Проверить баланс по ролям.
- [ ] Сформировать fairness summary.

Метрики:

```text
senior_recommendation_share
junior_recommendation_share
top_employee_concentration
average_recommended_workload
growth_task_distribution
```

**Ожидаемый результат:** проект показывает управленческую зрелость, а не просто accuracy.

**Примерное время:** 6–10 часов.  
**Коммит:** `Add fairness analysis notebook`

---

## 19.7. Ноутбук Plane integration demo

- [ ] В `06_plane_integration_demo.ipynb` показать подключение к Plane.
- [ ] Получить список проектов.
- [ ] Получить список задач.
- [ ] Выбрать одну задачу.
- [ ] Получить рекомендацию COMPASS AI.
- [ ] Показать top-3 кандидатов.
- [ ] Показать текст объяснения.
- [ ] Показать пример комментария для Plane.
- [ ] Опционально записать комментарий в Plane.

**Ожидаемый результат:** интеграция с Plane демонстрируется в notebook.

**Примерное время:** 5–8 часов.  
**Коммит:** `Add Plane integration demo notebook`

---

## 19.8. Ноутбук бизнес-отчёта

- [ ] В `07_business_report.ipynb` собрать основные результаты.
- [ ] Показать проблему.
- [ ] Показать решение.
- [ ] Показать пример рекомендации.
- [ ] Показать метрики модели.
- [ ] Показать аналитику загрузки.
- [ ] Показать fairness.
- [ ] Показать выводы для тимлида.
- [ ] Этот notebook потом можно экспортировать в HTML/PDF.

**Ожидаемый результат:** есть отчёт, который можно показать как результат проекта.

**Примерное время:** 6–10 часов.  
**Коммит:** `Add business report notebook`

---

## 19.9. Автоматизировать запуск notebooks

- [ ] Создать `src/reports/generate_notebooks.py`.
- [ ] Использовать `papermill`.
- [ ] Автоматически запускать notebooks по порядку.
- [ ] Сохранять выполненные версии в `reports/notebooks`.
- [ ] Экспортировать HTML через `nbconvert`.
- [ ] Добавить команду `make reports`.

Папка:

```text
reports/notebooks
```

Команда:

```bash
mkdir -p reports/notebooks
```

Команда запуска:

```bash
python src/reports/generate_notebooks.py
```

Команда через Makefile:

```bash
make reports
```

**Ожидаемый результат:** отчёты генерируются автоматически.

**Примерное время:** 6–10 часов.  
**Коммит:** `Automate notebook reports`

---

# 20. Этап 18 — Plane MCP Server

## 20.1. Изучить Plane MCP Server

- [ ] Открыть `https://github.com/makeplane/plane-mcp-server`.
- [ ] Изучить README.
- [ ] Проверить доступные tools.
- [ ] Проверить, какие сущности поддерживаются.
- [ ] Проверить, как передаётся Plane API key.
- [ ] Проверить, как подключить MCP server к AI-клиенту.
- [ ] Проверить ограничения self-hosted Plane.
- [ ] Не заменять REST API на MCP полностью, пока REST API работает стабильнее.

**Ожидаемый результат:** понятно, где MCP полезен, а где достаточно REST API.

**Примерное время:** 2–3 часа.  
**Коммит:** `Research Plane MCP integration`

---

## 20.2. Запустить Plane MCP Server локально

- [ ] Следовать актуальной инструкции из README Plane MCP Server.
- [ ] Настроить переменные окружения.
- [ ] Подключить MCP к локальному Plane.
- [ ] Проверить, что MCP server видит workspace.
- [ ] Проверить, что MCP server видит задачи.
- [ ] Проверить, что MCP server может читать work items/issues.
- [ ] Проверить, что MCP server может создавать комментарии, если поддерживается.

**Важно:** если MCP server в текущей версии конфликтует с self-hosted Plane или endpoint names, оставить MCP как экспериментальный слой, а основной интеграционный путь делать через REST API.

**Ожидаемый результат:** MCP работает хотя бы в демонстрационном режиме.

**Примерное время:** 3–6 часов.  
**Коммит:** `Add Plane MCP local experiment`

---

## 20.3. Добавить MCP client wrapper

- [ ] Создать `src/integration/mcp_client.py`.
- [ ] Реализовать минимальную обёртку.
- [ ] Не завязывать весь проект на MCP.
- [ ] Добавить метод получения задач.
- [ ] Добавить метод получения проекта.
- [ ] Добавить метод создания AI-комментария, если доступно.
- [ ] Добавить fallback на REST API.

Файл:

```text
src/integration/mcp_client.py
```

**Ожидаемый результат:** в проекте есть демонстрация modern agent tooling через MCP.

**Примерное время:** 5–8 часов.  
**Коммит:** `Add MCP client wrapper`

---

# 21. Этап 19 — тестирование

## 21.1. Unit tests для данных

- [ ] Создать тесты генерации сотрудников.
- [ ] Проверить, что employee IDs уникальны.
- [ ] Проверить, что skills имеют допустимые уровни.
- [ ] Проверить, что workload в диапазоне 0–1.
- [ ] Проверить генерацию задач.
- [ ] Проверить, что complexity в диапазоне 1–5.
- [ ] Проверить, что labels не пустые.
- [ ] Проверить генерацию assignments.
- [ ] Проверить, что success_label равен 0 или 1.

Файлы:

```text
tests/test_generate_employees.py
tests/test_generate_tasks.py
tests/test_generate_assignments.py
```

Команда:

```bash
pytest tests/test_generate_employees.py tests/test_generate_tasks.py tests/test_generate_assignments.py
```

**Ожидаемый результат:** генерация данных не ломается.

**Примерное время:** 4–6 часов.  
**Коммит:** `Test synthetic data generation`

---

## 21.2. Unit tests для recommendation baseline

- [ ] Проверить skill matching.
- [ ] Проверить workload scoring.
- [ ] Проверить growth scoring.
- [ ] Проверить ranking.
- [ ] Проверить, что top-3 отсортирован по score.
- [ ] Проверить, что перегруженный сотрудник получает penalty.
- [ ] Проверить, что growth mode поднимает подходящих для развития сотрудников.

Файлы:

```text
tests/test_skill_matching.py
tests/test_workload_scoring.py
tests/test_growth_scoring.py
tests/test_rule_based_ranker.py
```

Команда:

```bash
pytest tests/test_skill_matching.py tests/test_workload_scoring.py tests/test_growth_scoring.py tests/test_rule_based_ranker.py
```

**Ожидаемый результат:** baseline работает предсказуемо.

**Примерное время:** 5–8 часов.  
**Коммит:** `Test recommendation baselines`

---

## 21.3. Unit tests для модели

- [ ] Проверить Dataset.
- [ ] Проверить shape одного batch.
- [ ] Проверить forward pass модели.
- [ ] Проверить, что output в диапазоне 0–1.
- [ ] Проверить, что loss считается.
- [ ] Проверить, что один training step проходит без ошибки.
- [ ] Проверить ONNX inference.

Файлы:

```text
tests/test_dataset.py
tests/test_matching_net.py
tests/test_onnx_inference.py
```

Команда:

```bash
pytest tests/test_dataset.py tests/test_matching_net.py tests/test_onnx_inference.py
```

**Ожидаемый результат:** ML core стабилен.

**Примерное время:** 5–8 часов.  
**Коммит:** `Test matching model pipeline`

---

## 21.4. Integration tests для Plane

- [ ] Создать `tests/test_plane_client.py`.
- [ ] Тесты должны пропускаться, если нет `PLANE_API_KEY`.
- [ ] Проверить healthcheck.
- [ ] Проверить получение проектов.
- [ ] Проверить получение задач.
- [ ] Проверить форматирование комментария.
- [ ] Не писать реальные комментарии без отдельного флага.

Файл:

```text
tests/test_plane_client.py
```

Команда:

```bash
pytest tests/test_plane_client.py
```

**Ожидаемый результат:** интеграция с Plane проверяется безопасно.

**Примерное время:** 4–8 часов.  
**Коммит:** `Test Plane integration client`

---

## 21.5. End-to-end test

- [ ] Создать `tests/test_e2e_recommendation.py`.
- [ ] Взять одну синтетическую задачу.
- [ ] Взять синтетическую команду.
- [ ] Запустить Task Analyzer.
- [ ] Запустить Team Analyzer.
- [ ] Запустить Matching Agent.
- [ ] Запустить Explanation Agent fallback или real LLM.
- [ ] Проверить, что есть top-3.
- [ ] Проверить, что есть explanation.
- [ ] Проверить, что response валидный.

Файл:

```text
tests/test_e2e_recommendation.py
```

Команда:

```bash
pytest tests/test_e2e_recommendation.py
```

**Ожидаемый результат:** весь pipeline проходит от задачи до рекомендации.

**Примерное время:** 5–8 часов.  
**Коммит:** `Add end to end recommendation test`

---

# 22. Этап 20 — качество кода и стабильность

## 22.1. Добавить логирование

- [ ] Создать `src/utils/logging.py`.
- [ ] Настроить единый logger.
- [ ] Логировать запуск API.
- [ ] Логировать генерацию данных.
- [ ] Логировать обучение модели.
- [ ] Логировать inference.
- [ ] Логировать обращения к Plane.
- [ ] Логировать ошибки LLM.
- [ ] Не логировать секреты.

Файл:

```text
src/utils/logging.py
```

**Ожидаемый результат:** проще отлаживать проект.

**Примерное время:** 3–5 часов.  
**Коммит:** `Add application logging`

---

## 22.2. Добавить config loader

- [ ] Создать `src/utils/config.py`.
- [ ] Читать `.env`.
- [ ] Читать YAML-конфиги.
- [ ] Валидировать обязательные настройки.
- [ ] Добавить понятные ошибки.
- [ ] Использовать config loader во всех местах проекта.

Файл:

```text
src/utils/config.py
```

**Ожидаемый результат:** настройки проекта централизованы.

**Примерное время:** 4–6 часов.  
**Коммит:** `Add centralized configuration loader`

---

## 22.3. Прогнать форматирование и линтер

- [ ] Запустить `black`.
- [ ] Запустить `ruff`.
- [ ] Исправить предупреждения.
- [ ] Запустить `pytest`.
- [ ] Проверить, что всё зелёное.

Команды:

```bash
black src app scripts tests
```

```bash
ruff check src app scripts tests
```

```bash
pytest
```

**Ожидаемый результат:** код чистый и тесты проходят.

**Примерное время:** 2–6 часов.  
**Коммит:** `Clean code style and tests`

---

# 23. Этап 21 — демо-сценарии

## 23.1. Подготовить демо-задачи в Plane

- [ ] Создать задачу `Реализовать JWT-авторизацию`.
- [ ] Создать задачу `Добавить dashboard командной загрузки`.
- [ ] Создать задачу `Оптимизировать SQL-запросы отчётов`.
- [ ] Создать задачу `Добавить экспорт отчётов в PDF`.
- [ ] Создать задачу `Починить ошибку назначения исполнителя`.
- [ ] Добавить labels.
- [ ] Добавить priority.
- [ ] Добавить deadline.
- [ ] Оставить задачи без assignee.

**Ожидаемый результат:** есть набор задач для показа COMPASS AI.

**Примерное время:** 1–2 часа.  
**Коммит:** коммит не нужен, если только Plane UI.

---

## 23.2. Подготовить демо-сценарий Fast Delivery

- [ ] Взять задачу с коротким deadline.
- [ ] Запустить recommendation mode `fast_delivery`.
- [ ] Убедиться, что модель выбирает сильного сотрудника.
- [ ] Убедиться, что объяснение говорит про скорость и reliability.
- [ ] Сохранить response в `reports/demo_fast_delivery.json`.

Команда:

```bash
curl "http://localhost:8000/recommendations/issue/ISSUE_ID?mode=fast_delivery&write_back=false" > reports/demo_fast_delivery.json
```

**Ожидаемый результат:** показан сценарий “сделать быстро”.

**Примерное время:** 1–2 часа.  
**Коммит:** `Add fast delivery demo output`

---

## 23.3. Подготовить демо-сценарий Balanced Workload

- [ ] Взять задачу средней сложности.
- [ ] Запустить recommendation mode `balanced_workload`.
- [ ] Убедиться, что перегруженный senior не всегда top-1.
- [ ] Убедиться, что объяснение говорит про баланс загрузки.
- [ ] Сохранить response в `reports/demo_balanced_workload.json`.

Команда:

```bash
curl "http://localhost:8000/recommendations/issue/ISSUE_ID?mode=balanced_workload&write_back=false" > reports/demo_balanced_workload.json
```

**Ожидаемый результат:** показан сценарий балансировки команды.

**Примерное время:** 1–2 часа.  
**Коммит:** `Add balanced workload demo output`

---

## 23.4. Подготовить демо-сценарий Growth Mode

- [ ] Взять growth-задачу.
- [ ] Запустить recommendation mode `growth`.
- [ ] Убедиться, что модель предлагает middle/junior с допустимым риском.
- [ ] Убедиться, что объяснение говорит про развитие.
- [ ] Сохранить response в `reports/demo_growth_mode.json`.

Команда:

```bash
curl "http://localhost:8000/recommendations/issue/ISSUE_ID?mode=growth&write_back=false" > reports/demo_growth_mode.json
```

**Ожидаемый результат:** показан сценарий развития сотрудника.

**Примерное время:** 1–2 часа.  
**Коммит:** `Add growth mode demo output`

---

## 23.5. Подготовить демо-сценарий Risk Minimization

- [ ] Взять бизнес-критичную задачу.
- [ ] Запустить recommendation mode `risk_minimization`.
- [ ] Убедиться, что модель выбирает надёжного сотрудника.
- [ ] Убедиться, что объяснение говорит про снижение риска.
- [ ] Сохранить response в `reports/demo_risk_minimization.json`.

Команда:

```bash
curl "http://localhost:8000/recommendations/issue/ISSUE_ID?mode=risk_minimization&write_back=false" > reports/demo_risk_minimization.json
```

**Ожидаемый результат:** показан сценарий минимизации риска.

**Примерное время:** 1–2 часа.  
**Коммит:** `Add risk minimization demo output`

---

# 24. Этап 22 — финальная проверка проекта

## 24.1. Полный локальный запуск

- [ ] Запустить Docker Desktop.
- [ ] Запустить Plane.
- [ ] Активировать Python окружение.
- [ ] Запустить COMPASS API.
- [ ] Запустить Ollama.
- [ ] Запустить dashboard.
- [ ] Открыть Plane.
- [ ] Открыть dashboard.
- [ ] Проверить рекомендацию для одной задачи.
- [ ] Проверить запись комментария в Plane.
- [ ] Проверить отчёты.

Команды:

```bash
source .venv/bin/activate
```

```bash
uvicorn app.api:app --reload --host 0.0.0.0 --port 8000
```

```bash
ollama serve
```

```bash
streamlit run app/dashboard.py
```

**Ожидаемый результат:** вся система работает локально.

**Примерное время:** 2–4 часа.  
**Коммит:** `Verify full local system run`

---

## 24.2. Полный ML pipeline с нуля

- [ ] Удалить processed data.
- [ ] Сгенерировать synthetic data.
- [ ] Построить features.
- [ ] Разделить dataset.
- [ ] Обучить модель.
- [ ] Оценить модель.
- [ ] Экспортировать ONNX.
- [ ] Проверить ONNX.
- [ ] Сгенерировать отчёты.

Команды:

```bash
rm -rf data/processed/*
```

```bash
make generate-data
```

```bash
make build-features
```

```bash
make train
```

```bash
make evaluate
```

```bash
make export-onnx
```

```bash
make reports
```

**Ожидаемый результат:** проект воспроизводится с нуля.

**Примерное время:** 3–6 часов.  
**Коммит:** `Verify reproducible ML pipeline`

---

## 24.3. Проверка итоговой структуры файлов

- [ ] Проверить наличие `src`.
- [ ] Проверить наличие `app`.
- [ ] Проверить наличие `notebooks`.
- [ ] Проверить наличие `reports`.
- [ ] Проверить наличие `models/task_employee_matcher.onnx`.
- [ ] Проверить наличие `models/compass_matching_model.pt`.
- [ ] Проверить наличие `data/synthetic`.
- [ ] Проверить наличие `data/processed`.
- [ ] Проверить наличие tests.
- [ ] Проверить наличие dashboard.
- [ ] Проверить наличие интеграции с Plane.

Команда:

```bash
find . -maxdepth 3 -type f | sort
```

**Ожидаемый результат:** проект содержит все ожидаемые артефакты.

**Примерное время:** 1 час.  
**Коммит:** `Finalize project artifacts`

---

# 25. Этап 23 — финальная документация

Документацию писать только после готового MVP, чтобы не описывать несуществующие функции.

## 25.1. Обновить README.md

- [ ] Описать, что такое COMPASS AI.
- [ ] Описать проблему.
- [ ] Описать решение.
- [ ] Описать архитектуру.
- [ ] Описать agentic pipeline.
- [ ] Описать ML-модель.
- [ ] Описать интеграцию с Plane.
- [ ] Описать ONNX export.
- [ ] Описать Jupyter reports.
- [ ] Описать локальный запуск.
- [ ] Описать демо-сценарии.
- [ ] Добавить скриншоты.
- [ ] Добавить ограничения проекта.
- [ ] Указать, что данные синтетические.
- [ ] Указать, что проект учебный.

Разделы README:

```text
Overview
Problem
Solution
Features
Architecture
Agent Pipeline
Machine Learning Model
Plane Integration
Reports
Local Setup
Usage
Demo
Project Structure
Limitations
License
```

**Ожидаемый результат:** README объясняет проект человеку, который впервые открыл репозиторий.

**Примерное время:** 5–8 часов.  
**Коммит:** `Update project README`

---

## 25.2. Обновить `docs/doc.md`

- [ ] Проверить, что `docs/doc.md` соответствует реальной реализации.
- [ ] Удалить обещания, которые не были сделаны.
- [ ] Добавить реальные названия файлов.
- [ ] Добавить реальные endpoints.
- [ ] Добавить реальные модели.
- [ ] Добавить реальные метрики.
- [ ] Добавить реальные ограничения.
- [ ] Добавить схему архитектуры.

**Ожидаемый результат:** общая документация совпадает с кодом.

**Примерное время:** 3–5 часов.  
**Коммит:** `Update technical documentation`

---

## 25.3. Создать docs для API

- [ ] Создать `docs/api.md`.
- [ ] Описать `/health`.
- [ ] Описать `/version`.
- [ ] Описать `/recommendations/demo`.
- [ ] Описать `/recommendations/manual`.
- [ ] Описать `/recommendations/issue/{issue_id}`.
- [ ] Описать `/recommendations/project/{project_id}/open-issues`.
- [ ] Для каждого endpoint указать request.
- [ ] Для каждого endpoint указать response.
- [ ] Для каждого endpoint указать пример.

Файл:

```text
docs/api.md
```

**Ожидаемый результат:** API понятно без чтения кода.

**Примерное время:** 3–5 часов.  
**Коммит:** `Add API documentation`

---

## 25.4. Создать docs для ML

- [ ] Создать `docs/ml_model.md`.
- [ ] Описать задачу ML.
- [ ] Описать synthetic data.
- [ ] Описать признаки.
- [ ] Описать label.
- [ ] Описать архитектуру `TaskEmployeeMatchingNet`.
- [ ] Описать обучение.
- [ ] Описать метрики.
- [ ] Описать baseline comparisons.
- [ ] Описать ONNX export.
- [ ] Описать ограничения.

Файл:

```text
docs/ml_model.md
```

**Ожидаемый результат:** ML-часть проекта выглядит как полноценная инженерная работа.

**Примерное время:** 4–6 часов.  
**Коммит:** `Add ML model documentation`

---

## 25.5. Создать docs для Plane integration

- [ ] Создать `docs/plane_integration.md`.
- [ ] Описать, как Plane используется.
- [ ] Описать, какие сущности Plane используются.
- [ ] Описать REST API integration.
- [ ] Описать MCP experiment.
- [ ] Описать write-back comments.
- [ ] Описать auto-assign mode.
- [ ] Описать ограничения self-hosted Plane.
- [ ] Описать настройку `.env`.

Файл:

```text
docs/plane_integration.md
```

**Ожидаемый результат:** интеграцию можно повторить.

**Примерное время:** 4–6 часов.  
**Коммит:** `Add Plane integration documentation`

---

## 25.6. Сделать скриншоты

- [ ] Сделать скриншот Plane workspace.
- [ ] Сделать скриншот задачи до рекомендации.
- [ ] Сделать скриншот комментария COMPASS AI в Plane.
- [ ] Сделать скриншот dashboard overview.
- [ ] Сделать скриншот team workload.
- [ ] Сделать скриншот model metrics.
- [ ] Сделать скриншот fairness analysis.
- [ ] Сохранить скриншоты в `docs/assets`.

Папка:

```text
docs/assets
```

Команда:

```bash
mkdir -p docs/assets
```

**Ожидаемый результат:** README можно сделать визуально убедительным.

**Примерное время:** 2–3 часа.  
**Коммит:** `Add project screenshots`

---

## 25.7. Финальный cleanup

- [ ] Проверить, что `.env` не попал в git.
- [ ] Проверить, что тяжёлые модели не попали в git, если они слишком большие.
- [ ] Проверить, что синтетические маленькие CSV можно оставить или убрать.
- [ ] Проверить, что README не содержит секретов.
- [ ] Проверить, что docs не содержат секретов.
- [ ] Запустить `pytest`.
- [ ] Запустить `ruff`.
- [ ] Запустить API.
- [ ] Запустить dashboard.
- [ ] Сделать финальный коммит.

Команды:

```bash
git status
```

```bash
pytest
```

```bash
ruff check src app scripts tests
```

**Ожидаемый результат:** репозиторий готов к публикации.

**Примерное время:** 2–4 часа.  
**Коммит:** `Prepare final project release`

---

# 26. Итоговая структура проекта

К финалу проект должен примерно выглядеть так:

```text
COMPASS-AI/
├── README.md
├── LICENSE
├── .gitignore
├── .env.example
├── requirements.txt
├── requirements-dev.txt
├── pyproject.toml
├── Makefile
├── docker-compose.compass.yml
│
├── app/
│   ├── api.py
│   └── dashboard.py
│
├── config/
│   ├── paths.yaml
│   ├── settings.yaml
│   └── synthetic_data.yaml
│
├── data/
│   ├── raw/
│   ├── synthetic/
│   │   ├── employees.csv
│   │   ├── employees.json
│   │   ├── tasks.csv
│   │   ├── tasks.json
│   │   ├── assignments.csv
│   │   └── assignments.json
│   └── processed/
│       ├── training_pairs.parquet
│       ├── train.parquet
│       ├── val.parquet
│       ├── test.parquet
│       ├── skill_vocab.json
│       ├── task_plane_mapping.csv
│       └── employee_plane_mapping.csv
│
├── docs/
│   ├── doc.md
│   ├── todo.md
│   ├── api.md
│   ├── ml_model.md
│   ├── plane_integration.md
│   └── assets/
│
├── models/
│   ├── compass_matching_model.pt
│   └── task_employee_matcher.onnx
│
├── notebooks/
│   ├── 01_synthetic_data_generation.ipynb
│   ├── 02_data_analysis.ipynb
│   ├── 03_model_training.ipynb
│   ├── 04_model_evaluation.ipynb
│   ├── 05_fairness_analysis.ipynb
│   ├── 06_plane_integration_demo.ipynb
│   └── 07_business_report.ipynb
│
├── plane/
│   ├── docker/
│   └── seed/
│       ├── create_labels.py
│       ├── create_tasks.py
│       └── plane_schema_notes.md
│
├── reports/
│   ├── figures/
│   ├── notebooks/
│   ├── model_metrics.json
│   ├── ranking_metrics.json
│   ├── onnx_validation.json
│   ├── training_history.csv
│   ├── test_predictions.csv
│   ├── demo_fast_delivery.json
│   ├── demo_balanced_workload.json
│   ├── demo_growth_mode.json
│   └── demo_risk_minimization.json
│
├── scripts/
│   ├── check_plane_connection.py
│   └── generate_synthetic_data.py
│
├── src/
│   ├── agents/
│   │   ├── state.py
│   │   ├── task_analyzer.py
│   │   ├── team_analyzer.py
│   │   ├── matching_agent.py
│   │   ├── explanation_agent.py
│   │   ├── plane_agent.py
│   │   └── orchestrator.py
│   │
│   ├── data/
│   │   ├── generate_employees.py
│   │   ├── generate_tasks.py
│   │   ├── generate_assignments.py
│   │   └── split_dataset.py
│   │
│   ├── features/
│   │   ├── skill_vectorizer.py
│   │   ├── text_embeddings.py
│   │   └── build_features.py
│   │
│   ├── integration/
│   │   ├── plane_client.py
│   │   ├── plane_mapping.py
│   │   ├── plane_comment_formatter.py
│   │   └── mcp_client.py
│   │
│   ├── llm/
│   │   └── ollama_client.py
│   │
│   ├── models/
│   │   ├── schemas.py
│   │   ├── dataset.py
│   │   ├── matching_net.py
│   │   ├── train.py
│   │   ├── evaluate.py
│   │   ├── ranking_metrics.py
│   │   ├── inference.py
│   │   ├── export_onnx.py
│   │   └── onnx_inference.py
│   │
│   ├── recommendation/
│   │   ├── skill_matching.py
│   │   ├── workload_scoring.py
│   │   ├── growth_scoring.py
│   │   └── rule_based_ranker.py
│   │
│   ├── reports/
│   │   └── generate_notebooks.py
│   │
│   └── utils/
│       ├── config.py
│       └── logging.py
│
├── tests/
│   ├── test_generate_employees.py
│   ├── test_generate_tasks.py
│   ├── test_generate_assignments.py
│   ├── test_skill_matching.py
│   ├── test_workload_scoring.py
│   ├── test_growth_scoring.py
│   ├── test_rule_based_ranker.py
│   ├── test_dataset.py
│   ├── test_matching_net.py
│   ├── test_onnx_inference.py
│   ├── test_plane_client.py
│   └── test_e2e_recommendation.py
│
└── tools/
```

---

# 27. Финальный definition of done

Проект считается готовым, если выполнено:

- [ ] Plane локально запускается.
- [ ] В Plane есть workspace, проекты, задачи и синтетическая команда.
- [ ] COMPASS API запускается локально.
- [ ] Dashboard запускается локально.
- [ ] Синтетические данные генерируются одной командой.
- [ ] Features строятся одной командой.
- [ ] Собственная нейронная сеть обучается.
- [ ] Есть сохранённый `.pt` checkpoint.
- [ ] Есть экспортированный `.onnx` файл.
- [ ] ONNX inference проверен.
- [ ] Есть top-3 рекомендации по задаче.
- [ ] Есть 4 режима рекомендации.
- [ ] Есть русскоязычное объяснение через LLM.
- [ ] Есть fallback explanation без LLM.
- [ ] Есть запись рекомендации в Plane comment.
- [ ] Есть batch-анализ задач проекта.
- [ ] Есть Jupyter notebooks.
- [ ] Есть HTML-отчёты.
- [ ] Есть fairness-анализ.
- [ ] Есть comparison с random baseline.
- [ ] Есть comparison с rule-based baseline.
- [ ] Есть тесты.
- [ ] README обновлён.
- [ ] Документация обновлена.
- [ ] Скриншоты добавлены.
- [ ] Секреты не попали в git.
- [ ] Финальный коммит сделан.

Финальный коммит:

```text
Complete COMPASS AI project
```

---