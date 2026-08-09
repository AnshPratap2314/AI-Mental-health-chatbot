from app.behavior_engine import BehaviorEngine
from app.context_state import ContextState


def test_context_initial_state():
    state = ContextState()

    result = state.get_state()

    assert result["current_mood"] is None
    assert result["previous_mood"] is None
    assert result["current_risk"] is None
    assert result["previous_risk"] is None
    assert result["last_topic"] is None
    assert result["previous_topic"] is None
    assert result["message_count"] == 0


def test_context_update():
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


def test_context_previous_state():
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


def test_follow_up_preserves_topic():
    state = ContextState()

    state.update(
        mood="anxious",
        risk_level="moderate",
        topic="college"
    )

    state.record_follow_up(
        mood="anxious",
        risk_level="moderate"
    )

    result = state.get_state()

    assert result["last_topic"] == "college"
    assert result["previous_topic"] is None
    assert result["message_count"] == 2


def test_context_reset():
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


def test_college_context():
    engine = BehaviorEngine()

    result = engine.generate_reply(
        "My college exams are stressing me out"
    )

    assert result["analysis"]["topic"] == "college"
    assert result["analysis"]["mood"] == "anxious"


def test_work_context():
    engine = BehaviorEngine()

    result = engine.generate_reply(
        "My internship interview is stressing me out"
    )

    assert result["analysis"]["topic"] == "work"
    assert result["analysis"]["mood"] == "anxious"


def test_follow_up_keeps_college_context():
    engine = BehaviorEngine()

    engine.generate_reply(
        "My college exams are stressing me out"
    )

    result = engine.generate_reply(
        "Tell me more"
    )

    state = result["analysis"]["state"]

    assert state["last_topic"] == "college"


def test_follow_up_keeps_work_context():
    engine = BehaviorEngine()

    engine.generate_reply(
        "My internship interview is stressing me out"
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


def test_topic_switch():
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


def test_mood_transition():
    engine = BehaviorEngine()

    engine.generate_reply(
        "I feel hopeless"
    )

    result = engine.generate_reply(
        "I am feeling better today"
    )

    state = result["analysis"]["state"]

    assert state["previous_mood"] == "hopeless"
    assert state["current_mood"] == "positive"


def test_crisis_overrides_context():
    engine = BehaviorEngine()

    engine.generate_reply(
        "My college exams are stressing me out"
    )

    result = engine.generate_reply(
        "I want to die"
    )

    assert result["analysis"]["risk_level"] == "high"
    assert result["mode"] == "crisis"
    assert "safety" in result


def test_context_does_not_create_crisis():
    engine = BehaviorEngine()

    engine.generate_reply(
        "I feel hopeless"
    )

    result = engine.generate_reply(
        "Tell me about study techniques"
    )

    assert result["analysis"]["risk_level"] != "high"


def test_negated_crisis():
    engine = BehaviorEngine()

    result = engine.generate_reply(
        "I don't want to die"
    )

    assert result["analysis"]["risk_level"] != "high"


def test_movie_context():
    engine = BehaviorEngine()

    result = engine.generate_reply(
        "I watched a movie about suicide"
    )

    assert result["analysis"]["risk_level"] == "low"
    assert result["analysis"]["signals"]["contextual_suicide"] is True


def test_memory_limit():
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


def test_turn_count():
    engine = BehaviorEngine()

    engine.generate_reply("Hello")
    engine.generate_reply("I feel lonely")
    engine.generate_reply("Tell me more")

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


def test_clear_memory():
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

    state = engine.get_context_state()

    assert state["current_mood"] is None
    assert state["current_risk"] is None
    assert state["last_topic"] is None
    assert state["message_count"] == 0


def test_memory_turn_numbers():
    engine = BehaviorEngine()

    engine.generate_reply("Hello")
    engine.generate_reply("I feel lonely")

    memory = engine.get_memory()

    assert memory[0]["turn"] == 1
    assert memory[1]["turn"] == 2


def test_response_structure():
    engine = BehaviorEngine()

    result = engine.generate_reply(
        "I feel anxious about my exams"
    )

    assert "reply" in result
    assert "response" in result
    assert "mode" in result
    assert "analysis" in result

    assert "risk_level" in result["analysis"]
    assert "risk_score" in result["analysis"]
    assert "mood" in result["analysis"]
    assert "topic" in result["analysis"]
    assert "signals" in result["analysis"]
    assert "context" in result["analysis"]
    assert "state" in result["analysis"]


def test_greeting():
    engine = BehaviorEngine(
        user_name="Ansh"
    )

    result = engine.generate_reply(
        "Hello"
    )

    assert "Ansh" in result["reply"]


def test_positive_mood():
    engine = BehaviorEngine()

    result = engine.generate_reply(
        "I am feeling better today"
    )

    assert result["analysis"]["mood"] == "positive"


def test_sad_mood():
    engine = BehaviorEngine()

    result = engine.generate_reply(
        "I feel lonely"
    )

    assert result["analysis"]["mood"] == "sad"


def test_anxiety_mood():
    engine = BehaviorEngine()

    result = engine.generate_reply(
        "I am very nervous about my interview"
    )

    assert result["analysis"]["mood"] == "anxious"


def test_hopeless_mood():
    engine = BehaviorEngine()

    result = engine.generate_reply(
        "I feel hopeless"
    )

    assert result["analysis"]["mood"] == "hopeless"


def test_support_request():
    engine = BehaviorEngine()

    result = engine.generate_reply(
        "I need help"
    )

    assert result["analysis"]["mode"] in {
        "supportive",
        "anxiety",
        "sad",
        "serious"
    }


def test_context_state_returned():
    engine = BehaviorEngine()

    result = engine.generate_reply(
        "I feel lonely"
    )

    assert "state" in result["analysis"]
    assert result["analysis"]["state"]["message_count"] == 1


def test_multiple_follow_ups():
    engine = BehaviorEngine()

    engine.generate_reply(
        "My internship interview is stressful"
    )

    engine.generate_reply(
        "Tell me more"
    )

    result = engine.generate_reply(
        "What should I do?"
    )

    state = result["analysis"]["state"]

    assert state["last_topic"] == "work"


def test_new_engine_has_clean_state():
    engine = BehaviorEngine()

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