from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import torch

from src.models.matching_net import MatchingNetConfig, TaskEmployeeMatchingNet

PROJECT_ROOT = Path(__file__).resolve().parents[2]

MODEL_PATH = PROJECT_ROOT / "models" / "compass_matching_model.pt"
ONNX_PATH = PROJECT_ROOT / "models" / "task_employee_matcher.onnx"
EXPORT_METADATA_PATH = PROJECT_ROOT / "reports" / "onnx_export.json"


class ONNXMatchingWrapper(torch.nn.Module):
    def __init__(self, model: TaskEmployeeMatchingNet) -> None:
        super().__init__()
        self.model = model

    def forward(
        self,
        task_features: torch.Tensor,
        employee_features: torch.Tensor,
        pair_features: torch.Tensor,
    ) -> torch.Tensor:
        output = self.model(task_features, employee_features, pair_features)
        return output["success_probability"]


def load_checkpoint(path: Path = MODEL_PATH) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(
            f"Missing checkpoint: {path}. Run training first: python src/models/train.py"
        )

    return torch.load(path, map_location="cpu")


def model_config_from_checkpoint(checkpoint: dict[str, Any]) -> MatchingNetConfig:
    config_payload = checkpoint["model_config"]

    embedding_dim = int(config_payload.get("embedding_dim", 128))

    return MatchingNetConfig(
        task_input_dim=int(config_payload["task_input_dim"]),
        employee_input_dim=int(config_payload["employee_input_dim"]),
        pair_input_dim=int(config_payload["pair_input_dim"]),
        task_embedding_dim=int(config_payload.get("task_embedding_dim", embedding_dim)),
        employee_embedding_dim=int(config_payload.get("employee_embedding_dim", embedding_dim)),
        hidden_dim=int(config_payload["hidden_dim"]),
        dropout=float(config_payload["dropout"]),
    )


def build_model_from_checkpoint(checkpoint: dict[str, Any]) -> TaskEmployeeMatchingNet:
    config = model_config_from_checkpoint(checkpoint)
    model = TaskEmployeeMatchingNet(config)
    model.load_state_dict(checkpoint["model_state_dict"])
    model.eval()

    return model


def export_model_to_onnx(
    model: TaskEmployeeMatchingNet,
    config: MatchingNetConfig,
    output_path: Path = ONNX_PATH,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    wrapped_model = ONNXMatchingWrapper(model)
    wrapped_model.eval()

    dummy_task_features = torch.randn(1, config.task_input_dim, dtype=torch.float32)
    dummy_employee_features = torch.randn(1, config.employee_input_dim, dtype=torch.float32)
    dummy_pair_features = torch.randn(1, config.pair_input_dim, dtype=torch.float32)

    torch.onnx.export(
        wrapped_model,
        (dummy_task_features, dummy_employee_features, dummy_pair_features),
        output_path,
        export_params=True,
        opset_version=17,
        do_constant_folding=True,
        input_names=["task_features", "employee_features", "pair_features"],
        output_names=["success_probability"],
        dynamic_axes={
            "task_features": {0: "batch_size"},
            "employee_features": {0: "batch_size"},
            "pair_features": {0: "batch_size"},
            "success_probability": {0: "batch_size"},
        },
    )


def save_export_metadata(
    config: MatchingNetConfig,
    onnx_path: Path = ONNX_PATH,
    metadata_path: Path = EXPORT_METADATA_PATH,
) -> None:
    metadata_path.parent.mkdir(parents=True, exist_ok=True)

    metadata = {
        "onnx_path": str(onnx_path.relative_to(PROJECT_ROOT)),
        "opset_version": 17,
        "task_input_dim": config.task_input_dim,
        "employee_input_dim": config.employee_input_dim,
        "pair_input_dim": config.pair_input_dim,
        "task_embedding_dim": config.task_embedding_dim,
        "employee_embedding_dim": config.employee_embedding_dim,
        "hidden_dim": config.hidden_dim,
        "dropout": config.dropout,
        "output": "success_probability",
        "dynamic_batch": True,
    }

    with metadata_path.open("w", encoding="utf-8") as file:
        json.dump(metadata, file, ensure_ascii=False, indent=2)


def main() -> None:
    checkpoint = load_checkpoint()
    config = model_config_from_checkpoint(checkpoint)
    model = build_model_from_checkpoint(checkpoint)

    export_model_to_onnx(model=model, config=config)
    save_export_metadata(config=config)

    print(f"ONNX model saved: {ONNX_PATH}")
    print(f"ONNX export metadata saved: {EXPORT_METADATA_PATH}")


if __name__ == "__main__":
    main()