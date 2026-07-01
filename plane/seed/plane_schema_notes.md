# Plane schema notes for COMPASS AI

## Goal

This file documents the actual Plane entities and API fields used by COMPASS AI integration.

The goal is to avoid guessing the Plane data model and to base the integration on real API responses from the local self-hosted Plane instance.

## Local Plane instance

Base URL:

    http://localhost

Workspace slug:

    compass-ai-lab

Main app:

    http://localhost/compass-ai-lab/

God Mode / Instance Admin:

    http://localhost/god-mode/general/

## API authentication

Plane REST API is available through the local Plane proxy.

Authentication uses the `x-api-key` header.

Example request:

    curl --request GET --url "$PLANE_BASE_URL/api/v1/workspaces/$PLANE_WORKSPACE_SLUG/projects/" --header "x-api-key: $PLANE_API_KEY"

Local secret values are stored only in `.env`.

The API token must never be committed.

Required local environment variables:

    PLANE_BASE_URL=http://localhost
    PLANE_API_KEY=<local_api_token>
    PLANE_WORKSPACE_SLUG=compass-ai-lab

`.env.example` must contain only placeholder values.

## Naming

Current Plane API uses the term:

    work items

Older project-management wording and parts of the roadmap may use:

    issues

COMPASS AI integration code should use the modern name:

    work_item
    work_items

Compatibility aliases may be kept in Python code:

    issue
    issues

This lets the code match the current Plane API while keeping the roadmap readable.

## Local workspace

Workspace slug:

    compass-ai-lab

Workspace ID observed from API responses:

    c81d4a58-ee30-4b3f-9221-cc1d95566440

## Local projects

Projects endpoint:

    GET /api/v1/workspaces/{workspace_slug}/projects/

Local request:

    GET /api/v1/workspaces/compass-ai-lab/projects/

Observed response shape:

    grouped_by
    sub_grouped_by
    total_count
    next_cursor
    prev_cursor
    next_page_results
    prev_page_results
    count
    total_pages
    total_results
    extra_stats
    results

The actual project list is stored inside:

    results

Observed projects:

    Backend Platform
    Frontend Platform
    Data Platform
    Internal Tools

Observed project IDs:

    Backend Platform: e608e7ad-f4fe-401d-b0f3-5570e82f08ee
    Frontend Platform: 33832fc6-ade4-4ac0-a937-9ba70b0859d8
    Data Platform: cdbeb78a-e8d3-4277-ad9b-13d6b8e44dab
    Internal Tools: 50d969c6-ae4c-4afe-a8aa-33cdb478f787

Observed project identifiers:

    Backend Platform: BACK
    Frontend Platform: FRONT
    Data Platform: DATA
    Internal Tools: TOOLS

Observed important project fields:

    id
    name
    identifier
    description
    description_text
    description_html
    total_members
    total_cycles
    total_modules
    is_member
    member_role
    cycle_view
    module_view
    issue_views_view
    page_view
    intake_view
    is_time_tracking_enabled
    is_issue_type_enabled
    timezone
    created_at
    updated_at
    created_by
    updated_by
    workspace
    default_assignee
    project_lead
    estimate
    default_state

Fields COMPASS AI will use first:

    id
    name
    identifier
    total_members
    total_cycles
    workspace

## Backend project

Backend Platform project ID:

    e608e7ad-f4fe-401d-b0f3-5570e82f08ee

Backend Platform identifier:

    BACK

Backend Platform currently has:

    total_members: 1
    total_cycles: 1
    total_modules: 0
    cycle_view: true
    is_time_tracking_enabled: false
    is_issue_type_enabled: false

## Work items

Work items endpoint:

    GET /api/v1/workspaces/{workspace_slug}/projects/{project_id}/work-items/

Local Backend Platform request:

    GET /api/v1/workspaces/compass-ai-lab/projects/e608e7ad-f4fe-401d-b0f3-5570e82f08ee/work-items/

Observed response shape:

    grouped_by
    sub_grouped_by
    total_count
    next_cursor
    prev_cursor
    next_page_results
    prev_page_results
    count
    total_pages
    total_results
    extra_stats
    results

