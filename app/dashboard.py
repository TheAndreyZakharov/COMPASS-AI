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

MODE_LABELS = {
    "balanced_workload": "Balanced workload",
    "fast_delivery": "Fast delivery",
    "growth": "Growth",
    "risk_minimization": "Risk minimization",
}

PAGE_DESCRIPTIONS = {
    "Overview": (
        "Общая картина synthetic-данных, качества назначений "
        "и базового состояния системы."
    ),
    "Issue Recommendations": (
        "AI-рекомендации исполнителей для synthetic, Plane и ручных задач."
    ),
    "Plane Live": (
        "Живые проекты, задачи и участники из Plane с запуском AI-анализа."
    ),
    "Synthetic Team Workload": (
        "Нагрузка synthetic-команды и риски перегруза по ML-профилям."
    ),
    "Plane Team": (
        "Быстрый просмотр активных пользователей, приглашений "
        "и проектных участников Plane."
    ),
    "Model Metrics": "Метрики ML-модели и ranking-качества.",
    "Fairness": "Проверка распределения назначений, концентрации и fairness-рисков.",
    "Settings": "Настройки dashboard, API и локальных сервисов.",
}

st.set_page_config(
    page_title="COMPASS AI Dashboard",
    page_icon="🧭",
    layout="wide",
)


