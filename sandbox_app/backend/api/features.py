from __future__ import annotations

from typing import Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from sandbox_app.backend.features.build_features import (
    FeatureBuildConfig,
    FeatureBuildError,
    build_features_for_dataset,
    read_feature_metadata,
)

router = APIRouter(prefix="/features", tags=["features"])


class BuildFeaturesRequest(BaseModel):
    dataset_id: str = Field(min_length=3, max_length=81)
    dataset_kind: Literal["generated", "imported"] = "generated"
    target_mode: Literal["quality", "speed", "balanced", "learning", "risk_aware"] = (
        "balanced"
    )
    overwrite: bool = False
    max_pairs: int | None = Field(default=None, ge=1)


@router.post("/build")
def build_features(payload: BuildFeaturesRequest) -> dict[str, object]:
    try:
        return build_features_for_dataset(
            FeatureBuildConfig(
                dataset_id=payload.dataset_id,
                dataset_kind=payload.dataset_kind,
                target_mode=payload.target_mode,
                overwrite=payload.overwrite,
                max_pairs=payload.max_pairs,
            )
        )
    except FeatureBuildError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/datasets/{dataset_id}/metadata")
def get_feature_metadata(
    dataset_id: str,
    dataset_kind: Literal["generated", "imported"] = "generated",
) -> dict[str, object]:
    try:
        return read_feature_metadata(dataset_id=dataset_id, dataset_kind=dataset_kind)
    except FeatureBuildError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc