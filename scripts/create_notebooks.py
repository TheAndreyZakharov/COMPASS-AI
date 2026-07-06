from __future__ import annotations

import textwrap
from pathlib import Path

import nbformat as nbf

ROOT = Path(__file__).resolve().parents[1]
NOTEBOOKS_DIR = ROOT / "notebooks"

KERNEL_METADATA = {
    "kernelspec": {
        "display_name": "Python (COMPASS AI)",
        "language": "python",
        "name": "compass-ai",
    },
    "language_info": {
        "name": "python",
        "pygments_lexer": "ipython3",
    },
}


def cell_text(text: str) -> str:
    return textwrap.dedent(text).strip() + "\n"


def md(text: str) -> nbf.NotebookNode:
    return nbf.v4.new_markdown_cell(cell_text(text))


def code(text: str) -> nbf.NotebookNode:
    return nbf.v4.new_code_cell(cell_text(text))


def write_notebook(path: Path, cells: list[nbf.NotebookNode]) -> None:
    notebook = nbf.v4.new_notebook()
    notebook["cells"] = cells
    notebook["metadata"] = KERNEL_METADATA
    path.parent.mkdir(parents=True, exist_ok=True)
    nbf.write(notebook, path)
    print(f"created {path}")


def setup_cell(import_json: bool = False) -> nbf.NotebookNode:
    imports = [
        "from __future__ import annotations",
        "",
    ]

    if import_json:
        imports.append("import json")

    imports.extend(
        [
            "import sys",
            "from pathlib import Path",
            "",
            "import pandas as pd",
            "",
            'ROOT = Path.cwd()',
            'if not (ROOT / "data").exists():',
            "    ROOT = ROOT.parent",
            "",
            "sys.path.insert(0, str(ROOT))",
            "",
            'DATA_SYNTHETIC = ROOT / "data" / "synthetic"',
            'DATA_PROCESSED = ROOT / "data" / "processed"',
            'REPORTS = ROOT / "reports"',
            'FIGURES = REPORTS / "figures"',
            "FIGURES.mkdir(parents=True, exist_ok=True)",
            "",
            'pd.set_option("display.max_columns", 80)',
            'pd.set_option("display.width", 160)',
            "",
            'print("Project root:", ROOT)',
        ]
    )

    return code("\n".join(imports))


def synthetic_data_notebook() -> list[nbf.NotebookNode]:
    return [
        md(
            """
            # 01 - Synthetic Data Generation

            Цель: визуально проверить synthetic dataset COMPASS AI.
            """
        ),
        setup_cell(),
        code(
            """
            import yaml

            config_path = ROOT / "config" / "synthetic_data.yaml"
            schema_path = ROOT / "config" / "synthetic_schema.yaml"

            with open(config_path, encoding="utf-8") as file:
                synthetic_config = yaml.safe_load(file)

            with open(schema_path, encoding="utf-8") as file:
                synthetic_schema = yaml.safe_load(file)

            display(synthetic_config)
            display(synthetic_schema)
            """
        ),
        code(
            """
            employees = pd.read_csv(DATA_SYNTHETIC / "employees.csv")
            tasks = pd.read_csv(DATA_SYNTHETIC / "tasks.csv")
            assignments = pd.read_csv(DATA_SYNTHETIC / "assignments.csv")

            print("employees:", employees.shape)
            print("tasks:", tasks.shape)
            print("assignments:", assignments.shape)
            """
        ),
        code("display(employees.head(10))"),
        code("display(tasks.head(10))"),
        code("display(assignments.head(10))"),
        code(
            """
            import plotly.express as px

            role_counts = employees["role"].value_counts().reset_index()
            role_counts.columns = ["role", "count"]

            fig = px.bar(role_counts, x="role", y="count")
            fig.update_layout(title="Employees by role")
            fig.show()
            """
        ),
        code(
            """
            import plotly.express as px

            fig = px.histogram(
                tasks,
                x="complexity",
                color="project_key",
                barmode="group",
            )
            fig.update_layout(title="Task complexity by project")
            fig.show()
            """
        ),
        code(
            """
            import plotly.express as px

            success_counts = (
                assignments["success_label"]
                .value_counts()
                .sort_index()
                .reset_index()
            )
            success_counts.columns = ["success_label", "count"]

            fig = px.bar(success_counts, x="success_label", y="count")
            fig.update_layout(title="Success label distribution")
            fig.show()
            """
        ),
        code(
            """
            import plotly.express as px

            outcome_counts = assignments["outcome_status"].value_counts().reset_index()
            outcome_counts.columns = ["outcome_status", "count"]

            fig = px.bar(outcome_counts, x="outcome_status", y="count")
            fig.update_layout(title="Assignment outcomes")
            fig.show()
            """
        ),
    ]


