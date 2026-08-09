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

    @classmethod
    def is_production(cls):

        return (
            cls.ENVIRONMENT.lower()
            == "production"
        )