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