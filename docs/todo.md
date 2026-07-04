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

- [x] Установить Docker Desktop для Mac, если не установлен.
- [x] Запустить Docker Desktop.
- [x] Проверить работу Docker.
- [x] Проверить работу Docker Compose.
- [x] Убедиться, что Docker использует достаточно ресурсов.

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

**Фактический результат:** Docker Desktop работает, Docker Compose работает, Plane containers успешно запускаются локально.

**Ожидаемый результат:** Docker работает.

**Примерное время:** 30–60 минут.  
**Коммит:** коммит не нужен.

---

## 5.2. Изучить официальный способ запуска Plane

- [x] Открыть `https://github.com/makeplane/plane`.
- [x] Открыть `https://developers.plane.so/self-hosting`.
- [x] Открыть Docker Compose guide.
- [x] Зафиксировать, какой способ запуска актуален.
- [x] Не копировать слепо старые compose-файлы из чужих гайдов.
- [x] Использовать официальный self-hosting способ Plane.
- [x] Зафиксировать локальные заметки по запуску Plane в `plane/docker/plane_local_setup.md`.

**Важно:** сначала поднять Plane отдельно, без COMPASS AI. Не надо сразу смешивать Plane и свой backend.

**Фактический способ запуска:** Plane запускается отдельно из локального checkout `plane/docker/plane-source` через официальный Docker Compose подход.

**Ожидаемый результат:** понятно, как локально запускать Plane.

**Примерное время:** 1–2 часа.  
**Коммит:** коммит не нужен, если ничего не добавлялось.

---

## 5.3. Установить Plane локально

- [x] Создать отдельную папку вне основного кода или внутри `plane/docker`.
- [x] Скачать/склонировать нужные self-hosting файлы Plane по официальной инструкции.
- [x] Создать `.env` для Plane.
- [x] Создать локальные `.env` файлы для Plane apps.
- [x] Проверить порты Plane.
- [x] Запустить Plane через Docker Compose.
- [x] Открыть Plane в браузере.
- [x] Создать первого пользователя-админа.
- [x] Открыть God Mode / Instance Admin.
- [x] Проверить, что Plane API отвечает.
- [x] Проверить, что Plane main UI отвечает.
- [x] Проверить, что Plane containers работают.

Plane source расположен здесь:

```text
plane/docker/plane-source
```

Команда клонирования:

```bash
git clone https://github.com/makeplane/plane.git plane/docker/plane-source
```

Текущая ветка Plane:

```text
preview
```

Plane source не коммитится в COMPASS AI и должен быть добавлен в `.gitignore`:

```gitignore
# External Plane source checkout
plane/docker/plane-source/
```

Созданы локальные env-файлы:

```text
plane/docker/plane-source/.env
plane/docker/plane-source/apps/api/.env
plane/docker/plane-source/apps/web/.env
plane/docker/plane-source/apps/admin/.env
plane/docker/plane-source/apps/space/.env
plane/docker/plane-source/apps/live/.env
```

Важные локальные URL-настройки Plane:

```text
WEB_URL=http://localhost
APP_BASE_URL=http://localhost
ADMIN_BASE_URL=http://localhost/god-mode
ADMIN_BASE_PATH=/god-mode
SPACE_BASE_URL=http://localhost/spaces
SPACE_BASE_PATH=/spaces
LIVE_BASE_URL=http://localhost/live
LIVE_BASE_PATH=/live
```

Команда проверки Docker Compose config:

```bash
docker compose config
```

Команда запуска Plane через Docker Compose:

```bash
docker compose up -d
```

Команда проверки контейнеров:

```bash
docker compose ps
```

Команда проверки API:

```bash
docker compose exec proxy wget -S -O- http://api:8000 2>&1 | head -30
```

Ожидаемый API-ответ:

```text
HTTP/1.1 200 OK
{"status": "OK"}
```

Команда проверки main UI:

```bash
curl -I http://localhost
```

Ожидаемый UI-ответ:

```text
HTTP/1.1 200 OK
```

Локальный Plane main UI:

```text
http://localhost
```

Локальный God Mode / Instance Admin:

```text
http://localhost/god-mode/general/
```

Первый instance admin создан через God Mode setup.

Данные instance admin:

```text
First name: Andrey
Last name: Zakharov
Email: admin@compass.local
Company name: COMPASS AI Lab
```

Пароль admin-пользователя является локальным секретом и не должен храниться в git или документации.

**Важно:** точные команды Plane брать из актуальной официальной документации, потому что структура self-hosting может меняться.

**Фактический результат:** Plane доступен локально, containers запускаются, API отвечает, main UI отвечает, God Mode доступен, первый instance admin создан.

**Ожидаемый результат:** Plane доступен в браузере локально.

**Примерное время:** 2–4 часа.  
**Коммит:** `Add Plane local setup notes`

---

## 5.4. Создать тестовый workspace в Plane

- [x] Открыть локальный Plane.
- [x] Создать workspace `compass-ai-lab`.
- [x] Создать проект `Backend Platform`.
- [x] Создать проект `Frontend Platform`.
- [x] Создать проект `Data Platform`.
- [x] Создать проект `Internal Tools`.
- [x] Создать несколько статусов задач.
- [x] Создать несколько labels.
- [x] Создать несколько cycles/sprints, если Plane это поддерживает в установленной версии.
- [x] Создать тестовый cycle в `Backend Platform`.
- [x] Создать тестовый work item в `Backend Platform`.

Workspace:

```text
compass-ai-lab
```

Workspace display/company name:

```text
COMPASS AI Lab
```

Созданные проекты:

```text
Backend Platform
Frontend Platform
Data Platform
Internal Tools
```

Рекомендуемые project identifiers:

```text
BACK
FRONT
DATA
TOOLS
```

Фактические статусы Plane используются стандартные:

```text
Backlog -> Backlog
Unstarted -> Todo
Started -> In Progress
Completed -> Done
Cancelled -> Cancelled
```

Целевые статусы из roadmap:

```text
Backlog
Ready
In Progress
Review
Done
Blocked
```

Фактическое решение: стандартные Plane states оставлены без ручной переработки, потому что они покрывают базовый workflow для учебного workspace.

Labels:

```text
backend
frontend
ml
data
devops
bug
feature
refactoring
urgent
growth-task
```

Фактическое решение по labels: labels созданы в проекте `Backend Platform`, потому что в текущем UI Plane общие workspace-level labels не были найдены. В следующем этапе labels можно будет автоматизировать через API/seed-скрипт и размножить по остальным проектам при необходимости.

Cycles/sprints:

```text
Cycles созданы во всех проектах.
```

Тестовый cycle в `Backend Platform`:

```text
Sprint 1 — COMPASS AI Setup
```

Тестовый work item создан в проекте:

```text
Backend Platform
```

Тестовый work item title:

```text
Реализовать JWT-авторизацию
```

Тестовый work item description:

```text
Нужно реализовать авторизацию через JWT для backend API. Требуется добавить login endpoint, refresh token flow, logout сценарий и защиту приватных endpoint-ов. Задача важна для безопасности MVP и должна быть выполнена с тестами.
```

Labels тестового work item:

```text
backend
feature
urgent
```

Priority:

```text
High
```

Assignee:

```text
empty
```

**Фактический результат:** в Plane есть учебная рабочая область `compass-ai-lab`, проекты, labels в `Backend Platform`, стандартные workflow states, cycles во всех проектах и тестовый work item.

**Ожидаемый результат:** в Plane есть учебная рабочая область, похожая на настоящую команду.

**Примерное время:** 1 час.  
**Коммит:** коммит не нужен, если всё делалось только в Plane UI.

---

## 5.5. Добавить локальные скрипты управления Plane

- [x] Создать скрипт полного запуска Plane.
- [x] Создать скрипт полного выключения Plane без удаления данных.
- [x] Проверить, что stop script останавливает Plane и освобождает ресурсы.
- [x] Проверить, что после stop сайт `http://localhost` недоступен.
- [x] Проверить, что start script снова поднимает Plane.
- [x] Проверить, что данные Plane сохраняются после stop/start.

Скрипт запуска:

```text
scripts/start_plane.sh
```

Команда запуска:

```bash
./scripts/start_plane.sh
```

Скрипт остановки:

```text
scripts/stop_plane.sh
```

Команда остановки:

```bash
./scripts/stop_plane.sh
```

Stop script использует:

```bash
docker compose stop
```

Это значит:

```text
контейнеры останавливаются
CPU/RAM освобождаются
сайт http://localhost перестаёт открываться
Docker volumes сохраняются
данные Plane не удаляются
```

Команду ниже не использовать для обычного выключения Plane:

```bash
docker compose down -v
```

Потому что `down -v` удаляет volumes и может удалить локальные данные Plane.

**Фактический результат:** Plane можно полностью запускать и останавливать из корня COMPASS AI через shell scripts.

**Ожидаемый результат:** локальный Plane удобно поднимать и выключать без удаления данных.

**Примерное время:** 30–60 минут.  
**Коммит:** `Add Plane local setup notes`

---

## 5.6. Зафиксировать локальные заметки по Plane

- [x] Создать или обновить `plane/docker/plane_local_setup.md`.
- [x] Описать локальный путь Plane source.
- [x] Описать локальные env-файлы.
- [x] Описать основные локальные URL.
- [x] Описать God Mode / Instance Admin.
- [x] Описать созданный admin account без сохранения пароля.
- [x] Описать workspace, projects, labels, states, cycles и test work item.
- [x] Описать команды запуска и остановки.
- [x] Описать, что Plane source и env-файлы не должны коммититься.

Файл заметок:

```text
plane/docker/plane_local_setup.md
```

**Фактический результат:** локальная инструкция по Plane сохранена в репозитории COMPASS AI.

**Ожидаемый результат:** состояние локального Plane понятно и воспроизводимо.

**Примерное время:** 30 минут.  
**Коммит:** `Add Plane local setup notes`

---

# 6. Этап 4 — изучение данных Plane перед разработкой интеграции

## 6.1. Получить доступ к Plane API

- [x] Найти в Plane настройки API/token.
- [x] Создать API token, если Plane это поддерживает в установленной версии.
- [x] Сохранить токен только в локальный `.env`.
- [x] Добавить пример переменных в `.env.example` без секретов.
- [x] Проверить доступ к API через `curl` или `httpx`.
- [x] Проверить, что API работает через local Plane proxy.
- [x] Проверить, что авторизация работает через header `x-api-key`.
- [x] Проверить, что COMPASS AI видит workspace `compass-ai-lab`.

Поля в `.env.example`:

```text
PLANE_BASE_URL=http://localhost
PLANE_API_KEY=replace_with_your_token
PLANE_WORKSPACE_SLUG=compass-ai-lab
COMPASS_API_URL=http://localhost:8000
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:1.5b-instruct
```

Фактические локальные значения:

```text
PLANE_BASE_URL=http://localhost
PLANE_WORKSPACE_SLUG=compass-ai-lab
```

Секретное значение хранится только в локальном `.env`:

```text
PLANE_API_KEY=<local_api_token>
```

API token нельзя коммитить.

Формат авторизации:

```text
x-api-key: $PLANE_API_KEY
```

Проверенный endpoint проектов:

```text
GET /api/v1/workspaces/compass-ai-lab/projects/
```

Проверочная команда:

```bash
curl --request GET --url "$PLANE_BASE_URL/api/v1/workspaces/$PLANE_WORKSPACE_SLUG/projects/" --header "x-api-key: $PLANE_API_KEY"
```

Фактический результат:

```text
Plane API доступен.
Авторизация через x-api-key работает.
Workspace compass-ai-lab найден.
Список проектов успешно читается.
```

**Ожидаемый результат:** понятно, как COMPASS AI будет авторизоваться в Plane.

**Примерное время:** 1–2 часа.  
**Коммит:** `Add environment configuration template`

---

## 6.2. Исследовать сущности Plane

- [x] Выяснить, как Plane называет задачи в текущей версии: `issues` или `work items`.
- [x] Выяснить, какие поля есть у задачи.
- [x] Выяснить, как получить список проектов.
- [x] Выяснить, как получить список участников workspace/project.
- [x] Выяснить, как получить статусы.
- [x] Выяснить, как получить labels.
- [x] Выяснить, как добавить комментарий к задаче.
- [x] Выяснить, как обновить assignee.
- [x] Зафиксировать найденные поля в локальном техническом файле, но не в финальной документации.
- [x] Сохранить raw API samples локально в `data/raw/plane_api_samples/`.
- [x] Зафиксировать реальные project IDs.
- [x] Зафиксировать реальные state IDs.
- [x] Зафиксировать реальные label IDs.
- [x] Зафиксировать test work item ID.
- [x] Зафиксировать, какие поля COMPASS AI будет использовать первыми.

Рабочий файл для заметок:

```text
plane/seed/plane_schema_notes.md
```

Команда:

```bash
touch plane/seed/plane_schema_notes.md
```

Raw API samples:

```text
data/raw/plane_api_samples/projects.json
data/raw/plane_api_samples/backend_work_items.json
data/raw/plane_api_samples/backend_work_item_detail.json
data/raw/plane_api_samples/backend_states.json
data/raw/plane_api_samples/backend_labels.json
data/raw/plane_api_samples/backend_work_item_comments.json
```

