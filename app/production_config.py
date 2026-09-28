import os


class ProductionConfig:
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"

    MAX_MESSAGE_LENGTH = max(
        100,
        int(os.getenv("MAX_MESSAGE_LENGTH", "4000")),
    )
    MAX_MEMORY = max(
        1,
        int(os.getenv("MAX_MEMORY", "20")),
    )

    # Session TTL and capacity are intentionally bounded to protect the
    # in-memory service in production.
    SESSION_TTL_SECONDS = max(
        60,
        int(os.getenv("SESSION_TTL_SECONDS", "7200")),
    )
    MAX_SESSIONS = max(
        1,
        int(os.getenv("MAX_SESSIONS", "1000")),
    )

    OPENAI_MODEL = os.getenv(
        "OPENAI_MODEL",
        "gpt-5-mini",
    ).strip() or "gpt-5-mini"

    @classmethod
    def llm_enabled(cls) -> bool:
        configured = os.getenv("ENABLE_LLM")

        if configured is not None:
            explicitly_enabled = configured.strip().lower() in {
                "1",
                "true",
                "yes",
                "on",
            }
            return explicitly_enabled and bool(
                os.getenv("OPENAI_API_KEY", "").strip()
            )

        return bool(os.getenv("OPENAI_API_KEY", "").strip())

    @classmethod
    def is_production(cls) -> bool:
        return cls.ENVIRONMENT.lower() == "production"