def apply_dashboard_theme() -> None:
    st.markdown(
        """
<style>
:root {
    --compass-bg: #f5f7fb;
    --compass-panel: rgba(255, 255, 255, 0.86);
    --compass-panel-solid: #ffffff;
    --compass-border: rgba(15, 23, 42, 0.08);
    --compass-text: #111827;
    --compass-muted: #667085;
    --compass-soft: #eef2ff;
    --compass-blue: #2563eb;
    --compass-blue-dark: #1d4ed8;
    --compass-green: #16a34a;
    --compass-amber: #d97706;
    --compass-red: #dc2626;
    --compass-shadow: 0 18px 55px rgba(15, 23, 42, 0.08);
}

html,
body,
[class*="css"] {
    font-family:
        -apple-system,
        BlinkMacSystemFont,
        "SF Pro Display",
        "Inter",
        "Segoe UI",
        sans-serif;
}

.stApp {
    background:
        radial-gradient(
            circle at top left,
            rgba(37, 99, 235, 0.10),
            transparent 30rem
        ),
        radial-gradient(
            circle at top right,
            rgba(14, 165, 233, 0.10),
            transparent 28rem
        ),
        linear-gradient(180deg, #fbfcff 0%, var(--compass-bg) 100%);
    color: var(--compass-text);
}

[data-testid="stHeader"] {
    background: rgba(251, 252, 255, 0.72);
    backdrop-filter: blur(18px);
}

[data-testid="stSidebar"] {
    background: rgba(255, 255, 255, 0.78);
    border-right: 1px solid var(--compass-border);
    backdrop-filter: blur(24px);
}

[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h1,
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h2,
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h3 {
    color: var(--compass-text);
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 4rem;
    max-width: 1440px;
}

.compass-hero {
    padding: 2rem 2.1rem;
    margin-bottom: 1.35rem;
    border: 1px solid var(--compass-border);
    border-radius: 28px;
    background:
        linear-gradient(
            135deg,
            rgba(255, 255, 255, 0.94),
            rgba(255, 255, 255, 0.72)
        ),
        radial-gradient(
            circle at 90% 10%,
            rgba(37, 99, 235, 0.12),
            transparent 22rem
        );
    box-shadow: var(--compass-shadow);
}

.compass-kicker {
    width: fit-content;
    padding: 0.35rem 0.7rem;
    margin-bottom: 0.9rem;
    border-radius: 999px;
    background: rgba(37, 99, 235, 0.08);
    color: var(--compass-blue-dark);
    font-size: 0.78rem;
    font-weight: 700;
    letter-spacing: 0.04em;
    text-transform: uppercase;
}

.compass-hero h1 {
    margin: 0;
    color: var(--compass-text);
    font-size: clamp(2rem, 4vw, 3.35rem);
    line-height: 1.02;
    letter-spacing: -0.02em;
}

.compass-hero p {
    max-width: 760px;
    margin: 0.9rem 0 0;
    color: var(--compass-muted);
    font-size: 1.08rem;
    line-height: 1.65;
}

.compass-section {
    padding: 1.35rem 1.45rem;
    margin: 1.05rem 0;
    border: 1px solid var(--compass-border);
    border-radius: 24px;
    background: var(--compass-panel);
    box-shadow: 0 12px 38px rgba(15, 23, 42, 0.055);
}

.compass-section-title {
    margin: 0 0 0.3rem;
    font-size: 1.08rem;
    font-weight: 800;
    color: var(--compass-text);
}

.compass-section-caption {
    margin: 0 0 1rem;
    color: var(--compass-muted);
    font-size: 0.95rem;
    line-height: 1.55;
}

.compass-callout {
    padding: 1rem 1.1rem;
    margin: 0.7rem 0 1rem;
    border-radius: 18px;
    border: 1px solid rgba(37, 99, 235, 0.14);
    background: rgba(37, 99, 235, 0.055);
    color: #1e3a8a;
}

.compass-card {
    padding: 1rem 1.05rem;
    border: 1px solid var(--compass-border);
    border-radius: 20px;
    background: rgba(255, 255, 255, 0.82);
}

.compass-candidate {
    padding: 1.1rem 1.2rem;
    margin: 0.75rem 0;
    border: 1px solid rgba(37, 99, 235, 0.13);
    border-radius: 22px;
    background:
        linear-gradient(
            135deg,
            rgba(255, 255, 255, 0.96),
            rgba(248, 250, 252, 0.92)
        ),
        radial-gradient(
            circle at top right,
            rgba(37, 99, 235, 0.08),
            transparent 12rem
        );
    box-shadow: 0 12px 32px rgba(15, 23, 42, 0.06);
}

.compass-candidate-rank {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    min-width: 2rem;
    height: 2rem;
    padding: 0 0.6rem;
    border-radius: 999px;
    background: #111827;
    color: white;
    font-size: 0.82rem;
    font-weight: 800;
}

.compass-candidate-name {
    margin: 0.7rem 0 0.2rem;
    font-size: 1.18rem;
    font-weight: 850;
    color: var(--compass-text);
}

.compass-candidate-meta {
    color: var(--compass-muted);
    font-size: 0.92rem;
    line-height: 1.5;
}

.compass-pill {
    display: inline-flex;
    align-items: center;
    width: fit-content;
    padding: 0.34rem 0.72rem;
    margin: 0.15rem 0.25rem 0.15rem 0;
    border-radius: 999px;
    border: 1px solid var(--compass-border);
    background: rgba(255, 255, 255, 0.9);
    color: #344054;
    font-size: 0.8rem;
    font-weight: 700;
}

.compass-pill-blue {
    border-color: rgba(37, 99, 235, 0.18);
    background: rgba(37, 99, 235, 0.08);
    color: #1d4ed8;
}

.compass-pill-green {
    border-color: rgba(22, 163, 74, 0.18);
    background: rgba(22, 163, 74, 0.08);
    color: #15803d;
}

.compass-pill-amber {
    border-color: rgba(217, 119, 6, 0.18);
    background: rgba(217, 119, 6, 0.08);
    color: #b45309;
}

.compass-pill-red {
    border-color: rgba(220, 38, 38, 0.18);
    background: rgba(220, 38, 38, 0.08);
    color: #b91c1c;
}

[data-testid="stMetric"] {
    padding: 1.05rem 1rem;
    border: 1px solid var(--compass-border);
    border-radius: 22px;
    background: rgba(255, 255, 255, 0.82);
    box-shadow: 0 10px 30px rgba(15, 23, 42, 0.045);
}

[data-testid="stMetricLabel"] {
    color: var(--compass-muted);
    font-weight: 700;
}

[data-testid="stMetricValue"] {
    color: var(--compass-text);
    font-weight: 850;
}

.stButton > button {
    border-radius: 999px;
    border: 1px solid rgba(37, 99, 235, 0.18);
    background: linear-gradient(180deg, #2f6df6, #1d4ed8);
    color: white;
    font-weight: 800;
    box-shadow: 0 12px 25px rgba(37, 99, 235, 0.18);
}

.stButton > button:hover {
    border-color: rgba(37, 99, 235, 0.30);
    background: linear-gradient(180deg, #3b82f6, #2563eb);
    color: white;
}

.stTabs [data-baseweb="tab-list"] {
    gap: 0.35rem;
    padding: 0.3rem;
    border-radius: 999px;
    background: rgba(15, 23, 42, 0.045);
}

.stTabs [data-baseweb="tab"] {
    border-radius: 999px;
    color: #475467;
    font-weight: 750;
}

.stTabs [aria-selected="true"] {
    background: white;
    color: var(--compass-text);
    box-shadow: 0 8px 20px rgba(15, 23, 42, 0.08);
}

[data-testid="stExpander"] {
    border: 1px solid var(--compass-border);
    border-radius: 18px;
    background: rgba(255, 255, 255, 0.68);
    box-shadow: 0 8px 24px rgba(15, 23, 42, 0.04);
}

[data-testid="stDataFrame"] {
    border-radius: 16px;
    overflow: hidden;
}

hr {
    margin: 1.2rem 0;
    border-color: rgba(15, 23, 42, 0.08);
}

@media (max-width: 768px) {
    .block-container {
        padding-top: 1rem;
    }

    .compass-hero {
        padding: 1.35rem;
        border-radius: 22px;
    }

    .compass-section {
        padding: 1rem;
        border-radius: 20px;
    }
}
</style>
""",
        unsafe_allow_html=True,
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


def page_hero(title: str, description: str) -> None:
    st.markdown(
        f"""
<div class="compass-hero">
    <div class="compass-kicker">COMPASS AI</div>
    <h1>{title}</h1>
    <p>{description}</p>
</div>
""",
        unsafe_allow_html=True,
    )


def section_header(title: str, caption: str | None = None) -> None:
    caption_html = ""
    if caption:
        caption_html = f'<p class="compass-section-caption">{caption}</p>'

    st.markdown(
        f"""
<div class="compass-section">
    <p class="compass-section-title">{title}</p>
    {caption_html}
</div>
""",
        unsafe_allow_html=True,
    )


def callout(text: str) -> None:
    st.markdown(
        f'<div class="compass-callout">{text}</div>',
        unsafe_allow_html=True,
    )


def metric_cards(
    items: list[tuple[str, Any]],
    columns_count: int | None = None,
) -> None:
    if not items:
        return

    columns_count = columns_count or min(len(items), 5)
    columns = st.columns(columns_count)

    for index, (label, value) in enumerate(items):
        with columns[index % columns_count]:
            st.metric(label, value)


def style_chart(chart: Any, height: int = 360) -> Any:
    chart.update_layout(
        template="plotly_white",
        height=height,
        margin=dict(l=16, r=16, t=34, b=16),
        paper_bgcolor="rgba(255,255,255,0)",
        plot_bgcolor="rgba(255,255,255,0)",
        font=dict(
            family="Inter, SF Pro Display, Arial",
            color="#111827",
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
        ),
    )
    chart.update_xaxes(showgrid=False, zeroline=False)
    chart.update_yaxes(gridcolor="rgba(15,23,42,0.08)", zeroline=False)
    return chart


def show_chart(chart: Any, height: int = 360) -> None:
    st.plotly_chart(style_chart(chart, height=height), width="stretch")


def show_table_expander(
    title: str,
    df: pd.DataFrame,
    columns: list[str] | None = None,
    expanded: bool = False,
) -> None:
    with st.expander(title, expanded=expanded):
        if columns:
            visible_columns = dataframe_columns(df, columns)
            st.dataframe(df[visible_columns], width="stretch")
        else:
            st.dataframe(df, width="stretch")


def mode_selectbox(label: str, key: str | None = None) -> str:
    selected_label = st.selectbox(
        label,
        [MODE_LABELS[mode] for mode in RECOMMENDATION_MODES],
        index=0,
        key=key,
    )
    reverse_labels = {
        label_value: mode
        for mode, label_value in MODE_LABELS.items()
    }
    return reverse_labels[selected_label]


def score_pill(value: Any) -> str:
    score = safe_float(value)
    if score >= 0.80:
        class_name = "compass-pill-green"
    elif score >= 0.60:
        class_name = "compass-pill-blue"
    elif score >= 0.40:
        class_name = "compass-pill-amber"
    else:
        class_name = "compass-pill-red"

    return f'<span class="compass-pill {class_name}">Score {score:.3f}</span>'


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
    page_hero("Overview", PAGE_DESCRIPTIONS["Overview"])

    employees = load_employees()
    tasks = load_tasks()
    assignments = load_assignments()

    if employees.empty or tasks.empty or assignments.empty:
        st.warning("Synthetic data не найдены. Сначала запусти генерацию данных.")
        return

    average_workload = safe_float(
        employees.get("current_workload", pd.Series()).mean(),
    )
    average_success_probability = safe_float(
        assignments.get("success_probability", pd.Series()).mean(),
    )

    if "risk_score" in assignments.columns:
        high_risk_assignments = int((assignments["risk_score"] >= 0.70).sum())
    else:
        high_risk_assignments = 0

    metric_cards(
        [
            ("Synthetic tasks", len(tasks)),
            ("Synthetic employees", len(employees)),
            ("Avg workload", f"{average_workload:.2f}"),
            ("High risk rows", high_risk_assignments),
            ("Avg success probability", f"{average_success_probability:.2f}"),
        ],
    )

    st.divider()

    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        if "project_key" in tasks.columns:
            section_header(
                "Tasks by project",
                "Где сосредоточена synthetic-нагрузка.",
            )
            project_counts = tasks["project_key"].value_counts().reset_index()
            project_counts.columns = ["project_key", "tasks_count"]
            chart = px.bar(
                project_counts,
                x="project_key",
                y="tasks_count",
                color="tasks_count",
                color_continuous_scale="Blues",
            )
            show_chart(chart)

    with chart_col2:
        if "task_type" in tasks.columns:
            section_header(
                "Tasks by type",
                "Какие категории задач чаще встречаются.",
            )
            type_counts = tasks["task_type"].value_counts().reset_index()
            type_counts.columns = ["task_type", "tasks_count"]
            chart = px.bar(
                type_counts,
                x="task_type",
                y="tasks_count",
                color="tasks_count",
                color_continuous_scale="Blues",
            )
            show_chart(chart)

    if "outcome_status" in assignments.columns:
        section_header(
            "Assignment outcomes",
            "Итоги synthetic-назначений в обучающих данных.",
        )
        outcome_counts = assignments["outcome_status"].value_counts().reset_index()
        outcome_counts.columns = ["outcome_status", "count"]
        chart = px.pie(
            outcome_counts,
            names="outcome_status",
            values="count",
            hole=0.62,
            color_discrete_sequence=px.colors.qualitative.Set2,
        )
        show_chart(chart, height=410)

    show_table_expander("Show synthetic tasks table", tasks, expanded=False)
    show_table_expander("Show synthetic employees table", employees, expanded=False)
    show_table_expander(
        "Show synthetic assignments table",
        assignments,
        expanded=False,
    )

    with st.expander("API status", expanded=False):
        show_api_status(api_url)


def issue_recommendations_page(api_url: str) -> None:
    page_hero("Issue Recommendations", PAGE_DESCRIPTIONS["Issue Recommendations"])

    callout(
        "Выбери режим рекомендации один раз сверху. "
        "Дальше можно анализировать synthetic-задачу, "
        "реальную Plane-задачу по ID или ручное описание задачи."
    )

    control_col1, control_col2, control_col3 = st.columns([1.4, 1, 1])
    with control_col1:
        mode = mode_selectbox("Recommendation mode")
    with control_col2:
        top_k = st.slider("Top candidates", min_value=1, max_value=10, value=3)
    with control_col3:
        use_llm = st.checkbox("Use LLM explanation", value=False)

    tab_synthetic, tab_plane, tab_manual = st.tabs(
        ["Synthetic task", "Plane work item by ID", "Manual task"],
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
    section_header(
        "Analyze synthetic task",
        "Быстрый демо-анализ задачи из synthetic dataset.",
    )

    tasks = load_tasks()
    if tasks.empty or "task_id" not in tasks.columns:
        st.warning("tasks.csv не найден или в нём нет колонки task_id.")
        return

    task_options = tasks["task_id"].head(250).tolist()
    task_id = st.selectbox("Synthetic task id", task_options, index=0)

    with st.expander("Preview selected synthetic task", expanded=False):
        selected_task = tasks[tasks["task_id"] == task_id]
        st.dataframe(selected_task, width="stretch")

    if not st.button("Analyze synthetic issue", type="primary"):
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
    section_header(
        "Analyze real Plane work item by ID",
        (
            "Ручной режим для конкретной Plane-задачи. "
            "Для удобного выбора из списка используй Plane Live."
        ),
    )

    with st.expander("Plane work item settings", expanded=True):
        project_id = st.text_input("Plane project id", value=DEFAULT_PLANE_PROJECT_ID)
        work_item_id = st.text_input("Plane work item id")

        advanced_col1, advanced_col2, advanced_col3 = st.columns(3)
        with advanced_col1:
            write_back = st.checkbox(
                "Write recommendation comment to Plane",
                value=False,
            )
        with advanced_col2:
            auto_assign = st.checkbox("Auto assign top candidate", value=False)
        with advanced_col3:
            threshold = st.number_input(
                "Auto assign threshold",
                min_value=0.0,
                max_value=1.0,
                value=0.75,
            )

    if not st.button("Analyze Plane work item by ID", type="primary"):
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
    section_header(
        "Analyze manual task",
        "Опиши задачу вручную и получи AI-рекомендацию без привязки к Plane.",
    )

    with st.expander("Task description", expanded=True):
        title = st.text_input(
            "Task title",
            value="Добавить endpoint для командной аналитики",
        )
        description = st.text_area(
            "Task description",
            value=(
                "Нужно сделать FastAPI endpoint для summary по загрузке "
                "команды и рискам."
            ),
            height=130,
        )

        meta_col1, meta_col2, meta_col3 = st.columns([1, 1.4, 1])
        with meta_col1:
            priority = st.selectbox(
                "Priority",
                ["none", "low", "medium", "high", "urgent"],
                index=3,
            )
        with meta_col2:
            labels = st.text_input("Labels", value="backend, fastapi, feature")
        with meta_col3:
            deadline_days = st.number_input(
                "Deadline days",
                min_value=1,
                max_value=90,
                value=7,
            )

    if not st.button("Analyze manual task", type="primary"):
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
    page_hero("Plane Live", PAGE_DESCRIPTIONS["Plane Live"])

    top_col1, top_col2 = st.columns([1, 2])
    with top_col1:
        if st.button("Refresh Plane data", type="primary"):
            st.cache_data.clear()
            st.rerun()

    with top_col2, st.expander("API status", expanded=False):
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

    metric_cards(
        [
            ("Plane projects", live_data.get("projects_count", len(projects))),
            ("Plane work items", live_data.get("work_items_count", 0)),
            ("Open work items", live_data.get("open_work_items_count", 0)),
            ("Workspace members", live_data.get("workspace_members_count", 0)),
        ],
        columns_count=4,
    )

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

    if not project_labels:
        st.warning("Plane projects вернулись, но payload некорректный.")
        return

    section_header(
        "Select project",
        "Сначала выбери Plane-проект, затем задачу для AI-анализа.",
    )

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

    metric_cards(
        [
            ("Project members", len(members)),
            ("Project work items", len(work_items)),
            (
                "Project open work items",
                int(selected_project.get("open_work_items_count") or 0),
            ),
        ],
        columns_count=3,
    )

    if members:
        members_df = pd.DataFrame(members)
        show_table_expander(
            "Show real Plane project members",
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
    else:
        st.warning("В этом Plane project нет members или API их не вернул.")

    if not work_items:
        st.warning("В этом Plane project нет work items.")
        return

    work_items_df = pd.DataFrame(work_items)
    show_table_expander(
        "Show real Plane work items",
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

    st.divider()

    section_header(
        "Analyze selected work item",
        (
            "Выбери задачу из проекта и запусти рекомендацию. "
            "Таблицы и debug-данные спрятаны ниже."
        ),
    )

    filter_col1, filter_col2 = st.columns([1, 2])
    with filter_col1:
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

    with filter_col2:
        selected_task_label = st.selectbox(
            "Select Plane work item for AI analysis",
            selectable_df["select_label"].tolist(),
        )

    selected_task_row = selectable_df[
        selectable_df["select_label"] == selected_task_label
    ].iloc[0]
    work_item_id = str(selected_task_row.get("id") or "")

    selected_preview = pd.DataFrame(
        [selected_task_row.drop(labels=["select_label"]).to_dict()],
    )
    show_table_expander(
        "Show selected work item details",
        selected_preview,
        expanded=False,
    )

    settings_col1, settings_col2, settings_col3 = st.columns([1.4, 1, 1])
    with settings_col1:
        mode = mode_selectbox("Plane Live recommendation mode", key="plane_live_mode")
    with settings_col2:
        top_k = st.slider(
            "Plane Live Top K",
            min_value=1,
            max_value=10,
            value=3,
        )
    with settings_col3:
        use_llm = st.checkbox("Plane Live: use LLM explanation", value=False)

    with st.expander("Advanced Plane actions", expanded=False):
        action_col1, action_col2, action_col3 = st.columns(3)
        with action_col1:
            write_back = st.checkbox(
                "Plane Live: write comment to Plane",
                value=False,
            )
        with action_col2:
            auto_assign = st.checkbox(
                "Plane Live: auto assign top candidate",
                value=False,
            )
        with action_col3:
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

    if not st.button("Analyze selected Plane work item", type="primary"):
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
    mode_value = MODE_LABELS.get(
        str(response.get("mode")),
        response.get("mode", "n/a"),
    )

    metric_cards(
        [
            ("Task", task_id or plane_work_item_id or "n/a"),
            ("Mode", mode_value),
            ("Top score", f"{top_score:.4f}" if top_score is not None else "n/a"),
            ("Source", candidate.get("source", response.get("source", "n/a"))),
            ("Candidate scope", response.get("candidate_scope", "default")),
        ],
    )

    candidates = response.get("top_candidates") or []

    section_header(
        "Top candidates",
        "Главные рекомендации отсортированы по score. Полная таблица доступна ниже.",
    )

    if isinstance(candidates, list) and candidates:
        candidates_df = pd.DataFrame(candidates)

        for candidate_item in candidates[:3]:
            if not isinstance(candidate_item, dict):
                continue

            rank = candidate_item.get("rank", "n/a")
            name = (
                candidate_item.get("name")
                or candidate_item.get("employee_id")
                or "Unknown candidate"
            )
            role = candidate_item.get("role") or "role n/a"
            grade = candidate_item.get("grade") or "grade n/a"
            source = candidate_item.get("source") or "source n/a"
            success_probability = candidate_item.get("success_probability")

            probability_html = ""
            if success_probability is not None:
                probability_html = (
                    '<span class="compass-pill compass-pill-green">'
                    f"Success {safe_float(success_probability):.3f}</span>"
                )

            st.markdown(
                f"""
<div class="compass-candidate">
    <span class="compass-candidate-rank">#{rank}</span>
    <div class="compass-candidate-name">{name}</div>
    <div class="compass-candidate-meta">{role} · {grade} · {source}</div>
    <div style="margin-top: 0.75rem;">
        {score_pill(candidate_item.get("score"))}
        {probability_html}
    </div>
</div>
""",
                unsafe_allow_html=True,
            )

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
        show_table_expander(
            "Show full candidates table",
            candidates_df,
            visible_columns,
            expanded=False,
        )
    else:
        st.warning("Кандидаты не вернулись.")

    section_header("Explanation", "Краткое объяснение рекомендации.")
    st.markdown(response.get("explanation") or "No explanation")

    with st.expander("Plane live debug", expanded=False):
        st.json(response.get("plane_live", {}))

    with st.expander("Plane write-back debug", expanded=False):
        st.json(response.get("plane_write_back", {}))

    with st.expander("Plane auto-assign debug", expanded=False):
        st.json(response.get("plane_auto_assign", {}))

    with st.expander("Raw response", expanded=False):
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
    page_hero("Synthetic Team Workload", PAGE_DESCRIPTIONS["Synthetic Team Workload"])

    callout(
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
    employees["workload_percent"] = (
        employees["current_workload"].apply(safe_float) * 100
    )
    employees["overload_risk"] = employees["current_workload"].apply(
        workload_risk_level,
    )

    average_workload = safe_float(employees["current_workload"].mean())
    high_risk_count = int((employees["overload_risk"] == "high").sum())
    critical_risk_count = int((employees["overload_risk"] == "critical").sum())

    metric_cards(
        [
            ("Synthetic employees", len(employees)),
            ("Avg workload", f"{average_workload:.2f}"),
            ("High risk", high_risk_count),
            ("Critical risk", critical_risk_count),
        ],
        columns_count=4,
    )

    section_header(
        "Workload by synthetic employee",
        "Самые загруженные участники сверху. Цвет показывает уровень риска.",
    )

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
        color_discrete_map={
            "low": "#16a34a",
            "medium": "#d97706",
            "high": "#dc2626",
            "critical": "#7f1d1d",
        },
    )
    show_chart(chart, height=430)

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

    show_table_expander(
        "Show synthetic team table",
        employees,
        columns,
        expanded=False,
    )


def plane_team_page(api_url: str) -> None:
    page_hero("Plane Team", PAGE_DESCRIPTIONS["Plane Team"])

    callout(
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

    metric_cards(
        [
            (
                "Workspace members",
                response.get("workspace_members_count", len(workspace_members)),
            ),
            (
                "Pending invitations",
                response.get("pending_invitations_count", len(pending_invitations)),
            ),
            ("Projects", len(projects)),
        ],
        columns_count=3,
    )

    if workspace_members:
        members_df = pd.DataFrame(workspace_members)
        show_table_expander(
            "Show active workspace members",
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
            expanded=True,
        )
    else:
        st.warning("Plane API не вернул активных workspace members.")

    if pending_invitations:
        pending_df = pd.DataFrame(pending_invitations)
        show_table_expander(
            "Show pending invitations",
            pending_df,
            [
                "id",
                "email",
                "role",
                "accepted",
                "responded_at",
                "created_at",
            ],
            expanded=False,
        )
    else:
        st.success("Нет pending invitations.")

    section_header(
        "Project members",
        (
            "Участники по проектам спрятаны в раскрывающиеся блоки, "
            "чтобы страница не выглядела как debug-таблица."
        ),
    )

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

        title = f"{project_name} ({project_identifier}) · members: {len(members)}"
        with st.expander(title, expanded=False):
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
    page_hero("Model Metrics", PAGE_DESCRIPTIONS["Model Metrics"])

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
    section_header(
        "Classification metrics",
        "Основные метрики качества binary classification модели.",
    )

    metric_cards(
        [
            ("ROC-AUC", f"{safe_float(model_metrics.get('roc_auc')):.4f}"),
            ("PR-AUC", f"{safe_float(model_metrics.get('pr_auc')):.4f}"),
            ("F1", f"{safe_float(model_metrics.get('f1')):.4f}"),
            ("Precision", f"{safe_float(model_metrics.get('precision')):.4f}"),
            ("Recall", f"{safe_float(model_metrics.get('recall')):.4f}"),
        ],
    )

    with st.expander("Show raw classification metrics", expanded=False):
        st.json(model_metrics)


def show_ranking_metrics(ranking_metrics: dict[str, Any]) -> None:
    section_header(
        "Ranking metrics",
        "Сравнение моделей по качеству ранжирования кандидатов.",
    )

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

    metric_columns = dataframe_columns(
        ranking_df,
        ["precision_at_1", "precision_at_3", "ndcg_at_3", "mrr"],
    )

    if metric_columns:
        long_df = ranking_df.melt(
            id_vars=["model"],
            value_vars=metric_columns,
            var_name="metric",
            value_name="value",
        )
        chart = px.bar(
            long_df,
            x="metric",
            y="value",
            color="model",
            barmode="group",
            color_discrete_sequence=px.colors.qualitative.Set2,
        )
        show_chart(chart, height=420)

    show_table_expander("Show ranking metrics table", ranking_df, expanded=False)


def fairness_page() -> None:
    page_hero("Fairness", PAGE_DESCRIPTIONS["Fairness"])

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

    metric_cards(
        [
            ("Senior assignment share", f"{senior_share:.2f}"),
            ("Junior assignment share", f"{junior_share:.2f}"),
            ("Top employee concentration", f"{top_employee_share:.2f}"),
            ("Avg assigned workload", f"{average_workload:.2f}"),
            ("Growth match share", f"{growth_share:.2f}"),
        ],
    )

    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        section_header("Assignment distribution by grade")
        grade_counts = merged["grade"].value_counts().reset_index()
        grade_counts.columns = ["grade", "assignments"]
        chart = px.bar(
            grade_counts,
            x="grade",
            y="assignments",
            color="grade",
            color_discrete_sequence=px.colors.qualitative.Set2,
        )
        show_chart(chart)

    with chart_col2:
        section_header("Assignment distribution by role")
        role_counts = merged["role"].value_counts().reset_index()
        role_counts.columns = ["role", "assignments"]
        chart = px.bar(
            role_counts,
            x="role",
            y="assignments",
            color="role",
            color_discrete_sequence=px.colors.qualitative.Set2,
        )
        show_chart(chart)

    section_header(
        "Top employee concentration",
        "Проверяем, не забирает ли один участник слишком большую долю назначений.",
    )
    employee_counts = merged["name"].value_counts().head(15).reset_index()
    employee_counts.columns = ["employee", "assignments"]
    chart = px.bar(
        employee_counts,
        x="employee",
        y="assignments",
        color="assignments",
        color_continuous_scale="Blues",
    )
    show_chart(chart, height=430)

    with st.expander("Fairness notes", expanded=False):
        st.markdown(
            """
- Senior share показывает, не забирают ли senior почти все назначения.
- Junior share показывает, не игнорируются ли junior.
- Top employee concentration показывает, нет ли концентрации на одном человеке.
- Avg assigned workload показывает риск усиления перегруза.
- Growth match share показывает долю назначений, полезных для развития.
""",
        )

    show_table_expander("Show merged fairness dataset", merged, expanded=False)


def settings_page(api_url: str) -> None:
    page_hero("Settings", PAGE_DESCRIPTIONS["Settings"])

    section_header(
        "Current dashboard configuration",
        (
            "Служебные параметры спрятаны в аккуратные блоки, "
            "чтобы страница не выглядела как debug-screen."
        ),
    )

    with st.expander("Show dashboard configuration", expanded=True):
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

    section_header("Health check")
    if st.button("Check COMPASS API", type="primary"):
        show_api_status(api_url)

    with st.expander("Required local services", expanded=False):
        st.markdown(
            """
- FastAPI backend: `uvicorn app.api:app --reload --host 0.0.0.0 --port 8000`
- Plane: `./scripts/start_plane.sh`
- Optional LLM: `ollama serve`
- Dashboard: `streamlit run app/dashboard.py`
""",
        )


def main() -> None:
    apply_dashboard_theme()

    st.sidebar.title("COMPASS AI")
    st.sidebar.caption("AI-панель для задач, команды, Plane и качества рекомендаций.")

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

    st.sidebar.divider()
    st.sidebar.caption(PAGE_DESCRIPTIONS.get(page, ""))

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