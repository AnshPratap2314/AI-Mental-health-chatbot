from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data" / "mindcare_responses"


def main():
    for split in ["train", "validation", "test"]:
        path = DATA_DIR / f"{split}.csv"
        df = pd.read_csv(path)

        print("\n" + "=" * 70)
        print(split.upper())
        print("=" * 70)

        print("Rows:", len(df))
        print("Unique messages:", df["message"].nunique())
        print("Unique responses:", df["response"].nunique())

        print("\nResponses per intent:")

        diversity = (
            df.groupby("intent")["response"]
            .nunique()
            .sort_values()
        )

        print(diversity.to_string())

        print(
            "\nMinimum responses/intent:",
            diversity.min(),
        )

        print(
            "Maximum responses/intent:",
            diversity.max(),
        )

        print(
            "Mean responses/intent:",
            round(diversity.mean(), 2),
        )


if __name__ == "__main__":
    main()