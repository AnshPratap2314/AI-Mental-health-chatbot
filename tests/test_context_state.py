from app.behavior_engine import BehaviorEngine
from app.context_state import ContextState


def test_initial_state():
    state = ContextState()

    result = state.get_state()

    assert result["current_mood"] is None
    assert result["previous_mood"] is None
    assert result["current_risk"] is None
    assert result["previous_risk"] is None
    assert result["last_topic"] is None
    assert result["previous_topic"] is None
    assert result["message_count"] == 0


def test_state_update():
    state = ContextState()

    state.update(
        mood="sad",
        risk_level="low",
        topic="college"
    )

    result = state.get_state()

    assert result["current_mood"] == "sad"
    assert result["current_risk"] == "low"
    assert result["last_topic"] == "college"
    assert result["message_count"] == 1


def test_previous_state():
    state = ContextState()

    state.update(
        mood="sad",
        risk_level="low",
        topic="college"
    )

    state.update(
        mood="anxious",
        risk_level="moderate",
        topic="work"
    )

    result = state.get_state()

    assert result["current_mood"] == "anxious"
    assert result["previous_mood"] == "sad"
    assert result["current_risk"] == "moderate"
    assert result["previous_risk"] == "low"
    assert result["last_topic"] == "work"
    assert result["previous_topic"] == "college"
    assert result["message_count"] == 2


def test_reset():
    state = ContextState()

    state.update(
        mood="sad",
        risk_level="moderate",
        topic="college"
    )

    state.reset()

    result = state.get_state()

    assert result["current_mood"] is None
    assert result["previous_mood"] is None
    assert result["current_risk"] is None
    assert result["previous_risk"] is None
    assert result["last_topic"] is None
    assert result["previous_topic"] is None
    assert result["message_count"] == 0


def test_topic_persists_across_turns():
    engine = BehaviorEngine()

    engine.generate_reply(
        "My college exams are stressing me out"
    )

    result = engine.generate_reply(
        "Tell me more"
    )

    state = result["analysis"]["state"]

    assert state["last_topic"] == "college"


def test_mood_persists_across_turns():
    engine = BehaviorEngine()

    engine.generate_reply(
        "I feel hopeless"
    )

    result = engine.generate_reply(
        "I don't know what to do"
    )

    state = result["analysis"]["state"]

    assert state["previous_mood"] == "hopeless"


def test_context_state_is_returned():
    engine = BehaviorEngine()

    result = engine.generate_reply(
        "I feel lonely"
    )

    assert "state" in result["analysis"]


def test_follow_up_uses_previous_topic():
    engine = BehaviorEngine()

    engine.generate_reply(
        "My internship interview is stressing me out"
    )

    result = engine.generate_reply(
        "What should I do?"
    )

    reply = result["reply"].lower()

    assert (
        "work" in reply
        or "career" in reply
        or "interview" in reply
        or "internship" in reply
    )


def test_context_reset():
    engine = BehaviorEngine()

    engine.generate_reply(
        "My exams are stressing me out"
    )

    engine.clear_memory()

    state = engine.get_context_state()

    assert state["last_topic"] is None
    assert state["current_mood"] is None
    assert state["current_risk"] is None
    assert state["message_count"] == 0


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


def test_follow_up_after_topic_switch():
    engine = BehaviorEngine()

    engine.generate_reply(
        "My college exams are stressing me out"
    )

    engine.generate_reply(
        "My internship interview is stressing me out"
    )

    result = engine.generate_reply(
        "What should I do?"
    )

    reply = result["reply"].lower()

    assert (
        "work" in reply
        or "career" in reply
        or "interview" in reply
        or "internship" in reply
    )


def test_mood_changes_across_turns():
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


def test_context_does_not_override_current_topic():
    engine = BehaviorEngine()

    engine.generate_reply(
        "My exams are stressing me out"
    )

    result = engine.generate_reply(
        "My internship interview is stressing me out"
    )

    state = result["analysis"]["state"]

    assert state["last_topic"] == "work"
    assert state["previous_topic"] == "college"


