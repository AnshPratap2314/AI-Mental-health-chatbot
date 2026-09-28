import pandas as pd
from pathlib import Path
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

from app.ml.hybrid_engine import HybridRiskEngine


DATA_PATH = Path("evaluation/challenge_set/challenge_cases.csv")
RESULT_PATH = Path("evaluation/challenge_set/challenge_results.csv")


def main():
    print("=" * 70)
    print("MINDCARE INDEPENDENT CHALLENGE SET")
    print("=" * 70)

    df = pd.read_csv(DATA_PATH)

    engine = HybridRiskEngine()

    predictions = []

    for _, row in df.iterrows():
        result = engine.predict(row["message"])

        predictions.append({
            "message": row["message"],
            "expected": row["expected"],
            "predicted": result["category"],
            "risk_level": result["risk_level"],
            "decision_source": result["decision_source"],
            "ml_category": result["ml_category"],
            "rule_category": result["rule_category"],
            "rule_fired": result["rule_fired"],
            "matched_rule": result["matched_rule"],
            "ml_high_risk_probability": result["ml_high_risk_probability"],
        })

    results = pd.DataFrame(predictions)

    y_true = results["expected"]
    y_pred = results["predicted"]

    accuracy = accuracy_score(y_true, y_pred)

    print(f"\nChallenge samples: {len(results)}")
    print(f"Accuracy: {accuracy:.4f}")

    print("\nClassification Report:")
    print("-" * 70)

    print(
        classification_report(
            y_true,
            y_pred,
            zero_division=0
        )
    )

    print("Confusion Matrix:")
    print("-" * 70)

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
        labels=labels
    )

    matrix_df = pd.DataFrame(
        matrix,
        index=labels,
        columns=labels
    )

    print(matrix_df)

    errors = results[
        results["expected"] != results["predicted"]
    ]

    print("\nErrors:")
    print("-" * 70)

    if errors.empty:
        print("None")
    else:
        print(
            errors[
                [
                    "message",
                    "expected",
                    "predicted",
                    "decision_source",
                ]
            ].to_string(index=False)
        )

    results.to_csv(RESULT_PATH, index=False)

    print(f"\nSaved: {RESULT_PATH}")


if __name__ == "__main__":
    main()