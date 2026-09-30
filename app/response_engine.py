from collections import deque
from typing import Any, Dict, Optional

try:

    from .response_model import TrainedResponseModel

except Exception:

    TrainedResponseModel = None





class ResponseEngine:

    """

    MindCare response routing engine.

    Routing order:

        Authoritative Safety/Risk

                    ↓

        Conversation Controls

                    ↓

                 LLM

                    ↓

        Trained Response Model

                    ↓

        Deterministic Fallback

    IMPORTANT:

    - BehaviorEngine risk is authoritative.

    - TrainedResponseModel risk is NEVER used for safety decisions.

    - LLM receives the complete BehaviorEngine analysis.

    - Conversation-control messages are handled deterministically.

    """

    RESPONSE_MODEL_NAME = "mindcare-response-10k"

    def __init__(

        self,

        user_name="friend",

        llm_engine=None,

    ):

        self.user_name = user_name or "friend"

        self.llm_engine = llm_engine

        self.last_source = "fallback"

        self.last_model = None

        self.response_model = None

        # Per-session response history prevents immediate repetition while
        # keeping selection bounded to relevant candidates.
        self._recent_trained_responses = deque(maxlen=8)

        if TrainedResponseModel is not None:

            try:

                self.response_model = TrainedResponseModel()

            except Exception:

                self.response_model = None

# =====================================================================
# MAIN RESPONSE ROUTER
# =====================================================================
    def generate(

        self,

        message,

        analysis,

        context,

    ):

        message = (message or "").strip()

        text = message.lower()

        analysis = analysis or {}

        context = context or {}

        self.last_source = "fallback"

        self.last_model = None

        signals = analysis.get(

            "signals",

            {},

        )

        if not isinstance(signals, dict):

            signals = {}

        state = analysis.get(

            "state",

            {},

        )

        if not isinstance(state, dict):

            state = {}

# ================================================================
# AUTHORITATIVE RISK
# ================================================================
# This comes from BehaviorEngine.
# NEVER replace this with:
#     response_model.predict_metadata()["risk_level"]
# The trained response model is not a safety engine.
        risk_level = str(

            analysis.get(

                "risk_level",

                state.get(

                    "current_risk",

                    "low",

                ),

            )

            or "low"

        ).lower()

        topic = (

            analysis.get("topic")

            or state.get("last_topic")

        )

# ================================================================
# 1. AUTHORITATIVE SAFETY ROUTING
# ================================================================
        if (

            risk_level == "high"

            or signals.get("crisis")

            or signals.get("self_harm")

            or signals.get("plan")
            or signals.get("contextual_suicide")

        ):

            self.last_source = "safety"

            self.last_model = None

            return self._crisis_response()

# ================================================================
# 2. CONVERSATION CONTROL
# ================================================================
# These should remain deterministic and should not be replaced
# by either the LLM or the response dataset.
        if self._is_follow_up(text):

            self.last_source = "fallback"

            self.last_model = None

            return self._follow_up_response(

                topic,

                self._previous_message(context),

            )

        if self._is_greeting(text):

            self.last_source = "fallback"

            self.last_model = None

            return self._greeting_response()

        if self._is_gratitude(text):

            self.last_source = "fallback"

            self.last_model = None

            return self._gratitude_response()

# ================================================================
# 3. REAL LLM
# ================================================================
# The LLM gets the complete BehaviorEngine analysis.
# This is important for tests and production because the LLM
# should receive:
#   mood
#   mood_intensity
#   topic
#   risk_level
#   signals
#   context
# exactly as produced by BehaviorEngine.
        if self.llm_engine is not None:

            llm_reply = self._try_llm(

                message,

                analysis,

                context,

            )

            if llm_reply:

                return llm_reply

# ================================================================
# 4. TRAINED RESPONSE MODEL
# ================================================================
        trained_reply = self._trained_response(

            message,

            analysis,

            context,

        )

        if trained_reply:

            self.last_source = "trained_response_model"

            self.last_model = self.RESPONSE_MODEL_NAME

            return trained_reply

