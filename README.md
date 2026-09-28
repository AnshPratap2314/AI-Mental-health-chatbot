# MindCare AI

> Safety-focused conversational AI prototype built with Python, FastAPI,
> classical ML, deterministic safety controls, persistent auditing,
> automated testing, and Docker.

## ⚠️ Scope and Safety Notice

MindCare AI is a **software-engineering and AI-safety prototype**. It is
not a medical device, diagnostic system, therapist, emergency service,
or replacement for qualified professional care.

The current ML evaluation uses a **synthetic, non-clinical dataset**.
Its benchmark results must not be interpreted as clinical effectiveness,
diagnostic accuracy, or real-world crisis-detection performance.

## Overview

MindCare uses a deterministic-first architecture:

``` text
User Message
     ↓
API Validation
     ↓
Behavior + Context Analysis
     ↓
┌───────────────┬───────────────┐
│ Rule Engine   │ ML Classifier │
└───────────────┴───────────────┘
             ↓
       Hybrid Risk Layer
             ↓
        Safety Policy
             ↓
      ┌──────┴──────┐
      │             │
  High Risk       Normal
      │             │
      ▼             ▼
Deterministic   Response/LLM
Safety Reply    Generation
      │             │
      └──────┬──────┘
             ▼
       Safety Audit
             ↓
     Persistent JSONL
```

**Core principle:** the LLM can generate language, but it does not own
the final high-risk safety decision.

## Key Features

### AI/ML

-   TF-IDF + Logistic Regression
-   Six-class synthetic benchmark
-   Rule-based risk detection
-   Hybrid rule + ML decision system
-   Context-aware conversation state
-   Hard-negative testing
-   Independent challenge-set evaluation
-   5-fold cross-validation

### Safety

-   Deterministic high-risk overrides
-   Crisis/self-harm/plan signal handling
-   Negation and contextual-reference handling
-   Human-support and immediate-guidance flags
-   LLM safety gate
-   Dangerous-instruction filtering
-   Persistent safety audit

### Backend and security

-   FastAPI REST API
-   Pydantic input validation
-   Session management and TTL
-   Chat and session rate limiting
-   CORS allowlist
-   Security headers
-   Authenticated audit endpoints
-   Privacy-conscious request logging

### Deployment and reliability

-   Docker
-   Docker Compose
-   Gunicorn + Uvicorn worker
-   Healthcheck
-   Persistent Docker volume
-   Automated regression tests

## Architecture

``` text
                         ┌──────────────────┐
                         │   Web Frontend   │
                         └────────┬─────────┘
                                  ↓
                         ┌──────────────────┐
                         │     FastAPI      │
                         └────────┬─────────┘
                                  ↓
                 ┌────────────────┼────────────────┐
                 ↓                ↓                ↓
            Validation       Rate Limit        Session
                 └────────────────┼────────────────┘
                                  ↓
                         ┌──────────────────┐
                         │  Behavior Engine │
                         └────────┬─────────┘
                                  ↓
              ┌───────────────────┼───────────────────┐
              ↓                   ↓                   ↓
         Rule Engine          ML Model           Context
              └───────────────────┼───────────────────┘
                                  ↓
                         ┌──────────────────┐
                         │ Hybrid Risk      │
                         │ Engine           │
                         └────────┬─────────┘
                                  ↓
                         ┌──────────────────┐
                         │ Safety Policy    │
                         └────────┬─────────┘
                                  ↓
                         ┌────────┴────────┐
                         ↓                 ↓
                   High-risk           Normal
                         ↓                 ↓
                 Deterministic       Response/LLM
                  safety path         generation
                         └────────┬────────┘
                                  ↓
                         ┌──────────────────┐
                         │ Persistent Audit │
                         │ JSONL + Volume   │
                         └──────────────────┘
```

Detailed architecture: [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)

## Safety Architecture

High-risk processing follows:

``` text
Message
  ↓
Rule + ML + Context Analysis
  ↓
Safety Precedence
  ↓
High Risk?
  ├── YES → Deterministic Safety Response
  │          + human-support flag
  │          + immediate-guidance flag
  │          + audit
  │
  └── NO  → Normal response path
             + safety validation
             + audit
```

Configured authoritative safety signals take precedence over normal ML
output. The LLM is not the final safety authority.

Detailed design: [`docs/SAFETY_DESIGN.md`](docs/SAFETY_DESIGN.md)

