# MindCare AI --- Safety Design

## Scope

MindCare is a supportive conversational AI prototype, not a medical
device, diagnostic system, therapist, or emergency service.

## 1. Safety Principles

1.  Deterministic safety controls have authority over normal generation.
2.  ML predictions are evidence, not unconditional safety decisions.
3.  LLM output is subject to a safety gate.
4.  High-risk messages follow a deterministic response path.
5.  Safety decisions are auditable without storing the original message.
6.  Safety behavior is regression-tested.
7.  Benchmark results are not clinical validation.

## 2. Safety Flow

``` text
User message
     ↓
Rule analysis + ML + context
     ↓
Hybrid analysis
     ↓
Safety precedence
     ↓
┌───────────────┬───────────────┐
│ High risk     │ Normal        │
├───────────────┼───────────────┤
│ Deterministic │ Normal        │
│ safety reply  │ response path │
│ Support flag  │ Safety gate   │
│ Guidance flag │ Audit         │
│ Audit         │               │
└───────────────┴───────────────┘
```

## 3. Authoritative Signals

Configured signals include:

-   crisis
-   self-harm
-   intent
-   plan
-   temporal indicators
-   contextual suicide
-   negation
-   protective signals

Safety precedence prevents ordinary ML classification from overriding
authoritative safety rules.

## 4. LLM Boundary

The LLM is not the final safety authority.

``` text
Safety Policy
     ↓
LLM permitted?
  ├── NO  → deterministic safety response
  └── YES → LLM generation
```

Configured dangerous instructional patterns are rejected.

## 5. High-Risk Policy

A high-risk result requires:

-   deterministic safety response
-   human-support flag
-   immediate-guidance flag
-   crisis mode
-   audit record

## 6. Negation and Context

The system must distinguish direct statements from negated or contextual
statements.

Examples represented in testing include:

``` text
"I want to hurt myself."
```

versus:

``` text
"I am not thinking about hurting myself."
```

and discussion of another person's situation.

## 7. Audit

The audit stores:

-   timestamp
-   risk level
-   risk score
-   action
-   mode
-   signals
-   decision source
-   human-support requirement
-   immediate-guidance requirement

It intentionally excludes the original message, username, IP address,
credentials and full session ID.

## 8. Safety Testing

The test suite includes low-, moderate- and high-risk behavior, crisis
overrides, negation, contextual cases, hard negatives, API-level safety
flow and persistent audit behavior.

Current regression result:

``` text
230 passed
```

## 9. Limitations

Potential failure modes include:

-   ambiguous wording
-   indirect language
-   novel expressions
-   cultural context
-   multilingual/code-switched language outside the benchmark
-   sarcasm
-   missing context
-   adversarial input

Real-world deployment would require additional validation and qualified
domain expertise.

## 10. Responsible Claims

Prefer:

> The system demonstrates deterministic-first safety engineering on a
> synthetic benchmark.

Avoid:

> The system guarantees safety.

Prefer:

> The classifier achieved 100% accuracy on the current synthetic test
> set.

Avoid:

> The system has 100% real-world crisis detection accuracy.

## 11. Emergency Scope

MindCare should never be presented as an emergency response service.
When immediate danger is discussed, users should be directed toward
appropriate local emergency services or qualified crisis support rather
than being encouraged to rely on the chatbot alone.