# ================================================================
# 5. MODERATE / SERIOUS DETERMINISTIC FALLBACK
# ================================================================
# Moderate by itself does NOT mean "serious response".
# Only route here when the authoritative analysis contains
# an actual serious signal.
        if (

            risk_level == "moderate"

            and (

                signals.get("serious")

                or signals.get("hopelessness")

                or signals.get("worthlessness")

            )

        ):

            self.last_source = "fallback"

            self.last_model = None

            return self._serious_response(topic)

        if (

            signals.get("serious")

            and risk_level != "high"

        ):

            self.last_source = "fallback"

            self.last_model = None

            return self._serious_response(topic)

# ================================================================
# 6. ORIGINAL FALLBACK
# ================================================================
        self.last_source = "fallback"

        self.last_model = None

        return self._fallback_response(

            message,

            analysis,

            context,

        )

# =====================================================================
# CONTEXT
# =====================================================================
    def _previous_message(

        self,

        context: Dict[str, Any],

    ) -> str:

        messages = context.get(

            "recent_user_messages",

            [],

        )

        if isinstance(

            messages,

            (list, tuple),

        ) and messages:

            return str(

                messages[-1] or ""

            )

        return ""

# =====================================================================
# TRAINED RESPONSE MODEL
# =====================================================================
    def _trained_response(

        self,

        message: str,

        analysis: Dict[str, Any],

        context: Dict[str, Any],

    ) -> Optional[str]:

        """Select a trained response only when relevance is sufficiently strong."""

        model = self.response_model

        if model is None:

            return None

        risk_level = str(

            analysis.get("risk_level", "low") or "low"

        ).lower()

        signals = analysis.get("signals", {})

        if not isinstance(signals, dict):

            signals = {}

# The response model can never override authoritative safety.
        if (

            risk_level == "high"

            or signals.get("crisis")

            or signals.get("self_harm")

            or signals.get("plan")

        ):

            return None

# Preserve stable deterministic behavior for the simplest direct
# emotional statement.
        if message.lower().strip() in {

            "i feel lonely",

            "i'm lonely",

            "im lonely",

            "i am lonely",

        }:

            return None

        try:

            metadata = model.predict_metadata(message)

        except Exception:

            metadata = {}

        if not isinstance(metadata, dict):

            metadata = {}

        requested_mood = analysis.get("mood") or metadata.get("mood")

        requested_intent = analysis.get("intent") or metadata.get("intent")

        requested_topic = (

            analysis.get("topic")

            or analysis.get("state", {}).get("last_topic")

            or metadata.get("topic")

        )

        try:

            examples = model.find_examples(

                message=message,

                risk_level=risk_level,

                mood=requested_mood,

                intent=requested_intent,

                topic=requested_topic,

                top_k=5,

            )

        except Exception:

            return None

        if not examples:

            return None

        best = examples[0]

        similarity = float(best.get("similarity", 0.0) or 0.0)

        retrieval_score = float(best.get("retrieval_score", 0.0) or 0.0)

        metadata_match_count = int(best.get("metadata_match_count", 0) or 0)

        phrase_hint = bool(best.get("phrase_hint", False))

        semantic = best.get("semantic_metadata", {}) or {}

        intent_semantic = float(

            semantic.get("intent_semantic_confidence", 0.0) or 0.0

        )

        mood_semantic = float(

            semantic.get("mood_semantic_confidence", 0.0) or 0.0

        )

        topic_semantic = float(

            semantic.get("topic_semantic_confidence", 0.0) or 0.0

        )

        semantic_consensus = min(

            intent_semantic,

            mood_semantic,

            topic_semantic,

        )

        if str(best.get("risk_level", "")).lower() == "high":

            return None

