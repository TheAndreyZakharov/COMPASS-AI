from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import httpx
import pandas as pd
import plotly.express as px
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]

EMPLOYEES_PATH = PROJECT_ROOT / "data" / "synthetic" / "employees.csv"
TASKS_PATH = PROJECT_ROOT / "data" / "synthetic" / "tasks.csv"
ASSIGNMENTS_PATH = PROJECT_ROOT / "data" / "synthetic" / "assignments.csv"
MODEL_METRICS_PATH = PROJECT_ROOT / "reports" / "model_metrics.json"
RANKING_METRICS_PATH = PROJECT_ROOT / "reports" / "ranking_metrics.json"

DEFAULT_API_URL = "http://localhost:8000"
DEFAULT_PLANE_PROJECT_ID = "e608e7ad-f4fe-401d-b0f3-5570e82f08ee"

RECOMMENDATION_MODES = [
    "balanced_workload",
    "fast_delivery",
    "growth",
    "risk_minimization",
]


st.set_page_config(
    page_title="COMPASS AI Dashboard",
    page_icon="🧭",
    layout="wide",
)


def read_json_file(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}

    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, dict):
        return {}

    return data


@st.cache_data(show_spinner=False)
def load_employees() -> pd.DataFrame:
    if not EMPLOYEES_PATH.exists():
        return pd.DataFrame()

    return pd.read_csv(EMPLOYEES_PATH)


@st.cache_data(show_spinner=False)
def load_tasks() -> pd.DataFrame:
    if not TASKS_PATH.exists():
        return pd.DataFrame()

    return pd.read_csv(TASKS_PATH)


@st.cache_data(show_spinner=False)
def load_assignments() -> pd.DataFrame:
    if not ASSIGNMENTS_PATH.exists():
        return pd.DataFrame()

    return pd.read_csv(ASSIGNMENTS_PATH)


@st.cache_data(show_spinner=False)
def load_model_metrics() -> dict[str, Any]:
    return read_json_file(MODEL_METRICS_PATH)


@st.cache_data(show_spinner=False)
def load_ranking_metrics() -> dict[str, Any]:
    return read_json_file(RANKING_METRICS_PATH)


def safe_float(value: Any, default: float = 0.0) -> float:
    if value is None:
        return default

    try:
        if pd.isna(value):
            return default
    except TypeError:
        pass

    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(safe_float(value, float(default)))
    except (TypeError, ValueError):
        return default


def normalize_bool(value: bool) -> str:
    return str(value).lower()


def api_get(
    api_url: str,
    path: str,
    params: dict[str, Any] | None = None,
) -> dict[str, Any]:
    url = f"{api_url.rstrip('/')}/{path.lstrip('/')}"
    with httpx.Client(timeout=60.0) as client:
        response = client.get(url, params=params)
        response.raise_for_status()
        data = response.json()

    if not isinstance(data, dict):
        return {"response": data}

    return data


def api_post(api_url: str, path: str, payload: dict[str, Any]) -> dict[str, Any]:
    url = f"{api_url.rstrip('/')}/{path.lstrip('/')}"
    with httpx.Client(timeout=60.0) as client:
        response = client.post(url, json=payload)
        response.raise_for_status()
        data = response.json()

    if not isinstance(data, dict):
        return {"response": data}

    return data


def top_candidate(response: dict[str, Any]) -> dict[str, Any]:
    candidates = response.get("top_candidates") or []
    if not isinstance(candidates, list) or not candidates:
        return {}

    candidate = candidates[0]
    if not isinstance(candidate, dict):
        return {}

    return candidate


def dataframe_columns(df: pd.DataFrame, columns: list[str]) -> list[str]:
    return [column for column in columns if column in df.columns]


def show_api_status(api_url: str) -> None:
    try:
        health = api_get(api_url, "/health")
    except Exception as exc:
        st.error(f"COMPASS API недоступен: {exc}")
        return

    status = health.get("status", "unknown")
    service = health.get("service", "unknown")
    st.success(f"COMPASS API работает: {service}, status={status}")


