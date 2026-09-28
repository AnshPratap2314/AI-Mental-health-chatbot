import pandas as pd

from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
)

from app.ml.text_classifier import MindCareTextClassifier


TEST_PATH = "data/mindcare_clean/test.csv"

LABELS = [
    "crisis",
    "self_harm",
    "negated",
    "contextual",
    "neutral",
    "positive",
]


def main():

    df = pd.read_csv(TEST_PATH)

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
    print("MINDCARE FINAL TEST EVALUATION")
    print("=" * 60)

    print(f"\nTest samples: {len(df)}")
    print(f"Accuracy: {accuracy:.4f}")

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

    print("\nConfusion Matrix:\n")

    print(
        pd.DataFrame(
            matrix,
            index=LABELS,
            columns=LABELS,
        )
    )


if __name__ == "__main__":
    main()