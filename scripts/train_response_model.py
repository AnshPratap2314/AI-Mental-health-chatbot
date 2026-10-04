from __future__ import annotations

import json

import shutil

from datetime import datetime

from pathlib import Path

import re
import unicodedata

import joblib

import numpy as np

import pandas as pd

from sklearn import __version__ as sklearn_version

from sklearn.feature_extraction.text import TfidfVectorizer

from sklearn.linear_model import LogisticRegression

from sklearn.metrics import accuracy_score, f1_score

from sklearn.metrics.pairwise import cosine_similarity

from sklearn.pipeline import FeatureUnion

# ============================================================
# PATHS
# ============================================================
ROOT = Path(__file__).resolve().parents[1]

DATA_DIR = ROOT / "data" / "mindcare_responses"

MODEL_DIR = ROOT / "models" / "response_model"

TRAIN_PATH = DATA_DIR / "train.csv"

VALIDATION_PATH = DATA_DIR / "validation.csv"

TEST_PATH = DATA_DIR / "test.csv"

MODEL_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================
# CONFIG
# ============================================================
TARGETS = [

    "intent",

    "mood",

    "topic",

    "risk_level",

]

REQUIRED_COLUMNS = {

    "message",

    "response",

    "intent",

    "mood",

    "topic",

    "risk_level",

}

EXPECTED_INTENTS = {

    "anger",

    "anxiety",

    "career",

    "casual",

    "exam_stress",

    "family",

    "gratitude",

    "greeting",

    "high_risk",

    "loneliness",

    "motivation",

    "negated_distress",

    "overwhelm",

    "positive",

    "relationship",

    "sadness",

    "self_reflection",

    "sleep",

    "uncertainty",

    "work_stress",

}

RANDOM_STATE = 42

# ============================================================
# DATA
# ============================================================
RESPONSE_NORMALIZER_VERSION = "v1-clean-boundary-grammar"


def normalize_response_text(response: str) -> str:
    """Normalize response-bank text before any model artifact is built."""
    text = unicodedata.normalize("NFKC", str(response or ""))
    text = re.sub(r"[\u200b-\u200f\u2060\ufeff]", "", text)
    text = " ".join(text.split()).strip()
    repairs = (
        (r"\borsomething\b", "or something"), (r"\bisto\b", "is to"),
        (r"\bimmediatedanger\b", "immediate danger"), (r"\bpracticaloption\b", "practical option"),
        (r"\bworryingyou\b", "worrying you"), (r"\bwhatkind\b", "what kind"),
        (r"\batime\b", "a time"), (r"\bonestep\b", "one step"), (r"\bonesmall\b", "one small"),
        (r"\bmightreach\b", "might reach"), (r"\bmightfind\b", "might find"),
        (r"\btogive\b", "to give"), (r"\btostart\b", "to start"), (r"\btoseparate\b", "to separate"),
        (r"\btounderstanding\b", "to understanding"), (r"\bonunderstanding\b", "on understanding"),
        (r"\bonfocus\b", "on focus"), (r"\btheimmediate\b", "the immediate"), (r"\bitmay\b", "it may"),
        (r"\bwrite downwhat\b", "write down what"), (r"\bcouldbe\b", "could be"),
        (r"\bstepcould\b", "step could"), (r"\bgiveyourself\b", "give yourself"),
        (r"\bandthink\b", "and think"), (r"\btakethe\b", "take the"), (r"\bthesituation\b", "the situation"),
    )
    for pattern, replacement in repairs:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    for pattern, replacement in (
        (r"\bsituation\s+situation\b", "situation"),
        (r"\byou\s+are\s+wanting\b", "you want"),
        (r"\bconsider\s+take\b", "consider taking"),
        (r"\bconsider\s+write\b", "consider writing"),
        (r"\bconsider\s+separate\b", "consider separating"),
        (r"\bconsider\s+give\b", "consider giving"),
        (r"\bconsider\s+focus\b", "consider focusing"),
    ):
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    text = re.sub(r"\s+([,.!?;:])", r"\1", text)
    text = re.sub(r"([.!?])(?=[A-Za-z])", r"\1 ", text)
    return " ".join(text.split()).strip()


