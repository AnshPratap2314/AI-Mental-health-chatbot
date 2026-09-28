from app.ml.rule_engine import RuleBasedRiskEngine


def main():

    engine = RuleBasedRiskEngine()

    examples = [
        "I am feeling happy today.",
        "I have several assignments due this week.",
        "I am not thinking about self-harm.",
        "I am thinking about suicide.",
        "My friend is having thoughts about self-harm.",
        "I feel better and more hopeful today.",
    ]

    print("=" * 60)
    print("MINDCARE RULE ENGINE TEST")
    print("=" * 60)

    for message in examples:

        result = engine.predict_detailed(message)

        print("\nMessage:")
        print(message)

        print("Result:")
        print(result)


if __name__ == "__main__":
    main()