Эти файлы не коммитятся, потому что могут содержать локальные user IDs, emails, workspace IDs и project IDs.

Фактический термин Plane для задач:

```text
work items
```

Совместимый термин roadmap:

```text
issues
```

Решение в коде:

```text
основные методы используют work_item / work_items
alias-методы используют issue / issues
```

Локальный workspace:

```text
slug: compass-ai-lab
id: c81d4a58-ee30-4b3f-9221-cc1d95566440
```

Проверенный endpoint проектов:

```text
GET /api/v1/workspaces/{workspace_slug}/projects/
```

Фактические проекты:

```text
Backend Platform: e608e7ad-f4fe-401d-b0f3-5570e82f08ee, identifier BACK
Frontend Platform: 33832fc6-ade4-4ac0-a937-9ba70b0859d8, identifier FRONT
Data Platform: cdbeb78a-e8d3-4277-ad9b-13d6b8e44dab, identifier DATA
Internal Tools: 50d969c6-ae4c-4afe-a8aa-33cdb478f787, identifier TOOLS
```

Фактическая структура projects response:

```text
grouped_by
sub_grouped_by
total_count
next_cursor
prev_cursor
next_page_results
prev_page_results
count
total_pages
total_results
extra_stats
results
```

Фактический список проектов находится в:

```text
results
```

Поля проекта, которые COMPASS AI использует первыми:

```text
id
name
identifier
total_members
total_cycles
workspace
```

Backend Platform:

```text
project_id: e608e7ad-f4fe-401d-b0f3-5570e82f08ee
identifier: BACK
total_members: 1
total_cycles: 1
total_modules: 0
cycle_view: true
is_time_tracking_enabled: false
is_issue_type_enabled: false
```

Проверенный endpoint work items:

```text
GET /api/v1/workspaces/{workspace_slug}/projects/{project_id}/work-items/
```

Фактический Backend Platform endpoint:

```text
GET /api/v1/workspaces/compass-ai-lab/projects/e608e7ad-f4fe-401d-b0f3-5570e82f08ee/work-items/
```

Фактическая структура work items response:

```text
grouped_by
sub_grouped_by
total_count
next_cursor
prev_cursor
next_page_results
prev_page_results
count
total_pages
total_results
extra_stats
results
```

Фактический список work items находится в:

```text
results
```

Тестовый work item:

```text
id: 22ab005a-a3b1-49e1-947b-3d3251c63e47
name: Реализовать JWT-авторизацию
sequence_id: 1
priority: high
project: e608e7ad-f4fe-401d-b0f3-5570e82f08ee
state: 633f3777-fce6-40bb-a6e7-096df86429a4
assignees: []
```

Labels тестового work item:

```text
backend: 19ad9f4d-9f1f-4518-9076-419b4fb2f3e5
feature: 5b1f0192-7664-4679-b2c3-98e1fe8a4e8e
urgent: caa1adb5-1451-48dd-9d07-8e1c641c633e
```

Минимально нужные поля задачи по roadmap:

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

Фактически найденные важные поля work item:

```text
id
name
description_html
priority
start_date
target_date
sequence_id
completed_at
project
state
estimate_point
assignees
labels
created_at
updated_at
```

COMPASS AI mapping:

```text
Plane work item id -> plane_work_item_id / plane_issue_id
Plane work item name -> task title
Plane description_html -> task description
Plane priority -> task priority
Plane state -> task state id
Plane labels -> required stack / task type hints
Plane assignees -> current assignees
Plane target_date -> deadline signal
Plane estimate_point -> estimate signal, if enabled later
```

Проверенный endpoint detail одного work item:

```text
GET /api/v1/workspaces/{workspace_slug}/projects/{project_id}/work-items/{work_item_id}/
```

Фактический test work item detail endpoint:

```text
GET /api/v1/workspaces/compass-ai-lab/projects/e608e7ad-f4fe-401d-b0f3-5570e82f08ee/work-items/22ab005a-a3b1-49e1-947b-3d3251c63e47/
```

Проверенный endpoint states:

```text
GET /api/v1/workspaces/{workspace_slug}/projects/{project_id}/states/
```

Фактические states Backend Platform:

```text
Backlog: 8325f1a6-aa63-46a9-8cbb-340848a506aa, group backlog
Todo: 633f3777-fce6-40bb-a6e7-096df86429a4, group unstarted
In Progress: 74855d6f-1911-4e7d-a355-07521647c3f5, group started
Done: b68d69f3-e88a-4ea1-b8c6-626e083a2d41, group completed
Cancelled: 34a698dc-d031-43f5-b875-a4af26fcc24d, group cancelled
```

COMPASS AI state interpretation:

```text
backlog -> not ready or future work
unstarted -> ready to be assigned or started
started -> already active
completed -> finished
cancelled -> excluded from recommendation backlog
```

Текущий test work item state:

```text
state id: 633f3777-fce6-40bb-a6e7-096df86429a4
state name: Todo
state group: unstarted
```

Проверенный endpoint labels:

```text
GET /api/v1/workspaces/{workspace_slug}/projects/{project_id}/labels/
```

Фактические Backend Platform labels:

```text
growth-task: dff694be-63b4-40bc-ade8-96920df9673d
urgent: caa1adb5-1451-48dd-9d07-8e1c641c633e
refactoring: 97ee2eee-eaa8-4fd6-8742-dd9c46e54979
feature: 5b1f0192-7664-4679-b2c3-98e1fe8a4e8e
bug: ce9f294a-bef7-4441-97b3-49576aafc371
devops: a12c8e8c-3bf5-49c7-a20a-43a344e07090
data: bb5f64d5-870a-4b26-bbd4-980b983c7261
ml: 754b3ad4-c8ce-4f8a-8c93-4013e6e6acd0
frontend: 8d02ccac-3438-492c-b087-f54c12abb6fd
backend: 19ad9f4d-9f1f-4518-9076-419b4fb2f3e5
```

Фактическое решение по labels:

```text
Labels созданы в Backend Platform.
Shared workspace-level labels в текущем Plane UI не найдены.
Если нужно, labels будут размножены по другим проектам позже через seed script.
```

COMPASS AI label interpretation:

```text
backend -> backend stack / backend task
frontend -> frontend stack / frontend task
ml -> ML/data science task signal
data -> data/analytics task signal
devops -> infrastructure/deployment task signal
bug -> bugfix task type
feature -> feature task type
refactoring -> refactoring task type
urgent -> urgency/business priority signal
growth-task -> learning/development signal
```

Проверенный endpoint comments на чтение:

```text
GET /api/v1/workspaces/{workspace_slug}/projects/{project_id}/work-items/{work_item_id}/comments/
```

Фактический comments endpoint тестовой задачи:

```text
GET /api/v1/workspaces/compass-ai-lab/projects/e608e7ad-f4fe-401d-b0f3-5570e82f08ee/work-items/22ab005a-a3b1-49e1-947b-3d3251c63e47/comments/
```

Фактический результат comments:

```text
total_count: 0
count: 0
total_pages: 0
total_results: 0
results: []
```

Подготовленный будущий endpoint для создания комментария:

```text
POST /api/v1/workspaces/{workspace_slug}/projects/{project_id}/work-items/{work_item_id}/comments/
```

Важно:

```text
POST comment body будет проверяться отдельно на этапе write-back.
На текущем этапе реальные комментарии в Plane не писались.
```

Минимально нужно узнать поля пользователя:

```text
id
display_name
email
avatar
role
```

Фактический статус по пользователям:

```text
project members endpoint добавлен в PlaneClient как list_project_members(project_id)
точный response shape будет проверяться на следующем этапе, когда появится синтетическая команда и mapping employee -> Plane user
```

Фактический статус по assignee update:

```text
update_work_item_assignee(project_id, work_item_id, assignee_id) подготовлен в PlaneClient
реальный PATCH payload будет проверяться позже на этапе optional auto-assignment
по умолчанию автоматическое назначение делать нельзя
```

Фактический статус по cycles:

```text
Cycles созданы во всех проектах через UI
Backend Platform имеет total_cycles: 1
cycles endpoint будет проверяться позже, если cycle data понадобится для workload/context
```

**Ожидаемый результат:** ты не придумываешь интеграцию вслепую, а опираешься на реальные поля Plane.

**Примерное время:** 2–3 часа.  
**Коммит:** `Document Plane data model notes`

---

## 6.3. Написать минимальный Plane client

- [x] Создать файл `src/integration/plane_client.py`.
- [x] Реализовать класс `PlaneClient`.
- [x] Добавить чтение настроек из `.env`.
- [x] Добавить метод проверки соединения.
- [x] Добавить метод получения workspace.
- [x] Добавить метод получения projects.
- [x] Добавить метод получения issues/work items.
- [x] Добавить метод получения project members.
- [x] Добавить метод получения labels.
- [x] Добавить метод добавления комментария.
- [x] Добавить метод обновления assignee, если API позволяет.
- [x] Не добавлять ML-логику в этот файл.
- [x] Добавить методы для современной терминологии Plane: `work_items`.
- [x] Добавить compatibility aliases для roadmap-терминологии: `issues`.
- [x] Добавить метод получения states.
- [x] Добавить метод чтения comments.
- [x] Добавить обработку HTTP-ошибок через `PlaneClientError`.

Файл:

```text
src/integration/plane_client.py
```

Класс:

```text
PlaneClient
```

Основные методы:

```text
healthcheck()
api_healthcheck()
get_workspace()
list_projects()
list_project_members(project_id)
list_work_items(project_id)
get_work_item(project_id, work_item_id)
list_states(project_id)
list_labels(project_id)
list_work_item_comments(project_id, work_item_id)
create_work_item_comment(project_id, work_item_id, text)
update_work_item_assignee(project_id, work_item_id, assignee_id)
```

Compatibility alias methods:

```text
list_issues(project_id)
get_issue(project_id, issue_id)
create_issue_comment(project_id, issue_id, text)
update_issue_assignee(project_id, issue_id, assignee_id)
```

Важно:

```text
PlaneClient содержит только REST API communication.
PlaneClient не содержит ML-логику.
PlaneClient не принимает решений по рекомендации.
PlaneClient не логирует секреты.
```

Текущий проверенный read path:

```text
list_projects()
list_work_items(project_id)
get_work_item(project_id, work_item_id)
list_states(project_id)
list_labels(project_id)
list_work_item_comments(project_id, work_item_id)
```

Подготовленные write methods:

```text
create_work_item_comment(project_id, work_item_id, text)
update_work_item_assignee(project_id, work_item_id, assignee_id)
```

Важно:

```text
write methods подготовлены, но реальные write-back операции будут проверяться позже,
когда будет реализован формат комментария COMPASS AI и защита от дублей.
```

**Ожидаемый результат:** есть отдельный слой для общения с Plane.

**Примерное время:** 3–5 часов.  
**Коммит:** `Add Plane API client`

---

## 6.4. Написать CLI для проверки Plane client

- [x] Создать `scripts/check_plane_connection.py`.
- [x] Скрипт должен загружать `.env`.
- [x] Скрипт должен вызывать `PlaneClient.healthcheck()`.
- [x] Скрипт должен вывести список проектов.
- [x] Скрипт должен вывести количество задач в каждом проекте.
- [x] Скрипт должен завершаться понятной ошибкой, если Plane недоступен.
- [x] Скрипт должен вывести количество states в каждом проекте.
- [x] Скрипт должен вывести количество labels в каждом проекте.
- [x] Скрипт должен вывести первый work item, если он есть.
- [x] Скрипт должен продолжать проверку остальных проектов, если один проект частично не проверился.

Файл:

```text
scripts/check_plane_connection.py
```

Команда запуска:

```bash
python scripts/check_plane_connection.py
```

Фактический успешный вывод:

```text
Checking Plane connection...
Workspace slug: compass-ai-lab
Base URL: http://localhost
Plane API healthcheck: OK
Projects found: 4

Project: Backend Platform (BACK)
Project ID: e608e7ad-f4fe-401d-b0f3-5570e82f08ee
  Work items: 1
  States: 5
  Labels: 10
  First work item: Реализовать JWT-авторизацию

Project: Frontend Platform (FRONT)
Project ID: 33832fc6-ade4-4ac0-a937-9ba70b0859d8
  Work items: 0
  States: 5
  Labels: 0

Project: Data Platform (DATA)
Project ID: cdbeb78a-e8d3-4277-ad9b-13d6b8e44dab
  Work items: 0
  States: 5
  Labels: 0

Project: Internal Tools (TOOLS)
Project ID: 50d969c6-ae4c-4afe-a8aa-33cdb478f787
  Work items: 0
  States: 5
  Labels: 0

Plane connection check completed.
```

Фактический результат:

```text
COMPASS AI видит Plane.
COMPASS AI видит workspace compass-ai-lab.
COMPASS AI видит 4 проекта.
COMPASS AI читает work items.
COMPASS AI читает states.
COMPASS AI читает labels.
```

**Ожидаемый результат:** можно быстро проверить, что Plane и COMPASS AI видят друг друга.

**Примерное время:** 1–2 часа.  
**Коммит:** `Add Plane connection checker`

---

# 7. Этап 5 — проектирование синтетической команды и данных

## 7.1. Определить состав синтетической команды

