from __future__ import annotations

import time
from dataclasses import dataclass

from src.integration.plane_client import PlaneClient, PlaneClientError

LABELS: dict[str, str] = {
    "backend": "#2563eb",
    "frontend": "#7c3aed",
    "ml": "#db2777",
    "data": "#0891b2",
    "devops": "#ea580c",
    "bug": "#dc2626",
    "feature": "#16a34a",
    "refactoring": "#9333ea",
    "urgent": "#ef4444",
    "growth-task": "#22c55e",
    "python": "#3776ab",
    "fastapi": "#009688",
    "django": "#0c4b33",
    "postgresql": "#336791",
    "redis": "#d82c20",
    "docker": "#2496ed",
    "kubernetes": "#326ce5",
    "react": "#61dafb",
    "typescript": "#3178c6",
    "nextjs": "#111827",
    "html-css": "#e34f26",
    "pytorch": "#ee4c2c",
    "testing": "#64748b",
    "security": "#991b1b",
    "documentation": "#475569",
}


@dataclass(frozen=True)
class LabelResult:
    project_name: str
    project_identifier: str
    label_name: str
    action: str


def existing_label_names(labels: list[dict]) -> set[str]:
    return {str(label.get("name", "")).strip().lower() for label in labels}


def main() -> None:
    results: list[LabelResult] = []

    with PlaneClient() as client:
        projects = client.list_projects()

        if not projects:
            raise PlaneClientError("No Plane projects found.")

        for project in projects:
            project_id = str(project["id"])
            project_name = str(project.get("name", ""))
            project_identifier = str(project.get("identifier", ""))

            current_labels = client.list_labels(project_id)
            current_names = existing_label_names(current_labels)

            for label_name, color in LABELS.items():
                if label_name.lower() in current_names:
                    results.append(
                        LabelResult(
                            project_name=project_name,
                            project_identifier=project_identifier,
                            label_name=label_name,
                            action="exists",
                        )
                    )
                    continue

                client.create_label(
                    project_id=project_id,
                    name=label_name,
                    color=color,
                )

                time.sleep(0.5)

                results.append(
                    LabelResult(
                        project_name=project_name,
                        project_identifier=project_identifier,
                        label_name=label_name,
                        action="created",
                    )
                )

    print("Plane label seed completed.")
    print()

    for result in results:
        print(
            f"{result.project_identifier:<6} "
            f"{result.action:<8} "
            f"{result.label_name:<18} "
            f"{result.project_name}"
        )

    print()
    print(f"Total label actions: {len(results)}")


if __name__ == "__main__":
    main()