def response_quality_artifacts(text: str) -> list[str]:
    """Return known malformed response patterns that should never enter an artifact."""
    value = str(text or "")
    patterns = (
        r"\borsomething\b", r"\bisto\b", r"\bimmediatedanger\b", r"\bpracticaloption\b",
        r"\bworryingyou\b", r"\bwhatkind\b", r"\batime\b", r"\bonestep\b", r"\bonesmall\b",
        r"\bmightreach\b", r"\bmightfind\b", r"\btogive\b", r"\btostart\b", r"\btoseparate\b",
        r"\btheimmediate\b", r"\bitmay\b", r"\bwrite downwhat\b", r"\bcouldbe\b",
        r"\bstepcould\b", r"\bgiveyourself\b", r"\bandthink\b", r"\btakethe\b",
        r"\bthesituation\b",
    )
    return [p for p in patterns if re.search(p, value, flags=re.IGNORECASE)]


def load_split(path: Path) -> pd.DataFrame:

    if not path.exists():

        raise FileNotFoundError(

            f"Dataset split not found: {path}"

        )

    df = pd.read_csv(path)

    missing = REQUIRED_COLUMNS - set(df.columns)

    if missing:

        raise ValueError(

            f"{path.name} missing columns: "

            + ", ".join(sorted(missing))

        )

    df = df.copy()

    df["message"] = (

        df["message"]

        .fillna("")

        .astype(str)

        .str.strip()

    )

    df["response"] = (

        df["response"]

        .fillna("")

        .astype(str)

        .map(normalize_response_text)
    )

    df = df[

        (df["message"] != "")

        & (df["response"] != "")

    ].reset_index(drop=True)

    for column in TARGETS:

        df[column] = (

            df[column]

            .fillna("")

            .astype(str)

            .str.strip()

            .str.lower()

        )

    return df

def normalize_messages(df: pd.DataFrame) -> set[str]:

    return set(

        df["message"]

        .str.lower()

        .str.strip()

    )

def validate_dataset(

    train_df: pd.DataFrame,

    validation_df: pd.DataFrame,

    test_df: pd.DataFrame,

    ) -> dict:

    print("\n" + "=" * 70)

    print("DATASET INTEGRITY CHECK")

    print("=" * 70)

    splits = {

        "train": train_df,

        "validation": validation_df,

        "test": test_df,

    }

    response_artifacts = {}
    for name, df in splits.items():
        bad = []
        for value in df["response"]:
            bad.extend(response_quality_artifacts(value))
        response_artifacts[name] = len(bad)
        if bad:
            raise ValueError(
                f"{name} contains {len(bad)} malformed response token artifacts "
                "after normalization."
            )

# Basic structure.
    for name, df in splits.items():

        duplicate_messages = int(

            df["message"]

            .str.lower()

            .str.strip()

            .duplicated()

            .sum()

        )

        duplicate_responses = int(

            df["response"].duplicated().sum()

        )

        print(f"\n{name}:")

        print(f"  rows: {len(df)}")

        print(f"  unique messages: {df['message'].nunique()}")

        print(f"  unique responses: {df['response'].nunique()}")

        print(f"  duplicate messages: {duplicate_messages}")

        print(f"  duplicate responses: {duplicate_responses}")

        print(f"  intents: {df['intent'].nunique()}")

        if duplicate_messages:

            raise ValueError(

                f"{name} contains duplicate messages."

            )

        if df["message"].nunique() != len(df):

            raise ValueError(

                f"{name} does not contain unique messages."

            )

        if not df[TARGETS].notna().all().all():

            raise ValueError(

                f"{name} contains missing target values."

            )

# Expected intent set.
    for name, df in splits.items():

        actual = set(df["intent"].unique())

        missing = EXPECTED_INTENTS - actual

        unexpected = actual - EXPECTED_INTENTS

        if missing or unexpected:

            raise ValueError(

                f"{name} intent mismatch. "

                f"Missing={sorted(missing)}, "

                f"Unexpected={sorted(unexpected)}"

            )

