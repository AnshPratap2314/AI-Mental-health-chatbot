import pandas as pd
from pathlib import Path
from collections import Counter

from app.ml.hybrid_engine import HybridRiskEngine


DATA_PATH = Path("data/mindcare_clean/test.csv")
OUTPUT_PATH = Path("evaluation/decision_source_analysis.csv")


def main():
    print("=" * 70)
    print("MINDCARE HYBRID DECISION-SOURCE ANALYSIS")
    print("=" * 70)

    df = pd.read_csv(DATA_PATH)
    engine = HybridRiskEngine()

    rows = []

    for _, row in df.iterrows():
        result = engine.predict(row["message"])

        rows.append({
            "message": row["message"],
            "expected": row["category"],
            "predicted": result["category"],
            "decision_source": result["decision_source"],
            "risk_level": result["risk_level"],
            "ml_category": result["ml_category"],
            "rule_category": result["rule_category"],
            "rule_fired": result["rule_fired"],
            "matched_rule": result["matched_rule"],
            "ml_high_risk_probability": result["ml_high_risk_probability"],
            "correct": row["category"] == result["category"],
        })

    results = pd.DataFrame(rows)

    print(f"\nTest samples: {len(results)}")

    print("\nDecision Source Distribution")
    print("-" * 70)

    source_counts = (
        results["decision_source"]
        .value_counts()
        .sort_values(ascending=False)
    )

    for source, count in source_counts.items():
        percentage = count / len(results) * 100
        print(f"{source:30s}: {count:3d} ({percentage:6.2f}%)")

    print("\nDecision Source Accuracy")
    print("-" * 70)

    source_accuracy = (
        results
        .groupby("decision_source")["correct"]
        .agg(["count", "mean"])
        .sort_values("count", ascending=False)
    )

    for source, row in source_accuracy.iterrows():
        print(
            f"{source:30s}: "
            f"{int(row['count']):3d} samples | "
            f"accuracy={row['mean']:.4f}"
        )

    print("\nRule-Fired Distribution")
    print("-" * 70)

    rule_counts = (
        results["rule_fired"]
        .fillna(False)
        .astype(str)
        .value_counts()
    )

    for rule, count in rule_counts.items():
        print(f"{rule:30s}: {count:3d}")

    results.to_csv(OUTPUT_PATH, index=False)

    print(f"\nSaved: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()