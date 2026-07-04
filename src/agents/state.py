from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

RecommendationMode = Literal[
    "fast_delivery",
    "balanced_workload",
    "growth",
    "risk_minimization",
]


@dataclass
class AgentError:
    step: str
    message: str


@dataclass
class AgentState:
    issue: dict[str, Any] | None = None
    task_features: dict[str, Any] = field(default_factory=dict)
    employees: list[dict[str, Any]] = field(default_factory=list)
    employee_features: list[dict[str, Any]] = field(default_factory=list)
    candidate_scores: list[dict[str, Any]] = field(default_factory=list)
    top_candidates: list[dict[str, Any]] = field(default_factory=list)
    recommendation_mode: RecommendationMode = "balanced_workload"
    explanation: str = ""
    final_response: dict[str, Any] = field(default_factory=dict)
    errors: list[AgentError] = field(default_factory=list)

    def add_error(self, step: str, message: str) -> None:
        self.errors.append(AgentError(step=step, message=message))

    def has_errors(self) -> bool:
        return bool(self.errors)

    def error_payload(self) -> list[dict[str, str]]:
        return [
            {
                "step": error.step,
                "message": error.message,
            }
            for error in self.errors
        ]


def normalize_mode(mode: str | None) -> RecommendationMode:
    allowed_modes: set[str] = {
        "fast_delivery",
        "balanced_workload",
        "growth",
        "risk_minimization",
    }

    if mode in allowed_modes:
        return mode  # type: ignore[return-value]

    return "balanced_workload"