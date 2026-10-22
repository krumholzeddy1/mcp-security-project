"""
Supplementary evaluation (Appendix J of the dissertation).

Adds three analyses that the primary pipeline (evaluation/evaluate.py) does not
perform, without altering any primary output:

  1. B2, a post-registration change-detection baseline that flags a session when
     description_changed_after_registration == 1, evaluated on the same 180-session
     held-out test split as B1 and the ML detectors, and on the full corpus.
  2. Wilson 95% confidence intervals for the headline binomial proportions.
  3. 5x10 repeated stratified cross-validation (50 folds, random_state=42) of B1, B2
     and the three ML classifiers, stratified on is_attack as in detection/train_model.py.

Usage (from the repository root, pinned environment active):
    python -m evaluation.supplementary_eval
"""

import warnings
from math import sqrt
from pathlib import Path

import numpy as np
import pandas as pd
import sklearn
from sklearn.model_selection import RepeatedStratifiedKFold

from detection.train_model import FEATURE_COLUMNS, build_models

warnings.filterwarnings("ignore")
ROOT = Path(__file__).resolve().parents[1]


def wilson(k, n, z=1.959964):
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return c - h, c + h


def metrics(pred, label):
    pred = np.asarray(pred).astype(bool)
    label = np.asarray(label)
    atk = label != "benign"
    tp, fp, fn, tn = (pred & atk).sum(), (pred & ~atk).sum(), (~pred & atk).sum(), (~pred & ~atk).sum()
    prec = tp / max(tp + fp, 1)
    rec = tp / (tp + fn)
    f1 = 2 * prec * rec / max(prec + rec, 1e-9)
    return dict(tp=int(tp), fp=int(fp), fn=int(fn), tn=int(tn), precision=prec, recall=rec, f1=f1,
                recall_poisoned=pred[label == "poisoned"].mean(),
                recall_rugpull=pred[label == "rugpull"].mean(),
                benign_fp_rate=pred[label == "benign"].mean())


def main():
    print(f"scikit-learn {sklearn.__version__}, pandas {pd.__version__}, numpy {np.__version__}")
    corpus = pd.read_csv(ROOT / "data" / "corpus.csv")
    test = pd.read_csv(ROOT / "data" / "model_test_results.csv")

    print("\n" + "=" * 70 + "\nTest split (n=180): B1, B2, B1 OR B2 and Gradient Boosting\n" + "=" * 70)
    rows = {
        "B1 schema validator": test.reg_suspicious_keyword_hits >= 1,
        "B2 change check": test.description_changed_after_registration == 1,
        "B1 OR B2": (test.reg_suspicious_keyword_hits >= 1) | (test.description_changed_after_registration == 1),
        "Gradient Boosting": test.pred_gradient_boosting == 1,
    }
    ms = {name: metrics(pr, test.label) for name, pr in rows.items()}
    print(f"{'method':20s}{'TP':>5s}{'FP':>5s}{'FN':>5s}{'TN':>5s}")
    for name, m in ms.items():
        print(f"{name:20s}{m['tp']:5d}{m['fp']:5d}{m['fn']:5d}{m['tn']:5d}")
    print()
    print(f"{'method':20s}{'P':>6s}{'R':>6s}{'F1':>6s}{'Rpois':>7s}{'Rrug':>6s}{'FPR':>6s}")
    for name, m in ms.items():
        print(f"{name:20s}{m['precision']:6.3f}{m['recall']:6.3f}{m['f1']:6.3f}"
              f"{m['recall_poisoned']:7.3f}{m['recall_rugpull']:6.3f}{m['benign_fp_rate']:6.3f}")

    print("\n" + "=" * 70 + "\nB2 on the full 600-session corpus\n" + "=" * 70)
    m = metrics(corpus.description_changed_after_registration == 1, corpus.label)
    print(f"flagged: rug-pull {int(round(m['recall_rugpull'] * 200))}/200, poisoned {int(round(m['recall_poisoned'] * 200))}/200, "
          f"benign {int(round(m['benign_fp_rate'] * 200))}/200")
    print(f"precision={m['precision']:.3f} recall={m['recall']:.3f} f1={m['f1']:.3f}")

    print("\n" + "=" * 70 + "\nWilson 95% confidence intervals\n" + "=" * 70)
    for label, k, n in [("GBT rug-pull recall (test)", 59, 67), ("RF rug-pull recall (test)", 60, 67),
                        ("LR rug-pull recall (test)", 59, 67), ("GBT rug recall (skewed)", 28, 30),
                        ("B2 rug-pull recall (corpus)", 180, 200), ("B2 benign FPR (corpus)", 42, 200),
                        ("B2 benign FPR (test)", 13, 60), ("GBT benign FPR (test)", 5, 60),
                        ("GBT benign FPR (skewed)", 27, 540)]:
        lo, hi = wilson(k, n)
        print(f"{label:28s}{k:>4d}/{n:<4d}= {k / n:.3f}  [{lo:.3f}, {hi:.3f}]")

    print("\n" + "=" * 70 + "\n5x10 repeated stratified CV (50 folds): mean (2.5th-97.5th pct)\n" + "=" * 70)
    df = corpus.copy()
    df["is_attack"] = (df.label != "benign").astype(int)
    X, y = df[FEATURE_COLUMNS], df.is_attack
    cv = RepeatedStratifiedKFold(n_splits=5, n_repeats=10, random_state=42)
    res = {k: [] for k in ["B1", "B2", "logistic_regression", "random_forest", "gradient_boosting"]}
    for tr, te in cv.split(X, y):
        lab = df.label.iloc[te].values
        res["B1"].append(metrics(X.iloc[te].reg_suspicious_keyword_hits >= 1, lab))
        res["B2"].append(metrics(X.iloc[te].description_changed_after_registration == 1, lab))
        for name, model in build_models().items():
            model.fit(X.iloc[tr], y.iloc[tr])
            res[name].append(metrics(model.predict(X.iloc[te]), lab))
    keys = ["f1", "recall_rugpull", "recall_poisoned", "benign_fp_rate"]
    titles = {"f1": "F1", "recall_rugpull": "Rug-pull recall",
              "recall_poisoned": "Poisoned recall", "benign_fp_rate": "Benign false-positive rate"}
    short = {"B1": "B1", "B2": "B2", "logistic_regression": "LR", "random_forest": "RF", "gradient_boosting": "GBT"}
    summary = {name: {} for name in res}
    for name, folds in res.items():
        for k in keys:
            v = np.array([f[k] for f in folds])
            lo, hi = np.percentile(v, [2.5, 97.5])
            summary[name][k] = (v.mean(), lo, hi)
    for k in keys:
        print(f"\n{titles[k]}")
        for name in res:
            mean, lo, hi = summary[name][k]
            print(f"  {short[name]:4s}{mean:.3f}  ({lo:.3f}-{hi:.3f})")
    out = [dict(method=n, **{f"{k}{suf}": round(summary[n][k][i], 3) for k in keys
                             for i, suf in enumerate(["", "_lo", "_hi"])}) for n in res]
    pd.DataFrame(out).to_csv(ROOT / "data" / "supplementary_cv_results.csv", index=False)
    print("\nSaved cross-validation summary to data/supplementary_cv_results.csv")


if __name__ == "__main__":
    main()
