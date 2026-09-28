import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    precision_recall_fscore_support,
)

from app.ml.rule_engine import RuleBasedRiskEngine
from app.ml.text_classifier import MindCareTextClassifier


DATA_PATH = "data/mindcare_clean/test.csv"


HIGH_RISK_LABELS = {
    "crisis",
    "self_harm",
}


def evaluate_system(name, y_true, y_pred):

    print("\n" + "=" * 70)
    print(name)
    print("=" * 70)

    accuracy = accuracy_score(
        y_true,
        y_pred,
    )

    print(f"\nAccuracy: {accuracy:.4f}")

    print("\nClassification Report:")

    print(
        classification_report(
            y_true,
            y_pred,
            zero_division=0,
        )
    )

    print("Confusion Matrix:")

    labels = [
        "crisis",
        "self_harm",
        "negated",
        "contextual",
        "neutral",
        "positive",
    ]

    matrix = confusion_matrix(
        y_true,
        y_pred,
        labels=labels,
    )

    print(
        pd.DataFrame(
            matrix,
            index=labels,
            columns=labels,
        )
    )

    # Binary high-risk evaluation
    y_true_risk = [
        label in HIGH_RISK_LABELS
        for label in y_true
    ]

    y_pred_risk = [
        label in HIGH_RISK_LABELS
        for label in y_pred
    ]

    precision, recall, f1, _ = (
        precision_recall_fscore_support(
            y_true_risk,
            y_pred_risk,
            average="binary",
            zero_division=0,
        )
    )

    print("\nHigh-Risk Metrics:")

    print(
        f"Precision: {precision:.4f}"
    )

    print(
        f"Recall:    {recall:.4f}"
    )

    print(
        f"F1:        {f1:.4f}"
    )

    tn, fp, fn, tp = confusion_matrix(
        y_true_risk,
        y_pred_risk,
    ).ravel()

    print("\nHigh-Risk Counts:")

    print(f"TN: {tn}")
    print(f"FP: {fp}")
    print(f"FN: {fn}")
    print(f"TP: {tp}")


def main():

    df = pd.read_csv(DATA_PATH)

    messages = df["message"].tolist()
    y_true = df["category"].tolist()

    # --------------------------------------------------
    # RULES
    # --------------------------------------------------

    rule_engine = RuleBasedRiskEngine()

    rule_predictions = [
        rule_engine.predict(message)
        for message in messages
    ]

    # --------------------------------------------------
    # ML
    # --------------------------------------------------

    ml_model = MindCareTextClassifier()
    ml_model.load()

    ml_predictions = ml_model.predict_many(
        messages
    )

    # --------------------------------------------------
    # RESULTS
    # --------------------------------------------------

    print("\n")
    print("=" * 70)
    print("MINDCARE — RULES vs ML")
    print("=" * 70)

    print(
        f"\nTest samples: {len(df)}"
    )

    evaluate_system(
        "RULE-BASED BASELINE",
        y_true,
        rule_predictions,
    )

    evaluate_system(
        "TF-IDF + LOGISTIC REGRESSION",
        y_true,
        ml_predictions,
    )


if __name__ == "__main__":
    main()