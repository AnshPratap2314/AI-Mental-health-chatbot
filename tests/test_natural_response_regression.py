from app.behavior_engine import BehaviorEngine
from app.llm_engine import LLMEngine


def test_fallback_reacts_to_different_emotional_messages():
    engine = BehaviorEngine(llm_engine=LLMEngine(enabled=False))

    lonely = engine.generate_reply("I feel lonely")["reply"]
    sad = engine.generate_reply("hi I am sad")["reply"]

    assert lonely
    assert sad
    assert lonely != sad
    assert "lonely" in lonely.lower() or "alone" in lonely.lower()


def test_conversation_context_contains_previous_assistant_reply():
    engine = BehaviorEngine(llm_engine=LLMEngine(enabled=False))

    first = engine.generate_reply("I am anxious about my internship")["reply"]
    context = engine.get_context()

    assert context["recent_turns"]
    assert context["recent_turns"][-1]["user"] == "I am anxious about my internship"
    assert context["recent_turns"][-1]["assistant"] == first


def test_positive_success_message_is_recognized():
    engine = BehaviorEngine(llm_engine=LLMEngine(enabled=False))

    result = engine.generate_reply("I got selected for an internship")

    assert result["analysis"]["mood"] == "positive"
    assert result["analysis"]["state"]["last_topic"] == "work"


def test_fallback_does_not_repeat_previous_assistant_reply():
    engine = BehaviorEngine(llm_engine=LLMEngine(enabled=False))

    first = engine.generate_reply("I got selected for an internship")["reply"]
    second = engine.generate_reply("Tell me more")["reply"]

    assert first != second


def test_response_metadata_reports_fallback():
    engine = BehaviorEngine(llm_engine=LLMEngine(enabled=False))

    result = engine.generate_reply("I feel lonely")

    assert result["response_source"] == "fallback"
    assert result["response_model"] is None
