from pathlib import Path

import pandas as pd
from sklearn.metrics import (
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
)

from app.ml.text_classifier import MindCareTextClassifier


DATA_PATH = Path("data/mindcare_clean/validation.csv")

THRESHOLDS = [
    0.50,
    0.55,
    0.60,
    0.65,
    0.70,
    0.75,
    0.80,
    0.85,
    0.90,
    0.95,
]


def main():
    print("=" * 70)
    print("MINDCARE HIGH-RISK THRESHOLD ANALYSIS")
    print("=" * 70)

    df = pd.read_csv(DATA_PATH)

    messages = df["message"].tolist()

    true_high_risk = df["category"].isin(
        ["crisis", "self_harm"]
    ).astype(int).tolist()

    model = MindCareTextClassifier()
    model.load()

    probabilities = model.pipeline.predict_proba(messages)
    classes = list(model.pipeline.classes_)

    crisis_index = classes.index("crisis")
    self_harm_index = classes.index("self_harm")

    high_risk_probabilities = [
        max(
            probabilities[i][crisis_index],
            probabilities[i][self_harm_index],
        )
        for i in range(len(messages))
    ]

    results = []

    for threshold in THRESHOLDS:

        predicted_high_risk = [
            int(probability >= threshold)
            for probability in high_risk_probabilities
        ]

        precision = precision_score(
            true_high_risk,
            predicted_high_risk,
            zero_division=0,
        )

        recall = recall_score(
            true_high_risk,
            predicted_high_risk,
            zero_division=0,
        )

        f1 = f1_score(
            true_high_risk,
            predicted_high_risk,
            zero_division=0,
        )

        tn, fp, fn, tp = confusion_matrix(
            true_high_risk,
            predicted_high_risk,
            labels=[0, 1],
        ).ravel()

        results.append(
            {
                "threshold": threshold,
                "precision": precision,
                "recall": recall,
                "f1": f1,
                "TN": tn,
                "FP": fp,
                "FN": fn,
                "TP": tp,
            }
        )

    results_df = pd.DataFrame(results)

    print("\nValidation samples:", len(df))
    print("\nHigh-risk distribution:")
    print(df["category"].value_counts().sort_index())

    print("\nThreshold results:")
    print(
        results_df.to_string(
            index=False,
            float_format=lambda x: f"{x:.4f}",
        )
    )

    output_path = Path(
        "evaluation/threshold_analysis.csv"
    )

    results_df.to_csv(output_path, index=False)

    print(f"\nSaved: {output_path}")


if __name__ == "__main__":
    main()