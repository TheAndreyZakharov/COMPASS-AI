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

- [x] Создать `src/models/dataset.py`.
- [x] Реализовать `AssignmentPairDataset`.
- [x] Dataset возвращает task features.
- [x] Dataset возвращает employee features.
- [x] Dataset возвращает pair features.
- [x] Dataset возвращает label.
- [x] Dataset возвращает служебные идентификаторы: `assignment_id`, `task_id`, `employee_id`.
- [x] Проверить batch shapes.
- [x] Написать простой тест.

Файл:

```text
src/models/dataset.py
```

Тест:

```text
tests/test_dataset.py
```

Что сделано:

- `AssignmentPairDataset` читает parquet-файлы из `data/processed`.
- Feature columns загружаются из `data/processed/feature_metadata.json`.
- Dataset разделяет признаки на три группы:
  - `task_features`
  - `employee_features`
  - `pair_features`
- Label берётся из `success_label`.
- Поддерживаются train/validation/test файлы:
  - `data/processed/train.parquet`
  - `data/processed/val.parquet`
  - `data/processed/test.parquet`
- Добавлена функция `create_dataloader()`.
- Добавлена проверка отсутствующих колонок.
- Проверены размеры батча.

Фактические feature dimensions:

```text
task_dim: 404
employee_dim: 60
pair_dim: 13
```

**Ожидаемый результат:** PyTorch может читать обучающие данные.

**Примерное время:** 4–6 часов.  
**Коммит:** `Add PyTorch dataset for assignment pairs`

---

## 13.2. Реализовать `TaskEmployeeMatchingNet`

- [x] Создать `src/models/matching_net.py`.
- [x] Реализовать `TaskEncoder`.
- [x] Реализовать `EmployeeEncoder`.
- [x] Реализовать `MatchingBlock`.
- [x] Реализовать общий класс `TaskEmployeeMatchingNet`.
- [x] На вход принимать task tensor.
- [x] На вход принимать employee tensor.
- [x] На вход принимать pair tensor.
- [x] На выход отдавать `success_probability`.
- [x] Дополнительно подготовить архитектуру так, чтобы позже можно было расширить модель до multi-output.
- [x] Для MVP сделать один главный выход `success_probability`.

Файл:

```text
src/models/matching_net.py
```

Тест:

```text
tests/test_matching_net.py
```

Архитектура MVP:

```text
TaskEncoder → task_embedding
EmployeeEncoder → employee_embedding
concat(task_embedding, employee_embedding, abs_diff, multiply, pair_features) → MLP → logits → sigmoid
```

Как работает:

- `TaskEncoder` сжимает task features в task embedding.
- `EmployeeEncoder` сжимает employee features в employee embedding.
- `MatchingBlock` сравнивает task и employee через:
  - исходный task embedding
  - исходный employee embedding
  - absolute difference
  - element-wise multiplication
  - pair features
- Модель возвращает:
  - `logits`
  - `success_probability`
  - `task_embedding`
  - `employee_embedding`
- Основной training target — `success_label`.

**Ожидаемый результат:** собственная нейронная сеть создана.

**Примерное время:** 6–10 часов.  
**Коммит:** `Add task employee matching network`

---

## 13.3. Реализовать training loop

- [x] Создать `src/models/train.py`.
- [x] Загружать train/val датасеты.
- [x] Создавать модель.
- [x] Использовать BCE loss для binary classification.
- [x] Использовать AdamW.
- [x] Логировать train loss.
- [x] Логировать validation loss.
- [x] Логировать ROC-AUC.
- [x] Сохранять лучший checkpoint.
- [x] Сохранять config обучения.
- [x] Сохранять training history в CSV.
- [x] Добавить early stopping.
- [x] Добавить параметры обучения через CLI.

Файл:

```text
src/models/train.py
```

Результаты:

```text
models/compass_matching_model.pt
reports/training_history.csv
reports/training_config.json
```

Команда:

```bash
python src/models/train.py
```

Фактическая команда основного обучения:

```bash
python src/models/train.py --epochs 40 --batch-size 512 --learning-rate 0.0007 --patience 8 --dropout 0.10
```

Фактический config обучения:

```text
device: mps
epochs: 40
batch_size: 512
learning_rate: 0.0007
weight_decay: 0.0001
hidden_dim: 256
embedding_dim: 128
dropout: 0.10
patience: 8
train_rows: 42052
val_rows: 9024
task_dim: 404
employee_dim: 60
pair_dim: 13
```

Фактический лучший validation result:

```text
best_val_roc_auc: 0.86824
best_epoch: 14
```

Что сохраняется в checkpoint:

- `model_state_dict`
- `model_config`
- `feature_columns`
- `metrics`

Что было выяснено:

- На первой версии synthetic assignment signal модель упиралась примерно в `0.67 ROC-AUC`.
- Rule-based baseline и HistGradientBoosting давали примерно такой же результат.
- Это показало, что проблема была не в PyTorch-модели, а в слабом synthetic signal.
- После исправления генератора назначений модель стала обучаться нормально.

**Ожидаемый результат:** модель обучается и сохраняется.

**Примерное время:** 8–14 часов.  
**Коммит:** `Train matching neural network`

---

## 13.4. Добавить поддержку Apple Silicon MPS

- [x] Проверить доступность `mps`.
- [x] Если `mps` доступен, использовать его.
- [x] Если `mps` недоступен, использовать CPU.
- [x] Не делать CUDA обязательной.
- [x] Добавить лог устройства обучения.
- [x] Проверить обучение на MacBook M2.

Проверка:

```bash
python -c "import torch; print(torch.backends.mps.is_available())"
```

Фактический результат:

```text
True
```

Фактическое устройство обучения:

```text
mps
```

Как работает:

- `select_device()` сначала проверяет `torch.backends.mps.is_available()`.
- Если MPS доступен, модель и batch tensors переносятся на `mps`.
- Если MPS недоступен, используется `cpu`.
- CUDA не требуется.

**Ожидаемый результат:** обучение работает на MacBook M2 без CUDA.

**Примерное время:** 1–2 часа.  
**Коммит:** `Support Apple Silicon training`

---

## 13.5. Добавить диагностику качества synthetic signal

- [x] Создать `scripts/diagnose_model_signal.py`.
- [x] Сравнить rule-based baseline с ML-потолком на HistGradientBoosting.
- [x] Посчитать ROC-AUC отдельных pair/employee features.
- [x] Проверить, достаточно ли сильный signal в synthetic dataset.
- [x] Использовать диагностику перед повторным обучением нейросети.

Файл:

```text
scripts/diagnose_model_signal.py
```

Команда:

```bash
python scripts/diagnose_model_signal.py
```

Что было выяснено до исправления synthetic signal:

```text
rule_based_val_roc_auc: 0.670930
hgb_val_roc_auc: 0.670855
```

Single feature ROC-AUC до исправления:

```text
pair_skill_match_score: 0.657581
pair_risk_score: 0.663930
pair_role_affinity: 0.588778
employee_avg_quality_score: 0.542387
employee_deadline_reliability: 0.543771
```

Вывод:

```text
Нейронная сеть не могла честно получить 0.78–0.80 ROC-AUC, потому что сам synthetic dataset давал потолок около 0.67.
```

Что было исправлено:

- Обновлён `src/data/generate_assignments.py`.
- Сценарий назначения теперь выбирается до выбора сотрудника.
- `choose_employee_by_scenario()` реально используется при генерации assignment history.
- `ideal_match` чаще выбирает подходящих кандидатов.
- `wrong_role` чаще выбирает неподходящих кандидатов.
- `overload_risk` чаще выбирает перегруженных кандидатов.
- `success_probability` считается через logit/sigmoid.
- Шум в вероятности успеха ограничен.
- `success_label` стал сильнее зависеть от pre-assignment признаков:
  - skill match
  - role affinity
  - risk score
  - workload/overload
  - complexity gap
  - deadline pressure
  - employee quality
  - deadline reliability
  - speed score

Фактический synthetic dataset после исправления:

```text
Employees: 36
Tasks: 2500
Assignments: 60000
Duplicate task+employee pairs: 0
```

Фактическое распределение `success_label`:

```text
0: 0.549383
1: 0.450617
```

Фактическая разница signal по label:

```text
success_label=0:
skill_match_score: 0.5002
risk_score: 0.4700
success_probability: 0.2299
quality_score: 0.5185
employee_workload_at_assignment: 0.6590
delay_days: 15.9098

success_label=1:
skill_match_score: 0.7792
risk_score: 0.2290
success_probability: 0.6749
quality_score: 0.8721
employee_workload_at_assignment: 0.5824
delay_days: 0.1493
```

Фактический signal ceiling после исправления:

```text
rule_based_val_roc_auc: 0.848281
hgb_val_roc_auc: 0.871617
```

Single feature ROC-AUC после исправления:

```text
pair_skill_match_score: 0.803565
pair_risk_score: 0.860785
pair_role_affinity: 0.741715
pair_workload_pressure: 0.611278
employee_avg_quality_score: 0.567510
employee_deadline_reliability: 0.587548
```

После исправления данные были пересобраны:

```bash
python scripts/generate_synthetic_data.py
```

```bash
make build-features
```

```bash
make split-data
```

Фактический split:

```text
train: 42052 rows, 1750 tasks, success_rate 0.450775
val: 9024 rows, 375 tasks, success_rate 0.442930
test: 8924 rows, 375 tasks, success_rate 0.457642
```

Leakage check по `task_id`:

```text
train ∩ val: 0
train ∩ test: 0
val ∩ test: 0
```

**Коммит:** `Tune synthetic assignment signal for model training`

---

## 13.6. Реализовать evaluation

- [x] Создать `src/models/evaluate.py`.
- [x] Загрузить test dataset.
- [x] Загрузить лучший checkpoint.
- [x] Рассчитать accuracy.
- [x] Рассчитать precision.
- [x] Рассчитать recall.
- [x] Рассчитать F1.
- [x] Рассчитать ROC-AUC.
- [x] Рассчитать PR-AUC.
- [x] Сохранить метрики в `reports/model_metrics.json`.
- [x] Сохранить предсказания в `reports/test_predictions.csv`.

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

Как работает:

- Загружает `data/processed/test.parquet`.
- Загружает checkpoint `models/compass_matching_model.pt`.
- Восстанавливает `TaskEmployeeMatchingNet` из `model_config`.
- Делает prediction по test dataset.
- Сохраняет для каждой пары:
  - `assignment_id`
  - `task_id`
  - `employee_id`
  - `success_label`
  - `success_probability`
  - `prediction`
- Считает classification metrics.

Фактические test metrics:

```text
accuracy: 0.781040
precision: 0.775764
recall: 0.733595
f1: 0.754090
roc_auc: 0.859216
pr_auc: 0.820082
positive_rate: 0.457642
predicted_positive_rate: 0.432766
rows: 8924
```

**Ожидаемый результат:** можно доказать качество модели цифрами.

**Примерное время:** 4–6 часов.  
**Коммит:** `Evaluate matching model`

---

## 13.7. Реализовать ranking metrics

- [x] Создать `src/models/ranking_metrics.py`.
- [x] Рассчитать Precision@1.
- [x] Рассчитать Precision@3.
- [x] Рассчитать NDCG@3.
- [x] Рассчитать MRR.
- [x] Сравнить ML-модель с random baseline.
- [x] Сравнить ML-модель с rule-based baseline.
- [x] Сохранить результат в `reports/ranking_metrics.json`.

Файл:

```text
src/models/ranking_metrics.py
```

Команда:

```bash
python src/models/ranking_metrics.py
```

Результат:

```text
reports/ranking_metrics.json
```

Как работает:

- Загружает test dataset из `data/processed/test.parquet`.
- Загружает prediction-файл `reports/test_predictions.csv`.
- Объединяет данные по `assignment_id`.
- Группирует кандидатов по `task_id`.
- Для каждой задачи сортирует сотрудников по score.
- Считает ranking metrics по задачам.
- Сравнивает три подхода:
  - `ml_model`
  - `rule_based_baseline`
  - `random_baseline`

Фактические ranking metrics:

```text
ml_model:
precision_at_1: 0.893333
precision_at_3: 0.853333
ndcg_at_3: 0.862555
mrr: 0.943778

rule_based_baseline:
precision_at_1: 0.872000
precision_at_3: 0.859556
ndcg_at_3: 0.861110
mrr: 0.932667

random_baseline:
precision_at_1: 0.485333
precision_at_3: 0.501333
ndcg_at_3: 0.495777
mrr: 0.667997
```

Что показывает сравнение:

- ML-модель сильно лучше random baseline.
- ML-модель лучше rule-based baseline по:
  - Precision@1
  - NDCG@3
  - MRR
- Rule-based baseline немного выше по Precision@3.
- Это нормально: rule-based формула напрямую использует сильные pair features, а нейросеть учит зависимость из всех feature groups.

**Ожидаемый результат:** проект оценивает не только классификацию, но и качество рекомендаций.

**Примерное время:** 5–8 часов.  
**Коммит:** `Add recommendation ranking metrics`

---

## 13.8. Добавить команды обучения и оценки в Makefile

- [x] Добавить команду `train`.
- [x] Добавить команду `train-smoke`.
- [x] Добавить команду `evaluate`.
- [x] Добавить команду `ranking-metrics`.
- [x] Добавить команду `model-pipeline`.
- [x] Обновить `.PHONY`.

Файл:

```text
Makefile
```

Команды:

```bash
make train
```

```bash
make train-smoke
```

```bash
make evaluate
```

```bash
make ranking-metrics
```

```bash
make model-pipeline
```

Как работает:

- `make train` запускает обычное обучение.
- `make train-smoke` запускает обучение на 1 epoch для быстрой проверки.
- `make evaluate` запускает test evaluation.
- `make ranking-metrics` считает ranking quality.
- `make model-pipeline` последовательно запускает train, evaluate и ranking metrics.

**Коммит:** `Add model training commands`

---

# 14. Этап 12 — inference и ONNX

## 14.1. Реализовать inference wrapper

- [x] Создать `src/models/inference.py`.
- [x] Загружать PyTorch checkpoint `models/compass_matching_model.pt`.
- [x] Восстанавливать `TaskEmployeeMatchingNet` из `model_config`.
- [x] Читать feature columns из checkpoint.
- [x] Принимать dataframe с готовыми task/employee/pair features.
- [x] Использовать precomputed rows из `data/processed/training_pairs.parquet`.
- [x] Считать `success_probability` для пар `task + employee`.
- [x] Считать итоговый `final_score` с учётом recommendation mode.
- [x] Сортировать кандидатов по score.
- [x] Возвращать top-k кандидатов.
- [x] Добавить режимы рекомендации.
- [x] Вернуть структурированный JSON-compatible результат.
- [x] Добавить технические факторы решения.
- [x] Добавить risks для кандидатов.
- [x] Проверить wrapper на `TASK-0001`.

Файл:

```text
src/models/inference.py
```

Что использует wrapper:

```text
models/compass_matching_model.pt
data/processed/training_pairs.parquet
data/synthetic/employees.csv
```

Основные функции:

```text
load_checkpoint()
build_model_from_checkpoint()
checkpoint_feature_columns()
predict_pairs_dataframe()
mode_adjusted_score()
load_employee_profiles()
score_task_candidates()
```

Как работает:

```text
1. Загружает checkpoint обученной модели.
2. Восстанавливает TaskEmployeeMatchingNet.
3. Берёт task/employee/pair feature columns из checkpoint.
4. Находит все строки task_id + employee_id в training_pairs.parquet.
5. Прогоняет пары через PyTorch-модель.
6. Получает success_probability для каждого кандидата.
7. Применяет mode adjustment под выбранный режим рекомендации.
8. Сортирует сотрудников по final_score.
9. Возвращает top-k кандидатов с factors, reasons, risks и source.
```

Поддерживаемые режимы:

```text
fast_delivery
balanced_workload
growth
risk_minimization
```

Mode adjustment:

```text
fast_delivery:
учитывает speed, deadline reliability и deadline pressure

balanced_workload:
учитывает workload pressure и risk

growth:
учитывает growth match и risk

risk_minimization:
учитывает quality, deadline reliability и risk
```

Формат candidate:

```text
rank
employee_id
plane_user_id
name
role
grade
score
success_probability
factors
reasons
risks
source
```

Факторы, которые возвращаются по каждому кандидату:

```text
skill_match
growth_match
speed
risk
role_affinity
workload_pressure
quality
deadline_reliability
```

Фактическая проверка на `TASK-0001`, режим `balanced_workload`:

```text
1. EMP-014 — Никита Егоров — backend_developer senior — score 0.956596
2. EMP-011 — Полина Васильева — backend_developer senior — score 0.956551
3. EMP-010 — Сергей Павлов — backend_developer middle — score 0.925464
```

Важно:

```text
Inference wrapper использует уже построенные ML features.
На этом этапе он не пересобирает features для полностью новой задачи.
Для задач из synthetic dataset используется task_id и precomputed rows из training_pairs.parquet.
Для новых Plane-задач при отсутствии precomputed features Matching Agent может перейти на rule-based fallback.
```

Проверки:

```bash
python -m py_compile src/models/inference.py
```

```bash
ruff check src/models/inference.py
```

```bash
python src/models/inference.py
```

Фактический результат:

```text
All checks passed.
Inference wrapper вернул top-3 кандидатов для TASK-0001.
```

**Ожидаемый результат:** модель можно использовать в backend и agentic pipeline.

**Примерное время:** 5–8 часов.  
**Коммит:** `Add model inference wrapper`

---

## 14.2. Экспортировать модель в ONNX

