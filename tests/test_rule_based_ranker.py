import pandas as pd

from src.recommendation.rule_based_ranker import (
    rank_employees_for_task,
    recommendation_to_dict,
    role_affinity_score,
    score_employee_for_task,
)


def test_role_affinity_is_high_for_matching_backend_role() -> None:
    task = {"task_type": "backend_feature"}
    employee = {"role": "backend_developer"}

    assert role_affinity_score(task, employee) == 1.0


def test_role_affinity_penalizes_wrong_role() -> None:
    task = {"task_type": "ml_pipeline"}
    employee = {"role": "frontend_developer"}

    assert role_affinity_score(task, employee) == 0.25


def test_score_employee_for_task_returns_candidate_score() -> None:
    task = {
        "task_id": "TASK-1",
        "title": "Test task",
        "task_type": "backend_feature",
        "required_skills": '{"Python": 4, "FastAPI": 3}',
        "complexity": 3,
    }
    employee = {
        "employee_id": "EMP-1",
        "name": "Test Employee",
        "role": "backend_developer",
        "grade": "middle",
        "skills": '{"Python": 5, "FastAPI": 4}',
        "current_workload": 0.3,
        "active_tasks_count": 2,
        "availability": 1.0,
        "avg_completion_speed": 0.8,
        "avg_quality_score": 0.9,
        "deadline_reliability": 0.85,
        "learning_goals": '["FastAPI"]',
    }

    candidate = score_employee_for_task(task, employee)

    assert 0 <= candidate.score <= 1
    assert candidate.employee_id == "EMP-1"
    assert candidate.reasons


def test_rank_employees_for_task_returns_top_3_sorted() -> None:
    task = {
        "task_id": "TASK-1",
        "title": "Backend task",
        "task_type": "backend_feature",
        "required_skills": '{"Python": 4, "FastAPI": 3}',
        "complexity": 3,
    }
    employees = pd.DataFrame(
        [
            {
                "employee_id": "EMP-1",
                "name": "Strong Backend",
                "role": "backend_developer",
                "grade": "senior",
                "skills": '{"Python": 5, "FastAPI": 5}',
                "current_workload": 0.3,
                "active_tasks_count": 2,
                "availability": 1.0,
                "avg_completion_speed": 0.9,
                "avg_quality_score": 0.95,
                "deadline_reliability": 0.9,
                "learning_goals": '["System Design"]',
            },
            {
                "employee_id": "EMP-2",
                "name": "Overloaded Backend",
                "role": "backend_developer",
                "grade": "senior",
                "skills": '{"Python": 5, "FastAPI": 5}',
                "current_workload": 0.98,
                "active_tasks_count": 9,
                "availability": 1.0,
                "avg_completion_speed": 0.9,
                "avg_quality_score": 0.95,
                "deadline_reliability": 0.9,
                "learning_goals": '["System Design"]',
            },
            {
                "employee_id": "EMP-3",
                "name": "Frontend",
                "role": "frontend_developer",
                "grade": "middle",
                "skills": '{"React": 5, "TypeScript": 5}',
                "current_workload": 0.2,
                "active_tasks_count": 1,
                "availability": 1.0,
                "avg_completion_speed": 0.8,
                "avg_quality_score": 0.8,
                "deadline_reliability": 0.8,
                "learning_goals": '["React"]',
            },
        ]
    )

    recommendation = rank_employees_for_task(task, employees, top_k=3)

    assert len(recommendation.candidates) == 3
    assert recommendation.candidates[0].score >= recommendation.candidates[1].score
    assert recommendation.candidates[1].score >= recommendation.candidates[2].score
    assert recommendation.candidates[0].employee_id == "EMP-1"


def test_recommendation_to_dict_returns_serializable_dict() -> None:
    task = {
        "task_id": "TASK-1",
        "title": "Backend task",
        "task_type": "backend_feature",
        "required_skills": '{"Python": 4}',
        "complexity": 2,
    }
    employees = [
        {
            "employee_id": "EMP-1",
            "name": "Backend",
            "role": "backend_developer",
            "grade": "middle",
            "skills": '{"Python": 5}',
            "current_workload": 0.3,
            "active_tasks_count": 2,
            "availability": 1.0,
            "avg_completion_speed": 0.8,
            "avg_quality_score": 0.9,
            "deadline_reliability": 0.85,
            "learning_goals": '["Python"]',
        }
    ]

    recommendation = rank_employees_for_task(task, employees, top_k=1)
    payload = recommendation_to_dict(recommendation)

    assert payload["task_id"] == "TASK-1"
    assert payload["source"] == "rule_based_baseline"
    assert len(payload["candidates"]) == 1