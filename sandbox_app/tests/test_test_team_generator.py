from __future__ import annotations

import shutil

from sandbox_app.backend.data_generation.test_team import (
    TEST_CASES_DIR,
    TestTeamConfig,
    active_todo_tasks,
    build_test_case_summary,
    delete_test_case,
    generate_test_case,
    list_test_cases,
    load_test_case,
    recommendation_context,
)


def test_generate_load_and_delete_test_case() -> None:
    test_case_id = "pytest_test_team_generator"
    test_case_dir = TEST_CASES_DIR / test_case_id

    if test_case_dir.exists():
        shutil.rmtree(test_case_dir)

    result = generate_test_case(
        TestTeamConfig(
            test_case_id=test_case_id,
            domain_profile="developers",
            people_count=6,
            active_tasks_count=9,
            history_depth=4,
            seed=27021,
            overwrite=True,
        )
    )

    assert result["test_case_id"] == test_case_id
    assert (test_case_dir / "team.json").exists()
    assert (test_case_dir / "active_tasks.json").exists()
    assert (test_case_dir / "history.json").exists()
    assert (test_case_dir / "metadata.json").exists()

    loaded = load_test_case(test_case_id)
    assert len(loaded["team"]) == 6
    assert len(loaded["active_tasks"]) == 9
    assert len(loaded["history"]) == 24

    summary = build_test_case_summary(test_case_id)
    assert summary["test_case_id"] == test_case_id
    assert len(summary["capacity"]) == 6
    assert summary["metadata"]["recommendation_ready"] is True

    pending_tasks = active_todo_tasks(test_case_id)
    assert len(pending_tasks) == 9

    context = recommendation_context(test_case_id)
    assert context["team_size"] == 6
    assert context["active_tasks_count"] == 9
    assert context["history_rows"] == 24
    assert context["estimated_pending_hours"] > 0

    listing = list_test_cases()
    assert any(item["test_case_id"] == test_case_id for item in listing["test_cases"])

    deleted = delete_test_case(test_case_id)
    assert deleted["deleted"] is True
    assert not test_case_dir.exists()