- [x] Создать список сотрудников.
- [x] Сделать команду реалистичной, не слишком большой.
- [x] Использовать 12–20 сотрудников.
- [x] Добавить разные роли.
- [x] Добавить разные грейды.
- [x] Добавить разные навыки.
- [x] Добавить разные цели развития.
- [x] Добавить разную текущую загрузку.
- [x] Не использовать реальные персональные данные.
- [x] Создать человекочитаемый design-документ.
- [x] Создать машинно-читаемую YAML-схему для будущего генератора данных.

Design-документ:

```text
docs/synthetic_data_design.md
```

Машинно-читаемая схема:

```text
config/synthetic_schema.yaml
```

Фактический размер синтетической команды:

```text
18 сотрудников
```

Фактический состав:

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

Роли в YAML:

```text
backend_developer
frontend_developer
qa_engineer
data_ml_engineer
devops_engineer
team_lead
```

Грейды:

```text
junior
middle
senior
lead
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
active_tasks_count
avg_completion_speed
avg_quality_score
deadline_reliability
learning_goals
mentor_level
availability
timezone
```

Важное решение:

```text
plane_user_id может быть пустым на этапе synthetic data.
Связь employee_id -> plane_user_id будет сделана позже через data/processed/employee_plane_mapping.csv.
```

**Ожидаемый результат:** есть понятная учебная команда, для которой можно генерировать задачи и историю.

**Примерное время:** 1–2 часа.  
**Коммит:** `Define synthetic team schema`

---

## 7.2. Определить словари навыков

- [x] Создать список технических навыков.
- [x] Создать список soft/management навыков.
- [x] Создать список доменных навыков.
- [x] Создать шкалу уровней навыков от 0 до 5.
- [x] Привязать навыки к ролям.
- [x] Подготовить taxonomy для будущего `skill_vectorizer.py`.
- [x] Подготовить taxonomy для rule-based baseline.
- [x] Подготовить taxonomy для ML features.

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

Доменные навыки:

```text
backend_architecture
frontend_architecture
qa_strategy
data_pipelines
ml_experimentation
devops_operations
product_thinking
team_coordination
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

Фактическое решение:

```text
Одна taxonomy используется и для сотрудников, и для задач.
Отсутствующий навык считается уровнем 0.
Порядок skills должен быть стабильным при feature engineering.
```

**Ожидаемый результат:** skills можно превратить в вектор для модели.

**Примерное время:** 1 час.  
**Коммит:** `Define skills taxonomy`

---

## 7.3. Определить типы задач

- [x] Создать список типов задач.
- [x] Для каждого типа определить частые навыки.
- [x] Для каждого типа определить среднюю сложность.
- [x] Для каждого типа определить среднее время выполнения.
- [x] Добавить задачи для развития junior/middle сотрудников.
- [x] Учесть реальные поля Plane work items из этапа 6.
- [x] Добавить совместимость `plane_work_item_id` и `plane_issue_id`.

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
plane_work_item_id
plane_issue_id
plane_project_id
project_key
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
source
created_at
updated_at
```

Project keys:

```text
BACK -> Backend Platform
FRONT -> Frontend Platform
DATA -> Data Platform
TOOLS -> Internal Tools
```

Приоритеты, совместимые с Plane:

```text
none
low
medium
high
urgent
```

Связь с Plane:

```text
Plane id -> plane_work_item_id
Plane name -> title
Plane description_html -> description
Plane priority -> priority
Plane target_date -> deadline_days
Plane project -> plane_project_id
Plane labels -> required_stack / task_type / urgency hints
Plane estimate_point -> estimated_hours or estimate feature later
Plane state -> workflow state
```

Важное решение:

```text
Внутри COMPASS AI предпочитаем plane_work_item_id.
plane_issue_id оставляем как alias для совместимости с roadmap.
```

**Ожидаемый результат:** задачи можно генерировать системно, а не случайным хаосом.

**Примерное время:** 1 час.  
**Коммит:** `Define task schema`

---

## 7.4. Определить историю назначений

- [x] Описать, как будет выглядеть историческое назначение.
- [x] Каждое назначение — это пара `task_id + employee_id`.
- [x] Для каждой пары хранить результат выполнения.
- [x] Добавить признаки качества, скорости и просрочки.
- [x] Добавить целевую метку `success_label`.
- [x] Добавить признаки для будущего multi-output ML.
- [x] Добавить вероятностную формулу synthetic success.
- [x] Добавить overload penalty.
- [x] Добавить complexity gap penalty.

Поля истории:

```text
assignment_id
task_id
employee_id
plane_work_item_id
plane_issue_id
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
speed_score
collaboration_score
risk_score
success_label
```

Правила label:

```text
success_label = 1, если completed_on_time = true, quality_score >= 0.75, reopened_count <= 1, employee_workload_at_assignment <= 0.85
success_label = 0, если задача просрочена, quality_score < 0.6, reopened_count >= 3 или workload > 0.95
```

Формула вероятности успеха для synthetic data:

```text
success_probability =
  0.35 * skill_match_score
+ 0.20 * deadline_reliability
+ 0.15 * avg_quality_score
+ 0.10 * avg_completion_speed
+ 0.10 * collaboration_score
+ 0.10 * growth_match_score
- 0.25 * overload_penalty
- 0.15 * complexity_gap_penalty
```

Важное решение:

```text
success_label остаётся binary для MVP.
Дополнительные score-поля сохраняются заранее для будущего multi-output варианта модели:
speed_score
quality_score
learning_score
overload_risk
```

**Ожидаемый результат:** данные подходят для supervised learning.

**Примерное время:** 1–2 часа.  
**Коммит:** `Define assignment history schema`

---

# 8. Этап 6 — генератор синтетических данных

## 8.1. Создать конфиг генерации данных

- [x] Создать `config/synthetic_data.yaml`.
- [x] Указать seed генерации.
- [x] Указать количество сотрудников.
- [x] Указать количество задач.
- [x] Указать количество исторических назначений.
- [x] Указать диапазоны сложности.
- [x] Указать диапазоны загрузки.
- [x] Указать список ролей.
- [x] Указать список навыков.
- [x] Указать распределения грейдов.
- [x] Добавить output paths для CSV/JSON файлов.
- [x] Добавить реальные Plane project IDs из этапа 6.
- [x] Добавить веса проектов для генерации backlog.
- [x] Увеличить synthetic dataset до размера, подходящего для обучения ML-модели.
- [x] Добавить разные сценарии назначений.
- [x] Добавить разные типы исходов выполнения задач.
- [x] Настроить баланс хороших и плохих исходов для supervised learning.

Файл:

```text
config/synthetic_data.yaml
```

Дополнительная схема, на которую опирается генератор:

```text
config/synthetic_schema.yaml
```

Параметры:

```text
random_seed
employees_count
tasks_count
assignments_count
projects
role_grade_plan
task_types
scenario_weights
outcome_distribution
date_range_start
date_range_end
```

Фактические значения MVP были:

```text
employees_count: 18
tasks_count: 120
assignments_count: 650
```

Фактические значения после усиления training dataset:

```text
random_seed: 42
employees_count: 36
tasks_count: 2500
assignments_count: 60000
date_range_start: 2023-01-01
date_range_end: 2026-06-30
```

Файлы результата:

```text
data/synthetic/employees.csv
data/synthetic/employees.json
data/synthetic/tasks.csv
data/synthetic/tasks.json
data/synthetic/assignments.csv
data/synthetic/assignments.json
```

Важно:

```text
data/synthetic/*.csv и data/synthetic/*.json не коммитятся,
потому что они воспроизводимо генерируются одной командой.
```

Важно:

```text
Большой synthetic dataset нужен для обучения нейросети.
Его не нужно целиком загружать в Plane.
Plane использует отдельный demo backlog из этапа 9.
```

**Ожидаемый результат:** генератор данных настраивается без изменения кода.

**Фактический результат:** конфиг генерации расширен до ML-ready training dataset.

**Примерное время:** 1 час.  
**Коммит:** `Add synthetic data configuration`

Дополнительные коммиты:

```text
Scale synthetic training configuration
Expand synthetic data schema
Tune synthetic assignment scenario balance
```

---

## 8.2. Реализовать генерацию сотрудников

- [x] Создать `src/data/generate_employees.py`.
- [x] Сгенерировать `employee_id`.
- [x] Сгенерировать русские имена.
- [x] Сгенерировать роли.
- [x] Сгенерировать грейды.
- [x] Сгенерировать опыт.
- [x] Сгенерировать skills vector.
- [x] Сгенерировать текущую загрузку.
- [x] Сгенерировать среднюю скорость.
- [x] Сгенерировать среднее качество.
- [x] Сгенерировать reliability.
- [x] Сгенерировать learning goals.
- [x] Сохранить результат в `data/synthetic/employees.csv`.
- [x] Сохранить JSON-версию в `data/synthetic/employees.json`.
- [x] Добавить `active_tasks_count`.
- [x] Добавить `availability`.
- [x] Добавить `timezone`.
- [x] Оставить `plane_user_id` пустым до этапа mapping users.
- [x] Убрать hardcoded team на 18 сотрудников.
- [x] Читать `role_grade_plan` из `config/synthetic_data.yaml`.
- [x] Поддержать команду на 36 сотрудников.

Файл генератора:

```text
src/data/generate_employees.py
```

Файлы результата:

```text
data/synthetic/employees.csv
data/synthetic/employees.json
```

Команда запуска:

```bash
python src/data/generate_employees.py
```

Фактический размер команды после усиления dataset:

```text
36 сотрудников
```

Фактический состав команды:

```text
backend_developer: 14
frontend_developer: 9
qa_engineer: 4
data_ml_engineer: 4
devops_engineer: 3
team_lead: 2
```

Фактический состав по грейдам:

```text
middle: 15
senior: 10
junior: 9
lead: 2
```

