from typing import Any, Dict, Optional


class SafetyResources:

    def __init__(self):
        self.resources = {
            "default": {
                "emergency": "Contact your local emergency services.",
                "trusted_person": "Move toward a trusted person who can stay with you.",
                "professional": "Contact a qualified mental-health professional or crisis service."
            },
            "india": {
                "emergency": "Contact your local emergency services.",
                "trusted_person": "Move toward a trusted person who can stay with you.",
                "professional": "Contact a qualified mental-health professional or crisis service."
            }
        }

    def get(
        self,
        country: Optional[str] = None
    ) -> Dict[str, str]:

        key = str(
            country or "default"
        ).lower()

        return dict(
            self.resources.get(
                key,
                self.resources["default"]
            )
        )

    def build_crisis_guidance(
        self,
        country: Optional[str] = None
    ) -> Dict[str, Any]:

        resources = self.get(country)

        return {
            "resources": resources,
            "steps": [
                "Move to a safer place.",
                "Stay with or contact a trusted person.",
                "Contact local emergency or crisis support if you may be in immediate danger."
            ]
        }