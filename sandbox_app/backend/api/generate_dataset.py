from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException
from sandbox_app.backend.data_generation.dataset import (
    DatasetGenerationError,
    generate_full_dataset,
)
from sandbox_app.backend.data_generation.history import HistoryGenerationError
from sandbox_app.backend.data_generation.tasks import TaskGenerationError
from sandbox_app.backend.data_generation.training_pairs import TrainingPairsGenerationError
from sandbox_app.backend.features.schema import FeatureSchemaError
from sandbox_app.backend.utils.json_io import JsonFileError

router = APIRouter(prefix="/generate", tags=["generation"])


@router.post("/dataset")
def generate_dataset_endpoint(payload: dict[str, Any]) -> dict[str, Any]:
    try:
        result = generate_full_dataset(payload)
        return {
            "dataset_id": result["dataset_id"],
            "dataset_dir": result["dataset_dir"],
            "metadata": result["metadata"],
            "generation_report": result["generation_report"],
            "preview": result["preview"],
        }
    except (
        DatasetGenerationError,
        FeatureSchemaError,
        TaskGenerationError,
        HistoryGenerationError,
        TrainingPairsGenerationError,
    ) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except JsonFileError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc