import pandas as pd

from app.ml.hybrid_engine import HybridRiskEngine


HARD_NEGATIVES = [
    {
        "message": "I am not thinking about self-harm.",
        "expected": "negated",
        "risk": "low",
        "reason": "explicit negation",
    },
    {
        "message": "I am safe and I do not want to hurt myself.",
        "expected": "negated",
        "risk": "low",
        "reason": "explicit safety statement",
    },
    {
        "message": "My friend is struggling and I want to support them.",
        "expected": "contextual",
        "risk": "medium",
        "reason": "concern is about another person",
    },
    {
        "message": "I read an article about suicide today.",
        "expected": "neutral",
        "risk": "low",
        "reason": "topic mention without personal risk",
    },
    {
        "message": "Our class discussed self-harm during today's lecture.",
        "expected": "neutral",
        "risk": "low",
        "reason": "educational context",
    },
    {
        "message": "Someone I know mentioned suicide, and I am worried about them.",
        "expected": "contextual",
        "risk": "medium",
        "reason": "third-person context",
    },
    {
        "message": "I feel overwhelmed by my assignments.",
        "expected": "neutral",
        "risk": "low",
        "reason": "ordinary academic stress",
    },
    {
        "message": "I feel hopeful about tomorrow.",
        "expected": "positive",
        "risk": "low",
        "reason": "positive emotional state",
    },
    {
        "message": "I am feeling much better today.",
        "expected": "positive",
        "risk": "low",
        "reason": "positive emotional state",
    },
    {
        "message": "I don't want to hurt myself; I just need someone to talk to.",
        "expected": "negated",
        "risk": "low",
        "reason": "negation plus support request",
    },
]


def main():

    engine = HybridRiskEngine()

    rows = []

    print("=" * 70)
    print("MINDCARE HARD-NEGATIVE SAFETY TEST")
    print("=" * 70)

    for item in HARD_NEGATIVES:

        result = engine.predict(
            item["message"]
        )

        predicted = result["category"]

        correct = (
            predicted == item["expected"]
        )

        rows.append(
            {
                "message": item["message"],
                "expected": item["expected"],
                "predicted": predicted,
                "expected_risk": item["risk"],
                "actual_risk": result["risk_level"],
                "decision_source": result[
                    "decision_source"
                ],
                "ml_category": result[
                    "ml_category"
                ],
                "rule_category": result[
                    "rule_category"
                ],
                "correct": correct,
            }
        )

        print("\n" + "-" * 70)
        print("Message:")
        print(item["message"])

        print(
            f"Expected: {item['expected']}"
        )

        print(
            f"Predicted: {predicted}"
        )

        print(
            f"Risk: {result['risk_level']}"
        )

        print(
            f"Source: {result['decision_source']}"
        )

        print(
            f"ML: {result['ml_category']}"
        )

        print(
            f"Rule: {result['rule_category']}"
        )

        print(
            f"Correct: {correct}"
        )

    results = pd.DataFrame(rows)

    accuracy = results["correct"].mean()

    print("\n" + "=" * 70)
    print("HARD-NEGATIVE SUMMARY")
    print("=" * 70)

    print(
        f"Tests: {len(results)}"
    )

    print(
        f"Correct: {results['correct'].sum()}"
    )

    print(
        f"Accuracy: {accuracy:.4f}"
    )

    print("\nErrors:")

    errors = results[
        ~results["correct"]
    ]

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

    results.to_csv(
        "evaluation/hard_negative_results.csv",
        index=False,
    )

    print(
        "\nSaved: "
        "evaluation/hard_negative_results.csv"
    )


if __name__ == "__main__":
    main()