# Sandbox Feature Schemas

Feature schemas define domain-specific roles, grades, skills, employee features,
task features, and outcome features.

The sandbox includes system examples:

- developers
- designers

The custom profile is intentionally empty and editable. It can describe any
domain: medicine, law, education, sales, operations, support, engineering, or
another team type.

Supported feature types:

- numeric
- categorical
- boolean
- text
- skill_list

Feature groups:

- employee_features
- task_features
- outcome_features

Examples:

- A medical team can use roles like Surgeon, Nurse, Therapist, Radiologist.
- A medical team can use grades like resident, specialist, senior_specialist.
- A medical team can use skills like triage, diagnostics, surgery, imaging.
- A medical task can use features like emergency_level and requires_surgery.

System profiles are useful defaults. Custom profiles are the flexible mechanism
for real experiments in any domain.