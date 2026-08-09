from typing import Any, Dict, Optional

from app.safety_policy import SafetyPolicy


class SafetyEngine:

    def __init__(self):
        self.policy_engine = SafetyPolicy()

    def analyze(
        self,
        message: str,
        risk_level: str = "low",
        risk_score: float = 0.0,
        signals: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:

        message = self._clean(message)
        signals = signals or {}
        context = context or {}

        policy = self.policy_engine.evaluate(
            risk_level=risk_level,
            signals=signals,
            risk_score=risk_score
        )

        return {
            "message": message,
            "risk_level": policy["risk_level"],
            "risk_score": policy["risk_score"],
            "policy": policy,
            "signals": signals,
            "context": context,
            "requires_human_support": policy[
                "require_human_support"
            ],
            "requires_immediate_guidance": policy[
                "require_immediate_guidance"
            ]
        }

    def build_response(
        self,
        safety_result: Dict[str, Any]
    ) -> Dict[str, Any]:

        policy = safety_result.get(
            "policy",
            {}
        )

        risk_level = policy.get(
            "risk_level",
            "low"
        )

        if risk_level == "high":
            return self._high_risk_response(
                policy
            )

        if risk_level == "moderate":
            return self._moderate_risk_response(
                policy
            )

        return self._low_risk_response(
            policy
        )

    def _high_risk_response(
        self,
        policy: Dict[str, Any]
    ) -> Dict[str, Any]:

        return {
            "risk_level": "high",
            "policy": policy,
            "require_safety_response": True,
            "requires_human_support": True,
            "requires_immediate_guidance": bool(
                policy.get(
                    "require_immediate_guidance",
                    False
                )
            ),
            "emergency_guidance": (
                "If you may act on these thoughts "
                "or you are in immediate danger, "
                "move toward a safe person or place "
                "and contact your local emergency "
                "services or an appropriate crisis service."
            ),
            "human_support_guidance": (
                "Please consider telling someone you "
                "trust and reaching a qualified mental "
                "health professional or crisis service."
            ),
            "do_not": [
                "Do not provide self-harm instructions.",
                "Do not encourage harmful behavior.",
                "Do not minimize the person's distress.",
                "Do not present the system as a replacement for professional care.",
                "Do not make a clinical diagnosis."
            ]
        }

    def _moderate_risk_response(
        self,
        policy: Dict[str, Any]
    ) -> Dict[str, Any]:

        return {
            "risk_level": "moderate",
            "policy": policy,
            "require_safety_response": False,
            "requires_human_support": True,
            "requires_immediate_guidance": False,
            "human_support_guidance": (
                "Consider reaching out to someone you "
                "trust or a qualified mental health "
                "professional if these feelings continue "
                "or become harder to manage."
            ),
            "do_not": [
                "Do not diagnose the person.",
                "Do not minimize distress.",
                "Do not provide harmful instructions."
            ]
        }

    def _low_risk_response(
        self,
        policy: Dict[str, Any]
    ) -> Dict[str, Any]:

        return {
            "risk_level": "low",
            "policy": policy,
            "require_safety_response": False,
            "requires_human_support": False,
            "requires_immediate_guidance": False
        }

    def is_safe_to_continue(
        self,
        safety_result: Dict[str, Any]
    ) -> bool:

        policy = safety_result.get(
            "policy",
            {}
        )

        return bool(
            policy.get(
                "allow_follow_up",
                True
            )
        )

    def should_block_normal_response(
        self,
        safety_result: Dict[str, Any]
    ) -> bool:

        policy = safety_result.get(
            "policy",
            {}
        )

        return not bool(
            policy.get(
                "allow_normal_response",
                False
            )
        )

    def should_require_human_support(
        self,
        safety_result: Dict[str, Any]
    ) -> bool:

        policy = safety_result.get(
            "policy",
            {}
        )

        return bool(
            policy.get(
                "require_human_support",
                False
            )
        )

    def _clean(
        self,
        message: str
    ) -> str:

        if message is None:
            return ""

        return " ".join(
            str(message).strip().split()
        )