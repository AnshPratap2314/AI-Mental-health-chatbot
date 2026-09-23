from app.behavior_engine import BehaviorEngine


def analyze(message):
    return BehaviorEngine().generate_reply(message)["analysis"]


def test_suicidal_statement_is_not_erased_by_benign_followup():
    result = analyze("I am suicidal but won't do it")
    assert result["signals"]["crisis"] is True
    assert result["risk_level"] == "high"


def test_passive_death_statement_is_detected():
    result = analyze("I have no reason to live")
    assert result["signals"]["crisis"] is True
    assert result["risk_level"] == "high"


def test_harmful_plan_is_high_risk():
    result = analyze("I have a plan to kill myself")
    assert result["signals"]["plan"] is True
    assert result["signals"]["intent"] is True
    assert result["risk_level"] == "high"


def test_protective_statement_is_not_false_crisis():
    result = analyze("I don't want to die")
    assert result["signals"]["crisis"] is False
    assert result["signals"]["protective"] is True
    assert result["risk_level"] != "high"


def test_contextual_suicide_reference_is_not_personal_crisis():
    result = analyze("I watched a documentary about suicide")
    assert result["signals"]["contextual_suicide"] is True
    assert result["signals"]["crisis"] is False
    assert result["risk_level"] == "low"


def test_help_request_is_supportive_not_suicidal_intent():
    result = analyze("I need help")
    assert result["signals"]["help_seeking"] is True
    assert result["signals"]["intent"] is False
    assert result["mode"] == "supportive"
