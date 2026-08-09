from typing import Any, Dict, Optional


class ResponseEngine:

    def __init__(
        self,
        user_name="friend",
        llm_engine=None
    ):
        self.user_name = user_name or "friend"
        self.llm_engine = llm_engine

    def generate(
        self,
        message,
        analysis,
        context
    ):
        message = (message or "").strip()
        text = message.lower()

        analysis = analysis or {}
        context = context or {}

        signals = analysis.get("signals", {})
        state = analysis.get("state", {})

        risk_level = str(
            analysis.get(
                "risk_level",
                state.get("current_risk", "low")
            ) or "low"
        ).lower()

        topic = state.get("last_topic")

        if (
            risk_level == "high"
            or signals.get("crisis")
            or signals.get("self_harm")
        ):
            return self._crisis_response()

        if risk_level == "moderate":
            return self._serious_response(topic)

        if signals.get("serious"):
            return self._serious_response(topic)

        if self.llm_engine is not None:
            llm_reply = self._try_llm(
                message,
                analysis,
                context
            )

            if llm_reply:
                return llm_reply

        return self._fallback_response(
            message,
            analysis,
            context
        )

    def _try_llm(
        self,
        message: str,
        analysis: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Optional[str]:

        try:
            if hasattr(self.llm_engine, "generate"):
                result = self.llm_engine.generate(
                    message=message,
                    analysis=analysis,
                    context=context
                )
            elif hasattr(self.llm_engine, "generate_response"):
                result = self.llm_engine.generate_response(
                    message=message,
                    analysis=analysis,
                    context=context
                )
            elif hasattr(self.llm_engine, "respond"):
                result = self.llm_engine.respond(
                    message=message,
                    analysis=analysis,
                    context=context
                )
            else:
                return None

            if isinstance(result, dict):
                reply = (
                    result.get("reply")
                    or result.get("response")
                    or result.get("text")
                )
            else:
                reply = result

            if not isinstance(reply, str):
                return None

            reply = reply.strip()

            if not reply:
                return None

            return reply

        except Exception:
            return None

    def _fallback_response(
        self,
        message: str,
        analysis: Dict[str, Any],
        context: Dict[str, Any]
    ) -> str:

        text = message.lower()

        signals = analysis.get(
            "signals",
            {}
        )

        state = analysis.get(
            "state",
            {}
        )

        topic = state.get(
            "last_topic"
        )

        previous_messages = context.get(
            "recent_user_messages",
            []
        )

        previous_message = (
            previous_messages[-1]
            if previous_messages
            else ""
        )

        if self._is_follow_up(text):
            return self._follow_up_response(
                topic,
                previous_message
            )

        if signals.get("crisis") or signals.get("self_harm"):
            return self._crisis_response()

        if signals.get("hopelessness"):
            return self._hopeless_response(topic)

        if signals.get("worthlessness"):
            return self._worthlessness_response(topic)

        if signals.get("sad"):
            return self._sad_response(
                text,
                topic
            )

        if signals.get("anxiety"):
            return self._anxiety_response(topic)

        if signals.get("intent"):
            return self._intent_response(topic)

        if self._is_greeting(text):
            return self._greeting_response()

        if self._is_gratitude(text):
            return self._gratitude_response()

        if analysis.get("mood") == "positive":
            return self._positive_response(topic)

        return self._neutral_response(
            topic,
            previous_message
        )

    def _is_follow_up(
        self,
        text: str
    ) -> bool:

        text = text.strip()

        exact_phrases = {
            "why",
            "how",
            "continue",
            "go on",
            "what else",
            "tell me more",
            "what should i do",
            "what can i do",
            "what do i do",
            "then what",
            "anything else",
            "more about that",
            "explain more"
        }

        if text in exact_phrases:
            return True

        phrases = [
            "tell me more",
            "what do you mean",
            "and then",
            "can you explain",
            "explain more",
            "more about that",
            "what should i do",
            "what can i do",
            "what do i do"
        ]

        return any(
            phrase in text
            for phrase in phrases
        )

    def _is_greeting(
        self,
        text: str
    ) -> bool:

        return text.strip() in {
            "hi",
            "hello",
            "hey",
            "good morning",
            "good afternoon",
            "good evening"
        }

    def _is_gratitude(
        self,
        text: str
    ) -> bool:

        return any(
            phrase in text
            for phrase in [
                "thank you",
                "thanks",
                "thx",
                "thank u"
            ]
        )

    def _topic_label(
        self,
        topic: Optional[str]
    ) -> str:

        labels = {
            "college": "college and exams",
            "work": "your internship and career",
            "future": "your future",
            "relationships": "your relationships",
            "family": "your family",
            "health": "your health",
            "finance": "your financial situation",
            "friends": "your friendships",
            "social": "your social life",
            "personal": "your personal situation"
        }

        return labels.get(
            topic,
            "what you're dealing with"
        )

    def _topic_keyword(
        self,
        topic: Optional[str]
    ) -> str:

        keywords = {
            "college": "college",
            "work": "work",
            "future": "future",
            "relationships": "relationship",
            "family": "family",
            "health": "health",
            "finance": "finances",
            "friends": "friendships",
            "social": "social life",
            "personal": "personal situation"
        }

        return keywords.get(
            topic,
            "situation"
        )

    def _follow_up_response(
        self,
        topic: Optional[str],
        previous_message: str
    ) -> str:

        if topic == "college":
            return (
                "Your college and exam situation seems to be "
                "weighing on you. What part of your studies feels "
                "hardest right now?"
            )

        if topic == "work":
            return (
                "Your internship and career situation seems "
                "important right now. What part of the work or "
                "interview process is worrying you most?"
            )

        if topic == "future":
            return (
                "It sounds like your future is on your mind. "
                "What part of the future feels most uncertain "
                "or difficult right now?"
            )

        if topic == "relationships":
            return (
                "It sounds like your relationship situation is "
                "weighing on you. What has been happening?"
            )

        if topic == "family":
            return (
                "It sounds like something involving your family "
                "has been difficult. What part of the situation "
                "is affecting you most?"
            )

        if topic == "health":
            return (
                "It sounds like your health situation is on your "
                "mind. What has been worrying you most?"
            )

        if topic == "finance":
            return (
                "It sounds like your financial situation is "
                "causing some pressure. What feels hardest "
                "about it right now?"
            )

        if topic == "friends":
            return (
                "It sounds like your friendships are affecting "
                "how you're feeling. What happened?"
            )

        if topic == "social":
            return (
                "It sounds like your social situation is weighing "
                "on you. What has been difficult?"
            )

        if previous_message:
            return (
                "I'm following what you've shared. "
                "Let's take it one step at a time. "
                "What feels hardest right now?"
            )

        return (
            "I'm listening. Tell me a little more about "
            "what's been happening."
        )

    def _sad_response(
        self,
        text: str,
        topic: Optional[str]
    ) -> str:

        if "lonely" in text or "loneliness" in text:
            return (
                "I'm sorry you're feeling lonely. "
                f"It sounds like your {self._topic_keyword(topic)} "
                "situation may be affecting you. "
                "What's been happening?"
            )

        return (
            "I'm sorry you're going through this. "
            f"Let's talk about your {self._topic_keyword(topic)} "
            "situation one step at a time. "
            "What has been weighing on you?"
        )

    def _anxiety_response(
        self,
        topic: Optional[str]
    ) -> str:

        if topic == "college":
            return (
                "It sounds like your college and exams are making "
                "you anxious. Let's focus on one part of your "
                "studies at a time. What is worrying you most?"
            )

        if topic == "work":
            return (
                "It sounds like your internship or career situation "
                "is making you anxious. Let's focus on one part of "
                "it at a time. What concerns you most?"
            )

        if topic == "future":
            return (
                "It sounds like uncertainty about your future is "
                "making you anxious. Let's focus on what you can "
                "deal with right now. What concerns you most?"
            )

        return (
            "It sounds like things are feeling overwhelming. "
            "Let's slow things down and focus on one thing "
            "at a time. What is worrying you the most?"
        )

    def _hopeless_response(
        self,
        topic: Optional[str]
    ) -> str:

        if topic == "college":
            return (
                "I'm sorry your college situation feels so "
                "overwhelming right now. You don't have to solve "
                "everything at once. What feels hardest about "
                "your exams or studies?"
            )

        if topic == "work":
            return (
                "I'm sorry your work or internship situation feels "
                "so difficult right now. You don't have to solve "
                "everything at once. What feels hardest about it?"
            )

        return (
            "I'm sorry things feel so difficult right now. "
            "You don't have to explain everything at once. "
            "What feels hardest at the moment?"
        )

    def _worthlessness_response(
        self,
        topic: Optional[str]
    ) -> str:

        if topic == "college":
            return (
                "I'm sorry you're carrying that feeling. "
                "Struggling with college or exams does not define "
                "your worth. What has led you to feel this way?"
            )

        if topic == "work":
            return (
                "I'm sorry you're carrying that feeling. "
                "Difficulties with work, interviews, or internships "
                "do not define your worth. What happened?"
            )

        return (
            "I'm sorry you're carrying that feeling. "
            "Feeling worthless can be very heavy. "
            "Would you like to tell me what led you to feel this way?"
        )

    def _intent_response(
        self,
        topic: Optional[str]
    ) -> str:

        if topic == "college":
            return (
                "I'm here with you. Let's take your college "
                "situation one step at a time. What would you "
                "like help with first?"
            )

        if topic == "work":
            return (
                "I'm here with you. Let's take your internship "
                "or career situation one step at a time. "
                "What would you like help with first?"
            )

        if topic == "future":
            return (
                "I'm here with you. Let's take your future "
                "concerns one step at a time. What would you "
                "like to work through first?"
            )

        return (
            "I'm here with you. Let's slow things down "
            "and focus on what is happening right now."
        )

    def _greeting_response(self) -> str:
        return (
            f"Hi {self.user_name}. "
            "I'm here to listen. What's on your mind?"
        )

    def _gratitude_response(self) -> str:
        return (
            "You're welcome. I'm glad you felt comfortable "
            "sharing that with me."
        )

    def _positive_response(
        self,
        topic: Optional[str]
    ) -> str:

        if topic == "college":
            return (
                "It's good to hear that you're feeling better "
                "about college. What has been going well?"
            )

        if topic == "work":
            return (
                "It's good to hear that you're feeling better "
                "about your work or career situation. "
                "What has been going well?"
            )

        if topic == "future":
            return (
                "It's good to hear that you're feeling more "
                "positive about your future. What are you "
                "looking forward to?"
            )

        return (
            "That's good to hear. "
            "Tell me more about what's going well."
        )

    def _neutral_response(
        self,
        topic: Optional[str],
        previous_message: str
    ) -> str:

        if topic == "college":
            return (
                "I'm following your college situation. "
                "Tell me a little more about your exams, "
                "studies, or what has been difficult."
            )

        if topic == "work":
            return (
                "I'm following your work and career situation. "
                "Tell me a little more about your internship, "
                "interview, or what has been difficult."
            )

        if topic == "future":
            return (
                "I'm following what you've shared about your "
                "future. Tell me a little more about what's "
                "on your mind."
            )

        if topic == "relationships":
            return (
                "I'm following what you've shared about your "
                "relationship situation. Tell me a little more "
                "about what happened."
            )

        if topic == "family":
            return (
                "I'm following what you've shared about your "
                "family situation. Tell me a little more."
            )

        if topic:
            return (
                f"I'm following your {self._topic_keyword(topic)} "
                "situation. Tell me a little more about what's "
                "happening."
            )

        if previous_message:
            return (
                "I'm following what you've shared. "
                "Tell me a little more about what is happening."
            )

        return (
            "I'm here to listen. "
            "Tell me what's on your mind."
        )

    def _serious_response(
        self,
        topic: Optional[str]
    ) -> str:

        if topic == "college":
            return (
                "It sounds like your college situation is "
                "becoming very difficult to carry. "
                "You don't have to handle everything at once. "
                "What feels most difficult right now?"
            )

        if topic == "work":
            return (
                "It sounds like your work or internship situation "
                "is becoming very difficult to carry. "
                "You don't have to handle everything at once. "
                "What feels most difficult right now?"
            )

        return (
            "It sounds like you're going through something "
            "very difficult. Your safety matters. "
            "If you feel you may be in immediate danger, "
            "please contact local emergency services or "
            "a trusted person nearby."
        )

    def _crisis_response(self) -> str:
        return (
            "I'm really sorry you're going through this. "
            "Your safety is important. If you think you might "
            "act on these thoughts or you're in immediate danger, "
            "please move toward a safe person or place and "
            "contact your local emergency services or a qualified "
            "crisis service. You can keep talking to me while "
            "you reach human support."
        )