def test_context_does_not_create_crisis():
    engine = BehaviorEngine()

    engine.generate_reply(
        "I feel hopeless"
    )

    result = engine.generate_reply(
        "Tell me about study techniques"
    )

    assert result["analysis"]["risk_level"] != "high"


def test_crisis_overrides_context():
    engine = BehaviorEngine()

    engine.generate_reply(
        "My exams are stressing me out"
    )

    result = engine.generate_reply(
        "I want to die"
    )

    assert result["analysis"]["risk_level"] == "high"
    assert result["mode"] == "crisis"


def test_memory_window_limit():
    engine = BehaviorEngine(
        max_memory=3
    )

    engine.generate_reply(
        "I feel lonely"
    )

    engine.generate_reply(
        "My exams are stressful"
    )

    engine.generate_reply(
        "I am worried about my internship"
    )

    engine.generate_reply(
        "I am thinking about my future"
    )

    memory = engine.get_memory()

    assert len(memory) == 3
    assert memory[0]["message"] == "My exams are stressful"
    assert memory[-1]["message"] == "I am thinking about my future"


def test_turn_count_increases():
    engine = BehaviorEngine()

    engine.generate_reply(
        "Hello"
    )

    engine.generate_reply(
        "I feel lonely"
    )

    engine.generate_reply(
        "Tell me more"
    )

    assert engine.get_turn_count() == 3


def test_duplicate_does_not_increase_turn_count():
    engine = BehaviorEngine()

    engine.generate_reply(
        "I feel lonely"
    )

    engine.generate_reply(
        "I feel lonely"
    )

    assert engine.get_turn_count() == 1


def test_reset_clears_memory_and_turn_count():
    engine = BehaviorEngine()

    engine.generate_reply(
        "I feel lonely"
    )

    engine.generate_reply(
        "My exams are stressful"
    )

    engine.clear_memory()

    assert engine.get_memory() == []
    assert engine.get_turn_count() == 0
    assert engine.get_context()["message_count"] == 0


def test_current_topic_survives_multiple_turns():
    engine = BehaviorEngine()

    engine.generate_reply(
        "My internship interview is stressing me out"
    )

    engine.generate_reply(
        "I am really nervous"
    )

    result = engine.generate_reply(
        "What should I do?"
    )

    state = result["analysis"]["state"]

    assert state["last_topic"] == "work"


def test_previous_topic_is_preserved():
    engine = BehaviorEngine()

    engine.generate_reply(
        "My college exams are stressful"
    )

    engine.generate_reply(
        "My internship interview is stressful"
    )

    result = engine.generate_reply(
        "I am worried about tomorrow"
    )

    state = result["analysis"]["state"]

    assert state["last_topic"] == "future"
    assert state["previous_topic"] == "work"


def test_memory_returns_turn_numbers():
    engine = BehaviorEngine()

    engine.generate_reply(
        "Hello"
    )

    engine.generate_reply(
        "I feel lonely"
    )

    memory = engine.get_memory()

    assert memory[0]["turn"] == 1
    assert memory[1]["turn"] == 2
def test_follow_up_references_previous_topic():
    engine = BehaviorEngine()

    engine.generate_reply(
        "My college exams are stressing me out"
    )

    result = engine.generate_reply(
        "Tell me more"
    )

    reply = result["reply"].lower()

    assert (
        "exam" in reply
        or "college" in reply
        or "study" in reply
    )


def test_follow_up_references_previous_message():
    engine = BehaviorEngine()

    engine.generate_reply(
        "My internship interview is stressing me out"
    )

    result = engine.generate_reply(
        "Tell me more"
    )

    reply = result["reply"].lower()

    assert (
        "internship" in reply
        or "interview" in reply
        or "work" in reply
        or "career" in reply
    )


def test_context_response_uses_current_topic():
    engine = BehaviorEngine()

    engine.generate_reply(
        "My exams are stressing me out"
    )

    result = engine.generate_reply(
        "What should I do?"
    )

    reply = result["reply"].lower()

    assert (
        "exam" in reply
        or "college" in reply
        or "study" in reply
    )


