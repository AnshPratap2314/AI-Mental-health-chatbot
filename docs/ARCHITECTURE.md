# MindCare AI --- Architecture

## 1. Design Goal

MindCare separates API handling, analysis, decision-making, response
generation, and auditing.

The core principle is:

> **Analysis ≠ decision ≠ generation ≠ audit**

The LLM is a generation component, not the final authority for high-risk
safety decisions.

## 2. System Architecture

``` text
User / Frontend
      │
      ▼
FastAPI
      │
      ├── CORS
      ├── Validation
      ├── Rate Limiting
      └── Security Headers
      │
      ▼
Session Manager
      │
      ▼
Behavior Engine
      │
      ├── Rule Engine
      ├── ML Classifier
      └── Context Engine
      │
      ▼
Hybrid Risk Engine
      │
      ▼
Safety Policy
      │
      ├── High Risk → Deterministic Safety Response
      │
      └── Normal → Response/LLM Path
                         │
                         ▼
                  Safety Validation
                         │
                         ▼
                   Safety Audit
                         │
                         ▼
                 Persistent JSONL
```

## 3. Components

### `app/main.py`

Owns the FastAPI application, middleware, endpoints, validation, rate
limiting, audit endpoints and application wiring.

### `app/behavior_engine.py`

Coordinates message analysis, context, safety signals, hybrid decisions
and response strategy.

### `app/ml/`

Contains the ML components:

-   dataset handling
-   labels
-   TF-IDF classifier
-   rule engine
-   hybrid engine

### `app/llm_engine.py`

Handles permitted LLM generation and generation-side safety filtering.

### `app/safety_engine.py`

Converts analysis into safety-policy decisions.

### `app/safety_policy.py`

Defines the safety-response requirements for different risk states.

### `app/safety_audit.py`

Persists structured safety-decision metadata using JSONL and file
locking.

### `app/session_manager.py`

Maintains process-local conversation sessions and TTL behavior.

### `app/logging_config.py`

Configures application logging while avoiding normal storage of
sensitive chatbot content.

## 4. Request Flow

``` text
POST /chat
   ↓
Pydantic validation
   ↓
Rate-limit check
   ↓
Session lookup
   ↓
Behavior analysis
   ↓
Rule analysis + ML + context
   ↓
Hybrid decision
   ↓
Safety policy
   ↓
Response strategy
   ↓
LLM/deterministic response where allowed
   ↓
Audit record
   ↓
JSON response
```

## 5. Decision Precedence

Configured safety signals have precedence over ordinary ML output.

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
hybrid / ML result
```

This prevents a neutral ML prediction from masking a high-risk rule
signal.

## 6. High-Risk Flow

``` text
Message
  ↓
Risk analysis
  ↓
High risk?
  ↓ YES
Deterministic safety path
  ├── human support = true
  ├── immediate guidance = true
  ├── crisis mode
  └── audit
```

The normal LLM response path is not the controlling path for the
high-risk decision.

## 7. Normal Flow

``` text
Message
  ↓
Analysis
  ↓
Low/moderate non-crisis result
  ↓
Response strategy
  ├── deterministic response
  └── LLM response when permitted
  ↓
Safety validation
  ↓
Audit
```

## 8. LLM Boundary

The LLM can generate conversational language but is subject to a safety
gate.

``` text
Safety Policy
     ↓
LLM permitted?
  ├── NO  → deterministic safety response
  └── YES → LLM generation
```

Dangerous instructional patterns are blocked.

## 9. Session Architecture

Current design:

``` text
FastAPI
  ↓
SessionManager
  ├── session ID
  ├── profile
  ├── conversation state
  ├── recent context
  └── TTL
```

Session state is process-local. Therefore the current Docker deployment
uses one worker.

For horizontal scaling, move session state to shared infrastructure such
as Redis or a database.

## 10. Audit Architecture

``` text
Risk Decision
     ↓
SafetyAudit
     ↓
JSON serialization
     ↓
File lock
     ↓
logs/safety_audit.jsonl
     ↓
Docker persistent volume
```

Audit records include decision metadata but intentionally omit the
original message, username, IP, credentials and full session ID.

## 11. Security Flow

``` text
Request
  ↓
CORS
  ↓
Method handling
  ↓
Pydantic validation
  ↓
Rate limiting
  ↓
Audit authentication where required
  ↓
Application logic
```

Implemented controls include bounded inputs, CORS allowlisting, rate
limiting, authenticated audit endpoints and security headers.

## 12. Docker

``` text
Docker Compose
      ↓
mindcare-api
      ↓
Gunicorn
      ↓
Uvicorn worker
      ↓
FastAPI
```

Current mapping:

``` text
host 8001 → container 8000
```

Healthcheck:

``` text
GET /health
```

Logs/audit data are stored through the configured Docker volume.

## 13. Persistence and Concurrency

The audit implementation uses:

-   JSONL persistence
-   bounded history
-   file locks
-   refresh-on-read
-   persistent source-of-truth reads
-   graceful persistence failure handling

This allows persisted audit history to remain available after container
restart.

## 14. ML Architecture

``` text
1,200-example synthetic dataset
       ↓
840 train / 180 validation / 180 test
       ↓
TF-IDF
       ↓
Logistic Regression
       ↓
class + probabilities
       ↓
Hybrid Risk Engine
       ↓
Safety Policy
```

## 15. Architectural Trade-offs

### Deterministic safety vs LLM flexibility

Deterministic authority provides predictable, testable behavior at the
cost of some flexibility.

### JSONL vs database

JSONL is simple and inspectable for the current prototype. A high-volume
deployment would benefit from a dedicated durable audit store.

### In-memory sessions vs shared state

In-memory sessions simplify the current deployment but limit horizontal
scaling.

### Classical ML vs large neural model

TF-IDF + Logistic Regression is lightweight, inexpensive and easy to
inspect, but has less semantic generalization than larger models.

## 16. Future Scalable Architecture

``` text
Load Balancer
     │
 ┌───┴────┐
 ▼        ▼
API #1   API #2
 │        │
 └──┬────┘
    │
 ┌──┼───────────────┐
 ▼  ▼               ▼
Redis PostgreSQL  Model Store
 │    │               │
 └────┼───────────────┘
      ▼
Audit / Metrics / Monitoring
```

This is a future architecture, not a current implementation claim.

## 17. Production Boundary

Current project status should be described as a **production-style AI
safety prototype**.

It should not be described as:

-   clinically validated
-   a medical device
-   a diagnostic service
-   a guaranteed crisis detector
-   a regulatory-approved healthcare system

## 18. Summary

The architecture intentionally separates:

``` text
analysis
   ↓
decision
   ↓
generation
   ↓
audit
```

This separation is the central engineering property of MindCare AI.
