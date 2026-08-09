from app.crisis_manager import CrisisManager
from app.safety_resources import SafetyResources
from app.safety_audit import SafetyAudit
from app.user_profile import UserProfile
from app.personalization_engine import PersonalizationEngine
from app.privacy_manager import PrivacyManager
from app.security import SecurityManager
from app.health import HealthManager
from app.production_config import ProductionConfig


def test_crisis_manager_low_risk():
    manager = CrisisManager()

    result = manager.evaluate(
        "low",
        {}
    )

    assert result["mode"] == "normal"
    assert result["llm_allowed"] is True


def test_crisis_manager_high_risk():
    manager = CrisisManager()

    result = manager.evaluate(
        "high",
        {
            "crisis": True
        }
    )

    assert result["mode"] == "crisis"
    assert result["immediate_guidance"] is True
    assert result["llm_allowed"] is False


def test_crisis_manager_self_harm():
    manager = CrisisManager()

    result = manager.evaluate(
        "high",
        {
            "self_harm": True
        }
    )

    assert result["mode"] == "crisis"


def test_protective_signal():
    manager = CrisisManager()

    result = manager.evaluate(
        "high",
        {
            "protective": True
        }
    )

    assert result["risk_level"] == "moderate"


def test_safety_resources():
    resources = SafetyResources()

    result = resources.get()

    assert "emergency" in result
    assert "trusted_person" in result
    assert "professional" in result


def test_safety_audit():
    audit = SafetyAudit()

    audit.record(
        "high",
        "immediate_human_support",
        "crisis",
        {
            "crisis": True
        }
    )

    assert audit.count() == 1
    assert audit.get_records()[0]["risk_level"] == "high"


def test_user_profile():
    profile = UserProfile(
        "Ansh"
    )

    profile.update(
        tone="warm"
    )

    profile.add_topic(
        "college"
    )

    profile.add_mood(
        "anxious"
    )

    data = profile.get()

    assert data["user_name"] == "Ansh"
    assert data["preferred_tone"] == "warm"
    assert "college" in data["topic_history"]
    assert "anxious" in data["mood_history"]


def test_personalization():
    engine = PersonalizationEngine()

    result = engine.personalize(
        "I'm here to listen.",
        {
            "user_name": "Ansh",
            "preferred_tone": "warm"
        }
    )

    assert result


def test_privacy_email():
    manager = PrivacyManager()

    result = manager.sanitize_text(
        "My email is test@example.com"
    )

    assert "test@example.com" not in result
    assert "[REDACTED]" in result


def test_privacy_api_key():
    manager = PrivacyManager()

    result = manager.sanitize_text(
        "api_key=secret123"
    )

    assert "secret123" not in result


def test_identifier_hash():
    manager = PrivacyManager()

    result = manager.hash_identifier(
        "session-123"
    )

    assert len(result) == 64


def test_security_message():
    security = SecurityManager()

    assert security.validate_message(
        "Hello"
    ) is True


def test_security_empty_message():
    security = SecurityManager()

    assert security.validate_message(
        ""
    ) is False


def test_security_long_message():
    security = SecurityManager(
        max_message_length=10
    )

    assert security.validate_message(
        "a" * 100
    ) is False


def test_session_token():
    security = SecurityManager()

    token = security.generate_session_token()

    assert isinstance(
        token,
        str
    )

    assert len(token) > 20


def test_health_manager():
    health = HealthManager()

    result = health.check()

    assert result["status"] == "healthy"


def test_production_config():
    assert ProductionConfig.MAX_MESSAGE_LENGTH > 0
    assert ProductionConfig.MAX_MEMORY > 0