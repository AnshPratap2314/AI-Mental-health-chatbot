import os


class ProductionConfig:
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"
    MAX_MESSAGE_LENGTH = max(100, int(os.getenv("MAX_MESSAGE_LENGTH", "4000")))
    MAX_MEMORY = max(1, int(os.getenv("MAX_MEMORY", "20")))
    SESSION_TTL_SECONDS = max(60, int(os.getenv("SESSION_TTL_SECONDS", "1800")))
    MAX_SESSIONS = max(1, int(os.getenv("MAX_SESSIONS", "1000")))
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5-mini")

    @classmethod
    def llm_enabled(cls) -> bool:
        configured = os.getenv("ENABLE_LLM")
        if configured is not None:
            return configured.lower() in {"1", "true", "yes", "on"}
        return bool(os.getenv("OPENAI_API_KEY", "").strip())

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
        return cls.ENVIRONMENT.lower() == "production"