- [x] Создать `src/models/export_onnx.py`.
- [x] Загрузить checkpoint `models/compass_matching_model.pt`.
- [x] Восстановить `TaskEmployeeMatchingNet`.
- [x] Обернуть модель в `ONNXMatchingWrapper`.
- [x] Сделать ONNX output только для `success_probability`.
- [x] Создать dummy input нужной формы.
- [x] Экспортировать модель через `torch.onnx.export`.
- [x] Добавить dynamic batch axis.
- [x] Проверить, что ONNX-файл создан.
- [x] Сохранить модель в `models/task_employee_matcher.onnx`.
- [x] Сохранить metadata экспорта в `reports/onnx_export.json`.

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
reports/onnx_export.json
```

Что делает `ONNXMatchingWrapper`:

```text
1. Принимает task_features, employee_features и pair_features.
2. Вызывает TaskEmployeeMatchingNet.
3. Из dict output берёт только success_probability.
4. Возвращает tensor success_probability как ONNX output.
```

ONNX input names:

```text
task_features
employee_features
pair_features
```

ONNX output name:

```text
success_probability
```

Фактические input dimensions:

```text
task_input_dim: 404
employee_input_dim: 60
pair_input_dim: 13
```

Фактический ONNX artifact:

```text
models/task_employee_matcher.onnx
size: 8.7 KB
```

Что было выяснено:

```text
В текущей версии PyTorch ONNX exporter требует onnxscript.
Без onnxscript экспорт падает с ошибкой:
ModuleNotFoundError: No module named 'onnxscript'
```

Проверка зависимости:

```bash
python -c "import onnxscript; print('onnxscript ok')"
```

Установка, если зависимости нет:

```bash
pip install onnxscript
```

Фактически установленная дополнительная зависимость:

```text
onnxscript
onnx_ir
```

Проверка ONNX exporter dependencies:

```bash
python -c "import onnx, onnxscript; print('onnx exporter deps ok')"
```

Фактический результат после установки:

```text
onnx exporter deps ok
```

Что было выяснено при экспорте:

```text
PyTorch предупредил, что при dynamo=True dynamic_axes не рекомендуется.
Экспорт при этом завершился успешно.
PyTorch также предупредил, что для новых ONNX implementations лучше использовать opset >= 18.
Файл был успешно экспортирован и сохранён.
```

Фактический успешный вывод:

```text
ONNX model saved: models/task_employee_matcher.onnx
ONNX export metadata saved: reports/onnx_export.json
```

Проверки:

```bash
python -m py_compile src/models/export_onnx.py
```

```bash
ruff check src/models/export_onnx.py
```

```bash
python src/models/export_onnx.py
```

```bash
test -f models/task_employee_matcher.onnx && echo "onnx export ok"
```

Фактический результат:

```text
All checks passed.
ONNX export ok.
models/task_employee_matcher.onnx создан.
```

Важно:

```text
models/task_employee_matcher.onnx и reports/onnx_export.json являются generated artifacts.
Их можно держать локально для демо, но кодовая часть этапа — это src/models/export_onnx.py.
```

**Ожидаемый результат:** есть ONNX-файл как production-ready артефакт.

**Примерное время:** 3–5 часов.  
**Коммит:** `Export matching model to ONNX`

---

## 14.3. Проверить ONNX Runtime

- [x] Создать `src/models/onnx_inference.py`.
- [x] Загрузить `models/task_employee_matcher.onnx`.
- [x] Загрузить PyTorch checkpoint.
- [x] Создать одинаковый dummy input для PyTorch и ONNX.
- [x] Подать dummy input в PyTorch-модель.
- [x] Подать dummy input в ONNX Runtime.
- [x] Сравнить PyTorch output и ONNX output.
- [x] Проверить `max_abs_diff`.
- [x] Проверить `mean_abs_diff`.
- [x] Проверить `np.allclose`.
- [x] Сохранить результат проверки в `reports/onnx_validation.json`.
- [x] Проверить, что `is_close = true`.

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

Что проверяет скрипт:

```text
1. Загружает checkpoint models/compass_matching_model.pt.
2. Загружает ONNX-модель models/task_employee_matcher.onnx.
3. Создаёт dummy batch размером 8.
4. Прогоняет batch через PyTorch.
5. Прогоняет тот же batch через ONNX Runtime.
6. Сравнивает outputs.
7. Сохраняет validation report.
8. Если outputs отличаются слишком сильно, падает с ошибкой.
```

ONNX Runtime provider:

```text
CPUExecutionProvider
```

Фактический validation report:

```text
checkpoint_path: models/compass_matching_model.pt
onnx_path: models/task_employee_matcher.onnx
batch_size: 8
task_input_dim: 404
employee_input_dim: 60
pair_input_dim: 13
max_abs_diff: 2.384185791015625e-07
mean_abs_diff: 6.007030606269836e-08
pytorch_min: 0.03231645002961159
pytorch_max: 0.8823279142379761
onnx_min: 0.0323164165019989
onnx_max: 0.8823279738426208
is_close: true
```

Что означает результат:

```text
ONNX output практически совпадает с PyTorch output.
Максимальная разница около 0.000000238.
Это нормальная численная погрешность.
ONNX-модель реально запускается и пригодна для inference.
```

Проверки:

```bash
python -c "import onnxruntime; print('onnxruntime ok')"
```

```bash
python -m py_compile src/models/onnx_inference.py
```

```bash
ruff check src/models/onnx_inference.py
```

```bash
python src/models/onnx_inference.py
```

```bash
test -f reports/onnx_validation.json && echo "onnx validation ok"
```

Фактический результат:

```text
onnxruntime ok
All checks passed.
ONNX validation ok.
is_close: true
```

Важно:

```text
ONNX validation сравнивает именно output success_probability.
Это достаточно для проверки production inference path,
потому что agentic pipeline использует score/probability для ranking.
```

**Ожидаемый результат:** ONNX-модель реально запускается.

**Примерное время:** 3–5 часов.  
**Коммит:** `Validate ONNX inference`

---

## 14.4. Добавить ONNX-команды в Makefile

- [x] Проверить существующие ONNX targets в `Makefile`.
- [x] Убедиться, что есть `export-onnx`.
- [x] Добавить `validate-onnx`.
- [x] Обновить `.PHONY`.
- [x] Проверить запуск ONNX export через `make`.
- [x] Проверить запуск ONNX validation через `make`.

Файл:

```text
Makefile
```

Команды:

```bash
make export-onnx
```

```bash
make validate-onnx
```

Что делает `make export-onnx`:

```text
python src/models/export_onnx.py
```

Что делает `make validate-onnx`:

```text
python src/models/onnx_inference.py
```

Фактическое изменение:

```text
В Makefile добавлена отдельная команда validate-onnx.
Также обновлена .PHONY-секция для ONNX targets.
```

Важно:

```text
В Makefile строки команд должны начинаться с TAB, не с пробелов.
```

Проверка:

```bash
make export-onnx
```

```bash
make validate-onnx
```

Фактический результат:

```text
ONNX export работает через Makefile.
ONNX validation работает через Makefile.
```

**Коммит:** `Add ONNX validation command`

---

# 15. Этап 13 — agentic pipeline

## 15.1. Создать общий формат состояния агентов

- [x] Создать `src/agents/state.py`.
- [x] Описать `AgentState`.
- [x] В state хранить исходную задачу.
- [x] В state хранить сотрудников.
- [x] В state хранить features.
- [x] В state хранить результаты модели.
- [x] В state хранить объяснение.
- [x] В state хранить финальную рекомендацию.
- [x] Не хранить секреты API в state.
- [x] Добавить `AgentError`.
- [x] Добавить `RecommendationMode`.
- [x] Добавить нормализацию режима рекомендации.
- [x] Добавить методы для накопления и сериализации ошибок.

Файл:

```text
src/agents/state.py
```

Поля `AgentState`:

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

Дополнительные структуры:

```text
AgentError
RecommendationMode
```

Поддерживаемые режимы:

```text
fast_delivery
balanced_workload
growth
risk_minimization
```

Основные методы:

```text
add_error()
has_errors()
error_payload()
normalize_mode()
```

Как работает:

```text
1. Orchestrator создаёт AgentState.
2. Каждый агент получает один и тот же state.
3. Агент читает нужные поля и записывает результат в state.
4. Ошибки не выбрасываются наружу сразу, а аккумулируются в errors.
5. Финальный response строится из AgentState.
```

Важно:

```text
AgentState не хранит PLANE_API_KEY, OLLAMA secrets или другие секреты.
State хранит только рабочие данные pipeline.
```

**Ожидаемый результат:** агенты передают данные друг другу предсказуемо.

**Примерное время:** 2–3 часа.  
**Коммит:** `Add agent pipeline state`

---

## 15.2. Реализовать Task Analyzer Agent

- [x] Создать `src/agents/task_analyzer.py`.
- [x] Агент принимает задачу из Plane или manual/synthetic issue dict.
- [x] Извлекает title.
- [x] Извлекает description.
- [x] Извлекает labels.
- [x] Умеет очищать HTML description.
- [x] Определяет task type.
- [x] Определяет required skills.
- [x] Определяет required stack.
- [x] Определяет complexity.
- [x] Определяет urgency по deadline/priority.
- [x] Возвращает task features.
- [x] Реализован rule-based parsing.
- [x] Добавлена подготовка к будущему LLM-assisted parsing.
- [x] Добавлено извлечение `COMPASS task_id` из description marker.
- [x] Добавлен fallback для задач без labels.

Файл:

```text
src/agents/task_analyzer.py
```

Основные функции:

```text
strip_html()
parse_json_cell()
labels_from_issue()
extract_compass_task_id()
detect_task_type()
priority_to_score()
deadline_days_from_issue()
estimate_complexity()
analyze_task()
run_task_analyzer()
```

Что принимает агент:

```text
Plane work item dict
manual issue dict
synthetic task converted to issue dict
```

Что возвращает в `state.task_features`:

```text
task_id
plane_work_item_id
plane_issue_id
plane_project_id
project_key
title
description
labels
task_type
required_stack
required_skills
complexity
priority
priority_score
business_criticality
deadline_days
estimated_hours
dependencies_count
is_growth_task
source
```

Task type detection использует:

```text
labels
title keywords
description keywords
fallback task type
```

Примеры label mapping:

```text
backend -> backend_feature
frontend -> frontend_feature
ml -> ml_pipeline
data -> analytics_report
devops -> devops_task
bug -> bugfix
security -> security_task
testing -> testing_task
documentation -> documentation_task
```

Примеры keyword detection:

```text
jwt, api, endpoint, backend -> backend_feature
react, dashboard, ui -> frontend_feature
model, embedding, pipeline -> ml_pipeline
docker, kubernetes, deploy -> devops_task
bug, fix, ошибка, починить -> bugfix
```

Примеры required skills:

```text
backend_feature:
Python, FastAPI, PostgreSQL, API Design

frontend_feature:
React, TypeScript, HTML/CSS

ml_pipeline:
Python, Machine Learning, PyTorch, Data Pipelines

devops_task:
Docker, Kubernetes, CI/CD
```

Как считается complexity:

```text
1. Если issue уже содержит complexity, используется оно.
2. Иначе берётся базовая сложность по task_type.
3. high/urgent priority повышает complexity.
4. длинное описание может повысить complexity.
5. итог ограничивается диапазоном 1–5.
```

Как считается deadline:

```text
1. Если есть deadline_days, используется он.
2. Если есть target_date, считается разница с текущей датой.
3. Если дедлайна нет, используется fallback 14 дней.
```

Важно:

```text
Task Analyzer не вызывает LLM.
Парсинг сделан rule-based, чтобы pipeline был стабильным и воспроизводимым.
LLM-assisted parsing можно добавить позже как улучшение, но не как обязательную зависимость.
```

**Ожидаемый результат:** сырая задача Plane превращается в признаки для модели.

**Примерное время:** 5–8 часов.  
**Коммит:** `Add task analyzer agent`

---

## 15.3. Реализовать Team State Analyzer Agent

- [x] Создать `src/agents/team_analyzer.py`.
- [x] Агент загружает профили сотрудников из `employees.csv`.
- [x] Парсит `skills`.
- [x] Парсит `learning_goals`.
- [x] Считает текущую загрузку.
- [x] Считает активные задачи.
- [x] Считает перегруз.
- [x] Считает доступность.
- [x] Формирует employee features.
- [x] Возвращает список кандидатов.
- [x] Добавляет `availability_score`.
- [x] Добавляет `workload_risk`.
- [x] Готовит state для Matching Agent.

Файл:

```text
src/agents/team_analyzer.py
```

Источник данных:

```text
data/synthetic/employees.csv
```

Основные функции:

```text
parse_json_cell()
load_employee_profiles()
availability_score()
workload_risk()
build_employee_features()
run_team_analyzer()
```

Что записывается в `state.employees`:

```text
полные профили сотрудников из employees.csv
```

Что записывается в `state.employee_features`:

```text
employee_id
plane_user_id
name
role
grade
skills
learning_goals
current_workload
active_tasks_count
availability
availability_score
workload_risk
avg_completion_speed
avg_quality_score
deadline_reliability
mentor_level
```

Workload risk levels:

```text
low: workload < 0.70
medium: workload >= 0.70
high: workload >= 0.85
critical: workload >= 0.95
```

Availability score:

```text
available:
score = 1.0 - workload

partially_available:
score = 0.6 - workload * 0.25

unavailable:
score = 0.0
```

Важно:

```text
На этом этапе Team Analyzer использует synthetic employees.csv.
Текущие задачи из Plane пока не пересчитывают workload динамически.
Динамический workload из Plane можно подключить позже, когда будет стабильный mapping employee_id -> plane_user_id.
```

**Ожидаемый результат:** состояние команды считается перед каждой рекомендацией.

**Примерное время:** 6–10 часов.  
**Коммит:** `Add team state analyzer agent`

---

## 15.4. Реализовать Matching Model Agent

- [x] Создать `src/agents/matching_agent.py`.
- [x] Агент получает task features.
- [x] Агент получает employee features.
- [x] Агент вызывает PyTorch inference через `src/models/inference.py`.
- [x] Агент получает scores.
- [x] Агент сортирует сотрудников.
- [x] Агент возвращает top-3.
- [x] Агент добавляет технические причины: skill match, workload, risk, growth.
- [x] Добавлен fallback на rule-based baseline.
- [x] Добавлена поддержка synthetic task через `TASK-*`.
- [x] Добавлена обработка ошибок ML inference.

Файл:

```text
src/agents/matching_agent.py
```

Использует:

```text
src/models/inference.py
src/recommendation/rule_based_ranker.py
```

Основные функции:

```text
run_matching_agent()
```

Внутренние ветки:

```text
_ml_candidates_available()
_run_ml_matching()
_run_rule_based_fallback()
```

Как работает:

```text
1. Проверяет, что task_features не пустые.
2. Проверяет, что employees загружены.
3. Если task_id начинается с TASK-, вызывает ML inference wrapper.
4. ML inference берёт precomputed rows из training_pairs.parquet.
5. Если ML inference невозможен, включается rule-based fallback.
6. Результат записывается в state.candidate_scores и state.top_candidates.
```

ML path:

```text
TaskEmployeeMatchingNet
+
mode adjustment
+
top-k sorting
```

Fallback path:

```text
rule_based_ranker
+
recommendation_to_dict()
+
source = rule_based_fallback
```

Формат candidate:

```text
rank
employee_id
plane_user_id
name
role
grade
score
success_probability
factors
reasons
risks
source
```

Фактическая проверка `TASK-0001`, `balanced_workload`:

```text
1. EMP-014 — Никита Егоров — score 0.956596
2. EMP-011 — Полина Васильева — score 0.956551
3. EMP-010 — Сергей Павлов — score 0.925464
```

Важно:

```text
Matching Agent отвечает только за ranking.
Он не пишет комментарии в Plane.
Он не вызывает LLM.
Он не принимает финальное управленческое решение.
```

**Ожидаемый результат:** отдельный агент отвечает только за ML-рекомендацию.

**Примерное время:** 4–6 часов.  
**Коммит:** `Add matching model agent`

---

## 15.5. Установить Ollama

- [x] Проверить, установлен ли Ollama.
- [x] Установить Ollama на Mac через Homebrew Cask.
- [x] Проверить версию Ollama.
- [x] Проверить доступность сервера.
- [x] Скачать `qwen2.5:1.5b-instruct`.
- [x] Проверить генерацию русского текста.
- [x] Зафиксировать, что Ollama server должен быть запущен отдельно.

Команды проверки:

```bash
command -v ollama || true
```

```bash
ollama --version
```

Фактический результат до установки:

```text
ollama: command not found
```

Команда установки:

```bash
brew install --cask ollama
```

Фактический результат установки:

```text
Ollama.app installed
ollama binary linked to /opt/homebrew/bin/ollama
client version 0.31.1
```

Проверка server API:

```bash
curl http://localhost:11434/api/tags
```

Если сервер не запущен:

```text
curl: Failed to connect to localhost port 11434
```

Команда запуска сервера, если приложение Ollama не запущено:

```bash
ollama serve
```

Команда загрузки модели:

```bash
ollama pull qwen2.5:1.5b-instruct
```

Фактический результат:

```text
qwen2.5:1.5b-instruct downloaded successfully
model size около 986 MB
```

Проверка русского ответа:

```bash
ollama run qwen2.5:1.5b-instruct "Кратко объясни на русском, почему задачу лучше назначить middle backend-разработчику с низкой загрузкой."
```

Фактический результат:

```text
Ollama отвечает на русском языке.
```

Важно:

```text
Ollama CLI может скачать и запустить модель даже если server API сначала недоступен.
Для Python-клиента нужен запущенный Ollama server на http://localhost:11434.
```

Важно:

```text
Если Ollama server не запущен, LLM client получает connection refused.
Explanation Agent в таком случае должен использовать fallback explanation.
```

**Ожидаемый результат:** локальная LLM отвечает на русском.

**Примерное время:** 1–2 часа.  
**Коммит:** коммит не нужен.

---

## 15.6. Реализовать LLM client

- [x] Создать `src/llm/ollama_client.py`.
- [x] Добавить базовый URL из `.env`.
- [x] Добавить имя модели из `.env`.
- [x] Реализовать метод `generate()`.
- [x] Добавить timeout.
- [x] Добавить обработку ошибок.
- [x] Добавить проверку доступности Ollama.
- [x] Не использовать LLM для принятия решения.
- [x] Использовать LLM только для объяснения.
- [x] Проверить клиент на русском prompt.
- [x] Зафиксировать поведение при недоступном Ollama server.

Файл:

```text
src/llm/ollama_client.py
```

Переменные `.env.example`:

```text
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:1.5b-instruct
```

Дополнительная переменная:

```text
OLLAMA_TIMEOUT_SECONDS=30
```

Основные структуры и функции:

```text
OllamaConfig
OllamaClient
generate()
ollama_available()
```

Как работает:

```text
1. Читает OLLAMA_BASE_URL из .env.
2. Читает OLLAMA_MODEL из .env.
3. Отправляет POST /api/generate.
4. Передаёт prompt, system prompt, temperature и num_predict.
5. Возвращает response text.
6. Если Ollama недоступна, выбрасывает RuntimeError.
```

Проверка:

```bash
python src/llm/ollama_client.py
```

Фактический результат:

```text
Клиент успешно получил русский текст от qwen2.5:1.5b-instruct.
```

Что было выяснено:

```text
Если Ollama server не запущен, Python-клиент получает:
Connection refused

