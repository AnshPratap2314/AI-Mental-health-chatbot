# MindCare AI — Ethical Mental Health Chatbot

MindCare AI is a supportive conversational application that combines a deterministic safety layer, mood/context analysis, session memory, personalization, and an optional OpenAI LLM for natural, mood-aware responses.

> **Important:** MindCare AI is not a medical device, therapist, emergency service, or diagnostic system. Its safety classifier is designed to route conversations conservatively; it must not be treated as a clinical risk assessment.

## Architecture

```text
User message
    │
    ▼
Input validation / security
    │
    ▼
BehaviorEngine
    ├── mood detection
    ├── topic detection
    ├── contextual state
    ├── deterministic safety/risk analysis
    └── crisis policy
           │
           ├── Immediate/high risk ──► deterministic safety response
           │
           └── non-immediate ───────► ResponseEngine
                                         │
                                         ├── LLMEngine (if configured)
                                         │     ├── current mood
                                         │     ├── previous mood
                                         │     ├── mood trend
                                         │     ├── topic continuity
                                         │     ├── user tone/language
                                         │     └── recent context
                                         │
                                         └── deterministic fallback
```

### Key design principle

The **LLM generates language; it does not make the safety decision**.

High-risk/immediate conversations stay on the deterministic safety path. Moderate-risk conversations may use the LLM for empathetic, mood-aware wording while the deterministic risk decision remains authoritative.

## Mood-aware LLM behavior

The LLM receives structured conversational context such as:

- current mood
- previous mood
- recent mood trend
- mood intensity
- current topic and previous topic
- conversation mode
- user preferred tone/language
- recent user messages
- deterministic safety level

Examples of response style:

| Detected mood | Response strategy |
|---|---|
| Sad | Validate first; avoid forced positivity |
| Anxious | Calm language + one small grounding/practical step |
| Hopeless | Acknowledge heaviness + focus on one manageable next step |
| Low self-worth | Separate worth from setbacks; avoid empty praise |
| Reflective | Help the user explore what they mean |
| Seeking support | Warm + practical |
| Positive | Acknowledge the positive experience naturally |
| Neutral | Conversational and curious |

The model is explicitly instructed not to diagnose, invent personal facts, encourage dependency, or provide harmful instructions.

## LLM setup

Copy the example environment file:

```bash
cp .env.example .env
```

Set:

```env
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-5-mini
ENABLE_LLM=true
OPENAI_TIMEOUT_SECONDS=20
```

The API key must remain server-side. **Do not put it in `frontend/script.js` or expose it to the browser.**

If `OPENAI_API_KEY` is missing or the LLM cannot be initialized, MindCare automatically falls back to deterministic responses.

## Run locally

### Backend

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### Frontend

Serve the `frontend` directory with a local static server, for example:

```bash
cd frontend
python3 -m http.server 5500
```

The frontend should point to the API URL configured for the deployment.

## Environment variables

| Variable | Purpose | Default |
|---|---|---|
| `OPENAI_API_KEY` | Server-side LLM authentication | empty |
| `OPENAI_MODEL` | OpenAI model used for generation | `gpt-5-mini` |
| `ENABLE_LLM` | Enable/disable LLM generation | inferred from API key |
| `OPENAI_TIMEOUT_SECONDS` | LLM request timeout | `20` |
| `FRONTEND_URLS` | Comma-separated allowed browser origins | configured defaults |
| `API_PUBLIC_URL` | Public API URL shown by status endpoint | local/deployment value |
| `SESSION_TTL_SECONDS` | Session inactivity timeout | `1800` |
| `MAX_SESSIONS` | Maximum in-memory sessions | `1000` |
| `MAX_MEMORY` | User messages retained per session | `20` |
| `MAX_MESSAGE_LENGTH` | Maximum accepted message size | `4000` |
| `CHAT_RATE_LIMIT` | Chat requests per client per minute | `30` |

## Safety behavior

The deterministic layer handles explicit high-risk signals such as suicidal ideation, self-harm, plans, and immediate-risk language. The LLM is not used to decide whether a user is at risk.

For immediate danger, the application directs the user toward local emergency services, a crisis service, or a trusted person. It does not claim to contact emergency services itself.

## API endpoints

- `GET /` — service information
- `GET /health` — health check
- `GET /health/live` — liveness check
- `GET /health/ready` — readiness and LLM configuration status
- `POST /session` — create a conversation session
- `POST /chat` — send a message
- `DELETE /session/{session_id}` — delete a conversation session
- `GET /api/status` — deployment/API information

## Testing

Run the complete suite:

```bash
python -m pytest -q
```

Current release verification:

```text
201 passed
```

The test suite covers safety detection, nuanced crisis cases, session hardening, API flow, fallback behavior, and mood-aware LLM prompt construction.

## Privacy notes

Conversation state is held in memory for the lifetime of the session and is removed when the session expires, is deleted, or the server process is restarted. The application does not intentionally persist chat messages to a database in this version.

Session IDs should be treated as bearer credentials and must not be logged or shared.

## Production notes

Before using the project with real users, perform a separate security, privacy, clinical-safety, abuse-resistance, and legal review appropriate to the deployment jurisdiction. The current safety layer is not a substitute for professional clinical assessment.
