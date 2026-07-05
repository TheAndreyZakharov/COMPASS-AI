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
    col1.metric("Tasks", len(tasks))
    col2.metric("Employees", len(employees))
    col3.metric("Avg workload", f"{average_workload:.2f}")
    col4.metric("High risk rows", high_risk_assignments)
    col5.metric("Avg success probability", f"{average_success_probability:.2f}")

    if "project_key" in tasks.columns:
        st.subheader("Tasks by project")
        project_counts = tasks["project_key"].value_counts().reset_index()
        project_counts.columns = ["project_key", "tasks_count"]
        chart = px.bar(project_counts, x="project_key", y="tasks_count")
        st.plotly_chart(chart, use_container_width=True)

    if "task_type" in tasks.columns:
        st.subheader("Tasks by type")
        type_counts = tasks["task_type"].value_counts().reset_index()
        type_counts.columns = ["task_type", "tasks_count"]
        chart = px.bar(type_counts, x="task_type", y="tasks_count")
        st.plotly_chart(chart, use_container_width=True)

    if "outcome_status" in assignments.columns:
        st.subheader("Assignment outcomes")
        outcome_counts = assignments["outcome_status"].value_counts().reset_index()
        outcome_counts.columns = ["outcome_status", "count"]
        chart = px.pie(outcome_counts, names="outcome_status", values="count")
        st.plotly_chart(chart, use_container_width=True)

    with st.expander("API status"):
        show_api_status(api_url)


def issue_recommendations_page(api_url: str) -> None:
    st.header("Issue Recommendations")

    mode = st.selectbox("Recommendation mode", RECOMMENDATION_MODES, index=0)
    top_k = st.slider("Top K", min_value=1, max_value=10, value=3)
    use_llm = st.checkbox("Use LLM explanation", value=False)

    tab_synthetic, tab_plane, tab_manual = st.tabs(
        ["Synthetic TASK-*", "Plane work item", "Manual task"],
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
    st.subheader("Analyze real Plane work item")

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

    if not st.button("Analyze Plane work item"):
        return

    if not work_item_id.strip():
        st.warning("Укажи Plane work item id.")
        return

    try:
        response = api_get(
            api_url,
            f"/recommendations/issue/{work_item_id.strip()}",
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


def show_recommendation_response(response: dict[str, Any]) -> None:
    candidate = top_candidate(response)

    st.success("Recommendation completed")

    task_id = response.get("task_id")
    plane_work_item_id = response.get("plane_work_item_id")
    top_score = safe_float(candidate.get("score")) if candidate else None

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Task", task_id or plane_work_item_id or "n/a")
    col2.metric("Mode", response.get("mode", "n/a"))
    col3.metric("Top score", f"{top_score:.4f}" if top_score is not None else "n/a")
    col4.metric("Source", candidate.get("source", response.get("source", "n/a")))

    st.subheader("Top candidates")
    candidates = response.get("top_candidates") or []

    if isinstance(candidates, list) and candidates:
        candidates_df = pd.DataFrame(candidates)
        visible_columns = dataframe_columns(
            candidates_df,
            [
                "rank",
                "employee_id",
                "name",
                "role",
                "grade",
                "score",
                "success_probability",
                "source",
            ],
        )
        st.dataframe(candidates_df[visible_columns], use_container_width=True)
    else:
        st.warning("Кандидаты не вернулись.")

    st.subheader("Explanation")
    st.markdown(response.get("explanation") or "No explanation")

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
    st.header("Team Workload")

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
    missing_columns = [column for column in required_columns if column not in employees.columns]
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
    col1.metric("Employees", len(employees))
    col2.metric("Avg workload", f"{average_workload:.2f}")
    col3.metric("High risk", high_risk_count)
    col4.metric("Critical risk", critical_risk_count)

    st.subheader("Workload by employee")
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
    st.plotly_chart(chart, use_container_width=True)

    st.subheader("Team table")
    columns = dataframe_columns(
        employees,
        [
            "employee_id",
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
    st.dataframe(employees[columns], use_container_width=True)


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
    st.dataframe(ranking_df, use_container_width=True)

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
    st.plotly_chart(chart, use_container_width=True)


def fairness_page() -> None:
    st.header("Fairness")

    employees = load_employees()
    assignments = load_assignments()

    if employees.empty or assignments.empty:
        st.warning("Synthetic data не найдены.")
        return

    required_assignment_columns = ["employee_id"]
    required_employee_columns = ["employee_id", "name", "role", "grade", "current_workload"]

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
    st.plotly_chart(px.bar(grade_counts, x="grade", y="assignments"), use_container_width=True)

    st.subheader("Assignment distribution by role")
    role_counts = merged["role"].value_counts().reset_index()
    role_counts.columns = ["role", "assignments"]
    st.plotly_chart(px.bar(role_counts, x="role", y="assignments"), use_container_width=True)

    st.subheader("Top employee concentration")
    employee_counts = merged["name"].value_counts().head(15).reset_index()
    employee_counts.columns = ["employee", "assignments"]
    st.plotly_chart(
        px.bar(employee_counts, x="employee", y="assignments"),
        use_container_width=True,
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
            "Team Workload",
            "Model Metrics",
            "Fairness",
            "Settings",
        ],
    )

    if page == "Overview":
        overview_page(api_url)
    elif page == "Issue Recommendations":
        issue_recommendations_page(api_url)
    elif page == "Team Workload":
        team_workload_page()
    elif page == "Model Metrics":
        model_metrics_page()
    elif page == "Fairness":
        fairness_page()
    elif page == "Settings":
        settings_page(api_url)


if __name__ == "__main__":
    main()