Поля employees:

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
active_tasks_count
avg_completion_speed
avg_quality_score
deadline_reliability
learning_goals
mentor_level
availability
timezone
```

Фактическая средняя загрузка команды после усиления dataset:

```text
0.628
```

Важно:

```text
skills и learning_goals сохраняются как JSON-строки в CSV
и как нормальные JSON-значения в JSON export.
```

Важно по Plane:

```text
plane_user_id пока пустой,
потому что сопоставление synthetic employee -> Plane user хранится отдельно
в data/processed/employee_plane_mapping.csv.
```

**Ожидаемый результат:** есть синтетическая команда.

**Фактический результат:** генератор сотрудников масштабирован до 36 человек и больше не завязан на hardcoded 18 rows.

**Примерное время:** 3–5 часов.  
**Коммит:** `Generate synthetic employees`

Дополнительный коммит:

```text
Expand synthetic employee generation
```

---

## 8.3. Реализовать генерацию задач

- [x] Создать `src/data/generate_tasks.py`.
- [x] Сгенерировать задачи на русском языке.
- [x] Сгенерировать реалистичные заголовки.
- [x] Сгенерировать реалистичные описания.
- [x] Сгенерировать тип задачи.
- [x] Сгенерировать требуемый стек.
- [x] Сгенерировать требуемые навыки.
- [x] Сгенерировать сложность от 1 до 5.
- [x] Сгенерировать priority.
- [x] Сгенерировать business criticality.
- [x] Сгенерировать дедлайн в днях.
- [x] Сгенерировать estimated hours.
- [x] Сгенерировать dependencies count.
- [x] Сохранить результат в `data/synthetic/tasks.csv`.
- [x] Сохранить JSON-версию в `data/synthetic/tasks.json`.
- [x] Добавить `plane_work_item_id`.
- [x] Добавить `plane_issue_id`.
- [x] Добавить `plane_project_id`.
- [x] Добавить `project_key`.
- [x] Добавить `source`.
- [x] Добавить `created_at` и `updated_at`.
- [x] Увеличить количество задач до 2500.
- [x] Добавить дополнительную вариативность title/description через task contexts и business areas.

Файл генератора:

```text
src/data/generate_tasks.py
```

Файлы результата:

```text
data/synthetic/tasks.csv
data/synthetic/tasks.json
```

Команда запуска:

```bash
python src/data/generate_tasks.py
```

Фактическое количество задач после усиления dataset:

```text
2500
```

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

Фактическое распределение задач по типам после усиления dataset:

```text
analytics_report: 201
api_integration: 210
backend_feature: 213
bugfix: 214
database_migration: 186
devops_task: 206
documentation_task: 231
frontend_feature: 210
ml_pipeline: 216
refactoring: 201
security_task: 212
testing_task: 200
```

Фактическое распределение задач по проектам после усиления dataset:

```text
BACK: 1422
DATA: 416
FRONT: 258
TOOLS: 404
```

Поля tasks:

```text
task_id
plane_work_item_id
plane_issue_id
plane_project_id
project_key
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
source
created_at
updated_at
```

Важно:

```text
plane_work_item_id и plane_issue_id в большом training dataset остаются пустыми,
потому что этот dataset нужен для обучения модели, а не для массовой загрузки в Plane.
```

Важно:

```text
В Plane уже загружен отдельный demo backlog из 120 задач на этапе 9.
Повторно запускать plane/seed/create_tasks.py после увеличения tasks_count не нужно.
```

**Ожидаемый результат:** есть синтетический backlog задач.

**Фактический результат:** `tasks.csv` и `tasks.json` масштабированы до 2500 задач и стали разнообразнее.

**Примерное время:** 3–5 часов.  
**Коммит:** `Generate synthetic tasks`

Дополнительный коммит:

```text
Increase synthetic task diversity
```

---

## 8.4. Реализовать генерацию истории назначений

- [x] Создать `src/data/generate_assignments.py`.
- [x] Загружать сотрудников из `employees.csv`.
- [x] Загружать задачи из `tasks.csv`.
- [x] Для каждой исторической задачи выбирать сотрудника не полностью случайно, а с учётом навыков и загрузки.
- [x] Рассчитывать `skill_match_score`.
- [x] Рассчитывать `growth_match_score`.
- [x] Рассчитывать вероятность успешного выполнения.
- [x] Генерировать `completed_on_time`.
- [x] Генерировать `actual_hours`.
- [x] Генерировать `quality_score`.
- [x] Генерировать `reopened_count`.
- [x] Генерировать `manager_rating`.
- [x] Генерировать `success_label`.
- [x] Добавить `speed_score`.
- [x] Добавить `collaboration_score`.
- [x] Добавить `risk_score`.
- [x] Добавить защиту от дублей пары `task_id + employee_id`.
- [x] Сохранить результат в `data/synthetic/assignments.csv`.
- [x] Сохранить JSON-версию в `data/synthetic/assignments.json`.
- [x] Увеличить историю назначений до 60000 строк.
- [x] Добавить сценарии назначений.
- [x] Добавить разные исходы выполнения.
- [x] Добавить полностью не завершённые задачи.
- [x] Добавить delayed delivery.
- [x] Добавить failed delivery.
- [x] Добавить partial success.
- [x] Добавить `success_probability`.
- [x] Добавить `assignment_scenario`.
- [x] Добавить `outcome_status`.
- [x] Добавить `delay_days`.
- [x] Добавить `delivery_speed_category`.
- [x] Настроить outcome logic так, чтобы successful и failed assignments имели понятные различия по quality, risk и delay.

Файл генератора:

```text
src/data/generate_assignments.py
```

Файлы результата:

```text
data/synthetic/assignments.csv
data/synthetic/assignments.json
```

Команда запуска:

```bash
python src/data/generate_assignments.py
```

Фактическое количество исторических назначений после усиления dataset:

```text
60000
```

Поля assignments:

```text
assignment_id
task_id
employee_id
plane_work_item_id
plane_issue_id
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
speed_score
collaboration_score
risk_score
success_probability
assignment_scenario
outcome_status
delay_days
delivery_speed_category
success_label
```

Сценарии назначений:

```text
ideal_match
balanced_match
growth_stretch
overload_risk
wrong_role
urgent_deadline
random_assignment
```

Фактическое распределение сценариев после финальной настройки:

```text
balanced_match: 0.230217
growth_stretch: 0.169033
ideal_match: 0.233800
overload_risk: 0.089717
random_assignment: 0.051117
urgent_deadline: 0.089867
wrong_role: 0.136250
```

Типы исходов:

```text
full_success
partial_success
delayed_delivery
failed_delivery
cancelled_or_not_finished
```

Фактическое распределение исходов после финальной настройки:

```text
cancelled_or_not_finished: 0.061017
delayed_delivery: 0.160550
failed_delivery: 0.207450
full_success: 0.452367
partial_success: 0.118617
```

Фактическое распределение `success_label` после финальной настройки:

```text
0: 0.487983
1: 0.512017
```

Логика выбора исполнителя:

```text
ideal_match выбирает сильных подходящих кандидатов
balanced_match учитывает skill match и загрузку
growth_stretch создаёт задачи на развитие
overload_risk создаёт случаи перегруза
wrong_role создаёт плохие назначения по роли/скиллам
urgent_deadline создаёт срочные рискованные назначения
random_assignment добавляет шум и неожиданные пары
```

Логика success_label:

```text
success_label остаётся binary:
1 — успешный или допустимо успешный исход
0 — плохой, сорванный, сильно просроченный или не завершённый исход
```

Важно:

```text
Датасет содержит и хорошие, и плохие исходы почти в balanced-пропорции.
Это удобно для обучения binary classifier, потому что модель видит достаточно примеров обоих классов.
```

Проверка уникальности пар:

```bash
python -c "import pandas as pd; df=pd.read_csv('data/synthetic/assignments.csv'); print('duplicate task+employee pairs:', df.duplicated(['task_id','employee_id']).sum())"
```

Фактический результат:

```text
duplicate task+employee pairs: 0
```

Проверка различий между успешными и неуспешными назначениями:

```bash
python -c "import pandas as pd; df=pd.read_csv('data/synthetic/assignments.csv'); print(df.groupby('success_label')[['skill_match_score','risk_score','quality_score','employee_workload_at_assignment','delay_days']].mean())"
```

Фактический результат:

```text
success_label=0:
skill_match_score: 0.507875
risk_score: 0.435771
quality_score: 0.552405
employee_workload_at_assignment: 0.643700
delay_days: 14.615253

success_label=1:
skill_match_score: 0.640930
risk_score: 0.327116
quality_score: 0.842342
employee_workload_at_assignment: 0.606869
delay_days: 0.544448
```

**Ожидаемый результат:** есть обучающая история назначений.

**Фактический результат:** создан большой ML-ready assignment history dataset на 60000 строк с разными сценариями и исходами, без дублей `task_id + employee_id`.

**Примерное время:** 5–8 часов.  
**Коммит:** `Generate synthetic assignment history`

Дополнительные коммиты:

```text
Generate diverse assignment outcomes
Tune synthetic assignment outcome logic
```

---

## 8.5. Создать общий pipeline генерации данных

- [x] Создать `scripts/generate_synthetic_data.py`.
- [x] Скрипт должен запускать генерацию сотрудников.
- [x] Скрипт должен запускать генерацию задач.
- [x] Скрипт должен запускать генерацию истории назначений.
- [x] Скрипт должен проверять, что все CSV-файлы созданы.
- [x] Скрипт должен печатать краткую статистику.
- [x] Добавить команду в `Makefile`.
- [x] Проверить запуск через `python`.
- [x] Проверить запуск через `make generate-data`.
- [x] Добавить вывод outcome status distribution.
- [x] Добавить вывод assignment scenario distribution.
- [x] Добавить проверку дублей task+employee.
- [x] Добавить средний risk score.
- [x] Проверить финальный dataset на 36 сотрудников, 2500 задач и 60000 назначений.

Файл pipeline:

```text
scripts/generate_synthetic_data.py
```

Команда запуска:

```bash
python scripts/generate_synthetic_data.py
```

Команда через Makefile:

```bash
make generate-data
```

Фактическая статистика pipeline после усиления dataset:

```text
Employees: 36
Tasks: 2500
Assignments: 60000
```

Pipeline печатает:

```text
employees by role
employees by grade
tasks by type
tasks by project
success label distribution
outcome status distribution
assignment scenario distribution
duplicate task+employee pairs
average workload
average skill match
average risk score
```

Проверка размеров датасетов:

```bash
python -c "import pandas as pd; print('employees', len(pd.read_csv('data/synthetic/employees.csv'))); print('tasks', len(pd.read_csv('data/synthetic/tasks.csv'))); print('assignments', len(pd.read_csv('data/synthetic/assignments.csv')))"
```

Фактический результат:

```text
employees 36
tasks 2500
assignments 60000
```

Проверка качества кода:

```bash
python -m py_compile src/data/generate_employees.py src/data/generate_tasks.py src/data/generate_assignments.py scripts/generate_synthetic_data.py
```

```bash
ruff check src/data/generate_employees.py src/data/generate_tasks.py src/data/generate_assignments.py scripts/generate_synthetic_data.py
```

Ожидаемый результат:

```text
All checks passed!
```

**Ожидаемый результат:** все данные генерируются одной командой.

**Фактический результат:** общий pipeline генерации данных масштабирован и готовит большой датасет для ML-обучения.

**Примерное время:** 2–3 часа.  
**Коммит:** `Add synthetic data generation pipeline`

Дополнительные коммиты:

```text
Report synthetic dataset outcome statistics
Scale synthetic dataset for model training
```

---

# 9. Этап 7 — загрузка синтетических данных в Plane

## 9.1. Подготовить mapping между COMPASS AI и Plane

- [x] Создать `src/integration/plane_mapping.py`.
- [x] Определить, как поля COMPASS AI превращаются в поля Plane.
- [x] Сопоставить `task.title` с Plane issue title.
- [x] Сопоставить `task.description` с Plane issue description.
- [x] Сопоставить `priority` с Plane priority.
- [x] Сопоставить `required_stack` с labels.
- [x] Сопоставить `task_type` с labels.
- [x] Сопоставить `deadline_days` с target date.
- [x] Сопоставить `estimated_hours` с estimate, если поле доступно.
- [x] Сопоставить `employee_id` с `plane_user_id`.
- [x] Использовать современный термин Plane `work item` внутри кода.
- [x] Оставить `plane_issue_id` как compatibility alias для roadmap.
- [x] Добавить преобразование synthetic task в Plane work item payload.
- [x] Добавить HTML-описание задачи с metadata COMPASS AI.
- [x] Добавить marker `COMPASS task_id` в `description_html` для защиты от дублей.
- [x] Добавить mapping task type → labels.
- [x] Добавить mapping required stack → labels.
- [x] Добавить нормализацию Plane priority.
- [x] Добавить расчёт `target_date` из `deadline_days`.
- [x] Добавить получение `plane_project_id` из synthetic task.
- [x] Расширить `PlaneClient` методами для seeding.
- [x] Добавить обработку Plane API rate limits.
- [x] Исправить trailing slash для work items endpoint после `301 Moved Permanently`.

Файл:

```text
src/integration/plane_mapping.py
```

Дополнительно доработан файл:

```text
src/integration/plane_client.py
```

Добавленные методы `PlaneClient`:

```text
create_label(project_id, name, color)
create_work_item(project_id, name, description_html, priority, labels, target_date)
create_issue(project_id, name, description_html, priority, labels, target_date)
```

Основные mapping-функции:

```text
parse_json_cell(value, default)
normalize_priority(priority)
normalize_label_name(label)
labels_for_task(task)
target_date_from_deadline(deadline_days)
task_description_html(task)
task_to_plane_work_item_payload(task, label_name_to_id)
task_project_id(task)
compass_task_marker(task_id)
```

Фактический mapping COMPASS AI → Plane:

```text
task_id -> marker COMPASS task_id в description_html
title -> name
description -> description_html
priority -> priority
required_stack -> labels
task_type -> labels
deadline_days -> target_date
estimated_hours -> metadata внутри description_html
plane_project_id -> project_id в Plane API path
plane_work_item_id -> основной ID задачи Plane после seed
plane_issue_id -> alias, равный plane_work_item_id
```

Фактические label mapping решения:

```text
backend_feature -> backend, feature
frontend_feature -> frontend, feature
bugfix -> bug
refactoring -> refactoring
database_migration -> backend, data
api_integration -> backend, feature
ml_pipeline -> ml, data
analytics_report -> data
devops_task -> devops
testing_task -> testing
security_task -> security
documentation_task -> documentation
```

Фактические stack label mapping решения:

```text
Python -> python
FastAPI -> fastapi
Django -> django
PostgreSQL -> postgresql
Redis -> redis
Docker -> docker
Kubernetes -> kubernetes
React -> react
TypeScript -> typescript
Next.js -> nextjs
HTML/CSS -> html-css
PyTorch -> pytorch
```

Важное решение:

```text
Внутри кода используем Plane work items.
Термин issue оставлен только как совместимость с roadmap и будущими API endpoint aliases.
```

Важное решение:

```text
estimated_hours пока не пишется в отдельное Plane estimate field,
потому что estimate_point в локальном Plane не был включён и не проверялся как write field.
Значение estimated_hours сохраняется в description_html как metadata.
```

Важное решение:

```text
description_html содержит marker COMPASS task_id.
Этот marker используется seed-скриптом, чтобы повторный запуск не создавал дубли задач.
```

Выяснено по Plane API:

```text
Plane требует trailing slash на work-items endpoint.
Без trailing slash API возвращает 301 Moved Permanently.
```

Фактическая исправленная форма endpoint:

```text
POST /api/v1/workspaces/{workspace_slug}/projects/{project_id}/work-items/
```

Выяснено по Plane API:

```text
Plane может возвращать 429 RATE_LIMIT_EXCEEDED при массовом создании labels/tasks.
```

Фактическое решение:

```text
PlaneClient доработан: при 429 делает retry с паузой.
Seed-скрипты запускаются безопаснее, но массовые операции всё равно могут занимать время.
```

Проверки:

```bash
python -m py_compile src/integration/plane_client.py
```

```bash
ruff check src/integration/plane_client.py
```

```bash
python -m py_compile src/integration/plane_mapping.py
```

```bash
ruff check src/integration/plane_mapping.py
```

Фактический результат проверок:

```text
All checks passed!
```

**Ожидаемый результат:** понятно, какие данные можно реально положить в Plane.

**Фактический результат:** mapping слой создан, PlaneClient расширен для seeding, rate limits обработаны, work-items endpoint исправлен.

**Примерное время:** 2–3 часа.  
**Коммит:** `Map COMPASS data to Plane fields`

Дополнительные коммиты:

```text
Extend Plane client for seeding
Handle Plane API rate limits
```

---

## 9.2. Создать seed-скрипт для Plane labels

- [x] Создать `plane/seed/create_labels.py`.
- [x] Скрипт должен создать labels для технологий.
- [x] Скрипт должен создать labels для типов задач.
- [x] Скрипт должен не создавать дубликаты.
- [x] Скрипт должен печатать список созданных labels.
- [x] Создать labels во всех 4 проектах Plane.
- [x] Проверять существующие labels перед созданием.
- [x] Повторный запуск должен быть безопасным.
- [x] Добавить throttling/retry из-за Plane API rate limits.
- [x] Проверить результат через `scripts/check_plane_connection.py`.

Файл:

```text
plane/seed/create_labels.py
```

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

Фактически добавленный расширенный набор labels:

```text
backend
frontend
ml
data
devops
bug
feature
refactoring
urgent
growth-task
python
fastapi
django
postgresql
redis
docker
kubernetes
react
typescript
nextjs
html-css
pytorch
testing
security
documentation
```

Команда:

```bash
python plane/seed/create_labels.py
```

Фактический результат после успешного запуска:

```text
Backend Platform: 25 labels
Frontend Platform: 25 labels
Data Platform: 25 labels
Internal Tools: 25 labels
```

Проверочная команда:

```bash
python scripts/check_plane_connection.py
```

Фактический проверенный вывод по labels:

```text
Project: Backend Platform (BACK)
  Labels: 25

