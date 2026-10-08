<div align="center">

# 🧠 MindCare AI

### Safety-First Conversational AI, Engineered as a Real Software System

<p>
  <a href="https://mindcare-ai-o1e5.onrender.com">
    <img src="https://img.shields.io/badge/%E2%96%B6%20LIVE%20DEMO-MindCare%20AI-6C63FF?style=for-the-badge&logo=render&logoColor=white" alt="Live Demo">
  </a>
  <a href="https://mindcare-ai-semb.onrender.com/health">
    <img src="https://img.shields.io/badge/API-HEALTHY-16A34A?style=for-the-badge&logo=fastapi&logoColor=white" alt="API Health">
  </a>
  <a href="https://github.com/AnshPratap2314/AI-Mental-health-chatbot">
    <img src="https://img.shields.io/badge/GITHUB-SOURCE-181717?style=for-the-badge&logo=github&logoColor=white" alt="GitHub">
  </a>
</p>

<p>
  <img src="https://img.shields.io/badge/Python-3.11-3776AB?style=flat-square&logo=python&logoColor=white">
  <img src="https://img.shields.io/badge/FastAPI-REST%20API-009688?style=flat-square&logo=fastapi&logoColor=white">
  <img src="https://img.shields.io/badge/ML-Hybrid%20Architecture-F59E0B?style=flat-square">
  <img src="https://img.shields.io/badge/Response%20Model-50K%20Messages-7C3AED?style=flat-square">
  <img src="https://img.shields.io/badge/Tests-238%20Passing-16A34A?style=flat-square">
  <img src="https://img.shields.io/badge/Docker-Supported-2496ED?style=flat-square&logo=docker&logoColor=white">
  <img src="https://img.shields.io/badge/Deployment-Render-46E3B7?style=flat-square&logo=render&logoColor=111827">
</p>

<p><strong>MindCare is a full-stack AI/ML application that separates safety decisions from response generation, combines deterministic safety logic with ML-based routing and a trained 50K-message response model, and exposes the system through a production-style FastAPI backend.</strong></p>

</div>

---

## 🚀 Start Here

| | |
|---|---|
| 🌐 **Live Demo** | https://mindcare-ai-o1e5.onrender.com |
| ⚡ **Backend API** | https://mindcare-ai-semb.onrender.com |
| 💚 **API Health** | https://mindcare-ai-semb.onrender.com/health |
| 💻 **Repository** | https://github.com/AnshPratap2314/AI-Mental-health-chatbot |
| 🧠 **Response Model** | `mindcare-response-50k` |
| 📦 **Response Dataset** | 50,000 messages |
| 🧪 **Regression Suite** | **238 tests passing** |
| 🐍 **Backend** | Python 3.11 + FastAPI |
| ☁️ **Deployment** | Render |
| 🐳 **Containerization** | Docker / Docker Compose |

> **Recruiter takeaway:** This project is not just a chatbot UI. It demonstrates AI/ML, backend engineering, safety-aware system design, testing, model evaluation, API security, containerization, and production deployment in one project.

---

# ⭐ Why This Project Is Worth Looking At

Most conversational-AI projects stop at:

**user message → LLM → response**

MindCare takes a different engineering approach:

```text
User Message
     │
     ▼
Safety / Risk Analysis
     │
     ▼
Conversation & Intent Routing
     │
     ▼
Response Engine
     │
     ├── Trained 50K Response Model
     ├── Optional LLM Support
     └── Deterministic Fallback
     │
     ▼
Safety-Aware Response
```

The key architectural principle is:

> **The model that generates a response is not the authority for safety/risk decisions.**

This makes safety-critical behavior easier to test, audit, reason about, and reproduce.

---

# 🧠 What Is MindCare?

**MindCare AI** is a safety-first supportive conversational application designed for conversations around:

- everyday emotions
- loneliness
- anxiety
- stress
- academic pressure
- exam stress
- uncertainty
- difficult days
- overwhelm

The engineering challenge is not simply generating fluent text.

The project focuses on building a system that can:

