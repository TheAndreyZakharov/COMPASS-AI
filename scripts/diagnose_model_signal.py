from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import roc_auc_score

PROJECT_ROOT = Path(__file__).resolve().parents[1]

TRAIN_PATH = PROJECT_ROOT / "data" / "processed" / "train.parquet"
VAL_PATH = PROJECT_ROOT / "data" / "processed" / "val.parquet"
FEATURE_METADATA_PATH = PROJECT_ROOT / "data" / "processed" / "feature_metadata.json"


def auc_for_feature(df: pd.DataFrame, feature: str, invert: bool = False) -> float:
    score = -df[feature] if invert else df[feature]
    return float(roc_auc_score(df["success_label"], score))


def main() -> None:
    train = pd.read_parquet(TRAIN_PATH)
    val = pd.read_parquet(VAL_PATH)

    with FEATURE_METADATA_PATH.open("r", encoding="utf-8") as file:
        metadata = json.load(file)

    feature_columns = (
        metadata["task_feature_columns"]
        + metadata["employee_feature_columns"]
        + metadata["pair_feature_columns"]
    )

    rule_based_score = (
        0.30 * val["pair_skill_match_score"]
        + 0.10 * val["pair_growth_match_score"]
        + 0.15 * val["pair_speed_score"]
        + 0.15 * val["employee_avg_quality_score"]
        + 0.15 * val["employee_deadline_reliability"]
        + 0.10 * val["pair_role_affinity"]
        + 0.05 * (1 - val["pair_workload_pressure"])
        - 0.10 * val["pair_risk_score"]
    )

    hgb = HistGradientBoostingClassifier(
        max_iter=150,
        learning_rate=0.05,
        max_leaf_nodes=31,
        random_state=42,
    )
    hgb.fit(train[feature_columns], train["success_label"])
    hgb_predictions = hgb.predict_proba(val[feature_columns])[:, 1]

    feature_auc = {
        "pair_skill_match_score": auc_for_feature(val, "pair_skill_match_score"),
        "pair_growth_match_score": auc_for_feature(val, "pair_growth_match_score"),
        "pair_speed_score": auc_for_feature(val, "pair_speed_score"),
        "pair_collaboration_score": auc_for_feature(val, "pair_collaboration_score"),
        "pair_risk_score": auc_for_feature(val, "pair_risk_score", invert=True),
        "pair_role_affinity": auc_for_feature(val, "pair_role_affinity"),
        "pair_workload_pressure": auc_for_feature(val, "pair_workload_pressure", invert=True),
        "employee_avg_quality_score": auc_for_feature(val, "employee_avg_quality_score"),
        "employee_deadline_reliability": auc_for_feature(val, "employee_deadline_reliability"),
    }

    report = {
        "train_rows": len(train),
        "val_rows": len(val),
        "train_success_rate": round(float(train["success_label"].mean()), 6),
        "val_success_rate": round(float(val["success_label"].mean()), 6),
        "rule_based_val_roc_auc": round(
            float(roc_auc_score(val["success_label"], rule_based_score)),
            6,
        ),
        "hgb_val_roc_auc": round(float(roc_auc_score(val["success_label"], hgb_predictions)), 6),
        "single_feature_auc": {key: round(value, 6) for key, value in feature_auc.items()},
    }

    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()