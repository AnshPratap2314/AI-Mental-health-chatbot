from pathlib import Path

import pandas as pd

from app.ml.hybrid_engine import HybridRiskEngine


DATA_PATH = Path("data/mindcare_clean/test.csv")
OUTPUT_PATH = Path("evaluation/hybrid_error_analysis.csv")


HIGH_RISK_LABELS = {"crisis", "self_harm"}


def main():
    print("=" * 70)
    print("MINDCARE HYBRID ERROR ANALYSIS")
    print("=" * 70)

    df = pd.read_csv(DATA_PATH)

    engine = HybridRiskEngine()

    records = []

    for _, row in df.iterrows():
        message = str(row["message"])
        expected = str(row["category"])

        result = engine.predict(message)

        predicted = result["category"]

        expected_high_risk = expected in HIGH_RISK_LABELS
        predicted_high_risk = predicted in HIGH_RISK_LABELS

        error_type = "correct"

        if expected_high_risk and not predicted_high_risk:
            error_type = "false_negative"

        elif not expected_high_risk and predicted_high_risk:
            error_type = "false_positive"

        elif expected != predicted:
            error_type = "multiclass_error"

        records.append(
            {
                "message": message,
                "expected": expected,
                "predicted": predicted,
                "error_type": error_type,
                "risk_level": result["risk_level"],
                "decision_source": result["decision_source"],
                "ml_category": result["ml_category"],
                "rule_category": result["rule_category"],
                "rule_fired": result["rule_fired"],
                "matched_rule": result["matched_rule"],
                "ml_high_risk_probability": result[
                    "ml_high_risk_probability"
                ],
            }
        )

    results = pd.DataFrame(records)

    errors = results[
        results["error_type"] != "correct"
    ].copy()

    print(f"\nTotal test samples: {len(results)}")
    print(f"Total errors: {len(errors)}")

    print("\nError distribution:")
    print(
        errors["error_type"]
        .value_counts()
        .to_string()
    )

    print("\n" + "=" * 70)
    print("FALSE POSITIVES")
    print("=" * 70)

    false_positives = errors[
        errors["error_type"] == "false_positive"
    ]

    if false_positives.empty:
        print("None")
    else:
        for _, row in false_positives.iterrows():
            print("\nMessage:")
            print(row["message"])
            print(f"Expected: {row['expected']}")
            print(f"Predicted: {row['predicted']}")
            print(f"Risk: {row['risk_level']}")
            print(f"Decision source: {row['decision_source']}")
            print(f"ML: {row['ml_category']}")
            print(f"Rule: {row['rule_category']}")
            print(f"Rule fired: {row['rule_fired']}")
            print(
                "ML high-risk probability: "
                f"{row['ml_high_risk_probability']:.4f}"
            )

    print("\n" + "=" * 70)
    print("FALSE NEGATIVES")
    print("=" * 70)

    false_negatives = errors[
        errors["error_type"] == "false_negative"
    ]

    if false_negatives.empty:
        print("None")
    else:
        for _, row in false_negatives.iterrows():
            print("\nMessage:")
            print(row["message"])
            print(f"Expected: {row['expected']}")
            print(f"Predicted: {row['predicted']}")
            print(f"Risk: {row['risk_level']}")
            print(f"Decision source: {row['decision_source']}")
            print(f"ML: {row['ml_category']}")
            print(f"Rule: {row['rule_category']}")
            print(f"Rule fired: {row['rule_fired']}")
            print(
                "ML high-risk probability: "
                f"{row['ml_high_risk_probability']:.4f}"
            )

    print("\n" + "=" * 70)
    print("MULTICLASS ERRORS")
    print("=" * 70)

    multiclass_errors = errors[
        errors["error_type"] == "multiclass_error"
    ]

    if multiclass_errors.empty:
        print("None")
    else:
        for _, row in multiclass_errors.iterrows():
            print("\nMessage:")
            print(row["message"])
            print(f"Expected: {row['expected']}")
            print(f"Predicted: {row['predicted']}")
            print(f"Decision source: {row['decision_source']}")
            print(f"ML: {row['ml_category']}")
            print(f"Rule: {row['rule_category']}")

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