Project: Frontend Platform (FRONT)
  Labels: 25

Project: Data Platform (DATA)
  Labels: 25

Project: Internal Tools (TOOLS)
  Labels: 25
```

Что было выяснено:

```text
При первом запуске Plane вернул 429 RATE_LIMIT_EXCEEDED.
Часть labels уже успела создаться до ошибки.
После retry/throttling повторный запуск корректно определил existing labels и дозаполнил недостающие.
```

Фактическая идемпотентность:

```text
Повторный запуск показывает action exists для уже созданных labels.
Новые labels создаются только там, где их ещё нет.
```

Важное решение:

```text
Labels создаются на уровне каждого project.
Workspace-level labels не используются, потому что в текущем локальном Plane UI они не применялись.
```

Проверки:

```bash
python -m py_compile plane/seed/create_labels.py
```

```bash
ruff check plane/seed/create_labels.py
```

Фактический результат проверок:

```text
All checks passed!
```

**Ожидаемый результат:** в Plane есть labels, которые нужны для задач.

**Фактический результат:** labels seeding реализован, проверен, все 4 проекта имеют по 25 labels.

**Примерное время:** 2–4 часа.  
**Коммит:** `Add Plane labels seeding`

Дополнительный коммит:

```text
Throttle Plane label seeding
```

---

## 9.3. Создать seed-скрипт для Plane задач

- [x] Создать `plane/seed/create_tasks.py`.
- [x] Скрипт должен читать `data/synthetic/tasks.csv`.
- [x] Скрипт должен создавать задачи в нужном проекте Plane.
- [x] Скрипт должен добавлять labels.
- [x] Скрипт должен добавлять priority.
- [x] Скрипт должен добавлять target date, если поле доступно.
- [x] Скрипт должен сохранить mapping `task_id → plane_issue_id`.
- [x] Mapping сохранить в `data/processed/task_plane_mapping.csv`.
- [x] Использовать `plane_work_item_id` как основной ID.
- [x] Записывать `plane_issue_id` как alias, равный `plane_work_item_id`.
- [x] Сначала проверить seed на `limit=5`.
- [x] После проверки запустить полный seed на 120 задач.
- [x] Добавить защиту от дублей через marker `COMPASS task_id`.
- [x] Повторный запуск должен распознавать уже созданные задачи как `exists`.
- [x] Учесть Plane API rate limits при массовом создании.
- [x] Проверить итоговое количество задач в Plane.

Файл:

```text
plane/seed/create_tasks.py
```

Команда:

```bash
python plane/seed/create_tasks.py
```

Результат:

```text
data/processed/task_plane_mapping.csv
```

Поля mapping:

```text
task_id
plane_work_item_id
plane_issue_id
plane_project_id
project_key
title
action
```

Фактический тестовый запуск:

```text
Сначала создано 5 задач.
mapping сохранился в data/processed/task_plane_mapping.csv.
Plane UI и checker подтвердили появление задач.
```

Фактический результат тестового запуска:

```text
TASK-0001 -> Backend Platform
TASK-0002 -> Data Platform
TASK-0003 -> Backend Platform
TASK-0004 -> Frontend Platform
TASK-0005 -> Backend Platform
```

Фактический полный запуск:

```text
created: 115
exists: 5
total mapping rows: 120
```

Что это значит:

```text
Первые 5 задач были созданы на тестовом запуске.
При полном запуске скрипт не создал их повторно, а распознал как exists.
Остальные 115 задач были созданы.
```

Фактическое итоговое количество work items в Plane:

```text
Backend Platform: 57 work items
Frontend Platform: 19 work items
Data Platform: 26 work items
Internal Tools: 19 work items
```

Пояснение:

```text
Backend Platform содержит 57 work items, потому что там уже была 1 тестовая задача из раннего Plane setup
и 56 synthetic tasks из generated backlog.
```

Проверочная команда:

```bash
python scripts/check_plane_connection.py
```

Фактический проверенный вывод:

```text
Project: Backend Platform (BACK)
  Work items: 57
  States: 5
  Labels: 25

Project: Frontend Platform (FRONT)
  Work items: 19
  States: 5
  Labels: 25

Project: Data Platform (DATA)
  Work items: 26
  States: 5
  Labels: 25

Project: Internal Tools (TOOLS)
  Work items: 19
  States: 5
  Labels: 25
```

Что было выяснено:

```text
Plane может возвращать 429 при массовом создании задач.
PlaneClient retry обработал эти ситуации, поэтому seed завершился успешно.
```

Что было исправлено:

```text
Первый запуск create_tasks получил 301 Moved Permanently из-за отсутствия trailing slash.
Endpoint create_work_item исправлен на /work-items/.
```

Важное решение:

```text
data/processed/task_plane_mapping.csv не коммитится,
потому что содержит локальные Plane IDs и является локальным воспроизводимым артефактом.
```

Проверки:

```bash
python -m py_compile plane/seed/create_tasks.py
```

```bash
ruff check plane/seed/create_tasks.py
```

Фактический результат проверок:

```text
All checks passed!
```

**Ожидаемый результат:** в Plane появляется синтетический backlog.

**Фактический результат:** в Plane загружены все 120 synthetic tasks, mapping сохранён локально, повторный запуск защищён от дублей.

**Примерное время:** 4–8 часов.  
**Коммит:** `Seed Plane with synthetic tasks`

---

## 9.4. Создать seed-скрипт для пользователей Plane

- [x] Проверить, можно ли создавать пользователей через API.
- [x] Если можно, создать синтетических пользователей автоматически.
- [x] Если нельзя, создать пользователей вручную в UI.
- [x] После создания пользователей выгрузить их IDs.
- [x] Сопоставить `employee_id` с `plane_user_id`.
- [x] Сохранить mapping в `data/processed/employee_plane_mapping.csv`.
- [x] Создать `plane/seed/create_employee_mapping.py`.
- [x] Прочитать synthetic employees из `data/synthetic/employees.csv`.
- [x] Попробовать получить Plane project members через `PlaneClient.list_project_members(project_id)`.
- [x] Автоматически сопоставить найденных Plane members с employees, если members доступны.
- [x] Для отсутствующих Plane users оставить `manual_required`.
- [x] Не создавать пользователей автоматически без стабильного проверенного Plane invite/user API flow.

Файл скрипта:

```text
plane/seed/create_employee_mapping.py
```

Файл результата:

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
grade
mapping_status
```

Команда:

```bash
python plane/seed/create_employee_mapping.py
```

Фактический результат:

```text
auto_matched: 1
manual_required: 17
```

Автоматически найденный Plane user:

```text
EMP-001 -> e12805b3-4184-468c-bb7f-a8a11b5efdf6 -> admin@compass.local
```

Фактический mapping status:

```text
EMP-001 auto_matched
EMP-002 manual_required
EMP-003 manual_required
EMP-004 manual_required
EMP-005 manual_required
EMP-006 manual_required
EMP-007 manual_required
EMP-008 manual_required
EMP-009 manual_required
EMP-010 manual_required
EMP-011 manual_required
EMP-012 manual_required
EMP-013 manual_required
EMP-014 manual_required
EMP-015 manual_required
EMP-016 manual_required
EMP-017 manual_required
EMP-018 manual_required
```

Что было выяснено:

```text
Сейчас в Plane project members фактически доступен только admin user.
Поэтому полноценное employee -> Plane user mapping требует ручного создания дополнительных Plane users
или отдельного invite/user flow позже.
```

Важное решение:

```text
Автоматическое создание пользователей Plane не делаем на этом этапе.
Это безопаснее, потому что user creation/invite flow в self-hosted Plane может отличаться от project API.
```

Важное решение:

```text
Для учебного MVP достаточно вручную создать 5–8 пользователей в Plane UI
и заполнить data/processed/employee_plane_mapping.csv.
```

Важное решение по git:

```text
data/processed/employee_plane_mapping.csv не коммитится,
потому что содержит локальные Plane user IDs и email.
```

Проверки:

```bash
python -m py_compile plane/seed/create_employee_mapping.py
```

```bash
ruff check plane/seed/create_employee_mapping.py
```

Фактический результат проверок:

```text
All checks passed!
```

**Важно:** если Plane self-hosted не даёт удобно создавать пользователей через API, это не критично. Для учебного проекта можно вручную создать 5–8 пользователей и сопоставить их с синтетическими сотрудниками.

**Ожидаемый результат:** COMPASS AI знает, как связать своего сотрудника с пользователем Plane.

**Фактический результат:** employee mapping script создан, mapping file подготовлен, 1 пользователь сопоставлен автоматически, остальные требуют ручного заполнения после создания пользователей в Plane.

**Примерное время:** 2–5 часов.  
**Коммит:** `Map synthetic employees to Plane users`

---

# 10. Этап 8 — базовый backend COMPASS AI

## 10.1. Создать FastAPI-приложение

- [x] Создать `app/api.py`.
- [x] Создать endpoint `/health`.
- [x] Создать endpoint `/version`.
- [x] Создать endpoint `/recommendations/demo`.
- [x] Создать endpoint `/recommendations/issue/{issue_id}`.
- [x] Создать endpoint `/reports/summary`.
- [x] Подключить CORS для локального dashboard.
- [x] Подключить чтение `.env`.
- [x] Добавить запуск через `uvicorn`.
- [x] Проверить запуск через `make api`.
- [x] Проверить запуск напрямую через `uvicorn`.
- [x] Добавить placeholder endpoint для будущей Plane/agentic интеграции.
- [x] Добавить summary endpoint по synthetic dataset.

Файл:

```text
app/api.py
```

Команда запуска напрямую:

```bash
uvicorn app.api:app --reload --host 0.0.0.0 --port 8000
```

Команда запуска через Makefile:

```bash
make api
```

Фактически проверенный Makefile target:

```text
api:
     uvicorn app.api:app --reload --host 0.0.0.0 --port 8000
```

Фактические endpoints:

```text
GET /health
GET /version
GET /reports/summary
GET /recommendations/demo
GET /recommendations/issue/{issue_id}
```

Проверка `/health`:

```bash
curl http://localhost:8000/health
```

Фактический response:

```json
{"status":"ok","service":"compass-ai"}
```

Проверка `/version`:

```bash
curl http://localhost:8000/version
```

Фактический response:

```json
{"service":"compass-ai","version":"0.1.0","environment":"local"}
```

Проверка `/reports/summary`:

```bash
curl http://localhost:8000/reports/summary
```

Фактический response содержит:

```text
employees_count
tasks_count
assignments_count
average_workload
average_skill_match
average_risk_score
success_rate
failed_rate
tasks_by_project
tasks_by_type
assignments_by_outcome
assignments_by_scenario
```

Фактическая статистика synthetic dataset через API:

```text
employees_count: 36
tasks_count: 2500
assignments_count: 60000
average_workload: 0.628
average_skill_match: 0.576
average_risk_score: 0.38
success_rate: 0.512
failed_rate: 0.488
```

Фактическое распределение задач по проектам через API:

```text
BACK: 1422
DATA: 416
FRONT: 258
TOOLS: 404
```

Фактическое распределение assignment outcomes через API:

```text
cancelled_or_not_finished: 3661
delayed_delivery: 9633
failed_delivery: 12447
full_success: 27142
partial_success: 7117
```

Фактическое распределение assignment scenarios через API:

```text
balanced_match: 13813
growth_stretch: 10142
ideal_match: 14028
overload_risk: 5383
random_assignment: 3067
urgent_deadline: 5392
wrong_role: 8175
```

Важно:

```text
/recommendations/issue/{issue_id} пока является placeholder endpoint.
Реальная интеграция с Plane и agentic pipeline будет подключена позже на этапах 15–16.
```

Фактическая проверка запуска:

```text
Uvicorn успешно запустил FastAPI backend на http://0.0.0.0:8000.
Endpoints /health, /version и /reports/summary вернули HTTP 200 OK.
```

