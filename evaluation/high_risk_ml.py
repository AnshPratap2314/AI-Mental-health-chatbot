import pandas as pd

from sklearn.metrics import (
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
)

from app.ml.text_classifier import MindCareTextClassifier


TEST_PATH = "data/mindcare/test.csv"

HIGH_RISK = {
    "crisis",
    "self_harm",
}


def to_binary(label):
    return 1 if label in HIGH_RISK else 0


def main():

    df = pd.read_csv(TEST_PATH)

    model = MindCareTextClassifier()
    model.load()

    predictions = model.predict_many(
        df["message"].tolist()
    )

    actual = df["category"].tolist()

    y_true = [
        to_binary(label)
        for label in actual
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
    print("MINDCARE ML HIGH-RISK TEST")
    print("=" * 60)

    print(f"\nPrecision: {precision:.4f}")
    print(f"Recall:    {recall:.4f}")
    print(f"F1:        {f1:.4f}")

    print("\nConfusion Matrix:")
    print(matrix)

    print("\nCounts:")
    print(f"TN: {tn}")
    print(f"FP: {fp}")
    print(f"FN: {fn}")
    print(f"TP: {tp}")


if __name__ == "__main__":
    main()