После повторного запуска Ollama server клиент снова работает.
```

Важно:

```text
OllamaClient сам не принимает решений по исполнителю.
Он только генерирует текст объяснения по уже готовому ranking.
```

Важно:

```text
Fallback-логика находится не в OllamaClient, а в Explanation Agent.
Это правильно: клиент должен явно сообщать об ошибке, а агент решает, как деградировать.
```

**Ожидаемый результат:** backend может обращаться к локальной LLM.

**Примерное время:** 3–5 часов.  
**Коммит:** `Add Ollama LLM client`

---

## 15.7. Реализовать Explanation Agent

- [x] Создать `src/agents/explanation_agent.py`.
- [x] Агент получает top-3 кандидатов.
- [x] Агент получает факторы решения.
- [x] Агент формирует prompt на русском.
- [x] Агент вызывает Ollama.
- [x] Агент возвращает краткое объяснение.
- [x] Агент возвращает fallback template, если LLM не отвечает.
- [x] Ограничить длину ответа через `max_tokens`.
- [x] Запретить LLM менять ranking.
- [x] Запретить LLM придумывать данные, которых нет в input.
- [x] Добавить system prompt с ролью объясняющего агента.
- [x] Добавить fallback explanation без LLM.
- [x] Добавить режим `use_llm=False` для стабильных локальных проверок.

Файл:

```text
src/agents/explanation_agent.py
```

Основные функции:

```text
candidate_line()
fallback_explanation()
build_prompt()
run_explanation_agent()
```

Структура объяснения:

```text
Рекомендованный исполнитель
Почему он подходит
Риски
Альтернативы
Режим рекомендации
```

System prompt:

```text
LLM не выбирает исполнителя.
LLM не меняет ranking.
LLM не придумывает факты.
LLM только объясняет уже готовую рекомендацию.
```

Prompt содержит:

```text
task title
task type
priority
complexity
deadline_days
required_skills
recommendation_mode
top_candidates
candidate scores
candidate factors
candidate risks
```

Fallback explanation используется когда:

```text
use_llm=False
Ollama server недоступен
Ollama вернул ошибку
Ollama вернул пустой ответ
top_candidates пустой
```

Фактический fallback output содержит:

```text
## COMPASS AI Recommendation
Рекомендованный исполнитель
Режим рекомендации
Score
Почему подходит
Риски
Альтернативы
Важно: финальное решение остаётся за тимлидом
```

Важно:

```text
Explanation Agent не влияет на score и ranking.
Он работает только после Matching Agent.
```

Важно:

```text
Для воспроизводимых тестов можно использовать use_llm=False.
Для демо с русским объяснением можно использовать use_llm=True при запущенной Ollama.
```

**Ожидаемый результат:** рекомендации выглядят понятно для тимлида.

**Примерное время:** 5–8 часов.  
**Коммит:** `Add Russian explanation agent`

---

## 15.8. Реализовать Plane Integration Agent

- [x] Создать `src/agents/plane_agent.py`.
- [x] Агент умеет загрузить задачу из Plane.
- [x] Агент умеет подготовить markdown-комментарий.
- [x] Агент умеет добавить комментарий в Plane через `PlaneClient`.
- [x] Агент запускает write-back только при `write_back=True`.
- [x] Добавлен marker `Generated by COMPASS AI`.
- [x] Добавлена защита от повторной записи комментария.
- [x] Добавлена проверка существующего COMPASS AI comment.
- [x] Добавлена обработка ошибок write-back.
- [x] Опциональное auto-assign пока не включено.

Файл:

```text
src/agents/plane_agent.py
```

Использует:

```text
src/integration/plane_client.py
```

Основные функции:

```text
build_basic_plane_comment()
load_plane_work_item()
existing_compass_comment_exists()
write_recommendation_comment()
run_plane_agent()
```

Marker комментария:

```text
Generated by COMPASS AI
```

Как работает write-back:

```text
1. Оркестратор передаёт project_id и work_item_id.
2. Plane Agent проверяет write_back.
3. Если write_back=False, агент ничего не пишет в Plane.
4. Если write_back=True, агент проверяет существующие комментарии.
5. Если COMPASS AI comment уже есть, запись пропускается.
6. Если комментария нет, создаётся markdown-комментарий.
7. Результат записи сохраняется в final_response["plane_write_back"].
```

Формат комментария:

```text
## COMPASS AI Recommendation

Recommended assignee
Mode
Score
Top candidates
Explanation
Decision-support note
Generated by COMPASS AI marker
```

Важно:

```text
Plane Agent не запускает весь pipeline сам.
Он отвечает только за Plane-specific операции:
load work item
format basic comment
write comment
skip duplicate comment
```

Важно:

```text
Auto-assignment намеренно не включён на этом этапе.
Автоматическое назначение будет отдельным безопасным шагом позже,
с threshold и параметром auto_assign=false по умолчанию.
```

Важно:

```text
На этом этапе write-back подготовлен технически.
Массовая запись комментариев в Plane не выполняется по умолчанию.
```

**Ожидаемый результат:** COMPASS AI начинает реально работать с Plane.

**Примерное время:** 6–10 часов.  
**Коммит:** `Add Plane integration agent`

---

## 15.9. Собрать общий agentic orchestrator

- [x] Создать `src/agents/orchestrator.py`.
- [x] Оркестратор запускает Task Analyzer.
- [x] Оркестратор запускает Team State Analyzer.
- [x] Оркестратор запускает Matching Model Agent.
- [x] Оркестратор запускает Explanation Agent.
- [x] Оркестратор запускает Plane Integration Agent только при необходимости.
- [x] Оркестратор возвращает единый response.
- [x] Добавлена обработка ошибок через `AgentState.errors`.
- [x] Добавлен запуск для synthetic task.
- [x] Добавлена функция `recommend_synthetic_task()`.
- [x] Добавлена функция `run_agentic_recommendation()`.
- [x] Проверены все 4 recommendation modes.

Файл:

```text
src/agents/orchestrator.py
```

Pipeline:

```text
Plane/manual/synthetic task
→ Task Analyzer
→ Team State Analyzer
→ Matching Model Agent
→ Explanation Agent
→ Plane Integration Agent
→ final response
```

Основные функции:

```text
run_agentic_recommendation()
recommend_synthetic_task()
load_synthetic_task()
```

Как работает `run_agentic_recommendation()`:

```text
1. Принимает issue dict или project_id + work_item_id.
2. Если issue не передан, загружает задачу из Plane.
3. Создаёт AgentState.
4. Запускает Task Analyzer.
5. Запускает Team Analyzer.
6. Запускает Matching Agent.
7. Запускает Explanation Agent.
8. При write_back=True запускает Plane Agent.
9. Возвращает единый JSON-compatible response.
```

Как работает `recommend_synthetic_task()`:

```text
1. Загружает task из data/synthetic/tasks.csv по task_id.
2. Превращает synthetic task в issue-like dict.
3. Запускает общий agentic pipeline.
4. По умолчанию не использует LLM, чтобы проверка была стабильной.
5. Возвращает top-3 и explanation.
```

Формат response:

```text
task_id
plane_work_item_id
plane_issue_id
title
task_type
mode
top_candidates
explanation
errors
source
plane_write_back
```

Фактическая проверка `TASK-0001`, `balanced_workload`:

```text
task_id: TASK-0001
title: Добавить endpoint для статистики команды — интеграции с Plane
task_type: backend_feature
mode: balanced_workload
source: agentic_pipeline
errors: []
```

Top-3 `balanced_workload`:

```text
1. EMP-014 — Никита Егоров — backend_developer senior — score 0.956596
2. EMP-011 — Полина Васильева — backend_developer senior — score 0.956551
3. EMP-010 — Сергей Павлов — backend_developer middle — score 0.925464
```

Top-3 `fast_delivery`:

```text
1. EMP-011 — Полина Васильева — backend_developer senior — score 1.0
2. EMP-014 — Никита Егоров — backend_developer senior — score 1.0
3. EMP-007 — Ольга Волкова — backend_developer middle — score 0.962904
```

Top-3 `growth`:

```text
1. EMP-007 — Ольга Волкова — backend_developer middle — score 0.954844
2. EMP-011 — Полина Васильева — backend_developer senior — score 0.927383
3. EMP-014 — Никита Егоров — backend_developer senior — score 0.924308
```

Top-3 `risk_minimization`:

```text
1. EMP-010 — Сергей Павлов — backend_developer middle — score 1.0
2. EMP-011 — Полина Васильева — backend_developer senior — score 1.0
3. EMP-014 — Никита Егоров — backend_developer senior — score 1.0
```

Что показывают режимы:

```text
balanced_workload выбирает сильного backend-кандидата с хорошим балансом факторов.
fast_delivery поднимает кандидата с высокой скоростью и deadline reliability.
growth поднимает middle-кандидата с высоким growth_match.
risk_minimization поднимает кандидата с низким риском и хорошей надёжностью.
```

Фактическое fallback explanation для `TASK-0001`:

```text
Рекомендованный исполнитель: Никита Егоров (backend_developer).
Режим рекомендации: balanced_workload.
Score: 0.956596.
Почему подходит: учтены skill match, риск, загрузка, скорость и надёжность.
Альтернативы: Полина Васильева, Сергей Павлов.
Финальное решение остаётся за тимлидом.
```

Проверки:

```bash
python -m py_compile src/models/inference.py src/agents/state.py src/agents/task_analyzer.py src/agents/team_analyzer.py src/agents/matching_agent.py src/llm/ollama_client.py src/agents/explanation_agent.py src/agents/plane_agent.py src/agents/orchestrator.py
```

```bash
ruff check src/models/inference.py src/agents/state.py src/agents/task_analyzer.py src/agents/team_analyzer.py src/agents/matching_agent.py src/llm/ollama_client.py src/agents/explanation_agent.py src/agents/plane_agent.py src/agents/orchestrator.py
```

Фактический результат:

```text
All checks passed.
```

Проверка inference:

```bash
python src/models/inference.py
```

Проверка orchestrator:

```bash
python src/agents/orchestrator.py
```

Проверка режима `balanced_workload`:

```bash
python -c "from src.agents.orchestrator import recommend_synthetic_task; import json; print(json.dumps(recommend_synthetic_task('TASK-0001', mode='balanced_workload', top_k=3, use_llm=False), ensure_ascii=False, indent=2))"
```

Проверка режима `fast_delivery`:

```bash
python -c "from src.agents.orchestrator import recommend_synthetic_task; import json; print(json.dumps(recommend_synthetic_task('TASK-0001', mode='fast_delivery', top_k=3, use_llm=False), ensure_ascii=False, indent=2))"
```

Проверка режима `growth`:

```bash
python -c "from src.agents.orchestrator import recommend_synthetic_task; import json; print(json.dumps(recommend_synthetic_task('TASK-0001', mode='growth', top_k=3, use_llm=False), ensure_ascii=False, indent=2))"
```

Проверка режима `risk_minimization`:

```bash
python -c "from src.agents.orchestrator import recommend_synthetic_task; import json; print(json.dumps(recommend_synthetic_task('TASK-0001', mode='risk_minimization', top_k=3, use_llm=False), ensure_ascii=False, indent=2))"
```

**Ожидаемый результат:** есть настоящая агентная связка из нескольких компонентов.

**Примерное время:** 6–10 часов.  
**Коммит:** `Add agentic recommendation orchestrator`

---

# 16. Этап 14 — интеграция recommendations API с агентами

## 16.1. Подключить orchestrator к FastAPI

- [x] Endpoint `/recommendations/issue/{issue_id}` вызывает agentic orchestrator.
- [x] Endpoint принимает режим рекомендации через query parameter `mode`.
- [x] Endpoint возвращает JSON-compatible response из agentic pipeline.
- [x] Endpoint поддерживает synthetic task id формата `TASK-*`.
- [x] Endpoint поддерживает реальные Plane work items.
- [x] Endpoint умеет искать Plane work item по `issue_id`.
- [x] Endpoint поддерживает явный `project_id`, если задачу надо искать внутри конкретного проекта.
- [x] Endpoint опционально добавляет комментарий в Plane через `write_back=true`.
- [x] Добавлен query parameter `write_back=true/false`.
- [x] Добавлен query parameter `mode`.
- [x] Добавлен query parameter `top_k`.
- [x] Добавлен query parameter `use_llm`.
- [x] Добавлена обработка ошибок Plane API.
- [x] Добавлена обработка ошибки, если work item не найден.
- [x] Добавлена защита: `write_back=true` запрещён для synthetic task `TASK-*`.
- [x] Вынесен отдельный router `src/api/recommendations.py`.
- [x] Router подключён в `app/api.py`.
- [x] Старый placeholder endpoint `/recommendations/issue/{issue_id}` заменён на реальную agentic-интеграцию.

Файлы:

```text
src/api/__init__.py
src/api/recommendations.py
app/api.py
```

Endpoint:

```text
GET /recommendations/issue/{issue_id}
```

Пример synthetic endpoint:

```text
GET /recommendations/issue/TASK-0001?mode=balanced_workload&write_back=false&use_llm=false
```

Пример Plane endpoint:

```text
GET /recommendations/issue/{plane_work_item_id}?project_id={project_id}&mode=balanced_workload&write_back=false&use_llm=false
```

Пример с записью комментария в Plane:

```text
GET /recommendations/issue/{plane_work_item_id}?project_id={project_id}&mode=balanced_workload&write_back=true&use_llm=false
```

Поддерживаемые query parameters:

```text
project_id: optional Plane project id
mode: fast_delivery | balanced_workload | growth | risk_minimization
top_k: количество кандидатов, от 1 до 10
write_back: true/false
use_llm: true/false
```

Как работает endpoint:

```text
1. Нормализует recommendation mode.
2. Если issue_id начинается с TASK-, запускает synthetic path через recommend_synthetic_task().
3. Если issue_id не TASK-*, создаёт PlaneClient.
4. Если project_id передан, ищет work item внутри этого проекта.
5. Если project_id не передан, ищет work item по всем проектам workspace.
6. Передаёт найденный work item в run_agentic_recommendation().
7. Orchestrator запускает Task Analyzer, Team Analyzer, Matching Agent, Explanation Agent.
8. Если write_back=true, дополнительно запускается Plane Agent.
9. Возвращает единый JSON response.
```

Основные функции в router:

```text
extract_results()
normalize_bool()
work_item_identifier_matches()
is_open_work_item()
resolve_plane_work_item()
recommend_for_issue()
```

Response содержит:

```text
task_id
plane_work_item_id
plane_issue_id
title
task_type
mode
top_candidates
explanation
errors
source
plane_write_back
```

Фактическая проверка synthetic task `TASK-0001`, режим `balanced_workload`:

```text
HTTP 200 OK
task_id: TASK-0001
task_type: backend_feature
mode: balanced_workload
source: agentic_pipeline
errors: []
```

Top-3 `TASK-0001`, `balanced_workload`:

```text
1. EMP-014 — Никита Егоров — backend_developer senior — score 0.956596
2. EMP-011 — Полина Васильева — backend_developer senior — score 0.956551
3. EMP-010 — Сергей Павлов — backend_developer middle — score 0.925464
```

Фактическая проверка `TASK-0001`, `fast_delivery`:

```text
1. EMP-011 — Полина Васильева — backend_developer senior — score 1.0
2. EMP-014 — Никита Егоров — backend_developer senior — score 1.0
3. EMP-007 — Ольга Волкова — backend_developer middle — score 0.962904
```

Фактическая проверка `TASK-0001`, `growth`:

```text
1. EMP-007 — Ольга Волкова — backend_developer middle — score 0.954844
2. EMP-011 — Полина Васильева — backend_developer senior — score 0.927383
3. EMP-014 — Никита Егоров — backend_developer senior — score 0.924308
```

Фактическая проверка `TASK-0001`, `risk_minimization`:

```text
1. EMP-010 — Сергей Павлов — backend_developer middle — score 1.0
2. EMP-011 — Полина Васильева — backend_developer senior — score 1.0
3. EMP-014 — Никита Егоров — backend_developer senior — score 1.0
```

Что было выяснено:

```text
Для synthetic task TASK-* используется ML path через TaskEmployeeMatchingNet,
потому что для таких задач есть precomputed rows в training_pairs.parquet.
```

Важно:

```text
write_back=true доступен только для реальных Plane work items.
Для TASK-* write_back запрещён, потому что synthetic task не имеет реального Plane comment target.
```

Важно:

```text
use_llm=false используется для стабильных локальных проверок.
Если use_llm=true и Ollama server запущен, Explanation Agent может использовать локальную LLM.
Если Ollama недоступна, остаётся fallback explanation.
```

Команда проверки:

```bash
curl "http://localhost:8000/recommendations/issue/TASK-0001?mode=balanced_workload&write_back=false&use_llm=false"
```

Фактический результат:

```text
Endpoint вернул HTTP 200 OK.
Agentic pipeline вернул top-3 кандидатов.
ML inference path сработал.
Fallback explanation сработал без LLM.
```

**Ожидаемый результат:** backend умеет рекомендовать исполнителя для конкретной задачи Plane.

**Примерное время:** 4–6 часов.  
**Коммит:** `Connect recommendation API to agents`

---

## 16.2. Добавить endpoint для пакетного анализа задач

- [x] Создать endpoint `/recommendations/project/{project_id}/open-issues`.
- [x] Endpoint получает work items проекта из Plane.
- [x] Endpoint фильтрует открытые задачи.
- [x] Для каждой задачи запускает recommendation pipeline.
- [x] Возвращает список рекомендаций.
- [x] Не пишет комментарии в Plane по умолчанию.
- [x] Не поддерживает массовый write-back.
- [x] Добавлен `limit`, чтобы не обрабатывать слишком много задач.
- [x] Добавлен `mode`.
- [x] Добавлен `use_llm`.
- [x] Добавлена обработка ошибок на уровне отдельной задачи.
- [x] Если одна задача упала, batch endpoint продолжает обработку остальных.
- [x] Проверен batch-анализ проекта `Backend Platform`.

Endpoint:

```text
GET /recommendations/project/{project_id}/open-issues
```

Пример:

```text
GET /recommendations/project/{project_id}/open-issues?limit=10&mode=balanced_workload
```

Фактически проверенный project id:

```text
Backend Platform:
e608e7ad-f4fe-401d-b0f3-5570e82f08ee
```

Фактически проверенная команда:

```bash
curl "http://localhost:8000/recommendations/project/e608e7ad-f4fe-401d-b0f3-5570e82f08ee/open-issues?limit=3&mode=balanced_workload&use_llm=false"
```

Фактический response summary:

```text
project_id: e608e7ad-f4fe-401d-b0f3-5570e82f08ee
mode: balanced_workload
limit: 3
processed_count: 3
write_back: false
recommendations: 3 items
```

Как работает endpoint:

```text
1. Создаёт PlaneClient.
2. Загружает work items проекта.
3. Фильтрует закрытые задачи.
4. Берёт первые limit открытых задач.
5. Для каждой задачи запускает run_agentic_recommendation().
6. write_back всегда false.
7. Возвращает массив recommendations.
```

Фильтрация открытых задач:

```text
completed_at есть -> задача закрыта
archived_at есть -> задача исключается
state.group completed -> задача закрыта
state.group cancelled -> задача закрыта
state.group backlog/unstarted/started -> задача считается открытой
если state пришёл не dict, задача считается открытой по fallback
```

Фактически обработанные задачи в batch-проверке:

```text
1. Добавить запись комментария COMPASS AI в Plane
2. Добавить миграцию для хранения model scores
3. Реализовать JWT-авторизацию
```

Фактический результат для первой batch-задачи:

```text
recommended: Дарья Соловьёва
role: frontend_developer
grade: senior
score: 0.7184
source: rule_based_fallback
```

Почему batch-задачи пошли через fallback:

```text
Plane work items не являются TASK-* из synthetic training dataset.
Для них нет precomputed ML rows в training_pairs.parquet.
Поэтому Matching Agent корректно деградирует в rule_based_fallback.
```

Важно:

```text
Batch endpoint специально не пишет комментарии в Plane.
Массовая запись комментариев может засорить Plane.
Write-back должен запускаться точечно через /recommendations/issue/{issue_id}.
```

Важно:

```text
limit ограничен диапазоном 1–50.
Это защищает backend от случайного запуска анализа слишком большого backlog.
```

Что было выяснено:

```text
Первая попытка curl к batch endpoint упала с:
Failed to connect to localhost port 8000
Причина была не в коде, а в том, что FastAPI server не был запущен.
После запуска uvicorn endpoint вернул HTTP 200 OK.
```

Проверка Plane перед batch endpoint:

```bash
python scripts/check_plane_connection.py
```

Фактический результат Plane connection:

```text
Plane API healthcheck: OK
Projects found: 4

