import pandas as pd

from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
)

from app.ml.text_classifier import MindCareTextClassifier


VALIDATION_PATH = "data/mindcare/validation.csv"


LABELS = [
    "crisis",
    "self_harm",
    "negated",
    "contextual",
    "neutral",
    "positive",
]


def main():

    df = pd.read_csv(
        VALIDATION_PATH
    )

    model = MindCareTextClassifier()

    model.load()

    predictions = model.predict_many(
        df["message"].tolist()
    )

    actual = df["category"].tolist()

    accuracy = accuracy_score(
        actual,
        predictions,
    )

    print("\n" + "=" * 60)
    print("MINDCARE ML VALIDATION")
    print("=" * 60)

    print(
        f"\nAccuracy: {accuracy:.4f}"
    )

    print("\nClassification Report:\n")

    print(
        classification_report(
            actual,
            predictions,
            labels=LABELS,
            zero_division=0,
        )
    )

    matrix = confusion_matrix(
        actual,
        predictions,
        labels=LABELS,
    )

    print("\nConfusion Matrix:")

    print(
        pd.DataFrame(
            matrix,
            index=LABELS,
            columns=LABELS,
        )
    )


if __name__ == "__main__":
    main()