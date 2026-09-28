from pathlib import Path

import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)

from app.ml.rule_engine import MindCareRuleEngine
from app.ml.text_classifier import MindCareTextClassifier
from app.ml.hybrid_engine import HybridRiskEngine


DATA_PATH = Path("data/mindcare_clean/test.csv")
OUTPUT_PATH = Path("evaluation/canonical_results.csv")

LABELS = [
    "crisis",
    "self_harm",
    "negated",
    "contextual",
    "neutral",
    "positive",
]

HIGH_RISK_LABELS = {"crisis", "self_harm"}


def high_risk_metrics(y_true, y_pred):
    true_binary = [
        1 if label in HIGH_RISK_LABELS else 0
        for label in y_true
    ]

    pred_binary = [
        1 if label in HIGH_RISK_LABELS else 0
        for label in y_pred
    ]

    precision = precision_score(
        true_binary,
        pred_binary,
        zero_division=0,
    )

    recall = recall_score(
        true_binary,
        pred_binary,
        zero_division=0,
    )

    f1 = f1_score(
        true_binary,
        pred_binary,
        zero_division=0,
    )

    tn, fp, fn, tp = confusion_matrix(
        true_binary,
        pred_binary,
        labels=[0, 1],
    ).ravel()

    return {
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "TN": tn,
        "FP": fp,
        "FN": fn,
        "TP": tp,
    }


def evaluate(name, y_true, y_pred):
    accuracy = accuracy_score(y_true, y_pred)

    macro_precision = precision_score(
        y_true,
        y_pred,
        labels=LABELS,
        average="macro",
        zero_division=0,
    )

    macro_recall = recall_score(
        y_true,
        y_pred,
        labels=LABELS,
        average="macro",
        zero_division=0,
    )

    macro_f1 = f1_score(
        y_true,
        y_pred,
        labels=LABELS,
        average="macro",
        zero_division=0,
    )

    high_risk = high_risk_metrics(
        y_true,
        y_pred,
    )

    print("\n" + "=" * 70)
    print(name)
    print("=" * 70)

    print(f"Accuracy:           {accuracy:.4f}")
    print(f"Macro Precision:    {macro_precision:.4f}")
    print(f"Macro Recall:       {macro_recall:.4f}")
    print(f"Macro F1:           {macro_f1:.4f}")

    print("\nHigh-Risk Metrics:")
    print(
        f"Precision:          {high_risk['precision']:.4f}"
    )
    print(
        f"Recall:             {high_risk['recall']:.4f}"
    )
    print(
        f"F1:                 {high_risk['f1']:.4f}"
    )

    print("\nHigh-Risk Confusion Matrix:")
    print(f"TN: {high_risk['TN']}")
    print(f"FP: {high_risk['FP']}")
    print(f"FN: {high_risk['FN']}")
    print(f"TP: {high_risk['TP']}")

    print("\nMulticlass Classification Report:")
    print(
        classification_report(
            y_true,
            y_pred,
            labels=LABELS,
            zero_division=0,
        )
    )

    return {
        "system": name,
        "accuracy": accuracy,
        "macro_f1": macro_f1,
        "high_risk_precision": high_risk["precision"],
        "high_risk_recall": high_risk["recall"],
        "high_risk_f1": high_risk["f1"],
        "fp": high_risk["FP"],
        "fn": high_risk["FN"],
    }


def main():
    print("=" * 70)
    print("MINDCARE CANONICAL BENCHMARK")
    print("=" * 70)

    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"Test dataset not found: {DATA_PATH}"
        )

    df = pd.read_csv(DATA_PATH)

    required_columns = {
        "message",
        "category",
    }

    missing = required_columns - set(df.columns)

    if missing:
        raise ValueError(
            f"Missing required columns: {sorted(missing)}"
        )

    messages = df["message"].astype(str).tolist()
    y_true = df["category"].astype(str).tolist()

    print(f"\nTest samples: {len(df)}")
    print(f"Dataset: {DATA_PATH}")

    # ---------------------------------------------------------
    # 1. RULE-BASED
    # ---------------------------------------------------------

    rule_engine = MindCareRuleEngine()

    rule_predictions = [
        rule_engine.predict(message)
        for message in messages
    ]

    rule_result = evaluate(
        "RULE-BASED",
        y_true,
        rule_predictions,
    )

    # ---------------------------------------------------------
    # 2. TF-IDF + LOGISTIC REGRESSION
    # ---------------------------------------------------------

    ml_model = MindCareTextClassifier()
    ml_model.load()

    ml_predictions = list(
        ml_model.predict_many(messages)
    )

    ml_result = evaluate(
        "TF-IDF + LOGISTIC REGRESSION",
        y_true,
        ml_predictions,
    )

    # ---------------------------------------------------------
    # 3. HYBRID
    # ---------------------------------------------------------

    hybrid_engine = HybridRiskEngine()

    hybrid_predictions = [
        hybrid_engine.predict(message)["category"]
        for message in messages
    ]

    hybrid_result = evaluate(
        "HYBRID",
        y_true,
        hybrid_predictions,
    )

    # ---------------------------------------------------------
    # FINAL COMPARISON
    # ---------------------------------------------------------

    results = pd.DataFrame(
        [
            rule_result,
            ml_result,
            hybrid_result,
        ]
    )

    print("\n" + "=" * 70)
    print("FINAL COMPARISON")
    print("=" * 70)

    print(
        results.to_string(
            index=False,
            float_format=lambda x: f"{x:.6f}",
        )
    )

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    results.to_csv(
        OUTPUT_PATH,
        index=False,
    )

    print(f"\nSaved: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()