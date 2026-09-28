import pandas as pd

from sklearn.metrics import (
    classification_report,
    confusion_matrix,
)

from app.ml.rule_engine import RuleBasedRiskEngine


TEST_PATH = "data/mindcare/test.csv"


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

    engine = RuleBasedRiskEngine()

    predictions = [
        engine.predict(message)
        for message in df["message"]
    ]

    actual = df["category"]

    print("\n===== RULE-BASED BASELINE =====\n")

    print(
        classification_report(
            actual,
            predictions,
            labels=LABELS,
            zero_division=0,
        )
    )

    print("\n===== CONFUSION MATRIX =====")

    matrix = confusion_matrix(
        actual,
        predictions,
        labels=LABELS,
    )

    matrix_df = pd.DataFrame(
        matrix,
        index=LABELS,
        columns=LABELS,
    )

    print(matrix_df)


if __name__ == "__main__":
    main()