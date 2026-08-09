from app.behavior_engine import BehaviorEngine


def test_low_risk():
    engine = BehaviorEngine()

    result = engine.generate_reply("Hello")

    assert result["analysis"]["risk_level"] == "low"


def test_sad_message():
    engine = BehaviorEngine()

    result = engine.generate_reply("I feel lonely")

    assert result["analysis"]["risk_level"] == "low"
    assert result["mode"] == "sad"


def test_moderate_risk():
    engine = BehaviorEngine()

    result = engine.generate_reply("I feel hopeless")

    assert result["analysis"]["risk_level"] == "moderate"
    assert result["mode"] == "serious"


def test_worthless_message():
    engine = BehaviorEngine()

    result = engine.generate_reply("I feel worthless")

    assert result["analysis"]["risk_level"] == "moderate"
    assert result["mode"] == "serious"


def test_cant_handle_message():
    engine = BehaviorEngine()

    result = engine.generate_reply("I can't handle this")

    assert result["analysis"]["risk_level"] == "moderate"
    assert result["mode"] == "serious"


def test_crisis_message():
    engine = BehaviorEngine()

    result = engine.generate_reply("I want to die")

    assert result["analysis"]["risk_level"] == "high"
    assert result["mode"] == "crisis"


def test_crisis_safety_policy():
    engine = BehaviorEngine()

    result = engine.generate_reply("I want to die")

    assert result["safety"]["risk_level"] == "high"
    assert result["safety"]["policy"]["require_safety_response"] is True
    assert result["safety"]["policy"]["allow_random_response"] is False


def test_negated_crisis():
    engine = BehaviorEngine()

    result = engine.generate_reply("I don't want to die")

    assert result["analysis"]["risk_level"] != "high"


def test_negated_self_harm():
    engine = BehaviorEngine()

    result = engine.generate_reply(
        "I don't want to hurt myself"
    )

    assert result["analysis"]["risk_level"] != "high"


def test_movie_context():
    engine = BehaviorEngine()

    result = engine.generate_reply(
        "I watched a movie about suicide"
    )

    assert result["analysis"]["risk_level"] != "high"


def test_news_context():
    engine = BehaviorEngine()

    result = engine.generate_reply(
        "I read a news article about suicide"
    )

    assert result["analysis"]["risk_level"] != "high"


def test_future_protective_context():
    engine = BehaviorEngine()

    result = engine.generate_reply(
        "I want to live for my family"
    )

    assert result["analysis"]["risk_level"] != "high"


def test_crisis_with_temporal_signal():
    engine = BehaviorEngine()

    result = engine.generate_reply(
        "I want to die tonight"
    )

    assert result["analysis"]["risk_level"] == "high"


def test_intent_signal():
    engine = BehaviorEngine()

    result = engine.generate_reply(
        "I might do it"
    )

    assert result["analysis"]["risk_level"] in [
        "moderate",
        "high"
    ]


def test_signals_are_returned():
    engine = BehaviorEngine()

    result = engine.generate_reply(
        "I feel hopeless"
    )

    signals = result["analysis"]["signals"]

    assert "crisis" in signals
    assert "serious" in signals
    assert "sad" in signals
    assert "intent" in signals
    assert "temporal" in signals
    assert "protective" in signals
    assert "negated" in signals


def test_context_empty_conversation():
    engine = BehaviorEngine()

    result = engine.generate_reply(
        "Hello"
    )

    context = result["analysis"]["context"]

    assert context["message_count"] == 0
    assert context["has_previous_context"] is False


def test_context_after_message():
    engine = BehaviorEngine()

    engine.generate_reply(
        "I feel lonely"
    )

    result = engine.generate_reply(
        "Tell me more"
    )

    context = result["analysis"]["context"]

    assert context["message_count"] == 1
    assert context["has_previous_context"] is True


def test_context_contains_previous_message():
    engine = BehaviorEngine()

    engine.generate_reply(
        "I feel hopeless"
    )

    result = engine.generate_reply(
        "I don't know what to do"
    )

    messages = result["analysis"]["context"][
        "recent_user_messages"
    ]

    assert "I feel hopeless" in messages
def test_context_risk_boost():

    engine = BehaviorEngine()

    engine.generate_reply(
        "I feel hopeless"
    )

    result = engine.generate_reply(
        "I don't know what to do"
    )

    assert result["analysis"]["context_risk_boost"] > 0


def test_context_does_not_create_crisis():

    engine = BehaviorEngine()

    engine.generate_reply(
        "I watched a movie about suicide"
    )

    result = engine.generate_reply(
        "The movie was very sad"
    )

    assert result["analysis"]["risk_level"] != "high"


def test_context_is_returned():

    engine = BehaviorEngine()

    engine.generate_reply(
        "I feel hopeless"
    )

    result = engine.generate_reply(
        "Tell me more"
    )

    assert "context" in result["analysis"]

    assert "context_risk_boost" in result["analysis"]
def test_context_empty_conversation():

    engine = BehaviorEngine()

    result = engine.generate_reply(
        "Hello"
    )

    context = result["analysis"]["context"]

    assert context["message_count"] == 0
    assert context["has_previous_context"] is False


def test_context_after_message():

    engine = BehaviorEngine()

    engine.generate_reply(
        "I feel lonely"
    )

    result = engine.generate_reply(
        "Tell me more"
    )

    context = result["analysis"]["context"]

    assert context["message_count"] == 1
    assert context["has_previous_context"] is True


def test_context_contains_previous_message():

    engine = BehaviorEngine()

    engine.generate_reply(
        "I feel hopeless"
    )

    result = engine.generate_reply(
        "I don't know what to do"
    )

    messages = result["analysis"]["context"][
        "recent_user_messages"
    ]

    assert "I feel hopeless" in messages


def test_duplicate_message_not_stored_twice():

    engine = BehaviorEngine()

    first = engine.generate_reply(
        "I feel lonely"
    )

    second = engine.generate_reply(
        "I feel lonely"
    )

    messages = second["analysis"]["context"][
        "recent_user_messages"
    ]

    assert messages.count("I feel lonely") == 1


def test_new_engine_has_new_memory():

    engine_one = BehaviorEngine()

    engine_one.generate_reply(
        "I feel lonely"
    )

    engine_two = BehaviorEngine()

    result = engine_two.generate_reply(
        "Hello"
    )

    context = result["analysis"]["context"]

    assert context["message_count"] == 0
    assert context["has_previous_context"] is False