# Three gates avoid both extremes: rejecting useful low-overlap
# paraphrases and accepting weak unrelated matches.
#
# The retrieval model now ranks contextual agreement first, so a
# phrase-guided relationship/loneliness/positive candidate can be
# accepted even when its lexical overlap is modest.
        strong_match = (

            similarity >= 0.30

            and retrieval_score >= 0.65

        )

        consensus_match = (

            semantic_consensus >= 0.66

            and metadata_match_count >= 2

            and similarity >= 0.10

            and retrieval_score >= 0.55

        )

        phrase_match = (

            phrase_hint

            and metadata_match_count >= 2

            and similarity >= 0.10

            and retrieval_score >= 0.50

        )

        # Phrase hints can improve routing, but they cannot bypass
        # the minimum semantic-evidence floor.
        guided_match = (
            phrase_hint
            and metadata_match_count >= 2
            and similarity >= 0.10
            and retrieval_score >= 0.45
        )

        if not (

            strong_match

            or consensus_match

            or phrase_match

            or guided_match

        ):

            return None

        # Keep diversity bounded by the already-ranked candidate set.
        eligible_examples = [
            item
            for item in examples
            if float(item.get("similarity", 0.0) or 0.0)
            >= max(0.10, similarity - 0.12)
        ]

        return self._select_diverse_trained_response(
            eligible_examples or examples[:1]
        )

# LLM
# =====================================================================
    def _select_diverse_trained_response(
        self,
        examples,
    ) -> Optional[str]:
        """Select a relevant response while avoiding immediate repetition."""
        if not examples:
            return None

        recent = {
            str(item).strip().casefold()
            for item in self._recent_trained_responses
        }

        eligible = []
        for item in examples:
            response = str(item.get("response", "") or "").strip()
            if not response:
                continue
            if len(response) < 20 or len(response) > 500:
                continue

            lowered = response.casefold()
            if any(
                marker in lowered
                for marker in (
                    "intent:",
                    "mood:",
                    "topic:",
                    "risk_level:",
                    "retrieval score:",
                )
            ):
                continue

            eligible.append((item, response))

        if not eligible:
            return None

        for _, response in eligible:
            if response.casefold() not in recent:
                self._recent_trained_responses.append(response)
                return response

        response = eligible[0][1]
        self._recent_trained_responses.append(response)
        return response

    def _try_llm(

        self,

        message: str,

        analysis: Dict[str, Any],

        context: Dict[str, Any],

    ) -> Optional[str]:

        try:

            if (

                getattr(

                    self.llm_engine,

                    "enabled",

                    True,

                )

                is False

            ):

                return None

# ------------------------------------------------------------
# Call LLM using the complete BehaviorEngine analysis.
# ------------------------------------------------------------
            if hasattr(

                self.llm_engine,

                "generate",

            ):

                result = self.llm_engine.generate(

                    message=message,

                    analysis=analysis,

                    context=context,

                )

            elif hasattr(

                self.llm_engine,

                "generate_response",

            ):

                result = (

                    self.llm_engine.generate_response(

                        message=message,

                        analysis=analysis,

                        context=context,

                    )

                )

            elif hasattr(

                self.llm_engine,

                "respond",

            ):

                result = self.llm_engine.respond(

                    message=message,

                    analysis=analysis,

                    context=context,

                )

            else:

                return None

# ------------------------------------------------------------
# Normalize LLM response
# ------------------------------------------------------------
            if isinstance(

                result,

                dict,

            ):

                if result.get(

                    "used_llm"

                ) is False:

                    return None

                reply = (

                    result.get("reply")

                    or result.get("response")

                    or result.get("text")

                )

                if reply:

                    self.last_source = str(

                        result.get(

                            "source",

                            "llm",

                        )

                        or "llm"

                    )

                    self.last_model = (

                        result.get("model")

                    )

            else:

                reply = result

                if reply:

                    self.last_source = "llm"

                    self.last_model = getattr(

                        self.llm_engine,

                        "model_name",

                        None,

                    )

            if not isinstance(

                reply,

                str,

            ):

                return None

            reply = reply.strip()

            if not reply:

                return None

            return reply

        except Exception:

            return None