def eda_notebook() -> list[nbf.NotebookNode]:
    return [
        md(
            """
            # 02 - Exploratory Data Analysis

            Цель: проверить пропуски, распределения, корреляции и связи признаков.
            """
        ),
        setup_cell(),
        code(
            """
            employees = pd.read_csv(DATA_SYNTHETIC / "employees.csv")
            tasks = pd.read_csv(DATA_SYNTHETIC / "tasks.csv")
            assignments = pd.read_csv(DATA_SYNTHETIC / "assignments.csv")

            merged = assignments.merge(
                tasks,
                on="task_id",
                suffixes=("_assignment", "_task"),
            )
            merged = merged.merge(
                employees,
                on="employee_id",
                suffixes=("", "_employee"),
            )

            print("merged:", merged.shape)
            """
        ),
        code(
            """
            missing_report = pd.DataFrame(
                {
                    "employees_missing": employees.isna().sum(),
                    "tasks_missing": tasks.isna().sum(),
                    "assignments_missing": assignments.isna().sum(),
                }
            ).fillna(0)

            display(
                missing_report
                .sort_values("assignments_missing", ascending=False)
                .head(30)
            )
            """
        ),
        code(
            """
            numeric_cols = [
                "skill_match_score",
                "growth_match_score",
                "risk_score",
                "quality_score",
                "employee_workload_at_assignment",
                "delay_days",
                "success_probability",
                "success_label",
            ]

            corr = assignments[numeric_cols].corr(numeric_only=True)
            display(corr)
            """
        ),
        code(
            """
            import plotly.express as px

            fig = px.imshow(corr, text_auto=True)
            fig.update_layout(title="Correlation matrix")
            fig.show()
            fig.write_html(FIGURES / "eda_correlation_matrix.html")
            """
        ),
        code(
            """
            import plotly.express as px

            success_by_skill = (
                assignments
                .groupby("success_label")["skill_match_score"]
                .mean()
                .reset_index()
            )

            fig = px.bar(
                success_by_skill,
                x="success_label",
                y="skill_match_score",
            )
            fig.update_layout(title="Average skill match by success label")
            fig.show()
            fig.write_html(FIGURES / "eda_skill_match_by_success.html")
            """
        ),
        code(
            """
            import plotly.express as px

            success_by_workload = (
                assignments
                .groupby("success_label")["employee_workload_at_assignment"]
                .mean()
                .reset_index()
            )

            fig = px.bar(
                success_by_workload,
                x="success_label",
                y="employee_workload_at_assignment",
            )
            fig.update_layout(title="Average workload by success label")
            fig.show()
            fig.write_html(FIGURES / "eda_workload_by_success.html")
            """
        ),
        code(
            """
            import plotly.express as px

            complexity_success = (
                merged
                .groupby("complexity")["success_label"]
                .mean()
                .reset_index()
            )

            fig = px.line(
                complexity_success,
                x="complexity",
                y="success_label",
                markers=True,
            )
            fig.update_layout(title="Success rate by task complexity")
            fig.show()
            fig.write_html(FIGURES / "eda_success_by_complexity.html")
            """
        ),
    ]


