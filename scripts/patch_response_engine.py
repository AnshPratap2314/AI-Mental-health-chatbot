from pathlib import Path


path = Path("app/response_engine.py")
backup = Path("app/response_engine.py.before_trained_response")

# Always start from the original clean ResponseEngine.
if backup.exists():
    text = backup.read_text(encoding="utf-8")
else:
    text = path.read_text(encoding="utf-8")
    backup.write_text(text, encoding="utf-8")


# ============================================================
# 1. Import trained response model
# ============================================================

import_marker = "from typing import Any, Dict, Optional\n"

import_block = """
try:
    from app.response_model import TrainedResponseModel
except ImportError:
    TrainedResponseModel = None

"""

if "from app.response_model import TrainedResponseModel" not in text:
    text = text.replace(
        import_marker,
        import_marker + import_block,
        1,
    )


# ============================================================
# 2. Initialize model + metadata
# ============================================================

init_marker = """        self.user_name = user_name or "friend"
        self.llm_engine = llm_engine
"""

init_block = """        self.user_name = user_name or "friend"
        self.llm_engine = llm_engine

        self.response_model = None
        self.last_source = "fallback"
        self.last_model = None

        if TrainedResponseModel is not None:
            try:
                self.response_model = TrainedResponseModel(
                    top_k=3
                )
                self.last_model = "mindcare-response-10k"
            except Exception:
                self.response_model = None
                self.last_model = None
"""

if "self.response_model = None" not in text:
    if init_marker not in text:
        raise SystemExit(
            "Could not find ResponseEngine.__init__."
        )

    text = text.replace(
        init_marker,
        init_block,
        1,
    )


# ============================================================
# 3. Replace normal response path
# ============================================================

old_path = """        if self.llm_engine is not None:
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
"""

new_path = """        # --------------------------------------------------------
        # Deterministic conversation rules MUST remain authoritative
        # for greetings, gratitude and follow-up/context messages.
        # --------------------------------------------------------

        if self._is_follow_up(text):
            self.last_source = "deterministic"
            self.last_model = None

            return self._follow_up_response(
                topic,
                self._previous_message(context)
            )

        if self._is_greeting(text):
            self.last_source = "deterministic"
            self.last_model = None

            return self._greeting_response()

        if self._is_gratitude(text):
            self.last_source = "deterministic"
            self.last_model = None

            return self._gratitude_response()

        # --------------------------------------------------------
        # Existing deterministic emotional/context responses.
        # These should not be replaced by generic retrieved text.
        # --------------------------------------------------------

        if signals.get("hopelessness"):
            self.last_source = "deterministic"
            self.last_model = None
            return self._hopeless_response(topic)

        if signals.get("worthlessness"):
            self.last_source = "deterministic"
            self.last_model = None
            return self._worthlessness_response(topic)

        if signals.get("sad"):
            self.last_source = "deterministic"
            self.last_model = None
            return self._sad_response(
                text,
                topic
            )

        if signals.get("anxiety"):
            self.last_source = "deterministic"
            self.last_model = None
            return self._anxiety_response(topic)

        if signals.get("intent"):
            self.last_source = "deterministic"
            self.last_model = None
            return self._intent_response(topic)

        # --------------------------------------------------------
        # Trained retrieval
        # --------------------------------------------------------

        trained_examples = self._retrieve_trained_examples(
            message,
            analysis,
            context,
        )

        enriched_context = dict(context)

        if trained_examples:
            enriched_context["response_examples"] = (
                trained_examples
            )

            enriched_context["response_model_context"] = (
                self._format_trained_examples(
                    trained_examples
                )
            )

        # --------------------------------------------------------
        # LLM
        # --------------------------------------------------------

        if self.llm_engine is not None:
            llm_reply = self._try_llm(
                message,
                analysis,
                enriched_context
            )

            if llm_reply:
                self.last_source = "llm"
                return llm_reply

        # --------------------------------------------------------
        # Trained response fallback
        # --------------------------------------------------------

        trained_response = self._select_trained_response(
            trained_examples,
            message,
            analysis,
        )

        if trained_response:
            self.last_source = "trained_response_model"
            self.last_model = "mindcare-response-10k"

            return trained_response

        # --------------------------------------------------------
        # Existing fallback
        # --------------------------------------------------------

        self.last_source = "fallback"
        self.last_model = None

        return self._fallback_response(
            message,
            analysis,
            enriched_context
        )
"""

if old_path not in text:
    raise SystemExit(
        "Could not find the normal ResponseEngine path."
    )