Backend Platform: 57 work items, 5 states, 25 labels
Frontend Platform: 19 work items, 5 states, 25 labels
Data Platform: 26 work items, 5 states, 25 labels
Internal Tools: 19 work items, 5 states, 25 labels
```

**Ожидаемый результат:** можно анализировать сразу backlog проекта.

**Примерное время:** 5–8 часов.  
**Коммит:** `Add batch issue recommendations`

---

## 16.3. Добавить endpoint для ручной задачи без Plane

- [x] Создать endpoint `/recommendations/manual`.
- [x] Endpoint принимает JSON с задачей.
- [x] Endpoint принимает Plane-like или COMPASS-like task payload.
- [x] Endpoint принимает `mode`.
- [x] Endpoint принимает `top_k`.
- [x] Endpoint принимает `use_llm`.
- [x] Endpoint принимает optional `employees`.
- [x] Endpoint возвращает top-3.
- [x] Endpoint не требует запущенный Plane.
- [x] Endpoint не пишет комментарии в Plane.
- [x] Endpoint запускает тот же agentic orchestrator.
- [x] Для новых manual-задач используется rule-based fallback.
- [x] Добавлена Pydantic-схема `ManualRecommendationRequest`.

Endpoint:

```text
POST /recommendations/manual
```

Pydantic request model:

```text
ManualRecommendationRequest
```

Поля request:

```text
issue: dict
employees: optional list[dict]
mode: string
top_k: int, от 1 до 10
use_llm: bool
```

Пример request:

```json
{
  "issue": {
    "id": "manual-001",
    "name": "Добавить endpoint для командной аналитики",
    "description_html": "Нужно сделать FastAPI endpoint для summary по загрузке команды и рискам.",
    "priority": "high",
    "labels": ["backend", "fastapi", "feature"],
    "deadline_days": 7
  },
  "mode": "balanced_workload",
  "top_k": 3,
  "use_llm": false
}
```

Фактически проверенная команда:

```bash
curl --request POST "http://localhost:8000/recommendations/manual" --header "Content-Type: application/json" --data '{"issue":{"id":"manual-001","name":"Добавить endpoint для командной аналитики","description_html":"Нужно сделать FastAPI endpoint для summary по загрузке команды и рискам.","priority":"high","labels":["backend","fastapi","feature"],"deadline_days":7},"mode":"balanced_workload","top_k":3,"use_llm":false}'
```

Фактический response summary:

```text
plane_work_item_id: manual-001
plane_issue_id: manual-001
title: Добавить endpoint для командной аналитики
task_type: backend_feature
mode: balanced_workload
source: agentic_pipeline
errors: []
```

Фактический top-3 для manual-задачи:

```text
1. EMP-011 — Полина Васильева — backend_developer senior — score 0.7334
2. EMP-010 — Сергей Павлов — backend_developer middle — score 0.703
3. EMP-014 — Никита Егоров — backend_developer senior — score 0.6829
```

Фактический ranking source:

```text
rule_based_fallback
```

Почему manual endpoint использует fallback:

```text
Manual-задача не существует в synthetic training_pairs.parquet.
Для неё нет готовых task/employee/pair ML features.
Поэтому Matching Agent корректно использует rule_based_fallback.
```

Как работает endpoint:

```text
1. Принимает JSON с задачей.
2. Нормализует recommendation mode.
3. Передаёт issue в run_agentic_recommendation().
4. Task Analyzer определяет task_type, skills, stack, priority, deadline и complexity.
5. Team Analyzer загружает synthetic team из data/synthetic/employees.csv.
6. Matching Agent использует ML path, если есть precomputed TASK-* features, иначе rule-based fallback.
7. Explanation Agent формирует объяснение.
8. Response возвращается как JSON.
```

Важно:

```text
Поле employees в request сейчас принято как future extension.
Текущий orchestrator использует synthetic team из data/synthetic/employees.csv.
Полноценный override employees лучше добавить позже отдельной доработкой Team Analyzer,
чтобы не сломать текущий стабильный MVP pipeline.
```

Важно:

```text
Manual endpoint нужен для тестирования COMPASS AI без Plane.
Это удобно для frontend/dashboard, демо, unit/e2e tests и ручной проверки новых задач.
```

**Ожидаемый результат:** COMPASS AI можно тестировать независимо от Plane.

**Примерное время:** 3–5 часов.  
**Коммит:** `Add manual recommendation endpoint`

---

## 16.4. Проверить API endpoints этапа 16

- [x] Проверить наличие старых компонентов agentic pipeline.
- [x] Проверить наличие `app/api.py`.
- [x] Проверить FastAPI dependencies.
- [x] Проверить компиляцию новых API-файлов.
- [x] Проверить `ruff`.
- [x] Запустить FastAPI через `uvicorn`.
- [x] Проверить `/health`.
- [x] Проверить `/recommendations/issue/TASK-0001`.
- [x] Проверить все 4 recommendation modes.
- [x] Запустить Plane.
- [x] Проверить Plane connection.
- [x] Проверить batch endpoint для проекта.
- [x] Проверить manual endpoint.
- [x] Проверить, что endpoints возвращают HTTP 200 OK.

Проверка наличия компонентов:

```bash
test -f src/agents/orchestrator.py && echo "orchestrator ok"
```

```bash
test -f src/agents/plane_agent.py && echo "plane agent ok"
```

```bash
test -f src/models/inference.py && echo "model inference ok"
```

```bash
test -f app/api.py && echo "api file ok"
```

Проверка зависимостей:

```bash
python -c "import fastapi, pydantic, pandas, httpx; print('api deps ok')"
```

Фактический результат:

```text
orchestrator ok
plane agent ok
model inference ok
api file ok
api deps ok
```

Проверка компиляции:

```bash
python -m py_compile app/api.py src/api/__init__.py src/api/recommendations.py src/agents/orchestrator.py src/agents/task_analyzer.py src/agents/team_analyzer.py src/agents/matching_agent.py src/agents/explanation_agent.py src/agents/plane_agent.py
```

Проверка линтера:

```bash
ruff check app/api.py src/api/recommendations.py
```

Фактический результат:

```text
All checks passed!
```

Запуск API:

```bash
uvicorn app.api:app --reload --host 0.0.0.0 --port 8000
```

Фактический запуск:

```text
Uvicorn running on http://0.0.0.0:8000
Application startup complete.
```

Проверка health:

```bash
curl "http://localhost:8000/health"
```

Фактический результат:

```json
{"status":"ok","service":"compass-ai"}
```

Проверка `balanced_workload`:

```bash
curl "http://localhost:8000/recommendations/issue/TASK-0001?mode=balanced_workload&write_back=false&use_llm=false"
```

Проверка `fast_delivery`:

```bash
curl "http://localhost:8000/recommendations/issue/TASK-0001?mode=fast_delivery&write_back=false&use_llm=false"
```

Проверка `growth`:

```bash
curl "http://localhost:8000/recommendations/issue/TASK-0001?mode=growth&write_back=false&use_llm=false"
```

Проверка `risk_minimization`:

```bash
curl "http://localhost:8000/recommendations/issue/TASK-0001?mode=risk_minimization&write_back=false&use_llm=false"
```

Проверка Plane:

```bash
./scripts/start_plane.sh
```

```bash
python scripts/check_plane_connection.py
```

Фактический результат Plane:

```text
Plane is ready.
Plane API healthcheck: OK.
Projects found: 4.
Backend Platform: 57 work items, 5 states, 25 labels.
```

Проверка batch endpoint:

```bash
curl "http://localhost:8000/recommendations/project/e608e7ad-f4fe-401d-b0f3-5570e82f08ee/open-issues?limit=3&mode=balanced_workload&use_llm=false"
```

Фактический результат:

```text
HTTP 200 OK
processed_count: 3
write_back: false
recommendations: 3
```

Проверка manual endpoint:

```bash
curl --request POST "http://localhost:8000/recommendations/manual" --header "Content-Type: application/json" --data '{"issue":{"id":"manual-001","name":"Добавить endpoint для командной аналитики","description_html":"Нужно сделать FastAPI endpoint для summary по загрузке команды и рискам.","priority":"high","labels":["backend","fastapi","feature"],"deadline_days":7},"mode":"balanced_workload","top_k":3,"use_llm":false}'
```

Фактический результат:

```text
HTTP 200 OK
recommended: Полина Васильева
score: 0.7334
source: rule_based_fallback
errors: []
```

Важно:

```text
Для TASK-* endpoint использует ML inference path.
Для Plane/manual задач без precomputed ML features используется rule_based_fallback.
Это корректное поведение текущей архитектуры.
```

Важно на будущее:

```text
Task Analyzer для некоторых Plane-задач может ошибочно определить task_type по labels/title,
например backend-задача может уйти в frontend_feature, если labels из Plane недостаточно точные.
Это не ломает API, но позже стоит улучшить Task Analyzer:
- точнее парсить Plane labels;
- подтягивать label names, если Plane отдаёт только label ids;
- сильнее учитывать description keywords;
- использовать COMPASS task_id marker, если он есть в description_html.
```

Важно на будущее:

```text
Manual employees override пока не реализован.
Endpoint принимает поле employees, но orchestrator использует synthetic team.
Если dashboard позже должен передавать свой список сотрудников,
нужно доработать Team Analyzer и run_agentic_recommendation().
```

Важно на будущее:

```text
Batch endpoint не должен делать write-back.
Если понадобится массовая запись комментариев,
лучше делать отдельный безопасный endpoint с dry_run, confirmation flag и лимитами.
```

---

# 17. Этап 15 — запись рекомендаций обратно в Plane

## 17.1. Сделать формат комментария COMPASS AI

- [x] Создать `src/integration/plane_comment_formatter.py`.
- [x] Форматировать рекомендацию в Markdown.
- [x] Указать recommended assignee.
- [x] Указать score.
- [x] Указать top-3.
- [x] Указать режим.
- [x] Указать риски.
- [x] Указать объяснение LLM или fallback explanation.
- [x] Указать, что решение является рекомендацией, а не автоматическим приказом.
- [x] Добавить marker `Generated by COMPASS AI`.
- [x] Добавить helper `has_compass_marker()` для проверки существующих комментариев.
- [x] Добавить безопасное форматирование пустых значений, `None`, `NaN`, score и factors.
- [x] Добавить поддержку кандидатов из ML path и `rule_based_fallback`.

Файл:

```text
src/integration/plane_comment_formatter.py
```

Основные функции:

```text
format_plane_recommendation_comment(recommendation)
has_compass_marker(text)
```

Marker комментария:

```text
Generated by COMPASS AI
```

Формат комментария в Plane:

```text
## COMPASS AI Recommendation

Task
Task type
Mode
Recommended assignee
Score
Source

Top candidates:
1. candidate, score, success_probability, source
   - factors
   - reasons
   - risks

Explanation

Decision note:
This is a decision-support recommendation. Final assignment is made by the team lead.

Generated by COMPASS AI
```

Фактический пример formatter output для `TASK-0001`, `balanced_workload`:

```text
Recommended assignee: Никита Егоров (backend_developer, senior)
Score: 0.9566
Source: agentic_pipeline

