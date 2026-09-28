import re
from pathlib import Path

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


DATA_DIR = Path("data/mindcare_clean")

TRAIN_PATH = DATA_DIR / "train.csv"
VALIDATION_PATH = DATA_DIR / "validation.csv"
TEST_PATH = DATA_DIR / "test.csv"


def normalize_text(text):
    text = str(text).lower().strip()
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[^\w\s]", "", text)
    return text


def check_normalized_duplicates(df, name):
    normalized = df["message"].apply(normalize_text)
    duplicates = normalized.duplicated().sum()

    print(f"{name} normalized duplicates: {duplicates}")

    return set(normalized)


def compare_sets(train_set, other_set, name):
    overlap = train_set & other_set

    print(
        f"Normalized overlap Train ∩ {name}: "
        f"{len(overlap)}"
    )


def semantic_similarity_check(
    train_df,
    test_df,
    split_name,
    threshold=0.90,
):
    print("\n" + "=" * 60)
    print(
        f"SEMANTIC SIMILARITY: TRAIN vs {split_name.upper()}"
    )
    print("=" * 60)

    combined = pd.concat(
        [
            train_df["message"],
            test_df["message"],
        ],
        ignore_index=True,
    )

    vectorizer = TfidfVectorizer(
        lowercase=True,
        ngram_range=(1, 2),
        min_df=1,
    )

    matrix = vectorizer.fit_transform(combined)

    train_matrix = matrix[:len(train_df)]
    other_matrix = matrix[len(train_df):]

    similarities = cosine_similarity(
        other_matrix,
        train_matrix,
    )

    max_similarities = similarities.max(axis=1)

    suspicious = max_similarities >= threshold

    print(f"Compared samples: {len(test_df)}")
    print(f"Similarity threshold: {threshold:.2f}")
    print(
        f"Potential near-duplicates: "
        f"{suspicious.sum()}"
    )

    if suspicious.sum() > 0:

        print("\nTop suspicious examples:")

        indices = suspicious.nonzero()[0]

        # Display at most 10 examples
        for other_index in indices[:10]:

            train_index = similarities[
                other_index
            ].argmax()

            score = similarities[
                other_index,
                train_index,
            ]

            print("\n" + "-" * 60)
            print(f"Similarity: {score:.4f}")

            print("OTHER:")
            print(
                test_df.iloc[other_index]["message"]
            )

            print("TRAIN:")
            print(
                train_df.iloc[train_index]["message"]
            )


def main():

    train = pd.read_csv(TRAIN_PATH)
    validation = pd.read_csv(VALIDATION_PATH)
    test = pd.read_csv(TEST_PATH)

    print("=" * 60)
    print("MINDCARE NEAR-DUPLICATE DATASET AUDIT")
    print("=" * 60)

    print(f"\nTrain samples: {len(train)}")
    print(f"Validation samples: {len(validation)}")
    print(f"Test samples: {len(test)}")

    print("\n" + "=" * 60)
    print("NORMALIZED DUPLICATE CHECK")
    print("=" * 60)

    train_normalized = check_normalized_duplicates(
        train,
        "Train",
    )

    validation_normalized = check_normalized_duplicates(
        validation,
        "Validation",
    )

    test_normalized = check_normalized_duplicates(
        test,
        "Test",
    )

    print()

    compare_sets(
        train_normalized,
        validation_normalized,
        "Validation",
    )

    compare_sets(
        train_normalized,
        test_normalized,
        "Test",
    )

    compare_sets(
        validation_normalized,
        test_normalized,
        "Test",
    )

    semantic_similarity_check(
        train,
        validation,
        "Validation",
        threshold=0.90,
    )

    semantic_similarity_check(
        train,
        test,
        "Test",
        threshold=0.90,
    )


if __name__ == "__main__":
    main()