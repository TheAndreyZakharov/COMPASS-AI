# COMPASS AI Sandbox

Autonomous local sandbox for COMPASS-AI experiments.

## Purpose

The sandbox lives entirely inside sandbox_app and is isolated from the main COMPASS API, src modules, main LLM modules, and agent modules.

It is designed for the full local experiment cycle:

- configurable domain feature schemas
- synthetic team and backlog generation
- assignment history generation
- large training dataset generation
- data viewing in a browser
- multi-model training
- training sessions and model artifacts
- recommendations and bulk assignment simulation
- reports, exports, and Russian Qwen/Ollama explanations

## Runtime

Target Python version: 3.11.x.

Expected project environment:

source .venv/bin/activate

The sandbox has its own requirements.txt but uses the existing project .venv.

## Structure

backend contains sandbox-only backend code.
frontend contains browser UI files.
config contains sandbox settings, model presets, data contracts, and feature schemas.
data contains generated, imported, test case, and export data.
training_sessions stores reproducible training runs.
assignment_sessions stores bulk assignment runs.
reports stores generated reports.
logs stores runtime logs and pid files.
tests contains sandbox tests.

## Roadmap

27.1 creates the autonomous structure and validated JSON/Python foundations.
27.2 adds local run, stop, restart, smoke test, and Makefile commands.
27.3 adds the FastAPI backend foundation.
