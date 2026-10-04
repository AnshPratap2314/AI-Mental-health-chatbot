import re
import unicodedata
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

    RESPONSE_MODEL_NAME = "mindcare-response-50k"

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
        self.response_model_load_error = None

        # Per-session response history prevents immediate repetition while
        # keeping selection bounded to relevant candidates.
        self._recent_trained_responses = deque(maxlen=8)

        self._load_response_model()

    def _load_response_model(self) -> bool:
        """Load the 50K response model without breaking the main router."""
        if TrainedResponseModel is None:
            self.response_model_load_error = "TrainedResponseModel import unavailable"
            return False

        try:
            self.response_model = TrainedResponseModel()
            self.response_model_load_error = None
            return True
        except Exception as exc:
            # Keep production chat alive, but retain a diagnostic for local
            # verification instead of silently hiding initialization failures.
            self.response_model = None
            self.response_model_load_error = f"{type(exc).__name__}: {exc}"
            return False

# =====================================================================
# MAIN RESPONSE ROUTER
# =====================================================================
    def generate(
        self,
        message,
        analysis,
        context,
    ):
        """Generate a response and apply a mandatory final cleanup boundary."""
        response = self._generate_raw(message, analysis, context)
        return self._finalize_response(response)

    @classmethod
    def _finalize_response(cls, response: Optional[str]) -> Optional[str]:
        """Apply the authoritative final text sanitizer to every response path."""
        if response is None:
            return None

        text = unicodedata.normalize("NFKC", str(response))
        text = re.sub(r"[\u200b-\u200f\u2060\ufeff]", "", text)
        text = cls._clean_response_text(text)

        explicit_repairs = (
            ("orsomething", "or something"),
            ("Orsomething", "Or something"),
            ("ORSOMETHING", "OR SOMETHING"),
            ("isto", "is to"),
            ("Isto", "Is to"),
            ("ISTO", "IS TO"),
            ("immediatedanger", "immediate danger"),
            ("Immediatedanger", "Immediate danger"),
            ("IMMEDIATEDANGER", "IMMEDIATE DANGER"),
            ("practicaloption", "practical option"),
            ("Practicaloption", "Practical option"),
            ("PRACTICALOPTION", "PRACTICAL OPTION"),
            ("worryingyou", "worrying you"),
            ("Worryingyou", "Worrying you"),
            ("whatkind", "what kind"),
            ("Whatkind", "What kind"),
            ("atime", "a time"),
            ("Atime", "A time"),
            ("onestep", "one step"),
            ("Onestep", "One step"),
            ("onesmall", "one small"),
            ("Onesmall", "One small"),
            ("mightreach", "might reach"),
            ("Mightreach", "Might reach"),
            ("mightfind", "might find"),
            ("Mightfind", "Might find"),
            ("togive", "to give"),
            ("Togive", "To give"),
            ("tostart", "to start"),
            ("Tostart", "To start"),
            ("tounderstanding", "to understanding"),
            ("Tounderstanding", "To understanding"),
            ("onunderstanding", "on understanding"),
            ("Onunderstanding", "On understanding"),
        )

        for bad, good in explicit_repairs:
            text = text.replace(bad, good)

        text = re.sub(r"\s+([,.!?;:])", r"\1", text)
        text = re.sub(r"([.!?])(?=[A-Za-z])", r"\1 ", text)
        return " ".join(text.split()).strip()

    def _generate_raw(

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

        if self._is_short_uncertainty(text):

            self.last_source = "fallback"

            self.last_model = None

            return self._uncertainty_response()

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

            return str(trained_reply)

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
        """Select a safe, semantically relevant response from the 50K bank.

        BehaviorEngine owns safety. This method only decides whether a normal
        response-bank example is relevant enough to use.
        """
        if self.response_model is None:
            self._load_response_model()

        model = self.response_model
        if model is None:
            return None

        risk_level = str(analysis.get("risk_level", "low") or "low").lower()
        signals = analysis.get("signals", {})
        if not isinstance(signals, dict):
            signals = {}

        # Never use the normal response bank for authoritative safety cases.
        if (
            risk_level == "high"
            or signals.get("crisis")
            or signals.get("self_harm")
            or signals.get("plan")
            or signals.get("contextual_suicide")
        ):
            return None

        normalized = " ".join(message.lower().strip().split())
        if normalized in {
            "hi", "hii", "hiii", "hello", "helo", "hey", "heyy",
            "heyyy", "hiya", "yo", "hmm", "hmmm", "hm", "umm", "um",
            "uh", "uhh", "idk", "i dk", "idontknow", "i dont know",
            "i don't know", "not sure", "unsure", "no idea",
        }:
            return None

        try:
            metadata = model.predict_metadata(message)
            self.response_model_last_error = None
        except Exception as exc:
            self.response_model_last_error = (
                f"metadata: {type(exc).__name__}: {exc}"
            )
            metadata = {}

        if not isinstance(metadata, dict):
            metadata = {}

        state = analysis.get("state", {})
        if not isinstance(state, dict):
            state = {}

        requested_mood = metadata.get("mood") or analysis.get("mood")
        requested_intent = metadata.get("intent") or analysis.get("intent")
        requested_topic = (
            metadata.get("topic")
            or analysis.get("topic")
            or state.get("last_topic")
        )

        # Generic stress statements should not be forced into a topic such as
        # work merely because the response-model metadata classifier guessed it.
        # Keep the mood signal, but let semantic retrieval determine the topic.
        generic_stress = bool(
            re.search(
                r"\b(?:getting|feeling|feel|am|i'm|im)\s+stressed\b",
                normalized,
            )
        ) or normalized in {
            "i am stressed",
            "im stressed",
            "i'm stressed",
            "i feel stressed",
            "i am getting stressed",
            "im getting stressed",
            "i'm getting stressed",
        }
        if generic_stress:
            requested_intent = analysis.get("intent")
            requested_topic = (
                analysis.get("topic")
                or state.get("last_topic")
            )

        # Explicit low-risk loneliness routing.
        generic_loneliness = bool(
            re.search(
                r"\b(?:feel|feeling|am|i'm|im)\s+(?:very\s+)?lonely\b",
                normalized,
            )
        ) or normalized in {
            "i feel lonely",
            "i'm lonely",
            "im lonely",
            "i am lonely",
            "i feel alone",
            "i am alone",
        }

        if generic_loneliness:
            requested_intent = "loneliness"
            requested_mood = "sad"
            requested_topic = "social"

        # Use the user's exact wording first, plus a canonical stress
        # paraphrase when the wording is colloquial.
        retrieval_queries = [message]
        if generic_loneliness:
            retrieval_queries.append(
                "I feel lonely and alone and wish I had someone to talk to"
            )
        if generic_stress:
            retrieval_queries.append(
                "I feel stressed and overwhelmed and have too much on my mind"
            )

        examples = []
        for retrieval_query in retrieval_queries:
            try:
                found = model.find_examples(
                    message=retrieval_query,
                    risk_level=risk_level,
                    mood=requested_mood,
                    intent=requested_intent,
                    topic=requested_topic,
                    top_k=30,
                )
                self.response_model_last_error = None
            except Exception as exc:
                self.response_model_last_error = (
                    f"retrieval: {type(exc).__name__}: {exc}"
                )
                found = []

            if found:
                examples.extend(found)

        if not examples and generic_loneliness:
            # For this ordinary low-risk intent, recover directly from the
            # already-loaded trained response index before using fallback.
            try:
                index = getattr(model, "index", None)
                records = (
                    index.get("records") or []
                    if isinstance(index, dict)
                    else []
                )
                examples = [
                    item
                    for item in records
                    if isinstance(item, dict)
                    and str(item.get("intent", "")).strip().lower()
                    == "loneliness"
                    and str(item.get("risk_level", "low")).strip().lower()
                    != "high"
                    and str(item.get("response", "")).strip()
                ]
            except Exception as exc:
                self.response_model_last_error = (
                    f"loneliness index recovery: "
                    f"{type(exc).__name__}: {exc}"
                )
                examples = []

        if not examples:
            return None

        # Remove duplicate response texts while preserving retrieval order.
        unique_examples = []
        seen_responses = set()
        for item in examples:
            key = str(item.get("response", "")).strip().casefold()
            if key and key not in seen_responses:
                seen_responses.add(key)
                unique_examples.append(item)
        examples = unique_examples

        # Do not allow a high-risk record to enter the normal response path.
        safe_examples = [
            item
            for item in examples
            if str(item.get("risk_level", "")).strip().lower() != "high"
        ]
        if not safe_examples:
            return None

        if generic_loneliness:
            loneliness_examples = [
                item
                for item in safe_examples
                if str(item.get("intent", "")).strip().lower()
                == "loneliness"
                and str(item.get("response", "")).strip()
            ]
            if loneliness_examples:
                # Prefer a trained response whose wording explicitly anchors
                # the reply to loneliness/being alone/connection/support.
                # This keeps the response semantically faithful to a direct
                # loneliness message instead of selecting a generic emotional
                # response that happens to share the same intent label.
                loneliness_anchors = (
                    "lonely",
                    "alone",
                    "connection",
                    "company",
                    "support",
                )
                anchored_loneliness = [
                    item
                    for item in loneliness_examples
                    if any(
                        anchor in str(item.get("response", "")).lower()
                        for anchor in loneliness_anchors
                    )
                ]
                trained_loneliness = self._select_diverse_trained_response(
                    anchored_loneliness or loneliness_examples
                )
                if trained_loneliness:
                    if not any(
                        anchor in trained_loneliness.lower()
                        for anchor in loneliness_anchors
                    ):
                        trained_loneliness = (
                            "It sounds like you are feeling lonely. "
                            + trained_loneliness
                        )
                    return trained_loneliness

        # For generic stress, prefer a candidate that is not explicitly tied
        # to a topic absent from the user's message.
        if generic_stress:
            neutral_candidates = [
                item for item in safe_examples
                if str(item.get("topic", "")).strip().lower()
                in {"", "general", "personal"}
            ]
            if neutral_candidates:
                safe_examples = neutral_candidates + [
                    item for item in safe_examples
                    if item not in neutral_candidates
                ]

        best = safe_examples[0]
        similarity = float(best.get("similarity", 0.0) or 0.0)
        retrieval_score = float(
            best.get("retrieval_score", similarity) or similarity
        )
        matches = set(best.get("metadata_matches", []) or [])
        phrase_hint = bool(best.get("phrase_hint", False))

        # Similarity remains the hard relevance floor. A phrase hint plus a
        # matching mood is sufficient for ordinary low-risk emotional input.
        semantic_floor = 0.18 if phrase_hint else 0.20
        if similarity < semantic_floor:
            return None

        accepted = (
            similarity >= 0.34
            or ("intent" in matches and similarity >= 0.20)
            or (
                phrase_hint
                and (
                    "intent" in matches
                    or "topic" in matches
                    or "mood" in matches
                )
                and similarity >= 0.24
            )
            or retrieval_score >= 0.42
        )
        if not accepted:
            return None

        similarity_window = max(0.16, similarity - 0.16)
        eligible_examples = [
            item
            for item in safe_examples
            if float(item.get("similarity", 0.0) or 0.0)
            >= similarity_window
        ]

        return self._select_diverse_trained_response(
            eligible_examples or [best]
        )

    def _select_diverse_trained_response(
        self,
        examples,
    ) -> Optional[str]:
        """Select a relevant response while avoiding immediate repetition."""
        if not examples:
            return None

        recent = {
            self._clean_response_text(str(item)).casefold()
            for item in self._recent_trained_responses
        }

        eligible = []
        for item in examples:
            response = str(item.get("response", "") or "").strip()
            if not response:
                continue
            if len(response) < 12 or len(response) > 700:
                continue

            cleaned = self._clean_response_text(response)
            lowered = cleaned.casefold()

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

            if len(cleaned) < 12:
                continue

            eligible.append((item, cleaned))

        if not eligible:
            return None

        for _, response in eligible:
            if response.casefold() not in recent:
                self._recent_trained_responses.append(response)
                return response

        # If every candidate was recently used, repeat the strongest eligible
        # candidate rather than returning an uncleaned response.
        response = eligible[0][1]
        self._recent_trained_responses.append(response)
        return response

    @staticmethod
    def _clean_response_text(response: str) -> str:
        """Normalize response-bank token-boundary and grammar artifacts."""
        text = unicodedata.normalize("NFKC", str(response or ""))
        text = re.sub(r"[\u200b-\u200f\u2060\ufeff]", "", text)
        text = " ".join(text.split()).strip()

        explicit_repairs = (
            ("orsomething", "or something"),
            ("Orsomething", "Or something"),
            ("ORSOMETHING", "OR SOMETHING"),
            ("isto", "is to"),
            ("Isto", "Is to"),
            ("ISTO", "IS TO"),
            ("immediatedanger", "immediate danger"),
            ("Immediatedanger", "Immediate danger"),
            ("IMMEDIATEDANGER", "IMMEDIATE DANGER"),
            ("practicaloption", "practical option"),
            ("Practicaloption", "Practical option"),
            ("PRACTICALOPTION", "PRACTICAL OPTION"),
            ("worryingyou", "worrying you"),
            ("Worryingyou", "Worrying you"),
            ("whatkind", "what kind"),
            ("Whatkind", "What kind"),
            ("atime", "a time"),
            ("Atime", "A time"),
            ("onestep", "one step"),
            ("Onestep", "One step"),
            ("onesmall", "one small"),
            ("Onesmall", "One small"),
            ("mightreach", "might reach"),
            ("Mightreach", "Might reach"),
            ("mightfind", "might find"),
            ("Mightfind", "Might find"),
            ("togive", "to give"),
            ("Togive", "To give"),
            ("tostart", "to start"),
            ("Tostart", "To start"),
            ("tounderstanding", "to understanding"),
            ("Tounderstanding", "To understanding"),
            ("onunderstanding", "on understanding"),
            ("Onunderstanding", "On understanding"),
        )

        for bad, good in explicit_repairs:
            text = text.replace(bad, good)

        grammar_replacements = (
            (r"\bsituation\s+situation\b", "situation"),
            (r"\byou\s+are\s+wanting\b", "you want"),
            (r"\bconsider\s+take\b", "consider taking"),
            (r"\bconsider\s+write\b", "consider writing"),
            (r"\bconsider\s+separate\b", "consider separating"),
            (r"\bconsider\s+give\b", "consider giving"),
            (r"\bconsider\s+focus\b", "consider focusing"),
            (r"\bfocus\s+onunderstanding\b", "focus on understanding"),
        )

        for pattern, replacement in grammar_replacements:
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)

        text = re.sub(r"\s+([,.!?;:])", r"\1", text)
        text = re.sub(r"([.!?])(?=[A-Za-z])", r"\1 ", text)
        return " ".join(text.split()).strip()

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

        normalized = " ".join(text.strip().lower().split())

        return normalized in {

            "hi",

            "hii",

            "hiii",

            "hello",

            "helo",

            "hey",

            "heyy",

            "heyyy",

            "hiya",

            "yo",

            "good morning",

            "good afternoon",

            "good evening",

        }

    def _is_short_uncertainty(

        self,

        text: str,

    ) -> bool:

        normalized = " ".join(text.strip().lower().split())

        return normalized in {

            "idk",

            "i dk",

            "idontknow",

            "i dont know",

            "i don't know",

            "dont know",

            "don't know",

            "not sure",

            "unsure",

            "no idea",

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
    def _uncertainty_response(self) -> str:

        return (

            "That's okay. You don't have to have everything figured out "

            "right now. What part feels unclear?"

        )

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

