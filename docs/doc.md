# COMPASS AI

**COMPASS** — **Competency-Oriented Matching & Project Assignment Support System**

**COMPASS AI** — система интеллектуального назначения задач по компетенциям, загрузке и целям развития сотрудников.

Проект разрабатывается как учебный ML/AI-проект с синтетическими данными, собственной обучаемой нейронной сетью, экспортом модели в ONNX, Jupyter-отчётами и интеграцией с готовой project management-системой Plane.

---

## 1. Цель проекта

COMPASS AI помогает тимлиду выбрать оптимального исполнителя для задачи.

Система анализирует:

- описание задачи;
- стек технологий;
- сложность;
- дедлайн;
- бизнес-критичность;
- навыки сотрудников;
- опыт сотрудников;
- текущую загрузку;
- историю выполнения похожих задач;
- цели развития сотрудника.

На выходе система выдаёт:

- топ-3 рекомендуемых исполнителей;
- score пригодности;
- объяснение рекомендации на русском языке;
- альтернативные стратегии назначения:
  - `быстрее выполнить`;
  - `сбалансировать нагрузку`;
  - `дать сотруднику развивающую задачу`;
  - `снизить риск срыва дедлайна`.

---

## 2. Базовый сценарий работы

1. Тимлид работает в Plane.
2. В Plane создаётся новая задача.
3. COMPASS AI получает данные о задаче и команде.
4. Нейронная модель считает score для каждой пары `задача — сотрудник`.
5. Система ранжирует сотрудников.
6. LLM-модуль формирует краткое объяснение на русском языке.
7. Тимлид получает рекомендацию:
   - кого назначить;
   - почему именно его;
   - какие есть риски;
   - кому можно дать задачу для развития.

---

## 3. Используемая система управления задачами

Используем **Plane**.

Plane — open-source project management tool для работы с issues, cycles, modules и roadmap. Его можно использовать как учебную замену Jira/Linear. Также существует Plane MCP Server, который позволяет AI-инструментам взаимодействовать с Plane через Model Context Protocol. Источники: GitHub Plane и Plane MCP Server.  

В проекте Plane используется как готовая среда, где хранятся:

- проекты;
- задачи;
- статусы;
- исполнители;
- циклы;
- приоритеты;
- дедлайны.

Своё отдельное приложение для ручного создания задач не разрабатывается.

---

## 4. Архитектура проекта

```text
COMPASS AI
│
├── Plane
│   ├── задачи
│   ├── сотрудники
│   ├── проекты
│   └── статусы
│
├── Integration Layer
│   ├── Plane REST API
│   └── Plane MCP Server
│
├── Synthetic Data Generator
│   ├── сотрудники
│   ├── навыки
│   ├── задачи
│   ├── история назначений
│   └── результаты выполнения
│
├── ML Core
│   ├── task encoder
│   ├── employee encoder
│   ├── matching neural network
│   └── ranking module
│
├── LLM Explanation Layer
│   ├── генерация объяснения
│   ├── формирование рекомендаций
│   └── русскоязычный ответ
│
├── Reports
│   ├── Jupyter notebooks
│   ├── метрики модели
│   ├── fairness-анализ
│   └── аналитика загрузки команды
│
└── Export
    ├── PyTorch model
    └── ONNX model
```

---

## 5. Что именно обучаем сами

Главная модель проекта — собственная нейронная сеть для matching-задачи.

Она обучается предсказывать вероятность успешного назначения задачи конкретному сотруднику.

Формально:

```text
input: task_features + employee_features
output: success_score
```

Где `success_score` — вероятность, что сотрудник:

- выполнит задачу вовремя;
- выполнит задачу качественно;
- не будет перегружен;
- соответствует стеку задачи;
- получит полезный опыт.

---

## 6. Основная ML-модель

### Название модели

```text
TaskEmployeeMatchingNet
```

### Тип модели

Нейронная matching-модель на PyTorch.

### Входы модели

#### Признаки задачи

```text
task_type
task_complexity
task_priority
deadline_days
business_criticality
required_skills
required_stack
estimated_hours
dependencies_count
task_text_embedding
```

#### Признаки сотрудника

```text
employee_role
experience_years
current_workload
skill_vector
stack_vector
avg_completion_speed
avg_quality_score
deadline_reliability
learning_goals
development_vector
```