def overview_page(api_url: str) -> None:
    st.header("Overview")

    employees = load_employees()
    tasks = load_tasks()
    assignments = load_assignments()

    if employees.empty or tasks.empty or assignments.empty:
        st.warning("Synthetic data не найдены. Сначала запусти генерацию данных.")
        return

    average_workload = safe_float(employees.get("current_workload", pd.Series()).mean())
    average_success_probability = safe_float(
        assignments.get("success_probability", pd.Series()).mean(),
    )

    if "risk_score" in assignments.columns:
        high_risk_assignments = int((assignments["risk_score"] >= 0.70).sum())
    else:
        high_risk_assignments = 0

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Synthetic tasks", len(tasks))
    col2.metric("Synthetic employees", len(employees))
    col3.metric("Avg workload", f"{average_workload:.2f}")
    col4.metric("High risk rows", high_risk_assignments)
    col5.metric("Avg success probability", f"{average_success_probability:.2f}")

    if "project_key" in tasks.columns:
        st.subheader("Synthetic tasks by project")
        project_counts = tasks["project_key"].value_counts().reset_index()
        project_counts.columns = ["project_key", "tasks_count"]
        chart = px.bar(project_counts, x="project_key", y="tasks_count")
        st.plotly_chart(chart, width="stretch")

    if "task_type" in tasks.columns:
        st.subheader("Synthetic tasks by type")
        type_counts = tasks["task_type"].value_counts().reset_index()
        type_counts.columns = ["task_type", "tasks_count"]
        chart = px.bar(type_counts, x="task_type", y="tasks_count")
        st.plotly_chart(chart, width="stretch")

    if "outcome_status" in assignments.columns:
        st.subheader("Synthetic assignment outcomes")
        outcome_counts = assignments["outcome_status"].value_counts().reset_index()
        outcome_counts.columns = ["outcome_status", "count"]
        chart = px.pie(outcome_counts, names="outcome_status", values="count")
        st.plotly_chart(chart, width="stretch")

    with st.expander("API status"):
        show_api_status(api_url)


def issue_recommendations_page(api_url: str) -> None:
    st.header("Issue Recommendations")

    mode = st.selectbox("Recommendation mode", RECOMMENDATION_MODES, index=0)
    top_k = st.slider("Top K", min_value=1, max_value=10, value=3)
    use_llm = st.checkbox("Use LLM explanation", value=False)

    tab_synthetic, tab_plane, tab_manual = st.tabs(
        ["Synthetic TASK-*", "Plane work item by ID", "Manual task"],
    )

    with tab_synthetic:
        synthetic_recommendation_tab(
            api_url=api_url,
            mode=mode,
            top_k=top_k,
            use_llm=use_llm,
        )

    with tab_plane:
        plane_recommendation_tab(
            api_url=api_url,
            mode=mode,
            top_k=top_k,
            use_llm=use_llm,
        )

    with tab_manual:
        manual_recommendation_tab(
            api_url=api_url,
            mode=mode,
            top_k=top_k,
            use_llm=use_llm,
        )


def synthetic_recommendation_tab(
    api_url: str,
    mode: str,
    top_k: int,
    use_llm: bool,
) -> None:
    st.subheader("Analyze synthetic task")

    tasks = load_tasks()
    if tasks.empty or "task_id" not in tasks.columns:
        st.warning("tasks.csv не найден или в нём нет колонки task_id.")
        return

    task_options = tasks["task_id"].head(250).tolist()
    task_id = st.selectbox("Synthetic task id", task_options, index=0)

    if not st.button("Analyze synthetic issue"):
        return

    try:
        response = api_get(
            api_url,
            f"/recommendations/issue/{task_id}",
            params={
                "mode": mode,
                "top_k": top_k,
                "write_back": "false",
                "auto_assign": "false",
                "use_llm": normalize_bool(use_llm),
            },
        )
    except Exception as exc:
        st.error(f"Ошибка анализа synthetic task: {exc}")
        return

    show_recommendation_response(response)


