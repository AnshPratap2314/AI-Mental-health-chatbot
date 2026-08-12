from typing import Any, Dict, Optional


class SafetyResources:
    """
    Provides real, verifiable crisis and support contact information.

    IMPORTANT: Helpline numbers change over time. The numbers below were
    verified as of the time this module was written. Whoever maintains
    this project should periodically re-verify them (e.g. against
    https://findahelpline.com) since giving someone a dead number during
    a crisis is worse than giving no number at all.
    """

    def __init__(self):
        self.resources = {
            "default": {
                "emergency": (
                    "If you are in immediate physical danger, contact your "
                    "local emergency number right away."
                ),
                "immediate_danger": (
                    "If you are in immediate physical danger, contact your "
                    "local emergency number right away."
                ),
                "crisis_line": (
                    "Find A Helpline (findahelpline.com) lists free, "
                    "confidential crisis lines for your country, available "
                    "24/7 in most regions."
                ),
                "trusted_person": (
                    "If you can, reach out to a trusted friend, family "
                    "member, or anyone nearby who can stay with you right now."
                ),
                "professional": (
                    "A doctor, therapist, or counselor can help you make a "
                    "plan for ongoing support, not just this moment."
                ),
            },
            "india": {
                "emergency": (
                    "If you are in immediate physical danger, call 112 "
                    "(India's national emergency number)."
                ),
                "immediate_danger": (
                    "If you are in immediate physical danger, call 112 "
                    "(India's national emergency number)."
                ),
                "crisis_line": (
                    "Tele-MANAS — India's free, 24/7 government mental "
                    "health helpline: call 14416 or 1800-89-14416. "
                    "Available in English, Hindi, and 18+ regional languages."
                ),
                "additional_lines": (
                    "Vandrevala Foundation: 1860-2662-345 (24/7). "
                    "iCall (TISS): 9152987821 (Mon-Sat, 10am-8pm). "
                    "AASRA: 9820466726 (24/7)."
                ),
                "trusted_person": (
                    "If you can, reach out to a trusted friend, family "
                    "member, or anyone nearby who can stay with you right now."
                ),
                "professional": (
                    "A doctor, therapist, or counselor can help you make a "
                    "plan for ongoing support, not just this moment."
                ),
            },
            "us": {
                "emergency": (
                    "If you are in immediate physical danger, call 911."
                ),
                "immediate_danger": (
                    "If you are in immediate physical danger, call 911."
                ),
                "crisis_line": (
                    "988 Suicide & Crisis Lifeline — call or text 988, "
                    "free and available 24/7 across the US."
                ),
                "trusted_person": (
                    "If you can, reach out to a trusted friend, family "
                    "member, or anyone nearby who can stay with you right now."
                ),
                "professional": (
                    "A doctor, therapist, or counselor can help you make a "
                    "plan for ongoing support, not just this moment."
                ),
            },
        }

    def get(
        self,
        country: Optional[str] = None
    ) -> Dict[str, str]:

        key = str(
            country or "default"
        ).lower()

        return dict(
            self.resources.get(
                key,
                self.resources["default"]
            )
        )

    def build_crisis_guidance(
        self,
        country: Optional[str] = None
    ) -> Dict[str, Any]:

        resources = self.get(country)

        return {
            "resources": resources,
            "steps": [
                "Move to a safer place if you can.",
                "Reach out to or stay with a trusted person right now.",
                "Call one of the crisis lines above, or your local "
                "emergency number if you may be in immediate danger.",
            ],
        }

    def format_for_reply(
        self,
        country: Optional[str] = None
    ) -> str:
        """
        Human-readable, chat-friendly version of the crisis resources,
        meant to be inserted directly into a reply to the user.
        """

        resources = self.get(country)

        lines = []

        if "crisis_line" in resources:
            lines.append(resources["crisis_line"])

        if "additional_lines" in resources:
            lines.append(resources["additional_lines"])

        if "immediate_danger" in resources:
            lines.append(resources["immediate_danger"])

        return " ".join(lines)
