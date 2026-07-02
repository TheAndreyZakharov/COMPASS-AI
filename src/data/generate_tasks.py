from __future__ import annotations

import json
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SYNTHETIC_SCHEMA_PATH = PROJECT_ROOT / "config" / "synthetic_schema.yaml"
SYNTHETIC_DATA_CONFIG_PATH = PROJECT_ROOT / "config" / "synthetic_data.yaml"


TASK_TEMPLATES: dict[str, list[tuple[str, str]]] = {
    "backend_feature": [
        (
            "Реализовать JWT-авторизацию",
            (
                "Добавить login endpoint, refresh token flow, logout сценарий "
                "и защиту приватных endpoint-ов."
            ),
        ),
        (
            "Добавить endpoint для статистики команды",
            (
                "Реализовать backend endpoint, который возвращает агрегированную "
                "статистику по задачам и загрузке команды."
            ),
        ),
        (
            "Добавить фильтрацию задач по статусу",
            "Расширить API задач фильтрами по статусу, приоритету и исполнителю.",
        ),
    ],
    "frontend_feature": [
        (
            "Добавить страницу командной загрузки",
            (
                "Сделать UI-страницу с таблицей сотрудников, текущей загрузкой "
                "и индикаторами риска."
            ),
        ),
        (
            "Реализовать фильтр задач на dashboard",
            "Добавить фильтры по проекту, статусу, приоритету и recommended assignee.",
        ),
        (
            "Добавить карточку рекомендации исполнителя",
            "Показать top-3 кандидатов, score и краткое объяснение на странице задачи.",
        ),
    ],
    "bugfix": [
        (
            "Починить ошибку при смене assignee",
            (
                "Исправить сценарий, при котором задача может потерять исполнителя "
                "после обновления статуса."
            ),
        ),
        (
            "Исправить падение API при пустом описании задачи",
            (
                "Добавить корректную обработку задач без description и покрыть "
                "сценарий тестом."
            ),
        ),
        (
            "Починить некорректный расчёт дедлайна",
            (
                "Исправить расчёт deadline_days для задач без target date "
                "и задач с просроченным сроком."
            ),
        ),
    ],
    "refactoring": [
        (
            "Упростить слой интеграции с Plane",
            (
                "Разделить API-клиент, mapping и форматирование комментариев "
                "по отдельным модулям."
            ),
        ),
        (
            "Рефакторинг расчёта recommendation score",
            "Выделить отдельные функции для skill, workload, growth и risk score.",
        ),
        (
            "Разделить генератор данных на независимые шаги",
            (
                "Сделать генерацию сотрудников, задач и назначений независимой "
                "и воспроизводимой."
            ),
        ),
    ],
    "database_migration": [
        (
            "Добавить таблицу истории назначений",
            (
                "Подготовить структуру для хранения task_id, employee_id, outcome "
                "и quality metrics."
            ),
        ),
        (
            "Оптимизировать SQL-запросы в отчётах",
            "Переписать тяжёлые запросы аналитики и добавить индексы для ускорения отчётов.",
        ),
        (
            "Добавить миграцию для хранения model scores",
            "Сохранять score модели, режим рекомендации и дату расчёта.",
        ),
    ],
    "api_integration": [
        (
            "Подключить чтение work items из Plane",
            (
                "Получить список задач проекта через Plane API и привести ответ "
                "к внутреннему формату COMPASS AI."
            ),
        ),
        (
            "Добавить запись комментария COMPASS AI в Plane",
            (
                "Подготовить интеграционный метод для безопасной записи "
                "Markdown-комментария к задаче."
            ),
        ),
        (
            "Добавить проверку Plane API token",
            "Сделать понятную диагностику ошибок авторизации и недоступности Plane API.",
        ),
    ],
    "ml_pipeline": [
        (
            "Собрать датасет пар задача-сотрудник",
            (
                "Построить training_pairs.parquet с task features, employee features, "
                "pair features и success_label."
            ),
        ),
        (
            "Добавить text embeddings для описаний задач",
            (
                "Использовать multilingual sentence-transformer для векторизации "
                "title и description."
            ),
        ),
        (
            "Реализовать baseline для сравнения с нейросетью",
            "Собрать rule-based ranking, чтобы сравнивать ML-модель с понятной эвристикой.",
        ),
    ],
    "analytics_report": [
        (
            "Добавить экспорт аналитики в CSV",
            "Сформировать CSV-отчёт по задачам, рекомендациям, загрузке и рискам.",
        ),
        (
            "Собрать отчёт по fairness рекомендаций",
            (
                "Проверить, не выбираются ли почти всегда senior и не игнорируются "
                "ли junior сотрудники."
            ),
        ),
        (
            "Добавить график распределения workload",
            "Построить график текущей загрузки команды и выделить перегруженных сотрудников.",
        ),
    ],
    "devops_task": [
        (
            "Настроить Docker Compose для dev-окружения",
            (
                "Подготовить локальный запуск сервисов COMPASS AI рядом "
                "с self-hosted Plane."
            ),
        ),
        (
            "Добавить healthcheck для COMPASS API",
            "Настроить endpoint и проверку доступности backend-сервиса.",
        ),
        (
            "Настроить CI-проверку линтера и тестов",
            "Добавить команды проверки кода и тестов для автоматического контроля качества.",
        ),
    ],
    "testing_task": [
        (
            "Добавить тесты генерации сотрудников",
            (
                "Проверить уникальность employee_id, диапазоны workload "
                "и корректные уровни skills."
            ),
        ),
        (
            "Добавить тесты rule-based ranker",
            "Проверить сортировку top-3, penalty за перегруз и growth mode.",
        ),
        (
            "Добавить integration test PlaneClient",
            "Проверить чтение проектов и задач, если задан PLANE_API_KEY.",
        ),
    ],
    "security_task": [
        (
            "Проверить отсутствие секретов в логах",
            "Убедиться, что API tokens и .env значения не печатаются в stdout и reports.",
        ),
        (
            "Добавить безопасную обработку API token",
            "Проверить, что Plane API token берётся из .env и не сохраняется в git.",
        ),
        (
            "Провести ревизию auto-assignment",
            (
                "Убедиться, что автоматическое назначение выключено по умолчанию "
                "и требует threshold."
            ),
        ),
    ],
    "documentation_task": [
        (
            "Описать локальный запуск проекта",
            (
                "Добавить документацию по запуску Plane, COMPASS API, dashboard "
                "и генерации данных."
            ),
        ),
        (
            "Описать структуру synthetic data",
            "Зафиксировать поля employees, tasks и assignments для будущих отчётов.",
        ),
        (
            "Подготовить demo сценарии проекта",
            "Описать fast_delivery, balanced_workload, growth и risk_minimization сценарии.",
        ),
    ],
}


