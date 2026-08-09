from typing import Any, Dict, Optional


class CrisisManager:

    def __init__(self):
        self.default_action = "supportive_conversation"

    def evaluate(
        self,
        risk_level: str,
        signals: Optional[Dict[str, Any]] = None,
        safety_policy: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:

        signals = signals or {}
        safety_policy = safety_policy or {}

        risk = str(
            risk_level or "low"
        ).lower()

        crisis = bool(
            signals.get("crisis")
            or safety_policy.get("crisis_detected")
        )

        self_harm = bool(
            signals.get("self_harm")
            or safety_policy.get("self_harm_detected")
        )

        intent = bool(
            signals.get("intent")
            or safety_policy.get("intent_detected")
        )

        temporal = bool(
            signals.get("temporal")
            or safety_policy.get("temporal_signal")
        )

        protective = bool(
            signals.get("protective")
            or safety_policy.get("protective_signal")
        )

        if protective and not intent and not temporal:
            if risk == "high":
                risk = "moderate"

        immediate = (
            risk == "high"
            and (
                crisis
                or self_harm
                or intent
                or temporal
            )
        )

        if immediate:
            action = "immediate_human_support"
            mode = "crisis"
        elif risk == "high":
            action = "human_support"
            mode = "safety"
        elif risk == "moderate":
            action = "encourage_human_support"
            mode = "support"
        else:
            action = "supportive_conversation"
            mode = "normal"

        return {
            "risk_level": risk,
            "crisis_detected": crisis,
            "self_harm_detected": self_harm,
            "intent_detected": intent,
            "temporal_signal": temporal,
            "protective_signal": protective,
            "immediate_guidance": immediate,
            "action": action,
            "mode": mode,
            "llm_allowed": not immediate and risk != "high",
            "normal_response_allowed": risk != "high"
        }

    def requires_escalation(
        self,
        result: Dict[str, Any]
    ) -> bool:

        return bool(
            result.get("immediate_guidance")
            or result.get("risk_level") == "high"
        )

    def crisis_response_required(
        self,
        result: Dict[str, Any]
    ) -> bool:

        return bool(
            result.get("mode") == "crisis"
        )