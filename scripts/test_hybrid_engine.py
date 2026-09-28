from app.ml.hybrid_engine import HybridRiskEngine


def main():

    engine = HybridRiskEngine()

    examples = [
        "I am feeling happy today.",
        "I have several assignments due this week.",
        "I am not thinking about self-harm.",
        "I am thinking about suicide.",
        "My friend is having thoughts about self-harm.",
        "I feel better and more hopeful today.",
    ]

    print("=" * 70)
    print("MINDCARE HYBRID ENGINE TEST")
    print("=" * 70)

    for message in examples:

        result = engine.predict(message)

        print("\n" + "-" * 70)
        print("Message:")
        print(message)

        print("\nFinal:")
        print(
            f"Category: {result['category']}"
        )

        print(
            f"Risk: {result['risk_level']}"
        )

        print(
            f"Decision source: "
            f"{result['decision_source']}"
        )

        print(
            f"ML category: "
            f"{result['ml_category']}"
        )

        print(
            f"ML confidence: "
            f"{result['ml_confidence']:.4f}"
        )

        print(
            f"Rule category: "
            f"{result['rule_category']}"
        )

        print(
            f"Matched rule: "
            f"{result['matched_rule']}"
        )


if __name__ == "__main__":
    main()