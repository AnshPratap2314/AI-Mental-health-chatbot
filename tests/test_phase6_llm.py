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

class _FakeResponse:
    def __init__(self, text):
        self.output_text = text


class _FakeResponses:
    def __init__(self, text):
        self.text = text
        self.last_instructions = ""
        self.last_input = ""

    def create(self, *, model, instructions, input):
        self.last_instructions = instructions
        self.last_input = input
        return _FakeResponse(self.text)


class _FakeClient:
    def __init__(self, text):
        self.responses = _FakeResponses(text)


def test_llm_uses_current_mood_and_mood_trend():
    engine = LLMEngine(enabled=False)
    engine.enabled = True
    engine._client = _FakeClient(
        "That sounds really heavy. You don't have to solve everything at once."
    )

    analysis = {
        "mood": "sad",
        "risk_level": "moderate",
        "mode": "sad",
        "risk_score": 0.25,
        "mood_intensity": "moderate",
        "signals": {"sad": True, "serious": True},
        "state": {
            "current_mood": "sad",
            "previous_mood": "anxious",
            "last_topic": "college",
            "previous_topic": "college",
        },
    }
    context = {
        "recent_user_messages": [
            "I am getting anxious about exams",
            "Now I just feel really sad about everything",
        ],
        "user_profile": {
            "preferred_tone": "supportive",
            "preferred_language": "en",
            "mood_history": ["anxious", "sad"],
        },
    }

    result = engine.generate("Now I just feel really sad about everything", analysis, context)

    assert result["used_llm"] is True
    prompt = engine._client.responses.last_input
    assert "Current mood: sad" in prompt
    assert "Previous mood: anxious" in prompt
    assert "anxious -> sad" in prompt
    assert "college" in prompt
    assert "Lead with empathy" in prompt


def test_moderate_risk_can_use_llm_but_high_risk_cannot():
    engine = LLMEngine(enabled=False)
    engine.enabled = True
    engine._client = _FakeClient("Let's slow this down and look at one thing at a time.")

    moderate = engine.generate(
        "I feel overwhelmed and hopeless about my exams",
        {
            "mood": "hopeless",
            "risk_level": "moderate",
            "signals": {"hopelessness": True},
            "state": {"current_mood": "hopeless"},
        },
        {},
    )
    assert moderate["used_llm"] is True

    high = engine.generate(
        "I want to die tonight",
        {
            "mood": "distressed",
            "risk_level": "high",
            "signals": {"crisis": True, "temporal": True},
            "crisis": {"immediate_guidance": True},
            "state": {"current_mood": "distressed"},
        },
        {},
    )
    assert high["used_llm"] is False
    assert high["source"] == "fallback"


def test_behavior_engine_passes_mood_metadata_to_llm():
    from app.behavior_engine import BehaviorEngine

    class FakeLLM:
        def __init__(self):
            self.analysis = None

        def generate(self, message, analysis, context):
            self.analysis = analysis
            return {
                "text": "I hear you. Let's take this one step at a time.",
                "used_llm": True,
                "source": "llm",
            }

    llm = FakeLLM()
    engine = BehaviorEngine(user_name="friend", llm_engine=llm)
    result = engine.generate_reply("I feel anxious about my exams")

    assert result["analysis"]["mood"] == "anxious"
    assert result["analysis"]["mood_intensity"] in {"moderate", "high"}
    assert llm.analysis["mood"] == "anxious"
    assert llm.analysis["state"]["current_mood"] == "anxious"