1. analyze risk independently,
2. recognize conversation context,
3. route messages to appropriate behavior,
4. retrieve/generate an appropriate response,
5. maintain session state,
6. validate and protect API requests,
7. test behavior against regressions,
8. run locally through Docker,
9. and operate as a deployed web application.

---

# 🏗️ System Architecture

```text
                         ┌──────────────────────────┐
                         │      USER / BROWSER      │
                         └────────────┬─────────────┘
                                      │
                                      ▼
                         ┌──────────────────────────┐
                         │    MindCare Frontend     │
                         │    HTML / CSS / JS       │
                         └────────────┬─────────────┘
                                      │ HTTPS / REST
                                      ▼
                  ┌────────────────────────────────────┐
                  │          FastAPI Backend            │
                  │                                    │
                  │ Validation · Sessions · Rate Limit │
                  │ CORS · Security Headers · Audit    │
                  └──────────────────┬─────────────────┘
                                     │
                                     ▼
                         ┌──────────────────────────┐
                         │     Safety / Risk       │
                         │        Layer            │
                         │                          │
                         │ Crisis · Self-Harm      │
                         │ Negation · Protective   │
                         │ Signals · Risk Score    │
                         └────────────┬─────────────┘
                                      │
                                      ▼
                         ┌──────────────────────────┐
                         │ Conversation / Intent     │
                         │ Routing                   │
                         │                          │
                         │ Exam · Academic · Mood   │
                         │ Loneliness · Anxiety     │
                         │ Overwhelm · General     │
                         └────────────┬─────────────┘
                                      │
                                      ▼
                         ┌──────────────────────────┐
                         │      Response Engine      │
                         └────────────┬─────────────┘
                                      │
                     ┌────────────────┼────────────────┐
                     ▼                ▼                ▼
              ┌────────────┐  ┌────────────┐  ┌────────────┐
              │ 50K Trained│  │ Optional   │  │Deterministic│
              │ Response   │  │ LLM        │  │ Fallback    │
              │ Model      │  │ Support    │  │             │
              └────────────┘  └────────────┘  └────────────┘
                     │                │                │
                     └────────────────┼────────────────┘
                                      ▼
                         ┌──────────────────────────┐
                         │   Safety-Aware Reply     │
                         └──────────────────────────┘
```

---

# 🛡️ Safety-First Engineering

A central design decision is to keep safety/risk analysis separate from response generation.

```text
User Message
     │
     ▼
Safety / Risk Analysis
     │
     ▼
Conversation Controls
     │
     ▼
Response Engine
     │
     ├── Trained Response Model
     ├── Optional LLM
     └── Deterministic Fallback
```

### Why this matters

A generative model should not be trusted as the only mechanism deciding whether a message contains a safety-critical signal.

MindCare therefore uses deterministic and structured logic for important safety decisions, while the response model focuses on producing useful conversational output.

This separation improves:

- testability
- auditability
- reproducibility
- debugging
- regression protection
- explainability of safety behavior

---

## 🔐 Negation-Aware Safety Detection

A naive keyword matcher can incorrectly treat:

```text
"I am not suicidal and I do not want to hurt myself"
```

as high risk simply because it contains words such as `suicidal` and `hurt myself`.

MindCare explicitly handles recognized negated safety phrases before evaluating relevant crisis/self-harm patterns.

Examples:

```text
"I am not suicidal"
"I don't want to hurt myself"
"I am not suicidal and I do not want to hurt myself"
```

are expected to remain low-risk rather than being incorrectly escalated.

This is a small feature with an important engineering lesson:

> **Safety systems need semantic/rule-aware handling, not just raw keyword matching.**

---

# 💬 Context-Aware Conversation Routing

MindCare routes different types of messages differently instead of treating every input as generic conversation.

### 🎓 Exam Stress

```text
"I have exam stress"
```

→ exam/academic context

### 📚 Academic Overwhelm

```text
"I have too much college work and I feel overwhelmed"
```

→ academic/work-stress context

### 🌱 Loneliness

