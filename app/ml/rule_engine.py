import re


class MindCareRuleEngine:
    """
    Deterministic rule-based baseline for MindCare.

    The engine is intentionally conservative and interpretable.

    It distinguishes:
    - personal high-risk language
    - explicit negation
    - third-person/contextual mentions
    - informational/educational mentions
    - ordinary academic/work stress
    - positive emotional language
    """

    HIGH_RISK_PATTERNS = {
        "self_harm": [
            r"\bhurt myself\b",
            r"\bharm myself\b",
            r"\bself[- ]harm\b",
            r"\bkill myself\b",
            r"\bend my life\b",
            r"\bsuicidal\b",
            r"\bsuicide\b",
        ],
        "crisis": [
            r"\bin immediate danger\b",
            r"\bnot safe\b",
            r"\bfeel unsafe\b",
            r"\bcan't keep myself safe\b",
            r"\bcannot keep myself safe\b",
            r"\bdo not feel safe\b",
        ],
    }

    NEGATION_PATTERNS = [
    # English
    r"\bnot suicidal\b",
    r"\bnot thinking about hurting myself\b",
    r"\bdo not want to hurt myself\b",
    r"\bdon't want to hurt myself\b",
    r"\bnot considering self[- ]harm\b",
    r"\bnot thinking about self[- ]harm\b",
    r"\bnot thinking about suicide\b",
    r"\bdo not want to kill myself\b",
    r"\bdon't want to kill myself\b",
    r"\bnot going to hurt myself\b",
    r"\bnot going to harm myself\b",
    r"\bdo not want to harm myself\b",
    r"\bdon't want to harm myself\b",
    r"\bdo not want to self[- ]harm\b",
    r"\bdon't want to self[- ]harm\b",
    r"\bdon't want to die\b",
    r"\bdo not want to die\b",
    r"\bnot suicidal\b",
    r"\bnot thinking about suicide\b",

    # Hinglish / code-mixed
    r"\bself[- ]harm consider nahi kar raha hoon\b",
    r"\bself[- ]harm consider nahi kar rahi hoon\b",
    r"\bself[- ]harm ke thoughts nahi aa rahe\b",
    r"\bself[- ]harm ke thoughts nahi aa rahe hain\b",
    r"\bmain suicidal nahi hoon\b",
    r"\bmain suicide nahi karunga\b",
    r"\bmain suicide nahi karungi\b",
    r"\bmain khud ko harm nahi karna chahta\b",
    r"\bmain khud ko harm nahi karna chahti\b",
    r"\bmain khud ko harm nahi kar raha hoon\b",
    r"\bmain khud ko harm nahi kar rahi hoon\b",
    r"\bmain khud ko hurt nahi karna chahta\b",
    r"\bmain khud ko hurt nahi karna chahti\b",
    r"\bmain self[- ]harm nahi kar raha hoon\b",
    r"\bmain self[- ]harm nahi kar rahi hoon\b",
]

    CONTEXT_PATTERNS = [
        r"\bmy friend\b",
        r"\bmy roommate\b",
        r"\bmy classmate\b",
        r"\bmy family\b",
        r"\bsomeone i know\b",
        r"\bsomeone close to me\b",
        r"\banother person\b",
        r"\bthey are\b",
        r"\bthey're\b",
        r"\bworried about them\b",
        r"\bconcerned about them\b",
        r"\bhelping them\b",
        r"\bsupport them\b",
        r"\ba family member\b",
        r"\bfamily member\b",
        r"\bmy family member\b",
        r"\bmy classmate\b",
        r"\bmera classmate\b",
        r"\bmeri classmate\b",
        r"\bfamily member says\b",
        r"\bfamily member said\b",
        r"\bworried about a friend\b",
        r"\bfriend .* talking about suicide\b",
        r"\bfriend .* mentioned suicide\b",
        r"\bfriend .* struggling\b",
    ]

    INFORMATIONAL_PATTERNS = [
        r"\bread an article\b",
        r"\barticle about\b",
        r"\bread about\b",
        r"\bnews about\b",
        r"\bwatched a video\b",
        r"\bwatched a documentary\b",
        r"\bin today's lecture\b",
        r"\btoday's lecture\b",
        r"\bclass discussed\b",
        r"\bclass discussion\b",
        r"\bdiscussed .* during class\b",
        r"\bdiscussed .* during today's lecture\b",
        r"\blearned about\b",
        r"\bstudied\b",
        r"\bresearching\b",
        r"\bdiscussion about\b",
        r"\bfor my research\b",
        r"\bfor a research project\b",
        r"\bfor my assignment\b",
    ]

    POSITIVE_PATTERNS = [
        r"\bfeel better\b",
        r"\bfeeling better\b",
        r"\bfeeling much better\b",
        r"\bfeel much better\b",
        r"\bfeeling good\b",
        r"\bfeel good\b",
        r"\bfeeling happy\b",
        r"\bfeel happy\b",
        r"\bproud of myself\b",
        r"\bdoing well\b",
        r"\bfeeling hopeful\b",
        r"\bfeel hopeful\b",
        r"\bhopeful about\b",
        r"\bfeeling positive\b",
        r"\bfeel positive\b",
        r"\bthings are getting better\b",
        r"\bgetting much better\b",
        r"\bgetting better\b",
        r"\bthings are getting better\b",
        r"\bthings are much better\b",
    ]

    ORDINARY_STRESS_PATTERNS = [
        r"\boverwhelmed by my assignments\b",
        r"\boverwhelmed by assignments\b",
        r"\boverwhelmed with my assignments\b",
        r"\boverwhelmed with assignments\b",
        r"\bstressed about my assignments\b",
        r"\bstressed about assignments\b",
        r"\bassignment stress\b",
        r"\bcollege stress\b",
        r"\bwork stress\b",
        r"\bdeadline stress\b",
        r"\bpressure from my assignments\b",
        r"\bpressure from my work\b",
        r"\bpressure from my college\b",
        r"\bpressure from my job\b",
        r"\bpressure from my studies\b",
        r"\bpressure from my responsibilities\b",
        r"\bpressure from my tasks\b",
        r"\bstressed about college\b",
        r"\bstressed about work\b",
        r"\bstressed about studies\b",
        r"\bstressed about school\b",
        r"\bstressed about deadlines\b",
        r"\bworried about my assignments\b",
        r"\bcollege deadlines\b",
        r"\bdeadlines are making me stressed\b",
        r"\bdeadlines .* stressed\b",
        r"\bdeadline .* stress\b",
        r"\bstruggling emotionally\b",
        r"\bneed someone to talk to\b",
        r"\bjust need someone to talk to\b",
    ]

    def predict(self, message: str) -> str:
        """
        Return only the predicted category.
        """
        return self.predict_detailed(message)["category"]

    def predict_detailed(self, message: str) -> dict:
        """
        Return category, risk level, rule fired, and matched rule.
        """

        if not isinstance(message, str):
            raise TypeError("message must be a string")

        text = message.lower().strip()

        # -------------------------------------------------
        # 1. Explicit negation gets highest priority.
        # -------------------------------------------------
        for pattern in self.NEGATION_PATTERNS:
            if re.search(pattern, text):
                return {
                    "category": "negated",
                    "risk_level": "low",
                    "rule_fired": "negation",
                    "matched_rule": pattern,
                }

        # -------------------------------------------------
        # 2. Informational / educational context.
        #
        # Prevents words such as "suicide" or "self-harm"
        # from automatically becoming personal high-risk
        # signals when the user is discussing information,
        # education, research, media, or coursework.
        # -------------------------------------------------
        for pattern in self.INFORMATIONAL_PATTERNS:
            if re.search(pattern, text):
                return {
                    "category": "neutral",
                    "risk_level": "low",
                    "rule_fired": "informational_context",
                    "matched_rule": pattern,
                }

        # -------------------------------------------------
        # 3. Ordinary academic / work stress.
        #
        # Generic stress around assignments, exams, work,
        # deadlines, etc. should not automatically become
        # a crisis classification.
        # -------------------------------------------------
        for pattern in self.ORDINARY_STRESS_PATTERNS:
            if re.search(pattern, text):
                return {
                    "category": "neutral",
                    "risk_level": "low",
                    "rule_fired": "ordinary_stress",
                    "matched_rule": pattern,
                }

        # -------------------------------------------------
        # 4. Third-person / contextual language.
        #
        # If a high-risk keyword appears while the message
        # clearly refers to another person, classify it as
        # contextual rather than personal high-risk.
        # -------------------------------------------------
        has_context = any(
            re.search(pattern, text)
            for pattern in self.CONTEXT_PATTERNS
        )

        # -------------------------------------------------
        # 5. Personal high-risk language.
        # -------------------------------------------------
        for category, patterns in self.HIGH_RISK_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, text):

                    if has_context:
                        return {
                            "category": "contextual",
                            "risk_level": "medium",
                            "rule_fired": "contextual",
                            "matched_rule": f"contextual_{category}",
                        }

                    return {
                        "category": category,
                        "risk_level": "high",
                        "rule_fired": "high_risk",
                        "matched_rule": category,
                    }

        # -------------------------------------------------
        # 6. Positive emotional language.
        # -------------------------------------------------
        for pattern in self.POSITIVE_PATTERNS:
            if re.search(pattern, text):
                return {
                    "category": "positive",
                    "risk_level": "low",
                    "rule_fired": "positive",
                    "matched_rule": pattern,
                }

        # -------------------------------------------------
        # 7. Default.
        # -------------------------------------------------
        return {
            "category": "neutral",
            "risk_level": "low",
            "rule_fired": False,
            "matched_rule": None,
        }