from app.behavior_engine import BehaviorEngine
from app.response_engine import ResponseEngine


def test_response_engine_exists():
    engine = ResponseEngine()

    assert engine is not None


def test_response_engine_uses_user_name():
    engine = BehaviorEngine(
        user_name="Ansh"
    )

    result = engine.generate_reply(
        "hello"
    )

    assert "Ansh" in result["reply"]


def test_response_engine_handles_positive_mood():
    engine = BehaviorEngine()

    result = engine.generate_reply(
        "I am feeling great today"
    )

    assert result["analysis"]["mood"] == "positive"
    assert len(result["reply"]) > 0


def test_response_engine_handles_sad_mood():
    engine = BehaviorEngine()

    result = engine.generate_reply(
        "I feel lonely"
    )

    assert result["analysis"]["mood"] == "sad"
    assert len(result["reply"]) > 0


def test_response_engine_handles_anxiety():
    engine = BehaviorEngine()

    result = engine.generate_reply(
        "I am very anxious about my exams"
    )

    assert result["analysis"]["mood"] == "anxious"
    assert len(result["reply"]) > 0


def test_response_engine_uses_college_topic():
    engine = BehaviorEngine()

    result = engine.generate_reply(
        "My college exams are stressing me out"
    )

    assert result["analysis"]["topic"] == "college"


def test_response_engine_uses_work_topic():
    engine = BehaviorEngine()

    result = engine.generate_reply(
        "My internship interview is tomorrow"
    )

    assert result["analysis"]["topic"] == "work"


def test_follow_up_preserves_topic():
    engine = BehaviorEngine()

    engine.generate_reply(
        "My college exams are stressing me out"
    )

    result = engine.generate_reply(
        "Tell me more"
    )

    assert result["analysis"]["state"]["last_topic"] == "college"


def test_topic_switch():
    engine = BehaviorEngine()

    engine.generate_reply(
        "My college exams are stressing me out"
    )

    result = engine.generate_reply(
        "My internship interview is tomorrow"
    )

    state = result["analysis"]["state"]

    assert state["last_topic"] == "work"
    assert state["previous_topic"] == "college"


def test_crisis_response_has_priority():
    engine = BehaviorEngine()

    result = engine.generate_reply(
        "I want to die"
    )

    assert result["analysis"]["risk_level"] == "high"
    assert result["mode"] == "crisis"
    assert "safety" in result


def test_contextual_suicide_is_not_crisis():
    engine = BehaviorEngine()

    result = engine.generate_reply(
        "I watched a movie about suicide"
    )

    assert result["analysis"]["risk_level"] == "low"
    assert result["analysis"]["signals"]["contextual_suicide"] is True


def test_response_structure():
    engine = BehaviorEngine()

    result = engine.generate_reply(
        "I feel stressed"
    )

    assert "reply" in result
    assert "response" in result
    assert "mode" in result
    assert "analysis" in result
    assert "risk_level" in result["analysis"]
    assert "mood" in result["analysis"]
    assert "topic" in result["analysis"]
    assert "state" in result["analysis"]


def test_multiple_follow_ups():
    engine = BehaviorEngine()

    engine.generate_reply(
        "My internship interview is stressing me out"
    )

    engine.generate_reply(
        "Tell me more"
    )

    result = engine.generate_reply(
        "What should I do?"
    )

    state = result["analysis"]["state"]

    assert state["last_topic"] == "work"


def test_clear_memory_resets_response_context():
    engine = BehaviorEngine()

    engine.generate_reply(
        "My college exams are stressful"
    )

    engine.clear_memory()

    state = engine.get_context_state()

    assert state["last_topic"] is None
    assert state["current_mood"] is None
    assert state["message_count"] == 0