# Cross-split message leakage.
    train_messages = normalize_messages(train_df)

    validation_messages = normalize_messages(validation_df)

    test_messages = normalize_messages(test_df)

    train_validation_overlap = (

        train_messages & validation_messages

    )

    train_test_overlap = (

        train_messages & test_messages

    )

    validation_test_overlap = (

        validation_messages & test_messages

    )

    print("\nCross-split message leakage:")

    print(

        "  train -> validation:",

        len(train_validation_overlap),

    )

    print(

        "  train -> test:",

        len(train_test_overlap),

    )

    print(

        "  validation -> test:",

        len(validation_test_overlap),

    )

    if (

        train_validation_overlap

        or train_test_overlap

        or validation_test_overlap

    ):

        raise ValueError(

            "DATA LEAKAGE DETECTED. Training stopped."

        )

# Cross-split response overlap is NOT treated as leakage because
# response text is intentionally reused as a response bank.
    print(

        "\nNote: repeated response texts across splits are allowed; "

        "message leakage is the primary split-integrity check."

    )

# Per-intent distribution.
    print("\nPer-intent distribution:")

    distribution = pd.DataFrame({

        "train": train_df["intent"].value_counts(),

        "validation": validation_df["intent"].value_counts(),

        "test": test_df["intent"].value_counts(),

    }).fillna(0).astype(int).sort_index()

    print(distribution.to_string())

    return {

        "train": len(train_df),

        "validation": len(validation_df),

        "test": len(test_df),

        "train_validation_overlap": len(train_validation_overlap),

        "train_test_overlap": len(train_test_overlap),

        "validation_test_overlap": len(

            validation_test_overlap

        ),

        "train_duplicate_messages": 0,

        "validation_duplicate_messages": 0,

        "test_duplicate_messages": 0,

        "intent_distribution": distribution.to_dict(),

    }

# ============================================================
# FEATURE EXTRACTOR
# ============================================================
def build_feature_extractor():

    word_vectorizer = TfidfVectorizer(

        lowercase=True,

        strip_accents="unicode",

        ngram_range=(1, 2),

        min_df=1,

        max_df=0.98,

        sublinear_tf=True,

    )

    char_vectorizer = TfidfVectorizer(

        analyzer="char_wb",

        lowercase=True,

        ngram_range=(3, 5),

        min_df=1,

        sublinear_tf=True,

    )

    return FeatureUnion(

        [

            ("word", word_vectorizer),

            ("char", char_vectorizer),

        ]

    )

# ============================================================
# CLASSIFIER TRAINING
# ============================================================
def train_classifiers(

    train_df: pd.DataFrame,

    validation_df: pd.DataFrame,

    test_df: pd.DataFrame,

    ):

    print("\nBuilding classifier features...")

    features = build_feature_extractor()

    X_train = features.fit_transform(

        train_df["message"]

    )

    X_validation = features.transform(

        validation_df["message"]

    )

    X_test = features.transform(

        test_df["message"]

    )

    print(

        f"Feature matrix: "

        f"train={X_train.shape}, "

        f"validation={X_validation.shape}, "

        f"test={X_test.shape}"

    )

    models = {}

    metrics = {}

    for target in TARGETS:

        print(f"\nTraining target: {target}")

        model = LogisticRegression(

            max_iter=3000,

            class_weight="balanced",

            random_state=RANDOM_STATE,

        )

        model.fit(

            X_train,

            train_df[target],

        )

        models[target] = model

        validation_predictions = model.predict(

            X_validation

        )

        test_predictions = model.predict(

            X_test

        )

        validation_accuracy = accuracy_score(

            validation_df[target],

            validation_predictions,

        )

        validation_f1 = f1_score(

            validation_df[target],

            validation_predictions,

            average="macro",

            zero_division=0,

        )

        test_accuracy = accuracy_score(

            test_df[target],

            test_predictions,

        )

        test_f1 = f1_score(

            test_df[target],

            test_predictions,

            average="macro",

            zero_division=0,

        )

        metrics[target] = {

            "validation_accuracy": float(

                validation_accuracy

            ),

            "validation_macro_f1": float(

                validation_f1

            ),

            "test_accuracy": float(

                test_accuracy

            ),

            "test_macro_f1": float(

                test_f1

            ),

        }

        print(

            f"  validation accuracy: "

            f"{validation_accuracy:.4f}"

        )

        print(

            f"  validation macro F1: "

            f"{validation_f1:.4f}"

        )

        print(

            f"  test accuracy: "

            f"{test_accuracy:.4f}"

        )

        print(

            f"  test macro F1: "

            f"{test_f1:.4f}"

        )

    classifier_bundle = {

# Keep these keys compatible with the existing
# app/response_model.py integration.
        "features": features,

        "models": models,

        "targets": TARGETS,

        "sklearn_version": sklearn_version,

        "model_version": "mindcare-response-model-v3-clean-response-bank",

    }

    return classifier_bundle, metrics