Проверка качества кода:

```bash
python -m py_compile app/api.py
```

```bash
ruff check app/api.py
```

Фактический результат:

```text
All checks passed!
```

**Ожидаемый результат:** локальный backend COMPASS AI работает.

**Фактический результат:** FastAPI-приложение создано, health/version/reports endpoints работают, placeholder для Plane issue recommendation подготовлен.

**Примерное время:** 3–5 часов.  
**Коммит:** `Add COMPASS FastAPI service`

---

## 10.2. Создать Pydantic-схемы API

- [x] Создать `src/models/schemas.py`.
- [x] Описать `TaskInput`.
- [x] Описать `EmployeeInput`.
- [x] Описать `RecommendationRequest`.
- [x] Описать `CandidateRecommendation`.
- [x] Описать `RecommendationResponse`.
- [x] Описать `ExplanationResponse`.
- [x] Описать `AnalyticsSummary`.
- [x] Описать `HealthResponse`.
- [x] Описать `VersionResponse`.
- [x] Добавить `RecommendationMode`.

Файл:

```text
src/models/schemas.py
```

Основные структуры:

```text
HealthResponse
VersionResponse
TaskInput
EmployeeInput
RecommendationRequest
CandidateRecommendation
RecommendationResponse
ExplanationResponse
AnalyticsSummary
```

Поддерживаемые recommendation modes:

```text
fast_delivery
balanced_workload
growth
risk_minimization
```

Важно:

```text
Эти схемы используются FastAPI endpoints и будут переиспользованы позже
в agentic pipeline, inference wrapper и dashboard.
```

Важно:

```text
Pydantic-схемы заранее учитывают Plane compatibility:
plane_work_item_id
plane_issue_id
plane_project_id
project_key
```

Проверка качества кода:

```bash
python -m py_compile src/models/schemas.py
```

```bash
ruff check src/models/schemas.py
```

Фактический результат:

```text
All checks passed!
```

**Ожидаемый результат:** API возвращает строго структурированные данные.

**Фактический результат:** Pydantic-схемы API созданы и используются FastAPI endpoints.

**Примерное время:** 2–3 часа.  
**Коммит:** `Add API data schemas`

---

## 10.3. Добавить demo endpoint без ML

- [x] Endpoint `/recommendations/demo` берёт тестовую задачу из `tasks.csv`.
- [x] Endpoint берёт список сотрудников из `employees.csv`.
- [x] Endpoint возвращает top-3 по простому rule-based правилу.
- [x] Пока не использует нейросеть.
- [x] Возвращает JSON с кандидатом, score, reasons и risks.
- [x] Поддерживает query parameter `mode`.
- [x] Поддерживает query parameter `task_id`.
- [x] Поддерживает query parameter `top_k`.
- [x] Проверяется через браузер или curl.
- [x] Проверен режим `balanced_workload`.
- [x] Проверен режим `fast_delivery`.
- [x] Проверена рекомендация для конкретной synthetic task `TASK-0001`.

Файл demo-ranker:

```text
src/recommendation/demo_ranker.py
```

FastAPI endpoint:

```text
GET /recommendations/demo
```

Команда проверки default demo recommendation:

```bash
curl http://localhost:8000/recommendations/demo
```

Фактический default response:

```text
task_id: TASK-0022
mode: balanced_workload
source: rule_based_demo
top candidates: 3
```

Фактический top-3 для default demo recommendation:

```text
1. EMP-011 — Полина Васильева — backend_developer senior — score 0.8186
2. EMP-027 — Валерия Фомина — qa_engineer senior — score 0.785
3. EMP-010 — Сергей Павлов — backend_developer middle — score 0.7725
```

Команда проверки режима `fast_delivery`:

```bash
curl "http://localhost:8000/recommendations/demo?mode=fast_delivery"
```

Фактический top-3 для `fast_delivery`:

```text
1. EMP-011 — Полина Васильева — backend_developer senior — score 0.8579
2. EMP-027 — Валерия Фомина — qa_engineer senior — score 0.7888
3. EMP-014 — Никита Егоров — backend_developer senior — score 0.7769
```

Команда проверки конкретной synthetic task:

```bash
curl "http://localhost:8000/recommendations/demo?task_id=TASK-0001&mode=balanced_workload"
```

Фактическая задача:

```text
TASK-0001
Добавить endpoint для статистики команды — интеграции с Plane
```

Фактический top-3 для `TASK-0001`:

```text
1. EMP-011 — Полина Васильева — backend_developer senior — score 0.8804
2. EMP-010 — Сергей Павлов — backend_developer middle — score 0.8456
3. EMP-014 — Никита Егоров — backend_developer senior — score 0.819
```

Фактическая логика demo scoring:

```text
skill_match
role_affinity
workload_score
speed
quality
deadline_reliability
growth_match
```

Фактические режимы demo scoring:

```text
fast_delivery
balanced_workload
growth
risk_minimization
```

Фактический response содержит:

```text
task_id
plane_work_item_id
plane_issue_id
title
mode
candidates
rank
employee_id
plane_user_id
name
role
grade
score
reasons
risks
factors
source
explanation
```

Важно:

```text
Это лёгкий demo-ranker, а не финальный rule-based baseline.
Полный rule-based baseline будет реализован на этапе 11.
Нейросеть будет подключена позже после feature engineering и обучения модели.
```

Важно:

```text
LLM на этом этапе не используется.
Demo endpoint возвращает только структурированную рекомендацию и техническое объяснение.
Русскоязычные LLM-объяснения будут добавлены позже в agentic pipeline.
```

Фактическая проверка запуска:

```text
/recommendations/demo вернул HTTP 200 OK.
/recommendations/demo?mode=fast_delivery вернул HTTP 200 OK.
/recommendations/demo?task_id=TASK-0001&mode=balanced_workload вернул HTTP 200 OK.
```

Проверка качества кода:

```bash
python -m py_compile app/api.py src/recommendation/demo_ranker.py
```

```bash
ruff check app/api.py src/recommendation/demo_ranker.py
```

Фактический результат:

```text
All checks passed!
```

**Ожидаемый результат:** до ML уже есть end-to-end форма ответа.

**Фактический результат:** `/recommendations/demo` возвращает структурированный top-k response с score, reasons, risks и factors.

**Примерное время:** 2–4 часа.  
**Коммит:** `Add demo recommendation endpoint`

---

## 10.4. Финальная проверка backend API

- [x] Проверить компиляцию всех файлов этапа 10.
- [x] Проверить lint всех файлов этапа 10.
- [x] Проверить запуск FastAPI через `uvicorn`.
- [x] Проверить `/health`.
- [x] Проверить `/version`.
- [x] Проверить `/reports/summary`.
- [x] Проверить `/recommendations/demo`.
- [x] Проверить `/recommendations/demo?mode=fast_delivery`.
- [x] Проверить `/recommendations/demo?task_id=TASK-0001&mode=balanced_workload`.

Проверка компиляции:

```bash
python -m py_compile src/models/schemas.py src/recommendation/demo_ranker.py app/api.py
```

Проверка линтера:

```bash
ruff check src/models/schemas.py src/recommendation/demo_ranker.py app/api.py
```

Фактический результат:

```text
All checks passed!
```

Фактический результат этапа:

```text
COMPASS AI backend запускается локально.
API возвращает health/version/status.
API читает большой synthetic dataset.
API отдаёт summary по данным.
API отдаёт demo top-3 рекомендацию без ML.
API уже использует Pydantic response schemas.
```

Важно:

```text
Этап 10 не обучает модель и не использует нейросеть.
Этап 10 нужен, чтобы заранее получить рабочую backend-обвязку,
к которой позже подключатся rule-based baseline, feature engineering,
TaskEmployeeMatchingNet, agents, LLM explanation и Plane write-back.
```

**Ожидаемый результат:** базовый backend готов для следующих этапов.

**Фактический результат:** этап 10 завершён и проверен.

**Коммиты этапа:**

```text
Add API data schemas
Add COMPASS FastAPI service
Add demo recommendation endpoint
```

---

# 11. Этап 9 — базовые эвристики до нейронной сети

## 11.1. Реализовать skill matching

- [x] Создать `src/recommendation/skill_matching.py`.
- [x] Реализовать расчёт совпадения навыков задачи и сотрудника.
- [x] Учитывать required skills.
- [x] Учитывать stack.
- [x] Учитывать уровень владения навыком.
- [x] Вернуть score от 0 до 1.
- [x] Написать тесты.
- [x] Добавить нормализацию названий навыков.
- [x] Добавить безопасный парсинг JSON-полей из CSV.
- [x] Добавить обработку `dict`, `list`, JSON-string, пустых значений и `NaN`.
- [x] Добавить определение matched skills.
- [x] Добавить определение missing skills.
- [x] Добавить определение weak skills.
- [x] Добавить fallback: если `required_skills` пустой, использовать `required_stack`.
- [x] Добавить dataclass-результат `SkillMatchResult`.

Файл:

```text
src/recommendation/skill_matching.py
```

Тест:

```text
tests/test_skill_matching.py
```

Основная структура результата:

```text
SkillMatchResult
```

Поля `SkillMatchResult`:

```text
score
matched_skills
missing_skills
weak_skills
required_skills_count
average_required_level
```

Основные функции:

```text
normalize_skill_name(skill)
normalize_stack_name(stack_item)
parse_employee_skills(employee)
parse_required_skills(task)
parse_required_stack(task)
skill_level(employee, skill_name)
calculate_skill_match(task, employee)
skill_match_score(task, employee)
```

Фактическая логика `skill_match`:

```text
1. Берём skills сотрудника.
2. Берём required_skills задачи.
3. Если required_skills нет, используем required_stack как список навыков с дефолтным уровнем 3.
4. Для каждого required skill сравниваем employee_level / required_level.
5. Ограничиваем вклад каждого навыка диапазоном 0–1.
6. Считаем среднее значение по required skills.
7. Добавляем небольшой stack bonus, если стек задачи совпадает со skills сотрудника.
8. Возвращаем итоговый score от 0 до 1.
```

Правила интерпретации:

```text
score ближе к 1.0 -> сотрудник технически хорошо подходит
score около 0.5 -> частичное совпадение
score ближе к 0.0 -> сотрудник технически плохо подходит
```

Что считается matched skill:

```text
employee_level / required_level >= 0.85
```

Что считается weak skill:

```text
0 < employee_level / required_level < 0.85
```

Что считается missing skill:

```text
employee_level отсутствует или равен 0
```

Важно:

```text
Названия навыков нормализуются:
Python -> python
FastAPI -> fastapi
HTML/CSS -> html/css
```

Важно:

```text
Модуль работает с данными из CSV, где skills и required_skills хранятся как JSON-строки.
Поэтому внутри есть безопасный JSON parser.
```

Важно:

```text
skill_matching.py не зависит от pandas.
Это обычный Python-модуль, который можно использовать и в API, и в agents, и в feature engineering.
```

Проверки:

```bash
python -m py_compile src/recommendation/skill_matching.py tests/test_skill_matching.py
```

```bash
ruff check src/recommendation/skill_matching.py tests/test_skill_matching.py
```

```bash
pytest tests/test_skill_matching.py
```

Фактически проверено тестами:

```text
парсинг employee skills из JSON-строки
парсинг required skills из list
высокий score для сильного кандидата
поиск missing skills
возврат score в диапазоне 0–1
```

**Ожидаемый результат:** можно понять, насколько сотрудник технически подходит к задаче.

**Фактический результат:** реализован независимый skill matching модуль с explainable output: score, matched skills, weak skills и missing skills.

**Примерное время:** 3–5 часов.  
**Коммит:** `Add skill matching baseline`

---

## 11.2. Реализовать workload scoring

- [x] Создать `src/recommendation/workload_scoring.py`.
- [x] Реализовать penalty за высокую загрузку.
- [x] Нормализовать загрузку от 0 до 1.
- [x] Считать загрузку выше 0.85 рискованной.
- [x] Считать загрузку выше 0.95 критической.
- [x] Написать тесты.
- [x] Добавить поддержку workload в формате `0.75`.
- [x] Добавить поддержку workload в формате `75`.
- [x] Учесть `active_tasks_count`.
- [x] Учесть `availability`.
- [x] Добавить risk level: `low`, `medium`, `high`, `critical`.
- [x] Добавить reasons для объяснения penalty.
- [x] Добавить dataclass-результат `WorkloadScoreResult`.

Файл:

```text
src/recommendation/workload_scoring.py
```

Тест:

```text
tests/test_workload_scoring.py
```

Основная структура результата:

```text
WorkloadScoreResult
```

Поля `WorkloadScoreResult`:

```text
score
workload
active_tasks_count
availability
risk_level
reasons
```

Основные функции:

```text
normalize_workload(value)
workload_risk_level(workload)
calculate_workload_score(employee)
workload_score(employee)
workload_penalty(employee)
```

Фактическая логика `workload_score`:

```text
1. Берём current_workload сотрудника.
2. Нормализуем его к диапазону 0–1.
3. Базовый score считается как 1 - workload.
4. Если workload >= 0.70, применяем medium penalty.
5. Если workload >= 0.85, применяем high penalty.
6. Если workload >= 0.95, применяем critical penalty.
7. Дополнительно штрафуем за большое количество активных задач.
8. Дополнительно штрафуем за ограниченную availability.
9. Возвращаем итоговый score от 0 до 1.
```