def plane_recommendation_tab(
    api_url: str,
    mode: str,
    top_k: int,
    use_llm: bool,
) -> None:
    st.subheader("Analyze real Plane work item by ID")

    project_id = st.text_input("Plane project id", value=DEFAULT_PLANE_PROJECT_ID)
    work_item_id = st.text_input("Plane work item id")
    write_back = st.checkbox("Write recommendation comment to Plane", value=False)
    auto_assign = st.checkbox("Auto assign top candidate", value=False)
    threshold = st.number_input(
        "Auto assign threshold",
        min_value=0.0,
        max_value=1.0,
        value=0.75,
    )

    st.caption(
        "Этот старый режим анализирует Plane task по ручному ID. "
        "Новый live-режим со списком задач находится на странице Plane Live."
    )

    if not st.button("Analyze Plane work item by ID"):
        return

    if not work_item_id.strip():
        st.warning("Укажи Plane work item id.")
        return

    try:
        response = api_get(
            api_url,
            f"/plane/recommendations/work-item/{work_item_id.strip()}",
            params={
                "project_id": project_id.strip(),
                "mode": mode,
                "top_k": top_k,
                "write_back": normalize_bool(write_back),
                "auto_assign": normalize_bool(auto_assign),
                "threshold": threshold,
                "use_llm": normalize_bool(use_llm),
            },
        )
    except Exception as exc:
        st.error(f"Ошибка анализа Plane work item: {exc}")
        return

    show_recommendation_response(response)


def manual_recommendation_tab(
    api_url: str,
    mode: str,
    top_k: int,
    use_llm: bool,
) -> None:
    st.subheader("Analyze manual task")

    title = st.text_input(
        "Task title",
        value="Добавить endpoint для командной аналитики",
    )
    description = st.text_area(
        "Task description",
        value="Нужно сделать FastAPI endpoint для summary по загрузке команды и рискам.",
        height=120,
    )
    priority = st.selectbox(
        "Priority",
        ["none", "low", "medium", "high", "urgent"],
        index=3,
    )
    labels = st.text_input("Labels", value="backend, fastapi, feature")
    deadline_days = st.number_input(
        "Deadline days",
        min_value=1,
        max_value=90,
        value=7,
    )

    if not st.button("Analyze manual task"):
        return

    label_list = [label.strip() for label in labels.split(",") if label.strip()]
    payload = {
        "issue": {
            "id": "manual-dashboard-task",
            "name": title,
            "description_html": description,
            "priority": priority,
            "labels": label_list,
            "deadline_days": int(deadline_days),
        },
        "mode": mode,
        "top_k": top_k,
        "use_llm": use_llm,
    }

    try:
        response = api_post(api_url, "/recommendations/manual", payload)
    except Exception as exc:
        st.error(f"Ошибка анализа manual task: {exc}")
        return

    show_recommendation_response(response)


