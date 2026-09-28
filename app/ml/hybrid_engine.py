from app.ml.rule_engine import MindCareRuleEngine
from app.ml.text_classifier import MindCareTextClassifier


class HybridRiskEngine:
    """
    Hybrid MindCare decision engine.

    Combines:
    - deterministic safety/context rules
    - TF-IDF + Logistic Regression
    - confidence-aware high-risk decisions
    """

    ML_HIGH_RISK_THRESHOLD = 0.50

    def __init__(self):
        self.rule_engine = MindCareRuleEngine()
        self.ml_model = MindCareTextClassifier()
        self.ml_model.load()

    def _build_result(
        self,
        category,
        risk_level,
        decision_source,
        ml_category,
        rule_category,
        rule_fired,
        matched_rule,
        ml_high_risk_probability,
    ):
        """
        Keep a stable result schema for all decision paths.
        """

        return {
            "category": category,
            "risk_level": risk_level,
            "decision_source": decision_source,

            # Fields expected by evaluation scripts
            "ml_category": ml_category,
            "rule_category": rule_category,

            "rule_fired": rule_fired,
            "matched_rule": matched_rule,

            "ml_high_risk_probability": ml_high_risk_probability,
        }

    def predict(self, message: str) -> dict:
        rule_result = self.rule_engine.predict_detailed(message)

        ml_category = self.ml_model.predict(message)
        probabilities = self.ml_model.predict_proba(message)

        classes = self.ml_model.pipeline.classes_

        probability_map = {
            label: float(probability)
            for label, probability in zip(classes, probabilities)
        }

        ml_high_risk_probability = max(
            probability_map.get("crisis", 0.0),
            probability_map.get("self_harm", 0.0),
        )

        rule_category = rule_result["category"]
        rule_fired = rule_result["rule_fired"]
        matched_rule = rule_result["matched_rule"]

        # ---------------------------------------------------------
        # 1. NEGATION OVERRIDE
        # ---------------------------------------------------------
        if rule_category == "negated":
            return self._build_result(
                category="negated",
                risk_level="low",
                decision_source="rule_override",
                ml_category=ml_category,
                rule_category=rule_category,
                rule_fired=rule_fired,
                matched_rule=matched_rule,
                ml_high_risk_probability=ml_high_risk_probability,
            )

        # ---------------------------------------------------------
        # 2. INFORMATIONAL / EDUCATIONAL CONTEXT
        # ---------------------------------------------------------
        if rule_fired == "informational_context":
            return self._build_result(
                category="neutral",
                risk_level="low",
                decision_source="rule_context_override",
                ml_category=ml_category,
                rule_category=rule_category,
                rule_fired=rule_fired,
                matched_rule=matched_rule,
                ml_high_risk_probability=ml_high_risk_probability,
            )

        # ---------------------------------------------------------
        # 3. ORDINARY STRESS
        # ---------------------------------------------------------
        if rule_fired == "ordinary_stress":
            return self._build_result(
                category="neutral",
                risk_level="low",
                decision_source="rule_stress_override",
                ml_category=ml_category,
                rule_category=rule_category,
                rule_fired=rule_fired,
                matched_rule=matched_rule,
                ml_high_risk_probability=ml_high_risk_probability,
            )

        # ---------------------------------------------------------
        # 4. EXPLICIT PERSONAL HIGH-RISK RULE
        # ---------------------------------------------------------
        if (
            rule_category in {"crisis", "self_harm"}
            and rule_fired == "high_risk"
        ):
            return self._build_result(
                category=rule_category,
                risk_level="high",
                decision_source="rule_safety_override",
                ml_category=ml_category,
                rule_category=rule_category,
                rule_fired=rule_fired,
                matched_rule=matched_rule,
                ml_high_risk_probability=ml_high_risk_probability,
            )

        # ---------------------------------------------------------
        # 5. POSITIVE RULE
        # ---------------------------------------------------------
        if (
            rule_category == "positive"
            and rule_fired == "positive"
        ):
            return self._build_result(
                category="positive",
                risk_level="low",
                decision_source="rule_positive_override",
                ml_category=ml_category,
                rule_category=rule_category,
                rule_fired=rule_fired,
                matched_rule=matched_rule,
                ml_high_risk_probability=ml_high_risk_probability,
            )

        # ---------------------------------------------------------
        # 6. CONTEXTUAL RULE
        # ---------------------------------------------------------
        if (
            rule_category == "contextual"
            and rule_fired == "contextual"
        ):
            return self._build_result(
                category="contextual",
                risk_level="medium",
                decision_source="rule_context",
                ml_category=ml_category,
                rule_category=rule_category,
                rule_fired=rule_fired,
                matched_rule=matched_rule,
                ml_high_risk_probability=ml_high_risk_probability,
            )

        # ---------------------------------------------------------
        # 7. ML HIGH-RISK WITH CONFIDENCE THRESHOLD
        # ---------------------------------------------------------
        if (
            ml_category in {"crisis", "self_harm"}
            and ml_high_risk_probability
            >= self.ML_HIGH_RISK_THRESHOLD
        ):
            return self._build_result(
                category=ml_category,
                risk_level="high",
                decision_source="ml_high_risk",
                ml_category=ml_category,
                rule_category=rule_category,
                rule_fired=rule_fired,
                matched_rule=matched_rule,
                ml_high_risk_probability=ml_high_risk_probability,
            )

        # ---------------------------------------------------------
        # 8. ML CONTEXTUAL
        # ---------------------------------------------------------
        if ml_category == "contextual":
            return self._build_result(
                category="contextual",
                risk_level="medium",
                decision_source="ml_contextual",
                ml_category=ml_category,
                rule_category=rule_category,
                rule_fired=rule_fired,
                matched_rule=matched_rule,
                ml_high_risk_probability=ml_high_risk_probability,
            )

        # ---------------------------------------------------------
        # 9. ML POSITIVE
        # ---------------------------------------------------------
        if ml_category == "positive":
            return self._build_result(
                category="positive",
                risk_level="low",
                decision_source="ml_positive",
                ml_category=ml_category,
                rule_category=rule_category,
                rule_fired=rule_fired,
                matched_rule=matched_rule,
                ml_high_risk_probability=ml_high_risk_probability,
            )

        # ---------------------------------------------------------
        # 10. DEFAULT ML PREDICTION
        # ---------------------------------------------------------
        if ml_category in {"crisis", "self_harm"}:
            risk_level = "high"
        elif ml_category == "contextual":
            risk_level = "medium"
        else:
            risk_level = "low"

        return self._build_result(
            category=ml_category,
            risk_level=risk_level,
            decision_source="ml",
            ml_category=ml_category,
            rule_category=rule_category,
            rule_fired=rule_fired,
            matched_rule=matched_rule,
            ml_high_risk_probability=ml_high_risk_probability,
        )