def test_context_response_uses_latest_topic_after_switch():
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

    reply = result["reply"].lower()

    assert (
        "internship" in reply
        or "interview" in reply
        or "work" in reply
        or "career" in reply
    )


def test_context_does_not_override_crisis_response():
    engine = BehaviorEngine()

    engine.generate_reply(
        "My college exams are stressing me out"
    )

    result = engine.generate_reply(
        "I want to die"
    )

    assert result["analysis"]["risk_level"] == "high"
    assert result["mode"] == "crisis"

    reply = result["reply"].lower()

    assert (
        "safety" in reply
        or "support" in reply
        or "immediate" in reply
    )


def test_context_state_contains_topic_and_mood():
    engine = BehaviorEngine()

    result = engine.generate_reply(
        "My internship interview is stressing me out"
    )

    state = result["analysis"]["state"]

    assert state["last_topic"] == "work"
    assert state["current_mood"] == "anxious"
def test_multi_topic_conversation():
    engine = BehaviorEngine()

    engine.generate_reply(
        "My college exams are stressing me out"
    )

    engine.generate_reply(
        "My internship interview is also worrying me"
    )

    result = engine.generate_reply(
        "Tell me more"
    )

    state = result["analysis"]["state"]

    assert state["last_topic"] == "work"
    assert state["previous_topic"] == "college"


def test_latest_topic_has_priority():
    engine = BehaviorEngine()

    engine.generate_reply(
        "My exams are stressful"
    )

    engine.generate_reply(
        "My internship interview is stressful"
    )

    result = engine.generate_reply(
        "What should I do?"
    )

    reply = result["reply"].lower()

    assert (
        "internship" in reply
        or "interview" in reply
        or "work" in reply
        or "career" in reply
    )


def test_mood_transition_over_multiple_turns():
    engine = BehaviorEngine()

    engine.generate_reply(
        "I feel hopeless"
    )

    engine.generate_reply(
        "I'm very anxious"
    )

    result = engine.generate_reply(
        "I'm feeling better today"
    )

    state = result["analysis"]["state"]

    assert state["current_mood"] == "positive"
    assert state["previous_mood"] == "anxious"


def test_risk_transition_over_multiple_turns():
    engine = BehaviorEngine()

    engine.generate_reply(
        "I feel hopeless"
    )

    result = engine.generate_reply(
        "I want to die"
    )

    assert result["analysis"]["risk_level"] == "high"
    assert result["mode"] == "crisis"


def test_context_survives_multiple_turns():
    engine = BehaviorEngine()

    engine.generate_reply(
        "My college exams are stressful"
    )

    engine.generate_reply(
        "I am studying every day"
    )

    engine.generate_reply(
        "I am also worried about my internship"
    )

    engine.generate_reply(
        "The interview is next week"
    )

    result = engine.generate_reply(
        "Tell me more"
    )

    state = result["analysis"]["state"]

    assert state["last_topic"] == "work"
    assert state["message_count"] >= 4


def test_crisis_overrides_long_context():
    engine = BehaviorEngine()

    engine.generate_reply(
        "My exams are stressful"
    )

    engine.generate_reply(
        "My internship is worrying me"
    )

    engine.generate_reply(
        "I feel exhausted"
    )

    engine.generate_reply(
        "I don't know what to do"
    )

    result = engine.generate_reply(
        "I want to die"
    )

    assert result["analysis"]["risk_level"] == "high"
    assert result["mode"] == "crisis"


def test_context_reset_removes_previous_topics():
    engine = BehaviorEngine()

    engine.generate_reply(
        "My college exams are stressful"
    )

    engine.generate_reply(
        "My internship is stressful"
    )

    engine.clear_memory()

    result = engine.generate_reply(
        "Tell me more"
    )

    state = result["analysis"]["state"]

    assert state["last_topic"] is None
    assert state["previous_topic"] is None
    assert state["message_count"] == 1    