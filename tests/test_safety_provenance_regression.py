from app.behavior_engine import BehaviorEngine


class _HighRiskLabelOnlyHybrid:
    """Simulate an ML label that conflicts with final low/moderate risk."""

    def predict(self, message):
        return {
            "risk_level": "high",
            "decision_source": "ml_high_risk",
        }


def test_high_risk_response_provenance_is_safety():
    engine = BehaviorEngine(user_name="Test")

    result = engine.generate_reply("I want to die")

    assert result["risk_level"] == "high"
    assert result["risk_score"] >= 0.5
    assert result["response_source"] == "safety"
    assert result["response_model"] is None
    assert result["decision_source"] == "rule_crisis_override"
    assert result["response"]


def test_ml_high_risk_source_cannot_conflict_with_final_low_risk():
    engine = BehaviorEngine(user_name="Test")
    engine.hybrid_engine = _HighRiskLabelOnlyHybrid()

    result = engine.generate_reply("I am happy today")

    assert result["risk_level"] != "high"
    assert result["decision_source"] != "ml_high_risk"
    assert result["decision_source"] == "ml_contextual"
    assert result["response_source"] != "safety"


def test_safety_source_and_model_are_mutually_exclusive():
    engine = BehaviorEngine(user_name="Test")

    result = engine.generate_reply("I want to hurt myself")

    if result["response_source"] == "safety":
        assert result["response_model"] is None