def plane_live_page(api_url: str) -> None:
    st.header("Plane Live")

    st.info(
        "Эта страница показывает только реальные данные из Plane: "
        "projects, work items и project members. "
        "Если в Plane появилась новая задача или новый активный member, "
        "они появятся здесь после refresh."
    )

    col_a, col_b = st.columns([1, 1])
    with col_a:
        if st.button("Refresh Plane data"):
            st.cache_data.clear()
            st.rerun()

    with col_b:
        show_api_status(api_url)

    try:
        live_data = api_get(api_url, "/plane/live")
    except Exception as exc:
        st.error(f"Не удалось загрузить Plane Live данные: {exc}")
        st.warning("Проверь, что Plane и FastAPI запущены.")
        return

    projects = live_data.get("projects") or []
    workspace_members = live_data.get("workspace_members") or []
    pending_invitations = live_data.get("pending_invitations") or []

    if not isinstance(projects, list):
        projects = []

    if not isinstance(workspace_members, list):
        workspace_members = []

    if not isinstance(pending_invitations, list):
        pending_invitations = []

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Plane projects", live_data.get("projects_count", len(projects)))
    col2.metric("Plane work items", live_data.get("work_items_count", 0))
    col3.metric("Open work items", live_data.get("open_work_items_count", 0))
    col4.metric("Workspace members", live_data.get("workspace_members_count", 0))

    if pending_invitations:
        st.warning(
            f"Есть pending invitations: {len(pending_invitations)}. "
            "Pending users не считаются полноценными активными исполнителями."
        )

    if not projects:
        st.warning("Plane projects не найдены.")
        return

    project_labels = [
        f"{project.get('name')} ({project.get('identifier')})"
        for project in projects
        if isinstance(project, dict)
    ]

    selected_label = st.selectbox("Plane project", project_labels, index=0)
    selected_index = project_labels.index(selected_label)
    selected_project = projects[selected_index]

    if not isinstance(selected_project, dict):
        st.error("Некорректный project payload.")
        return

    project_id = str(selected_project.get("project_id") or "")
    work_items = selected_project.get("work_items") or []
    members = selected_project.get("members") or []

    if not isinstance(work_items, list):
        work_items = []

    if not isinstance(members, list):
        members = []

    project_col1, project_col2, project_col3 = st.columns(3)
    project_col1.metric("Project members", len(members))
    project_col2.metric("Project work items", len(work_items))
    project_col3.metric(
        "Project open work items",
        int(selected_project.get("open_work_items_count") or 0),
    )

    st.subheader("Real Plane project members")

    if members:
        members_df = pd.DataFrame(members)
        visible_columns = dataframe_columns(
            members_df,
            [
                "id",
                "member",
                "email",
                "display_name",
                "first_name",
                "last_name",
                "role",
            ],
        )
        st.dataframe(members_df[visible_columns], width="stretch")
    else:
        st.warning("В этом Plane project нет members или API их не вернул.")

    st.subheader("Real Plane work items")

    if not work_items:
        st.warning("В этом Plane project нет work items.")
        return

    work_items_df = pd.DataFrame(work_items)
    visible_columns = dataframe_columns(
        work_items_df,
        [
            "id",
            "identifier",
            "name",
            "priority",
            "is_open",
            "assignees_count",
            "target_date",
            "updated_at",
        ],
    )
    st.dataframe(work_items_df[visible_columns], width="stretch")

    open_only = st.checkbox("Show only open work items", value=True)

    if open_only and "is_open" in work_items_df.columns:
        selectable_df = work_items_df[work_items_df["is_open"]].copy()
    else:
        selectable_df = work_items_df.copy()

    if selectable_df.empty:
        st.warning("Нет задач для анализа после фильтра.")
        return

    selectable_df["select_label"] = selectable_df.apply(
        lambda row: f"{row.get('identifier', '')} — {row.get('name', '')}",
        axis=1,
    )

    selected_task_label = st.selectbox(
        "Select Plane work item for AI analysis",
        selectable_df["select_label"].tolist(),
    )
    selected_task_row = selectable_df[
        selectable_df["select_label"] == selected_task_label
    ].iloc[0]
    work_item_id = str(selected_task_row.get("id") or "")

    st.subheader("Analyze selected Plane work item")

    mode = st.selectbox(
        "Plane Live recommendation mode",
        RECOMMENDATION_MODES,
        index=0,
    )
    top_k = st.slider(
        "Plane Live Top K",
        min_value=1,
        max_value=10,
        value=3,
    )
    use_llm = st.checkbox("Plane Live: use LLM explanation", value=False)
    write_back = st.checkbox("Plane Live: write comment to Plane", value=False)
    auto_assign = st.checkbox("Plane Live: auto assign top candidate", value=False)
    threshold = st.number_input(
        "Plane Live: auto assign threshold",
        min_value=0.0,
        max_value=1.0,
        value=0.75,
    )

    st.caption(
        "В этом режиме кандидаты ограничены реальными project members Plane. "
        "Если member не связан с COMPASS employee profile, он всё равно "
        "попадёт в список как plane_unmapped кандидат, но с нейтральными skills."
    )

    if not st.button("Analyze selected Plane work item"):
        return

    try:
        response = api_get(
            api_url,
            f"/plane/recommendations/work-item/{work_item_id}",
            params={
                "project_id": project_id,
                "mode": mode,
                "top_k": top_k,
                "write_back": normalize_bool(write_back),
                "auto_assign": normalize_bool(auto_assign),
                "threshold": threshold,
                "use_llm": normalize_bool(use_llm),
            },
        )
    except Exception as exc:
        st.error(f"Ошибка Plane Live анализа: {exc}")
        return

    show_recommendation_response(response)


