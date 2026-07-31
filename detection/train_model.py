"""
Anomaly-detection model training (Deliverable 4).

Trains three candidate classifiers on tool-call metadata features:
  - Logistic Regression (linear baseline)
  - Random Forest (ensemble, non-parametric)
  - Gradient Boosting (selected primary model)

All three are trained on the same 70/30 stratified split from corpus.csv
so that the multi-model comparison in the evaluation step is apples-to-apples.
GBT is the primary model; LR and RF provide the comparison required to justify
the final model selection (Unit 2.3 requirement: do not pick a model without
showing the alternatives).

Usage:
    python -m detection.train_model
"""

import pandas as pd
import joblib
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

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


def build_models():
    return {
        "logistic_regression": Pipeline([
            ("scaler", StandardScaler()),
            ("clf", LogisticRegression(max_iter=1000, random_state=42)),
        ]),
        "random_forest": RandomForestClassifier(n_estimators=100, random_state=42),
        "gradient_boosting": GradientBoostingClassifier(random_state=42),
    }


def main():
    root = Path(__file__).resolve().parents[1]
    corpus_path = root / "data" / "corpus.csv"
    df, X, y = load_data(str(corpus_path))

    X_train, X_test, y_train, y_test, idx_train, idx_test = train_test_split(
        X, y, df.index, test_size=0.3, random_state=42, stratify=y
    )

    models = build_models()
    test_df = df.loc[idx_test].copy()

    for name, model in models.items():
        model.fit(X_train, y_train)
        model_path = root / "data" / f"detector_model_{name}.joblib"
        joblib.dump(model, model_path)
        test_df[f"pred_{name}"] = model.predict(X_test)
        print(f"Trained and saved: {name}")

    # Keep legacy column name for evaluate.py compatibility (GBT is primary)
    test_df["model_flagged"] = test_df["pred_gradient_boosting"]
    test_df.to_csv(root / "data" / "model_test_results.csv", index=False)

    # Alias primary model under the original filename for backwards compatibility
    joblib.dump(models["gradient_boosting"], root / "data" / "detector_model.joblib")

    gbt = models["gradient_boosting"]
    importances = pd.Series(gbt.feature_importances_, index=FEATURE_COLUMNS)
    print("\nGBT feature importances:")
    print(importances.sort_values(ascending=False))
    print(f"\nSaved test-set predictions to data/model_test_results.csv")


if __name__ == "__main__":
    main()
