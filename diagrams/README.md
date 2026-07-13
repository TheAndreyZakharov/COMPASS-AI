# COMPASS AI Diagrams

This file previews the Mermaid diagrams stored in this directory. GitHub renders these `mermaid` blocks directly in Markdown.

## English Diagrams

### COMPASS Overview

Source: [compass_overview.mmd](compass_overview.mmd)

```mermaid
flowchart TD
    User["Team lead or analyst"] --> Compass["COMPASS AI"]
    Compass --> Sandbox["Sandbox: synthetic data and controlled experiments"]
    Compass --> Plane["Plane integration: real task-management context"]
    Sandbox --> DataLab["Dataset generation, schema editing and Kanban Lab"]
    Sandbox --> Training["Local model training and comparison"]
    Plane --> LiveData["Plane projects, issues, members and workload"]
    DataLab --> Recommender["Assignment recommendation engine"]
    Training --> Recommender
    LiveData --> Recommender
    Recommender --> Explanations["Ollama / Qwen explanations"]
    Recommender --> Reports["Metrics, reports and fairness checks"]
    Explanations --> Decision["Human-reviewed task assignment decision"]
    Reports --> Decision
```

### Repository Architecture

Source: [repository_architecture.mmd](repository_architecture.mmd)

```mermaid
flowchart LR
    subgraph Repo["COMPASS-AI repository"]
        Docs["docs/\nconcept, roadmap, sandbox pipeline"]
        Assets["assets/forreadme/\nREADME screenshots and rendered diagrams"]
        Config["config/\nroot settings and synthetic schemas"]
        RootApp["app/\nFastAPI API and Streamlit dashboard"]
        Src["src/\ncore ML, recommendation and Plane integration"]
        PlaneStack["plane/ + scripts/\nlocal Plane, Ollama and stack orchestration"]
        Sandbox["sandbox_app/\nautonomous browser sandbox"]
        Tests["tests/ + sandbox_app/tests/\nroot and sandbox checks"]
        Artifacts["data/, models/, reports/, notebooks/\nroot datasets, models and analysis artifacts"]
        DiagramSrc["diagrams/\nMermaid architecture sources"]
    end

    RootApp --> Src
    RootApp --> PlaneStack
    Src --> Config
    Src --> Artifacts
    Src --> PlaneStack
    Sandbox --> SandboxBackend["sandbox_app/backend/\nFastAPI routers, generators, training, inference, reports"]
    Sandbox --> SandboxFrontend["sandbox_app/frontend/\nHTML, CSS and vanilla JavaScript UI"]
    Sandbox --> SandboxData["sandbox_app/data/\ngenerated, imported, test cases, Kanban Lab boards"]
    SandboxBackend --> SandboxData
    SandboxBackend --> SandboxSessions["sandbox_app/training_sessions/\nsaved training sessions"]
    SandboxBackend --> SandboxAssignments["sandbox_app/assignment_sessions/\nsaved assignment decisions"]
    PlaneStack --> PlaneLive["Plane Docker stack\nprojects, issues and members"]
    DiagramSrc --> Assets
    Docs --> RootApp
    Docs --> Sandbox
    Tests --> RootApp
    Tests --> Sandbox
```

### Sandbox Pipeline

Source: [sandbox_pipeline.mmd](sandbox_pipeline.mmd)

```mermaid
flowchart TD
    Browser["Browser UI\nRussian / English, light / dark themes"] --> SandboxAPI["Sandbox FastAPI backend"]
    SandboxAPI --> Settings["config/app_settings.json\nfeature schemas and model presets"]
    Browser --> Generator["Data Generation tab\nsample profiles or custom schema"]
    Generator --> Generated["data/generated/\nemployees, tasks, history, training pairs"]
    Generated --> Viewer["Data Viewer tab\nsummary, tables, graphs and Kanban view"]
    Generated --> Training["Training tab\nbaseline, sklearn and PyTorch models"]
    Training --> Sessions["training_sessions/\nmetrics, plots, model artifacts and ONNX exports"]
    Sessions --> Models["Models tab\nvalidation and ONNX export checks"]
    Generated --> TestCases["Assignment test cases\nteam, active tasks and history"]
    TestCases --> AssignmentLab["Task Assignment tab\nsingle-task and bulk recommendation"]
    Sessions --> AssignmentLab
    AssignmentLab --> Ollama["Ollama + Qwen2.5 1.5B\nhuman-readable explanations"]
    AssignmentLab --> AssignmentSessions["assignment_sessions/\nsaved recommendations"]
    Generated --> KanbanCopy["Kanban Lab copy\nisolated editable board"]
    KanbanCopy --> KanbanLab["Kanban Lab tab\nedit tasks, edit staff, drag columns and run recommendations"]
    KanbanLab --> SavedBoards["data/kanban_lab/\nsaved experimental boards"]
    KanbanLab --> Ollama
    AssignmentSessions --> Reports["Reports tab\ndataset, model and assignment reports"]
    Sessions --> Reports
```