# =====================================================================
# FALLBACK RESPONSE
# =====================================================================
    def _fallback_response(

        self,

        message: str,

        analysis: Dict[str, Any],

        context: Dict[str, Any],

    ) -> str:

        text = message.lower()

        signals = analysis.get(

            "signals",

            {},

        )

        if not isinstance(signals, dict):

            signals = {}

        state = analysis.get(

            "state",

            {},

        )

        if not isinstance(state, dict):

            state = {}

        topic = (

            state.get("last_topic")

            or analysis.get("topic")

        )

        previous_messages = context.get(

            "recent_user_messages",

            [],

        )

        previous_message = (

            previous_messages[-1]

            if previous_messages

            else ""

        )

# ---------------------------------------------------------------
# Follow-up
# ---------------------------------------------------------------
        if self._is_follow_up(text):

            return self._follow_up_response(

                topic,

                previous_message,

            )

# ---------------------------------------------------------------
# Loneliness
# ---------------------------------------------------------------
        if any(

            phrase in text

            for phrase in (

                "nobody cares",

                "no one cares",

                "left me alone",

                "feel alone",

                "feeling alone",

                "nobody is there",

                "no one is there",

                "feel isolated",

                "so isolated",

                "completely alone",

            )

        ):

            return (

                "That sounds really lonely, especially when you wanted "

                "someone to be there for you. If you're comfortable, "

                "what happened?"

            )

# ---------------------------------------------------------------
# Emotional uncertainty
# ---------------------------------------------------------------
        if any(

            phrase in text

            for phrase in (

                "don't know what i'm feeling",

                "dont know what i'm feeling",

                "don't know what i am feeling",

                "not sure what i'm feeling",

                "can't tell what i'm feeling",

                "cant tell what i'm feeling",

                "confused about how i feel",

                "not sure how i feel",

            )

        ):

            return (

                "That's okay. Sometimes it's hard to put feelings into "

                "words. We can take it slowly—does it feel more like "

                "sadness, stress, loneliness, or something else?"

            )

# ---------------------------------------------------------------
# Anger toward friend
# ---------------------------------------------------------------
        if any(

            phrase in text

            for phrase in (

                "angry at my friend",

                "angry with my friend",

                "mad at my friend",

                "mad with my friend",

                "friend made me angry",

            )

        ):

            return (

                "It sounds like something your friend did really upset "

                "you. If you want to talk about it, what happened?"

            )

# ---------------------------------------------------------------
# Positive mood
# ---------------------------------------------------------------
        if any(

            phrase in text

            for phrase in (

                "happy today",

                "feeling happy",

                "i am happy",

                "i'm happy",

                "good day",

                "feeling great",

                "i feel great",

                "excited today",

            )

        ):

            return (

                "I'm glad to hear that. "

                "What's been making today feel good?"

            )

# ---------------------------------------------------------------
# Safety fallbacks
# ---------------------------------------------------------------
        if (

            signals.get("crisis")

            or signals.get("self_harm")

        ):

            return self._crisis_response()

        if signals.get("hopelessness"):

            return self._hopeless_response(

                topic

            )

        if signals.get("worthlessness"):

            return self._worthlessness_response(

                topic

            )

        if signals.get("sad"):

            return self._sad_response(

                text,

                topic,

            )

        if signals.get("anxiety"):

            return self._anxiety_response(

                topic

            )

        if signals.get("intent"):

            return self._intent_response(

                topic

            )

        if self._is_greeting(text):

            return self._greeting_response()

        if self._is_gratitude(text):

            return self._gratitude_response()

        if analysis.get(

            "mood"

        ) == "positive":

            return self._positive_response(

                topic

            )

        return self._neutral_response(

            topic,

            previous_message,

        )

# =====================================================================
# MESSAGE CLASSIFIERS
# =====================================================================
    def _is_follow_up(

        self,

        text: str,

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

            "explain more",

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

            "what do i do",

        ]

        return any(

            phrase in text

            for phrase in phrases

        )

    def _is_greeting(

        self,

        text: str,

    ) -> bool:

        return text.strip() in {

            "hi",

            "hello",

            "hey",

            "good morning",

            "good afternoon",

            "good evening",

        }

    def _is_gratitude(

        self,

        text: str,

    ) -> bool:

        return any(

            phrase in text

            for phrase in (

                "thank you",

                "thanks",

                "thx",

                "thank u",

            )

        )

