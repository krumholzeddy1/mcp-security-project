"""
Comparative evaluation (Deliverable 5: "Evaluation vs. baseline defence").

Re-runs the baseline validator on the SAME test-set rows the model was
evaluated on (loaded from data/model_test_results.csv, produced by
detection/train_model.py), so the comparison is apples-to-apples, then
reports precision/recall/F1 for both, split out per attack class so the
rug-pull-detection gap is visible rather than averaged away.

Usage:
    python -m evaluation.evaluate
"""

import pandas as pd
from pathlib import Path
from sklearn.metrics import precision_score, recall_score, f1_score, confusion_matrix

from baseline.schema_validator import flag_at_registration


def main():
    root = Path(__file__).resolve().parents[1]
    df = pd.read_csv(root / "data" / "model_test_results.csv")

    df["baseline_flagged"] = df.apply(flag_at_registration, axis=1)
    y_true = df["is_attack"]

    results = []
    for name, col in [("baseline_schema_validator", "baseline_flagged"),
                       ("ml_anomaly_detector", "model_flagged")]:
        y_pred = df[col]
        results.append({
            "method": name,
            "precision": round(precision_score(y_true, y_pred, zero_division=0), 3),
            "recall": round(recall_score(y_true, y_pred, zero_division=0), 3),
            "f1": round(f1_score(y_true, y_pred, zero_division=0), 3),
        })

    summary = pd.DataFrame(results)
    print("Overall comparison (attack vs benign):")
    print(summary.to_string(index=False))

    print("\nRecall by attack class (this is where the baseline's blind spot should show up):")
    for label in ("poisoned", "rugpull"):
        subset = df[df["label"] == label]
        base_recall = subset["baseline_flagged"].mean()
        model_recall = subset["model_flagged"].mean()
        print(f"  {label:10s}  baseline recall = {base_recall:.3f}   model recall = {model_recall:.3f}")

    out_path = root / "data" / "evaluation_summary.csv"
    summary.to_csv(out_path, index=False)
    print(f"\nSaved summary to {out_path}")


if __name__ == "__main__":
    main()
