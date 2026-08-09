import os
import secrets


class SecurityManager:

    def __init__(
        self,
        max_message_length=4000
    ):
        self.max_message_length = max(
            1,
            int(max_message_length)
        )

    def validate_message(
        self,
        message: str
    ) -> bool:

        if not isinstance(
            message,
            str
        ):
            return False

        value = message.strip()

        if not value:
            return False

        if len(value) > self.max_message_length:
            return False

        return True

    def sanitize_message(
        self,
        message: str
    ) -> str:

        if not isinstance(
            message,
            str
        ):
            return ""

        return message.strip()

    def generate_session_token(self) -> str:

        return secrets.token_urlsafe(32)

    def api_key_configured(self) -> bool:

        value = os.getenv(
            "OPENAI_API_KEY",
            ""
        ).strip()

        return bool(
            value
            and value != "your_api_key_here"
        )

    def is_safe_environment(self) -> bool:

        return True