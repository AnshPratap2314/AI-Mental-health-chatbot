from typing import Any, Dict, Optional

# Default, verified as of the time this was written. Re-check periodically
# against https://findahelpline.com since helpline numbers can change.
_DEFAULT_EMERGENCY_NUMBER = "112"
_DEFAULT_CRISIS_NUMBER = "14416 (Tele-MANAS, 24/7 free govt. helpline)"


class SafetySupport:

    def __init__(
        self,
        country: Optional[str] = None,
        emergency_number: Optional[str] = None,
        crisis_number: Optional[str] = None
    ):
        self.country = (country or "").strip()
        self.emergency_number = emergency_number or _DEFAULT_EMERGENCY_NUMBER
        self.crisis_number = crisis_number or _DEFAULT_CRISIS_NUMBER

    def build_support(
        self,
        risk_level: str,
        policy: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:

        risk_level = str(
            risk_level or "low"
        ).lower()

        policy = policy or {}

        if risk_level == "high":
            return self._high_support(policy)

        if risk_level == "moderate":
            return self._moderate_support(policy)

        return self._low_support()

    def _low_support(self) -> Dict[str, Any]:
        return {
            "level": "normal",
            "title": "Supportive conversation",
            "action": "continue_conversation",
            "human_support": False,
            "immediate_guidance": False,
            "resources": []
        }

    def _moderate_support(
        self,
        policy: Dict[str, Any]
    ) -> Dict[str, Any]:

        return {
            "level": "elevated",
            "title": "Additional support may help",
            "action": "encourage_human_support",
            "human_support": True,
            "immediate_guidance": bool(
                policy.get(
                    "require_immediate_guidance",
                    False
                )
            ),
            "resources": self._resources()
        }

    def _high_support(
        self,
        policy: Dict[str, Any]
    ) -> Dict[str, Any]:

        return {
            "level": "critical",
            "title": "Immediate safety support",
            "action": "immediate_human_support",
            "human_support": True,
            "immediate_guidance": True,
            "resources": self._resources()
        }

    def _resources(self):
        resources = []

        if self.emergency_number:
            resources.append({
                "type": "emergency",
                "number": self.emergency_number,
                "label": "Emergency services"
            })

        if self.crisis_number:
            resources.append({
                "type": "crisis",
                "number": self.crisis_number,
                "label": "Crisis support"
            })

        return resources

    def get_country(self) -> str:
        return self.country

    def get_resources(self):
        return self._resources()