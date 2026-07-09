# Sandbox end-to-end pipeline checklist

Цель: вручную пройти полный рабочий цикл песочницы в браузере после backend tests.

## Browser scenario

1. Open browser app.
2. Create custom schema.
3. Generate full dataset.
4. Open Data Viewer.
5. Build features.
6. Train models.
7. Save training session.
8. Open model session.
9. Generate test team.
10. Run single recommendation.
11. Run bulk assignment.
12. Enable Qwen explanations.
13. Save assignment session.
14. Open Reports.
15. Export results.

## Expected result

- Backend status is Online.
- Settings page opens.
- Custom schema can be created without manual JSON editing.
- Full dataset generation returns dataset_id.
- Data Viewer opens generated dataset.
- Feature builder creates feature metadata.
- Training creates a training session.
- Models page opens saved model artifacts.
- Assignment Lab creates test case.
- Single recommendation returns top candidates.
- Bulk assignment creates assignment session.
- Qwen explanation checkbox does not change ranking.
- Reports page shows exports.
- Dataset, model and assignment exports can be generated.
- Main COMPASS API is not modified by sandbox flow.

## Terminal checks

Run full pytest suite:

python -m pytest sandbox_app/tests

Run backend smoke test:

bash sandbox_app/scripts/smoke_test.sh