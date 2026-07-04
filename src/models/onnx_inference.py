from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import onnxruntime as ort
import torch

from src.models.export_onnx import (
    MODEL_PATH,
    ONNX_PATH,
    build_model_from_checkpoint,
    load_checkpoint,
    model_config_from_checkpoint,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]

ONNX_VALIDATION_PATH = PROJECT_ROOT / "reports" / "onnx_validation.json"


def create_dummy_inputs(
    task_input_dim: int,
    employee_input_dim: int,
    pair_input_dim: int,
    batch_size: int = 8,
    seed: int = 42,
) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    generator = torch.Generator().manual_seed(seed)

    task_features = torch.randn(batch_size, task_input_dim, generator=generator)
    employee_features = torch.randn(batch_size, employee_input_dim, generator=generator)
    pair_features = torch.randn(batch_size, pair_input_dim, generator=generator)

    return task_features, employee_features, pair_features


@torch.no_grad()
def run_pytorch_inference(
    checkpoint: dict[str, Any],
    task_features: torch.Tensor,
    employee_features: torch.Tensor,
    pair_features: torch.Tensor,
) -> np.ndarray:
    model = build_model_from_checkpoint(checkpoint)
    model.eval()

    output = model(task_features, employee_features, pair_features)

    return output["success_probability"].detach().cpu().numpy()


def run_onnx_inference(
    onnx_path: Path,
    task_features: torch.Tensor,
    employee_features: torch.Tensor,
    pair_features: torch.Tensor,
) -> np.ndarray:
    if not onnx_path.exists():
        raise FileNotFoundError(
            f"Missing ONNX model: {onnx_path}. Run: python src/models/export_onnx.py"
        )

    session = ort.InferenceSession(
        str(onnx_path),
        providers=["CPUExecutionProvider"],
    )

    inputs = {
        "task_features": task_features.detach().cpu().numpy().astype(np.float32),
        "employee_features": employee_features.detach().cpu().numpy().astype(np.float32),
        "pair_features": pair_features.detach().cpu().numpy().astype(np.float32),
    }

    outputs = session.run(["success_probability"], inputs)

    return outputs[0]


def validate_outputs(
    pytorch_output: np.ndarray,
    onnx_output: np.ndarray,
) -> dict[str, float | bool]:
    absolute_diff = np.abs(pytorch_output - onnx_output)

    return {
        "max_abs_diff": float(np.max(absolute_diff)),
        "mean_abs_diff": float(np.mean(absolute_diff)),
        "pytorch_min": float(np.min(pytorch_output)),
        "pytorch_max": float(np.max(pytorch_output)),
        "onnx_min": float(np.min(onnx_output)),
        "onnx_max": float(np.max(onnx_output)),
        "is_close": bool(np.allclose(pytorch_output, onnx_output, atol=1e-5, rtol=1e-4)),
    }


def save_validation_report(report: dict[str, Any], path: Path = ONNX_VALIDATION_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as file:
        json.dump(report, file, ensure_ascii=False, indent=2)


def main() -> None:
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Missing checkpoint: {MODEL_PATH}. Run: python src/models/train.py"
        )

    checkpoint = load_checkpoint(MODEL_PATH)
    config = model_config_from_checkpoint(checkpoint)

    task_features, employee_features, pair_features = create_dummy_inputs(
        task_input_dim=config.task_input_dim,
        employee_input_dim=config.employee_input_dim,
        pair_input_dim=config.pair_input_dim,
    )

    pytorch_output = run_pytorch_inference(
        checkpoint=checkpoint,
        task_features=task_features,
        employee_features=employee_features,
        pair_features=pair_features,
    )

    onnx_output = run_onnx_inference(
        onnx_path=ONNX_PATH,
        task_features=task_features,
        employee_features=employee_features,
        pair_features=pair_features,
    )

    validation = validate_outputs(
        pytorch_output=pytorch_output,
        onnx_output=onnx_output,
    )

    report: dict[str, Any] = {
        "checkpoint_path": str(MODEL_PATH.relative_to(PROJECT_ROOT)),
        "onnx_path": str(ONNX_PATH.relative_to(PROJECT_ROOT)),
        "batch_size": int(task_features.shape[0]),
        "task_input_dim": config.task_input_dim,
        "employee_input_dim": config.employee_input_dim,
        "pair_input_dim": config.pair_input_dim,
        "validation": validation,
    }

    save_validation_report(report)

    print(f"ONNX validation saved: {ONNX_VALIDATION_PATH}")
    print(json.dumps(report, ensure_ascii=False, indent=2))

    if not validation["is_close"]:
        raise RuntimeError(
            "ONNX output differs from PyTorch output more than expected. "
            f"max_abs_diff={validation['max_abs_diff']}"
        )


if __name__ == "__main__":
    main()