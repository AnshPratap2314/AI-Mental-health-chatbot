from pathlib import Path

import pandas as pd

from app.ml.rule_engine import RuleBasedRiskEngine


TEST_PATH = "data/mindcare/test.csv"

OUTPUT_DIR = Path("evaluation/results")
OUTPUT_FILE = OUTPUT_DIR / "rule_baseline_predictions.csv"


def main():

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    df = pd.read_csv(TEST_PATH)

    engine = RuleBasedRiskEngine()

    df["predicted_category"] = [
        engine.predict(message)
        for message in df["message"]
    ]

    df["correct"] = (
        df["category"]
        == df["predicted_category"]
    )

    df["error_type"] = "correct"

    df.loc[
        ~df["correct"]
        & df["category"].isin(
            ["crisis", "self_harm"]
        ),
        "error_type",
    ] = "high_risk_false_negative"

    df.loc[
        ~df["correct"]
        & ~df["category"].isin(
            ["crisis", "self_harm"]
        ),
        "error_type",
    ] = "classification_error"

    df.to_csv(
        OUTPUT_FILE,
        index=False,
    )

    print("\nSaved:")
    print(OUTPUT_FILE)

    print("\nPrediction summary:")
    print(
        df["predicted_category"]
        .value_counts()
    )

    print("\nErrors:")
    print(
        df[
            ~df["correct"]
        ][
            [
                "message_id",
                "message",
                "category",
                "predicted_category",
                "error_type",
            ]
        ].to_string(index=False)
    )


if __name__ == "__main__":
    main()