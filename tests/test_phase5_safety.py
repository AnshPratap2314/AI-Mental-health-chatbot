from app.safety_policy import SafetyPolicy
from app.safety_engine import SafetyEngine


def test_low_risk_policy():
    policy = SafetyPolicy()

    result = policy.evaluate(
        "low",
        {
            "crisis": False,
            "self_harm": False,
            "intent": False,
            "temporal": False
        },
        0.05
    )

    assert result["risk_level"] == "low"
    assert result["priority"] == "normal"
    assert result["allow_normal_response"] is True
    assert result["allow_random_response"] is False
    assert result["require_human_support"] is False
    assert result["require_immediate_guidance"] is False


def test_moderate_risk_policy():
    policy = SafetyPolicy()

    result = policy.evaluate(
        "moderate",
        {
            "crisis": False,
            "self_harm": False,
            "intent": False,
            "temporal": False
        },
        0.35
    )

    assert result["risk_level"] == "moderate"
    assert result["priority"] == "elevated"
    assert result["allow_normal_response"] is True
    assert result["require_human_support"] is True
    assert result["require_immediate_guidance"] is False


def test_high_crisis_policy():
    policy = SafetyPolicy()

    result = policy.evaluate(
        "high",
        {
            "crisis": True,
            "self_harm": False,
            "intent": True,
            "temporal": True
        },
        0.95
    )

    assert result["risk_level"] == "high"
    assert result["priority"] == "critical"
    assert result["require_safety_response"] is True
    assert result["allow_normal_response"] is False
    assert result["allow_random_response"] is False
    assert result["require_human_support"] is True
    assert result["require_immediate_guidance"] is True


def test_high_self_harm_policy():
    policy = SafetyPolicy()

    result = policy.evaluate(
        "high",
        {
            "crisis": False,
            "self_harm": True,
            "intent": True,
            "temporal": True
        },
        0.9
    )

    assert result["risk_level"] == "high"
    assert result["require_safety_response"] is True
    assert result["require_human_support"] is True
    assert result["require_immediate_guidance"] is True


def test_contextual_suicide_is_not_crisis():
    policy = SafetyPolicy()

    result = policy.evaluate(
        "high",
        {
            "crisis": True,
            "self_harm": True,
            "contextual_suicide": True
        },
        0.8
    )

    assert result["risk_level"] == "low"
    assert result["crisis_detected"] is False
    assert result["self_harm_detected"] is False
    assert result["require_safety_response"] is False


def test_policy_never_allows_random_response():
    policy = SafetyPolicy()

    for risk in [
        "low",
        "moderate",
        "high"
    ]:
        result = policy.evaluate(
            risk,
            {},
            0.2
        )

        assert (
            result["allow_random_response"]
            is False
        )


def test_crisis_detection():
    policy = SafetyPolicy()

    result = policy.evaluate(
        "high",
        {
            "crisis": True,
            "self_harm": False
        },
        0.8
    )

    assert policy.is_crisis(result) is True


def test_human_support_requirement():
    policy = SafetyPolicy()

    low = policy.evaluate(
        "low",
        {},
        0.05
    )

    moderate = policy.evaluate(
        "moderate",
        {},
        0.3
    )

    high = policy.evaluate(
        "high",
        {
            "crisis": True
        },
        0.8
    )

    assert (
        policy.requires_human_support(low)
        is False
    )

    assert (
        policy.requires_human_support(moderate)
        is True
    )

    assert (
        policy.requires_human_support(high)
        is True
    )


def test_immediate_guidance_requirement():
    policy = SafetyPolicy()

    result = policy.evaluate(
        "high",
        {
            "crisis": True,
            "temporal": True
        },
        0.9
    )

    assert (
        policy.requires_immediate_guidance(result)
        is True
    )


def test_safety_engine_low_risk():
    engine = SafetyEngine()

    result = engine.analyze(
        "I had a difficult day",
        "low",
        0.05,
        {
            "sad": True
        }
    )

    assert result["risk_level"] == "low"
    assert (
        result["requires_human_support"]
        is False
    )


def test_safety_engine_moderate_risk():
    engine = SafetyEngine()

    result = engine.analyze(
        "I feel hopeless",
        "moderate",
        0.35,
        {
            "hopelessness": True
        }
    )

    assert result["risk_level"] == "moderate"
    assert (
        result["requires_human_support"]
        is True
    )


def test_safety_engine_high_risk():
    engine = SafetyEngine()

    result = engine.analyze(
        "I want to die",
        "high",
        0.9,
        {
            "crisis": True,
            "intent": True,
            "temporal": True
        }
    )

    assert result["risk_level"] == "high"
    assert (
        result["requires_human_support"]
        is True
    )
    assert (
        result["requires_immediate_guidance"]
        is True
    )


def test_high_risk_response():
    engine = SafetyEngine()

    result = engine.analyze(
        "I want to die",
        "high",
        0.95,
        {
            "crisis": True,
            "intent": True,
            "temporal": True
        }
    )

    response = engine.build_response(
        result
    )

    assert response["risk_level"] == "high"
    assert (
        response["require_safety_response"]
        is True
    )
    assert (
        response["requires_human_support"]
        is True
    )
    assert (
        response["requires_immediate_guidance"]
        is True
    )


def test_moderate_risk_response():
    engine = SafetyEngine()

    result = engine.analyze(
        "I feel hopeless",
        "moderate",
        0.3,
        {
            "hopelessness": True
        }
    )

    response = engine.build_response(
        result
    )

    assert response["risk_level"] == "moderate"
    assert (
        response["requires_human_support"]
        is True
    )
    assert (
        response["requires_immediate_guidance"]
        is False
    )


def test_low_risk_response():
    engine = SafetyEngine()

    result = engine.analyze(
        "I am having a normal day",
        "low",
        0.01,
        {}
    )

    response = engine.build_response(
        result
    )

    assert response["risk_level"] == "low"
    assert (
        response["require_safety_response"]
        is False
    )
    assert (
        response["requires_human_support"]
        is False
    )


def test_normal_response_blocked_for_high_risk():
    engine = SafetyEngine()

    result = engine.analyze(
        "I want to die",
        "high",
        0.9,
        {
            "crisis": True
        }
    )

    assert (
        engine.should_block_normal_response(result)
        is True
    )


def test_normal_response_allowed_for_low_risk():
    engine = SafetyEngine()

    result = engine.analyze(
        "Hello",
        "low",
        0.0,
        {}
    )

    assert (
        engine.should_block_normal_response(result)
        is False
    )


def test_follow_up_allowed():
    engine = SafetyEngine()

    result = engine.analyze(
        "I feel sad",
        "low",
        0.1,
        {
            "sad": True
        }
    )

    assert (
        engine.is_safe_to_continue(result)
        is True
    )