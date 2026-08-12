from typing import Any, Dict, List, Optional


class ResponseEngine:
    def __init__(
        self,
        user_name="friend",
        llm_engine=None
    ):
        self.user_name = user_name or "friend"
        self.llm_engine = llm_engine
        self._recent_responses: List[str] = []
        self._recent_strategies: List[str] = []

    def generate(
        self,
        message,
        analysis,
        context
    ):
        message = (message or "").strip()
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
        text = message.lower().strip()

        if (
            risk_level == "high"
            or signals.get("crisis")
            or signals.get("self_harm")
        ):
            return self._remember_response(
                self._crisis_response(),
                "crisis"
            )

        if self._is_advice_request(text):
            strategy = "advice"
            reply = self._advice_response(
                text,
                topic,
                context,
                analysis
            )
            return self._remember_response(reply, strategy)

        if self._is_bored_message(text):
            reply = self._bored_response(
                topic,
                context
            )
            return self._remember_response(reply, "engagement")

        if self._is_greeting(text):
            return self._remember_response(
                self._greeting_response(),
                "greeting"
            )

        if self._is_gratitude(text):
            return self._remember_response(
                self._gratitude_response(),
                "gratitude"
            )

        if signals.get("hopelessness"):
            reply = self._hopeless_response(topic, context)
            return self._remember_response(reply, "support")

        if signals.get("worthlessness"):
            reply = self._worthlessness_response(topic, context)
            return self._remember_response(reply, "support")

        if signals.get("anxiety"):
            reply = self._anxiety_response(
                message,
                topic,
                context
            )
            return self._remember_response(reply, "grounding")

        if signals.get("sad"):
            reply = self._sad_response(
                message,
                topic,
                context
            )
            return self._remember_response(reply, "validation")

        if analysis.get("mood") == "positive":
            reply = self._positive_response(
                message,
                topic,
                context
            )
            return self._remember_response(reply, "positive")

        if self.llm_engine is not None:
            llm_reply = self._try_llm(
                message,
                analysis,
                self._build_llm_context(
                    context,
                    topic
                )
            )

            if llm_reply and self._is_usable_llm_reply(llm_reply):
                return self._remember_response(
                    llm_reply,
                    "llm"
                )

        reply, strategy = self._fallback_response(
            message,
            analysis,
            context
        )

        return self._remember_response(
            reply,
            strategy
        )

    def _build_llm_context(
        self,
        context: Dict[str, Any],
        topic: Optional[str]
    ) -> Dict[str, Any]:
        recent_messages = list(
            context.get("recent_user_messages", [])
        )
        recent_replies = list(
            context.get("recent_assistant_messages", [])
        )

        guidance = {
            "topic": topic,
            "avoid_repeating": list(self._recent_responses[-4:]),
            "recent_strategies": list(self._recent_strategies[-4:]),
            "rules": [
                "Respond to the user's latest message, not only the topic.",
                "Do not ask tell-me-more questions repeatedly.",
                "Do not repeat the previous assistant response.",
                "If the user asks for advice, give one or two practical next steps.",
                "If the user is sharing emotion, validate it before exploring.",
                "Ask at most one natural follow-up question.",
                "Do not use crisis language unless the safety analysis indicates crisis."
            ]
        }

        return {
            **context,
            "recent_user_messages": recent_messages[-8:],
            "recent_assistant_messages": recent_replies[-8:],
            "response_guidance": guidance
        }

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

    def _is_usable_llm_reply(self, reply: str) -> bool:
        normalized = self._normalize(reply)

        if normalized in {
            self._normalize(item)
            for item in self._recent_responses[-4:]
        }:
            return False

        repetitive_phrases = [
            "tell me a little more about what is happening",
            "tell me a little more about that",
            "tell me a little more",
            "what feels hardest right now"
        ]

        if (
            normalized in repetitive_phrases
            and self._recent_responses
        ):
            return False

        return len(reply.split()) >= 4

    def _fallback_response(
        self,
        message: str,
        analysis: Dict[str, Any],
        context: Dict[str, Any]
    ):
        text = message.lower().strip()
        signals = analysis.get("signals", {})
        state = analysis.get("state", {})
        topic = state.get("last_topic")
        streak = int(
            state.get("same_topic_streak", 0) or 0
        )

        recent_messages = context.get(
            "recent_user_messages",
            []
        )
        previous_message = (
            recent_messages[-1]
            if recent_messages
            else ""
        )

        if self._is_advice_request(text):
            return (
                self._advice_response(
                    text,
                    topic,
                    context,
                    analysis
                ),
                "advice"
            )

        if signals.get("crisis") or signals.get("self_harm"):
            return self._crisis_response(), "crisis"

        if signals.get("hopelessness"):
            return self._hopeless_response(
                topic,
                context
            ), "support"

        if signals.get("worthlessness"):
            return self._worthlessness_response(
                topic,
                context
            ), "support"

        if signals.get("anxiety"):
            return self._anxiety_response(
                message,
                topic,
                context
            ), "grounding"

        if signals.get("sad"):
            return self._sad_response(
                message,
                topic,
                context
            ), "validation"

        if self._is_greeting(text):
            return self._greeting_response(), "greeting"

        if self._is_gratitude(text):
            return self._gratitude_response(), "gratitude"

        if analysis.get("mood") == "positive":
            return self._positive_response(
                message,
                topic,
                context
            ), "positive"

        return self._neutral_response(
            message,
            topic,
            previous_message,
            streak,
            context
        )

    def _is_advice_request(self, text: str) -> bool:
        text = self._normalize(text)

        exact = {
            "what should i do",
            "what can i do",
            "what do i do",
            "how should i handle this",
            "how do i handle this",
            "what should i say",
            "should i talk to them",
            "should i message them",
            "should i confront them",
            "any advice",
            "give me advice"
        }

        if text in exact:
            return True

        return any(
            phrase in text
            for phrase in [
                "what should i do now",
                "what can i do now",
                "what should i say to them",
                "how should i respond",
                "what would you do"
            ]
        )

    def _is_bored_message(self, text: str) -> bool:
        text = self._normalize(text)

        return any(
            phrase in text
            for phrase in [
                "bored",
                "boring",
                "nothing to do",
                "nothing interesting",
                "nothing happened",
                "nothing much happened"
            ]
        )

    def _bored_response(
        self,
        topic: Optional[str],
        context: Dict[str, Any]
    ) -> str:
        recent = context.get(
            "recent_user_messages",
            []
        )

        if recent and any(
            phrase in str(recent[-1]).lower()
            for phrase in [
                "nothing interesting",
                "nothing happened",
                "nothing much happened"
            ]
        ):
            return (
                "Sounds like today has felt pretty flat rather than "
                "actively bad. We can change the pace a little. "
                "Do you want to talk about something that's been on "
                "your mind, or find something small and fun to do?"
            )

        if recent:
            return (
                "A slow day can feel surprisingly empty. We don't have "
                "to force a deep conversation either. Want to tell me "
                "what you've been doing today, or should we find a "
                "small distraction?"
            )

        return (
            "Sounds like you're having one of those slow days. "
            "We can either chat about whatever is on your mind, "
            "or I can help you come up with something to make the "
            "day a little less boring."
        )

    def _is_greeting(self, text: str) -> bool:
        return text.strip() in {
            "hi",
            "hello",
            "hey",
            "good morning",
            "good afternoon",
            "good evening"
        }

    def _is_gratitude(self, text: str) -> bool:
        return any(
            phrase in text
            for phrase in [
                "thank you",
                "thanks",
                "thx",
                "thank u"
            ]
        )

    def _topic_label(self, topic: Optional[str]) -> str:
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

    def _topic_keyword(self, topic: Optional[str]) -> str:
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

    def _advice_response(
        self,
        text: str,
        topic: Optional[str],
        context: Dict[str, Any],
        analysis: Dict[str, Any]
    ) -> str:
        recent = context.get(
            "recent_user_messages",
            []
        )

        previous = (
            recent[-1]
            if recent
            else ""
        ).lower()

        if topic == "friends" or any(
            phrase in previous
            for phrase in [
                "friends",
                "friend",
                "invite me",
                "left me out",
                "went out without me"
            ]
        ):
            if any(
                phrase in previous
                for phrase in [
                    "didn't invite me",
                    "did not invite me",
                    "went out without me",
                    "left me out",
                    "excluded me"
                ]
            ):
                return (
                    "I'd avoid assuming the worst while you're still hurt. "
                    "If you want clarity, ask one of them calmly what happened "
                    "and give them room to explain. Their response will tell "
                    "you more than guessing will. If this keeps happening, "
                    "then it may be worth reconsidering how much effort you "
                    "want to put into that friendship."
                )

            return (
                "If you're unsure what to do with your friends, start with "
                "the smallest honest step: talk to the person you trust most "
                "and explain how the situation made you feel without blaming "
                "them. See how they respond before deciding what to do next."
            )

        if topic == "college":
            return (
                "Start with the part of college that needs attention first. "
                "Pick one concrete problem, decide what you can control today, "
                "and leave the rest for later. If you tell me what happened, "
                "I can help you think through the next step."
            )

        if topic == "work":
            return (
                "I'd break the situation into what you can control and what "
                "you can't. Handle the most immediate task first, then decide "
                "whether a conversation with the relevant person would help. "
                "If you tell me what happened, we can work out what to say."
            )

        if topic == "relationships":
            return (
                "Before making a big decision, give yourself a little space "
                "and separate what you know from what you're assuming. Then "
                "have a calm conversation about the specific issue rather "
                "than trying to solve the whole relationship at once."
            )

        return (
            "I'd start with the smallest next step instead of trying to solve "
            "everything at once. Tell me what happened, and I can help you "
            "compare a couple of realistic options."
        )

    def _sad_response(
        self,
        message: str,
        topic: Optional[str],
        context: Dict[str, Any]
    ) -> str:
        text = message.lower()
        recent = context.get(
            "recent_user_messages",
            []
        )

        if any(
            phrase in text
            for phrase in [
                "left out",
                "excluded",
                "ignored me",
                "didn't invite me",
                "did not invite me",
                "went out without me"
            ]
        ):
            return (
                "Yeah, I can see why that would hurt. Being left out can "
                "make you question where you stand with people, especially "
                "when you don't know the reason. You don't have to decide "
                "what it means about the friendship yet."
            )

        if "lonely" in text or "loneliness" in text:
            return (
                "That sounds lonely. Sometimes the hardest part isn't being "
                "alone for a moment, but feeling like you weren't thought of. "
                "What part of today has felt most isolating?"
            )

        if recent and len(recent) >= 2:
            return (
                "I hear you. It sounds like this has moved from being an "
                "annoying moment to something that's actually affecting how "
                "you feel. What part of it hurts the most?"
            )

        if topic == "college":
            return (
                "That sounds tough, especially when college already gives "
                "you enough to carry. What happened that brought you to this "
                "point?"
            )

        if topic == "work":
            return (
                "That sounds difficult. Work or internship pressure can stay "
                "in your head even after the day is over. What happened?"
            )

        return (
            "That sounds genuinely hard. You don't have to package it neatly "
            "for me. Tell me what happened in your own words."
        )

    def _anxiety_response(
        self,
        message: str,
        topic: Optional[str],
        context: Dict[str, Any]
    ) -> str:
        if topic == "college":
            return (
                "Let's make the college problem smaller for a moment. "
                "What is the one thing you're most worried will happen?"
            )

        if topic == "work":
            return (
                "Let's separate the career worry from the actual next step. "
                "What outcome are you most afraid of right now?"
            )

        if topic == "future":
            return (
                "Uncertainty about the future can make every possibility "
                "feel urgent. What specific outcome are you worrying about?"
            )

        return (
            "It sounds like your mind is running ahead of you a bit. "
            "What is the specific outcome you're worried about most?"
        )

    def _hopeless_response(
        self,
        topic: Optional[str],
        context: Dict[str, Any]
    ) -> str:
        if topic == "college":
            return (
                "That sounds overwhelming. You don't have to solve your "
                "whole college situation tonight. What is the most immediate "
                "problem you need to get through?"
            )

        if topic == "work":
            return (
                "That sounds like a lot to carry. Let's separate the immediate "
                "work problem from everything else. What is pressing on you "
                "most right now?"
            )

        return (
            "I'm sorry things feel this heavy. Let's keep the focus small for "
            "a moment. What is the hardest part of today?"
        )

    def _worthlessness_response(
        self,
        topic: Optional[str],
        context: Dict[str, Any]
    ) -> str:
        if topic == "college":
            return (
                "A difficult semester or exam result doesn't measure your "
                "worth as a person. What happened that made you feel this way?"
            )

        if topic == "work":
            return (
                "A rejection, mistake, or difficult work situation doesn't "
                "define your worth. What happened?"
            )

        return (
            "That sounds like a painful way to be seeing yourself right now. "
            "A difficult moment is not the same thing as being a worthless "
            "person. What happened before you started feeling this way?"
        )

    def _positive_response(
        self,
        message: str,
        topic: Optional[str],
        context: Dict[str, Any]
    ) -> str:
        if topic == "college":
            return (
                "That's good to hear. What changed with college that made "
                "things feel a little better?"
            )

        if topic == "work":
            return (
                "Nice. What happened with work or your career that gave you "
                "a bit more confidence?"
            )

        if topic == "friends":
            return (
                "I'm glad there's a better moment in there. What happened "
                "that made you feel good about your friends?"
            )

        return (
            "That's good to hear. What was the part of today that lifted "
            "your mood?"
        )

    def _neutral_response(
        self,
        message: str,
        topic: Optional[str],
        previous_message: str,
        streak: int,
        context: Dict[str, Any]
    ):
        text = message.lower().strip()

        if topic == "friends":
            if any(
                phrase in text
                for phrase in [
                    "went out",
                    "didn't invite",
                    "did not invite",
                    "left me out",
                    "excluded"
                ]
            ):
                return (
                    "That would make a lot of people feel left out. "
                    "Do you know whether there was a specific reason they "
                    "went without you, or are you mostly stuck wondering "
                    "what happened?"
                ), "reflection"

            options = [
                (
                    "I'm listening. What's been happening with your friends "
                    "that has been sitting with you?",
                    "exploration"
                ),
                (
                    "It sounds like there's something about this friendship "
                    "situation you haven't quite made sense of yet. What part "
                    "keeps replaying in your head?",
                    "reflection"
                ),
                (
                    "We can look at this from either side: how it made you "
                    "feel, or what you might want to do next. Which would "
                    "help more right now?",
                    "choice"
                )
            ]
            return options[min(max(streak, 0), len(options) - 1)]

        if topic == "college":
            options = [
                (
                    "What's going on with college today?",
                    "exploration"
                ),
                (
                    "Is the main issue the workload, exams, or something "
                    "outside academics?",
                    "clarification"
                ),
                (
                    "Let's narrow it down. What's the one college problem "
                    "you'd most like to change right now?",
                    "focus"
                )
            ]
            return options[min(max(streak, 0), len(options) - 1)]

        if topic == "work":
            options = [
                (
                    "What's been going on with work or your career?",
                    "exploration"
                ),
                (
                    "Is the pressure coming more from the work itself, "
                    "people around you, or uncertainty about what's next?",
                    "clarification"
                ),
                (
                    "Let's focus on one thing. What's the biggest work or "
                    "career problem on your mind today?",
                    "focus"
                )
            ]
            return options[min(max(streak, 0), len(options) - 1)]

        if topic:
            options = [
                (
                    f"What's been happening with your "
                    f"{self._topic_keyword(topic)}?",
                    "exploration"
                ),
                (
                    f"What part of your {self._topic_keyword(topic)} "
                    "situation is affecting you most?",
                    "clarification"
                ),
                (
                    "Would it help more to talk through what happened, "
                    "or think about what you could do next?",
                    "choice"
                )
            ]
            return options[min(max(streak, 0), len(options) - 1)]

        if previous_message:
            return (
                "I'm following you. Rather than making you repeat yourself, "
                "what do you think is the main thing you need from this "
                "conversation right now?",
                "needs"
            )

        return (
            "I'm here with you. What's been on your mind today?",
            "exploration"
        )

    def _greeting_response(self) -> str:
        return (
            f"Hey {self.user_name}. Good to see you. "
            "What's going on today?"
        )

    def _gratitude_response(self) -> str:
        return (
            "You're welcome. I'm glad you felt comfortable sharing that."
        )

    def _crisis_response(self) -> str:
        resources_line = ""

        try:
            from app.safety_resources import SafetyResources
            resources_line = SafetyResources().format_for_reply()
        except Exception:
            resources_line = ""

        if not resources_line:
            resources_line = (
                "Find A Helpline (findahelpline.com) can connect you to a "
                "free, confidential crisis line in your area."
            )

        return (
            "I'm really glad you told me. Your safety matters, and you "
            "don't have to handle this alone. "
            f"{resources_line} "
            "If you feel you might act on these thoughts or you're in "
            "immediate danger, please reach out to immediate human support "
            "or move toward a trusted person nearby. I'm still here with you."
        )

    def _remember_response(
        self,
        response: str,
        strategy: str
    ) -> str:
        response = (response or "").strip()

        if not response:
            return (
                "I'm here with you. Tell me what feels most important "
                "right now."
            )

        normalized = self._normalize(response)

        if normalized in {
            self._normalize(item)
            for item in self._recent_responses[-3:]
        }:
            return self._fresh_fallback(strategy)

        self._recent_responses.append(response)
        self._recent_strategies.append(strategy)

        if len(self._recent_responses) > 8:
            self._recent_responses = self._recent_responses[-8:]

        if len(self._recent_strategies) > 8:
            self._recent_strategies = self._recent_strategies[-8:]

        return response

    def _fresh_fallback(self, strategy: str) -> str:
        alternatives = {
            "exploration": (
                "I'm with you. What's the part of this situation "
                "you haven't said yet?"
            ),
            "reflection": (
                "I hear you. What is this situation making you think "
                "about yourself or the people involved?"
            ),
            "validation": (
                "That makes sense. What part of the situation is "
                "hurting or bothering you most?"
            ),
            "advice": (
                "Let's keep it practical. What outcome would you most "
                "like to get from the situation?"
            ),
            "support": (
                "You don't have to solve everything at once. "
                "What would make the next hour a little easier?"
            ),
            "engagement": (
                "Yeah, sounds like today has been pretty uneventful. "
                "Want to talk about something random, something that's "
                "been bothering you, or find a small thing to do?"
            )
        }

        return alternatives.get(
            strategy,
            "I'm still with you. What feels most important right now?"
        )

    def _normalize(self, text: str) -> str:
        import re

        text = str(text or "").lower().strip()
        text = re.sub(r"[^a-z0-9\\s']", " ", text)
        return " ".join(text.split())

    def get_recent_responses(self):
        return list(self._recent_responses)