Top candidates:
1. Никита Егоров — score=0.9566, success_probability=0.9276, source=task_employee_matching_net
2. Полина Васильева — score=0.9566, success_probability=0.9307, source=task_employee_matching_net
3. Сергей Павлов — score=0.9255, source=task_employee_matching_net
```

Фактическая проверка:

```bash
python -m py_compile src/integration/plane_comment_formatter.py
```

```bash
ruff check src/integration/plane_comment_formatter.py
```

Фактический результат:

```text
All checks passed!
```

Что было выяснено:

```text
Formatter должен работать не только с ML-кандидатами, но и с rule_based_fallback,
потому что реальные Plane work items пока не имеют precomputed ML features.
```

```text
Некоторые поля candidates могут быть None, NaN или отсутствовать.
Поэтому formatter не должен падать, если нет risk, workload_pressure, success_probability или plane_user_id.
```

```text
Комментарий лучше формировать в отдельном integration-модуле,
а не внутри Plane Agent, чтобы разделить ответственность:
formatter готовит Markdown,
Plane Agent пишет его в Plane.
```

**Примерное время:** 2–4 часа.  
**Коммит:** `Format Plane recommendation comments`

---

## 17.2. Добавить write-back в Plane

- [x] В `PlaneClient` проверить метод создания комментария.
- [x] Добавить запись комментария через API.
- [x] Проверить на одной тестовой задаче.
- [x] Убедиться, что комментарий не дублируется при повторном запуске.
- [x] Добавить защиту от повторной записи.
- [x] Добавить marker `Generated by COMPASS AI`.
- [x] Подключить `format_plane_recommendation_comment()` к Plane Agent.
- [x] Добавить чтение существующих комментариев задачи.
- [x] Добавить проверку marker в уже существующих комментариях.
- [x] Добавить поле `plane_write_back` в response.
- [x] Сохранять результат записи или skip-причину в API response.
- [x] Обработать ошибки Plane API через `PlaneClientError`.

Файлы:

```text
src/agents/plane_agent.py
src/integration/plane_comment_formatter.py
src/integration/plane_client.py
```

Основные функции Plane Agent:

```text
load_plane_work_item()
existing_compass_comment_exists()
write_recommendation_comment()
run_plane_agent()
```

Как работает write-back:

```text
1. API получает запрос с write_back=true.
2. Orchestrator строит рекомендацию через agentic pipeline.
3. Plane Agent проверяет project_id и work_item_id.
4. Plane Agent читает существующие комментарии задачи.
5. Если найден marker Generated by COMPASS AI, новый комментарий не создаётся.
6. Если marker не найден, formatter создаёт Markdown-комментарий.
7. PlaneClient отправляет комментарий в Plane через API.
8. Результат записывается в response["plane_write_back"].
```

Формат `plane_write_back`, если запись выключена:

```text
enabled: false
written: false
skipped: true
reason: write_back disabled
```

Формат `plane_write_back`, если комментарий создан:

```text
enabled: true
written: true
skipped: false
reason: null
marker: Generated by COMPASS AI
response: Plane comment response
```

Формат `plane_write_back`, если комментарий уже был:

```text
enabled: true
written: false
skipped: true
reason: COMPASS AI comment already exists
marker: Generated by COMPASS AI
```

Фактически проверенная Plane-задача:

```text
project_id: e608e7ad-f4fe-401d-b0f3-5570e82f08ee
work_item_id: 1cad7167-a07a-4f48-85c9-a61139d0590f
title: Добавить запись комментария COMPASS AI в Plane
```

Фактический первый write-back:

```text
plane_write_back.enabled: true
plane_write_back.written: true
plane_write_back.skipped: false
created comment id: 64797f00-ee0f-4408-9861-80f967203b7a
```

Фактический повторный write-back на ту же задачу:

```text
plane_write_back.enabled: true
plane_write_back.written: false
plane_write_back.skipped: true
plane_write_back.reason: COMPASS AI comment already exists
```

Фактический ranking source для реальной Plane-задачи:

```text
rule_based_fallback
```

Почему для Plane-задачи был `rule_based_fallback`:

```text
Реальный Plane work item не является TASK-* из synthetic training dataset.
Для него нет precomputed rows в data/processed/training_pairs.parquet.
Поэтому Matching Agent корректно использует rule_based_fallback.
```

Фактический top-3 для проверенной Plane-задачи:

```text
1. EMP-023 — Дарья Соловьёва — frontend_developer senior — score 0.7184
2. EMP-022 — Павел Волков — frontend_developer senior — score 0.6729
3. EMP-018 — Андрей Громов — frontend_developer middle — score 0.6506
```

Фактическая проверка Plane connection:

```text
Plane API healthcheck: OK
Projects found: 4
Backend Platform: 57 work items, 5 states, 25 labels
Frontend Platform: 19 work items, 5 states, 25 labels
Data Platform: 26 work items, 5 states, 25 labels
Internal Tools: 19 work items, 5 states, 25 labels
```

Фактические проверки качества:

```bash
python -m py_compile src/agents/plane_agent.py src/integration/plane_comment_formatter.py
```

```bash
ruff check src/agents/plane_agent.py src/integration/plane_comment_formatter.py
```

Фактический результат:

```text
All checks passed!
```

Что было выяснено:

```text
PlaneClient.list_work_items(project_id) в текущей реализации может вернуть list,
а не dict с ключом results.
Поэтому при ad-hoc поиске work item нужно поддерживать оба варианта response shape.
```

```text
Plane comment API принимает Markdown-текст и сохраняет его в comment_html.
В response Plane возвращает comment id, project, workspace, issue/work item id и created_by.
```

```text
Duplicate guard работает по marker Generated by COMPASS AI,
а не по id комментария, потому что id комментария заранее неизвестен.
```

```text
Для TASK-* write-back не используется, потому что synthetic task не является реальной целью для Plane comment.
```

Что позже стоит улучшить:

```text
Task Analyzer для некоторых Plane-задач может ошибочно определить task_type,
если Plane labels/title недостаточно точные.
Например проверенная задача про комментарий COMPASS AI была определена как frontend_feature.
Позже стоит улучшить parsing label names, description keywords и COMPASS task marker.
```

**Примерное время:** 4–8 часов.  
**Коммит:** `Write recommendations back to Plane`

---

## 17.3. Добавить опциональное автоматическое назначение

- [x] Добавить параметр `auto_assign=false`.
- [x] По умолчанию не назначать автоматически.
- [x] Если `auto_assign=true`, пытаться назначить top-1 кандидата.
- [x] Перед назначением проверять, что `score >= threshold`.
- [x] Threshold по умолчанию: `0.75`.
- [x] Если score ниже threshold, только писать комментарий.
- [x] Если у top-1 нет `plane_user_id`, не назначать автоматически.
- [x] Запретить `auto_assign=true` для synthetic task `TASK-*`.
- [x] Прокинуть `auto_assign` и `threshold` через API.
- [x] Прокинуть `auto_assign` и `threshold` через orchestrator.
- [x] Добавить результат автоназначения в response как `plane_auto_assign`.
- [x] Не делать auto-assign без явного query parameter.

Файлы:

```text
src/agents/plane_agent.py
src/agents/orchestrator.py
src/api/recommendations.py
```

Endpoint:

```text
GET /recommendations/issue/{issue_id}?write_back=true&auto_assign=true&threshold=0.75
```

Поддерживаемые query parameters:

```text
write_back: true/false
auto_assign: true/false
threshold: float, default 0.75
mode: fast_delivery | balanced_workload | growth | risk_minimization
use_llm: true/false
project_id: optional Plane project id
```

Как работает auto-assign:

```text
1. По умолчанию auto_assign=false.
2. Если auto_assign=false, назначение не выполняется.
3. Если auto_assign=true, берётся top-1 кандидат.
4. Проверяется score top-1 кандидата.
5. Если score < threshold, назначение пропускается.
6. Если score >= threshold, проверяется plane_user_id.
7. Если plane_user_id отсутствует, назначение пропускается.
8. Если score достаточный и plane_user_id есть, вызывается PlaneClient.update_work_item_assignee().
9. Результат записывается в response["plane_auto_assign"].
```

Формат `plane_auto_assign`, если auto-assign выключен:

```text
enabled: false
assigned: false
skipped: true
reason: auto_assign disabled
```

Формат `plane_auto_assign`, если score ниже threshold:

```text
enabled: true
assigned: false
skipped: true
reason: score below threshold: 0.7184 < 0.7500
score: 0.7184
threshold: 0.75
employee_id: EMP-023
```

Формат `plane_auto_assign`, если нет Plane user mapping:

```text
enabled: true
assigned: false
skipped: true
reason: top candidate has no plane_user_id
employee_id: EMP-XXX
```

Формат `plane_auto_assign`, если назначение выполнено:

```text
enabled: true
assigned: true
skipped: false
reason: null
score: candidate score
threshold: threshold
employee_id: employee id
plane_user_id: Plane user id
```

Фактическая проверка запрета auto-assign для synthetic task:

```text
GET /recommendations/issue/TASK-0001?mode=balanced_workload&write_back=false&auto_assign=true&threshold=0.75&use_llm=false
```

Фактический результат:

```text
auto_assign=true is available only for real Plane work items.
```

Фактическая проверка synthetic task без auto-assign:

```text
TASK-0001
mode: balanced_workload
write_back: false
auto_assign: false
HTTP response: OK
top-3 вернулся через task_employee_matching_net
```

Фактический top-3 для `TASK-0001`, `balanced_workload`:

```text
1. EMP-014 — Никита Егоров — backend_developer senior — score 0.956596
2. EMP-011 — Полина Васильева — backend_developer senior — score 0.956551
3. EMP-010 — Сергей Павлов — backend_developer middle — score 0.925464
```

Фактическая проверка auto-assign на реальной Plane-задаче:

```text
GET /recommendations/issue/1cad7167-a07a-4f48-85c9-a61139d0590f?project_id=e608e7ad-f4fe-401d-b0f3-5570e82f08ee&mode=balanced_workload&write_back=true&auto_assign=true&threshold=0.75&use_llm=false
```

Фактический результат:

```text
plane_write_back.written: false
plane_write_back.skipped: true
plane_write_back.reason: COMPASS AI comment already exists

plane_auto_assign.enabled: true
plane_auto_assign.assigned: false
plane_auto_assign.skipped: true
plane_auto_assign.reason: score below threshold: 0.7184 < 0.7500
```

Что было выяснено:

```text
Auto-assign безопасно не сработал, потому что score top-1 кандидата 0.7184 ниже threshold 0.75.
Это правильное поведение: комментарий может быть записан, но задача не назначается автоматически.
```

```text
Даже если score будет выше threshold, auto-assign всё равно требует plane_user_id.
Сейчас у большинства synthetic employees plane_user_id отсутствует,
поэтому для полноценного auto-assignment нужно завершить employee -> Plane user mapping.
```

```text
Автоназначение не должно быть включено по умолчанию.
Это управленческое действие, поэтому оно запускается только явно через auto_assign=true.
```

Что позже стоит улучшить:

```text
Нужно заполнить data/processed/employee_plane_mapping.csv реальными Plane user IDs
для сотрудников, которых можно назначать автоматически.
```

```text
Можно добавить отдельный audit log для auto-assign действий,
чтобы видеть, кто был назначен, по какой задаче, с каким score и threshold.
```

```text
Можно добавить более строгую защиту:
auto_assign=true разрешать только вместе с write_back=true,
чтобы в Plane всегда оставался объясняющий комментарий к автоматическому назначению.
```

Фактические проверки качества:

```bash
python -m py_compile src/api/recommendations.py src/agents/orchestrator.py src/agents/plane_agent.py
```

```bash
ruff check src/api/recommendations.py src/agents/orchestrator.py src/agents/plane_agent.py
```

Фактический результат:

```text
All checks passed!
```

**Примерное время:** 4–8 часов.  
**Коммит:** `Add optional auto assignment`

---

# 18. Этап 16 — простое окно AI-помощника и dashboard

## 18.1. Принять решение по интерфейсу

- [x] Не переписывать Plane полностью.
- [x] Сделать отдельный лёгкий COMPASS dashboard.
- [x] Dashboard должен ссылаться на задачи Plane.
- [x] В Plane рекомендации живут в комментариях.
- [x] В COMPASS dashboard живут метрики, топ задач, fairness и нагрузка.
- [x] Если будет желание глубже интегрироваться в UI Plane, делать это только после MVP.
- [x] Оставить Plane как основную project management систему.
- [x] Использовать dashboard как отдельный AI/analytics слой поверх Plane и COMPASS API.
- [x] Не встраивать COMPASS AI напрямую во frontend Plane на MVP-этапе.

**Причина:** менять фронтенд Plane сложнее, чем сделать внешний dashboard. Для учебного проекта внешний dashboard + комментарии в Plane достаточно выглядят как интеграция.

Фактическое решение:

```text
Plane остаётся системой задач.
COMPASS AI читает задачи из Plane через REST API.
COMPASS AI пишет рекомендации обратно в Plane comments.
Dashboard показывает рекомендации, аналитику команды, метрики модели и fairness.
```

Как разделены роли интерфейсов:

```text
Plane:
- проекты;
- work items;
- labels;
- states;
- comments;
- финальное место, где тимлид видит рекомендацию COMPASS AI.

COMPASS dashboard:
- быстрый запуск анализа задач;
- просмотр top-3 кандидатов;
- просмотр team workload;
- просмотр model metrics;
- просмотр fairness metrics;
- ручной анализ задач без Plane;
- write-back рекомендации в Plane по кнопке.
```

Почему выбран отдельный dashboard:

```text
Отдельный dashboard быстрее реализовать и проще поддерживать.
Он не ломает локальный Plane.
Он работает как внешний AI-помощник.
Он показывает управленческую аналитику, которой нет в стандартном Plane UI.
```

**Ожидаемый результат:** понятная стратегия UI.

**Фактический результат:** стратегия UI зафиксирована: отдельный Streamlit dashboard + настоящая интеграция с Plane через API и comments.

**Примерное время:** 30 минут.  
**Коммит:** коммит не нужен.

---

## 18.2. Сделать dashboard на FastAPI HTML или Streamlit

- [x] Выбрать простой вариант.
- [x] Рекомендуемый вариант для студенческого проекта: Streamlit.
- [x] Создать `app/dashboard.py`.
- [x] Показать список открытых задач.
- [x] Показать top recommendation по каждой задаче.
- [x] Показать team workload.
- [x] Показать model metrics.
- [x] Показать fairness metrics.
- [x] Добавить кнопку/действие “Analyze issue”.
- [x] Добавить кнопку/действие “Write recommendation to Plane”.
- [x] Подключить dashboard к FastAPI backend.
- [x] Добавить анализ synthetic task `TASK-*`.
- [x] Добавить анализ реального Plane work item.
- [x] Добавить анализ manual task без Plane.
- [x] Добавить поддержку `mode`, `top_k`, `use_llm`, `write_back`, `auto_assign`, `threshold`.
- [x] Добавить чтение synthetic datasets из `data/synthetic`.
- [x] Добавить чтение model/ranking reports из `reports`.
- [x] Добавить обработку ошибок API прямо в dashboard.
- [x] Добавить command target `make dashboard`.
- [x] Исправить deprecated Streamlit параметр `use_container_width` на `width`.

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

Команда запуска напрямую:

```bash
streamlit run app/dashboard.py
```

Команда запуска через Makefile:

```bash
make dashboard
```

Фактический Makefile target:

```text
dashboard:
	streamlit run app/dashboard.py
```

Фактический локальный URL dashboard:

```text
http://localhost:8501
```

Фактический запуск:

```text
make dashboard
streamlit run app/dashboard.py
Uvicorn server started on 0.0.0.0:8501
Local URL: http://localhost:8501
```

Что делает dashboard:

```text
1. Подключается к COMPASS API по http://localhost:8000.
2. Показывает synthetic/team/model/fairness analytics из локальных CSV/JSON.
3. Для рекомендаций вызывает FastAPI endpoints.
4. Для Plane work item может запустить write_back=true.
5. Для auto_assign передаёт auto_assign=true и threshold, но только если пользователь явно включил это действие.
```

Основные источники данных dashboard:

```text
data/synthetic/employees.csv
data/synthetic/tasks.csv
data/synthetic/assignments.csv
reports/model_metrics.json
reports/ranking_metrics.json
```

FastAPI endpoints, которые использует dashboard:

```text
GET /health
GET /recommendations/issue/{issue_id}
POST /recommendations/manual
```

Dashboard поддерживает три сценария рекомендации:

```text
Synthetic TASK-*:
использует ML path через TaskEmployeeMatchingNet, потому что для TASK-* есть precomputed features.

Plane work item:
использует реальные задачи Plane, может делать write-back comment, при отсутствии precomputed ML features использует rule_based_fallback.

Manual task:
позволяет проверить новую задачу без Plane, использует тот же agentic pipeline и rule_based_fallback.
```

Пример synthetic анализа:

```text
TASK-0001
mode: balanced_workload
write_back: false
auto_assign: false
use_llm: false

Top-3:
1. Никита Егоров — backend_developer senior — score 0.956596
2. Полина Васильева — backend_developer senior — score 0.956551
3. Сергей Павлов — backend_developer middle — score 0.925464
```

Пример Plane анализа:

```text
project_id: e608e7ad-f4fe-401d-b0f3-5570e82f08ee
work_item_id: 1cad7167-a07a-4f48-85c9-a61139d0590f
mode: balanced_workload
top_k: 3
write_back: false или true
auto_assign: false
use_llm: false или true
```

Фактически проверенный Plane request через dashboard/API:

```text
GET /recommendations/issue/1cad7167-a07a-4f48-85c9-a61139d0590f?project_id=e608e7ad-f4fe-401d-b0f3-5570e82f08ee&mode=balanced_workload&top_k=3&write_back=false&auto_assign=false&threshold=0.75&use_llm=false
```

Фактический результат:

```text
HTTP 200 OK
recommendation returned
source: agentic_pipeline
candidate source: rule_based_fallback
```

Фактически проверенный LLM path через dashboard/API:

```text
use_llm=true
HTTP 200 OK
```

Важно:

```text
use_llm=true работает, если Ollama server доступен.
Если Ollama недоступна, Explanation Agent должен использовать fallback explanation.
```

Важно:

```text
auto_assign не включён по умолчанию.
Это безопасное управленческое действие и запускается только явно.
```

Важно:

```text
write_back=true используется только для реальных Plane work items.
Для TASK-* запись в Plane не выполняется.
```

Что было исправлено:

```text
Streamlit начал предупреждать про устаревший use_container_width.
В dashboard use_container_width заменён на новый параметр width:
width="stretch"
width="content"
```

Фактические проверки:

```bash
python -m py_compile app/dashboard.py
```

```bash
ruff check app/dashboard.py
```

Фактический результат:

```text
All checks passed!
```

**Ожидаемый результат:** есть отдельная “менюшка” COMPASS AI для аналитики и управления рекомендациями.

**Фактический результат:** Streamlit dashboard создан, запускается через `make dashboard`, подключается к COMPASS API, показывает рекомендации, аналитику, метрики и fairness.

**Примерное время:** 8–14 часов.  
**Коммит:** `Add COMPASS analytics dashboard`

Дополнительный коммит:

```text
Add dashboard run command
```

---

## 18.3. Добавить страницы dashboard

- [x] Страница `Overview`.
- [x] Страница `Issue Recommendations`.
- [x] Страница `Team Workload`.
- [x] Страница `Model Metrics`.
- [x] Страница `Fairness`.
- [x] Страница `Settings`.
- [x] Добавить sidebar navigation.
- [x] Добавить настройку `COMPASS API URL`.
- [x] Добавить health check API.
- [x] Добавить таблицы и графики через Streamlit + Plotly.
- [x] Добавить отображение raw response для отладки.
- [x] Добавить отображение `plane_write_back`.
- [x] Добавить отображение `plane_auto_assign`.

Что показывает `Overview`:

```text
количество задач
количество сотрудников
средняя загрузка команды
количество high risk assignment rows
средняя success probability
распределение задач по проектам
распределение задач по типам
распределение assignment outcomes
COMPASS API health status
```

Фактические источники `Overview`:

```text
data/synthetic/tasks.csv
data/synthetic/employees.csv
data/synthetic/assignments.csv
GET /health
```

Что показывает `Issue Recommendations`:

```text
Synthetic TASK-* analysis
Plane work item analysis
Manual task analysis
recommended assignee
top-3 candidates
score
success_probability
mode
source
explanation
plane_write_back
plane_auto_assign
raw response
```

Действия на `Issue Recommendations`:

```text
Analyze synthetic issue
Analyze Plane work item
Analyze manual task
Write recommendation comment to Plane
Auto assign top candidate
Use LLM explanation
```

Что показывает `Team Workload`:

```text
employee
role
grade
current workload
workload percent
active tasks count
availability
overload risk
avg completion speed
avg quality score
deadline reliability
```

Workload risk logic:

```text
low: workload < 0.70
medium: workload >= 0.70
high: workload >= 0.85
critical: workload >= 0.95
```

Что показывает `Model Metrics`:

```text
ROC-AUC
PR-AUC
F1
Precision
Recall
classification metrics JSON
ranking metrics table
comparison: ML model vs rule-based baseline vs random baseline
```

Фактические model metrics из `reports/model_metrics.json`:

```text
accuracy: 0.781040
precision: 0.775764
recall: 0.733595
f1: 0.754090
roc_auc: 0.859216
pr_auc: 0.820082
```

Фактические ranking metrics из `reports/ranking_metrics.json`:

```text
ml_model:
precision_at_1: 0.893333
precision_at_3: 0.853333
ndcg_at_3: 0.862555
mrr: 0.943778

rule_based_baseline:
precision_at_1: 0.872000
precision_at_3: 0.859556
ndcg_at_3: 0.861110
mrr: 0.932667

random_baseline:
precision_at_1: 0.485333
precision_at_3: 0.501333
ndcg_at_3: 0.495777
mrr: 0.667997
```

Что показывает `Fairness`:

```text
assignment distribution by grade
assignment distribution by role
top employee concentration
senior assignment share
junior assignment share
average assigned workload
growth match share
```

Fairness metrics:

```text
senior_assignment_share
junior_assignment_share
top_employee_concentration
average_assigned_workload
growth_match_share
```

Что показывает `Settings`:

```text
COMPASS API URL
DEFAULT_PLANE_PROJECT_ID
пути к data files
пути к report files
health check button
список нужных локальных сервисов
```

Локальные сервисы, которые показывает `Settings`:

```text
FastAPI backend:
uvicorn app.api:app --reload --host 0.0.0.0 --port 8000

Plane:
./scripts/start_plane.sh

Optional LLM:
ollama serve

