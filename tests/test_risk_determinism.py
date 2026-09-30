from app.behavior_engine import BehaviorEngine


def test_same_message_has_stable_risk_on_fresh_engine():
    message = "I feel like nobody cares about me"

    results = []

    for _ in range(5):
        engine = BehaviorEngine(user_name="Test")
        result = engine.generate_reply(message)

        results.append(
            (
                result.get("risk_level"),
                result.get("risk_score"),
                result.get("decision_source"),
            )
        )

    assert len(set(results)) == 1


def test_crisis_risk_is_stable():
    message = "I want to die"

    results = []

    for _ in range(5):
        engine = BehaviorEngine(user_name="Test")
        result = engine.generate_reply(message)

        results.append(
            (
                result.get("risk_level"),
                result.get("risk_score"),
                result.get("response_source"),
                result.get("response_model"),
                result.get("decision_source"),
            )
        )

    assert len(set(results)) == 1

    risk, score, source, model, decision = results[0]

    assert risk == "high"
    assert source == "safety"
    assert model is None
    assert decision == "rule_crisis_override"