```text
"I feel lonely today"
```

→ emotional/loneliness context

### 🌧️ Difficult Days

The response pipeline also contains dedicated routing and phrase hints for difficult-day and overwhelm-related conversations.

---

# 🤖 50K Response Model

Current model:

```text
mindcare-response-50k
```

The response system uses a dedicated 50,000-message dataset:

| Split | Messages |
|---|---:|
| Training | **40,000** |
| Validation | **5,000** |
| Test | **5,000** |
| Total | **50,000** |

### Development evaluation

| Metric | Result |
|---|---:|
| Intent / Risk accuracy | **1.0000** |
| Mood accuracy | **~0.867** |
| Topic accuracy | **~0.868** |
| Mean retrieval similarity | **~0.8587** |

> These are development/evaluation metrics for the current model. They are **not clinical validation metrics**.

---

# 📊 Dataset Quality

The response dataset was structured to reduce common data-quality problems:

| Property | Value |
|---|---:|
| Total messages | **50,000** |
| Intents | **20** |
| Messages per intent | **2,500** |
| Unique normalized messages | **50,000** |
| Unique responses | **18,009** |
| Normalized duplicates | **0** |
| Train ↔ Validation overlap | **0** |
| Train ↔ Test overlap | **0** |
| Validation ↔ Test overlap | **0** |
| High-risk rows | **2,500** |
| English | **43,556** |
| Hinglish | **6,444** |

The dataset includes examples covering:

- greetings
- general conversation
- loneliness
- anxiety
- difficult days
- uncertainty
- sleep-related concerns
- study pressure
- academic stress
- work stress
- exam stress
- safety-oriented/high-risk conversations

**Important:** the 50K dataset is synthetic development/training data. It should not be represented as clinically validated human data.

---

# 🧪 Testing & Regression Engineering

MindCare currently reports:

```text
238 passed
```

Run the suite with:

```bash
pytest -q
```

The tests cover areas including:

- API behavior
- API security
- CORS/security configuration
- safety behavior
- response-model integration
- natural response behavior
- session behavior
- conversation routing
- regression cases

### Why regression testing matters

AI systems can regress in ways that are not obvious.

For example, changing a response model or routing rule can accidentally break:

- safety classification,
- negation handling,
- loneliness behavior,
- exam-stress routing,
- API behavior,
- response metadata.

MindCare therefore treats regression testing as part of the development process rather than as a final step.

---

# 🔒 Backend Engineering

MindCare is implemented as a real REST backend rather than a notebook-only ML project.

### Input validation

FastAPI/Pydantic validates:

- session IDs
- required fields
- message length
- request payload structure

### Session management

Supports:

- session creation
- isolated conversation sessions
- session lookup
- session expiration
- session deletion
- configurable session limits

### Rate limiting

Separate controls are available for:

- chat requests
- session creation

### CORS

Production frontend origins are explicitly controlled by the backend.

### Security headers

The API applies headers including:

```text
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
Referrer-Policy: no-referrer
Cache-Control: no-store
```

### Safety auditing

Safety-related decisions can be recorded through the project's audit infrastructure when audit authentication is configured.

---

