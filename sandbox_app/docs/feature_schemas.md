# Sandbox feature schemas

Feature schemas define domain-specific roles, grades, skills, task types, and custom features for employees, tasks, and outcomes.

The source directory is:

sandbox_app/config/feature_schemas

The backend loader and validator is:

sandbox_app/backend/features/schema.py

The API router is:

sandbox_app/backend/api/feature_schemas.py

## Built-in profiles

### developers

System profile for software engineering teams.

It cannot be deleted because system is true.

### designers

System profile for product, UX, UI, research, brand, and design system teams.

It cannot be deleted because system is true.

### custom

Free editable profile for any domain.

Examples:

- medicine
- law
- sales
- design
- development
- education
- operations

## Feature groups

Every profile has three feature groups:

- employee
- task
- outcome

Employee features describe people.

Task features describe work items.

Outcome features describe completed assignment results.

## Supported feature types

numeric:

- optional min
- optional max

categorical:

- required values list

boolean:

- true or false

text:

- free text

skill_list:

- list of strings

## Validation

profile_id must start with a lowercase letter and contain only lowercase letters, digits, underscores, or hyphens.

feature names must start with a lowercase letter and contain only lowercase letters, digits, or underscores.

Allowed feature groups:

- employee
- task
- outcome

Allowed feature types:

- numeric
- categorical
- boolean
- text
- skill_list

Only developers and designers may have system true.

System profiles cannot be deleted.

## API

List schemas:

GET /api/feature-schemas

List previews:

GET /api/feature-schemas?preview=true

Get one schema:

GET /api/feature-schemas/{profile_id}

Get one schema with preview:

GET /api/feature-schemas/{profile_id}?preview=true

Get template:

GET /api/feature-schemas/template?profile_id=medicine&name=Medicine

Create schema:

POST /api/feature-schemas

Update schema:

PUT /api/feature-schemas/{profile_id}

Delete non-system schema:

DELETE /api/feature-schemas/{profile_id}

Add feature:

POST /api/feature-schemas/{profile_id}/features/{group}

Patch or rename feature:

PATCH /api/feature-schemas/{profile_id}/features/{group}/{feature_name}

Delete feature:

DELETE /api/feature-schemas/{profile_id}/features/{group}/{feature_name}

## Patch feature payload examples

Rename feature:

{
  "new_name": "patient_complexity"
}

Change numeric range:

{
  "min": 0,
  "max": 100
}

Change categorical values:

{
  "values": ["low", "medium", "high"]
}

## Generator integration

Generators must load the selected domain_profile through the feature schema loader and use:

- roles
- grades
- skills
- task_types
- employee feature definitions
- task feature definitions
- outcome feature definitions

No generator should hardcode domain-specific features when a selected schema exists.