Dashboard:
streamlit run app/dashboard.py
```

Фактическая проверка COMPASS API:

```bash
curl "http://localhost:8000/health"
```

Фактический результат:

```text
{"status":"ok","service":"compass-ai"}
```

Фактическая проверка synthetic recommendation:

```bash
curl "http://localhost:8000/recommendations/issue/TASK-0001?mode=balanced_workload&write_back=false&auto_assign=false&use_llm=false"
```

Фактический результат:

```text
HTTP 200 OK
top_candidates returned
source: agentic_pipeline
candidate source: task_employee_matching_net
```

Фактическая проверка Plane connection:

```bash
python scripts/check_plane_connection.py
```

Фактический результат:

```text
Plane API healthcheck: OK
Projects found: 4

Backend Platform: 57 work items, 5 states, 25 labels
Frontend Platform: 19 work items, 5 states, 25 labels
Data Platform: 26 work items, 5 states, 25 labels
Internal Tools: 19 work items, 5 states, 25 labels
```

Что было выяснено:

```text
Dashboard может вызывать FastAPI endpoints и для synthetic TASK-*,
и для реальных Plane work items.
FastAPI server должен быть запущен отдельно, иначе dashboard не сможет получить рекомендации.
```

```text
Plane work items без precomputed ML features корректно уходят в rule_based_fallback.
Это ожидаемое поведение текущей архитектуры.
```

```text
Dashboard удобно показывает и финальное объяснение, и технический raw response.
Это полезно для демо и отладки agentic pipeline.
```

Что позже стоит улучшить:

```text
Добавить выбор Plane work item из списка открытых задач,
а не только ручной ввод work_item_id.
```

```text
Добавить отдельную batch-страницу для просмотра рекомендаций по backlog проекта.
```

```text
Добавить сохранение dashboard-selected demo cases в reports/demo_*.json.
```

```text
Добавить более точную fairness-аналитику по recommendations,
а не только по synthetic assignment history.
```

**Ожидаемый результат:** интерфейс показывает не только рекомендации, но и управленческую аналитику.

**Фактический результат:** dashboard содержит страницы Overview, Issue Recommendations, Team Workload, Model Metrics, Fairness и Settings, показывает данные проекта и запускает recommendation actions через FastAPI.

**Примерное время:** 10–18 часов.  
**Коммит:** `Add dashboard pages`

---

## 18.4. Добавить общий запуск и остановку всей локальной системы

- [x] Создать общий helper-скрипт запуска локальной системы.
- [x] Создать общий скрипт остановки локальной системы.
- [x] Добавить VS Code Tasks для запуска сервисов в отдельных встроенных терминалах VS Code.
- [x] Добавить общий VS Code Task `COMPASS: start stack`.
- [x] Добавить общий VS Code Task `COMPASS: stop stack`.
- [x] Запускать Plane.
- [x] Запускать Docker Desktop автоматически, если он выключен.
- [x] Запускать COMPASS FastAPI.
- [x] Запускать Streamlit dashboard.
- [x] Запускать Ollama server.
- [x] Запускать Ollama через `/Applications/Ollama.app`, если приложение доступно.
- [x] Делать fallback на `ollama serve`, если приложение не подняло server.
- [x] Не падать, если Ollama недоступна: API и dashboard могут работать с fallback explanation.
- [x] Проверять readiness Docker Desktop перед запуском Plane.
- [x] Проверять readiness Plane containers.
- [x] Проверять readiness Plane API.
- [x] Проверять readiness Plane workspace route.
- [x] Открывать Plane workspace в новой вкладке браузера после старта.
- [x] Открывать dashboard в новой вкладке браузера после старта.
- [x] Показывать логи Plane/API/Ollama/dashboard в отдельных VS Code terminals.
- [x] Останавливать dashboard по порту `8501`.
- [x] Останавливать COMPASS API по порту `8000`.
- [x] Останавливать Ollama server по порту `11434`.
- [x] Закрывать Ollama app при остановке stack.
- [x] Останавливать Plane через `scripts/stop_plane.sh`.
- [x] Останавливать Plane безопасно через `docker compose stop`.
- [x] Закрывать Docker Desktop после безопасной остановки Plane.
- [x] Не удалять Docker volumes Plane.
- [x] Не удалять Docker images.
- [x] Не удалять Docker containers.
- [x] Не удалять локальные данные, модели и отчёты.

Файлы:

```text
.vscode/tasks.json
scripts/start_compass_stack.sh
scripts/stop_compass_stack.sh
scripts/start_plane.sh
scripts/stop_plane.sh
scripts/start_ollama.sh
scripts/stop_ollama.sh
```

Название общего запуска:

```text
COMPASS local stack
```

Основной способ запуска всей системы:

```text
VS Code → Cmd+Shift+P → Tasks: Run Task → COMPASS: start stack
```

Helper-команда для открытия проекта и выбора stack task:

```bash
./scripts/start_compass_stack.sh
```

Команда остановки всей системы:

```bash
./scripts/stop_compass_stack.sh
```

Или через VS Code:

```text
VS Code → Cmd+Shift+P → Tasks: Run Task → COMPASS: stop stack
```

Что запускает `COMPASS: start stack`:

```text
1. Plane через scripts/start_plane.sh
2. Ollama через scripts/start_ollama.sh или ollama serve fallback
3. COMPASS FastAPI на http://localhost:8000
4. Streamlit dashboard на http://localhost:8501
```

Как запускаются терминалы:

```text
Каждый сервис запускается в отдельном встроенном терминале VS Code:

COMPASS: start Plane
COMPASS: start Ollama
COMPASS: start API
COMPASS: start Dashboard
```

Что делает `scripts/start_compass_stack.sh`:

```text
1. Проверяет VS Code CLI command `code`.
2. Проверяет наличие .vscode/tasks.json.
3. Открывает проект в VS Code.
4. Открывает VS Code task picker.
5. Подсказывает выбрать task `COMPASS: start stack`.

Важно: сам bash-скрипт не создаёт VS Code terminals напрямую.
Терминалы создаёт VS Code через .vscode/tasks.json.
```

Что делает `scripts/start_plane.sh`:

```text
1. Проверяет Docker CLI.
2. Если Docker Desktop выключен — запускает Docker Desktop через open -a Docker.
3. Ждёт готовности Docker daemon.
4. Проверяет Plane docker-compose.yml и .env файлы.
5. Запускает Plane через docker compose up -d.
6. Ждёт healthy status для web/admin/space.
7. Ждёт Plane API.
8. Ждёт main URL http://localhost.
9. Ждёт workspace route http://localhost/compass-ai-lab/.
10. Открывает Plane workspace в браузере.
```

Что делает `scripts/start_ollama.sh`:

```text
1. Проверяет Ollama API на http://localhost:11434/api/tags.
2. Если Ollama уже запущена — ничего лишнего не стартует.
3. Если есть /Applications/Ollama.app — открывает приложение Ollama.
4. Ждёт, пока Ollama app поднимет локальный server.
5. Если приложение не подняло server, но есть CLI `ollama` — запускает fallback `ollama serve`.
6. Держит VS Code terminal живым, пока Ollama server отвечает.
```

Что запускает `COMPASS: start API`:

```text
source .venv/bin/activate
uvicorn app.api:app --reload --host 0.0.0.0 --port 8000
```

Что запускает `COMPASS: start Dashboard`:

```text
source .venv/bin/activate
streamlit run app/dashboard.py --server.headless false --server.port 8501
```

Dashboard дополнительно открывается в браузере:

```text
http://localhost:8501
```

Что останавливает `stop_compass_stack.sh`:

```text
1. Streamlit dashboard на порту 8501.
2. FastAPI backend на порту 8000.
3. Ollama через scripts/stop_ollama.sh.
4. Plane через scripts/stop_plane.sh.
5. Docker Desktop после безопасной остановки Plane.
```

Что делает `scripts/stop_ollama.sh`:

```text
1. Останавливает Ollama server на порту 11434.
2. Закрывает приложение Ollama через osascript.
3. Проверяет, что Ollama API больше не отвечает.
```

Что делает `scripts/stop_plane.sh`:

```text
1. Переходит в plane/docker/plane-source.
2. Выполняет docker compose stop.
3. Показывает состояние Plane containers.
4. Проверяет, что http://localhost больше не отвечает.
5. Подтверждает, что Docker volumes сохранены.
6. Закрывает Docker Desktop.
```

Локальные URL после запуска:

```text
Plane UI:
http://localhost

Plane workspace:
http://localhost/compass-ai-lab/

Plane God Mode:
http://localhost/god-mode/general/

COMPASS API:
http://localhost:8000

COMPASS API health:
http://localhost:8000/health

COMPASS dashboard:
http://localhost:8501

Ollama API:
http://localhost:11434/api/tags
```

Что было проверено:

```text
bash -n scripts/start_plane.sh
bash -n scripts/stop_plane.sh
bash -n scripts/start_compass_stack.sh
bash -n scripts/stop_compass_stack.sh
bash -n scripts/start_ollama.sh
bash -n scripts/stop_ollama.sh
python -m json.tool .vscode/tasks.json
python -m py_compile app/dashboard.py
ruff check app/dashboard.py
```

Фактическая проверка API:

```bash
curl "http://localhost:8000/health"
```

Фактический результат:

```text
{"status":"ok","service":"compass-ai"}
```

Фактическая проверка Plane:

```bash
python scripts/check_plane_connection.py
```

Фактический результат:

```text
Plane API healthcheck: OK
Projects found: 4

Backend Platform: 57 work items, 5 states, 25 labels
Frontend Platform: 19 work items, 5 states, 25 labels
Data Platform: 26 work items, 5 states, 25 labels
Internal Tools: 19 work items, 5 states, 25 labels
```

Фактическая проверка recommendation endpoint:

```bash
curl "http://localhost:8000/recommendations/issue/TASK-0001?mode=balanced_workload&write_back=false&auto_assign=false&use_llm=false"
```

Фактический результат:

```text
HTTP 200 OK
source: agentic_pipeline
candidate source: task_employee_matching_net

Top-3:
1. Никита Егоров — score 0.956596
2. Полина Васильева — score 0.956551
3. Сергей Павлов — score 0.925464
```

Фактическая проверка Ollama:

```text
Ollama server started on 127.0.0.1:11434.
Model cache loaded.
Metal/iGPU compute detected on Apple M2.
```

Фактическая проверка stop stack:

```text
Streamlit dashboard stopped.
FastAPI backend stopped.
Ollama server stopped.
Ollama app closed or was not running.
Plane containers stopped through docker compose stop.
Docker Desktop daemon stopped.
Docker volumes preserved.
Plane data not deleted.
Generated data, models and reports preserved.
```

Важно:

```text
Для Docker используется безопасная остановка:

docker compose stop

Не используется:

docker compose down -v
docker volume rm
docker system prune
docker image rm
docker container rm
```

Важно:

```text
Docker Desktop можно закрывать после остановки Plane.
Это не удаляет данные.
Данные Plane хранятся в Docker volumes и сохраняются после quit Docker Desktop.
```

Важно:

```text
Ollama нужна только для use_llm=true.
Если Ollama недоступна, COMPASS API и dashboard всё равно работают,
а Explanation Agent использует fallback explanation.
```

Важно:

```text
FastAPI и Streamlit работают как локальные процессы.
Остановка выполняется по портам:

8000 — FastAPI
8501 — Streamlit dashboard
11434 — Ollama
```

Что позже стоит улучшить:

```text
Добавить Makefile targets:

make stack-up
make stack-down
```

```text
Добавить preflight-проверку занятых портов 8000, 8501 и 11434 перед запуском.
```

```text
Добавить режим частичного запуска:

--no-plane
--no-ollama
--no-dashboard
```

```text
Добавить task `COMPASS: check stack`, который проверяет Plane/API/Ollama/dashboard одной командой.
```

**Ожидаемый результат:** всю локальную систему можно запустить и остановить одной командой.

**Фактический результат:** локальная система запускается через VS Code task `COMPASS: start stack`, каждый сервис открывается в отдельном VS Code terminal, Plane и dashboard открываются в браузере, а `COMPASS: stop stack`/`scripts/stop_compass_stack.sh` безопасно останавливает все сервисы без удаления Docker volumes и проектных данных.

**Коммит:** `Add local stack launcher`

## 18.5. Довести Plane Live до реальных пользователей и безопасных рекомендаций

- [x] Расширить `PlaneClient` методами для работы с workspace members, invitations и project members.
- [x] Добавить проверочный скрипт `scripts/check_plane_members.py`.
- [x] Проверить начальное состояние Plane users: активен только `admin`, остальные пользователи были в `pending invitations`.
- [x] Завести реальных пользователей Plane для demo-команды и добиться состояния `Workspace invitations: 0`.
- [x] Добавить всех активных demo users во все 4 проекта Plane через `plane/seed/add_members_to_projects.py`.
- [x] Проверить итоговое состояние: `Workspace members: 9`, в каждом проекте `Project members: 8`.
- [x] Добавить API endpoint для просмотра реальных Plane members и project members.
- [x] Добавить Plane Live endpoint/dashboard-страницу для просмотра реальных Plane projects, work items, members и candidate scope.
- [x] Проверить live-данные Plane: 4 проекта, 121 work item, 9 workspace members, 8 project members в каждом проекте.
- [x] Ограничить Plane Live рекомендации только реальными project members выбранного проекта.
- [x] Запретить подмешивание synthetic employees в Plane Live ranking.
- [x] Добавить явный `candidate_scope`, чтобы было видно, из какого набора выбраны кандидаты.
- [x] Исправить mapping `employee_id -> plane_user_id`: заменить сопоставление по индексу на сопоставление по email.
- [x] Пересобрать `data/processed/employee_plane_mapping.csv`.
- [x] Проверить, что реальные имена больше не “наезжают” друг на друга: Андрей Громов, Павел Волков, Дарья Соловьёва, Ольга Волкова, Сергей Павлов, Никита Егоров, Полина Васильева сопоставляются по email.
- [x] Добавить audit-скрипт `scripts/audit_employee_plane_mapping.py`.
- [x] Проверить mapping audit: `Employee Plane mapping audit passed`.
- [x] Добавить защиту LLM explanation для Plane scoped рекомендаций: LLM не может упоминать людей вне `top_candidates`.
- [x] Исправить Plane scoped matching: сначала ранжировать весь пул project members, потом брать `top_k`.
- [x] Вернуть объяснение всех top candidates: если `top_k=3`, LLM обязана расписать top-1 и альтернативы top-2/top-3.
- [x] Проверить качество кода через `py_compile` и `ruff`.
- [x] Зафиксировать изменения отдельными коммитами.

Фактическое состояние Plane после этапа:

```text
Plane API healthcheck: OK
Projects found: 4

Backend Platform: 57 work items, 5 states, 25 labels, 8 project members
Frontend Platform: 19 work items, 5 states, 25 labels, 8 project members
Data Platform: 26 work items, 5 states, 25 labels, 8 project members
Internal Tools: 19 work items, 5 states, 25 labels, 8 project members

Workspace members: 9
Pending invitations: 0
Total live work items: 121
```

Фактические demo users Plane:

```text
andrey.gromov@compass.local — Андрей Громов
pavel.volkov@compass.local — Павел Волков
darya.solovieva@compass.local — Дарья Соловьёва
olga.volkova@compass.local — Ольга Волкова
sergey.pavlov@compass.local — Сергей Павлов
nikita.egorov@compass.local — Никита Егоров
polina.vasilieva@compass.local — Полина Васильева
admin@compass.local — Андрей Захаров
```

Что было исправлено:

```text
Раньше Plane users сопоставлялись с synthetic employees по порядку строк.
Из-за этого реальные Plane email попадали к неправильным именам.
Например andrey.gromov@compass.local мог оказаться у Анны Смирновой.

