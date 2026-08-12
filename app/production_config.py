import os


class ProductionConfig:

    ENVIRONMENT = os.getenv(
        "ENVIRONMENT",
        "development"
    )

    DEBUG = os.getenv(
        "DEBUG",
        "false"
    ).lower() == "true"

    MAX_MESSAGE_LENGTH = int(
        os.getenv(
            "MAX_MESSAGE_LENGTH",
            "4000"
        )
    )

    MAX_MEMORY = int(
        os.getenv(
            "MAX_MEMORY",
            "20"
        )
    )

    OPENAI_MODEL = os.getenv(
        "OPENAI_MODEL",
        "gpt-5-mini"
    )

    ENABLE_LLM = os.getenv(
        "ENABLE_LLM",
        "false"
    ).lower() == "true"

    # How long (seconds) an idle session is kept before eviction.
    # Default: 2 hours. Set to 0 to disable TTL-based eviction.
    SESSION_TTL_SECONDS = int(
        os.getenv(
            "SESSION_TTL_SECONDS",
            "7200"
        )
    )

    # Max simultaneous in-memory sessions before the oldest are evicted.
    # Set to 0 to disable the cap.
    MAX_SESSIONS = int(
        os.getenv(
            "MAX_SESSIONS",
            "1000"
        )
    )

    @classmethod
    def is_production(cls):

        return (
            cls.ENVIRONMENT.lower()
            == "production"
        )