### Plane Integration Pipeline

Source: [plane_integration.mmd](plane_integration.mmd)

```mermaid
flowchart TD
    Developer["Developer in VS Code"] --> Tasks["VS Code task\nCOMPASS: start stack"]
    Tasks --> Docker["Docker Desktop / local Plane stack"]
    Tasks --> Ollama["Ollama service\nQwen2.5 1.5B"]
    Tasks --> API["app/api.py\nFastAPI COMPASS API"]
    Tasks --> Dashboard["app/dashboard.py\nStreamlit dashboard"]
    Docker --> Plane["Plane web application\nprojects, issues and members"]
    Plane --> PlaneAPI["Plane REST API"]
    PlaneAPI --> Integration["src/integration/\nPlane client, mapping and comment formatting"]
    Integration --> Features["src/features/\nskill vectors and task-employee features"]
    Features --> Models["src/models/ and models/\nmatching model and ONNX artifact"]
    Models --> Ranking["src/recommendation/\nranking, workload, growth and fairness scoring"]
    Ranking --> Agents["src/agents/\nteam analysis and explanation orchestration"]
    Agents --> Ollama
    Agents --> API
    API --> Dashboard
    Dashboard --> User["Manager reviews candidates, explanations and metrics"]
    API --> PlaneComment["Optional formatted recommendation comment"]
    PlaneComment --> Plane
    Tasks --> Stop["VS Code task\nCOMPASS: stop stack"]
    Stop --> Docker
    Stop --> Ollama
    Stop --> API
    Stop --> Dashboard
```

## Russian Diagrams

### COMPASS Overview RU

Source: [compass_overview_RU.mmd](compass_overview_RU.mmd)

```mermaid
flowchart TD
    User["Руководитель команды или аналитик"] --> Compass["COMPASS AI"]
    Compass --> Sandbox["Sandbox: synthetic data и контролируемые эксперименты"]
    Compass --> Plane["Интеграция с Plane: реальный контекст управления задачами"]
    Sandbox --> DataLab["Генерация датасетов, настройка схем и Kanban Lab"]
    Sandbox --> Training["Локальное обучение и сравнение моделей"]
    Plane --> LiveData["Проекты, задачи, участники и загрузка из Plane"]
    DataLab --> Recommender["Движок рекомендаций по назначению задач"]
    Training --> Recommender
    LiveData --> Recommender
    Recommender --> Explanations["Объяснения через Ollama / Qwen"]
    Recommender --> Reports["Метрики, отчеты и проверки fairness"]
    Explanations --> Decision["Решение о назначении задачи с проверкой человеком"]
    Reports --> Decision
```

### Repository Architecture RU

Source: [repository_architecture_RU.mmd](repository_architecture_RU.mmd)

```mermaid
flowchart LR
    subgraph Repo["Репозиторий COMPASS-AI"]
        Docs["docs/\nконцепция, roadmap, sandbox pipeline"]
        Assets["assets/forreadme/\nскриншоты README и отрендеренные диаграммы"]
        Config["config/\nroot settings и synthetic schemas"]
        RootApp["app/\nFastAPI API и Streamlit dashboard"]
        Src["src/\ncore ML, рекомендации и интеграция с Plane"]
        PlaneStack["plane/ + scripts/\nлокальный Plane, Ollama и управление стеком"]
        Sandbox["sandbox_app/\nавтономный browser sandbox"]
        Tests["tests/ + sandbox_app/tests/\nпроверки root-проекта и sandbox"]
        Artifacts["data/, models/, reports/, notebooks/\nroot datasets, models и analysis artifacts"]
        DiagramSrc["diagrams/\nMermaid-исходники архитектуры"]
    end

    RootApp --> Src
    RootApp --> PlaneStack
    Src --> Config
    Src --> Artifacts
    Src --> PlaneStack
    Sandbox --> SandboxBackend["sandbox_app/backend/\nFastAPI routers, generators, training, inference, reports"]
    Sandbox --> SandboxFrontend["sandbox_app/frontend/\nHTML, CSS и vanilla JavaScript UI"]
    Sandbox --> SandboxData["sandbox_app/data/\ngenerated, imported, test cases, Kanban Lab boards"]
    SandboxBackend --> SandboxData
    SandboxBackend --> SandboxSessions["sandbox_app/training_sessions/\nсохраненные training sessions"]
    SandboxBackend --> SandboxAssignments["sandbox_app/assignment_sessions/\nсохраненные решения по назначениям"]
    PlaneStack --> PlaneLive["Plane Docker stack\nprojects, issues и members"]
    DiagramSrc --> Assets
    Docs --> RootApp
    Docs --> Sandbox
    Tests --> RootApp
    Tests --> Sandbox
```

