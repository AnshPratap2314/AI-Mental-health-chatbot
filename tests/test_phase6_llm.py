from app.llm_engine import LLMEngine
from app.response_engine import ResponseEngine


def test_llm_engine_exists():
    engine = LLMEngine(
        enabled=False
    )

    assert engine is not None


def test_llm_engine_fallback():
    engine = LLMEngine(
        enabled=False
    )

    result = engine.generate(
        message="I feel lonely",
        analysis={
            "mood": "sad",
            "risk_level": "low",
            "signals": {},
            "state": {
                "last_topic": None
            }
        },
        context={
            "recent_user_messages": []
        }
    )

    assert result["used_llm"] is False
    assert result["source"] == "fallback"
    assert result["text"]


def test_high_risk_never_uses_llm():
    engine = LLMEngine(
        enabled=False
    )

    result = engine.generate(
        message="I want to die",
        analysis={
            "mood": "distressed",
            "risk_level": "high",
            "signals": {
                "crisis": True
            },
            "safety": {
                "risk_level": "high",
                "policy": {
                    "risk_level": "high",
                    "require_safety_response": True
                }
            }
        },
        context={}
    )

    assert result["used_llm"] is False
    assert result["source"] == "fallback"


def test_response_engine_exists():
    engine = ResponseEngine(
        user_name="Ansh"
    )

    assert engine is not None


def test_response_engine_fallback():
    engine = ResponseEngine(
        user_name="Ansh",
        llm_engine=LLMEngine(
            enabled=False
        )
    )

    result = engine.generate(
        message="I feel lonely",
        analysis={
            "mood": "sad",
            "risk_level": "low",
            "signals": {
                "sad": True
            },
            "state": {
                "last_topic": None
            },
            "safety": {
                "risk_level": "low",
                "policy": {
                    "risk_level": "low",
                    "require_safety_response": False
                }
            }
        },
        context={}
    )

    assert result
    assert isinstance(
        result,
        str
    )


def test_crisis_response_has_priority():
    engine = ResponseEngine(
        user_name="Ansh",
        llm_engine=LLMEngine(
            enabled=False
        )
    )

    result = engine.generate(
        message="I want to die",
        analysis={
            "mood": "distressed",
            "risk_level": "high",
            "signals": {
                "crisis": True
            },
            "state": {},
            "safety": {
                "risk_level": "high",
                "policy": {
                    "risk_level": "high",
                    "require_safety_response": True
                }
            }
        },
        context={}
    )

    assert result
    assert (
        "safety" in result.lower()
        or "danger" in result.lower()
        or "support" in result.lower()
    )


def test_context_is_passed_to_llm_fallback():
    engine = LLMEngine(
        enabled=False
    )

    result = engine.generate(
        message="Tell me more",
        analysis={
            "mood": "reflective",
            "risk_level": "low",
            "signals": {},
            "state": {
                "last_topic": "college"
            }
        },
        context={
            "recent_user_messages": [
                "My college exams are stressful"
            ]
        }
    )

    assert result["text"]