# COMPASS AI Sandbox

Autonomous local sandbox for generating synthetic teams, generating tasks, building training datasets, training assignment models, testing recommendations, running bulk assignment simulations, and explaining results through local Ollama/Qwen.

## Status

This directory is intentionally isolated from the main COMPASS AI application.

The sandbox must not import main project agents, main project LLM clients, or mutate the main COMPASS API.

## Runtime

Target Python: 3.11.x

Expected local environment:

- project `.venv`
- browser UI
- FastAPI backend
- HTML/CSS/JS frontend
- local files for generated data, models, sessions, reports, and logs

## Main folders

- `backend` — sandbox backend modules
- `frontend` — browser UI
- `config` — app settings, feature schemas, model presets
- `data/generated` — generated datasets
- `data/imported` — imported datasets
- `data/test_cases` — generated test teams and backlogs
- `data/exports` — exported results
- `training_sessions` — saved model training sessions
- `assignment_sessions` — saved recommendation and bulk assignment sessions
- `reports` — HTML/JSON/CSV reports
- `logs` — local runtime logs
- `tests` — sandbox tests

## Roadmap position

This file belongs to milestone 27.1: autonomous sandbox app structure.

Run scripts, backend endpoints, frontend pages, data generation, training, inference, reports, and Qwen explanations are implemented in later milestone items.