TECH_STACK_SKILLS = {
    "Python",
    "FastAPI",
    "Django",
    "PostgreSQL",
    "Redis",
    "Docker",
    "Kubernetes",
    "React",
    "TypeScript",
    "Next.js",
    "HTML/CSS",
    "PyTorch",
}

TASK_CONTEXTS = [
    "auth",
    "billing",
    "analytics",
    "notifications",
    "reporting",
    "team workload",
    "recommendation engine",
    "Plane integration",
    "dashboard",
    "ML pipeline",
    "audit logs",
    "permissions",
    "data export",
    "model metrics",
    "fairness analysis",
]

TASK_AREAS_RU = [
    "модуля авторизации",
    "аналитического dashboard",
    "интеграции с Plane",
    "пайплайна рекомендаций",
    "системы отчётов",
    "модуля командной загрузки",
    "ML-пайплайна",
    "системы уведомлений",
    "модуля безопасности",
    "экспорта данных",
]

def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def weighted_choice(weights: dict[str, float], rng: random.Random) -> str:
    return rng.choices(list(weights.keys()), weights=list(weights.values()), k=1)[0]


def clamp_int(value: int, min_value: int, max_value: int) -> int:
    return max(min_value, min(max_value, value))


def generate_tasks() -> pd.DataFrame:
    schema = load_yaml(SYNTHETIC_SCHEMA_PATH)
    config = load_yaml(SYNTHETIC_DATA_CONFIG_PATH)

    seed = int(config["random_seed"]) + 1
    rng = random.Random(seed)
    np.random.seed(seed)

    tasks_count = int(config["tasks_count"])
    task_types = schema["tasks"]["task_types"]
    task_type_names = list(task_types.keys())
    project_config = config["projects"]

    date_start = datetime.fromisoformat(config["date_range_start"])
    date_end = datetime.fromisoformat(config["date_range_end"])
    total_days = (date_end - date_start).days

    priority_weights = config["task_generation"]["priorities"]
    growth_probability = float(config["task_generation"]["growth_task_probability"])

    tasks: list[dict[str, Any]] = []

    for index in range(1, tasks_count + 1):
        task_type = rng.choice(task_type_names)
        type_config = task_types[task_type]

        title, description = rng.choice(TASK_TEMPLATES[task_type])

        context = rng.choice(TASK_CONTEXTS)
        area_ru = rng.choice(TASK_AREAS_RU)

        title = f"{title} — {area_ru}"
        description = f"{description} Контекст задачи: {context}."
        
        project_key = type_config["default_project_key"]
        if rng.random() < 0.12:
            project_key = weighted_choice(
                {key: value["weight"] for key, value in project_config.items()},
                rng,
            )

        project = project_config[project_key]
        priority = weighted_choice(priority_weights, rng)

        average_complexity = int(type_config["average_complexity"])
        complexity = clamp_int(
            average_complexity + rng.randint(-1, 1),
            min_value=1,
            max_value=5,
        )

        priority_boost = 1 if priority in {"high", "urgent"} else 0
        business_criticality = clamp_int(
            complexity + priority_boost + rng.randint(-1, 1),
            min_value=1,
            max_value=5,
        )

        deadline_range = config["task_generation"]["deadline_days"]
        deadline_days = rng.randint(deadline_range["min"], deadline_range["max"])

        estimated_range = config["task_generation"]["estimated_hours"]
        estimated_hours = clamp_int(
            int(rng.normalvariate(average_complexity * 10, 8)),
            min_value=estimated_range["min"],
            max_value=estimated_range["max"],
        )

        dependencies_range = config["task_generation"]["dependencies_count"]
        dependencies_count = rng.randint(
            dependencies_range["min"],
            dependencies_range["max"],
        )

        created_at = date_start + timedelta(days=rng.randint(0, total_days))
        updated_at = created_at + timedelta(days=rng.randint(0, min(21, total_days)))

        required_skills = type_config["default_required_skills"]
        required_stack = [
            skill
            for skill in required_skills
            if skill in TECH_STACK_SKILLS
        ]

        is_growth_task = rng.random() < growth_probability
        if task_type == "documentation_task":
            is_growth_task = True

        tasks.append(
            {
                "task_id": f"TASK-{index:04d}",
                "plane_work_item_id": "",
                "plane_issue_id": "",
                "plane_project_id": project["plane_project_id"],
                "project_key": project_key,
                "title": title,
                "description": description,
                "task_type": task_type,
                "required_stack": json.dumps(required_stack, ensure_ascii=False),
                "required_skills": json.dumps(
                    required_skills,
                    ensure_ascii=False,
                    sort_keys=True,
                ),
                "complexity": complexity,
                "priority": priority,
                "business_criticality": business_criticality,
                "deadline_days": deadline_days,
                "estimated_hours": estimated_hours,
                "dependencies_count": dependencies_count,
                "is_growth_task": is_growth_task,
                "source": "synthetic",
                "created_at": created_at.isoformat(),
                "updated_at": updated_at.isoformat(),
            }
        )

    return pd.DataFrame(tasks)


def save_tasks(df: pd.DataFrame) -> None:
    config = load_yaml(SYNTHETIC_DATA_CONFIG_PATH)
    csv_path = PROJECT_ROOT / config["output"]["tasks_csv"]
    json_path = PROJECT_ROOT / config["output"]["tasks_json"]

    csv_path.parent.mkdir(parents=True, exist_ok=True)

    df.to_csv(csv_path, index=False)
    df.to_json(json_path, orient="records", force_ascii=False, indent=2)

    preview_columns = [
        "task_id",
        "project_key",
        "task_type",
        "priority",
        "complexity",
        "title",
    ]

    print(f"Tasks generated: {len(df)}")
    print(f"CSV: {csv_path}")
    print(f"JSON: {json_path}")
    print()
    print(df[preview_columns].head(20).to_string(index=False))


def main() -> None:
    tasks = generate_tasks()
    save_tasks(tasks)


if __name__ == "__main__":
    main()