text = text.replace(
    old_path,
    new_path,
    1,
)


# ============================================================
# 4. Add previous-message helper
# ============================================================

helper_marker = """    def _is_follow_up(
"""

helper = """    @staticmethod
    def _previous_message(context):
        context = context or {}

        messages = context.get(
            "recent_user_messages",
            []
        )

        if messages:
            return str(messages[-1])

        return ""

"""

if "def _previous_message(" not in text:
    text = text.replace(
        helper_marker,
        helper + helper_marker,
        1,
    )


# ============================================================
# 5. Trained retrieval helper
# ============================================================

retrieval_marker = """    def _try_llm(
"""

retrieval_helpers = """    def _retrieve_trained_examples(
        self,
        message: str,
        analysis: Dict[str, Any],
        context: Dict[str, Any],
    ):
        if self.response_model is None:
            return []

        risk_level = str(
            analysis.get(
                "risk_level",
                "low"
            )
            or "low"
        ).lower()

        signals = analysis.get(
            "signals",
            {}
        ) or {}

        # Absolute safety boundary.
        if (
            risk_level == "high"
            or signals.get("crisis")
            or signals.get("self_harm")
        ):
            return []

        state = analysis.get(
            "state",
            {}
        ) or {}

        mood = (
            analysis.get("mood")
            or state.get("current_mood")
        )

        topic = (
            analysis.get("topic")
            or state.get("last_topic")
        )

        intent = analysis.get(
            "intent"
        )

        try:
            return self.response_model.find_examples(
                message=message,
                risk_level=risk_level,
                mood=mood,
                topic=topic,
                intent=intent,
                top_k=3,
            )
        except Exception:
            return []

    @staticmethod
    def _format_trained_examples(
        examples
    ) -> str:

        if not examples:
            return ""

        lines = [
            "Relevant examples from the MindCare "
            "trained response model:",
            (
                "Use these examples only as guidance. "
                "Write a fresh response specific to "
                "the current user."
            ),
            ""
        ]

        for index, item in enumerate(
            examples,
            1
        ):
            lines.extend([
                f"Example {index}:",
                f"User pattern: {item.get('message', '')}",
                f"Response: {item.get('response', '')}",
                f"Intent: {item.get('intent', '')}",
                f"Mood: {item.get('mood', '')}",
                f"Topic: {item.get('topic', '')}",
                f"Similarity: {item.get('similarity', '')}",
                f"Score: {item.get('retrieval_score', '')}",
                "",
            ])

        return "\\n".join(lines)

    def _select_trained_response(
        self,
        examples,
        message: str,
        analysis: Dict[str, Any],
    ) -> Optional[str]:

        if not examples:
            return None

        risk_level = str(
            analysis.get(
                "risk_level",
                "low"
            )
            or "low"
        ).lower()

        if risk_level == "high":
            return None

        for item in examples:

            if not isinstance(
                item,
                dict
            ):
                continue

            if str(
                item.get(
                    "risk_level",
                    ""
                )
            ).lower() == "high":
                continue

            response = item.get(
                "response"
            )

            if (
                isinstance(
                    response,
                    str
                )
                and response.strip()
            ):
                return response.strip()

        return None

"""

if "def _retrieve_trained_examples(" not in text:
    if retrieval_marker not in text:
        raise SystemExit(
            "Could not find _try_llm()."
        )

    text = text.replace(
        retrieval_marker,
        retrieval_helpers + retrieval_marker,
        1,
    )


# ============================================================
# 6. Make disabled LLM really disabled
# ============================================================

old_llm_result = """            if isinstance(result, dict):
                reply = (
                    result.get("reply")
                    or result.get("response")
                    or result.get("text")
                )
            else:
                reply = result
"""

new_llm_result = """            if isinstance(result, dict):

                # LLMEngine may return a fallback response when
                # it is disabled. That must NOT be reported as
                # an LLM-generated response.
                if result.get("used_llm") is False:
                    return None

                if result.get("source") not in (
                    None,
                    "llm"
                ):
                    return None

                reply = (
                    result.get("reply")
                    or result.get("response")
                    or result.get("text")
                )

            else:
                reply = result
"""

if old_llm_result in text:
    text = text.replace(
        old_llm_result,
        new_llm_result,
        1,
    )


# ============================================================
# 7. Write result
# ============================================================

path.write_text(
    text,
    encoding="utf-8"
)

print("ResponseEngine patched successfully.")
print("Backup preserved at:", backup)