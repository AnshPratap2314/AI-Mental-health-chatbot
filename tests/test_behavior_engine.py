from app.behavior_engine import BehaviorEngine


def test_empty_message():
    engine = BehaviorEngine()

    result = engine.generate_reply("")

    assert "reply" in result
    assert "analysis" in result
    assert result["analysis"]["risk_level"] == "low"


def test_whitespace_message():
    engine = BehaviorEngine()

    result = engine.generate_reply("   ")

    assert "reply" in result
    assert result["analysis"]["risk_level"] == "low"


def test_greeting_response():
    engine = BehaviorEngine(user_name="Ansh")

    result = engine.generate_reply("Hello")

    assert result["reply"]
    assert "Ansh" in result["reply"]


def test_gratitude_response():
    engine = BehaviorEngine()

    result = engine.generate_reply("Thank you")

    assert result["reply"]
    assert "welcome" in result["reply"].lower()


def test_topic_change_updates_state():
    engine = BehaviorEngine()

    engine.generate_reply(
        "My college exams are stressful"
    )

    result = engine.generate_reply(
        "My internship interview is stressful"
    )

    state = result["analysis"]["state"]

    assert state["last_topic"] == "work"
    assert state["previous_topic"] == "college"


def test_follow_up_preserves_topic():
    engine = BehaviorEngine()

    engine.generate_reply(
        "My college exams are stressing me out"
    )

    result = engine.generate_reply(
        "Tell me more"
    )

    state = result["analysis"]["state"]

    assert state["last_topic"] == "college"
    assert "college" in result["reply"].lower()


def test_multiple_follow_ups_preserve_topic():
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

    reply = result["reply"].lower()

    assert (
        "work" in reply
        or "career" in reply
        or "internship" in reply
        or "interview" in reply
    )


def test_context_does_not_create_crisis():
    engine = BehaviorEngine()

    engine.generate_reply(
        "I feel hopeless"
    )

    result = engine.generate_reply(
        "Tell me about study techniques"
    )

    assert result["analysis"]["risk_level"] != "high"


def test_crisis_overrides_previous_topic():
    engine = BehaviorEngine()

    engine.generate_reply(
        "My exams are stressful"
    )

    result = engine.generate_reply(
        "I want to die"
    )

    assert result["analysis"]["risk_level"] == "high"
    assert result["mode"] == "crisis"
    assert result["safety"]["policy"]["require_safety_response"] is True
    assert result["safety"]["policy"]["allow_random_response"] is False
    assert result["safety"]["policy"]["allow_normal_response"] is False


def test_negated_crisis_remains_non_crisis():
    engine = BehaviorEngine()

    result = engine.generate_reply(
        "I don't want to die"
    )

    assert result["analysis"]["risk_level"] != "high"


def test_contextual_suicide_remains_low_risk():
    engine = BehaviorEngine()

    result = engine.generate_reply(
        "I watched a movie about suicide"
    )

    assert result["analysis"]["risk_level"] == "low"


def test_response_structure():
    engine = BehaviorEngine()

    result = engine.generate_reply(
        "I feel lonely"
    )

    assert "reply" in result
    assert "response" in result
    assert "mode" in result
    assert "analysis" in result

    analysis = result["analysis"]

    assert "message" in analysis
    assert "risk_level" in analysis
    assert "risk_score" in analysis
    assert "context_risk_boost" in analysis
    assert "mood" in analysis
    assert "mode" in analysis
    assert "signals" in analysis
    assert "context" in analysis
    assert "state" in analysis


def test_memory_and_state_stay_consistent():
    engine = BehaviorEngine()

    engine.generate_reply(
        "My exams are stressful"
    )

    engine.generate_reply(
        "I am nervous"
    )

    result = engine.generate_reply(
        "Tell me more"
    )

    assert result["analysis"]["state"]["message_count"] == 3
    assert result["analysis"]["context"]["message_count"] == 2
    assert engine.get_turn_count() == 3


def test_duplicate_message_does_not_break_state():
    engine = BehaviorEngine()

    engine.generate_reply(
        "I feel lonely"
    )

    engine.generate_reply(
        "I feel lonely"
    )

    state = engine.get_context_state()

    assert state["message_count"] == 2
    assert engine.get_turn_count() == 1


def test_topic_switch_then_follow_up():
    engine = BehaviorEngine()

    engine.generate_reply(
        "My college exams are stressful"
    )

    engine.generate_reply(
        "My internship interview is stressful"
    )

    result = engine.generate_reply(
        "Tell me more"
    )

    state = result["analysis"]["state"]

    assert state["last_topic"] == "work"
    assert state["previous_topic"] == "college"

    reply = result["reply"].lower()

    assert (
        "work" in reply
        or "career" in reply
        or "internship" in reply
        or "interview" in reply
    )


def test_mood_transition():
    engine = BehaviorEngine()

    engine.generate_reply(
        "I feel hopeless"
    )

    result = engine.generate_reply(
        "I'm feeling better today"
    )

    state = result["analysis"]["state"]

    assert state["previous_mood"] == "hopeless"
    assert state["current_mood"] == "positive"


def test_risk_transition():
    engine = BehaviorEngine()

    engine.generate_reply(
        "I feel hopeless"
    )

    result = engine.generate_reply(
        "I want to die"
    )

    state = result["analysis"]["state"]

    assert state["previous_risk"] in {
        "low",
        "moderate"
    }

    assert state["current_risk"] == "high"


def test_clear_memory_resets_state():
    engine = BehaviorEngine()

    engine.generate_reply(
        "My internship interview is stressful"
    )

    engine.clear_memory()

    assert engine.get_memory() == []
    assert engine.get_turn_count() == 0

    state = engine.get_context_state()

    assert state["current_mood"] is None
    assert state["previous_mood"] is None
    assert state["current_risk"] is None
    assert state["previous_risk"] is None
    assert state["last_topic"] is None
    assert state["previous_topic"] is None
    assert state["message_count"] == 0


def test_new_engine_has_clean_state():
    engine = BehaviorEngine()

    assert engine.get_memory() == []
    assert engine.get_turn_count() == 0

    state = engine.get_context_state()

    assert state["current_mood"] is None
    assert state["current_risk"] is None
    assert state["last_topic"] is None
    assert state["message_count"] == 0