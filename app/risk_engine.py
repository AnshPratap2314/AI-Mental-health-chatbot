import re
from typing import Dict


class RiskEngine:

    CRISIS_PATTERNS = [
        r"\bi want to die\b",
        r"\bi wanna die\b",
        r"\bi want to kill myself\b",
        r"\bi want to hurt myself\b",
        r"\bi am suicidal\b",
        r"\bi'm suicidal\b",
        r"\bkill myself\b",
        r"\bhurt myself\b",
        r"\bend my life\b",
        r"\bno reason to live\b",
        r"\bdon't want to live\b",
        r"\bdo not want to live\b"
    ]

    SERIOUS_PATTERNS = [
        r"\bhopeless\b",
        r"\bhelpless\b",
        r"\bworthless\b",
        r"\bfalling apart\b",
        r"\bcan't go on\b",
        r"\bcannot go on\b",
        r"\bcan't cope\b",
        r"\bcannot cope\b",
        r"\bcompletely alone\b",
        r"\bcan't handle\b",
        r"\bcannot handle\b",
        r"\bi can't handle this\b"
    ]

    SAD_PATTERNS = [
        r"\bsad\b",
        r"\blonely\b",
        r"\bempty\b",
        r"\bdown\b",
        r"\bdepressed\b",
        r"\bcrying\b",
        r"\bnot okay\b"
    ]

    INTENT_PATTERNS = [
        r"\bi might do it\b",
        r"\bi'm going to do it\b",
        r"\bi am going to do it\b",
        r"\bi can't stop myself\b",
        r"\bi don't think i can stop\b",
        r"\bi've decided\b"
    ]

    TEMPORAL_PATTERNS = [
        r"\bright now\b",
        r"\btonight\b",
        r"\btoday\b",
        r"\bsoon\b"
    ]

    PROTECTIVE_PATTERNS = [
        r"\bmy family\b",
        r"\bmy friends\b",
        r"\bmy pet\b",
        r"\bpeople i love\b",
        r"\bi want to live\b",
        r"\bi don't want to die\b",
        r"\bi do not want to die\b"
    ]

    NEGATION_PATTERNS = [
        r"\bi don't want to die\b",
        r"\bi do not want to die\b",
        r"\bi don't want to hurt myself\b",
        r"\bi do not want to hurt myself\b",
        r"\bi'm not suicidal\b",
        r"\bi am not suicidal\b",
        r"\bnot suicidal\b"
    ]

    @staticmethod
    def matches(text: str, patterns) -> bool:

        for pattern in patterns:

            if re.search(
                pattern,
                text,
                re.IGNORECASE
            ):
                return True

        return False

    def analyze(self, message: str) -> Dict:

        text = message.strip()

        negated = self.matches(
            text,
            self.NEGATION_PATTERNS
        )

        crisis = self.matches(
            text,
            self.CRISIS_PATTERNS
        )

        serious = self.matches(
            text,
            self.SERIOUS_PATTERNS
        )

        sad = self.matches(
            text,
            self.SAD_PATTERNS
        )

        intent = self.matches(
            text,
            self.INTENT_PATTERNS
        )

        temporal = self.matches(
            text,
            self.TEMPORAL_PATTERNS
        )

        protective = self.matches(
            text,
            self.PROTECTIVE_PATTERNS
        )

        if negated and not intent:

            crisis = False
            serious = False

        score = 0.0

        if crisis:
            score += 0.70

        if serious:
            score += 0.35

        if sad:
            score += 0.10

        if intent:
            score += 0.20

        if temporal and (
            crisis or intent
        ):
            score += 0.10

        if protective:
            score -= 0.05

        if negated and not intent:
            score = 0.0

        score = min(
            max(score, 0.0),
            1.0
        )

        if negated and not intent:

            risk_level = "low"

        elif crisis:

            risk_level = "high"

        elif intent and temporal:

            risk_level = "high"

        elif intent:

            risk_level = "moderate"

        elif serious:

            risk_level = "moderate"

        elif sad:

            risk_level = "low"

        else:

            risk_level = "low"

        return {
            "risk_level": risk_level,
            "risk_score": round(score, 2),
            "signals": {
                "crisis": crisis,
                "serious": serious,
                "sad": sad,
                "intent": intent,
                "temporal": temporal,
                "protective": protective,
                "negated": negated
            }
        }