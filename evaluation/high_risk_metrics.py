import pandas as pd

from sklearn.metrics import (
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
)

from app.ml.rule_engine import RuleBasedRiskEngine


TEST_PATH = "data/mindcare/test.csv"

HIGH_RISK_LABELS = {
    "crisis",
    "self_harm",
}


def to_binary(label: str) -> int:
    """
    Convert multiclass labels into:

    1 = high risk
    0 = non-high risk
    """

    return 1 if label in HIGH_RISK_LABELS else 0


def main():

    df = pd.read_csv(TEST_PATH)

    engine = RuleBasedRiskEngine()

    predictions = [
        engine.predict(message)
        for message in df["message"]
    ]

    y_true = [
        to_binary(label)
        for label in df["category"]
    ]

    y_pred = [
        to_binary(label)
        for label in predictions
    ]

    precision = precision_score(
        y_true,
        y_pred,
        zero_division=0,
    )

    recall = recall_score(
        y_true,
        y_pred,
        zero_division=0,
    )

    f1 = f1_score(
        y_true,
        y_pred,
        zero_division=0,
    )

    matrix = confusion_matrix(
        y_true,
        y_pred,
        labels=[0, 1],
    )

    tn, fp, fn, tp = matrix.ravel()

    print("\n" + "=" * 60)
    print("MINDCARE HIGH-RISK BASELINE")
    print("=" * 60)

    print(f"\nPrecision:       {precision:.4f}")
    print(f"Recall:          {recall:.4f}")
    print(f"F1 Score:        {f1:.4f}")

    print("\nConfusion Matrix:")
    print(matrix)

    print("\nDetailed Counts:")
    print(f"True Negatives:  {tn}")
    print(f"False Positives: {fp}")
    print(f"False Negatives: {fn}")
    print(f"True Positives:  {tp}")

    print("\n" + "=" * 60)

    print(
        "\nHigh-risk recall is the key metric we will try "
        "to improve with the ML/hybrid system."
    )


if __name__ == "__main__":
    main()