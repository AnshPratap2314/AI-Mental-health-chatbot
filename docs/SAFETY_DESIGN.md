# MindCare AI — Safety Design

## 1. Purpose

MindCare AI is designed as a supportive conversational system with
safety-oriented risk detection and response routing.

The system does not treat machine-learning predictions as the sole
authority for safety-critical decisions.

Safety-critical rules have priority over ordinary ML classification
and response generation.

---

## 2. Safety Architecture

The high-level processing flow is:

User Message
    ↓
Input Validation / Sanitization
    ↓
Context & State Analysis
    ↓
Risk Detection
    ↓
Authoritative Safety Rules
    ↓
Hybrid / ML Risk Analysis
    ↓
Safety Decision
    ↓
Response Routing
    ↓
Safety Audit
    ↓
API Response

---

## 3. Safety Decision Priority

The system uses explicit safety overrides.

The effective decision source follows this priority:

1. Contextual suicide override
2. Crisis override
3. Self-harm override
4. Plan-related override
5. High-risk safety override
6. Hybrid/ML decision
7. Rule engine fallback

This ordering prevents a low-confidence ML prediction from
overriding an authoritative safety signal.

---

## 4. High-Risk Response Isolation

When a message is classified as high risk through an authoritative
safety rule:

- `response_source` must be `safety`
- `response_model` must be `None`
- the safety response must not originate from the trained response model
- ordinary response retrieval must not replace the safety response
- the corresponding `decision_source` must identify the authoritative
  safety rule

This provides response provenance for safety-critical interactions.

---

## 5. ML Role

The ML components are used for:

- contextual classification
- risk estimation
- response intent classification
- response retrieval
- metadata prediction

ML predictions are not permitted to suppress an authoritative
crisis or self-harm rule.

The system therefore follows a hybrid architecture:

    Deterministic Safety Rules
              +
           ML Models
              ↓
       Safety-aware routing

---

## 6. Response Routing

Responses are selected in the following general order:

1. Safety response for high-risk situations
2. Deterministic safety/support response where applicable
3. Follow-up, greeting, or gratitude response
4. LLM response when safely configured
5. Trained response model
6. Safe fallback response

The safety layer is evaluated before normal response generation.

---

## 7. Provenance

Every generated response should have enough metadata to explain
where the decision originated.

Relevant fields include:

- `risk_level`
- `risk_score`
- `decision_source`
- `response_source`
- `response_model`

For high-risk responses, provenance must remain consistent with the
authoritative safety decision.

---

## 8. Audit Logging

Safety decisions are recorded using the safety audit system.

The audit record contains safety metadata rather than the user's
message content.

Recorded information may include:

- timestamp
- risk level
- risk score
- action
- mode
- detected signals
- decision source
- human-support requirement
- immediate-guidance requirement

Sensitive conversational content should not be written to the
safety audit log.

---

## 9. Determinism

Safety-critical classification should be deterministic for the same
input and equivalent state.

Regression tests verify that repeated evaluation of the same message
does not unexpectedly change:

- risk level
- risk score
- decision source
- safety response provenance

---

## 10. Fail-Safe Principle

If an authoritative safety rule detects a critical condition, normal
ML response generation must not override it.

Safety routing takes precedence over conversational personalization,
retrieval, or ordinary language-model generation.

---

## 11. Testing Requirements

Safety-related changes must preserve:

- crisis detection
- self-harm detection
- plan-related detection
- high-risk response isolation
- response provenance
- risk determinism
- audit behavior
- API security behavior

The complete automated test suite should pass before deployment.

---

## 12. Limitations

MindCare AI is a software project and should not be treated as a
replacement for qualified human support, professional assessment,
emergency services, or clinical care.

Model metrics and automated tests demonstrate software behavior under
the tested conditions; they do not establish clinical effectiveness.

---

## 13. Change Management

Changes to safety rules, risk thresholds, safety response routing,
or high-risk provenance should be accompanied by regression tests.

A safety-related change should not be merged solely because the
application starts successfully. The full automated test suite should
also pass.