Risk levels:

```text
low: workload < 0.70
medium: workload >= 0.70
high: workload >= 0.85
critical: workload >= 0.95
```

Интерпретация:

```text
score ближе к 1.0 -> у сотрудника есть свободная capacity
score ближе к 0.0 -> сотрудник перегружен
```

Важно:

```text
workload_score нужен, чтобы система не рекомендовала автоматически самого сильного специалиста,
если он уже перегружен.
```

Важно:

```text
workload_penalty = 1 - workload_score
```

Важно:

```text
Этот модуль тоже не зависит от pandas и может использоваться в API, agents, feature engineering и ML baseline.
```

Проверки:

```bash
python -m py_compile src/recommendation/workload_scoring.py tests/test_workload_scoring.py
```

```bash
ruff check src/recommendation/workload_scoring.py tests/test_workload_scoring.py
```

```bash
pytest tests/test_workload_scoring.py
```

Фактически проверено тестами:

```text
нормализация workload из fraction
нормализация workload из percent
высокий score при низкой загрузке
низкий score при высокой загрузке
critical risk при workload >= 0.95
workload_score и workload_penalty дополняют друг друга до 1.0
```

**Ожидаемый результат:** система не рекомендует автоматически самого сильного, если он перегружен.

**Фактический результат:** реализован workload scoring модуль с risk levels, penalty logic и explainable reasons.

**Примерное время:** 2–3 часа.  
**Коммит:** `Add workload scoring baseline`

---

## 11.3. Реализовать growth scoring

- [x] Создать `src/recommendation/growth_scoring.py`.
- [x] Сравнивать required skills задачи с learning goals сотрудника.
- [x] Повышать score, если задача подходит для развития.
- [x] Понижать score, если задача слишком сложная для текущего уровня.
- [x] Добавить параметр `mentor_available`.
- [x] Написать тесты.
- [x] Добавить парсинг `learning_goals` из JSON-строки.
- [x] Добавить нормализацию learning goals.
- [x] Добавить complexity fit по grade.
- [x] Добавить mentor bonus.
- [x] Добавить reasons.
- [x] Добавить risks.
- [x] Добавить dataclass-результат `GrowthScoreResult`.

Файл:

```text
src/recommendation/growth_scoring.py
```

Тест:

```text
tests/test_growth_scoring.py
```

Основная структура результата:

```text
GrowthScoreResult
```

Поля `GrowthScoreResult`:

```text
score
matched_learning_goals
complexity_fit
mentor_available
reasons
risks
```

Основные функции:

```text
parse_learning_goals(employee)
complexity_fit_score(task, employee)
calculate_growth_score(task, employee, mentor_available=False)
growth_score(task, employee, mentor_available=False)
```

Фактическая логика `growth_score`:

```text
1. Берём learning_goals сотрудника.
2. Берём required_skills задачи.
3. Считаем, какие learning_goals совпали с required_skills.
4. Считаем goal_match_score.
5. Считаем complexity_fit по grade сотрудника и complexity задачи.
6. Добавляем mentor bonus, если mentor_available=True.
7. Возвращаем итоговый score от 0 до 1.
```

Grade complexity limits:

```text
junior: безопасно до complexity 2
middle: безопасно до complexity 4
senior: безопасно до complexity 5
lead: безопасно до complexity 5
```

Интерпретация:

```text
score ближе к 1.0 -> задача хорошо подходит для развития сотрудника
score около 0.5 -> задача может быть stretch-задачей
score ближе к 0.0 -> задача плохо подходит как growth opportunity
```

Что считается growth fit:

```text
required_skills задачи пересекаются с learning_goals сотрудника
и complexity не слишком выше безопасного уровня для grade
```

Важно:

```text
growth_score нужен, чтобы COMPASS AI мог рекомендовать задачи не только самому сильному,
но и тому, кому задача полезна для развития.
```

Важно:

```text
mentor_available может поднять score для stretch-задачи,
потому что наличие ментора снижает риск.
```

Важно:

```text
Если задача слишком сложная для grade и mentor unavailable,
модуль возвращает risk: task may be too complex for current grade.
```

Проверки:

```bash
python -m py_compile src/recommendation/growth_scoring.py tests/test_growth_scoring.py
```

```bash
ruff check src/recommendation/growth_scoring.py tests/test_growth_scoring.py
```

```bash
pytest tests/test_growth_scoring.py
```

Фактически проверено тестами:

```text
парсинг learning_goals из JSON-строки
высокий score при совпадении learning_goals и required_skills
penalty за слишком сложную задачу для junior
mentor_available повышает growth score
score всегда в диапазоне 0–1
```

**Ожидаемый результат:** система может рекомендовать не только “самого быстрого”, но и “кому полезно дать задачу”.

**Фактический результат:** реализован growth scoring модуль с learning goals matching, complexity fit, mentor bonus, reasons и risks.

**Примерное время:** 3–5 часов.  
**Коммит:** `Add growth scoring baseline`

---

## 11.4. Собрать rule-based baseline

- [x] Создать `src/recommendation/rule_based_ranker.py`.
- [x] Объединить skill score.
- [x] Объединить workload score.
- [x] Объединить growth score.
- [x] Добавить speed score.
- [x] Добавить quality score.
- [x] Реализовать режимы: `fast_delivery`, `balanced_workload`, `growth`, `risk_minimization`.
- [x] Возвращать top-3 кандидатов.
- [x] Написать тесты.
- [x] Добавить role affinity.
- [x] Добавить mode-specific weights.
- [x] Добавить dataclass `RuleBasedCandidate`.
- [x] Добавить dataclass `RuleBasedRecommendation`.
- [x] Добавить conversion результата в JSON-serializable dict.
- [x] Добавить запуск baseline как standalone script.
- [x] Добавить загрузку synthetic employees/tasks из CSV.
- [x] Добавить поддержку `task_id`.
- [x] Добавить поддержку `top_k`.

Файл:

```text
src/recommendation/rule_based_ranker.py
```

Тест:

```text
tests/test_rule_based_ranker.py
```

Основные структуры:

```text
RuleBasedCandidate
RuleBasedRecommendation
```

Поля `RuleBasedCandidate`:

```text
rank
employee_id
plane_user_id
name
role
grade
score
reasons
risks
factors
```

Поля `RuleBasedRecommendation`:

```text
task_id
plane_work_item_id
plane_issue_id
title
mode
candidates
source
explanation
```

Основные функции:

```text
role_affinity_score(task, employee)
score_employee_for_task(task, employee, mode, mentor_available=False)
rank_employees_for_task(task, employees, mode, top_k, mentor_available=False)
load_synthetic_data(employees_path, tasks_path)
recommend_for_synthetic_task(task_id=None, mode="balanced_workload", top_k=3)
recommendation_to_dict(recommendation)
```

Фактическая логика rule-based baseline:

```text
1. Берём одну задачу.
2. Берём список сотрудников.
3. Для каждого сотрудника считаем:
   - skill_match
   - workload_score
   - growth_match
   - speed
   - quality
   - deadline_reliability
   - role_affinity
4. В зависимости от recommendation mode используем разные веса.
5. Считаем итоговый score.
6. Сортируем сотрудников по score.
7. Возвращаем top-k кандидатов.
```

Факторы, которые учитывает baseline:

```text
skill_match
workload_score
growth_match
speed
quality
deadline_reliability
role_affinity
```

Поддерживаемые режимы:

```text
fast_delivery
balanced_workload
growth
risk_minimization
```

Фактические mode weights:

```text
fast_delivery:
  skill: 0.30
  workload: 0.10
  growth: 0.05
  speed: 0.25
  quality: 0.15
  reliability: 0.15

balanced_workload:
  skill: 0.30
  workload: 0.25
  growth: 0.10
  speed: 0.10
  quality: 0.15
  reliability: 0.10

growth:
  skill: 0.25
  workload: 0.15
  growth: 0.30
  speed: 0.05
  quality: 0.15
  reliability: 0.10

risk_minimization:
  skill: 0.30
  workload: 0.20
  growth: 0.05
  speed: 0.10
  quality: 0.20
  reliability: 0.15
```

Как отличаются режимы:

```text
fast_delivery больше ценит speed и deadline_reliability
balanced_workload сильнее учитывает workload_score
growth сильнее учитывает growth_match
risk_minimization сильнее учитывает quality и deadline_reliability
```

Role affinity:

```text
role_affinity повышает score, если роль сотрудника подходит типу задачи.
Например:
backend_feature -> backend_developer, team_lead
frontend_feature -> frontend_developer
ml_pipeline -> data_ml_engineer
devops_task -> devops_engineer, backend_developer
testing_task -> qa_engineer, backend_developer, frontend_developer
```

Важно:

```text
role_affinity не является отдельным главным score,
но влияет на итоговую оценку как multiplier.
```

Важно:

```text
rule_based_ranker.py — это полноценный baseline для сравнения с будущей нейросетью.
Это не временный demo endpoint из этапа 10.
```

Важно:

```text
Нейросеть на этом этапе не используется.
Baseline нужен, чтобы потом доказать, что TaskEmployeeMatchingNet лучше простых правил.
```

Проверка standalone запуска:

```bash
python src/recommendation/rule_based_ranker.py
```

Ожидаемый результат:

```text
JSON с task_id, title, mode, source и top-3 candidates
```

Проверки:

```bash
python -m py_compile src/recommendation/rule_based_ranker.py tests/test_rule_based_ranker.py
```

```bash
ruff check src/recommendation/rule_based_ranker.py tests/test_rule_based_ranker.py
```

```bash
pytest tests/test_rule_based_ranker.py
```

Фактически проверено тестами:

```text
role_affinity высокий для подходящей роли
role_affinity штрафует неподходящую роль
score_employee_for_task возвращает кандидата со score
rank_employees_for_task возвращает top-3
top-3 отсортирован по score
перегруженный сотрудник получает penalty
recommendation_to_dict возвращает serializable dict
```

**Ожидаемый результат:** есть baseline, с которым потом сравнивается нейросеть.

**Фактический результат:** собран полноценный rule-based recommendation baseline с 4 режимами, role affinity, explainable factors, reasons, risks и top-k ranking.

**Примерное время:** 5–8 часов.  
**Коммит:** `Add rule based recommendation baseline`

---

## 11.5. Финальная проверка baseline

- [x] Проверить компиляцию всех baseline-модулей.
- [x] Проверить `ruff`.
- [x] Проверить unit tests.
- [x] Проверить запуск rule-based baseline на synthetic dataset.
- [x] Убедиться, что baseline возвращает top-3 кандидатов.
- [x] Убедиться, что scoring учитывает skill match, workload, growth, speed, quality и deadline reliability.
- [x] Убедиться, что baseline не использует нейросеть.
- [x] Убедиться, что baseline не зависит от Plane API.
- [x] Убедиться, что baseline можно запускать локально на `data/synthetic/*.csv`.

Фактические baseline-модули:

```text
src/recommendation/skill_matching.py
src/recommendation/workload_scoring.py
src/recommendation/growth_scoring.py
src/recommendation/rule_based_ranker.py
```

Фактические тесты:

```text
tests/test_skill_matching.py
tests/test_workload_scoring.py
tests/test_growth_scoring.py
tests/test_rule_based_ranker.py
```

Команда проверки компиляции:

```bash
python -m py_compile src/recommendation/skill_matching.py src/recommendation/workload_scoring.py src/recommendation/growth_scoring.py src/recommendation/rule_based_ranker.py
```

Команда проверки линтера:

```bash
ruff check src/recommendation/skill_matching.py src/recommendation/workload_scoring.py src/recommendation/growth_scoring.py src/recommendation/rule_based_ranker.py
```

Команда запуска тестов:

```bash
pytest tests/test_skill_matching.py tests/test_workload_scoring.py tests/test_growth_scoring.py tests/test_rule_based_ranker.py
```

Команда проверки baseline на synthetic dataset:

```bash
python src/recommendation/rule_based_ranker.py
```

Ожидаемый результат:

```text
All checks passed!
```

Фактический результат этапа:

```text
Есть прозрачный rule-based baseline до нейросети.
Он возвращает top-3 кандидатов и объяснимые факторы:
skill_match
workload_score
growth_match
speed
quality
deadline_reliability
role_affinity
```

Важно:

```text
Этот baseline нужен не вместо нейросети, а для сравнения с TaskEmployeeMatchingNet.
Позже ML-модель должна показать качество выше random baseline и rule-based baseline.
```

Важно:

```text
Baseline не пишет ничего в Plane.
Baseline только считает рекомендации локально по synthetic data.
Запись рекомендаций обратно в Plane будет сделана позже через Plane Integration Agent и write-back этапы.
```

Важно:

```text
Baseline не использует LLM.
LLM будет использоваться позже только для объяснения уже готового ranking,
а не для выбора исполнителя.
```

Связь с будущими этапами:

```text
Этап 11 -> даёт explainable rule-based baseline.
Этап 12 -> построит ML features.
Этап 13 -> обучит TaskEmployeeMatchingNet.
Этап 13.6 -> сравнит ML-модель с random baseline и rule-based baseline.
Этап 15 -> подключит baseline/ML к agentic pipeline.
```

