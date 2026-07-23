"""
Baseline defence (Deliverable 3: "Baseline schema-validator implementation").

Represents the class of defences documented in the literature as the
current state of practice: check the tool's schema/description once, at
registration time, against a denylist of suspicious keywords. This is a
one-shot, registration-time check — it has no way to notice a description
that changes *after* registration (the rug-pull pattern), which is exactly
the limitation the proposal's "Limitations of Current Defences" section
argues for.

Usage:
    python -m baseline.schema_validator
"""

import pandas as pd
from pathlib import Path

SUSPICIOUS_KEYWORD_THRESHOLD = 1  # flag if >= 1 suspicious keyword hit


def flag_at_registration(row) -> int:
    """
    A registration-time-only check. It can only ever see
    `reg_suspicious_keyword_hits` — the description as it existed when the
    tool was first registered. It structurally has no access to
    `call_suspicious_keyword_hits` or `description_changed_after_registration`,
    because a real schema/OAuth-scope validator never re-reads the
    description after connection. This is what makes rug-pull attacks
    invisible to it by construction, not by omission.
    """
    return int(row["reg_suspicious_keyword_hits"] >= SUSPICIOUS_KEYWORD_THRESHOLD)


def run_baseline(corpus_path: str) -> pd.DataFrame:
    df = pd.read_csv(corpus_path)
    df["baseline_flagged"] = df.apply(flag_at_registration, axis=1)
    df["baseline_correct"] = (
        (df["label"] != "benign") == (df["baseline_flagged"] == 1)
    )
    return df


def main():
    corpus_path = Path(__file__).resolve().parents[1] / "data" / "corpus.csv"
    df = run_baseline(str(corpus_path))
    out_path = corpus_path.parent / "baseline_results.csv"
    df.to_csv(out_path, index=False)

    print("Baseline schema-validator results by class:")
    print(df.groupby("label")["baseline_flagged"].mean().rename("flag_rate"))
    print(f"\nOverall accuracy: {df['baseline_correct'].mean():.3f}")
    print(f"Saved full results to {out_path}")


if __name__ == "__main__":
    main()
