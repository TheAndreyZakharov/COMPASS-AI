# Sandbox Data Contracts

This document describes canonical data contracts for COMPASS AI Sandbox.

The contracts are stored in `sandbox_app/config/data_contracts/data_contracts.json`.

## Main entities

- employees
- tasks
- assignment_history
- training_pairs
- current_team
- current_backlog
- recommendations
- training_session
- assignment_session
- dataset_metadata

## Storage formats

CSV is used for simple tabular data and quick inspection.

JSON is used for nested structures, metadata, recommendations, sessions, and test cases.

Parquet is used for large training datasets and feature matrices.

## Domain flexibility

Roles, grades, skills, employee custom features, task custom features, and outcome features are domain-specific.

The same contract can support software developers, designers, doctors, lawyers, teachers, operations teams, or any other custom team type.

Domain-specific names are controlled by feature schemas and generated/imported datasets.