## Hybrid Decision System

Conceptual precedence:

``` text
contextual_suicide
       ↓
crisis
       ↓
self_harm
       ↓
plan
       ↓
high-risk safety override
       ↓
hybrid / ML decision
```

Verified example:

``` text
Input:          "I want to die"
Risk level:     high
Risk score:     0.7
Decision source: rule_crisis_override
```

This prevents a low/neutral ML prediction from masking an authoritative
safety signal.

## ML Pipeline

``` text
Text
 ↓
TF-IDF
 ↓
Logistic Regression
 ↓
Class + Probability
 ↓
Hybrid Risk Engine
```

### Dataset

  Property                              Value
  ---------------- --------------------------
  Total examples                        1,200
  Classes                                   6
  Examples/class                          200
  Train                                   840
  Validation                              180
  Test                                    180
  Languages                English + Hinglish
  Type               Synthetic / non-clinical

Classes:

``` text
crisis
self_harm
negated
contextual
neutral
positive
```

Data-quality checks include exact duplicates, cross-split leakage,
near-duplicate auditing, challenge samples, and hard negatives.

## Evaluation

### Canonical test benchmark

  System                           Accuracy   Macro Precision   Macro Recall   Macro F1
  ------------------------------ ---------- ----------------- -------------- ----------
  Rule engine                        36.67%            86.81%         36.67%     35.25%
  TF-IDF + Logistic Regression         100%              100%           100%       100%
  Hybrid system                        100%              100%           100%       100%

Additional recorded results: - 5-fold CV: 1.0000 accuracy and macro F1 -
Independent challenge set: 20/20 correct - Hard-negative set: 10/10
correct - Canonical test errors: 0/180 - Validation threshold 0.50:
precision 1.0000, recall 0.9667, F1 0.9831

**Important:** these are synthetic benchmark results, not clinical
validation.

Detailed report: [`docs/EVALUATION.md`](docs/EVALUATION.md)

## Security

Implemented controls include:

-   Pydantic validation
-   bounded message/session/user input
-   malformed JSON rejection
-   method restrictions
-   CORS allowlist
-   chat rate limiting
-   session-creation rate limiting
-   authenticated audit endpoints
-   `X-Content-Type-Options: nosniff`
-   `X-Frame-Options: DENY`
-   `Referrer-Policy: no-referrer`
-   `Cache-Control: no-store`
-   privacy-conscious HTTP logging

Normal request logs intentionally avoid message bodies, query
parameters, authentication data, and full session identifiers.

## Persistent Safety Audit

Production uses:

``` text
logs/safety_audit.jsonl
```

The audit records structured metadata such as timestamp, risk level,
risk score, action, mode, signals, decision source, and safety-support
flags.

It intentionally does not store the original message, username, IP
address, credentials, or full session ID.

Persistence uses file locking and a bounded record history. Docker
stores the audit file on a persistent volume.

The audit was verified to survive container restart.

## API

### Health

``` http
GET /health
```

Example:

``` json
{
  "status": "healthy",
  "service": "mindcare-api",
  "version": "1.2.0"
}
```

### Create session

``` http
POST /session
Content-Type: application/json
```

``` json
{"user_name":"friend"}
```

### Chat

``` http
POST /chat
Content-Type: application/json
```

``` json
{
  "session_id": "SESSION_ID",
  "message": "I feel stressed about my exams."
}
```

The response can include risk level, score, signals, context, mode,
response source, decision source, and reply.

### Audit

``` http
GET /api/audit/count
X-MindCare-Audit-Key: <key>
```

``` http
GET /api/audit/recent
X-MindCare-Audit-Key: <key>
```

Audit endpoints require authentication.

## Docker

Build:

``` bash
docker compose build
```

Start:

``` bash
docker compose up -d
```

Check:

``` bash
docker compose ps
```

Health:

``` bash
curl -i http://127.0.0.1:8001/health
```

Logs:

``` bash
docker compose logs --tail=50 mindcare-api
```

Restart:

``` bash
docker compose restart mindcare-api
```

Current mapping:

``` text
host 8001 → container 8000
```

The current deployment uses one Gunicorn worker because session state is
process-local. Horizontal scaling requires shared session storage.

## Testing

Run:

``` bash
python -m pytest -q
```

Current verified regression result:

``` text
230 passed
```

Coverage includes behavior, context, conversation flow, safety,
sessions, LLM safety, API security, session hardening, and persistent
safety-audit end-to-end behavior.