### Sandbox Pipeline RU

Source: [sandbox_pipeline_RU.mmd](sandbox_pipeline_RU.mmd)

```mermaid
flowchart TD
    Browser["Browser UI\nрусский / английский, светлая / темная темы"] --> SandboxAPI["Sandbox FastAPI backend"]
    SandboxAPI --> Settings["config/app_settings.json\nfeature schemas и model presets"]
    Browser --> Generator["Вкладка генерации данных\nsample profiles или custom schema"]
    Generator --> Generated["data/generated/\nemployees, tasks, history, training pairs"]
    Generated --> Viewer["Вкладка просмотра данных\nsummary, tables, graphs и Kanban view"]
    Generated --> Training["Вкладка обучения\nbaseline, sklearn и PyTorch models"]
    Training --> Sessions["training_sessions/\nmetrics, plots, model artifacts и ONNX exports"]
    Sessions --> Models["Вкладка моделей\nvalidation и ONNX export checks"]
    Generated --> TestCases["Проверочные наборы назначений\nteam, active tasks и history"]
    TestCases --> AssignmentLab["Вкладка назначения задач\nsingle-task и bulk recommendation"]
    Sessions --> AssignmentLab
    AssignmentLab --> Ollama["Ollama + Qwen2.5 1.5B\nчеловеческие объяснения"]
    AssignmentLab --> AssignmentSessions["assignment_sessions/\nсохраненные рекомендации"]
    Generated --> KanbanCopy["Копия Kanban Lab\nизолированная редактируемая доска"]
    KanbanCopy --> KanbanLab["Вкладка Kanban Lab\nредактирование задач и персонала, drag columns, рекомендации"]
    KanbanLab --> SavedBoards["data/kanban_lab/\nсохраненные experimental boards"]
    KanbanLab --> Ollama
    AssignmentSessions --> Reports["Вкладка отчетов\ndataset, model и assignment reports"]
    Sessions --> Reports
```

### Plane Integration Pipeline RU

Source: [plane_integration_RU.mmd](plane_integration_RU.mmd)

```mermaid
flowchart TD
    Developer["Разработчик в VS Code"] --> Tasks["VS Code task\nCOMPASS: start stack"]
    Tasks --> Docker["Docker Desktop / локальный Plane stack"]
    Tasks --> Ollama["Ollama service\nQwen2.5 1.5B"]
    Tasks --> API["app/api.py\nFastAPI COMPASS API"]
    Tasks --> Dashboard["app/dashboard.py\nStreamlit dashboard"]
    Docker --> Plane["Plane web application\nprojects, issues и members"]
    Plane --> PlaneAPI["Plane REST API"]
    PlaneAPI --> Integration["src/integration/\nPlane client, mapping и comment formatting"]
    Integration --> Features["src/features/\nskill vectors и task-employee features"]
    Features --> Models["src/models/ и models/\nmatching model и ONNX artifact"]
    Models --> Ranking["src/recommendation/\nranking, workload, growth и fairness scoring"]
    Ranking --> Agents["src/agents/\nteam analysis и explanation orchestration"]
    Agents --> Ollama
    Agents --> API
    API --> Dashboard
    Dashboard --> User["Менеджер проверяет кандидатов, объяснения и метрики"]
    API --> PlaneComment["Optional formatted recommendation comment"]
    PlaneComment --> Plane
    Tasks --> Stop["VS Code task\nCOMPASS: stop stack"]
    Stop --> Docker
    Stop --> Ollama
    Stop --> API
    Stop --> Dashboard
```