def show_recommendation_response(response: dict[str, Any]) -> None:
    candidate = top_candidate(response)

    st.success("Recommendation completed")

    task_id = response.get("task_id")
    plane_work_item_id = response.get("plane_work_item_id")
    top_score = safe_float(candidate.get("score")) if candidate else None

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Task", task_id or plane_work_item_id or "n/a")
    col2.metric("Mode", response.get("mode", "n/a"))
    col3.metric("Top score", f"{top_score:.4f}" if top_score is not None else "n/a")
    col4.metric("Source", candidate.get("source", response.get("source", "n/a")))
    col5.metric("Candidate scope", response.get("candidate_scope", "default"))

    st.subheader("Top candidates")
    candidates = response.get("top_candidates") or []

    if isinstance(candidates, list) and candidates:
        candidates_df = pd.DataFrame(candidates)
        visible_columns = dataframe_columns(
            candidates_df,
            [
                "rank",
                "employee_id",
                "plane_user_id",
                "name",
                "role",
                "grade",
                "score",
                "success_probability",
                "source",
            ],
        )
        st.dataframe(candidates_df[visible_columns], width="stretch")
    else:
        st.warning("Кандидаты не вернулись.")

    st.subheader("Explanation")
    st.markdown(response.get("explanation") or "No explanation")

    with st.expander("Plane live"):
        st.json(response.get("plane_live", {}))

    with st.expander("Plane write-back"):
        st.json(response.get("plane_write_back", {}))

    with st.expander("Plane auto-assign"):
        st.json(response.get("plane_auto_assign", {}))

    with st.expander("Raw response"):
        st.json(response)


def workload_risk_level(workload: Any) -> str:
    value = safe_float(workload)

    if value >= 0.95:
        return "critical"

    if value >= 0.85:
        return "high"

    if value >= 0.70:
        return "medium"

    return "low"


def team_workload_page() -> None:
    st.header("Synthetic Team Workload")

    st.info(
        "Эта страница показывает synthetic/ML-профили COMPASS. "
        "Реальные люди и задачи из Plane находятся на странице Plane Live."
    )

    employees = load_employees()
    if employees.empty:
        st.warning("employees.csv не найден.")
        return

    required_columns = [
        "employee_id",
        "name",
        "role",
        "grade",
        "current_workload",
    ]
    missing_columns = [
        column
        for column in required_columns
        if column not in employees.columns
    ]
    if missing_columns:
        st.error(f"В employees.csv нет обязательных колонок: {missing_columns}")
        return

    employees = employees.copy()
    employees["workload_percent"] = employees["current_workload"].apply(safe_float) * 100
    employees["overload_risk"] = employees["current_workload"].apply(workload_risk_level)

    average_workload = safe_float(employees["current_workload"].mean())
    high_risk_count = int((employees["overload_risk"] == "high").sum())
    critical_risk_count = int((employees["overload_risk"] == "critical").sum())

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Synthetic employees", len(employees))
    col2.metric("Avg workload", f"{average_workload:.2f}")
    col3.metric("High risk", high_risk_count)
    col4.metric("Critical risk", critical_risk_count)

    st.subheader("Workload by synthetic employee")
    workload_chart = employees.sort_values("current_workload", ascending=False)

    hover_columns = dataframe_columns(
        workload_chart,
        ["employee_id", "role", "grade", "active_tasks_count"],
    )
    chart = px.bar(
        workload_chart,
        x="name",
        y="workload_percent",
        color="overload_risk",
        hover_data=hover_columns,
    )
    st.plotly_chart(chart, width="stretch")

    st.subheader("Synthetic team table")
    columns = dataframe_columns(
        employees,
        [
            "employee_id",
            "plane_user_id",
            "name",
            "role",
            "grade",
            "current_workload",
            "active_tasks_count",
            "availability",
            "overload_risk",
            "avg_completion_speed",
            "avg_quality_score",
            "deadline_reliability",
        ],
    )
    st.dataframe(employees[columns], width="stretch")


