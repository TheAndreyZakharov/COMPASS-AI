from __future__ import annotations

import shutil
from typing import Any, Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from sandbox_app.backend.core.paths import PATHS
from sandbox_app.backend.training.train_session import (
    SplitConfig,
    TrainingSessionConfig,
    TrainingSessionError,
    list_training_sessions,
    read_training_model_artifact,
    read_training_session,
    run_training_session,
)

router = APIRouter(prefix="/training", tags=["training"])


class SplitConfigPayload(BaseModel):
    train_size: float = Field(default=0.7, gt=0.0)
    validation_size: float = Field(default=0.15, ge=0.0)
    test_size: float = Field(default=0.15, ge=0.0)


class RunTrainingRequest(BaseModel):
    dataset_id: str = Field(min_length=3, max_length=81)
    dataset_kind: Literal["generated", "imported"] = "generated"
    target_mode: Literal["quality", "speed", "balanced", "learning", "risk_aware"] = (
        "balanced"
    )
    model_names: list[
        Literal[
            "baseline_rule_based",
            "sgd_classifier",
            "logistic_regression",
            "random_forest",
            "hist_gradient_boosting",
            "torch_mlp",
        ]
    ] = Field(default_factory=lambda: ["baseline_rule_based"])
    seed: int = 42
    split: SplitConfigPayload = Field(default_factory=SplitConfigPayload)
    model_params: dict[str, dict[str, Any]] = Field(default_factory=dict)
    auto_build_features: bool = True
    overwrite_features: bool = False
    max_pairs: int | None = Field(default=None, ge=1)


def delete_training_session_dir(session_id: str) -> dict[str, object]:
    root = PATHS.training_sessions_dir.resolve()
    target = (PATHS.training_sessions_dir / session_id).resolve()

    if not target.exists() or not target.is_dir():
        raise TrainingSessionError(f"Training session not found: {session_id}")

    if target == root or root not in target.parents:
        raise TrainingSessionError("Refusing to delete path outside training sessions root")

    shutil.rmtree(target)
    return {
        "deleted": True,
        "session_id": session_id,
        "path": str(target),
    }


@router.post("/run")
def run_training(payload: RunTrainingRequest) -> dict[str, object]:
    try:
        return run_training_session(
            TrainingSessionConfig(
                dataset_id=payload.dataset_id,
                dataset_kind=payload.dataset_kind,
                target_mode=payload.target_mode,
                model_names=list(payload.model_names),
                seed=payload.seed,
                split=SplitConfig(
                    train_size=payload.split.train_size,
                    validation_size=payload.split.validation_size,
                    test_size=payload.split.test_size,
                ),
                model_params=payload.model_params,
                auto_build_features=payload.auto_build_features,
                overwrite_features=payload.overwrite_features,
                max_pairs=payload.max_pairs,
            )
        )
    except TrainingSessionError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/sessions")
def get_training_sessions() -> dict[str, object]:
    return list_training_sessions()


@router.get("/sessions/{session_id}")
def get_training_session(session_id: str) -> dict[str, object]:
    try:
        return read_training_session(session_id)
    except TrainingSessionError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/sessions/{session_id}/artifacts")
def get_training_session_artifacts(session_id: str) -> dict[str, object]:
    try:
        details = read_training_session(session_id)
        return {
            "session_id": session_id,
            "artifacts": details["artifacts"],
            "summary": details["summary"],
        }
    except TrainingSessionError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/sessions/{session_id}/models/{model_name}")
def get_training_model_artifact(
    session_id: str,
    model_name: str,
) -> dict[str, object]:
    try:
        return read_training_model_artifact(session_id=session_id, model_name=model_name)
    except TrainingSessionError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.delete("/sessions/{session_id}")
def delete_training_session_endpoint(session_id: str) -> dict[str, object]:
    try:
        return delete_training_session_dir(session_id)
    except TrainingSessionError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
