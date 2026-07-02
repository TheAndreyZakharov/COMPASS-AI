# COMPASS AI synthetic data design

## Goal

This document defines the synthetic data model for COMPASS AI.

The synthetic data must support:

- realistic team profiles;
- realistic task generation;
- historical assignment generation;
- supervised learning for `TaskEmployeeMatchingNet`;
- rule-based recommendation baselines;
- workload analysis;
- growth-oriented recommendations;
- fairness analysis;
- Plane integration through `plane_user_id` and `plane_work_item_id`.

The data must not contain real personal data.

---

# 1. Synthetic team schema

## Team size

The target synthetic team contains 18 employees.

This is large enough for ranking and fairness analysis, but still small enough for manual inspection and demo scenarios.

## Team composition

```text
Backend Developer Junior — 2
Backend Developer Middle — 3
Backend Developer Senior — 2
Frontend Developer Junior — 2
Frontend Developer Middle — 2
Frontend Developer Senior — 1
QA Engineer — 2
Data/ML Engineer — 2
DevOps Engineer — 1
Team Lead — 1
```

## Employee fields

```text
employee_id
plane_user_id
name
role
grade
experience_years
primary_stack
skills
current_workload
active_tasks_count
avg_completion_speed
avg_quality_score
deadline_reliability
learning_goals
mentor_level
availability
timezone
```

## Field meanings

### employee_id

Internal stable COMPASS AI employee identifier.

Example:

```text
EMP-001
```

### plane_user_id

Optional Plane user ID.

Initially can be empty because the first synthetic employees may not exist as real Plane users yet.

Later this field will be mapped in:

```text
data/processed/employee_plane_mapping.csv
```

### name

Synthetic Russian-language display name.

No real personal data.

### role

Employee role.

Allowed values:

```text
backend_developer
frontend_developer
qa_engineer
data_ml_engineer
devops_engineer
team_lead
```

### grade

Employee seniority level.

Allowed values:

```text
junior
middle
senior
lead
```

### experience_years

Realistic years of experience.

Suggested ranges:

```text
junior: 0.5–2.0
middle: 2.0–5.0
senior: 5.0–9.0
lead: 7.0–12.0
```

### primary_stack

Main technology stack.

Examples:

```text
backend_python
frontend_react
qa_automation
data_ml
devops_platform
team_management
```

### skills

Dictionary of skill levels from 0 to 5.

Example:

```json
{
  "Python": 4,
  "FastAPI": 4,
  "PostgreSQL": 3,
  "Docker": 3
}
```

### current_workload

Current workload from 0 to 1.

Interpretation:

```text
0.00–0.40 -> low workload
0.40–0.70 -> normal workload
0.70–0.85 -> high workload
0.85–0.95 -> risky workload
0.95–1.00 -> critical overload
```

### active_tasks_count

Number of active Plane/synthetic tasks currently assigned.

### avg_completion_speed

Historical speed score from 0 to 1.

Higher is better.

### avg_quality_score

Historical quality score from 0 to 1.

Higher is better.

### deadline_reliability

Deadline reliability from 0 to 1.

Higher means the employee usually completes tasks on time.

### learning_goals

List of skills or areas the employee wants to improve.

Example:

```text
FastAPI
System Design
Machine Learning
```

### mentor_level

Mentoring capability from 0 to 5.

Interpretation:

```text
0 -> cannot mentor
1 -> can answer simple questions
2 -> can review simple tasks
3 -> can mentor junior employees
4 -> can mentor middle employees
5 -> team-level technical mentor
```

### availability

Availability flag.

Allowed values:

```text
available
partially_available
unavailable
```

### timezone

Timezone string.

For local demo:

```text
Europe/Berlin
```

## Design decisions

- The team intentionally contains more backend employees because the first Plane test project is `Backend Platform`.
- The team still includes frontend, QA, data/ML and DevOps roles to support future multi-project generation.
- `plane_user_id` is nullable because synthetic employees do not have to be real Plane users at the schema design stage.
- Workload and quality fields are numeric from the beginning because they will be used by rule-based scoring and neural network features.
- Learning goals are included from the beginning because one recommendation mode is `growth`.

---

# 2. Skills taxonomy

## Skill level scale

All skills use integer levels from 0 to 5.

```text
0 -> no skill
1 -> basic awareness
2 -> can solve simple tasks
3 -> confident working level
4 -> strong level
5 -> expert level
```

## Technical skills

```text
Python
FastAPI
Django
PostgreSQL
Redis
Docker
Kubernetes
React
TypeScript
Next.js
HTML/CSS
Testing
CI/CD
Data Analysis
Machine Learning
PyTorch
API Design
System Design
Monitoring
Security
```

## Soft and management skills

```text
communication
ownership
mentoring
documentation
code_review
planning
risk_management
```

## Domain skills

```text
backend_architecture
frontend_architecture
qa_strategy
data_pipelines
ml_experimentation
devops_operations
product_thinking
team_coordination
```

## Role-to-skill expectations