def plane_team_page(api_url: str) -> None:
    st.header("Plane Team")

    st.info(
        "Эта страница оставлена как быстрый просмотр людей Plane. "
        "Полный live-режим с задачами и AI-анализом находится на странице Plane Live."
    )

    try:
        response = api_get(api_url, "/plane/members")
    except Exception as exc:
        st.error(f"Не удалось загрузить Plane members: {exc}")
        return

    workspace_members = response.get("workspace_members") or []
    pending_invitations = response.get("pending_invitations") or []
    projects = response.get("projects") or []

    if not isinstance(workspace_members, list):
        workspace_members = []

    if not isinstance(pending_invitations, list):
        pending_invitations = []

    if not isinstance(projects, list):
        projects = []

    col1, col2, col3 = st.columns(3)
    col1.metric(
        "Workspace members",
        response.get("workspace_members_count", len(workspace_members)),
    )
    col2.metric(
        "Pending invitations",
        response.get("pending_invitations_count", len(pending_invitations)),
    )
    col3.metric("Projects", len(projects))

    st.subheader("Active workspace members")

    if workspace_members:
        members_df = pd.DataFrame(workspace_members)
        visible_columns = dataframe_columns(
            members_df,
            [
                "id",
                "member",
                "email",
                "display_name",
                "first_name",
                "last_name",
                "role",
            ],
        )
        st.dataframe(members_df[visible_columns], width="stretch")
    else:
        st.warning("Plane API не вернул активных workspace members.")

    st.subheader("Pending invitations")

    if pending_invitations:
        pending_df = pd.DataFrame(pending_invitations)
        visible_columns = dataframe_columns(
            pending_df,
            [
                "id",
                "email",
                "role",
                "accepted",
                "responded_at",
                "created_at",
            ],
        )
        st.dataframe(pending_df[visible_columns], width="stretch")
    else:
        st.success("Нет pending invitations.")

    st.subheader("Project members")

    if not projects:
        st.warning("Plane projects не вернулись.")
        return

    for project in projects:
        if not isinstance(project, dict):
            continue

        project_name = project.get("name") or "Unnamed project"
        project_identifier = project.get("identifier") or "n/a"
        members = project.get("members") or []

        if not isinstance(members, list):
            members = []

        title = f"{project_name} ({project_identifier}) — members: {len(members)}"
        with st.expander(title):
            if members:
                project_df = pd.DataFrame(members)
                visible_columns = dataframe_columns(
                    project_df,
                    [
                        "id",
                        "member",
                        "email",
                        "display_name",
                        "first_name",
                        "last_name",
                        "role",
                    ],
                )
                st.dataframe(project_df[visible_columns], width="stretch")
            else:
                st.warning("В проекте нет members или Plane API их не вернул.")


def model_metrics_page() -> None:
    st.header("Model Metrics")

    model_metrics = load_model_metrics()
    ranking_metrics = load_ranking_metrics()

    if not model_metrics:
        st.warning("reports/model_metrics.json не найден. Запусти evaluate.")
    else:
        show_classification_metrics(model_metrics)

    if not ranking_metrics:
        st.warning("reports/ranking_metrics.json не найден. Запусти ranking metrics.")
    else:
        show_ranking_metrics(ranking_metrics)


def show_classification_metrics(model_metrics: dict[str, Any]) -> None:
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("ROC-AUC", f"{safe_float(model_metrics.get('roc_auc')):.4f}")
    col2.metric("PR-AUC", f"{safe_float(model_metrics.get('pr_auc')):.4f}")
    col3.metric("F1", f"{safe_float(model_metrics.get('f1')):.4f}")
    col4.metric("Precision", f"{safe_float(model_metrics.get('precision')):.4f}")
    col5.metric("Recall", f"{safe_float(model_metrics.get('recall')):.4f}")

    st.subheader("Classification metrics")
    st.json(model_metrics)


def show_ranking_metrics(ranking_metrics: dict[str, Any]) -> None:
    st.subheader("Ranking metrics")

    rows = []
    for model_name, metrics in ranking_metrics.items():
        if isinstance(metrics, dict):
            row = {"model": model_name}
            row.update(metrics)
            rows.append(row)

    if not rows:
        st.warning("ranking_metrics.json не содержит model metrics.")
        return

    ranking_df = pd.DataFrame(rows)
    st.dataframe(ranking_df, width="stretch")

    metric_columns = dataframe_columns(
        ranking_df,
        ["precision_at_1", "precision_at_3", "ndcg_at_3", "mrr"],
    )

    if not metric_columns:
        return

    long_df = ranking_df.melt(
        id_vars=["model"],
        value_vars=metric_columns,
        var_name="metric",
        value_name="value",
    )
    chart = px.bar(long_df, x="metric", y="value", color="model", barmode="group")
    st.plotly_chart(chart, width="stretch")


