import pandas as pd

from pathlib import Path


DATA_DIR = Path("data/mindcare_clean")


def audit_file(path):

    df = pd.read_csv(path)

    print("\n" + "=" * 60)
    print(path)
    print("=" * 60)

    print(f"Rows: {len(df)}")

    duplicate_messages = (
        df["message"]
        .duplicated()
        .sum()
    )

    print(
        f"Exact duplicate messages: "
        f"{duplicate_messages}"
    )

    print("\nCategory counts:")
    print(
        df["category"]
        .value_counts()
    )

    print("\nLanguage counts:")
    print(
        df["language"]
        .value_counts()
    )

    print("\nSplit counts:")
    print(
        df["split"]
        .value_counts()
    )


def check_cross_split_leakage():

    train = pd.read_csv(
        DATA_DIR / "train.csv"
    )

    validation = pd.read_csv(
        DATA_DIR / "validation.csv"
    )

    test = pd.read_csv(
        DATA_DIR / "test.csv"
    )

    train_messages = set(
        train["message"]
    )

    validation_messages = set(
        validation["message"]
    )

    test_messages = set(
        test["message"]
    )

    train_validation = (
        train_messages
        & validation_messages
    )

    train_test = (
        train_messages
        & test_messages
    )

    validation_test = (
        validation_messages
        & test_messages
    )

    print("\n" + "=" * 60)
    print("CROSS-SPLIT LEAKAGE")
    print("=" * 60)

    print(
        f"Train ∩ Validation: "
        f"{len(train_validation)}"
    )

    print(
        f"Train ∩ Test: "
        f"{len(train_test)}"
    )

    print(
        f"Validation ∩ Test: "
        f"{len(validation_test)}"
    )


def main():

    for name in [
        "mindcare_clean_1200.csv",
        "train.csv",
        "validation.csv",
        "test.csv",
    ]:

        audit_file(
            DATA_DIR / name
        )

    check_cross_split_leakage()


if __name__ == "__main__":
    main()