from pathlib import Path
import pandas as pd


DATA_DIR = Path("data/mindcare")

DATASETS = {
    "complete": DATA_DIR / "mindcare_1200_synthetic.csv",
    "train": DATA_DIR / "train.csv",
    "validation": DATA_DIR / "validation.csv",
    "test": DATA_DIR / "test.csv",
}


REQUIRED_COLUMNS = {
    "message_id",
    "message",
    "category",
    "risk_level",
    "language",
    "source_type",
    "split",
    "label",
}


EXPECTED_CATEGORIES = {
    "crisis",
    "self_harm",
    "negated",
    "contextual",
    "neutral",
    "positive",
}


def check_file(name, path):
    print(f"\n{'=' * 60}")
    print(f"Checking: {name}")
    print(f"Path: {path}")
    print(f"{'=' * 60}")

    if not path.exists():
        print("❌ FILE NOT FOUND")
        return False

    df = pd.read_csv(path)

    print(f"Rows: {len(df)}")
    print(f"Columns: {list(df.columns)}")

    missing_columns = REQUIRED_COLUMNS - set(df.columns)

    if missing_columns:
        print(f"❌ Missing columns: {missing_columns}")
        return False

    missing_values = df.isnull().sum()

    if missing_values.sum() > 0:
        print("\n⚠️ Missing values:")
        print(missing_values[missing_values > 0])
    else:
        print("✅ No missing values")

    categories = set(df["category"])

    unknown_categories = categories - EXPECTED_CATEGORIES

    if unknown_categories:
        print(f"❌ Unknown categories: {unknown_categories}")
        return False

    print("\nCategory distribution:")
    print(df["category"].value_counts())

    print("\nLanguage distribution:")
    print(df["language"].value_counts())

    print("\nRisk distribution:")
    print(df["risk_level"].value_counts())

    print("✅ Dataset structure looks valid")

    return True


def main():
    print("\nMindCare Dataset Validation")

    results = []

    for name, path in DATASETS.items():
        results.append(
            check_file(name, path)
        )

    print("\n" + "=" * 60)

    if all(results):
        print("✅ ALL DATASETS PASSED")
    else:
        print("❌ SOME DATASETS FAILED")


if __name__ == "__main__":
    main()