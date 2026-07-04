from src.recommendation.growth_scoring import (
    calculate_growth_score,
    complexity_fit_score,
    growth_score,
    parse_learning_goals,
)


def test_parse_learning_goals_from_json_string() -> None:
    employee = {"learning_goals": '["FastAPI", "PostgreSQL"]'}

    goals = parse_learning_goals(employee)

    assert goals == ["fastapi", "postgresql"]


def test_growth_score_is_high_when_task_matches_learning_goals() -> None:
    task = {"required_skills": '{"FastAPI": 3, "PostgreSQL": 3}', "complexity": 3}
    employee = {"learning_goals": '["FastAPI", "PostgreSQL"]', "grade": "middle"}

    result = calculate_growth_score(task, employee)

    assert result.score > 0.8
    assert "fastapi" in result.matched_learning_goals
    assert "postgresql" in result.matched_learning_goals


def test_complexity_fit_penalizes_too_hard_task_for_junior() -> None:
    task = {"complexity": 5}
    employee = {"grade": "junior"}

    assert complexity_fit_score(task, employee) == 0.2


def test_mentor_support_adds_bonus() -> None:
    task = {"required_skills": '{"FastAPI": 3}', "complexity": 3}
    employee = {"learning_goals": '["FastAPI"]', "grade": "junior"}

    without_mentor = growth_score(task, employee, mentor_available=False)
    with_mentor = growth_score(task, employee, mentor_available=True)

    assert with_mentor > without_mentor


def test_growth_score_returns_float_between_zero_and_one() -> None:
    task = {"required_skills": '{"React": 3}', "complexity": 2}
    employee = {"learning_goals": '["FastAPI"]', "grade": "middle"}

    score = growth_score(task, employee)

    assert 0 <= score <= 1