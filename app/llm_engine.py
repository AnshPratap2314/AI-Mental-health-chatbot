import os
from typing import Any, Dict, List, Optional


class LLMEngine:

    def __init__(
        self,
        model: Optional[str] = None,
        enabled: Optional[bool] = None
    ):
        self.model = model or os.getenv(
            "OPENAI_MODEL",
            "gpt-5-mini"
        )

        api_key = os.getenv(
            "OPENAI_API_KEY"
        )

        if enabled is None:
            enabled = bool(api_key)

        self.enabled = bool(enabled and api_key)
        self.api_key = api_key

        self._client = None

        if self.enabled:
            self._initialize_client()

    def _initialize_client(self):
        try:
            from openai import OpenAI

            self._client = OpenAI(
                api_key=self.api_key
            )

        except Exception:
            self._client = None
            self.enabled = False

    def generate(
        self,
        message: str,
        analysis: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:

        if not self.enabled or self._client is None:
            return self._fallback_response(
                message,
                analysis,
                context
            )

        if self._is_high_risk(analysis):
            return self._fallback_response(
                message,
                analysis,
                context
            )

        try:
            prompt = self._build_prompt(
                message,
                analysis,
                context
            )

            response = self._client.responses.create(
                model=self.model,
                instructions=self._system_instructions(),
                input=prompt
            )

            text = self._extract_text(response)

            if not text:
                return self._fallback_response(
                    message,
                    analysis,
                    context
                )

            text = self._clean_response(text)

            if not self._validate_response(
                text,
                analysis
            ):
                return self._fallback_response(
                    message,
                    analysis,
                    context
                )

            return {
                "text": text,
                "source": "llm",
                "model": self.model,
                "used_llm": True
            }

        except Exception:
            return self._fallback_response(
                message,
                analysis,
                context
            )

    def _system_instructions(self) -> str:

        return (
            "You are MindCare, a warm, emotionally attuned companion — "
            "the kind of friend people message when they're happy, "
            "bored, stressed, or having a hard day. You are not a "
            "doctor, therapist, or emergency service, and you never "
            "diagnose or claim clinical expertise. "
            "Talk like a real, caring friend texting back: natural, "
            "specific to what they just said, never generic or "
            "scripted-sounding. Match their energy — celebrate good "
            "news with genuine enthusiasm, sit with sadness gently "
            "without rushing to fix it, and keep casual chat light "
            "and fun. "
            "Vary your phrasing every time; never reuse the same "
            "sentence structure twice in a row, and never repeat a "
            "question you've already asked in this conversation. "
            "Keep replies short and conversational (1-3 sentences "
            "unless the person clearly wants more), not a lecture. "
            "Ask at most one genuine, specific follow-up question "
            "when it fits naturally. "
            "Do not provide instructions for self-harm, suicide, "
            "violence, or dangerous behavior, and do not encourage "
            "harmful behavior. Do not make the user feel dependent "
            "on you — gently support real-world connection too. "
            "Never claim to have contacted emergency services, and "
            "never claim certainty about the user's mental health."
        )

    def _build_prompt(
        self,
        message: str,
        analysis: Dict[str, Any],
        context: Dict[str, Any]
    ) -> str:

        state = analysis.get(
            "state",
            {}
        )

        mood = state.get(
            "current_mood",
            analysis.get("mood", "neutral")
        )

        risk = analysis.get(
            "risk_level",
            "low"
        )

        topic = state.get(
            "last_topic"
        )

        recent_messages = context.get(
            "recent_user_messages",
            []
        )

        recent = recent_messages[-5:]

        history = "\n".join(
            "- " + str(item)
            for item in recent
        )

        recent_replies = context.get(
            "recent_assistant_messages",
            []
        )[-3:]

        reply_history = "\n".join(
            "- " + str(item)
            for item in recent_replies
        )

        return (
            "Current user message:\n"
            f"{message}\n\n"
            "Conversation state:\n"
            f"Mood: {mood}\n"
            f"Risk: {risk}\n"
            f"Topic: {topic or 'unknown'}\n\n"
            "Recent user messages:\n"
            f"{history or '- none'}\n\n"
            "Your own recent replies (do not repeat these "
            "phrasings or questions):\n"
            f"{reply_history or '- none'}\n\n"
            "Generate a supportive response that:\n"
            "1. Directly responds to the user's message.\n"
            "2. Matches the user's emotional state.\n"
            "3. Preserves the current conversation topic.\n"
            "4. Does not invent personal facts.\n"
            "5. Does not diagnose.\n"
            "6. Does not provide harmful instructions.\n"
            "7. Is concise, conversational, and sounds like a "
            "real friend, not a script.\n"
        )

    def _extract_text(
        self,
        response: Any
    ) -> str:

        text = getattr(
            response,
            "output_text",
            None
        )

        if text:
            return str(text).strip()

        output = getattr(
            response,
            "output",
            []
        )

        parts: List[str] = []

        for item in output or []:
            content = getattr(
                item,
                "content",
                []
            )

            for block in content or []:
                value = getattr(
                    block,
                    "text",
                    None
                )

                if value:
                    parts.append(
                        str(value)
                    )

        return " ".join(parts).strip()

    def _validate_response(
        self,
        text: str,
        analysis: Dict[str, Any]
    ) -> bool:

        if not text:
            return False

        if len(text) > 3000:
            return False

        lowered = text.lower()

        dangerous_patterns = [
            "here is how to kill yourself",
            "here's how to kill yourself",
            "instructions to kill yourself",
            "how to commit suicide",
            "how to self harm",
            "instructions for self harm",
            "ways to hurt yourself"
        ]

        for pattern in dangerous_patterns:
            if pattern in lowered:
                return False

        if analysis.get("risk_level") == "high":
            return False

        return True

    def _is_high_risk(
        self,
        analysis: Dict[str, Any]
    ) -> bool:

        safety = analysis.get(
            "safety",
            {}
        )

        policy = safety.get(
            "policy",
            {}
        )

        return (
            analysis.get("risk_level") == "high"
            or safety.get("risk_level") == "high"
            or policy.get("risk_level") == "high"
            or policy.get(
                "require_safety_response",
                False
            )
        )

    def _fallback_response(
        self,
        message: str,
        analysis: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:

        mood = analysis.get(
            "mood",
            "neutral"
        )

        topic = (
            analysis.get("state", {})
            .get("last_topic")
        )

        if mood == "anxious":
            text = (
                "It sounds like things are feeling overwhelming. "
                "Let's take this one step at a time. "
                "What feels most difficult right now?"
            )

        elif mood == "sad":
            text = (
                "I'm sorry you're going through this. "
                "I'm here to listen. "
                "What has been weighing on you?"
            )

        elif mood == "hopeless":
            text = (
                "It sounds like things feel very difficult right now. "
                "You don't have to explain everything at once. "
                "What feels hardest at the moment?"
            )

        elif mood == "low_self_worth":
            text = (
                "That sounds like a painful feeling to carry. "
                "I'm here to listen without judging you. "
                "What happened that led you to feel this way?"
            )

        elif mood == "positive":
            text = (
                "It's good to hear that. "
                "What has been going well for you?"
            )

        elif topic:
            text = (
                f"Let's stay with your {topic} situation. "
                "What part would you like to talk through?"
            )

        else:
            text = (
                "I'm here to listen. "
                "Tell me what's on your mind."
            )

        return {
            "text": text,
            "source": "fallback",
            "model": None,
            "used_llm": False
        }

    def _clean_response(
        self,
        text: str
    ) -> str:

        text = str(text).strip()

        while "\n\n\n" in text:
            text = text.replace(
                "\n\n\n",
                "\n\n"
            )

        return text