def training_notebook() -> list[nbf.NotebookNode]:
    return [
        md(
            """
            # 03 - Model Training

            Цель: показать конфиг обучения, split, архитектуру и историю обучения.
            """
        ),
        setup_cell(import_json=True),
        code(
            """
            split_meta_path = DATA_PROCESSED / "split_metadata.json"
            training_config_path = REPORTS / "training_config.json"
            history_path = REPORTS / "training_history.csv"
            checkpoint_path = ROOT / "models" / "compass_matching_model.pt"

            with open(split_meta_path, encoding="utf-8") as file:
                split_meta = json.load(file)

            with open(training_config_path, encoding="utf-8") as file:
                training_config = json.load(file)

            print("split metadata:")
            display(split_meta)

            print("training config:")
            display(training_config)

            print("checkpoint exists:", checkpoint_path.exists(), checkpoint_path)
            """
        ),
        code(
            """
            train_df = pd.read_parquet(DATA_PROCESSED / "train.parquet")
            val_df = pd.read_parquet(DATA_PROCESSED / "val.parquet")
            test_df = pd.read_parquet(DATA_PROCESSED / "test.parquet")

            split_summary = pd.DataFrame(
                [
                    {
                        "split": "train",
                        "rows": len(train_df),
                        "tasks": train_df["task_id"].nunique(),
                        "success_rate": train_df["success_label"].mean(),
                    },
                    {
                        "split": "val",
                        "rows": len(val_df),
                        "tasks": val_df["task_id"].nunique(),
                        "success_rate": val_df["success_label"].mean(),
                    },
                    {
                        "split": "test",
                        "rows": len(test_df),
                        "tasks": test_df["task_id"].nunique(),
                        "success_rate": test_df["success_label"].mean(),
                    },
                ]
            )

            display(split_summary)
            """
        ),
        code(
            """
            import inspect

            import torch

            from src.models.matching_net import MatchingNetConfig
            from src.models.matching_net import TaskEmployeeMatchingNet

            checkpoint = torch.load(
                checkpoint_path,
                map_location="cpu",
                weights_only=False,
            )

            config_source = checkpoint.get("model_config", {})
            if not config_source:
                config_source = training_config.get("model_config", {})
            if not config_source:
                config_source = training_config

            aliases = {
                "task_input_dim": training_config.get("task_dim"),
                "employee_input_dim": training_config.get("employee_dim"),
                "pair_input_dim": training_config.get("pair_dim"),
                "task_dim": training_config.get("task_dim"),
                "employee_dim": training_config.get("employee_dim"),
                "pair_dim": training_config.get("pair_dim"),
                "hidden_dim": training_config.get("hidden_dim", 256),
                "embedding_dim": training_config.get("embedding_dim", 128),
                "dropout": training_config.get("dropout", 0.1),
            }
            aliases.update(config_source)

            config_kwargs = {}
            for name in inspect.signature(MatchingNetConfig).parameters:
                if name in aliases and aliases[name] is not None:
                    config_kwargs[name] = aliases[name]

            print("MatchingNetConfig kwargs:")
            display(config_kwargs)

            model_config = MatchingNetConfig(**config_kwargs)
            model = TaskEmployeeMatchingNet(model_config)

            model
            """
        ),
        code(
            """
            history = pd.read_csv(history_path)
            display(history.head())
            """
        ),
        code(
            """
            import plotly.express as px

            fig = px.line(
                history,
                x="epoch",
                y=["train_loss", "val_loss"],
            )
            fig.update_layout(title="Training and validation loss")
            fig.show()
            fig.write_html(FIGURES / "training_loss.html")
            """
        ),
        code(
            """
            import plotly.express as px

            if "val_roc_auc" in history.columns:
                fig = px.line(history, x="epoch", y="val_roc_auc")
                fig.update_layout(title="Validation ROC-AUC")
                fig.show()
                fig.write_html(FIGURES / "training_val_roc_auc.html")
            """
        ),
    ]