The actual work item list is stored inside:

    results

Observed Backend Platform work items count:

    1

Observed test work item:

    id: 22ab005a-a3b1-49e1-947b-3d3251c63e47
    name: Реализовать JWT-авторизацию
    sequence_id: 1
    priority: high
    project: e608e7ad-f4fe-401d-b0f3-5570e82f08ee
    state: 633f3777-fce6-40bb-a6e7-096df86429a4
    assignees: []
    labels:
      - 19ad9f4d-9f1f-4518-9076-419b4fb2f3e5
      - 5b1f0192-7664-4679-b2c3-98e1fe8a4e8e
      - caa1adb5-1451-48dd-9d07-8e1c641c633e

Observed important work item fields:

    id
    type_id
    created_at
    updated_at
    deleted_at
    point
    name
    description_html
    description_binary
    priority
    start_date
    target_date
    sequence_id
    sort_order
    completed_at
    archived_at
    is_draft
    external_source
    external_id
    created_by
    updated_by
    project
    workspace
    parent
    state
    estimate_point
    type
    assignees
    labels

Fields COMPASS AI will use first:

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

COMPASS AI internal mapping:

    Plane work item id -> plane_issue_id or plane_work_item_id
    Plane work item name -> task title
    Plane description_html -> task description
    Plane priority -> task priority
    Plane state -> task state id
    Plane labels -> required stack / task type hints
    Plane assignees -> current assignees
    Plane target_date -> deadline signal
    Plane estimate_point -> estimate signal, if enabled later

## Test work item detail

Work item detail endpoint:

    GET /api/v1/workspaces/{workspace_slug}/projects/{project_id}/work-items/{work_item_id}/

Local test work item request:

    GET /api/v1/workspaces/compass-ai-lab/projects/e608e7ad-f4fe-401d-b0f3-5570e82f08ee/work-items/22ab005a-a3b1-49e1-947b-3d3251c63e47/

Observed test work item ID:

    22ab005a-a3b1-49e1-947b-3d3251c63e47

Observed test work item title:

    Реализовать JWT-авторизацию

Observed test work item description field:

    description_html

Observed test work item priority:

    high

Observed test work item state ID:

    633f3777-fce6-40bb-a6e7-096df86429a4

Observed test work item state by ID:

    Todo

Observed test work item labels by ID:

    19ad9f4d-9f1f-4518-9076-419b4fb2f3e5 -> backend
    5b1f0192-7664-4679-b2c3-98e1fe8a4e8e -> feature
    caa1adb5-1451-48dd-9d07-8e1c641c633e -> urgent

Observed test work item assignees:

    []

This is correct for COMPASS AI because the recommendation system should suggest candidates before assignment.

## States

States endpoint:

    GET /api/v1/workspaces/{workspace_slug}/projects/{project_id}/states/

Local Backend Platform request:

    GET /api/v1/workspaces/compass-ai-lab/projects/e608e7ad-f4fe-401d-b0f3-5570e82f08ee/states/

Observed Backend Platform states count:

    5

Observed states:

    Backlog
    Todo
    In Progress
    Done
    Cancelled

Observed state IDs:

    Backlog: 8325f1a6-aa63-46a9-8cbb-340848a506aa
    Todo: 633f3777-fce6-40bb-a6e7-096df86429a4
    In Progress: 74855d6f-1911-4e7d-a355-07521647c3f5
    Done: b68d69f3-e88a-4ea1-b8c6-626e083a2d41
    Cancelled: 34a698dc-d031-43f5-b875-a4af26fcc24d

Observed workflow mapping:

    Backlog -> backlog
    Todo -> unstarted
    In Progress -> started
    Done -> completed
    Cancelled -> cancelled

Observed important state fields:

    id
    created_at
    updated_at
    deleted_at
    name
    description
    color
    slug
    sequence
    group
    is_triage
    default
    external_source
    external_id
    created_by
    updated_by
    project
    workspace