# ============================================================
# RESPONSE RETRIEVAL INDEX
# ============================================================
def build_response_index(

    train_df: pd.DataFrame,

    ):

    print("\nBuilding response retrieval index...")

    vectorizer = TfidfVectorizer(

        lowercase=True,

        strip_accents="unicode",

        ngram_range=(1, 2),

        min_df=1,

        max_df=0.98,

        sublinear_tf=True,

    )

    matrix = vectorizer.fit_transform(

        train_df["message"]

    )

    records = train_df.copy()
    records["response"] = records["response"].map(normalize_response_text)
    records = records.to_dict(orient="records")

    index = {

        "vectorizer": vectorizer,

        "matrix": matrix,

        "records": records,

        "sklearn_version": sklearn_version,

        "model_version": "mindcare-response-model-v3-clean-response-bank",

        "retrieval_source": "training_messages",

    }

    return index

# ============================================================
# RETRIEVAL EVALUATION
# ============================================================
def evaluate_retrieval(

    index,

    test_df: pd.DataFrame,

    ):

    vectorizer = index["vectorizer"]

    matrix = index["matrix"]

    records = index["records"]

    intent_matches = []

    mood_matches = []

    topic_matches = []

    risk_matches = []

    response_matches = []

    similarities = []

    for _, row in test_df.iterrows():

        query = vectorizer.transform(

            [row["message"]]

        )

        scores = cosine_similarity(

            query,

            matrix,

        )[0]

        best_index = int(

            np.argmax(scores)

        )

        best = records[best_index]

        similarities.append(

            float(scores[best_index])

        )

        intent_matches.append(

            best["intent"] == row["intent"]

        )

        mood_matches.append(

            best["mood"] == row["mood"]

        )

        topic_matches.append(

            best["topic"] == row["topic"]

        )

        risk_matches.append(

            best["risk_level"] == row["risk_level"]

        )

        response_matches.append(

            str(best["response"]).strip()

            == str(row["response"]).strip()

        )

    return {

        "intent_match": float(

            np.mean(intent_matches)

        ),

        "mood_match": float(

            np.mean(mood_matches)

        ),

        "topic_match": float(

            np.mean(topic_matches)

        ),

        "risk_match": float(

            np.mean(risk_matches)

        ),

        "exact_response_match": float(

            np.mean(response_matches)

        ),

        "mean_similarity": float(

            np.mean(similarities)

        ),

    }

# ============================================================
# BACKUP
# ============================================================
def backup_existing_models():

    timestamp = datetime.now().strftime(

        "%Y%m%d_%H%M%S"

    )

    backup_dir = (

        ROOT

        / "models"

        / f"response_model_backup_{timestamp}"

    )

    existing_files = [

        MODEL_DIR / "response_classifier.joblib",

        MODEL_DIR / "response_index.joblib",

        MODEL_DIR / "training_report.json",

    ]

    existing_files = [

        path for path in existing_files

        if path.exists()

    ]

    if not existing_files:

        print("\nNo existing response-model files to back up.")

        return None

    backup_dir.mkdir(

        parents=True,

        exist_ok=True,

    )

    for source in existing_files:

        shutil.copy2(

            source,

            backup_dir / source.name,

        )

    print("\nExisting response model backed up to:")

    print(backup_dir)

    return backup_dir

