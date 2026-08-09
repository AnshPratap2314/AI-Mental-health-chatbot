from typing import Dict, List


class ContextEngine:

    def __init__(self, max_context_messages: int = 3):
        self.max_context_messages = max_context_messages

    def get_recent_user_messages(
        self,
        history: List[Dict[str, str]]
    ) -> List[str]:

        recent = history[
            -self.max_context_messages:
        ]

        return [
            item.get("user", "")
            for item in recent
        ]

    def build_context(
        self,
        history: List[Dict[str, str]]
    ) -> str:

        recent = history[
            -self.max_context_messages:
        ]

        if not recent:
            return ""

        parts = []

        for item in recent:

            parts.append(
                f"User: {item.get('user', '')}"
            )

            parts.append(
                f"Bot: {item.get('bot', '')}"
            )

        return "\n".join(parts)

    def analyze_context(
        self,
        history: List[Dict[str, str]]
    ) -> Dict:

        recent_messages = self.get_recent_user_messages(
            history
        )

        return {
            "message_count": len(recent_messages),
            "has_previous_context": len(recent_messages) > 0,
            "recent_user_messages": recent_messages
        }

    def has_previous_signal(
        self,
        history: List[Dict[str, str]],
        keywords: List[str]
    ) -> bool:

        recent_messages = self.get_recent_user_messages(
            history
        )

        combined_text = " ".join(
            recent_messages
        ).lower()

        return any(
            keyword.lower() in combined_text
            for keyword in keywords
        )

    def context_risk_boost(
        self,
        history: List[Dict[str, str]]
    ) -> float:

        boost = 0.0

        if self.has_previous_signal(
            history,
            [
                "hopeless",
                "helpless",
                "worthless",
                "can't handle",
                "cannot handle",
                "can't cope",
                "cannot cope"
            ]
        ):
            boost += 0.10

        return min(
            boost,
            0.20
        )