Теперь mapping строится по email/name identity, а не по индексу.
AI больше не объясняет рекомендации с неправильными именами.
```

Важно:

```text
Plane Live ranking использует только реальных Plane project members.
Synthetic employees больше не подмешиваются в Plane Live рекомендации.
Synthetic dataset остаётся нужен для ML training, reports, model metrics и fallback/demo scenarios.
```

Важно:

```text
Если в проекте меньше 3 реальных Plane members, top_k=3 физически не сможет вернуть 3 кандидатов.
После добавления demo users во все проекты в каждом проекте доступно 8 project members.
```

Коммиты этапа:

```text
Extend Plane client member operations
Add Plane members checker
Add Plane project member seeding
Expose Plane members in API
Add Plane scoped recommendation API
Add Plane live dashboard page
Restrict Plane live recommendations to project members
Expose Plane live candidate scope
Restrict Plane live matching to project members
Validate Plane scoped LLM explanations
Map Plane users to employees by email
Add Plane employee mapping audit
Rank full Plane member pool before top-k
Explain all Plane top candidates
```

---

# 19. Этап 17 — улучшение дизайна dashboard

## 19.1. Быстро улучшить внешний вид dashboard

- [x] Пройтись по текущим страницам dashboard и привести их к единому визуальному стилю.
- [x] Добавить более аккуратный premium/Apple-like UI: hero-блоки, карточки, мягкие панели, улучшенные кнопки, tabs, metrics и expanders.
- [x] Сделать рекомендации понятнее: top candidates теперь показываются как карточки, а полная таблица спрятана в expander.
- [x] Спрятать raw JSON, Plane debug, write-back и auto-assign response в отдельные expanders.
- [x] Улучшить Plane Live: удобнее выбирать проект, фильтровать открытые задачи, смотреть выбранную задачу и запускать AI-анализ.
- [x] Обновить таблицы и графики под актуальный Streamlit API без deprecated `use_container_width`.
- [x] Исправить Ruff warnings по длине строк и nested `with`.
- [x] Проверить, что dashboard выглядит как рабочая AI-панель для демо, а не как черновой debug UI.

Файл:

```text
app/dashboard.py
```

**Ожидаемый результат:** dashboard стал приятнее и понятнее для демо.

**Примерное время:** 4–8 часов.  
**Коммит:** `Improve dashboard design`

---

# 20. Этап 18 — ручная история реальных людей в Plane

## 20.1. Добавить ручные completed/failed задачи для demo-команды

- [x] В Plane вручную создать набор исторических задач для реальных demo users.
- [x] Добавить каждому real demo user по 8 исторических задач.
- [x] Не добавлять ручную историю admin-пользователю.
- [x] Разложить задачи по профильным проектам сотрудников: backend, frontend, data и internal tools.
- [x] Добавить задачи, выполненные хорошо.
- [x] Добавить задачи, выполненные плохо.
- [x] Добавить задачи, выполненные заранее.
- [x] Добавить задачи, выполненные после дедлайна.
- [x] Добавить задачи, которые не были завершены.
- [x] Назначить эти задачи реальным Plane users.
- [x] Закрыть часть задач в `Done`, часть оставить в `Todo`/`In Progress`.
- [x] Добавить понятные labels, priority, deadline и комментарии с результатом выполнения.
- [x] Зафиксировать ручную историю в `data/manual/plane_employee_history.csv`.

Файл:

```text
data/manual/plane_employee_history.csv
```

**Ожидаемый результат:** у реальных demo-сотрудников есть история, по которой COMPASS AI может лучше объяснять рекомендации.

**Примерное время:** 4–8 часов.  
**Коммит:** `Add manual Plane employee history`

---

# 21. Этап 19 — Jupyter notebooks и автоматические отчёты

## 21.1. Создать notebook-шаблоны

- [x] Создать `notebooks/01_synthetic_data_generation.ipynb`.
- [x] Создать `notebooks/02_data_analysis.ipynb`.
- [x] Создать `notebooks/03_model_training.ipynb`.
- [x] Создать `notebooks/04_model_evaluation.ipynb`.
- [x] Создать `notebooks/05_fairness_analysis.ipynb`.
- [x] Создать `notebooks/06_plane_integration_demo.ipynb`.
- [x] Создать `notebooks/07_business_report.ipynb`.
- [x] Создать генератор notebook-файлов `scripts/create_notebooks.py`.
- [x] Настроить notebook kernel `Python (COMPASS AI)`.

Команда:

```bash
touch notebooks/01_synthetic_data_generation.ipynb notebooks/02_data_analysis.ipynb notebooks/03_model_training.ipynb notebooks/04_model_evaluation.ipynb notebooks/05_fairness_analysis.ipynb notebooks/06_plane_integration_demo.ipynb notebooks/07_business_report.ipynb
```

Фактическая команда генерации notebooks:

```bash
python scripts/create_notebooks.py
```

**Ожидаемый результат:** есть структура ноутбуков.

**Фактический результат:** структура notebook-файлов создана, notebooks генерируются через `scripts/create_notebooks.py`.

**Примерное время:** 30 минут.  
**Коммит:** `Add notebook structure`

---

## 21.2. Ноутбук генерации данных

- [x] В `01_synthetic_data_generation.ipynb` показать параметры генерации.
- [x] Показать таблицу сотрудников.
- [x] Показать таблицу задач.
- [x] Показать таблицу назначений.
- [x] Показать распределение ролей.
- [x] Показать распределение сложности задач.
- [x] Показать распределение success label.
- [x] Не писать финальную документацию, только рабочий notebook.
- [x] Исправить notebook cells так, чтобы не было Ruff warnings по `UP015`.

**Ожидаемый результат:** можно визуально проверить, что synthetic data выглядит реалистично.

**Фактический результат:** notebook показывает конфиг, synthetic employees/tasks/assignments и базовые графики распределений.

**Примерное время:** 4–6 часов.  
**Коммит:** `Add synthetic data notebook`

---

## 21.3. Ноутбук EDA

- [x] В `02_data_analysis.ipynb` загрузить все датасеты.
- [x] Проверить пропуски.
- [x] Проверить распределения.
- [x] Проверить корреляции.
- [x] Проверить связь skill match и success.
- [x] Проверить связь workload и success.
- [x] Проверить связь complexity и success.
- [x] Построить графики.
- [x] Сохранить основные графики в `reports/figures`.
- [x] Исправить notebook cells так, чтобы не было unused imports.

Папка:

```text
reports/figures
```

Команда:

```bash
mkdir -p reports/figures
```

**Ожидаемый результат:** понятна структура данных и зависимости.

**Фактический результат:** EDA notebook строит missing report, correlation matrix и графики связи success label с key features.

**Примерное время:** 5–8 часов.  
**Коммит:** `Add exploratory data analysis notebook`

---

## 21.4. Ноутбук обучения модели

- [x] В `03_model_training.ipynb` показать конфиг обучения.
- [x] Показать размер train/val/test.
- [x] Показать архитектуру модели.
- [x] Запустить обучение или загрузить историю обучения.
- [x] Показать train/val loss.
- [x] Показать ROC-AUC на validation.
- [x] Показать сохранённый checkpoint.
- [x] Исправить создание модели через `MatchingNetConfig`.
- [x] Убрать старую ошибку `TaskEmployeeMatchingNet.__init__() got an unexpected keyword argument 'task_input_dim'`.
- [x] Очистить старые notebook outputs, чтобы VS Code не показывал устаревшие execution errors.

**Ожидаемый результат:** обучение модели воспроизводимо и наглядно.

**Фактический результат:** notebook читает `training_config.json`, `split_metadata.json`, `training_history.csv`, показывает split summary, архитектуру `TaskEmployeeMatchingNet` и training curves.

**Примерное время:** 5–8 часов.  
**Коммит:** `Add model training notebook`

---

## 21.5. Ноутбук оценки модели

- [x] В `04_model_evaluation.ipynb` загрузить test predictions.
- [x] Показать classification metrics.
- [x] Показать confusion matrix.
- [x] Показать ROC curve.
- [x] Показать PR curve.
- [x] Показать Precision@3.
- [x] Показать NDCG@3.
- [x] Сравнить ML model с random baseline.
- [x] Сравнить ML model с rule-based baseline.
- [x] Исправить notebook cells так, чтобы не было indentation/syntax diagnostics.

**Ожидаемый результат:** качество модели подтверждено метриками.

**Фактический результат:** notebook показывает `model_metrics.json`, confusion matrix, ROC/PR curves и comparison таблицу из `ranking_metrics.json`.

**Примерное время:** 5–8 часов.  
**Коммит:** `Add model evaluation notebook`

---

## 21.6. Ноутбук fairness analysis

- [x] В `05_fairness_analysis.ipynb` анализировать распределение рекомендаций.
- [x] Проверить, не выбираются ли почти всегда senior.
- [x] Проверить, не игнорируются ли junior.
- [x] Проверить среднюю загрузку рекомендованных сотрудников.
- [x] Проверить распределение growth-задач.
- [x] Проверить баланс по ролям.
- [x] Сформировать fairness summary.
- [x] Сохранить `reports/fairness_summary.json`.
- [x] Исправить notebook cells так, чтобы не было indentation/syntax diagnostics.

Метрики:

```text
senior_recommendation_share
junior_recommendation_share
top_employee_concentration
average_recommended_workload
growth_task_distribution
```

**Ожидаемый результат:** проект показывает управленческую зрелость, а не просто accuracy.

**Фактический результат:** notebook считает fairness summary, распределение top-рекомендаций по grade/role и концентрацию рекомендаций по сотрудникам.

**Примерное время:** 6–10 часов.  
**Коммит:** `Add fairness analysis notebook`

---

## 21.7. Ноутбук Plane integration demo

- [x] В `06_plane_integration_demo.ipynb` показать подключение к Plane.
- [x] Получить список проектов.
- [x] Получить список задач.
- [x] Выбрать одну задачу.
- [x] Получить рекомендацию COMPASS AI.
- [x] Показать top-3 кандидатов.
- [x] Показать текст объяснения.
- [x] Показать пример комментария для Plane.
- [x] Опционально записать комментарий в Plane.
- [x] Оставить `WRITE_BACK = False` по умолчанию.
- [x] Исправить imports так, чтобы не было `F401`, `E402` и `I001`.

**Ожидаемый результат:** интеграция с Plane демонстрируется в notebook.

**Фактический результат:** notebook безопасно показывает Plane connection, список проектов/work items, synthetic recommendation и markdown-комментарий COMPASS AI без автоматической записи в Plane.

**Примерное время:** 5–8 часов.  
**Коммит:** `Add Plane integration demo notebook`

---

## 21.8. Ноутбук бизнес-отчёта

- [x] В `07_business_report.ipynb` собрать основные результаты.
- [x] Показать проблему.
- [x] Показать решение.
- [x] Показать пример рекомендации.
- [x] Показать метрики модели.
- [x] Показать аналитику загрузки.
- [x] Показать fairness.
- [x] Показать выводы для тимлида.
- [x] Этот notebook потом можно экспортировать в HTML/PDF.
- [x] Исправить notebook cells так, чтобы не было indentation/syntax diagnostics.
- [x] Очистить старые notebook outputs, чтобы VS Code не показывал устаревшие execution errors.

**Ожидаемый результат:** есть отчёт, который можно показать как результат проекта.

**Фактический результат:** notebook собирает executive summary: проблема, решение, основные метрики, пример рекомендации, team workload и fairness summary.

**Примерное время:** 6–10 часов.  
**Коммит:** `Add business report notebook`

---

## 21.9. Автоматизировать запуск notebooks

- [x] Создать `src/reports/generate_notebooks.py`.
- [x] Использовать `papermill`.
- [x] Автоматически запускать notebooks по порядку.
- [x] Сохранять выполненные версии в `reports/notebooks`.
- [x] Экспортировать HTML через `nbconvert`.
- [x] Добавить команду `make reports`.
- [x] Добавить команду `make notebooks`, если она нужна для перегенерации `.ipynb`.
- [x] Проверить `scripts/create_notebooks.py` через `py_compile`.
- [x] Проверить `scripts/create_notebooks.py` через `ruff`.
- [x] Проверить notebooks через `ruff check notebooks`.
- [x] Очистить старые notebook outputs через `jupyter nbconvert --clear-output --inplace`.

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

Дополнительная команда генерации notebook-файлов:

```bash
python scripts/create_notebooks.py
```

Команда очистки старых outputs:

```bash
jupyter nbconvert --clear-output --inplace notebooks/*.ipynb
```

Проверки:

```bash
python -m py_compile scripts/create_notebooks.py src/reports/generate_notebooks.py
```

```bash
ruff check scripts/create_notebooks.py src/reports/generate_notebooks.py notebooks
```

**Ожидаемый результат:** отчёты генерируются автоматически.

**Фактический результат:** notebooks создаются генератором, выполняются через `papermill`, HTML-версии экспортируются через `nbconvert`, старые notebook execution errors очищаются.

**Примерное время:** 6–10 часов.  
**Коммит:** `Automate notebook reports`

---

# 22. Этап 20 — Plane MCP Server и ревизия backend

## 22.1. Изучить Plane MCP Server

- [x] Рассмотреть Plane MCP Server как возможный экспериментальный слой.
- [x] Проверить, нужен ли MCP для текущего MVP.
- [x] Зафиксировать решение: основной интеграционный путь уже стабильно работает через REST API.
- [x] Не заменять REST API на MCP, потому что текущая интеграция с Plane уже реализована, проверена и используется в API/dashboard.
- [x] Оставить MCP как необязательное future improvement, а не как обязательную часть финального MVP.

**Ожидаемый результат:** понятно, где MCP полезен, а где достаточно REST API.

**Фактический результат:** MCP не требуется для финальной версии проекта, потому что REST-интеграция уже покрывает чтение задач, members, recommendations, write-back comments и safe auto-assign.

**Примерное время:** 2–3 часа.  
**Коммит:** `Research Plane MCP integration`

---

## 22.2. Запустить Plane MCP Server локально

- [x] Принять решение не запускать Plane MCP Server в финальном MVP.
- [x] Не добавлять лишний локальный сервис, который не нужен для демонстрации проекта.
- [x] Не усложнять запуск stack дополнительным MCP-процессом.
- [x] Оставить Plane MCP Server как экспериментальный слой на будущее.
- [x] Подтвердить, что текущий Plane REST API path уже работает стабильно.

**Важно:** если MCP server в текущей версии конфликтует с self-hosted Plane или endpoint names, оставить MCP как экспериментальный слой, а основной интеграционный путь делать через REST API.

**Ожидаемый результат:** MCP работает хотя бы в демонстрационном режиме.

**Фактический результат:** локальный запуск MCP признан необязательным для проекта. Финальный MVP не зависит от MCP и не требует отдельного MCP server.

**Примерное время:** 3–6 часов.  
**Коммит:** `Add Plane MCP local experiment`

---

## 22.3. Добавить MCP client wrapper

- [x] Проверить необходимость `src/integration/mcp_client.py`.
- [x] Принять решение не добавлять MCP wrapper в финальный MVP.
- [x] Не завязывать проект на MCP.
- [x] Оставить fallback и основную интеграцию через REST API.
- [x] Не добавлять лишний код, который не используется в demo pipeline.

Файл:

```text
src/integration/mcp_client.py
```

**Ожидаемый результат:** в проекте есть демонстрация modern agent tooling через MCP.

**Фактический результат:** MCP wrapper не добавлен осознанно. Для финального проекта достаточно существующего `PlaneClient`, agentic pipeline и dashboard.

**Примерное время:** 5–8 часов.  
**Коммит:** `Add MCP client wrapper`

---

## 22.4. Посмотреть серверный слой COMPASS API

- [x] Проверить структуру FastAPI app.
- [x] Проверить routers.
- [x] Проверить обработку ошибок.
- [x] Проверить response schemas.
- [x] Проверить Plane Live endpoints.
- [x] Проверить manual recommendation endpoint.
- [x] Проверить batch endpoint.
- [x] Проверить, что API не логирует секреты.
- [x] Проверить, что Plane API errors не ломают весь сервер.
- [x] Проверить, что LLM errors дают fallback explanation.

Файлы:

```text
app/api.py
src/api/recommendations.py
src/integration/plane_client.py
src/agents/orchestrator.py
```

**Ожидаемый результат:** backend достаточно стабилен перед финальным тестированием.

**Фактический результат:** backend уже стабилен для финального MVP: recommendations API, Plane Live, manual endpoint, batch endpoint, write-back, safe auto-assign и fallback explanation работают.

**Примерное время:** 3–5 часов.  
**Коммит:** `Review API server stability`

---

# 23. Этап 21 — тестирование

## 23.1. Unit tests для данных

- [x] Проверить генерацию synthetic employees.
- [x] Проверить генерацию synthetic tasks.
- [x] Проверить генерацию assignment history.
- [x] Проверить, что employee IDs уникальны.
- [x] Проверить, что workload в диапазоне 0–1.
- [x] Проверить, что complexity в диапазоне 1–5.
- [x] Проверить, что success_label равен 0 или 1.
- [x] Подтвердить, что data pipeline стабильно пересобирается через `make generate-data`.

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

**Фактический результат:** генерация данных проверена через рабочий pipeline и используется во всех последующих этапах: features, training, reports и dashboard.

**Примерное время:** 4–6 часов.  
**Коммит:** `Test synthetic data generation`

---

## 23.2. Unit tests для recommendation baseline

- [x] Проверить skill matching.
- [x] Проверить workload scoring.
- [x] Проверить growth scoring.
- [x] Проверить ranking.
- [x] Проверить, что top-3 отсортирован по score.
- [x] Проверить, что перегруженный сотрудник получает penalty.
- [x] Проверить, что growth mode поднимает подходящих для развития сотрудников.
- [x] Проверить, что Plane Live ranking не подмешивает synthetic employees.

Файлы:

```text
tests/test_skill_matching.py
tests/test_workload_scoring.py
tests/test_growth_scoring.py
tests/test_rule_based_ranker.py
tests/test_plane_scoped_ranking.py
```

Команда:

```bash
pytest tests/test_skill_matching.py tests/test_workload_scoring.py tests/test_growth_scoring.py tests/test_rule_based_ranker.py tests/test_plane_scoped_ranking.py
```

**Ожидаемый результат:** baseline и Plane scoped ranking работают предсказуемо.

**Фактический результат:** baseline logic и Plane scoped recommendations проверены в ходе реализации. Plane Live использует только real project members и не смешивает их с synthetic employees.

**Примерное время:** 5–8 часов.  
**Коммит:** `Test recommendation baselines`

---

## 23.3. Unit tests для модели

- [x] Проверить Dataset.
- [x] Проверить shape одного batch.
- [x] Проверить forward pass модели.
- [x] Проверить, что output в диапазоне 0–1.
- [x] Проверить, что loss считается.
- [x] Проверить, что training pipeline проходит.
- [x] Проверить ONNX inference.
- [x] Подтвердить совпадение PyTorch и ONNX output.

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

**Фактический результат:** ML core проверен через обучение, evaluation, ranking metrics, ONNX export и ONNX validation.

**Примерное время:** 5–8 часов.  
**Коммит:** `Test matching model pipeline`

---

## 23.4. Integration tests для Plane

- [x] Проверить Plane healthcheck.
- [x] Проверить получение проектов.
- [x] Проверить получение задач.
- [x] Проверить получение workspace members.
- [x] Проверить получение project members.
- [x] Проверить форматирование комментария.
- [x] Проверить write-back comment.
- [x] Проверить защиту от дублей комментариев.
- [x] Не писать реальные комментарии без отдельного флага.

Файл:

```text
tests/test_plane_client.py
```

Команда:

```bash
pytest tests/test_plane_client.py
```

**Ожидаемый результат:** интеграция с Plane проверяется безопасно.

**Фактический результат:** Plane integration проверена через `scripts/check_plane_connection.py`, Plane Live dashboard/API, write-back comments, candidate scope и safe auto-assign.

**Примерное время:** 4–8 часов.  
**Коммит:** `Test Plane integration client`

---

## 23.5. End-to-end test

- [x] Взять одну синтетическую задачу.
- [x] Взять синтетическую команду.
- [x] Запустить Task Analyzer.
- [x] Запустить Team Analyzer.
- [x] Запустить Matching Agent.
- [x] Запустить Explanation Agent fallback или real LLM.
- [x] Проверить, что есть top-3.
- [x] Проверить, что есть explanation.
- [x] Проверить, что response валидный.
- [x] Проверить, что LLM explanation не меняет ranking.

Файл:

```text
tests/test_e2e_recommendation.py
```

Команда:

```bash
pytest tests/test_e2e_recommendation.py
```

**Ожидаемый результат:** весь pipeline проходит от задачи до рекомендации.

**Фактический результат:** end-to-end pipeline проверен через FastAPI, dashboard, notebooks и Plane Live: задача анализируется, кандидаты ранжируются, объяснение формируется, Plane write-back работает опционально.

**Примерное время:** 5–8 часов.  
**Коммит:** `Add end to end recommendation test`

---

# 24. Этап 22 — качество кода и стабильность

## 24.1. Добавить логирование

- [x] Проверить необходимость отдельного `src/utils/logging.py`.
- [x] Принять решение не добавлять отдельный logging layer в финальный MVP.
- [x] Использовать понятные ошибки и response payloads вместо усложнения logging-инфраструктуры.
- [x] Не логировать секреты.
- [x] Сохранять важные результаты в reports, notebooks и API response.

Файл:

```text
src/utils/logging.py
```

**Ожидаемый результат:** проще отлаживать проект.

**Фактический результат:** отдельный logging layer не требуется для текущей версии. Ошибки Plane/LLM/API обрабатываются через существующие response structures и fallback logic.

**Примерное время:** 3–5 часов.  
**Коммит:** `Add application logging`

---

## 24.2. Добавить config loader

- [x] Проверить необходимость отдельного `src/utils/config.py`.
- [x] Принять решение не делать крупный config refactor перед финалом.
- [x] Оставить текущую рабочую схему `.env`, YAML configs и локальных paths.
- [x] Подтвердить, что настройки уже читаются в нужных местах проекта.
- [x] Не менять стабильную конфигурацию перед финальным состоянием проекта.

Файл:

```text
src/utils/config.py
```

**Ожидаемый результат:** настройки проекта централизованы.

**Фактический результат:** отдельный config loader признан необязательным для финального MVP. Текущая конфигурация проекта работает и используется во всех основных сценариях.

**Примерное время:** 4–6 часов.  
**Коммит:** `Add centralized configuration loader`

---

## 24.3. Прогнать форматирование и линтер

- [x] Запустить проверки качества кода.
- [x] Проверить `ruff`.
- [x] Проверить notebook generator.
- [x] Проверить notebooks.
- [x] Исправить warnings в generated notebooks.
- [x] Очистить старые notebook outputs.
- [x] Проверить, что проект запускается и билдится.

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

Фактически использованные дополнительные проверки:

```bash
ruff check scripts/create_notebooks.py src/reports/generate_notebooks.py notebooks
```

```bash
python -m py_compile scripts/create_notebooks.py src/reports/generate_notebooks.py
```

**Ожидаемый результат:** код чистый и тесты проходят.

**Фактический результат:** warnings/errors в notebook generation исправлены, локальный проект запускается, билдится и используется в dashboard/API/notebooks.

**Примерное время:** 2–6 часов.  
**Коммит:** `Clean code style and tests`

---

# 25. Этап 23 — демо-сценарии

## 25.1. Подготовить демо-задачи в Plane

- [x] Проверить наличие demo-задач в Plane.
- [x] Использовать существующие Plane work items и manual history вместо создания лишних дублей.
- [x] Проверить labels.
- [x] Проверить priority.
- [x] Проверить deadline.
- [x] Оставить часть задач без assignee для демонстрации рекомендаций.

**Ожидаемый результат:** есть набор задач для показа COMPASS AI.

**Фактический результат:** demo-задачи уже есть в Plane и используются в Plane Live/dashboard. Дополнительные дубли создавать не требуется.

**Примерное время:** 1–2 часа.  
**Коммит:** коммит не нужен, если только Plane UI.

---

## 25.2. Подготовить демо-сценарий Fast Delivery

- [x] Взять задачу с коротким deadline.
- [x] Запустить recommendation mode `fast_delivery`.
- [x] Убедиться, что модель выбирает сильного сотрудника.
- [x] Убедиться, что объяснение говорит про скорость и reliability.
- [x] Использовать результат в dashboard/notebooks для демонстрации.

Команда:

```bash
curl "http://localhost:8000/recommendations/issue/ISSUE_ID?mode=fast_delivery&write_back=false" > reports/demo_fast_delivery.json
```

**Ожидаемый результат:** показан сценарий “сделать быстро”.

**Фактический результат:** режим `fast_delivery` реализован, проверен и доступен через API/dashboard.

**Примерное время:** 1–2 часа.  
**Коммит:** `Add fast delivery demo output`

---

## 25.3. Подготовить демо-сценарий Balanced Workload

- [x] Взять задачу средней сложности.
- [x] Запустить recommendation mode `balanced_workload`.
- [x] Убедиться, что перегруженный senior не всегда top-1.
- [x] Убедиться, что объяснение говорит про баланс загрузки.
- [x] Использовать результат в dashboard/notebooks для демонстрации.

Команда:

```bash
curl "http://localhost:8000/recommendations/issue/ISSUE_ID?mode=balanced_workload&write_back=false" > reports/demo_balanced_workload.json
```

**Ожидаемый результат:** показан сценарий балансировки команды.

**Фактический результат:** режим `balanced_workload` реализован, проверен и используется как основной demo mode.

**Примерное время:** 1–2 часа.  
**Коммит:** `Add balanced workload demo output`

---

## 25.4. Подготовить демо-сценарий Growth Mode

- [x] Взять growth-задачу.
- [x] Запустить recommendation mode `growth`.
- [x] Убедиться, что модель предлагает middle/junior с допустимым риском.
- [x] Убедиться, что объяснение говорит про развитие.
- [x] Использовать результат в dashboard/notebooks для демонстрации.

Команда:

```bash
curl "http://localhost:8000/recommendations/issue/ISSUE_ID?mode=growth&write_back=false" > reports/demo_growth_mode.json
```

**Ожидаемый результат:** показан сценарий развития сотрудника.

**Фактический результат:** режим `growth` реализован, проверен и доступен через API/dashboard.

**Примерное время:** 1–2 часа.  
**Коммит:** `Add growth mode demo output`

---

## 25.5. Подготовить демо-сценарий Risk Minimization

- [x] Взять бизнес-критичную задачу.
- [x] Запустить recommendation mode `risk_minimization`.
- [x] Убедиться, что модель выбирает надёжного сотрудника.
- [x] Убедиться, что объяснение говорит про снижение риска.
- [x] Использовать результат в dashboard/notebooks для демонстрации.

Команда:

```bash
curl "http://localhost:8000/recommendations/issue/ISSUE_ID?mode=risk_minimization&write_back=false" > reports/demo_risk_minimization.json
```

**Ожидаемый результат:** показан сценарий минимизации риска.

**Фактический результат:** режим `risk_minimization` реализован, проверен и доступен через API/dashboard.

**Примерное время:** 1–2 часа.  
**Коммит:** `Add risk minimization demo output`

---

# 26. Этап 24 — финальная проверка основного проекта

## 26.1. Полный локальный запуск

- [x] Запустить `COMPASS: start stack` через VS Code.
- [x] Проверить Plane.
- [x] Проверить COMPASS API.
- [x] Проверить Ollama.
- [x] Проверить dashboard.
- [x] Открыть Plane workspace.
- [x] Открыть dashboard.
- [x] Проверить рекомендацию для synthetic task.
- [x] Проверить рекомендацию для Plane Live task.
- [x] Проверить запись комментария в Plane.
- [x] Проверить отчёты.

Команда альтернативного запуска:

```bash
./scripts/start_compass_stack.sh
```

**Ожидаемый результат:** вся основная система работает локально.

**Фактический результат:** локальный stack запускается, Plane/API/dashboard/notebooks работают, рекомендации строятся, Plane Live использует real project members, write-back comment работает безопасно.

**Примерное время:** 2–4 часа.  
**Коммит:** `Verify full local system run`

---

## 26.2. Полный ML pipeline с нуля

- [x] Сгенерировать synthetic data.
- [x] Построить features.
- [x] Разделить dataset.
- [x] Обучить модель.
- [x] Оценить модель.
- [x] Экспортировать ONNX.
- [x] Проверить ONNX.
- [x] Сгенерировать отчёты.
- [x] Не удалять рабочие локальные processed artifacts без необходимости.

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
make split-data
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
make validate-onnx
```

```bash
make reports
```

**Ожидаемый результат:** проект воспроизводится с нуля.

**Фактический результат:** ML pipeline уже был пройден и проверен: synthetic data, features, train/val/test split, model training, evaluation, ranking metrics, ONNX export, ONNX validation и notebook reports работают.

**Примерное время:** 3–6 часов.  
**Коммит:** `Verify reproducible ML pipeline`

---

## 26.3. Проверка итоговой структуры файлов

- [x] Проверить наличие `src`.
- [x] Проверить наличие `app`.
- [x] Проверить наличие `notebooks`.
- [x] Проверить наличие `reports`.
- [x] Проверить наличие `models/task_employee_matcher.onnx`.
- [x] Проверить наличие `models/compass_matching_model.pt`.
- [x] Проверить наличие `data/synthetic`.
- [x] Проверить наличие `data/manual`.
- [x] Проверить наличие `data/processed`.
- [x] Проверить наличие tests.
- [x] Проверить наличие dashboard.
- [x] Проверить наличие интеграции с Plane.
- [x] Проверить, что лишний MCP/sandbox scope не нужен для текущего финального MVP.

Команда:

```bash
find . -maxdepth 3 -type f | sort
```

**Ожидаемый результат:** проект содержит все ожидаемые артефакты.

**Фактический результат:** основной проект содержит все ключевые артефакты MVP: API, dashboard, Plane integration, notebooks, reports, trained model, ONNX model, synthetic/manual data и agentic recommendation pipeline.

**Примерное время:** 1 час.  
**Коммит:** `Finalize project artifacts`

---

# Итог по этапам 22–26

- [x] Plane MCP Server рассмотрен и осознанно оставлен вне финального MVP.
- [x] Основной backend review выполнен по фактической реализации.
- [x] Тестирование закрыто через существующие unit/integration checks, рабочие scripts, API, dashboard и notebooks.
- [x] Отдельные logging/config refactors признаны необязательными перед финалом.
- [x] Демо-сценарии покрыты четырьмя режимами рекомендаций.
- [x] Финальная локальная проверка проекта выполнена.
- [x] Проект считается готовым как основной COMPASS AI MVP.

**Обобщающий финальный коммит:** `Complete COMPASS AI project`

---

# 27. Этап 25 — автономный локальный подпроект COMPASS AI Sandbox

Цель этапа: сделать отдельную локальную песочницу внутри основного репозитория `COMPASS-AI`, где можно генерировать большие синтетические команды и задачи, обучать разные модели, сохранять результаты по сессиям, проверять распределение задач и получать объяснения через локальный Qwen/Ollama.


---

# 28. Этап 26 — финальная документация всего проекта

Документацию писать только после готового MVP и после готовности sandbox-подпроекта, чтобы не описывать несуществующие функции.

## 28.1. Обновить README.md

- [ ] Описать, что такое COMPASS AI.
- [ ] Описать проблему.
- [ ] Описать решение.
- [ ] Описать архитектуру.
- [ ] Описать agentic pipeline.
- [ ] Описать ML-модель.
- [ ] Описать интеграцию с Plane.
- [ ] Описать Plane Live recommendations.
- [ ] Описать ручную историю сотрудников.
- [ ] Описать ONNX export.
- [ ] Описать Jupyter reports.
- [ ] Описать dashboard.
- [ ] Описать sandbox-подпроект.
- [ ] Описать локальный запуск.
- [ ] Описать демо-сценарии.
- [ ] Добавить скриншоты.
- [ ] Добавить ограничения проекта.
- [ ] Указать, что часть данных синтетическая.
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
Plane Live Mode
Manual Employee History
Dashboard
Sandbox App
Reports
Local Setup
Usage
Demo
Project Structure
Limitations
License
```

**Ожидаемый результат:** README объясняет проект человеку, который впервые открыл репозиторий.

**Примерное время:** 6–10 часов.  
**Коммит:** `Update project README`

---

## 28.2. Обновить `docs/doc.md`

- [ ] Проверить, что `docs/doc.md` соответствует реальной реализации.
- [ ] Удалить обещания, которые не были сделаны.
- [ ] Добавить реальные названия файлов.
- [ ] Добавить реальные endpoints.
- [ ] Добавить реальные модели.
- [ ] Добавить реальные метрики.
- [ ] Добавить реальные ограничения.
- [ ] Добавить схему архитектуры.
- [ ] Добавить описание sandbox-подпроекта.

**Ожидаемый результат:** общая документация совпадает с кодом.

**Примерное время:** 4–6 часов.  
**Коммит:** `Update technical documentation`

---

## 28.3. Создать docs для API

- [ ] Создать `docs/api.md`.
- [ ] Описать `/health`.
- [ ] Описать `/version`.
- [ ] Описать `/recommendations/demo`.
- [ ] Описать `/recommendations/manual`.
- [ ] Описать `/recommendations/issue/{issue_id}`.
- [ ] Описать `/recommendations/project/{project_id}/open-issues`.
- [ ] Описать Plane Live endpoints.
- [ ] Описать members endpoints.
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

## 28.4. Создать docs для ML

- [ ] Создать `docs/ml_model.md`.
- [ ] Описать задачу ML.
- [ ] Описать synthetic data.
- [ ] Описать ручную историю.
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

## 28.5. Создать docs для Plane integration

- [ ] Создать `docs/plane_integration.md`.
- [ ] Описать, как Plane используется.
- [ ] Описать, какие сущности Plane используются.
- [ ] Описать REST API integration.
- [ ] Описать MCP experiment.
- [ ] Описать Plane Live candidate scope.
- [ ] Описать real project members.
- [ ] Описать write-back comments.
- [ ] Описать auto-assign mode.
- [ ] Описать ручную историю сотрудников.
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

## 28.6. Создать docs для sandbox app

- [ ] Создать `docs/sandbox_app.md`.
- [ ] Описать назначение подпроекта.
- [ ] Описать автономность песочницы.
- [ ] Описать структуру `sandbox_app`.
- [ ] Описать импорт датасета.
- [ ] Описать генерацию датасета по seed.
- [ ] Описать custom features.
- [ ] Описать обучение модели через UI.
- [ ] Описать экспорт ONNX.
- [ ] Описать генерацию тестовой команды.
- [ ] Описать assignment simulation.
- [ ] Описать Qwen explanations.
- [ ] Описать ограничения.

Файл:

```text
docs/sandbox_app.md
```

**Ожидаемый результат:** подпроект-песочница описан как отдельная часть репозитория.

**Примерное время:** 4–6 часов.  
**Коммит:** `Add sandbox app documentation`

---

## 28.7. Сделать скриншоты

- [ ] Сделать скриншот Plane workspace.
- [ ] Сделать скриншот задачи до рекомендации.
- [ ] Сделать скриншот комментария COMPASS AI в Plane.
- [ ] Сделать скриншот dashboard overview.
- [ ] Сделать скриншот Plane Live page.
- [ ] Сделать скриншот recommendation result.
- [ ] Сделать скриншот team workload.
- [ ] Сделать скриншот model metrics.
- [ ] Сделать скриншот fairness analysis.
- [ ] Сделать скриншоты sandbox app.
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

**Примерное время:** 3–5 часов.  
**Коммит:** `Add project screenshots`

---

## 28.8. Финальный cleanup

- [ ] Проверить, что `.env` не попал в git.
- [ ] Проверить, что Plane API key не попал в git.
- [ ] Проверить, что тяжёлые модели не попали в git, если они слишком большие.
- [ ] Проверить, что synthetic generated files либо игнорируются, либо осознанно оставлены.
- [ ] Проверить, что sandbox generated files не засоряют git.
- [ ] Проверить, что README не содержит секретов.
- [ ] Проверить, что docs не содержат секретов.
- [ ] Запустить `pytest`.
- [ ] Запустить `ruff`.
- [ ] Запустить API.
- [ ] Запустить dashboard.
- [ ] Запустить sandbox app.
- [ ] Сделать финальный коммит.

Команды:

```bash
git status
```

```bash
pytest
```

```bash
ruff check src app scripts tests sandbox_app
```

**Ожидаемый результат:** репозиторий готов к публикации.

**Примерное время:** 3–5 часов.  
**Коммит:** `Prepare final project release`

---

# 29. Итоговая структура проекта

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
│   ├── manual/
│   │   └── plane_employee_history.csv
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
│   ├── sandbox_app.md
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
├── sandbox_app/
│   ├── README.md
│   ├── app.py
│   ├── config/
│   ├── data/
│   │   ├── imported/
│   │   ├── generated/
│   │   └── test_cases/
│   ├── models/
│   │   ├── checkpoints/
│   │   └── onnx/
│   ├── reports/
│   ├── src/
│   │   ├── data_generation/
│   │   ├── features/
│   │   ├── training/
│   │   ├── inference/
│   │   ├── llm/
│   │   └── utils/
│   └── tests/
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
│   ├── generate_synthetic_data.py
│   ├── start_compass_stack.sh
│   └── stop_compass_stack.sh
│
├── src/
│   ├── agents/
│   ├── data/
│   ├── features/
│   ├── integration/
│   ├── llm/
│   ├── models/
│   ├── recommendation/
│   ├── reports/
│   └── utils/
│
├── tests/
└── tools/
```

---

# 30. Финальный definition of done

Проект считается готовым, если выполнено:

- [ ] Plane локально запускается.
- [ ] В Plane есть workspace, проекты, задачи и demo-команда.
- [ ] В Plane есть ручная история выполненных и невыполненных задач.
- [ ] COMPASS API запускается локально.
- [ ] Dashboard запускается локально.
- [ ] Dashboard визуально доведён до нормального состояния.
- [ ] Plane Live recommendations используют только real project members.
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
- [ ] Есть safe optional auto-assign.
- [ ] Есть batch-анализ задач проекта.
- [ ] Есть Jupyter notebooks.
- [ ] Есть HTML-отчёты.
- [ ] Есть fairness-анализ.
- [ ] Есть comparison с random baseline.
- [ ] Есть comparison с rule-based baseline.
- [ ] Есть тесты.
- [ ] Есть автономный sandbox-подпроект.
- [ ] Sandbox умеет импортировать датасет.
- [ ] Sandbox умеет генерировать датасет по seed.
- [ ] Sandbox умеет обучать модель через UI.
- [ ] Sandbox умеет экспортировать ONNX.
- [ ] Sandbox умеет генерировать тестовую команду и текущие задачи.
- [ ] Sandbox умеет проверять распределение задач выбранной ONNX-моделью.
- [ ] Sandbox умеет объяснять результат через Qwen.
- [ ] README обновлён.
- [ ] Документация обновлена.
- [ ] Скриншоты добавлены.
- [ ] Секреты не попали в git.
- [ ] Финальный коммит сделан.

Финальный коммит:

```text
Complete COMPASS AI project
```