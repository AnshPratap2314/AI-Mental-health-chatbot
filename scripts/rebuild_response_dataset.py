from pathlib import Path
import shutil
import pandas as pd


ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data" / "mindcare_responses"

SOURCE_FILES = [
    DATA_DIR / "train.csv",
    DATA_DIR / "validation.csv",
    DATA_DIR / "test.csv",
]

OUTPUT_FILES = {
    "train": DATA_DIR / "train.csv",
    "validation": DATA_DIR / "validation.csv",
    "test": DATA_DIR / "test.csv",
}


REQUIRED_COLUMNS = [
    "id",
    "message",
    "response",
    "intent",
    "mood",
    "topic",
    "risk_level",
    "language",
    "synthetic",
    "split",
]


def normalize_message(value):
    return (
        str(value)
        .strip()
        .lower()
        .replace("\u2019", "'")
        .replace("\u2018", "'")
    )


def main():
    print("=" * 75)
    print("MindCare Response Dataset Rebuild")
    print("=" * 75)

    frames = []

    for path in SOURCE_FILES:
        if not path.exists():
            raise FileNotFoundError(f"Missing source file: {path}")

        df = pd.read_csv(path)

        missing = set(REQUIRED_COLUMNS) - set(df.columns)
        if missing:
            raise ValueError(
                f"{path.name} is missing columns: {sorted(missing)}"
            )

        frames.append(df[REQUIRED_COLUMNS].copy())

    combined = pd.concat(frames, ignore_index=True)

    print("\nOriginal combined rows:", len(combined))

    # ---------------------------------------------------------
    # Normalize messages for duplicate detection
    # ---------------------------------------------------------

    combined["_message_key"] = combined["message"].map(normalize_message)

    # Remove empty messages
    before_empty = len(combined)
    combined = combined[combined["_message_key"].str.len() > 0].copy()

    print("Removed empty messages:", before_empty - len(combined))

    # ---------------------------------------------------------
    # Check whether the same message has conflicting labels
    # ---------------------------------------------------------

    conflicts = (
        combined.groupby("_message_key")
        .agg(
            intent_count=("intent", "nunique"),
            risk_count=("risk_level", "nunique"),
        )
    )

    conflicting_messages = conflicts[
        (conflicts["intent_count"] > 1)
        | (conflicts["risk_count"] > 1)
    ]

    print(
        "Messages with conflicting labels:",
        len(conflicting_messages),
    )

    if len(conflicting_messages):
        print(
            "\nERROR: Conflicting labels found. "
            "Do not automatically deduplicate these."
        )

        examples = conflicting_messages.head(20).index

        for message in examples:
            print("\nMESSAGE:", repr(message))

            rows = combined[
                combined["_message_key"] == message
            ]

            print(
                rows[
                    [
                        "intent",
                        "mood",
                        "topic",
                        "risk_level",
                    ]
                ].to_string(index=False)
            )

        raise SystemExit(
            "\nDataset rebuild stopped because conflicting labels "
            "must be reviewed first."
        )

    # ---------------------------------------------------------
    # Global deduplication
    # ---------------------------------------------------------

    before = len(combined)

    # Keep the first occurrence only.
    combined = combined.drop_duplicates(
        subset=["_message_key"],
        keep="first",
    ).copy()

    removed = before - len(combined)

    print("Duplicate messages removed:", removed)
    print("Unique messages remaining:", len(combined))

    # ---------------------------------------------------------
    # Deterministic ordering
    # ---------------------------------------------------------

    combined = combined.sort_values(
        by=["intent", "_message_key"],
        kind="mergesort",
    ).reset_index(drop=True)

    # ---------------------------------------------------------
    # Stratified split by intent
    #
    # Approximately:
    # 80% train
    # 10% validation
    # 10% test
    # ---------------------------------------------------------

    train_parts = []
    val_parts = []
    test_parts = []

    for intent, group in combined.groupby(
        "intent",
        sort=True,
    ):
        group = group.sample(
            frac=1.0,
            random_state=42,
        ).reset_index(drop=True)

        n = len(group)

        if n < 10:
            raise ValueError(
                f"Intent '{intent}' has only {n} unique messages. "
                "Not enough for a reliable stratified split."
            )

        n_test = max(1, round(n * 0.10))
        n_val = max(1, round(n * 0.10))

        test = group.iloc[:n_test]
        validation = group.iloc[n_test:n_test + n_val]
        train = group.iloc[n_test + n_val:]

        train_parts.append(train)
        val_parts.append(validation)
        test_parts.append(test)

    train = pd.concat(
        train_parts,
        ignore_index=True,
    )

    validation = pd.concat(
        val_parts,
        ignore_index=True,
    )

    test = pd.concat(
        test_parts,
        ignore_index=True,
    )

    # ---------------------------------------------------------
    # Shuffle final datasets
    # ---------------------------------------------------------

    train = train.sample(
        frac=1.0,
        random_state=42,
    ).reset_index(drop=True)

    validation = validation.sample(
        frac=1.0,
        random_state=42,
    ).reset_index(drop=True)

    test = test.sample(
        frac=1.0,
        random_state=42,
    ).reset_index(drop=True)

    # ---------------------------------------------------------
    # Update split field
    # ---------------------------------------------------------

    train["split"] = "train"
    validation["split"] = "validation"
    test["split"] = "test"

    # ---------------------------------------------------------
    # Remove internal helper
    # ---------------------------------------------------------

    for df in (train, validation, test):
        df.drop(
            columns=["_message_key"],
            errors="ignore",
            inplace=True,
        )

    # ---------------------------------------------------------
    # Backup existing datasets
    # ---------------------------------------------------------

    for path in OUTPUT_FILES.values():
        if path.exists():
            backup = path.with_suffix(
                path.suffix + ".pre_dedup_backup"
            )

            if not backup.exists():
                shutil.copy2(path, backup)

    # ---------------------------------------------------------
    # Write new datasets
    # ---------------------------------------------------------

    train.to_csv(
        OUTPUT_FILES["train"],
        index=False,
    )

    validation.to_csv(
        OUTPUT_FILES["validation"],
        index=False,
    )

    test.to_csv(
        OUTPUT_FILES["test"],
        index=False,
    )

    # ---------------------------------------------------------
    # Verification
    # ---------------------------------------------------------

    print("\n" + "=" * 75)
    print("NEW DATASET")
    print("=" * 75)

    print("\nTrain:", len(train))
    print("Validation:", len(validation))
    print("Test:", len(test))
    print("Total:", len(train) + len(validation) + len(test))

    print("\nIntent distribution:")
    print(train["intent"].value_counts().sort_index())

    # Cross-split leakage
    train_keys = set(
        train["message"].map(normalize_message)
    )

    val_keys = set(
        validation["message"].map(normalize_message)
    )

    test_keys = set(
        test["message"].map(normalize_message)
    )

    print("\n" + "=" * 75)
    print("LEAKAGE CHECK")
    print("=" * 75)

    print(
        "Train → Validation overlap:",
        len(train_keys & val_keys),
    )

    print(
        "Train → Test overlap:",
        len(train_keys & test_keys),
    )

    print(
        "Validation → Test overlap:",
        len(val_keys & test_keys),
    )

    # Duplicate check inside each split
    print("\n" + "=" * 75)
    print("DUPLICATE CHECK")
    print("=" * 75)

    for name, df in [
        ("train", train),
        ("validation", validation),
        ("test", test),
    ]:
        duplicates = df["message"].map(
            normalize_message
        ).duplicated().sum()

        print(
            f"{name}: {duplicates} duplicate messages"
        )

    # Response diversity
    print("\n" + "=" * 75)
    print("RESPONSE DIVERSITY")
    print("=" * 75)

    stats = (
        train.groupby("intent")
        .agg(
            rows=("response", "size"),
            unique_messages=("message", "nunique"),
            unique_responses=("response", "nunique"),
        )
    )

    stats["response_diversity"] = (
        stats["unique_responses"] / stats["rows"]
    )

    print(stats.to_string())

    print("\n" + "=" * 75)
    print("REBUILD COMPLETE")
    print("=" * 75)

    print(
        "\nExisting datasets were backed up with "
        ".pre_dedup_backup."
    )

    print(
        "\nIMPORTANT: Do not retrain the response model yet."
    )


if __name__ == "__main__":
    main()