**Ожидаемый результат:** baseline стабильно работает и покрыт тестами.

**Фактический результат:** все baseline-модули реализованы, проверены линтером, покрыты unit tests и готовы для сравнения с будущей нейросетью.

**Коммит:** `Document recommendation baseline progress`


---

# 12. Этап 10 — feature engineering для нейронной сети

## 12.1. Реализовать skill vectors

- [x] Создать `src/features/skill_vectorizer.py`.
- [x] Определить фиксированный список навыков.
- [x] Превращать skills сотрудника в числовой вектор.
- [x] Превращать required skills задачи в числовой вектор.
- [x] Проверить одинаковую длину векторов.
- [x] Сохранить словарь навыков в `data/processed/skill_vocab.json`.
- [x] Добавить нормализацию названий навыков.
- [x] Добавить безопасный парсинг JSON-полей из CSV.
- [x] Поддержать skills в форматах `dict`, `list`, JSON-string, пустое значение и `NaN`.
- [x] Собирать skill vocabulary из `config/synthetic_schema.yaml`, `employees.csv` и `tasks.csv`.
- [x] Добавить автосоздание `skill_vocab.json`, если файл ещё не существует.
- [x] Проверить генерацию словаря на synthetic dataset.

Файл:

```text
src/features/skill_vectorizer.py
```

Результат:

```text
data/processed/skill_vocab.json
```

Фактический размер словаря навыков:

```text
40
```

Примеры навыков из словаря:

```text
api design
backend architecture
ci/cd
code review
communication
data analysis
data pipelines
devops operations
django
docker
```

Основные функции:

```text
build_skill_vocab()
save_skill_vocab()
load_skill_vocab()
vectorize_skills_cell()
employee_skill_vector()
task_required_skill_vector()
```

Как работает:

```text
1. Читает taxonomy из config/synthetic_schema.yaml.
2. Дополняет словарь навыками из data/synthetic/employees.csv.
3. Дополняет словарь required skills и required stack из data/synthetic/tasks.csv.
4. Нормализует названия навыков.
5. Сортирует список навыков, чтобы порядок был стабильным.
6. Сохраняет skill vocabulary в data/processed/skill_vocab.json.
7. Превращает skills сотрудника и required skills задачи в вектор одинаковой длины.
```

Формат вектора:

```text
одна позиция = один навык из skill_vocab
значение = уровень навыка / 5
диапазон значения = 0.0–1.0
```

Пример:

```text
Python level 5 -> 1.0
Python level 3 -> 0.6
нет навыка -> 0.0
```

Проверенные команды:

```bash
python src/features/skill_vectorizer.py
```

```bash
python -m py_compile src/features/skill_vectorizer.py
```

```bash
ruff check src/features/skill_vectorizer.py
```

Фактический результат проверки:

```text
Skill vocab saved: data/processed/skill_vocab.json
Skills count: 40
All checks passed!
```

**Ожидаемый результат:** навыки можно подавать в нейронную сеть.

**Примерное время:** 3–5 часов.  
**Коммит:** `Add skill vectorization`

---

## 12.2. Реализовать text embeddings для задач

- [x] Создать `src/features/text_embeddings.py`.
- [x] Подключить `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`.
- [x] Загружать модель локально.
- [x] Превращать `title + description` в embedding.
- [x] Проверить размерность 384.
- [x] Кешировать embeddings в `data/processed/task_text_embeddings.npy`.
- [x] Сделать fallback, если модель не скачалась.
- [x] Добавить metadata-файл для embeddings.
- [x] Добавить deterministic fallback embeddings размерности 384.
- [x] Проверить генерацию embeddings на 2500 задачах.
- [x] Проверить, что embeddings имеют форму `(2500, 384)`.

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

Metadata:

```text
data/processed/task_text_embeddings_meta.json
```

Команда проверки:

```bash
python src/features/text_embeddings.py
```

Фактический размер embeddings:

```text
(2500, 384)
```

Что подаётся в text encoder:

```text
title
description
task_type
required_stack
```

Как работает:

```text
1. Загружает data/synthetic/tasks.csv.
2. Для каждой задачи собирает текст из title, description, task_type и required_stack.
3. Загружает multilingual sentence-transformers модель.
4. Строит normalized embedding для каждой задачи.
5. Сохраняет матрицу embeddings в data/processed/task_text_embeddings.npy.
6. Сохраняет metadata в data/processed/task_text_embeddings_meta.json.
```

Fallback logic:

```text
Если sentence-transformers модель не загрузилась,
скрипт создаёт deterministic fallback embeddings размерности 384.
Fallback нужен только для устойчивости pipeline, не как финальная ML-замена модели.
```

Что было выяснено:

```text
sentence-transformers установлен.
Модель успешно скачалась с Hugging Face.
Размер model.safetensors около 471 MB.
HF Hub предупредил про unauthenticated requests, но загрузка прошла успешно.
```

Проверенные команды:

```bash
python src/features/text_embeddings.py
```

```bash
python -m py_compile src/features/text_embeddings.py
```

```bash
ruff check src/features/text_embeddings.py
```

Фактический результат проверки:

```text
Embeddings saved: data/processed/task_text_embeddings.npy
Metadata saved: data/processed/task_text_embeddings_meta.json
Shape: (2500, 384)
All checks passed!
```

**Ожидаемый результат:** русскоязычные описания задач превращаются в векторы.

**Примерное время:** 4–6 часов.  
**Коммит:** `Add multilingual task embeddings`

---

## 12.3. Реализовать numeric feature builder

- [x] Создать `src/features/build_features.py`.
- [x] Загружать employees, tasks, assignments.
- [x] Строить task numeric features.
- [x] Строить employee numeric features.
- [x] Строить pair features для каждой пары `task + employee`.
- [x] Добавить признаки разницы навыков.
- [x] Добавить признаки загрузки.
- [x] Добавить признаки опыта.
- [x] Добавить признаки дедлайна.
- [x] Добавить признаки бизнес-критичности.
- [x] Сохранять итоговый датасет в `data/processed/training_pairs.parquet`.
- [x] Подключить skill vectors из `skill_vectorizer.py`.
- [x] Подключить task text embeddings из `text_embeddings.py`.
- [x] Добавить one-hot признаки для task type.
- [x] Добавить one-hot признаки для project key.
- [x] Добавить one-hot признаки для role.
- [x] Добавить one-hot признаки для grade.
- [x] Добавить one-hot признаки для availability.
- [x] Добавить role affinity feature.
- [x] Добавить skill cosine feature.
- [x] Добавить mean/max skill gap.
- [x] Добавить overqualified ratio.
- [x] Добавить complexity gap.
- [x] Добавить deadline pressure.
- [x] Добавить workload pressure.
- [x] Сохранить feature metadata в `data/processed/feature_metadata.json`.

Файл:

```text
src/features/build_features.py
```

Результат:

```text
data/processed/training_pairs.parquet
```

Metadata:

```text
data/processed/feature_metadata.json
```

Команда:

```bash
python src/features/build_features.py
```

Фактический размер итогового датасета:

```text
60000 rows
483 columns
success_rate: 0.512
```

Фактическая структура features:

```text
task_feature_dim: 404
employee_feature_dim: 60
pair_feature_dim: 13
label_column: success_label
skill_vocab_size: 40
text_embedding_dim: 384
```

Task features включают:

```text
task complexity
task priority score
business criticality
deadline days
deadline pressure
estimated hours
dependencies count
is growth task
task type one-hot
project one-hot
384 text embedding columns
```

Employee features включают:

```text
experience years
current workload
active tasks count
avg completion speed
avg quality score
deadline reliability
mentor level
role one-hot
grade one-hot
availability one-hot
40 employee skill columns
```

Pair features включают:

```text
skill_match_score
growth_match_score
speed_score
collaboration_score
risk_score
skill_cosine
mean_skill_gap
max_skill_gap
overqualified_ratio
complexity_gap
deadline_pressure
workload_pressure
role_affinity
```

Как работает:

```text
1. Загружает employees.csv, tasks.csv и assignments.csv.
2. Загружает skill_vocab.json.
3. Загружает task_text_embeddings.npy.
4. Для каждой строки assignment находит связанную task и employee.
5. Строит task features.
6. Строит employee features.
7. Строит pair features.
8. Добавляет success_label как целевую метку.
9. Сохраняет ML-ready dataset в training_pairs.parquet.
10. Сохраняет список feature columns и размерности в feature_metadata.json.
```

Важно для будущей модели:

```text
TaskEmployeeMatchingNet будет получать три группы признаков:
task features
employee features
pair features
```

Проверенные команды:

```bash
python src/features/build_features.py
```

```bash
python -m py_compile src/features/build_features.py
```

```bash
ruff check src/features/build_features.py
```

Фактический результат проверки:

```text
Training features saved: data/processed/training_pairs.parquet
Feature metadata saved: data/processed/feature_metadata.json
Rows: 60000
Columns: 483
Success rate: 0.512
Task feature columns: 404
Employee feature columns: 60
Pair feature columns: 13
All checks passed!
```

**Ожидаемый результат:** создан датасет для обучения нейросети.

**Примерное время:** 6–10 часов.  
**Коммит:** `Build training features`

---

## 12.4. Разделить данные на train/validation/test

- [x] Создать `src/data/split_dataset.py`.
- [x] Использовать train/validation/test split.
- [x] Не допустить утечку данных, если одна и та же задача встречается в разных split.
- [x] Разделять лучше по `task_id`, а не по отдельным парам.
- [x] Сохранить `train.parquet`.
- [x] Сохранить `val.parquet`.
- [x] Сохранить `test.parquet`.
- [x] Использовать `GroupShuffleSplit`.
- [x] Добавить проверку пересечений `task_id` между split.
- [x] Сохранить metadata по split в `data/processed/split_metadata.json`.
- [x] Проверить количество строк, задач, сотрудников и success rate в каждом split.

Файлы:

```text
data/processed/train.parquet
data/processed/val.parquet
data/processed/test.parquet
```

Metadata:

```text
data/processed/split_metadata.json
```

Команда:

```bash
python src/data/split_dataset.py
```

Split strategy:

```text
group split by task_id
```

Фактические размеры split:

```text
train: 42042 rows, 1750 tasks, 36 employees, success_rate 0.512678
val: 9026 rows, 375 tasks, 36 employees, success_rate 0.508642
test: 8932 rows, 375 tasks, 36 employees, success_rate 0.512315
```

Фактическая проверка leakage:

```text
task_id overlap train/val: 0
task_id overlap train/test: 0
task_id overlap val/test: 0
```

Как работает:

```text
1. Загружает data/processed/training_pairs.parquet.
2. Делит данные не по отдельным строкам, а по task_id.
3. Сначала отделяет train.
4. Потом делит оставшуюся часть на validation и test.
5. Проверяет, что один task_id не встречается в разных split.
6. Сохраняет train.parquet, val.parquet и test.parquet.
7. Сохраняет split metadata.
```

Почему split по `task_id` важен:

```text
В assignments одна задача может встречаться с разными employee_id.
Если делить случайно по строкам, одна и та же задача может попасть и в train, и в test.
Это создаёт data leakage.
Поэтому split сделан группами по task_id.
```

Проверенные команды:

```bash
python src/data/split_dataset.py
```

```bash
python -m py_compile src/data/split_dataset.py
```

```bash
ruff check src/data/split_dataset.py
```

Фактический результат проверки:

```text
Train saved: data/processed/train.parquet
Val saved: data/processed/val.parquet
Test saved: data/processed/test.parquet
Split metadata saved: data/processed/split_metadata.json
All checks passed!
```

**Ожидаемый результат:** данные готовы к честному обучению и оценке.

**Примерное время:** 2–4 часа.  
**Коммит:** `Split training dataset`

---

## 12.5. Добавить команды feature engineering в Makefile

- [x] Добавить команду `skill-vocab`.
- [x] Добавить команду `text-embeddings`.
- [x] Добавить команду `build-features`.
- [x] Добавить команду `split-data`.
- [x] Проверить, что `make build-features` запускает полный feature pipeline.
- [x] Проверить, что `make split-data` создаёт train/val/test split.
- [x] Исправить ошибку `Makefile:1: *** missing separator. Stop.`.
- [x] Проверить Makefile после исправления.

Файл:

```text
Makefile
```

Добавленные команды:

```text
skill-vocab
text-embeddings
build-features
split-data
```

Команда полного feature pipeline:

```bash
make build-features
```

Что делает `make build-features`:

```text
1. python src/features/skill_vectorizer.py
2. python src/features/text_embeddings.py
3. python src/features/build_features.py
```

Команда split:

```bash
make split-data
```

Что делает `make split-data`:

```text
python src/data/split_dataset.py
```

Что было исправлено:

```text
При первом запуске make build-features была ошибка:
Makefile:1: *** missing separator. Stop.

После исправления Makefile команды make build-features и make split-data успешно отработали.
```

Фактический результат `make build-features`:

```text
skill_vocab.json создан
task_text_embeddings.npy создан
training_pairs.parquet создан
Rows: 60000
Columns: 483
Success rate: 0.512
```

Фактический результат `make split-data`:

```text
train.parquet: 42042 rows
val.parquet: 9026 rows
test.parquet: 8932 rows
```

**Коммит:** `Add feature engineering commands`

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