### Выходы модели

```text
success_probability
speed_score
quality_score
learning_score
overload_risk
final_matching_score
```

---

## 7. Архитектура нейронной сети

```text
Task Encoder:
task numeric features + task skill vector + task text embedding
→ Dense layers
→ task_embedding

Employee Encoder:
employee numeric features + employee skill vector + development vector
→ Dense layers
→ employee_embedding

Matching Block:
task_embedding + employee_embedding + abs(task - employee) + task * employee
→ MLP
→ final scores
```

### Пример

```text
Task:
"Сделать авторизацию через JWT"
stack: Python, FastAPI, PostgreSQL
complexity: 3/5
deadline: 4 days

Employee A:
Python: high
FastAPI: high
PostgreSQL: medium
current_workload: 40%

Employee B:
Python: medium
FastAPI: low
PostgreSQL: high
current_workload: 20%

Model result:
1. Employee A — 0.87
2. Employee B — 0.61
```

---

## 8. Дополнительные модели

### 8.1. Text Embedding Model

Используется для превращения русского описания задачи в вектор.

Модель:

```text
sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
```

Почему она подходит:

- бесплатная;
- доступна через Hugging Face;
- понимает русский язык;
- лёгкая;
- подходит для MacBook M2;
- хорошо подходит для semantic similarity.

Использование:

```text
"Добавить фильтрацию задач по статусу"
→ text embedding vector
```

Эта модель не является главной обучаемой моделью проекта. Она используется как готовый encoder для текста.

---

### 8.2. LLM для объяснений на русском языке

Используется локальная или бесплатная open-source LLM.

Варианты:

```text
Qwen2.5-1.5B-Instruct
Qwen2.5-3B-Instruct
Saiga/Mistral-based русскоязычная модель
```

Рекомендуемый вариант для MacBook M2:

```text
Qwen2.5-1.5B-Instruct
```

Задача LLM:

- не принимать решение;
- не обучаться;
- только объяснять результат основной модели;
- формировать русскоязычный текст для тимлида.

Пример входа в LLM:

```text
Task: Добавить JWT-авторизацию
Top candidates:
1. Иван — score 0.87, высокая экспертиза FastAPI, загрузка 40%
2. Анна — score 0.74, средняя экспертиза, загрузка 25%, хорошая задача для развития
3. Олег — score 0.68, высокая загрузка 80%

Explain recommendation in Russian.
```

Пример выхода:

```text
Рекомендуется назначить задачу Ивану, так как у него высокая экспертиза в FastAPI и Python, а текущая загрузка остаётся допустимой. Если цель — развитие сотрудника, альтернативно можно назначить задачу Анне, но потребуется ревью от более опытного разработчика.
```

---

## 9. Агентная схема

Проект можно оформить как простую multi-agent-систему.

### Agent 1 — Task Analyzer

Отвечает за анализ задачи.

Функции:

- читает описание задачи;
- выделяет стек;
- определяет сложность;
- определяет требуемые навыки;
- формирует task features.

---

### Agent 2 — Team State Analyzer

Отвечает за состояние команды.

Функции:

- анализирует загрузку сотрудников;
- смотрит опыт;
- смотрит навыки;
- смотрит историю выполнения задач;
- формирует employee features.

---

### Agent 3 — Matching Model Agent

Отвечает за ML-прогноз.

Функции:

- вызывает обученную нейронную сеть;
- считает score для каждого сотрудника;
- ранжирует кандидатов;
- отдаёт топ-3.

---

### Agent 4 — Explanation Agent

Отвечает за объяснение результата.

Функции:

- получает топ кандидатов;
- получает факторы решения;
- формирует объяснение на русском языке;
- предлагает разные стратегии назначения.

---

### Agent 5 — Plane Integration Agent

Отвечает за связь с Plane.

Функции:

- получает задачи из Plane;
- получает список сотрудников;
- отправляет рекомендацию;
- при необходимости создаёт комментарий к задаче.

---

## 10. Интеграция с Plane

### Вариант 1 — через Plane REST API

Используется для:

- получения задач;
- получения проектов;
- получения пользователей;
- чтения статусов;
- обновления задачи;
- добавления комментариев.

Пример логики:

