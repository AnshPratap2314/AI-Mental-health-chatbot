from typing import Any, Dict, Optional


class SafetyPolicy:

    PRIORITY = {
        "low": "normal",
        "moderate": "elevated",
        "high": "critical"
    }

    def evaluate(
        self,
        risk_level: str,
        signals: Optional[Dict[str, Any]] = None,
        risk_score: float = 0.0
    ) -> Dict[str, Any]:

        signals = signals or {}

        risk_level = str(
            risk_level or "low"
        ).lower()

        if risk_level not in {
            "low",
            "moderate",
            "high"
        }:
            risk_level = "low"

        crisis = bool(
            signals.get("crisis")
        )

        self_harm = bool(
            signals.get("self_harm")
        )

        intent = bool(
            signals.get("intent")
        )

        temporal = bool(
            signals.get("temporal")
        )

        protective = bool(
            signals.get("protective")
        )

        contextual = bool(
            signals.get("contextual_suicide")
        )

        if contextual:
            risk_level = "low"
            risk_score = 0.0
            crisis = False
            self_harm = False
            intent = False
            temporal = False

        immediate_guidance = bool(
            risk_level == "high"
            and (
                crisis
                or self_harm
                or temporal
                or intent
            )
        )

        require_safety_response = (
            risk_level == "high"
        )

        require_human_support = (
            risk_level in {
                "moderate",
                "high"
            }
        )

        allow_normal_response = (
            risk_level != "high"
        )

        allow_random_response = False
        allow_follow_up = True

        if risk_level == "high":
            priority = "critical"
        elif risk_level == "moderate":
            priority = "elevated"
        else:
            priority = "normal"

        if immediate_guidance:
            action = "immediate_human_support"
        elif require_human_support:
            action = "encourage_human_support"
        else:
            action = "supportive_conversation"

        return {
            "risk_level": risk_level,
            "risk_score": round(
                max(
                    0.0,
                    min(
                        float(risk_score),
                        1.0
                    )
                ),
                3
            ),
            "priority": priority,
            "action": action,
            "require_safety_response": require_safety_response,
            "allow_random_response": allow_random_response,
            "allow_normal_response": allow_normal_response,
            "require_human_support": require_human_support,
            "require_immediate_guidance": immediate_guidance,
            "allow_follow_up": allow_follow_up,
            "crisis_detected": crisis,
            "self_harm_detected": self_harm,
            "intent_detected": intent,
            "temporal_signal": temporal,
            "protective_signal": protective,
            "contextual_reference": contextual
        }

    def is_crisis(
        self,
        policy: Dict[str, Any]
    ) -> bool:

        return bool(
            policy.get("risk_level") == "high"
            and (
                policy.get("crisis_detected")
                or policy.get("self_harm_detected")
            )
        )

    def requires_human_support(
        self,
        policy: Dict[str, Any]
    ) -> bool:

        return bool(
            policy.get(
                "require_human_support",
                False
            )
        )

    def requires_immediate_guidance(
        self,
        policy: Dict[str, Any]
    ) -> bool:

        return bool(
            policy.get(
                "require_immediate_guidance",
                False
            )
        )

    def allows_normal_response(
        self,
        policy: Dict[str, Any]
    ) -> bool:

        return bool(
            policy.get(
                "allow_normal_response",
                False
            )
        )