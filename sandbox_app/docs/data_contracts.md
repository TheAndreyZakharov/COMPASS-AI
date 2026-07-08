# Sandbox data contracts

This document defines the canonical data formats used by COMPASS AI Sandbox.

The source of truth is:

sandbox_app/config/data_contracts/data_contracts.json

The backend loader is:

sandbox_app/backend/core/data_contracts.py

The API router is:

sandbox_app/backend/api/contracts.py

## Supported storage formats

CSV is used for simple flat tables that humans can inspect quickly.

JSON is used for nested structures, metadata, sessions, recommendations, reports, configs, and API payloads.

Parquet is used for large training datasets, feature matrices, targets, and predictions.

## Contracts

### employees

Team members used for generation, history, features, training, and recommendations.

Required core fields:

- employee_id
- name
- role
- grade
- skills
- availability_score
- current_workload
- fatigue_score
- avg_completion_speed
- avg_quality_score
- deadline_reliability
- mentor_level

Primary storage:

- employees.csv
- employees.json

### tasks

Tasks used as historical assignments, generated backlog, and recommendation inputs.

Required core fields:

- task_id
- title
- project_id
- task_type
- status
- priority
- complexity
- estimated_hours
- deadline_days
- required_skills

Allowed statuses:

- todo
- in_progress
- review
- done
- blocked
- failed

Primary storage:

- tasks.csv
- tasks.json

### assignment_history

Historical assignment outcomes used to learn task-employee fit.

Required core fields:

- assignment_id
- employee_id
- task_id
- assigned_at
- completed_at
- planned_hours
- actual_hours
- quality_score
- deadline_status
- outcome_label
- was_rework_needed
- feedback_score

Allowed deadline statuses:

- early
- on_time
- late
- missed

Allowed outcome labels:

- success
- good
- acceptable
- late
- failed
- rework

Primary storage:

- assignment_history.csv
- assignment_history.json

### training_pairs

Large task-employee candidate-pair dataset for model training.

Required core fields:

- pair_id
- task_id
- employee_id
- label
- target_score
- target_mode

Primary storage:

- training_pairs.parquet

### current_team

Current team snapshot used by Assignment Lab and recommendation tests.

It reuses employee required fields and adds optional runtime fields such as active_task_ids, weekly_capacity_hours, and available_from.

Primary storage:

- team.csv
- team.json

### current_backlog

Current todo backlog used by single recommendation and bulk assignment.

It reuses task required fields and constrains status to todo.

Primary storage:

- backlog.csv
- backlog.json

### recommendations

Single-task recommendation output and candidate ranking explanation inputs.

Required core fields:

- recommendation_id
- task_id
- model_id
- recommendation_mode
- generated_at
- candidates

Candidate required fields:

- employee_id
- rank
- score
- factors
- risks

Allowed recommendation modes:

- best_quality
- fastest_delivery
- best_learning
- balanced
- risk_aware

Qwen or Ollama explanations may populate explanation_ru but must not change ranking or invent candidates.

### training_session

Reproducible model training run.

Required core fields:

- session_id
- dataset_id
- status
- started_at
- target_mode
- models
- metrics
- artifacts_dir

Primary storage:

- session_summary.json

### assignment_session

Bulk assignment simulation run.

Required core fields:

- session_id
- test_case_id
- model_id
- status
- assignment_mode
- started_at
- assigned_tasks_count
- unassigned_tasks_count
- artifacts_dir

Primary storage:

- assignment_config.json

### dataset_metadata

Dataset-level metadata for generated and imported datasets.

Required core fields:

- dataset_id
- dataset_type
- domain_profile
- created_at
- seed
- counts
- files

Primary storage:

- dataset_metadata.json

## API

List all contracts:

GET /api/contracts

Get short summary:

GET /api/contracts/summary

Get one contract:

GET /api/contracts/{contract_name}

Examples:

GET /api/contracts/employees
GET /api/contracts/tasks
GET /api/contracts/assignment_history
GET /api/contracts/training_pairs
GET /api/contracts/recommendations
GET /api/contracts/dataset_metadata

## Validation rules

The backend validates that:

- all required top-level keys exist
- all required contract names exist
- csv, json, and parquet formats are defined
- required shared enums are non-empty
- every contract has description, primary_key, storage, and required fields or required_fields_ref

Record-level required-field validation is provided by validate_record_required_fields and will be reused by importers and generators.