Fields COMPASS AI will use first:

    id
    name
    group
    default
    project
    workspace

COMPASS AI state interpretation:

    backlog -> not ready or future work
    unstarted -> ready to be assigned or started
    started -> already active
    completed -> finished
    cancelled -> excluded from recommendation backlog

For the current test work item:

    state id: 633f3777-fce6-40bb-a6e7-096df86429a4
    state name: Todo
    state group: unstarted

## Labels

Project labels endpoint:

    GET /api/v1/workspaces/{workspace_slug}/projects/{project_id}/labels/

Local Backend Platform request:

    GET /api/v1/workspaces/compass-ai-lab/projects/e608e7ad-f4fe-401d-b0f3-5570e82f08ee/labels/

Observed Backend Platform labels count:

    10

Observed labels:

    growth-task
    urgent
    refactoring
    feature
    bug
    devops
    data
    ml
    frontend
    backend

Observed label IDs:

    growth-task: dff694be-63b4-40bc-ade8-96920df9673d
    urgent: caa1adb5-1451-48dd-9d07-8e1c641c633e
    refactoring: 97ee2eee-eaa8-4fd6-8742-dd9c46e54979
    feature: 5b1f0192-7664-4679-b2c3-98e1fe8a4e8e
    bug: ce9f294a-bef7-4441-97b3-49576aafc371
    devops: a12c8e8c-3bf5-49c7-a20a-43a344e07090
    data: bb5f64d5-870a-4b26-bbd4-980b983c7261
    ml: 754b3ad4-c8ce-4f8a-8c93-4013e6e6acd0
    frontend: 8d02ccac-3438-492c-b087-f54c12abb6fd
    backend: 19ad9f4d-9f1f-4518-9076-419b4fb2f3e5

Observed label colors:

    growth-task: #f78da7
    urgent: #ff6900
    refactoring: #fcb900
    feature: #8ed1fc
    bug: #eb144c
    devops: #abb8c3
    data: #7bdcb5
    ml: #00d084
    frontend: #9900ef
    backend: #0693e3

Observed important label fields:

    id
    created_at
    updated_at
    deleted_at
    name
    description
    color
    sort_order
    external_source
    external_id
    created_by
    updated_by
    workspace
    project
    parent

Fields COMPASS AI will use first:

    id
    name
    color
    project
    workspace

Current label setup decision:

    Labels were created in Backend Platform.
    Shared workspace-level labels were not found in the current Plane UI during manual setup.
    If needed, labels will be replicated to other projects later through a seed script.

COMPASS AI label interpretation:

    backend -> backend stack / backend task
    frontend -> frontend stack / frontend task
    ml -> ML/data science task signal
    data -> data/analytics task signal
    devops -> infrastructure/deployment task signal
    bug -> bugfix task type
    feature -> feature task type
    refactoring -> refactoring task type
    urgent -> urgency/business priority signal
    growth-task -> learning/development signal

## Comments

Work item comments endpoint:

    GET /api/v1/workspaces/{workspace_slug}/projects/{project_id}/work-items/{work_item_id}/comments/
    POST /api/v1/workspaces/{workspace_slug}/projects/{project_id}/work-items/{work_item_id}/comments/

Local test work item comments request:

    GET /api/v1/workspaces/compass-ai-lab/projects/e608e7ad-f4fe-401d-b0f3-5570e82f08ee/work-items/22ab005a-a3b1-49e1-947b-3d3251c63e47/comments/

Observed response:

    total_count: 0
    count: 0
    total_pages: 0
    total_results: 0
    results: []

Current test work item has no comments.

This is correct for the current stage.

Write-back will be implemented later in the roadmap.

COMPASS AI will use comments later for:

    create_work_item_comment(project_id, work_item_id, text)

Expected future comment marker:

    Generated by COMPASS AI

## Raw local samples

Raw API samples are stored locally in:

    data/raw/plane_api_samples/

