from __future__ import annotations

from sandbox_app.backend.llm.qwen_explainer import (
    ExplanationError,
    explain_assignment_session,
    explain_recommendation,
    validate_candidate_references,
)


def recommendation_payload() -> dict[str, object]:
    return {
        "recommendation_id": "rec_test",
        "recommendation_mode": "balanced",
        "model_name": "logistic_regression",
        "task": {
            "task_id": "task_1",
            "title": "Build API",
            "required_skills": ["python", "fastapi"],
        },
        "candidates": [
            {
                "employee_id": "emp_1",
                "name": "Anna",
                "role": "Backend Engineer",
                "grade": "senior",
                "score": 0.91,
                "model_score": 0.88,
                "matched_skills": ["python", "fastapi"],
                "missing_skills": [],
                "factors": {
                    "skill_match_ratio": 1.0,
                    "quality_fit_score": 0.9,
                    "speed_fit_score": 0.8,
                    "learning_fit_score": 0.4,
                    "risk_fit_score": 0.9,
                    "workload_pressure": 0.3,
                    "fatigue_risk": 0.2,
                    "availability_gap": 0.1,
                },
                "risks": [
                    {
                        "type": "none",
                        "level": "low",
                        "message": "Критичных рисков не обнаружено.",
                    }
                ],
            }
        ],
    }


def test_recommendation_fallback_without_llm() -> None:
    result = explain_recommendation(
        recommendation=recommendation_payload(),
        use_llm=False,
    )

    assert result["status"] == "fallback"
    assert result["llm_used"] is False
    assert result["language"] == "ru"
    assert result["ranking_source"] == "model_output_unchanged"
    assert "Anna" in result["summary"]


def test_assignment_fallback_without_llm() -> None:
    result = explain_assignment_session(
        assignment_session={
            "assignment_session_id": "assignment_test",
            "summary": {
                "assigned_tasks": 5,
                "unassigned_tasks": 1,
            },
            "fairness_report": {
                "assignment_spread": 2,
                "max_projected_workload": 0.82,
            },
        },
        use_llm=False,
    )

    assert result["status"] == "fallback"
    assert result["llm_used"] is False
    assert result["language"] == "ru"
    assert "Назначено задач" in result["summary"]


def test_candidate_reference_validation_rejects_unknown_candidate() -> None:
    candidates = recommendation_payload()["candidates"]

    try:
        validate_candidate_references(
            parsed={
                "candidate_explanations": [
                    {
                        "employee_id": "unknown_emp",
                        "explanation": "bad",
                    }
                ]
            },
            candidates=candidates,  # type: ignore[arg-type]
        )
    except ExplanationError as exc:
        assert "unknown employee_id" in str(exc)
    else:
        raise AssertionError("unknown candidate must be rejected")