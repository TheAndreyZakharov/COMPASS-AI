from __future__ import annotations

import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from src.api.plane import router as plane_router
from src.api.recommendations import router as recommendations_router
from src.models.schemas import (
    AnalyticsSummary,
    HealthResponse,
    RecommendationResponse,
    VersionResponse,
)
from src.recommendation.demo_ranker import get_demo_recommendation

PROJECT_ROOT = Path(__file__).resolve().parents[1]
EMPLOYEES_CSV_PATH = PROJECT_ROOT / "data" / "synthetic" / "employees.csv"
TASKS_CSV_PATH = PROJECT_ROOT / "data" / "synthetic" / "tasks.csv"
ASSIGNMENTS_CSV_PATH = PROJECT_ROOT / "data" / "synthetic" / "assignments.csv"

APP_VERSION = "0.1.0"

load_dotenv(PROJECT_ROOT / ".env")

app = FastAPI(
    title="COMPASS AI API",
    version=APP_VERSION,
    description="Competency-Oriented Matching & Project Assignment Support System",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost",
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8501",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(recommendations_router)
app.include_router(plane_router)


def synthetic_data_ready() -> bool:
    return (
        EMPLOYEES_CSV_PATH.exists()
        and TASKS_CSV_PATH.exists()
        and ASSIGNMENTS_CSV_PATH.exists()
    )


def value_counts_as_dict(series: pd.Series) -> dict[str, int]:
    counts = series.value_counts().sort_index()
    return {str(key): int(value) for key, value in counts.items()}


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok", service="compass-ai")


@app.get("/version", response_model=VersionResponse)
def version() -> VersionResponse:
    return VersionResponse(
        service="compass-ai",
        version=APP_VERSION,
        environment=os.getenv("APP_ENV", "local"),
    )


@app.get("/recommendations/demo", response_model=RecommendationResponse)
def recommendations_demo(
    mode: str = Query(default="balanced_workload"),
    task_id: str | None = Query(default=None),
    top_k: int = Query(default=3, ge=1, le=10),
) -> RecommendationResponse:
    try:
        return get_demo_recommendation(
            mode=mode,
            task_id=task_id,
            top_k=top_k,
        )
    except (FileNotFoundError, ValueError) as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/reports/summary", response_model=AnalyticsSummary)
def reports_summary() -> AnalyticsSummary:
    if not synthetic_data_ready():
        raise HTTPException(
            status_code=500,
            detail="Synthetic data is missing. Run make generate-data first.",
        )

    employees = pd.read_csv(EMPLOYEES_CSV_PATH)
    tasks = pd.read_csv(TASKS_CSV_PATH)
    assignments = pd.read_csv(ASSIGNMENTS_CSV_PATH)

    return AnalyticsSummary(
        employees_count=len(employees),
        tasks_count=len(tasks),
        assignments_count=len(assignments),
        average_workload=round(float(employees["current_workload"].mean()), 3),
        average_skill_match=round(float(assignments["skill_match_score"].mean()), 3),
        average_risk_score=round(float(assignments["risk_score"].mean()), 3),
        success_rate=round(float(assignments["success_label"].mean()), 3),
        failed_rate=round(1.0 - float(assignments["success_label"].mean()), 3),
        tasks_by_project=value_counts_as_dict(tasks["project_key"]),
        tasks_by_type=value_counts_as_dict(tasks["task_type"]),
        assignments_by_outcome=value_counts_as_dict(assignments["outcome_status"]),
        assignments_by_scenario=value_counts_as_dict(assignments["assignment_scenario"]),
    )