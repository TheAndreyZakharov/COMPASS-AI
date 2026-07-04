from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
TASKS_PATH = PROJECT_ROOT / "data" / "synthetic" / "tasks.csv"
EMBEDDINGS_PATH = PROJECT_ROOT / "data" / "processed" / "task_text_embeddings.npy"
EMBEDDINGS_META_PATH = PROJECT_ROOT / "data" / "processed" / "task_text_embeddings_meta.json"

MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
EMBEDDING_DIM = 384


def task_text(row: pd.Series) -> str:
    title = str(row.get("title", "") or "").strip()
    description = str(row.get("description", "") or "").strip()
    task_type = str(row.get("task_type", "") or "").strip()
    required_stack = str(row.get("required_stack", "") or "").strip()

    return "\n".join(
        part
        for part in [
            title,
            description,
            f"Task type: {task_type}" if task_type else "",
            f"Required stack: {required_stack}" if required_stack else "",
        ]
        if part
    )


def deterministic_fallback_embedding(text: str, dim: int = EMBEDDING_DIM) -> np.ndarray:
    seed = int(hashlib.sha256(text.encode("utf-8")).hexdigest()[:16], 16)
    rng = np.random.default_rng(seed)
    vector = rng.normal(loc=0.0, scale=1.0, size=dim).astype(np.float32)
    norm = np.linalg.norm(vector)

    if norm == 0:
        return vector

    return vector / norm


def build_embeddings_with_sentence_transformers(texts: list[str]) -> np.ndarray:
    from sentence_transformers import SentenceTransformer

    model = SentenceTransformer(MODEL_NAME)
    embeddings = model.encode(
        texts,
        batch_size=32,
        show_progress_bar=True,
        convert_to_numpy=True,
        normalize_embeddings=True,
    )

    return embeddings.astype(np.float32)


def build_fallback_embeddings(texts: list[str]) -> np.ndarray:
    return np.vstack([deterministic_fallback_embedding(text) for text in texts]).astype(np.float32)


def save_metadata(
    tasks: pd.DataFrame,
    embeddings: np.ndarray,
    source: str,
    path: Path = EMBEDDINGS_META_PATH,
) -> None:
    payload = {
        "model_name": MODEL_NAME,
        "source": source,
        "tasks_count": int(len(tasks)),
        "embedding_dim": int(embeddings.shape[1]),
        "embeddings_path": str(EMBEDDINGS_PATH.relative_to(PROJECT_ROOT)),
        "task_ids": tasks["task_id"].astype(str).tolist(),
    }

    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as file:
        json.dump(payload, file, ensure_ascii=False, indent=2)


def build_task_text_embeddings(
    tasks_path: Path = TASKS_PATH,
    embeddings_path: Path = EMBEDDINGS_PATH,
) -> np.ndarray:
    if not tasks_path.exists():
        raise FileNotFoundError(f"Missing tasks file: {tasks_path}")

    tasks = pd.read_csv(tasks_path)
    texts = [task_text(row) for _, row in tasks.iterrows()]

    try:
        embeddings = build_embeddings_with_sentence_transformers(texts)
        source = "sentence_transformers"
    except Exception as error:
        print(f"WARNING: sentence-transformers embedding failed: {error}")
        print("WARNING: using deterministic fallback embeddings")
        embeddings = build_fallback_embeddings(texts)
        source = "deterministic_fallback"

    if embeddings.shape != (len(tasks), EMBEDDING_DIM):
        raise ValueError(
            f"Unexpected embeddings shape: {embeddings.shape}, "
            f"expected ({len(tasks)}, {EMBEDDING_DIM})"
        )

    embeddings_path.parent.mkdir(parents=True, exist_ok=True)
    np.save(embeddings_path, embeddings)
    save_metadata(tasks, embeddings, source=source)

    return embeddings


def load_task_text_embeddings(path: Path = EMBEDDINGS_PATH) -> np.ndarray:
    if not path.exists():
        return build_task_text_embeddings()

    embeddings = np.load(path)

    if embeddings.ndim != 2 or embeddings.shape[1] != EMBEDDING_DIM:
        raise ValueError(f"Invalid embeddings shape: {embeddings.shape}")

    return embeddings.astype(np.float32)


def main() -> None:
    embeddings = build_task_text_embeddings()

    print(f"Embeddings saved: {EMBEDDINGS_PATH}")
    print(f"Metadata saved: {EMBEDDINGS_META_PATH}")
    print(f"Shape: {embeddings.shape}")


if __name__ == "__main__":
    main()