```text
1. Получить новую задачу из Plane.
2. Получить список участников проекта.
3. Передать данные в COMPASS AI.
4. Получить рекомендацию.
5. Добавить комментарий в задачу:
   "COMPASS AI рекомендует назначить задачу Ивану..."
```

---

### Вариант 2 — через Plane MCP Server

Используется для AI-интеграции.

Plane MCP Server предоставляет интерфейс, через который AI-агенты могут взаимодействовать с Plane.

В проекте MCP можно использовать как демонстрационный слой:

```text
AI Agent → Plane MCP Server → Plane
```

Пример команды:

```text
"Проанализируй новые задачи в проекте Backend и предложи исполнителей"
```

Результат:

```text
COMPASS AI получает задачи из Plane, запускает matching-модель и возвращает рекомендации.
```

---

## 11. Синтетические данные

Так как проект учебный, реальные HR-данные не используются.

Генерируются синтетические данные:

### Employees

```text
employee_id
name
role
grade
experience_years
skills
stack
current_workload
avg_speed
avg_quality
deadline_reliability
learning_goals
```

### Tasks

```text
task_id
title
description
type
complexity
priority
required_skills
required_stack
deadline_days
estimated_hours
business_criticality
```

### Assignments History

```text
task_id
employee_id
assigned_at
completed_on_time
actual_hours
quality_score
reopened_count
manager_rating
success_label
```

---

## 12. Как формируется label для обучения

Модель обучается на исторических назначениях.

Целевая переменная:

```text
success_label
```

Пример правила генерации:

```text
success_label = 1, если:
- задача выполнена вовремя;
- quality_score >= 0.75;
- actual_hours <= estimated_hours * 1.3;
- сотрудник не был перегружен.

success_label = 0, если:
- задача просрочена;
- качество низкое;
- сотрудник был перегружен;
- задача переоткрывалась много раз.
```

---

## 13. Режимы рекомендации

COMPASS AI поддерживает несколько стратегий.

### 13.1. Fast Delivery Mode

Цель — выполнить задачу максимально быстро.

Приоритет:

```text
speed_score
deadline_reliability
skill_match
low_risk
```

---

### 13.2. Balanced Workload Mode

Цель — не перегружать сильных сотрудников.

Приоритет:

```text
current_workload
fairness_score
team_balance
```

---

### 13.3. Growth Mode

Цель — дать сотруднику задачу для развития.

Приоритет:

```text
learning_score
partial_skill_match
mentor_available
acceptable_risk
```

---

### 13.4. Risk Minimization Mode

Цель — снизить риск провала задачи.

Приоритет:

```text
quality_score
experience
deadline_reliability
low_overload_risk
```

---

## 14. Выход системы

Пример результата:

```text
Task: "Добавить JWT-авторизацию"

Recommended assignee:
Иван Петров

Score:
0.87

Reason:
Иван имеет высокий уровень Python и FastAPI, уже выполнял похожие задачи и имеет умеренную загрузку 40%.

Alternatives:
1. Анна Смирнова — 0.74
   Хороший вариант для развития, но потребуется code review.

2. Олег Кузнецов — 0.68
   Технически подходит, но имеет высокую загрузку 80%.

Recommendation mode:
Fast Delivery
```

---

## 15. Jupyter Notebooks

В проекте автоматически генерируются ноутбуки.

```text
notebooks/
├── 01_synthetic_data_generation.ipynb
├── 02_data_analysis.ipynb
├── 03_model_training.ipynb
├── 04_model_evaluation.ipynb
├── 05_fairness_analysis.ipynb
├── 06_plane_integration_demo.ipynb
└── 07_business_report.ipynb
```

---

## 16. Что анализируется в отчётах

### Model Evaluation

```text
accuracy
precision
recall
F1-score
ROC-AUC
NDCG@3
Precision@3
```

---

### Recommendation Quality

```text
сравнение с random assignment
сравнение с rule-based baseline
качество top-3 рекомендаций
ошибки модели
```

---

### Workload Analytics

```text
загрузка сотрудников
перегруженные сотрудники
недозагруженные сотрудники
распределение задач по ролям
```

---

### Fairness Analysis

```text
не назначает ли модель все задачи одному senior-разработчику
не игнорирует ли junior-разработчиков
равномерность распределения задач
баланс между эффективностью и развитием
```

---

## 17. Экспорт модели

После обучения модель экспортируется в ONNX.

```text
models/
├── compass_matching_model.pt
└── task_employee_matcher.onnx
```

ONNX нужен для:

- независимого запуска модели;
- использования в API;
- демонстрации production-ready подхода;
- запуска через ONNX Runtime.

---

## 18. Технологический стек

### Язык

```text
Python 3.11+
```

### ML

```text
PyTorch
scikit-learn
pandas
numpy
sentence-transformers
onnx
onnxruntime
```

### Отчёты

```text
Jupyter Notebook
matplotlib
plotly
papermill
nbconvert
```

### Интеграция

```text
Plane
Plane REST API
Plane MCP Server
FastAPI
requests/httpx
```

### LLM

```text
Ollama или llama.cpp
Qwen2.5-1.5B-Instruct
Qwen2.5-3B-Instruct
```

### Локальный запуск

```text
MacBook M2
CPU/MPS
Docker
```

---

## 19. Структура проекта

```text
compass-ai/
├── README.md
├── docker-compose.yml
├── requirements.txt
├── .env.example
│
├── data/
│   ├── raw/
│   ├── synthetic/
│   └── processed/
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
├── src/
│   ├── data/
│   │   ├── generate_synthetic_data.py
│   │   └── preprocess.py
│   │
│   ├── models/
│   │   ├── matching_net.py
│   │   ├── train.py
│   │   ├── evaluate.py
│   │   └── export_onnx.py
│   │
│   ├── agents/
│   │   ├── task_analyzer.py
│   │   ├── team_analyzer.py
│   │   ├── matching_agent.py
│   │   ├── explanation_agent.py
│   │   └── plane_agent.py
│   │
│   ├── integration/
│   │   ├── plane_client.py
│   │   └── mcp_client.py
│   │
│   └── reports/
│       └── generate_reports.py
│
├── models/
│   ├── compass_matching_model.pt
│   └── task_employee_matcher.onnx
│
├── reports/
│   ├── model_metrics.html
│   ├── fairness_report.html
│   └── business_report.html
│
└── app/
    └── api.py
```

---

## 20. Минимальный MVP

MVP должен включать:

1. Генерацию синтетических сотрудников.
2. Генерацию синтетических задач.
3. Генерацию истории назначений.
4. Обучение собственной PyTorch-модели.
5. Ранжирование сотрудников под новую задачу.
6. Экспорт модели в ONNX.
7. Jupyter-отчёты с метриками.
8. Простую интеграцию с Plane:
   - получить задачу;
   - получить команду;
   - вернуть рекомендацию;
   - добавить комментарий к задаче.
9. Русскоязычное объяснение через LLM.

---

## 21. Что будет считаться результатом проекта

Финальный результат:

```text
COMPASS AI — working prototype
```

Система должна уметь:

- брать задачу из Plane;
- анализировать описание задачи;
- сравнивать задачу с профилями сотрудников;
- предсказывать лучшего исполнителя;
- объяснять решение на русском языке;
- показывать top-3 кандидатов;
- экспортировать модель в ONNX;
- генерировать Jupyter-отчёты;
- демонстрировать качество модели на синтетических данных.

---

## 22. Пример финальной рекомендации

```text
Задача:
"Реализовать API для экспорта отчётов в PDF"

Режим:
Balanced Workload

Рекомендация COMPASS AI:

1. Анна Смирнова — score 0.82
   Причина: хороший опыт с FastAPI и отчётами, текущая загрузка 45%, похожие задачи выполнялись успешно.

2. Иван Петров — score 0.79
   Причина: технически самый сильный кандидат, но текущая загрузка 85%, поэтому есть риск перегруза.

3. Максим Орлов — score 0.71
   Причина: подходит как growth-вариант, но потребуется ревью от senior-разработчика.

Итог:
Назначить Анну Смирнову.
```

---

## 23. Краткая формулировка проекта

COMPASS AI — учебный AI/ML-проект, в котором разрабатывается собственная нейронная matching-модель для интеллектуального назначения задач сотрудникам. Система интегрируется с Plane, использует синтетические данные, экспортирует модель в ONNX, генерирует Jupyter-отчёты и объясняет рекомендации на русском языке с помощью локальной open-source LLM.

---