Observed sample files:

    data/raw/plane_api_samples/projects.json
    data/raw/plane_api_samples/backend_work_items.json
    data/raw/plane_api_samples/backend_work_item_detail.json
    data/raw/plane_api_samples/backend_states.json
    data/raw/plane_api_samples/backend_labels.json
    data/raw/plane_api_samples/backend_work_item_comments.json

These files are not committed because they may contain local user IDs, emails, project IDs, workspace IDs and other instance-specific data.

## Local API checks performed

Projects:

    curl --silent --show-error --request GET --url "$PLANE_BASE_URL/api/v1/workspaces/$PLANE_WORKSPACE_SLUG/projects/" --header "x-api-key: $PLANE_API_KEY" > data/raw/plane_api_samples/projects.json

Backend work items:

    curl --silent --show-error --request GET --url "$PLANE_BASE_URL/api/v1/workspaces/$PLANE_WORKSPACE_SLUG/projects/$PLANE_BACKEND_PROJECT_ID/work-items/" --header "x-api-key: $PLANE_API_KEY" > data/raw/plane_api_samples/backend_work_items.json

Backend work item detail:

    curl --silent --show-error --request GET --url "$PLANE_BASE_URL/api/v1/workspaces/$PLANE_WORKSPACE_SLUG/projects/$PLANE_BACKEND_PROJECT_ID/work-items/$PLANE_TEST_WORK_ITEM_ID/" --header "x-api-key: $PLANE_API_KEY" > data/raw/plane_api_samples/backend_work_item_detail.json

Backend states:

    curl --silent --show-error --request GET --url "$PLANE_BASE_URL/api/v1/workspaces/$PLANE_WORKSPACE_SLUG/projects/$PLANE_BACKEND_PROJECT_ID/states/" --header "x-api-key: $PLANE_API_KEY" > data/raw/plane_api_samples/backend_states.json

Backend labels:

    curl --silent --show-error --request GET --url "$PLANE_BASE_URL/api/v1/workspaces/$PLANE_WORKSPACE_SLUG/projects/$PLANE_BACKEND_PROJECT_ID/labels/" --header "x-api-key: $PLANE_API_KEY" > data/raw/plane_api_samples/backend_labels.json

Backend work item comments:

    curl --silent --show-error --request GET --url "$PLANE_BASE_URL/api/v1/workspaces/$PLANE_WORKSPACE_SLUG/projects/$PLANE_BACKEND_PROJECT_ID/work-items/$PLANE_TEST_WORK_ITEM_ID/comments/" --header "x-api-key: $PLANE_API_KEY" > data/raw/plane_api_samples/backend_work_item_comments.json

## Implementation decisions for PlaneClient

PlaneClient should implement these methods first:

    list_projects()
    get_workspace()
    list_work_items(project_id)
    get_work_item(project_id, work_item_id)
    list_states(project_id)
    list_labels(project_id)
    list_work_item_comments(project_id, work_item_id)

Roadmap compatibility aliases should also exist:

    list_issues(project_id)
    get_issue(project_id, issue_id)
    create_issue_comment(project_id, issue_id, text)
    update_issue_assignee(project_id, issue_id, assignee_id)

PlaneClient must not contain ML logic.

PlaneClient must only handle Plane REST API communication.

## Open questions for the next stages

Project members endpoint:

    Need to verify exact current endpoint.

Comment creation body:

    Need to verify exact POST payload before writing real comments to Plane.

Assignee update body:

    Need to verify exact PATCH payload before implementing optional auto-assignment.

Workspace-level labels:

    Need to verify if API supports shared labels or if labels must be project-scoped.

Cycles endpoint:

    Need to verify exact endpoint later if COMPASS AI uses cycle data for workload/context.

Estimate points:

    Current Backend Platform has is_time_tracking_enabled=false and estimate=null.
    estimate_point is present on work items but currently null.
    Estimation can be added later if needed.

## Current stage conclusion

Plane API access works with `x-api-key`.

COMPASS AI can already read:

    projects
    Backend Platform work items
    work item detail
    states
    project labels
    comments list

This is enough to implement the first version of `PlaneClient` and `scripts/check_plane_connection.py`.