from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

RecommendationMode = Literal[
    "fast_delivery",
    "balanced_workload",
    "growth",
    "risk_minimization",
]


class HealthResponse(BaseModel):
    status: str
    service: str


class VersionResponse(BaseModel):
    service: str
    version: str
    environment: str


class TaskInput(BaseModel):
    task_id: str | None = None
    plane_work_item_id: str | None = None
    plane_issue_id: str | None = None
    plane_project_id: str | None = None
    project_key: str | None = None
    title: str
    description: str = ""
    task_type: str | None = None
    required_stack: list[str] = Field(default_factory=list)
    required_skills: dict[str, int] = Field(default_factory=dict)
    complexity: int | None = None
    priority: str = "medium"
    business_criticality: int | None = None
    deadline_days: int | None = None
    estimated_hours: float | None = None
    dependencies_count: int | None = None
    is_growth_task: bool = False


class EmployeeInput(BaseModel):
    employee_id: str
    plane_user_id: str | None = None
    name: str
    role: str
    grade: str
    experience_years: float
    primary_stack: str | None = None
    skills: dict[str, int] = Field(default_factory=dict)
    current_workload: float
    active_tasks_count: int = 0
    avg_completion_speed: float
    avg_quality_score: float
    deadline_reliability: float
    learning_goals: list[str] = Field(default_factory=list)
    mentor_level: int = 0
    availability: str = "available"
    timezone: str | None = None


class RecommendationRequest(BaseModel):
    task: TaskInput
    employees: list[EmployeeInput] | None = None
    mode: RecommendationMode = "balanced_workload"
    top_k: int = 3


class CandidateRecommendation(BaseModel):
    rank: int
    employee_id: str
    plane_user_id: str | None = None
    name: str
    role: str
    grade: str
    score: float
    reasons: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    factors: dict[str, Any] = Field(default_factory=dict)


class RecommendationResponse(BaseModel):
    task_id: str | None = None
    plane_work_item_id: str | None = None
    plane_issue_id: str | None = None
    title: str
    mode: RecommendationMode
    candidates: list[CandidateRecommendation]
    source: str
    explanation: str | None = None


class ExplanationResponse(BaseModel):
    text: str
    used_llm: bool
    fallback: bool = False


class AnalyticsSummary(BaseModel):
    employees_count: int
    tasks_count: int
    assignments_count: int
    average_workload: float | None = None
    average_skill_match: float | None = None
    average_risk_score: float | None = None
    success_rate: float | None = None
    failed_rate: float | None = None
    tasks_by_project: dict[str, int] = Field(default_factory=dict)
    tasks_by_type: dict[str, int] = Field(default_factory=dict)
    assignments_by_outcome: dict[str, int] = Field(default_factory=dict)
    assignments_by_scenario: dict[str, int] = Field(default_factory=dict)