def evaluation_notebook() -> list[nbf.NotebookNode]:
    return [
        md(
            """
            # 04 - Model Evaluation

            Цель: показать classification metrics, confusion matrix, ROC/PR curves.
            """
        ),
        setup_cell(import_json=True),
        code(
            """
            from sklearn.metrics import auc
            from sklearn.metrics import confusion_matrix
            from sklearn.metrics import precision_recall_curve
            from sklearn.metrics import roc_curve

            metrics_path = REPORTS / "model_metrics.json"
            ranking_path = REPORTS / "ranking_metrics.json"
            predictions_path = REPORTS / "test_predictions.csv"

            with open(metrics_path, encoding="utf-8") as file:
                model_metrics = json.load(file)

            with open(ranking_path, encoding="utf-8") as file:
                ranking_metrics = json.load(file)

            predictions = pd.read_csv(predictions_path)

            display(pd.DataFrame([model_metrics]))
            """
        ),
        code(
            """
            y_true = predictions["success_label"]
            y_pred = predictions["prediction"]
            y_score = predictions["success_probability"]

            cm = confusion_matrix(y_true, y_pred)
            cm_df = pd.DataFrame(
                cm,
                index=["actual_0", "actual_1"],
                columns=["pred_0", "pred_1"],
            )

            display(cm_df)
            """
        ),
        code(
            """
            import plotly.express as px

            fig = px.imshow(cm_df, text_auto=True)
            fig.update_layout(title="Confusion matrix")
            fig.show()
            fig.write_html(FIGURES / "evaluation_confusion_matrix.html")
            """
        ),
        code(
            """
            import plotly.express as px

            fpr, tpr, _ = roc_curve(y_true, y_score)
            roc_auc = auc(fpr, tpr)
            roc_df = pd.DataFrame({"fpr": fpr, "tpr": tpr})

            fig = px.line(roc_df, x="fpr", y="tpr")
            fig.update_layout(title=f"ROC curve AUC={roc_auc:.4f}")
            fig.show()
            fig.write_html(FIGURES / "evaluation_roc_curve.html")
            """
        ),
        code(
            """
            import plotly.express as px

            precision, recall, _ = precision_recall_curve(y_true, y_score)
            pr_df = pd.DataFrame({"precision": precision, "recall": recall})

            fig = px.line(pr_df, x="recall", y="precision")
            fig.update_layout(title="Precision-Recall curve")
            fig.show()
            fig.write_html(FIGURES / "evaluation_pr_curve.html")
            """
        ),
        code(
            """
            import plotly.express as px

            ranking_df = (
                pd.DataFrame(ranking_metrics)
                .T
                .reset_index()
                .rename(columns={"index": "model"})
            )
            display(ranking_df)

            fig = px.bar(
                ranking_df,
                x="model",
                y=["precision_at_1", "precision_at_3", "ndcg_at_3", "mrr"],
                barmode="group",
            )
            fig.update_layout(title="Ranking metrics comparison")
            fig.show()
            fig.write_html(FIGURES / "evaluation_ranking_metrics.html")
            """
        ),
    ]


