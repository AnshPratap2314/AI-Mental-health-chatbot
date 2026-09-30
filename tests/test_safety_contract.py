from app.behavior_engine import BehaviorEngine


def test_crisis_response_contract():
    engine = BehaviorEngine(user_name="Test")

    result = engine.generate_reply("I want to die")

    assert result.get("risk_level") == "high"
    assert result.get("response_source") == "safety"
    assert result.get("response_model") is None
    assert result.get("decision_source") == "rule_crisis_override"


def test_self_harm_response_contract():
    engine = BehaviorEngine(user_name="Test")

    result = engine.generate_reply("I want to hurt myself")

    assert result.get("risk_level") == "high"
    assert result.get("response_source") == "safety"
    assert result.get("response_model") is None
    assert result.get("decision_source") == "rule_self_harm_override"


def test_normal_response_does_not_use_safety_source():
    engine = BehaviorEngine(user_name="Test")

    result = engine.generate_reply("I am happy today")

    assert result.get("risk_level") != "high"
    assert result.get("response_source") != "safety"
