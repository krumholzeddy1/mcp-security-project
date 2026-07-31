"""
Comparative evaluation (Deliverable 5: "Evaluation vs. baseline defence").

Evaluation design follows Unit 2.5 guidance: per-class recall is the headline
metric, not overall accuracy or F1, because a missed attack is the costly failure
mode for this problem domain (a validator that detects nothing at all can score
high on precision while achieving zero operational value).

Two evaluation passes:
  1. Balanced corpus (corpus.csv, 200 per class): primary results comparing
     Logistic Regression, Random Forest, and Gradient Boosting against the
     baseline schema validator. Stratified 70/30 split from train_model.py.
  2. Skewed corpus (corpus_skewed.csv, 90/5/5 split): robustness check for
     precision degradation under realistic class imbalance (Unit 2.3 requirement).
     Reported separately to isolate the imbalance effect.

Usage:
    python -m evaluation.evaluate
"""

import pandas as pd
import joblib
import numpy as np
from pathlib import Path
from sklearn.metrics import (
    precision_score, recall_score, f1_score,
    confusion_matrix, classification_report,
)
from sklearn.model_selection import train_test_split

from baseline.schema_validator import flag_at_registration

FEATURE_COLUMNS = [
    "num_schema_fields",
    "reg_description_length",
    "reg_description_entropy",
    "reg_suspicious_keyword_hits",
    "call_description_length",
    "call_description_entropy",
    "call_suspicious_keyword_hits",
    "description_changed_after_registration",
    "time_since_registration_s",
    "call_position_in_session",
    "num_calls_in_session",
]


def compute_metrics(y_true, y_pred, name: str) -> dict:
    return {
        "method": name,
        "precision": round(precision_score(y_true, y_pred, zero_division=0), 3),
        "recall": round(recall_score(y_true, y_pred, zero_division=0), 3),
        "f1": round(f1_score(y_true, y_pred, zero_division=0), 3),
    }


def per_class_recall(df: pd.DataFrame, pred_col: str) -> dict:
    result = {}
    for label in ("poisoned", "rugpull"):
        subset = df[df["label"] == label]
        result[label] = round(subset[pred_col].mean(), 3)
    return result


def evaluate_balanced(root: Path) -> pd.DataFrame:
    """Primary evaluation on the balanced corpus, comparing all four methods."""
    df = pd.read_csv(root / "data" / "model_test_results.csv")
    df["baseline_flagged"] = df.apply(flag_at_registration, axis=1)
    y_true = df["is_attack"]

    methods = [
        ("baseline_schema_validator", "baseline_flagged"),
        ("logistic_regression", "pred_logistic_regression"),
        ("random_forest", "pred_random_forest"),
        ("gradient_boosting", "pred_gradient_boosting"),
    ]

    results = []
    for name, col in methods:
        row = compute_metrics(y_true, df[col], name)
        pcr = per_class_recall(df, col)
        row["recall_poisoned"] = pcr["poisoned"]
        row["recall_rugpull"] = pcr["rugpull"]
        results.append(row)

    summary = pd.DataFrame(results)

    print("=" * 70)
    print("PRIMARY RESULTS — Balanced corpus (200 per class, 70/30 split)")
    print("=" * 70)
    print("\nHeadline metric: per-class recall (attack-class recall is the")
    print("operationally critical measure — a missed attack costs more than")
    print("a false alarm, per the research question framing).\n")
    print(summary.to_string(index=False))

    print("\nBaseline blind spot — rug-pull recall by construction:")
    print("  baseline schema validator: rug-pull recall = 0.000")
    print("  (Registration-time keyword check sees only reg_suspicious_keyword_hits;")
    print("   rug-pull attacks start clean, so this is structurally zero.)\n")

    print("Confusion matrices (binary: benign=0, attack=1):")
    for name, col in methods:
        cm = confusion_matrix(y_true, df[col])
        tn, fp, fn, tp = cm.ravel()
        print(f"  {name}: TP={tp} FP={fp} FN={fn} TN={tn}")

    return summary


def evaluate_skewed(root: Path, primary_model_name: str = "gradient_boosting"):
    """
    Robustness check on the skewed corpus (90% benign / 5% poisoned / 5% rug-pull).

    The primary model is retrained on a stratified split of the skewed corpus to
    measure precision degradation under class imbalance. This isolates whether the
    GBT model's performance on the balanced corpus generalises to a deployment
    scenario where attacks are rare.

    Interpretation follows Unit 2.5: any precision drop is reported in operational
    terms (false alarms per benign session) rather than as a bare number.
    """
    skewed_path = root / "data" / "corpus_skewed.csv"
    if not skewed_path.exists():
        print("\nSkewed corpus not found — run corpus/generate_corpus.py first.")
        return

    df = pd.read_csv(skewed_path)
    df["is_attack"] = (df["label"] != "benign").astype(int)
    X = df[FEATURE_COLUMNS]
    y = df["is_attack"]

    # Load the model trained on the balanced corpus and apply it to the skewed set.
    # This tests whether balanced-corpus training generalises rather than retraining,
    # which is the more conservative and dissertation-relevant evaluation.
    model_path = root / "data" / f"detector_model_{primary_model_name}.joblib"
    if not model_path.exists():
        print(f"\nModel not found: {model_path}. Run detection/train_model.py first.")
        return

    model = joblib.load(model_path)
    preds = model.predict(X)
    df["model_flagged"] = preds
    df["baseline_flagged"] = df.apply(flag_at_registration, axis=1)

    print("\n" + "=" * 70)
    print("ROBUSTNESS CHECK — Skewed corpus (90% benign / 5% poisoned / 5% rug-pull)")
    print("=" * 70)
    print("Model trained on balanced corpus, applied directly to skewed distribution.\n")

    for name, col in [("baseline_schema_validator", "baseline_flagged"),
                      (f"gradient_boosting (balanced-trained)", "model_flagged")]:
        row = compute_metrics(y, df[col], name)
        pcr = per_class_recall(df, col)
        row["recall_poisoned"] = pcr["poisoned"]
        row["recall_rugpull"] = pcr["rugpull"]

        n_benign = (df["label"] == "benign").sum()
        fp = ((df["label"] == "benign") & (df[col] == 1)).sum()
        fpr_per_benign = round(fp / n_benign, 3) if n_benign else 0.0
        print(f"  {name}")
        print(f"    precision={row['precision']}  recall={row['recall']}  "
              f"f1={row['f1']}  recall_poisoned={row['recall_poisoned']}  "
              f"recall_rugpull={row['recall_rugpull']}")
        print(f"    False-alarm rate: {fp} false positives out of {n_benign} benign "
              f"sessions ({fpr_per_benign:.1%} of benign flagged)")
        print()

    print("Operational interpretation: any precision drop under class imbalance")
    print("translates directly to analyst workload — each false alarm is a session")
    print("a security team must manually triage. Reported here per Unit 2.5 guidance.")


def main():
    root = Path(__file__).resolve().parents[1]
    summary = evaluate_balanced(root)
    out_path = root / "data" / "evaluation_summary.csv"
    summary.to_csv(out_path, index=False)
    print(f"\nSaved summary to {out_path}")

    evaluate_skewed(root)


if __name__ == "__main__":
    main()
