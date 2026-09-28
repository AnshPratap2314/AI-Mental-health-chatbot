from pathlib import Path

import numpy as np
import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_validate
from sklearn.pipeline import Pipeline
from sklearn.metrics import make_scorer, f1_score, precision_score, recall_score


DATA_PATH = Path("data/mindcare_clean/mindcare_clean_1200.csv")


def main():
    print("=" * 70)
    print("MINDCARE CROSS-VALIDATION")
    print("=" * 70)

    df = pd.read_csv(DATA_PATH)

    X = df["message"].astype(str)
    y = df["category"].astype(str)

    pipeline = Pipeline([
        (
            "tfidf",
            TfidfVectorizer(
                lowercase=True,
                ngram_range=(1, 2),
                min_df=1,
                max_df=0.95,
                sublinear_tf=True,
            ),
        ),
        (
            "classifier",
            LogisticRegression(
                max_iter=2000,
                class_weight="balanced",
                random_state=42,
            ),
        ),
    ])

    cv = StratifiedKFold(
        n_splits=5,
        shuffle=True,
        random_state=42,
    )

    scoring = {
        "accuracy": "accuracy",
        "macro_precision": make_scorer(
            precision_score,
            average="macro",
            zero_division=0,
        ),
        "macro_recall": make_scorer(
            recall_score,
            average="macro",
            zero_division=0,
        ),
        "macro_f1": make_scorer(
            f1_score,
            average="macro",
            zero_division=0,
        ),
    }

    results = cross_validate(
        pipeline,
        X,
        y,
        cv=cv,
        scoring=scoring,
        return_train_score=False,
    )

    print("\n5-FOLD CROSS-VALIDATION")
    print("-" * 70)

    metrics = [
        "accuracy",
        "macro_precision",
        "macro_recall",
        "macro_f1",
    ]

    rows = []

    for metric in metrics:
        values = results[f"test_{metric}"]

        mean = np.mean(values)
        std = np.std(values)

        rows.append({
            "metric": metric,
            "mean": mean,
            "std": std,
        })

        print(
            f"{metric:20s}: "
            f"{mean:.4f} ± {std:.4f}"
        )

    output = pd.DataFrame(rows)

    output_path = Path("evaluation/cross_validation_results.csv")
    output.to_csv(output_path, index=False)

    print("\nFold-level results:")
    print("-" * 70)

    for metric in metrics:
        values = results[f"test_{metric}"]

        print(
            f"{metric:20s}: "
            + ", ".join(f"{v:.4f}" for v in values)
        )

    print(f"\nSaved: {output_path}")


if __name__ == "__main__":
    main()