"""
Anomaly-detection model (Deliverable 4: "Anomaly-detection model design & training").

Trains a gradient-boosted tree classifier on tool-call metadata features,
including the description-change signal the baseline validator structurally
cannot see. This is deliberately a simple, well-understood model family
(per the proposal's fallback plan: keep the model simple rather than risk
a more complex architecture inside a 13-week timeline).

Usage:
    python -m detection.train_model
"""

import pandas as pd
import joblib
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.preprocessing import LabelEncoder

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


def load_data(corpus_path: str):
    df = pd.read_csv(corpus_path)
    df["is_attack"] = (df["label"] != "benign").astype(int)
    X = df[FEATURE_COLUMNS]
    y = df["is_attack"]
    return df, X, y


def main():
    root = Path(__file__).resolve().parents[1]
    corpus_path = root / "data" / "corpus.csv"
    df, X, y = load_data(str(corpus_path))

    X_train, X_test, y_train, y_test, idx_train, idx_test = train_test_split(
        X, y, df.index, test_size=0.3, random_state=42, stratify=y
    )

    model = GradientBoostingClassifier(random_state=42)
    model.fit(X_train, y_train)

    model_path = root / "data" / "detector_model.joblib"
    joblib.dump(model, model_path)

    # Save test-set predictions (with original labels) for the evaluation step
    test_df = df.loc[idx_test].copy()
    test_df["model_flagged"] = model.predict(X_test)
    test_df.to_csv(root / "data" / "model_test_results.csv", index=False)

    importances = pd.Series(model.feature_importances_, index=FEATURE_COLUMNS)
    print("Feature importances:")
    print(importances.sort_values(ascending=False))
    print(f"\nSaved trained model to {model_path}")
    print(f"Saved test-set predictions to data/model_test_results.csv")


if __name__ == "__main__":
    main()
