from src.recommendation.workload_scoring import (
    calculate_workload_score,
    normalize_workload,
    workload_penalty,
    workload_score,
)


def test_normalize_workload_accepts_fraction() -> None:
    assert normalize_workload(0.75) == 0.75


def test_normalize_workload_accepts_percent() -> None:
    assert normalize_workload(75) == 0.75


def test_low_workload_gets_high_score() -> None:
    employee = {"current_workload": 0.25, "active_tasks_count": 1, "availability": 1.0}

    result = calculate_workload_score(employee)

    assert result.score > 0.7
    assert result.risk_level == "low"


def test_high_workload_gets_penalty() -> None:
    employee = {"current_workload": 0.9, "active_tasks_count": 6, "availability": 1.0}

    result = calculate_workload_score(employee)

    assert result.score < 0.1
    assert result.risk_level == "high"


def test_critical_workload_gets_critical_risk() -> None:
    employee = {"current_workload": 0.97, "active_tasks_count": 9, "availability": 1.0}

    result = calculate_workload_score(employee)

    assert result.risk_level == "critical"
    assert "critical workload" in result.reasons


def test_workload_score_and_penalty_are_complementary() -> None:
    employee = {"current_workload": 0.5, "active_tasks_count": 2, "availability": 1.0}

    score = workload_score(employee)
    penalty = workload_penalty(employee)

    assert round(score + penalty, 4) == 1.0