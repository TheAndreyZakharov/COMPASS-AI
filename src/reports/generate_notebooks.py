from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
NOTEBOOKS_DIR = ROOT / "notebooks"
OUTPUT_DIR = ROOT / "reports" / "notebooks"

NOTEBOOKS = [
    "01_synthetic_data_generation.ipynb",
    "02_data_analysis.ipynb",
    "03_model_training.ipynb",
    "04_model_evaluation.ipynb",
    "05_fairness_analysis.ipynb",
    "06_plane_integration_demo.ipynb",
    "07_business_report.ipynb",
]


def run(command: list[str]) -> None:
    print(" ".join(command))
    subprocess.run(command, cwd=ROOT, check=True)


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for notebook_name in NOTEBOOKS:
        source = NOTEBOOKS_DIR / notebook_name
        executed = OUTPUT_DIR / notebook_name.replace(".ipynb", "_executed.ipynb")

        if not source.exists():
            raise FileNotFoundError(f"Notebook not found: {source}")

        run(
            [
                sys.executable,
                "-m",
                "papermill",
                str(source),
                str(executed),
                "-k",
                "compass-ai",
            ]
        )

        run(
            [
                sys.executable,
                "-m",
                "jupyter",
                "nbconvert",
                "--to",
                "html",
                str(executed),
                "--output-dir",
                str(OUTPUT_DIR),
            ]
        )

    print(f"Notebook reports saved to {OUTPUT_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())