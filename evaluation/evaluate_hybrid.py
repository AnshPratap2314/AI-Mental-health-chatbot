import pandas as pd

from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    precision_recall_fscore_support,
)

from app.ml.hybrid_engine import HybridRiskEngine


DATA_PATH = "data/mindcare_clean/test.csv"

LABELS = [
    "crisis",
    "self_harm",
    "negated",
    "contextual",
    "neutral",
    "positive",
]

HIGH_RISK_LABELS = {
    "crisis",
    "self_harm",
}


def main():

    df = pd.read_csv(DATA_PATH)

    engine = HybridRiskEngine()

    y_true = df["category"].tolist()

    predictions = []

    for message in df["message"]:

        result = engine.predict(message)

        predictions.append(
            result["category"]
        )

    # --------------------------------------------------
    # Multiclass
    # --------------------------------------------------

    print("\n" + "=" * 70)
    print("MINDCARE HYBRID TEST EVALUATION")
    print("=" * 70)

    print(
        f"\nTest samples: {len(df)}"
    )

    accuracy = accuracy_score(
        y_true,
        predictions,
    )

    print(
        f"\nAccuracy: {accuracy:.4f}"
    )

    print("\nClassification Report:")

    print(
        classification_report(
            y_true,
            predictions,
            labels=LABELS,
            zero_division=0,
        )
    )

    print("Confusion Matrix:")

    matrix = confusion_matrix(
        y_true,
        predictions,
        labels=LABELS,
    )

    print(
        pd.DataFrame(
            matrix,
            index=LABELS,
            columns=LABELS,
        )
    )

    # --------------------------------------------------
    # High-risk binary evaluation
    # --------------------------------------------------

    y_true_risk = [
        label in HIGH_RISK_LABELS
        for label in y_true
    ]

    y_pred_risk = [
        label in HIGH_RISK_LABELS
        for label in predictions
    ]

    precision, recall, f1, _ = (
        precision_recall_fscore_support(
            y_true_risk,
            y_pred_risk,
            average="binary",
            zero_division=0,
        )
    )

    print("\nHigh-Risk Metrics:")

    print(
        f"Precision: {precision:.4f}"
    )

    print(
        f"Recall:    {recall:.4f}"
    )

    print(
        f"F1:        {f1:.4f}"
    )

    tn, fp, fn, tp = confusion_matrix(
        y_true_risk,
        y_pred_risk,
    ).ravel()

    print("\nHigh-Risk Counts:")

    print(f"TN: {tn}")
    print(f"FP: {fp}")
    print(f"FN: {fn}")
    print(f"TP: {tp}")


if __name__ == "__main__":
    main()