# ============================================================
# MAIN
# ============================================================
def main():

    print("=" * 70)

    print("MINDCARE TRAINED RESPONSE MODEL — V3 CLEAN RESPONSE BANK")

    print("=" * 70)

    print(

        f"\nscikit-learn version: "

        f"{sklearn_version}"

    )

    print("\nLoading datasets...")

    train_df = load_split(

        TRAIN_PATH

    )

    validation_df = load_split(

        VALIDATION_PATH

    )

    test_df = load_split(

        TEST_PATH

    )

    print(

        f"\nTrain:      {len(train_df)}"

    )

    print(

        f"Validation: {len(validation_df)}"

    )

    print(

        f"Test:       {len(test_df)}"

    )

# --------------------------------------------------------
# Validate BEFORE training.
# --------------------------------------------------------
    dataset_checks = validate_dataset(

        train_df,

        validation_df,

        test_df,

    )

# --------------------------------------------------------
# Train classifiers.
# --------------------------------------------------------
    classifier_bundle, metrics = (

        train_classifiers(

            train_df,

            validation_df,

            test_df,

        )

    )

# --------------------------------------------------------
# Build retrieval index.
# --------------------------------------------------------
    response_index = build_response_index(

        train_df

    )

# --------------------------------------------------------
# Evaluate retrieval on unseen test messages.
# --------------------------------------------------------
    print(

        "\nEvaluating retrieval..."

    )

    retrieval_metrics = (

        evaluate_retrieval(

            response_index,

            test_df,

        )

    )

    metrics["retrieval_top1"] = (

        retrieval_metrics

    )

    print("\nRetrieval metrics:")

    for key, value in retrieval_metrics.items():

        print(

            f"  {key}: {value:.4f}"

        )

# --------------------------------------------------------
# Backup current model BEFORE replacing it.
# --------------------------------------------------------
    backup_dir = backup_existing_models()

# --------------------------------------------------------
# Save.
# --------------------------------------------------------
    classifier_path = (

        MODEL_DIR

        / "response_classifier.joblib"

    )

    index_path = (

        MODEL_DIR

        / "response_index.joblib"

    )

    report_path = (

        MODEL_DIR

        / "training_report.json"

    )

    joblib.dump(

        classifier_bundle,

        classifier_path,

    )

    joblib.dump(

        response_index,

        index_path,

    )

    report = {

        "dataset": {

            "train": len(train_df),

            "validation": len(validation_df),

            "test": len(test_df),

            "total": (

                len(train_df)

                + len(validation_df)

                + len(test_df)

            ),

            "unique_train_messages": int(

                train_df["message"].nunique()

            ),

            "unique_validation_messages": int(

                validation_df["message"].nunique()

            ),

            "unique_test_messages": int(

                test_df["message"].nunique()

            ),

            "unique_train_responses": int(

                train_df["response"].nunique()

            ),

        },

        "environment": {

            "scikit_learn": sklearn_version,

        },

        "model": {

            "version": "mindcare-response-model-v2",

            "features": "word+char TF-IDF",

            "classifier": "LogisticRegression",

            "random_state": RANDOM_STATE,

        },

        "metrics": metrics,

        "dataset_integrity": dataset_checks,

        "backup_directory": (

            str(backup_dir)

            if backup_dir is not None

            else None

        ),

        "safety_note": (

            "Synthetic, non-clinical response dataset. "

            "Safety/risk decisions remain owned by the "

            "deterministic MindCare safety layer. "

            "The normal response model must not override "

            "authoritative crisis/self-harm/plan detection."

        ),

    }

    report_path.write_text(

        json.dumps(

            report,

            indent=2,

        ),

        encoding="utf-8",

    )

    print("\n" + "=" * 70)

    print("TRAINING COMPLETE")

    print("=" * 70)

    print(

        "\nClassifier:",

        classifier_path,

    )

    print(

        "Response index:",

        index_path,

    )

    print(

        "Training report:",

        report_path,

    )

    if backup_dir:

        print(

            "Previous model backup:",

            backup_dir,

        )

    print(

        "\nThe saved classifier bundle remains compatible "

        "with the existing response_model.py contract."

    )

if __name__ == "__main__":

    main()