# 🔌 REST API

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/` | API information |
| `GET` | `/health` | Health check |
| `GET` | `/health/live` | Liveness |
| `GET` | `/health/ready` | Readiness |
| `POST` | `/session` | Create conversation session |
| `POST` | `/chat` | Send message |
| `DELETE` | `/session/{session_id}` | Delete session |
| `GET` | `/api/status` | API status/configuration |
| `GET` | `/api/audit/count` | Audit record count |
| `GET` | `/api/audit/recent` | Recent audit records |

### Example

Create a session:

```http
POST /session
Content-Type: application/json
```

```json
{
  "user_name": "friend"
}
```

Send a message:

```http
POST /chat
Content-Type: application/json
```

```json
{
  "session_id": "YOUR_SESSION_ID",
  "message": "I have exam stress"
}
```

The response can include:

```json
{
  "session_id": "...",
  "mode": "...",
  "risk_level": "low",
  "risk_score": 0.05,
  "signals": {},
  "context": {},
  "response_source": "trained_response_model",
  "response_model": "mindcare-response-50k",
  "decision_source": "ml_positive",
  "reply": "..."
}
```

---

# 🐳 Docker & Reproducible Development

Docker support is included for reproducible local/container workflows.

Run the application with Docker Compose:

```bash
docker compose up -d --build
```

Check the container:

```bash
docker compose ps
```

Check the API:

```bash
curl http://127.0.0.1:8001/health
```

Expected:

```json
{
  "status": "healthy",
  "service": "mindcare-api",
  "version": "1.2.0"
}
```

The Docker setup also includes a healthcheck and was tested with the trained response model loaded inside the container.

> Docker is supported for reproducible local workflows. The current Render production deployment uses Render's native frontend/static-site and Python web-service setup.

---

# ☁️ Production Deployment

MindCare is deployed as two services on Render:

```text
Browser
   │
   ▼
Render Static Frontend
   │
   │ HTTPS / REST
   ▼
Render FastAPI Backend
   │
   ├── Safety Engine
   ├── Session Manager
   ├── Response Engine
   ├── 50K Response Model
   └── Safety Audit
