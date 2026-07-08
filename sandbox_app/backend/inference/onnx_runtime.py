from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np


class OnnxRuntimeError(RuntimeError):
    """Raised when ONNX runtime inference fails."""


def onnxruntime_available() -> bool:
    try:
        import onnxruntime  # noqa: F401
    except ImportError:
        return False

    return True


def sigmoid(values: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-values))


def probability_from_mapping(value: dict[Any, Any]) -> float:
    if 1 in value:
        return float(value[1])

    if "1" in value:
        return float(value["1"])

    if True in value:
        return float(value[True])

    numeric_items: list[tuple[float, float]] = []

    for key, item in value.items():
        try:
            numeric_items.append((float(key), float(item)))
        except (TypeError, ValueError):
            continue

    if numeric_items:
        numeric_items.sort(key=lambda pair: pair[0])
        return float(numeric_items[-1][1])

    raise OnnxRuntimeError("Could not extract positive probability from ONNX mapping")


def output_to_array(output: Any) -> np.ndarray:
    if isinstance(output, dict):
        return np.asarray([probability_from_mapping(output)], dtype=float)

    if isinstance(output, list):
        if not output:
            raise OnnxRuntimeError("ONNX runtime returned empty list output")

        if all(isinstance(item, dict) for item in output):
            return np.asarray(
                [probability_from_mapping(item) for item in output],
                dtype=float,
            )

        return np.asarray(output, dtype=float).reshape(-1)

    array = np.asarray(output)

    if array.dtype == object:
        try:
            return np.asarray(array.tolist(), dtype=float).reshape(-1)
        except (TypeError, ValueError) as exc:
            raise OnnxRuntimeError("ONNX output contains non-numeric objects") from exc

    if array.ndim == 2 and array.shape[1] >= 2:
        return np.asarray(array[:, 1], dtype=float).reshape(-1)

    return np.asarray(array, dtype=float).reshape(-1)


def select_score_output(outputs: list[Any]) -> np.ndarray:
    if not outputs:
        raise OnnxRuntimeError("ONNX runtime returned no outputs")

    errors: list[str] = []

    for output in reversed(outputs):
        try:
            scores = output_to_array(output)
        except OnnxRuntimeError as exc:
            errors.append(str(exc))
            continue

        if scores.size > 0:
            return scores

    details = "; ".join(errors) if errors else "no parseable outputs"
    raise OnnxRuntimeError(f"Could not parse ONNX outputs: {details}")


def normalize_scores(
    scores: np.ndarray,
    *,
    output_is_logits: bool = False,
) -> np.ndarray:
    scores = np.asarray(scores, dtype=float).reshape(-1)

    if scores.size == 0:
        raise OnnxRuntimeError("ONNX runtime returned empty output")

    if np.isnan(scores).any() or np.isinf(scores).any():
        raise OnnxRuntimeError("ONNX runtime returned NaN or infinite values")

    if output_is_logits or scores.min() < 0.0 or scores.max() > 1.0:
        scores = sigmoid(scores)

    return np.clip(scores, 0.0, 1.0)


def run_onnx_predictions(
    onnx_path: Path,
    matrix: np.ndarray,
    *,
    output_is_logits: bool = False,
) -> np.ndarray:
    if not onnxruntime_available():
        raise OnnxRuntimeError("onnxruntime is not installed")

    try:
        import onnxruntime as ort
    except ImportError as exc:
        raise OnnxRuntimeError("onnxruntime is not installed") from exc

    if not onnx_path.exists():
        raise OnnxRuntimeError(f"ONNX artifact not found: {onnx_path}")

    try:
        session = ort.InferenceSession(str(onnx_path), providers=["CPUExecutionProvider"])
        input_name = session.get_inputs()[0].name
        outputs = session.run(None, {input_name: matrix.astype(np.float32)})
        scores = select_score_output(outputs)
    except OnnxRuntimeError:
        raise
    except Exception as exc:
        raise OnnxRuntimeError(f"ONNX inference failed: {onnx_path}") from exc

    return normalize_scores(scores, output_is_logits=output_is_logits)