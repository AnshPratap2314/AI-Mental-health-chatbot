from app.behavior_engine import BehaviorEngine


def test_basic_conversation_flow():
    engine = BehaviorEngine()

    first = engine.generate_reply("I feel lonely")
    second = engine.generate_reply("I don't know what to do")
    third = engine.generate_reply("Tell me more")

    assert first["reply"]
    assert second["reply"]
    assert third["reply"]

    assert first["analysis"]["risk_level"] == "low"
    assert second["analysis"]["risk_level"] in {"low", "moderate"}


def test_conversation_keeps_memory():
    engine = BehaviorEngine()

    engine.generate_reply("I feel lonely")
    engine.generate_reply("My college exams are stressful")
    result = engine.generate_reply("Tell me more")

    context = result["analysis"]["context"]

    assert context["message_count"] == 2
    assert "I feel lonely" in context["recent_user_messages"]
    assert "My college exams are stressful" in context["recent_user_messages"]


def test_conversation_keeps_latest_topic():
    engine = BehaviorEngine()

    engine.generate_reply("My college exams are stressful")
    engine.generate_reply("My internship interview is stressful")
    result = engine.generate_reply("Tell me more")

    state = result["analysis"]["state"]

    assert state["last_topic"] == "work"
    assert state["previous_topic"] == "college"


def test_follow_up_response_is_contextual():
    engine = BehaviorEngine()

    engine.generate_reply("My college exams are stressing me out")
    result = engine.generate_reply("Tell me more")

    assert result["mode"] == "contextual"
    assert result["reply"]


def test_multiple_follow_ups_remain_contextual():
    engine = BehaviorEngine()

    engine.generate_reply("My college exams are stressing me out")

    result1 = engine.generate_reply("Tell me more")
    result2 = engine.generate_reply("What should I do?")
    result3 = engine.generate_reply("Why is this happening?")

    assert result1["reply"]
    assert result2["reply"]
    assert result3["reply"]

    assert result3["analysis"]["state"]["last_topic"] == "college"


def test_response_changes_when_topic_changes():
    engine = BehaviorEngine()

    first = engine.generate_reply(
        "My college exams are stressing me out"
    )

    second = engine.generate_reply(
        "My internship interview is stressing me out"
    )

    assert first["analysis"]["state"]["last_topic"] == "college"
    assert second["analysis"]["state"]["last_topic"] == "work"

    assert first["reply"] != second["reply"]


def test_mood_transition_changes_response():
    engine = BehaviorEngine()

    first = engine.generate_reply("I feel hopeless")
    second = engine.generate_reply("I'm feeling better today")

    assert first["analysis"]["mood"] == "hopeless"
    assert second["analysis"]["mood"] == "positive"

    assert first["reply"] != second["reply"]


def test_anxiety_conversation_flow():
    engine = BehaviorEngine()

    first = engine.generate_reply(
        "My exams are making me very anxious"
    )

    second = engine.generate_reply(
        "I keep overthinking everything"
    )

    assert first["mode"] == "anxiety"
    assert second["mode"] == "anxiety"
    assert second["reply"]


def test_sad_conversation_flow():
    engine = BehaviorEngine()

    first = engine.generate_reply(
        "I feel very lonely"
    )

    second = engine.generate_reply(
        "I have nobody to talk to"
    )

    assert first["mode"] == "sad"
    assert second["reply"]


def test_support_request_flow():
    engine = BehaviorEngine()

    engine.generate_reply(
        "I am struggling with my internship interview"
    )

    result = engine.generate_reply(
        "What should I do?"
    )

    assert result["reply"]

    state = result["analysis"]["state"]

    assert state["last_topic"] == "work"


def test_crisis_interrupts_normal_conversation():
    engine = BehaviorEngine()

    engine.generate_reply(
        "My college exams are stressing me out"
    )

    result = engine.generate_reply(
        "I want to die"
    )

    assert result["mode"] == "crisis"
    assert result["analysis"]["risk_level"] == "high"
    assert "safety" in result


def test_crisis_remains_high_priority_after_long_context():
    engine = BehaviorEngine()

    engine.generate_reply("My exams are stressful")
    engine.generate_reply("My internship is stressful")
    engine.generate_reply("I feel hopeless")
    engine.generate_reply("I feel lonely")

    result = engine.generate_reply("I want to die")

    assert result["mode"] == "crisis"
    assert result["analysis"]["risk_level"] == "high"
    assert result["safety"]["policy"]["require_safety_response"] is True


def test_normal_message_after_context():
    engine = BehaviorEngine()

    engine.generate_reply(
        "My college exams are stressing me out"
    )

    result = engine.generate_reply(
        "The weather is nice today"
    )

    assert result["reply"]
    assert result["analysis"]["risk_level"] != "high"


def test_empty_message_does_not_break_conversation():
    engine = BehaviorEngine()

    result = engine.generate_reply("")

    assert isinstance(result, dict)
    assert "reply" in result
    assert "analysis" in result


def test_greeting_flow():
    engine = BehaviorEngine(
        user_name="Ansh"
    )

    result = engine.generate_reply("Hello")

    assert result["reply"]
    assert "ansh" in result["reply"].lower()


def test_gratitude_flow():
    engine = BehaviorEngine()

    result = engine.generate_reply(
        "Thank you"
    )

    assert result["reply"]
    assert "welcome" in result["reply"].lower()


def test_duplicate_message_does_not_corrupt_flow():
    engine = BehaviorEngine()

    engine.generate_reply(
        "My college exams are stressful"
    )

    engine.generate_reply(
        "My college exams are stressful"
    )

    result = engine.generate_reply(
        "Tell me more"
    )

    assert result["reply"]
    assert result["analysis"]["state"]["last_topic"] == "college"


def test_conversation_state_matches_turn_count():
    engine = BehaviorEngine()

    engine.generate_reply("Hello")
    engine.generate_reply("I feel lonely")
    result = engine.generate_reply("Tell me more")

    state = result["analysis"]["state"]

    assert state["message_count"] == 3
    assert engine.get_turn_count() == 3


def test_reset_starts_new_conversation():
    engine = BehaviorEngine()

    engine.generate_reply(
        "My college exams are stressful"
    )

    engine.generate_reply(
        "Tell me more"
    )

    engine.clear_memory()

    result = engine.generate_reply(
        "Tell me more"
    )

    state = result["analysis"]["state"]

    assert state["last_topic"] is None
    assert state["previous_topic"] is None
    assert state["message_count"] == 1