def fairness_page() -> None:
    st.header("Fairness")

    employees = load_employees()
    assignments = load_assignments()

    if employees.empty or assignments.empty:
        st.warning("Synthetic data не найдены.")
        return

    required_assignment_columns = ["employee_id"]
    required_employee_columns = [
        "employee_id",
        "name",
        "role",
        "grade",
        "current_workload",
    ]

    if not all(column in assignments.columns for column in required_assignment_columns):
        st.error("В assignments.csv нет обязательной колонки employee_id.")
        return

    if not all(column in employees.columns for column in required_employee_columns):
        st.error("В employees.csv нет обязательных колонок для fairness анализа.")
        return

    employee_columns = dataframe_columns(
        employees,
        [
            "employee_id",
            "name",
            "role",
            "grade",
            "current_workload",
            "learning_goals",
        ],
    )

    merged = assignments.merge(
        employees[employee_columns],
        on="employee_id",
        how="left",
    )

    if merged.empty:
        st.warning("Нет данных для fairness анализа.")
        return

    senior_share = float((merged["grade"] == "senior").mean())
    junior_share = float((merged["grade"] == "junior").mean())
    average_workload = safe_float(merged["current_workload"].mean())

    employee_distribution = merged["employee_id"].value_counts(normalize=True)
    top_employee_share = safe_float(employee_distribution.iloc[0])

    if "growth_match_score" in merged.columns:
        growth_share = float((merged["growth_match_score"] > 0.5).mean())
    else:
        growth_share = 0.0

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Senior assignment share", f"{senior_share:.2f}")
    col2.metric("Junior assignment share", f"{junior_share:.2f}")
    col3.metric("Top employee concentration", f"{top_employee_share:.2f}")
    col4.metric("Avg assigned workload", f"{average_workload:.2f}")
    col5.metric("Growth match share", f"{growth_share:.2f}")

    st.subheader("Assignment distribution by grade")
    grade_counts = merged["grade"].value_counts().reset_index()
    grade_counts.columns = ["grade", "assignments"]
    st.plotly_chart(px.bar(grade_counts, x="grade", y="assignments"), width="stretch")

    st.subheader("Assignment distribution by role")
    role_counts = merged["role"].value_counts().reset_index()
    role_counts.columns = ["role", "assignments"]
    st.plotly_chart(px.bar(role_counts, x="role", y="assignments"), width="stretch")

    st.subheader("Top employee concentration")
    employee_counts = merged["name"].value_counts().head(15).reset_index()
    employee_counts.columns = ["employee", "assignments"]
    st.plotly_chart(
        px.bar(employee_counts, x="employee", y="assignments"),
        width="stretch",
    )

    st.subheader("Fairness notes")
    st.markdown(
        """
- Senior share показывает, не забирают ли senior почти все назначения.
- Junior share показывает, не игнорируются ли junior.
- Top employee concentration показывает, нет ли концентрации на одном человеке.
- Avg assigned workload показывает риск усиления перегруза.
- Growth match share показывает долю назначений, полезных для развития.
""",
    )


def settings_page(api_url: str) -> None:
    st.header("Settings")

    st.write("Current dashboard configuration")
    st.code(
        f"""
COMPASS_API_URL={api_url}
DEFAULT_PLANE_PROJECT_ID={DEFAULT_PLANE_PROJECT_ID}

Data files:
{EMPLOYEES_PATH}
{TASKS_PATH}
{ASSIGNMENTS_PATH}

Reports:
{MODEL_METRICS_PATH}
{RANKING_METRICS_PATH}
""".strip(),
    )

    st.subheader("Health check")
    if st.button("Check COMPASS API"):
        show_api_status(api_url)

    st.subheader("Required local services")
    st.markdown(
        """
- FastAPI backend: `uvicorn app.api:app --reload --host 0.0.0.0 --port 8000`
- Plane: `./scripts/start_plane.sh`
- Optional LLM: `ollama serve`
- Dashboard: `streamlit run app/dashboard.py`
""",
    )


def main() -> None:
    st.sidebar.title("COMPASS AI")

    api_url = st.sidebar.text_input("COMPASS API URL", value=DEFAULT_API_URL)

    page = st.sidebar.radio(
        "Page",
        [
            "Overview",
            "Issue Recommendations",
            "Plane Live",
            "Synthetic Team Workload",
            "Plane Team",
            "Model Metrics",
            "Fairness",
            "Settings",
        ],
    )

    if page == "Overview":
        overview_page(api_url)
    elif page == "Issue Recommendations":
        issue_recommendations_page(api_url)
    elif page == "Plane Live":
        plane_live_page(api_url)
    elif page == "Synthetic Team Workload":
        team_workload_page()
    elif page == "Plane Team":
        plane_team_page(api_url)
    elif page == "Model Metrics":
        model_metrics_page()
    elif page == "Fairness":
        fairness_page()
    elif page == "Settings":
        settings_page(api_url)


if __name__ == "__main__":
    main()