The 230-test result is a software regression result, not clinical
validation.

## Project Structure

``` text
AI-Mental-health-chatbot/
├── app/
│   ├── behavior_engine.py
│   ├── context_engine.py
│   ├── context_state.py
│   ├── crisis_manager.py
│   ├── health.py
│   ├── llm_engine.py
│   ├── main.py
│   ├── memory.py
│   ├── ml/
│   │   ├── dataset.py
│   │   ├── hybrid_engine.py
│   │   ├── labels.py
│   │   ├── rule_engine.py
│   │   └── text_classifier.py
│   ├── personalization_engine.py
│   ├── privacy_manager.py
│   ├── production_config.py
│   ├── response_engine.py
│   ├── risk_engine.py
│   ├── safety_audit.py
│   ├── safety_engine.py
│   ├── safety_policy.py
│   ├── safety_resources.py
│   ├── safety_support.py
│   ├── security.py
│   ├── session_manager.py
│   └── logging_config.py
├── data/
├── evaluation/
├── models/
├── scripts/
├── frontend/
├── tests/
├── docs/
├── logs/
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
├── pytest.ini
├── requirements.txt
└── README.md
```

## Local Development

``` bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Health:

``` bash
curl http://127.0.0.1:8000/health
```

Tests:

``` bash
python -m pytest -q
```

## Environment Variables

Relevant configuration includes:

``` text
MINDCARE_AUDIT_FILE
MINDCARE_AUDIT_MAX_RECORDS
MINDCARE_AUDIT_API_KEY
CHAT_RATE_LIMIT
CHAT_RATE_LIMIT_BURST
SESSION_RATE_LIMIT
SESSION_RATE_LIMIT_BURST
```

Never commit real secrets. Use a local `.env` and a safe `.env.example`
template.

## Limitations

-   The benchmark is synthetic and non-clinical.
-   High benchmark scores do not establish real-world safety or clinical
    performance.
-   Real conversations may contain ambiguous, indirect, multilingual,
    culturally specific, sarcastic, or novel language.
-   Sessions are currently process-local.
-   JSONL is appropriate for the current prototype but not ideal for
    high-volume distributed analytics.
-   The project has application logging and health checks but does not
    claim a complete enterprise observability stack.
-   Real deployment would require additional security, privacy, safety,
    expert, governance, and compliance validation.

## Future Improvements

1.  Shared Redis/PostgreSQL session storage
2.  CI/CD with GitHub Actions
3.  Dependency and container vulnerability scanning
4.  Structured metrics and observability
5.  Model/version registry
6.  Dataset versioning
7.  Calibration and threshold monitoring
8.  Drift monitoring
9.  Larger independently curated evaluation sets
10. Expert-reviewed safety evaluation
11. Production-grade audit storage
12. Load testing and horizontal scaling

## Interview Explanation

### 30 seconds

> MindCare AI is a safety-focused conversational AI prototype built with
> Python and FastAPI. I designed a hybrid architecture combining
> deterministic safety rules, a TF-IDF + Logistic Regression classifier,
> contextual analysis and response generation. The key design decision
> is that high-risk safety decisions are controlled by deterministic
> rules instead of being delegated entirely to an LLM. I also
> implemented API security, rate limiting, persistent safety auditing,
> automated regression testing and Docker deployment. The current suite
> has 230 passing tests, and the ML benchmark achieved 100% test
> accuracy on a synthetic, non-clinical dataset.

### Hardest engineering problem

> Preventing the ML or LLM layer from masking an authoritative safety
> signal. I solved this by giving deterministic safety rules precedence
> and recording the decision source in the audit system.

### Main trade-off

> I chose deterministic safety authority over maximum generative
> flexibility because predictable, testable and auditable behavior is
> more important in the safety path.

## Documentation

-   [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)
-   [`docs/SAFETY_DESIGN.md`](docs/SAFETY_DESIGN.md)
-   [`docs/EVALUATION.md`](docs/EVALUATION.md)

## Project Status

**Version:** 1.2.0\
**API:** FastAPI\
**ML:** TF-IDF + Logistic Regression\
**Safety:** Deterministic + hybrid decision architecture\
**Audit:** Persistent JSONL\
**Testing:** 230 passing tests\
**Deployment:** Docker Compose + Gunicorn + Uvicorn\
**Dataset:** 1,200 synthetic, non-clinical examples