# =====================================================================
# TOPIC HELPERS
# =====================================================================
    def _topic_label(

        self,

        topic: Optional[str],

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

            "personal": "your personal situation",

        }

        return labels.get(

            topic,

            "what you're dealing with",

        )

    def _topic_keyword(

        self,

        topic: Optional[str],

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

            "personal": "personal situation",

        }

        return keywords.get(

            topic,

            "situation",

        )

# =====================================================================
# FOLLOW-UP RESPONSE
# =====================================================================
    def _follow_up_response(

        self,

        topic: Optional[str],

        previous_message: str,

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

                "I'm here with you. Let's take it one step at a time. "

                "What feels hardest right now?"

            )

        return (

            "I'm listening. Tell me a little more about "

            "what's been happening."

        )

# =====================================================================
# SAD RESPONSE
# =====================================================================
    def _sad_response(

        self,

        text: str,

        topic: Optional[str],

    ) -> str:

        if (

            "lonely" in text

            or "loneliness" in text

        ):

            return (

                "I'm sorry you're feeling lonely. "

                f"It sounds like your "

                f"{self._topic_keyword(topic)} "

                "situation may be affecting you. "

                "What's been happening?"

            )

        return (

            "I'm sorry you're going through this. "

            f"Let's talk about your "

            f"{self._topic_keyword(topic)} "

            "situation one step at a time. "

            "What has been weighing on you?"

        )

# =====================================================================
# ANXIETY RESPONSE
# =====================================================================
    def _anxiety_response(

        self,

        topic: Optional[str],

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

# =====================================================================
# HOPELESSNESS
# =====================================================================
    def _hopeless_response(

        self,

        topic: Optional[str],

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

# =====================================================================
# WORTHLESSNESS
# =====================================================================
    def _worthlessness_response(

        self,

        topic: Optional[str],

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

# =====================================================================
# INTENT RESPONSE
# =====================================================================
    def _intent_response(

        self,

        topic: Optional[str],

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

# =====================================================================
# GREETING
# =====================================================================
    def _greeting_response(self) -> str:

        return (

            f"Hi {self.user_name}. "

            "I'm here to listen. What's on your mind?"

        )

# =====================================================================
# GRATITUDE
# =====================================================================
    def _gratitude_response(self) -> str:

        return (

            "You're welcome. I'm glad you felt comfortable "

            "sharing that with me."

        )

# =====================================================================
# POSITIVE
# =====================================================================
    def _positive_response(

        self,

        topic: Optional[str],

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

# =====================================================================
# NEUTRAL
# =====================================================================
    def _neutral_response(

        self,

        topic: Optional[str],

        previous_message: str,

    ) -> str:

        if topic == "college":

            return (

                "It sounds like college is on your mind. "

                "Tell me a little more about your exams, studies, "

                "or what's been difficult."

            )

        if topic == "work":

            return (

                "It sounds like work or your career is on your mind. "

                "Tell me a little more about your internship, "

                "interview, or what's been difficult."

            )

        if topic == "future":

            return (

                "It sounds like your future is on your mind. "

                "Tell me a little more about what's been bothering you."

            )

        if topic == "relationships":

            return (

                "It sounds like something in your relationship is "

                "weighing on you. What happened?"

            )

        if topic == "family":

            return (

                "It sounds like something with your family is on your "

                "mind. What happened?"

            )

        if topic:

            return (

                f"It sounds like your "

                f"{self._topic_keyword(topic)} "

                "is on your mind. Tell me a little more about "

                "what's happening."

            )

        if previous_message:

            return (

                "I'm here to listen. Tell me a little more about "

                "what's happening."

            )

        return (

            "I'm here to listen. "

            "Tell me what's on your mind."

        )

# =====================================================================
# SERIOUS
# =====================================================================
    def _serious_response(

        self,

        topic: Optional[str],

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

# =====================================================================
# CRISIS
# =====================================================================
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