```

### Production services

**Frontend**

```text
https://mindcare-ai-o1e5.onrender.com
```

**Backend**

```text
https://mindcare-ai-semb.onrender.com
```

**Health**

```text
https://mindcare-ai-semb.onrender.com/health
```

The production frontend/backend connection, CORS configuration, session creation, and `/chat` flow have been verified.

---

# 🧰 Technology Stack

### Backend
`Python 3.11` · `FastAPI` · `Uvicorn` · `Pydantic` · `python-dotenv`

### AI / ML
`NumPy` · `Pandas` · `Scikit-learn` · trained response model · retrieval/similarity pipeline · optional LLM integration

### Frontend
`HTML5` · `CSS3` · `JavaScript`

### Engineering
`Git` · `GitHub` · `pytest` · REST APIs · environment configuration

### Deployment & Infrastructure
`Render` · `Docker` · `Docker Compose`

---

# 📁 Project Structure

```text
AI-Mental-health-chatbot/
│
├── app/
│   ├── main.py
│   ├── behavior_engine.py
│   ├── response_engine.py
│   ├── response_model.py
│   ├── logging_config.py
│   ├── production_config.py
│   ├── safety_audit.py
│   ├── security.py
│   ├── session_manager.py
│   └── ml/
│       ├── hybrid_engine.py
│       └── rule_engine.py
│
├── Frontend/
│   ├── index.html
│   ├── script.js
│   ├── styles.css
│   └── README.md
│
├── data/
│   └── mindcare_responses/
│       ├── train.csv
│       ├── validation.csv
│       ├── test.csv
│       ├── dataset_audit.json
│       └── README.md
│
├── models/
│   └── response_model/
│       ├── response_classifier.joblib
│       ├── response_index.joblib
│       └── training_report.json
│
├── scripts/
│   ├── evaluate_response_diversity.py
│   └── ...
│
├── tests/
│   ├── test_api_security_regression.py
│   ├── test_natural_response_regression.py
│   └── ...
│
├── Dockerfile
├── docker-compose.yml
├── pytest.ini
├── requirements.txt
├── README.md
└── .env.example
```

---

# ⚙️ Run Locally

## 1. Clone

```bash
git clone https://github.com/AnshPratap2314/AI-Mental-health-chatbot.git
cd AI-Mental-health-chatbot
```

## 2. Create a virtual environment

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Windows

```bash
python -m venv .venv
.venv\Scripts\activate
```

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

## 4. Configure environment

```bash
cp .env.example .env
```

Configure the environment variables required for your local setup.

**Never commit API keys, credentials, or production secrets.**

## 5. Start the backend

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

API:

```text
http://127.0.0.1:8000
```

Health:

```text
http://127.0.0.1:8000/health
```

## 6. Start the frontend

```bash
cd Frontend
python3 -m http.server 5500
```

Open:

```text
http://localhost:5500
```

---

# 🧑‍💻 Engineering Highlights

If you are reviewing this repository as an engineering project, these are the areas I intentionally focused on:

### AI/ML
- Built a dedicated 50K-message response dataset
- Created balanced train/validation/test splits
- Evaluated intent/risk, mood, topic, and retrieval similarity
- Implemented response retrieval and routing
- Evaluated response diversity and naturalness

### AI Safety
- Separated safety decisions from response generation
- Added negation-aware safety handling
- Protected crisis/self-harm routing from naive keyword behavior
- Added safety audit infrastructure
- Added regression tests for safety-critical cases

### Backend
- Built a FastAPI REST service
- Added Pydantic request validation
- Implemented session lifecycle management
- Added rate limiting
- Configured production CORS
- Added security headers
- Added health/liveness/readiness endpoints

### Software Quality
- Maintained a 238-test regression suite
- Tested API security
- Tested response behavior
- Tested routing regressions
- Validated model integration after major changes

### Deployment
- Deployed frontend and backend separately
- Configured frontend/backend communication
- Verified production CORS
- Added Docker/Docker Compose support
- Added health monitoring

---

# 📈 Current Project Status

| Component | Status |
|---|:---:|
| Frontend | 🟢 Live |
| Backend API | 🟢 Live |
| `/health` | 🟢 Healthy |
| Frontend ↔ Backend | 🟢 Connected |
| CORS | 🟢 Configured |
| 50K response dataset | 🟢 Integrated |
| `mindcare-response-50k` | 🟢 Integrated |
| Safety/risk engine | 🟢 Implemented |
| Negation handling | 🟢 Implemented |
| Exam-stress routing | 🟢 Implemented |
| Loneliness routing | 🟢 Implemented |
| Session management | 🟢 Implemented |
| Rate limiting | 🟢 Implemented |
| Safety audit | 🟢 Implemented |
| Security headers | 🟢 Implemented |
| Regression tests | 🟢 **238 passed** |
| Render deployment | 🟢 Live |
| Docker support | 🟢 Verified |

---

# 🔭 Future Engineering Roadmap

Potential next improvements:

- human-written evaluation datasets
- stronger multilingual/Hinglish evaluation
- more rigorous safety benchmarking
- semantic evaluation of supportive responses
- human review workflows
- improved observability and production monitoring
- model/version management
- privacy-aware conversation memory
- accessibility improvements
- stronger CI/CD automation
- containerized production deployment where appropriate

These are future directions, not current functionality.

---

# ⚠️ Responsible AI

MindCare is an educational and engineering project for supportive conversational AI.

It should **not** be used as:

- a medical diagnostic system
- a clinical decision-making system
- a replacement for a therapist or doctor
- an emergency response service
- a substitute for professional treatment

The 50K dataset is synthetic development/training data, and the reported model metrics are engineering evaluation metrics rather than clinical validation.

---

# 👨‍💻 Developer

<div align="center">

## Ansh Pratap

**B.Tech Computer Science & Engineering**  
Mewar University, Rajasthan, India

**Focus:** Artificial Intelligence · Machine Learning · Python · Software Engineering · NLP/LLM Applications · AI Safety

<a href="https://github.com/AnshPratap2314">
  <img src="https://img.shields.io/badge/GitHub-AnshPratap2314-181717?style=for-the-badge&logo=github&logoColor=white" alt="GitHub">
</a>

</div>

---

# 📄 License

Add the project's intended open-source license before public distribution.

If this repository is intended to be open source, add the selected license as a separate `LICENSE` file.

---

<div align="center">

## 🧠 MindCare AI

### Safety-first conversational AI, engineered as a complete software system.

**[🚀 Try the Live Demo](https://mindcare-ai-o1e5.onrender.com)** · **[💻 View Source](https://github.com/AnshPratap2314/AI-Mental-health-chatbot)**

<br>

*Built with Python · FastAPI · Machine Learning · JavaScript · Testing · Docker · Responsible AI*

</div>
