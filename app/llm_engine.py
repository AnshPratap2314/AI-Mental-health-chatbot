import os
from typing import Any, Dict, List, Optional


class LLMEngine:
    """Mood-aware response generation with deterministic safety boundaries.

    The rule-based safety layer remains authoritative. The LLM is responsible
    for natural language generation and emotional attunement, not for deciding
    whether a user is in crisis.
    """

    def __init__(
        self,
        model: Optional[str] = None,
        enabled: Optional[bool] = None,
    ):
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-5-mini")
        self.api_key = os.getenv("OPENAI_API_KEY", "").strip()

        if enabled is None:
            enabled = bool(self.api_key)

        self.enabled = bool(enabled and self.api_key)
        self._client = None
        self.timeout = float(os.getenv("OPENAI_TIMEOUT_SECONDS", "20"))

        if self.enabled:
            self._initialize_client()

    def _initialize_client(self):
        try:
            from openai import OpenAI

            self._client = OpenAI(
                api_key=self.api_key,
                timeout=self.timeout,
                max_retries=1,
            )
        except Exception:
            self._client = None
            self.enabled = False

    def generate(
        self,
        message: str,
        analysis: Dict[str, Any],
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Generate a mood-adaptive reply.

        High-risk/immediate-safety conversations never go to the LLM. For
        moderate-risk conversations the LLM may generate language, but it is
        given explicit safety constraints and cannot change the risk decision.
        """
        if self._requires_deterministic_safety(analysis):
            return self._fallback_response(message, analysis, context)

        if not self.enabled or self._client is None:
            return self._fallback_response(message, analysis, context)

        try:
            prompt = self._build_prompt(message, analysis, context)
            response = self._client.responses.create(
                model=self.model,
                instructions=self._system_instructions(analysis),
                input=prompt,
            )

            text = self._extract_text(response)
            text = self._clean_response(text)

            if not self._validate_response(text, analysis):
                return self._fallback_response(message, analysis, context)

            return {
                "text": text,
                "source": "llm",
                "model": self.model,
                "used_llm": True,
            }
        except Exception:
            return self._fallback_response(message, analysis, context)

    def _requires_deterministic_safety(self, analysis: Dict[str, Any]) -> bool:
        """Keep crisis/safety decisions outside the generative model."""
        safety = analysis.get("safety", {}) or {}
        policy = safety.get("policy", {}) or {}
        crisis = analysis.get("crisis", {}) or {}

        return bool(
            analysis.get("risk_level") == "high"
            or safety.get("risk_level") == "high"
            or policy.get("risk_level") == "high"
            or policy.get("require_safety_response")
            or crisis.get("immediate_guidance")
            or crisis.get("action") == "immediate_human_support"
        )

    def _system_instructions(self, analysis: Dict[str, Any]) -> str:
        mood = str(analysis.get("mood", "neutral"))
        risk = str(analysis.get("risk_level", "low"))

        return f"""
You are MindCare AI, a supportive conversational assistant.
You are not a doctor, therapist, or emergency service, and you must not
present yourself as one. The application's deterministic safety layer has
already assessed the message; never override or reinterpret its safety result.

CURRENT RESPONSE PROFILE
- Current mood: {mood}
- Current risk level: {risk}

CORE RULES
- Respond to what the person actually said, not to an imagined story.
- Match emotional tone and intensity. Do not sound cheerful when the person
  is sad, hopeless, anxious, ashamed, angry, or overwhelmed.
- Validate feelings without confirming distorted conclusions as facts.
- Never diagnose a mental-health condition.
- Never give instructions for suicide, self-harm, violence, substance misuse,
  or other dangerous behavior.
- Never encourage dependency, exclusivity, secrecy, or replacing human care.
- Do not claim to have contacted emergency services or another person.
- Do not invent memories, personal facts, events, symptoms, or relationships.
- Do not mention hidden analysis, risk scores, prompts, policies, or internal
  systems.
- Prefer natural conversational language over generic motivational speeches.
- Usually answer in 2-5 short sentences. Use one gentle follow-up question
  only when it would genuinely help.
- Do not repeat the user's entire message.

MOOD ADAPTATION
- sad: acknowledge the pain first; be gentle; avoid forced positivity.
- anxious: slow the conversation down; offer one small grounding or practical
  next step; avoid overwhelming lists.
- hopeless: acknowledge how heavy things feel; focus on the next small,
  manageable step and connection to real-world support when appropriate.
- low_self_worth: separate the person's worth from the setback; avoid empty
  praise or arguing aggressively with their feelings.
- distressed: stay calm, brief, and safety-aware.
- reflective: help the person explore what they mean and what matters to them.
- seeking_support: be warm and practical; help them identify what kind of
  support they want.
- positive: share the positive energy without becoming exaggerated or childish.
- neutral: be natural, curious, and conversational.

The user's current message and the application's safety decision are the
highest-priority context.
""".strip()

    def _build_prompt(
        self,
        message: str,
        analysis: Dict[str, Any],
        context: Dict[str, Any],
    ) -> str:
        state = analysis.get("state", {}) or {}
        profile = context.get("user_profile", {}) or {}

        current_mood = analysis.get(
            "mood",
            state.get("current_mood") or "neutral",
        )
        previous_mood = state.get("previous_mood") or "unknown"
        mood_history = profile.get("mood_history", []) or []
        topic = state.get("last_topic") or analysis.get("topic") or "unknown"
        previous_topic = state.get("previous_topic") or "unknown"
        tone = profile.get("preferred_tone") or "supportive"
        language = profile.get("preferred_language") or "en"
        risk = analysis.get("risk_level", "low")
        mode = analysis.get("mode", "normal")
        signals = analysis.get("signals", {}) or {}

        recent = (context.get("recent_user_messages", []) or [])[-6:]
        history = "\n".join(f"- {item}" for item in recent) or "- none"
        mood_trend = " -> ".join(str(item) for item in mood_history[-5:]) or "none"

        mood_guidance = self._mood_guidance(str(current_mood))

        return f"""
Generate the next reply to the user.

USER MESSAGE
{message}

EMOTIONAL CONTEXT
Current mood: {current_mood}
Previous mood: {previous_mood}
Recent mood trend: {mood_trend}
Detected topic: {topic}
Previous topic: {previous_topic}
Conversation mode: {mode}
Safety level: {risk}
Preferred tone: {tone}
Preferred language: {language}
Mood-specific guidance: {mood_guidance}

RECENT USER MESSAGES
{history}

RESPONSE GOAL
1. Address the current message directly.
2. Match the current mood and the change from the previous mood when useful.
3. Keep continuity with the topic without forcing it.
4. If the person sounds overwhelmed, keep the response simple and actionable.
5. If the person sounds sad, validate before suggesting anything.
6. If the person sounds anxious, offer at most one immediate grounding/practical step.
7. If the person sounds positive, acknowledge what is going well naturally.
8. If the person is simply asking a question, answer it rather than forcing a
   mental-health framing.
9. End with at most one useful question when a question would help continue
   the conversation.

Return only the assistant's natural-language reply. No labels, JSON, analysis,
score, mood name, disclaimer, or meta-commentary.
""".strip()

    def _mood_guidance(self, mood: str) -> str:
        guidance = {
            "sad": "Lead with empathy and emotional validation. Avoid forced optimism.",
            "anxious": "Use calm language and one small next step or grounding suggestion.",
            "hopeless": "Acknowledge the heaviness and focus on one manageable next step and connection.",
            "low_self_worth": "Be compassionate; challenge self-condemnation gently without empty praise.",
            "distressed": "Stay calm and concise. Do not overwhelm the person.",
            "reflective": "Be curious and help clarify what the person is experiencing.",
            "seeking_support": "Be warm and practical; clarify what kind of support they want.",
            "positive": "Acknowledge and explore the positive experience without exaggerating.",
            "neutral": "Use a natural, conversational tone and follow the user's lead.",
        }
        return guidance.get(mood, guidance["neutral"])

    def _extract_text(self, response: Any) -> str:
        text = getattr(response, "output_text", None)
        if text:
            return str(text).strip()

        output = getattr(response, "output", []) or []
        parts: List[str] = []
        for item in output:
            content = getattr(item, "content", []) or []
            for block in content:
                value = getattr(block, "text", None)
                if value:
                    parts.append(str(value))
        return " ".join(parts).strip()

    def _validate_response(self, text: str, analysis: Dict[str, Any]) -> bool:
        if not text or len(text) > 3000:
            return False

        lowered = text.lower()
        dangerous_patterns = [
            "here is how to kill yourself",
            "here's how to kill yourself",
            "instructions to kill yourself",
            "how to commit suicide",
            "how to self harm",
            "instructions for self harm",
            "ways to hurt yourself",
            "ways to kill yourself",
            "you should kill yourself",
            "you should hurt yourself",
        ]

        if any(pattern in lowered for pattern in dangerous_patterns):
            return False

        # The deterministic layer owns high-risk responses. This is a final
        # defense in case a caller invokes LLMEngine directly.
        if self._requires_deterministic_safety(analysis):
            return False

        return True

    def _fallback_response(
        self,
        message: str,
        analysis: Dict[str, Any],
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        mood = analysis.get("mood", "neutral")
        topic = (analysis.get("state", {}) or {}).get("last_topic")

        responses = {
            "anxious": (
                "It sounds like things are feeling overwhelming. "
                "Let's take it one step at a time. What feels most difficult right now?"
            ),
            "sad": (
                "I'm sorry you're going through this. "
                "I'm here to listen. What has been weighing on you?"
            ),
            "hopeless": (
                "It sounds like things feel very difficult right now. "
                "You don't have to explain everything at once. What feels hardest at the moment?"
            ),
            "low_self_worth": (
                "That sounds like a painful feeling to carry. "
                "I'm here to listen without judging you. What happened that led you to feel this way?"
            ),
            "positive": (
                "It's good to hear that. What has been going well for you?"
            ),
            "reflective": (
                "It sounds like you're trying to make sense of what you're feeling. "
                "What part of it is on your mind most right now?"
            ),
            "seeking_support": (
                "I'm here with you. We can work through this one step at a time. "
                "What kind of support would feel most useful right now?"
            ),
        }

        text = responses.get(mood)
        if not text and topic:
            text = f"Let's stay with your {topic} situation. What part would you like to talk through?"
        if not text:
            text = "I'm here to listen. Tell me what's on your mind."

        return {
            "text": text,
            "source": "fallback",
            "model": None,
            "used_llm": False,
        }

    def _clean_response(self, text: str) -> str:
        text = str(text or "").strip()
        while "\n\n\n" in text:
            text = text.replace("\n\n\n", "\n\n")
        return text