def fairness_notebook() -> list[nbf.NotebookNode]:
    return [
        md(
            """
            # 05 - Fairness Analysis

            Цель: проверить senior/junior share, концентрацию и баланс ролей.
            """
        ),
        setup_cell(import_json=True),
        code(
            """
            employees = pd.read_csv(DATA_SYNTHETIC / "employees.csv")
            predictions = pd.read_csv(REPORTS / "test_predictions.csv")

            scored = predictions.merge(employees, on="employee_id", how="left")
            display(scored.head())
            """
        ),
        code(
            """
            top_by_task = (
                scored
                .sort_values(
                    ["task_id", "success_probability"],
                    ascending=[True, False],
                )
                .groupby("task_id")
                .head(1)
            )

            top_employee_share = top_by_task["employee_id"].value_counts(
                normalize=True
            )

            fairness_summary = {
                "recommended_tasks": int(top_by_task["task_id"].nunique()),
                "senior_recommendation_share": float(
                    (top_by_task["grade"] == "senior").mean()
                ),
                "junior_recommendation_share": float(
                    (top_by_task["grade"] == "junior").mean()
                ),
                "top_employee_concentration": float(
                    top_employee_share.head(1).iloc[0]
                ),
                "average_recommended_workload": float(
                    top_by_task["current_workload"].mean()
                ),
            }

            display(fairness_summary)
            """
        ),
        code(
            """
            import plotly.express as px

            grade_counts = top_by_task["grade"].value_counts().reset_index()
            grade_counts.columns = ["grade", "count"]

            fig = px.bar(grade_counts, x="grade", y="count")
            fig.update_layout(title="Top recommendations by grade")
            fig.show()
            fig.write_html(FIGURES / "fairness_recommendations_by_grade.html")
            """
        ),
        code(
            """
            import plotly.express as px

            role_counts = top_by_task["role"].value_counts().reset_index()
            role_counts.columns = ["role", "count"]

            fig = px.bar(role_counts, x="role", y="count")
            fig.update_layout(title="Top recommendations by role")
            fig.show()
            fig.write_html(FIGURES / "fairness_recommendations_by_role.html")
            """
        ),
        code(
            """
            import plotly.express as px

            employee_concentration = (
                top_by_task["name"]
                .value_counts()
                .head(10)
                .reset_index()
            )
            employee_concentration.columns = ["name", "top1_recommendations"]

            fig = px.bar(
                employee_concentration,
                x="name",
                y="top1_recommendations",
            )
            fig.update_layout(title="Top employee concentration")
            fig.show()
            fig.write_html(FIGURES / "fairness_top_employee_concentration.html")
            """
        ),
        code(
            """
            fairness_path = REPORTS / "fairness_summary.json"

            with open(fairness_path, "w", encoding="utf-8") as file:
                json.dump(fairness_summary, file, ensure_ascii=False, indent=2)

            print("saved", fairness_path)
            """
        ),
    ]


def plane_demo_notebook() -> list[nbf.NotebookNode]:
    return [
        md(
            """
            # 06 - Plane Integration Demo

            Цель: показать подключение к Plane и пример комментария COMPASS AI.
            """
        ),
        setup_cell(),
        code(
            """
            from dotenv import load_dotenv

            from src.integration.plane_client import PlaneClient

            load_dotenv(ROOT / ".env")

            try:
                client = PlaneClient.from_env()
                print("Plane API health:", client.api_healthcheck())

                projects = client.list_projects()
                projects_df = pd.DataFrame(projects)

                display(projects_df[["id", "name", "identifier"]].head())
            except Exception as exc:
                print("Plane is not available or .env is not configured:", exc)
                projects_df = pd.DataFrame()
            """
        ),
        code(
            """
            if not projects_df.empty:
                project_id = projects_df.iloc[0]["id"]
                work_items = client.list_work_items(project_id)
                work_items_df = pd.DataFrame(work_items)

                print("project_id:", project_id)
                display(work_items_df[["id", "name", "priority"]].head())
            else:
                project_id = None
                work_items_df = pd.DataFrame()
            """
        ),
        code(
            """
            from src.agents.orchestrator import recommend_synthetic_task

            recommendation = recommend_synthetic_task(
                "TASK-0001",
                mode="balanced_workload",
                top_k=3,
                use_llm=False,
            )

            display(pd.DataFrame(recommendation["top_candidates"]))
            """
        ),
        code(
            """
            from src.integration.plane_comment_formatter import (
                format_plane_recommendation_comment,
            )

            comment = format_plane_recommendation_comment(recommendation)
            print(comment)
            """
        ),
        code(
            """
            WRITE_BACK = False

            if WRITE_BACK and project_id and not work_items_df.empty:
                work_item_id = work_items_df.iloc[0]["id"]
                print("Would write comment to:", project_id, work_item_id)
            else:
                print("WRITE_BACK disabled. This notebook is safe by default.")
            """
        ),
    ]


