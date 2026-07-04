from src.recommendation.skill_matching import (
    calculate_skill_match,
    parse_employee_skills,
    parse_required_skills,
    skill_match_score,
)


def test_parse_employee_skills_from_json_string() -> None:
    employee = {"skills": '{"Python": 4, "FastAPI": 3}'}

    skills = parse_employee_skills(employee)

    assert skills["python"] == 4
    assert skills["fastapi"] == 3


def test_parse_required_skills_from_list() -> None:
    task = {"required_skills": '["Python", "FastAPI"]'}

    required = parse_required_skills(task)

    assert required == {"python": 3.0, "fastapi": 3.0}


def test_skill_match_is_high_for_good_candidate() -> None:
    task = {"required_skills": '{"Python": 4, "FastAPI": 3}'}
    employee = {"skills": '{"Python": 5, "FastAPI": 4}'}

    result = calculate_skill_match(task, employee)

    assert result.score > 0.9
    assert "python" in result.matched_skills
    assert "fastapi" in result.matched_skills
    assert result.missing_skills == []


def test_skill_match_detects_missing_skills() -> None:
    task = {"required_skills": '{"Python": 4, "FastAPI": 3, "PostgreSQL": 3}'}
    employee = {"skills": '{"Python": 4}'}

    result = calculate_skill_match(task, employee)

    assert result.score < 0.6
    assert "fastapi" in result.missing_skills
    assert "postgresql" in result.missing_skills


def test_skill_match_score_returns_float_between_zero_and_one() -> None:
    task = {"required_skills": '{"Python": 4}'}
    employee = {"skills": '{"Python": 2}'}

    score = skill_match_score(task, employee)

    assert 0 <= score <= 1