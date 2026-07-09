# Sandbox final readiness checklist

Цель: финально подтвердить, что этап 25 с автономной песочницей закрыт.

## Runtime readiness

1. sandbox_app exists as an autonomous subproject.
2. Backend starts with scripts/start.sh.
3. Backend stops with scripts/stop.sh.
4. Backend restarts with scripts/restart.sh.
5. Smoke test passes with scripts/smoke_test.sh.
6. Browser opens http://127.0.0.1:8601.
7. Backend binds only to 127.0.0.1:8601.
8. PID is stored in sandbox_app/logs.
9. Logs are stored in sandbox_app/logs.

## Product readiness

1. UI uses HTML, CSS and Vanilla JS.
2. Backend uses FastAPI.
3. Main COMPASS API is not modified by sandbox flow.
4. Custom schemas can be created.
5. Team generator works.
6. Task generator works.
7. History generator works.
8. Full dataset generator works.
9. Huge generation requires confirmation.
10. Data Viewer opens generated datasets.
11. Data Viewer shows tables.
12. Data Viewer shows kanban.
13. Import Data supports external datasets.
14. Feature builder creates training features.
15. Training runs multiple models.
16. Every training run creates a session.
17. Model artifacts are saved.
18. Training plots are saved as PNG.
19. Reports are saved.
20. Test team can be generated.
21. Single task recommendation works.
22. Bulk todo assignment works.
23. Qwen explanations can be enabled.
24. Fallback explanation works without LLM.
25. Exports are available.
26. Tests are present.
27. README exists.

## Final terminal checks

Run compileall:

python -m compileall -q sandbox_app/backend sandbox_app/tests

Run all tests:

pytest sandbox_app/tests

Run ruff when installed:

python -m ruff check sandbox_app

Run smoke test:

bash sandbox_app/scripts/smoke_test.sh

## Browser scenario

1. Open Dashboard.
2. Confirm backend status is online.
3. Open Settings.
4. Confirm schemas are visible.
5. Generate small_preview dataset.
6. Open Data Viewer.
7. Open Summary, tables and kanban.
8. Build features.
9. Train baseline, logistic regression and random forest.
10. Open Models.
11. Validate model artifact.
12. Generate test case.
13. Run single recommendation.
14. Enable Qwen explanations.
15. Run bulk assignment.
16. Open Reports.
17. Generate exports.

## Expected result

Sandbox is ready when the user can configure a domain schema, generate data, train models, create a test team, assign tasks, enable explanations and export reports without touching the main COMPASS API.