### backend_developer

Primary skills:

```text
Python
FastAPI
PostgreSQL
Redis
Docker
API Design
Testing
System Design
```

Secondary skills:

```text
CI/CD
Monitoring
Security
documentation
code_review
```

### frontend_developer

Primary skills:

```text
React
TypeScript
Next.js
HTML/CSS
Testing
API Design
```

Secondary skills:

```text
documentation
code_review
communication
frontend_architecture
```

### qa_engineer

Primary skills:

```text
Testing
API Design
documentation
risk_management
```

Secondary skills:

```text
Python
CI/CD
Monitoring
qa_strategy
```

### data_ml_engineer

Primary skills:

```text
Python
Data Analysis
Machine Learning
PyTorch
data_pipelines
ml_experimentation
```

Secondary skills:

```text
PostgreSQL
Docker
Testing
documentation
```

### devops_engineer

Primary skills:

```text
Docker
Kubernetes
CI/CD
Monitoring
Security
devops_operations
```

Secondary skills:

```text
Python
PostgreSQL
Redis
risk_management
```

### team_lead

Primary skills:

```text
planning
risk_management
mentoring
communication
ownership
team_coordination
System Design
code_review
```

Secondary skills:

```text
API Design
documentation
backend_architecture
product_thinking
```

## Design decisions

- Technical skills are capitalized because they represent technologies and concrete engineering capabilities.
- Soft and domain skills are lowercase snake_case because they are abstract competency dimensions.
- The same taxonomy will be used for employees and tasks.
- Missing skills should be treated as level 0.
- Skill vectors must keep a stable order in feature engineering.

---

# 3. Task schema

## Task types

```text
backend_feature
frontend_feature
bugfix
refactoring
database_migration
api_integration
ml_pipeline
analytics_report
devops_task
testing_task
security_task
documentation_task
```

## Task fields

```text
task_id
plane_work_item_id
plane_issue_id
plane_project_id
project_key
title
description
task_type
required_stack
required_skills
complexity
priority
business_criticality
deadline_days
estimated_hours
dependencies_count
is_growth_task
source
created_at
updated_at
```

## Field meanings

### task_id

Internal stable COMPASS AI task identifier.

Example:

```text
TASK-0001
```

### plane_work_item_id

Current Plane API work item ID.

This is the preferred field.

### plane_issue_id

Compatibility alias for older roadmap wording.

Can contain the same value as `plane_work_item_id`.

### plane_project_id

Plane project ID.

Example for current local Backend Platform:

```text
e608e7ad-f4fe-401d-b0f3-5570e82f08ee
```

### project_key

Logical project key.

Allowed values:

```text
BACK
FRONT
DATA
TOOLS
```

### title

Task title in Russian.

### description

Task description in Russian.

### task_type

One of the predefined task types.

### required_stack

List of technology stack tags.

Example:

```text
Python
FastAPI
PostgreSQL
Docker
```

### required_skills

Dictionary of required skills and minimum useful levels.

Example:

```json
{
  "Python": 3,
  "FastAPI": 3,
  "PostgreSQL": 2
}
```

### complexity

Integer task complexity from 1 to 5.

```text
1 -> very simple
2 -> simple
3 -> medium
4 -> complex
5 -> very complex
```

### priority

Task priority.

Allowed values aligned with Plane:

```text
none
low
medium
high
urgent
```

### business_criticality

Business criticality from 1 to 5.

This is separate from priority because a task can be technically urgent but not strategically critical.

### deadline_days

Number of days until target date.

### estimated_hours

Estimated implementation effort.

### dependencies_count

Number of blocking/related dependencies.

### is_growth_task

Boolean flag.

If true, the task is suitable for employee development and growth-mode recommendations.

### source

Task origin.

Allowed values:

```text
synthetic
plane
manual
```

## Plane mapping

Current Plane work item fields from stage 6:

```text
id
name
description_html
priority
start_date
target_date
sequence_id
completed_at
project
state
estimate_point
assignees
labels
created_at
updated_at
```

COMPASS AI mapping:

```text
Plane id -> plane_work_item_id
Plane name -> title
Plane description_html -> description
Plane priority -> priority
Plane target_date -> deadline_days
Plane project -> plane_project_id
Plane labels -> required_stack / task_type / urgency hints
Plane estimate_point -> estimated_hours or estimate feature later
Plane state -> current workflow state
```

## Task type default requirements

### backend_feature

Typical skills:

```text
Python
FastAPI
PostgreSQL
API Design
Testing
```

Average complexity:

```text
3
```

### frontend_feature

Typical skills:

```text
React
TypeScript
Next.js
HTML/CSS
Testing
```

Average complexity:

```text
3
```

### bugfix

Typical skills:

```text
Testing
Monitoring
API Design
```

Average complexity:

```text
2
```

### refactoring

Typical skills:

```text
System Design
Testing
code_review
documentation
```

Average complexity:

```text
3
```

### database_migration

Typical skills:

```text
PostgreSQL
System Design
Testing
risk_management
```

Average complexity:

```text
4
```

### api_integration

Typical skills:

```text
API Design
FastAPI
Testing
documentation
```

Average complexity:

```text
3
```

### ml_pipeline

Typical skills:

```text
Python
Machine Learning
PyTorch
Data Analysis
data_pipelines
```

Average complexity:

```text
4
```

### analytics_report

Typical skills:

```text
Data Analysis
PostgreSQL
Python
documentation
```

Average complexity:

```text
3
```

### devops_task

Typical skills:

```text
Docker
CI/CD
Monitoring
Security
```

Average complexity:

```text
4
```

### testing_task

Typical skills:

```text
Testing
documentation
API Design
```

Average complexity:

```text
2
```

### security_task

Typical skills:

```text
Security
System Design
risk_management
Testing
```

Average complexity:

```text
4
```

### documentation_task

Typical skills:

```text
documentation
communication
ownership
```

Average complexity:

```text
1
```

## Design decisions

- Task schema contains both `plane_work_item_id` and `plane_issue_id` for compatibility.
- The project should internally prefer `plane_work_item_id`.
- Labels from Plane are used as signals, not as the only source of truth.
- `required_skills` is a dictionary because the model needs levels, not only skill names.
- `deadline_days`, `estimated_hours`, `complexity` and `business_criticality` are numeric because they will be used in ML features.

---

# 4. Assignment history schema

## Goal

Assignment history is the supervised learning source for COMPASS AI.

Each row describes the historical result of assigning one task to one employee.

The neural network will learn from pairs:

```text
task_id + employee_id -> success_label
```

## Assignment fields

```text
assignment_id
task_id
employee_id
plane_work_item_id
plane_issue_id
assigned_at
completed_at
completed_on_time
estimated_hours
actual_hours
quality_score
reopened_count
manager_rating
employee_workload_at_assignment
skill_match_score
growth_match_score
speed_score
collaboration_score
risk_score
success_label
```

## Field meanings

### assignment_id

Internal stable assignment identifier.

Example:

```text
ASN-000001
```

### task_id

Internal COMPASS AI task ID.

### employee_id

Internal COMPASS AI employee ID.

### plane_work_item_id

Optional Plane work item ID.

Can be empty for purely synthetic historical data.

### plane_issue_id

Compatibility alias.

### assigned_at

Assignment timestamp.

### completed_at

Completion timestamp.

Can be empty if synthetic task failed or was not completed.

### completed_on_time

Boolean flag.

True if completed before target date.

### estimated_hours

Estimated effort.

### actual_hours

Actual effort.

### quality_score

Quality score from 0 to 1.

### reopened_count

How many times the work item was reopened or returned for rework.

### manager_rating

Manager rating from 1 to 5.

### employee_workload_at_assignment

Employee workload from 0 to 1 at assignment time.

### skill_match_score

Precomputed skill match score from 0 to 1.

### growth_match_score

Precomputed growth match score from 0 to 1.

### speed_score

Normalized speed score from 0 to 1.

### collaboration_score

Team/collaboration score from 0 to 1.

### risk_score

Risk score from 0 to 1.

Higher means more risky.

### success_label

Binary supervised learning label.

Allowed values:

```text
0
1
```

## Success label rules

Base positive rule:

```text
success_label = 1 if:
completed_on_time = true
quality_score >= 0.75
reopened_count <= 1
employee_workload_at_assignment <= 0.85
```

Base negative rule:

```text
success_label = 0 if:
completed_on_time = false
or quality_score < 0.60
or reopened_count >= 3
or employee_workload_at_assignment > 0.95
```

Ambiguous middle cases should be generated probabilistically.

## Recommended probability formula for synthetic data

The generator can calculate success probability using weighted factors:

```text
success_probability =
  0.35 * skill_match_score
+ 0.20 * deadline_reliability
+ 0.15 * avg_quality_score
+ 0.10 * avg_completion_speed
+ 0.10 * collaboration_score
+ 0.10 * growth_match_score
- 0.25 * overload_penalty
- 0.15 * complexity_gap_penalty
```

Then sample `success_label` from this probability.

## Overload penalty

```text
0.00 if workload <= 0.70
0.20 if 0.70 < workload <= 0.85
0.50 if 0.85 < workload <= 0.95
0.80 if workload > 0.95
```

## Complexity gap penalty

The penalty should increase when task complexity is too high for the employee grade.

Suggested comfortable complexity:

```text
junior: 1–2
middle: 2–4
senior: 3–5
lead: 4–5
```

## Design decisions

- `success_label` is binary for MVP neural network training.
- Detailed scores are still stored because future multi-output training may predict speed, quality, learning score and overload risk.
- Synthetic labels should not be perfectly deterministic, otherwise the ML task becomes too easy and unrealistic.
- Workload is included both as an employee field and as `employee_workload_at_assignment` because historical workload may differ from current workload.
- `plane_work_item_id` is optional because most historical assignments will be synthetic and not necessarily present in Plane.