def business_report_notebook() -> list[nbf.NotebookNode]:
    return [
        md(
            """
            # 07 - Business Report

            Цель: собрать понятный отчёт для тимлида.
            """
        ),
        setup_cell(import_json=True),
        md(
            """
            ## Problem

            Тимлиду сложно вручную выбирать исполнителя задачи: нужно учитывать
            навыки, загрузку, срочность, качество и развитие сотрудников.
            """
        ),
        md(
            """
            ## Solution

            COMPASS AI анализирует задачу и команду, ранжирует кандидатов через
            TaskEmployeeMatchingNet и объясняет рекомендацию на русском языке.
            """
        ),
        code(
            """
            employees = pd.read_csv(DATA_SYNTHETIC / "employees.csv")
            tasks = pd.read_csv(DATA_SYNTHETIC / "tasks.csv")
            assignments = pd.read_csv(DATA_SYNTHETIC / "assignments.csv")

            summary = {
                "employees": len(employees),
                "tasks": len(tasks),
                "assignments": len(assignments),
                "success_rate": float(assignments["success_label"].mean()),
                "average_workload": float(employees["current_workload"].mean()),
            }

            display(summary)
            """
        ),
        code(
            """
            with open(REPORTS / "model_metrics.json", encoding="utf-8") as file:
                model_metrics = json.load(file)

            with open(REPORTS / "ranking_metrics.json", encoding="utf-8") as file:
                ranking_metrics = json.load(file)

            display(pd.DataFrame([model_metrics]))
            display(pd.DataFrame(ranking_metrics).T)
            """
        ),
        code(
            """
            from src.agents.orchestrator import recommend_synthetic_task

            example = recommend_synthetic_task(
                "TASK-0001",
                mode="balanced_workload",
                top_k=3,
                use_llm=False,
            )

            print("Task:", example["title"])
            print("Mode:", example["mode"])
            print("Recommended:", example["top_candidates"][0]["name"])
            print("Explanation:")
            print(example["explanation"])
            """
        ),
        code(
            """
            import plotly.express as px

            workload_df = (
                employees[
                    [
                        "name",
                        "role",
                        "grade",
                        "current_workload",
                        "active_tasks_count",
                    ]
                ]
                .sort_values("current_workload", ascending=False)
                .head(15)
            )

            fig = px.bar(
                workload_df,
                x="name",
                y="current_workload",
                color="role",
            )
            fig.update_layout(title="Team workload")
            fig.show()
            fig.write_html(FIGURES / "business_team_workload.html")
            """
        ),
        code(
            """
            fairness_path = REPORTS / "fairness_summary.json"

            if fairness_path.exists():
                with open(fairness_path, encoding="utf-8") as file:
                    fairness_summary = json.load(file)

                display(fairness_summary)
            else:
                print("Run 05_fairness_analysis.ipynb first")
            """
        ),
        md(
            """
            ## Conclusion

            COMPASS AI показывает не только accuracy, но и управленческую зрелость:
            учитывает риски, загрузку, развитие и качество прошлых назначений.
            """
        ),
    ]


def notebook_specs() -> dict[str, list[nbf.NotebookNode]]:
    return {
        "01_synthetic_data_generation.ipynb": synthetic_data_notebook(),
        "02_data_analysis.ipynb": eda_notebook(),
        "03_model_training.ipynb": training_notebook(),
        "04_model_evaluation.ipynb": evaluation_notebook(),
        "05_fairness_analysis.ipynb": fairness_notebook(),
        "06_plane_integration_demo.ipynb": plane_demo_notebook(),
        "07_business_report.ipynb": business_report_notebook(),
    }


def main() -> None:
    for filename, cells in notebook_specs().items():
        write_notebook(NOTEBOOKS_DIR / filename, cells)


if __name__ == "__main__":
    main()