from typing import Any, Dict, Optional


class PersonalizationEngine:

    def __init__(self):
        self.default_tone = "supportive"

    def personalize(
        self,
        response: str,
        profile: Optional[Dict[str, Any]] = None,
        topic: Optional[str] = None
    ) -> str:

        response = (response or "").strip()
        profile = profile or {}

        if not response:
            return response

        tone = str(
            profile.get(
                "preferred_tone",
                self.default_tone
            )
        ).lower()

        user_name = profile.get(
            "user_name",
            "friend"
        )

        if tone == "concise":
            response = self._make_concise(
                response
            )

        if tone == "warm":
            response = self._make_warm(
                response,
                user_name
            )

        if topic:
            response = self._topic_adjustment(
                response,
                topic
            )

        return response

    def _make_concise(
        self,
        response: str
    ) -> str:

        sentences = [
            sentence.strip()
            for sentence in response.split(".")
            if sentence.strip()
        ]

        if len(sentences) <= 2:
            return response

        return ". ".join(
            sentences[:2]
        ) + "."

    def _make_warm(
        self,
        response: str,
        user_name: str
    ) -> str:

        if not user_name:
            return response

        if user_name == "friend":
            return response

        if response.lower().startswith(
            user_name.lower()
        ):
            return response

        if len(response) > 180:
            return response

        return (
            f"{user_name}, "
            f"{response[0].lower()}"
            f"{response[1:]}"
        )

    def _topic_adjustment(
        self,
        response: str,
        topic: str
    ) -> str:

        if not response:
            return response

        return response

    def get_tone(
        self,
        profile: Optional[Dict[str, Any]] = None
    ) -> str:

        profile = profile or {}

        return str(
            profile.get(
                "preferred_tone",
                self.default_tone
            )
        ).lower()