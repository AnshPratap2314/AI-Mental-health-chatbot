<div align="center">

# 🧠 MindCare AI

### Safety-First Supportive Conversational AI

**A full-stack AI/ML project combining safety-aware risk analysis, contextual conversation routing, a 50K-message response model, FastAPI backend engineering, automated testing, and live deployment.**

<br>

<a href="https://mindcare-ai-o1e5.onrender.com" target="_blank" rel="noopener noreferrer">
  <img src="https://img.shields.io/badge/%E2%96%B6%20LIVE%20DEMO-MindCare%20AI-6C63FF?style=for-the-badge&logo=render&logoColor=white" alt="Live Demo">
</a>
&nbsp;
<a href="https://mindcare-ai-semb.onrender.com/health" target="_blank" rel="noopener noreferrer">
  <img src="https://img.shields.io/badge/API-HEALTHY-16A34A?style=for-the-badge&logo=fastapi&logoColor=white" alt="API Health">
</a>
&nbsp;
<a href="https://github.com/AnshPratap2314/AI-Mental-health-chatbot" target="_blank" rel="noopener noreferrer">
  <img src="https://img.shields.io/badge/GITHUB-REPOSITORY-181717?style=for-the-badge&logo=github&logoColor=white" alt="GitHub Repository">
</a>

<br><br>

<img src="https://img.shields.io/badge/Python-3.11-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python 3.11">
<img src="https://img.shields.io/badge/FastAPI-REST%20API-009688?style=flat-square&logo=fastapi&logoColor=white" alt="FastAPI">
<img src="https://img.shields.io/badge/ML-Hybrid%20Architecture-F59E0B?style=flat-square" alt="Hybrid ML">
<img src="https://img.shields.io/badge/Response%20Model-50K%20Messages-7C3AED?style=flat-square" alt="50K response model">
<img src="https://img.shields.io/badge/Tests-238%20Passing-16A34A?style=flat-square" alt="238 tests passing">
<img src="https://img.shields.io/badge/Deployment-Render-46E3B7?style=flat-square&logo=render&logoColor=111827" alt="Render">

</div>

---

## 📌 At a Glance

| | |
|---|---|
| **Project** | MindCare AI |
| **Type** | Full-stack AI/ML conversational application |
| **Primary focus** | Safety-aware supportive conversation |
| **Backend** | Python + FastAPI |
| **Frontend** | HTML + CSS + JavaScript |
| **Response model** | `mindcare-response-50k` |
| **Response dataset** | 50,000 messages |
| **Tests** | **238 passed** |
| **Deployment** | Render |
| **API version** | `1.2.0` |
| **Developer** | Ansh Pratap |

> **Responsible-use note:** MindCare is a supportive AI application and engineering project. It is **not** a medical diagnostic system, replacement for a qualified professional, treatment service, or emergency response service.

---

## 🚀 Quick Links

<table>
<tr>
<td align="center">

**🌐 Product**

<a href="https://mindcare-ai-o1e5.onrender.com" target="_blank" rel="noopener noreferrer"><strong>Open Live Demo ↗</strong></a>

</td>
<td align="center">

**⚡ API**

<a href="https://mindcare-ai-semb.onrender.com" target="_blank" rel="noopener noreferrer"><strong>Open Backend ↗</strong></a>

</td>
<td align="center">

**💚 Health**

<a href="https://mindcare-ai-semb.onrender.com/health" target="_blank" rel="noopener noreferrer"><strong>Check API Health ↗</strong></a>

</td>
<td align="center">

**💻 Source**

<a href="https://github.com/AnshPratap2314/AI-Mental-health-chatbot" target="_blank" rel="noopener noreferrer"><strong>View GitHub ↗</strong></a>

</td>
</tr>
</table>

---

## 🧠 What is MindCare?

**MindCare AI** is a safety-first conversational AI application designed to provide supportive conversations around:

- everyday emotions
- stress and difficult days
- loneliness
- anxiety
- academic pressure
- exam stress
- uncertainty and overwhelm

The important engineering goal is not simply to generate a fluent response.

MindCare is designed around a stronger question:

> **How can a conversational AI system remain useful while keeping safety and risk decisions independent from the response-generation model?**

To achieve this, the project separates **safety analysis**, **conversation routing**, and **response generation**.

---

# ⭐ What Makes This Project Different?

### 01 · Safety is an independent layer

The response model is **not** the authority for crisis or self-harm decisions.

Safety/risk analysis happens separately before response generation.

### 02 · 50K-message response pipeline

The current response system uses a dedicated **50,000-message dataset** with:

- 40,000 training messages
- 5,000 validation messages
- 5,000 test messages
- 20 balanced intents
- 18,009 unique response texts
- zero normalized message duplicates
- zero cross-split leakage

### 03 · Built as an actual software system

The project includes much more than an ML model:

- FastAPI REST API
- session management
- request validation
- rate limiting
- CORS
- security headers
- safety audit logging
- health/readiness endpoints
- automated regression tests
- production deployment

### 04 · Regression-driven development

The current full regression suite reports:

```text
238 passed
```

This was used to validate major safety, routing, response-model, API, and deployment-related changes.

---

# 🏗️ System Architecture

```text
                         ┌───────────────────────────┐
                         │        USER / BROWSER      │
                         └─────────────┬─────────────┘
                                       │
                                       ▼
                         ┌───────────────────────────┐
                         │     MindCare Frontend     │
                         │    HTML / CSS / JavaScript │
                         └─────────────┬─────────────┘
                                       │ HTTPS / REST
                                       ▼
                    ┌──────────────────────────────────────┐
                    │            FastAPI Backend            │
                    │                                      │
                    │  Validation · Sessions · Rate Limits │
                    │  CORS · Security Headers · Audit     │
                    └──────────────────┬───────────────────┘
                                       │
                                       ▼
                         ┌───────────────────────────┐
                         │    Safety / Risk Layer    │
                         │                           │
                         │ Crisis · Self-Harm        │
                         │ Negation · Protective     │
                         │ Signals · Risk Score      │
                         └─────────────┬─────────────┘
                                       │
                                       ▼
                         ┌───────────────────────────┐
                         │ Conversation / Intent     │
                         │ Routing                   │
                         │                           │
                         │ Exam · Academic · Mood   │
                         │ Loneliness · Anxiety      │
                         │ Difficult Day · General  │
                         └─────────────┬─────────────┘
                                       │
                                       ▼
                         ┌───────────────────────────┐
                         │      Response Engine      │
                         └─────────────┬─────────────┘
                                       │
                    ┌──────────────────┼──────────────────┐
                    ▼                  ▼                  ▼
             ┌─────────────┐   ┌─────────────┐   ┌─────────────┐
             │ Trained     │   │ Optional    │   │ Deterministic│
             │ Response    │   │ LLM Support │   │ Fallback     │
             │ Model       │   │             │   │              │
             └─────────────┘   └─────────────┘   └─────────────┘
                    │                  │                  │
                    └──────────────────┼──────────────────┘
                                       ▼
                         ┌───────────────────────────┐
                         │   Safety-Aware Response   │
                         └───────────────────────────┘
```

---

# 🛡️ Safety-First Design

A core architectural decision is:

> **Safety/risk decisions must not depend solely on the response model.**

The system therefore separates:

```text
User message
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

This makes important behavior easier to:

- test
- audit
- reason about
- reproduce
- protect from model-routing regressions

---

## 🔐 Negation-Aware Safety Detection

One important safety regression was identified and fixed.

A naive keyword system can incorrectly interpret:

```text
"I am not suicidal and I do not want to hurt myself"
```

as a high-risk message simply because words such as `suicidal` and `hurt myself` appear.

MindCare handles recognized negated safety phrases before evaluating relevant crisis/self-harm patterns.

Expected behavior for examples such as:

```text
"I am not suicidal"
"I don't want to hurt myself"
"I am not suicidal and I do not want to hurt myself"
```

is:

```text
risk = low
risk_score = 0.0
crisis = false
self_harm = false
protective = true
```

This is an example of using deterministic logic where predictable safety behavior matters.

---

# 💬 Context-Aware Conversation Routing

MindCare does not treat every message as generic conversation.

### 🎓 Exam Stress

```text
"I have exam stress"
```

is routed toward an academic/exam context.

### 📚 Academic Overwhelm

```text
"my exams are coming and till now I have read nothing"
```

is handled as an academic-pressure conversation.

### 🌱 Loneliness

```text
"I feel lonely today"
```

is treated as an emotional/loneliness conversation rather than incorrectly triggering the ordinary-stress rule.

### 🌧️ Difficult Days

The response pipeline includes dedicated routing/phrase hints for difficult-day and overwhelm-related conversations.

---

# 🤖 AI / ML Response System

Current model identifier:

```text
mindcare-response-50k
```

The response system was migrated to a 50K-message dataset with:

```text
40,000 training
5,000 validation
5,000 test
```

### Current development evaluation

| Metric | Result |
|---|---:|
| Intent / Risk accuracy | **1.0000** |
| Mood accuracy | **~0.867** |
| Topic accuracy | **~0.868** |
| Mean retrieval similarity | **~0.8587** |

> These are development/evaluation metrics for the current model and are **not clinical validation metrics**.

---

# 📚 50K Dataset

The current response dataset contains:

| Property | Value |
|---|---:|
| Total messages | **50,000** |
| Train | **40,000** |
| Validation | **5,000** |
| Test | **5,000** |
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

The dataset includes varied examples for areas including:

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

The dataset is **synthetic development/training data**. It should not be represented as clinically validated human data.

---

# 🧪 Testing & Quality

The current regression suite:

```text
238 passed in 81.84s
```

Run it with:

```bash
pytest -q
```

The tests cover important areas including:

- API behavior
- API security
- CORS/security configuration
- safety behavior
- natural response behavior
- response-model integration
- session behavior
- routing behavior
- regression cases

### Why this matters

For an AI application, changing a model or routing rule can unintentionally break previously correct behavior.

MindCare therefore treats regression testing as part of the development workflow rather than as an afterthought.

---

# 🔒 Backend Engineering

## Input Validation

FastAPI/Pydantic models validate request payloads including:

- user name
- session ID
- message length
- required fields

## Session Management

The backend supports:

- isolated conversation sessions
- session creation
- session lookup
- session expiration
- session deletion
- configurable session limits

## Rate Limiting

Separate controls exist for:

- chat requests
- session creation

## CORS

The production backend explicitly controls allowed frontend origins.

Current frontend:

```text
https://mindcare-ai-o1e5.onrender.com
```

Alternate supported frontend:

```text
https://ai-mental-health-chatbot-nm2r.onrender.com
```

## Security Headers

The API applies headers including:

```text
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
Referrer-Policy: no-referrer
Cache-Control: no-store
```

## Safety Auditing

Safety-related decisions can be recorded using the project's `SafetyAudit` component.

Protected audit endpoints are available when audit authentication is configured.

---

# 🔌 REST API

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/` | API information |
| `GET` | `/health` | Health check |
| `GET` | `/health/live` | Liveness check |
| `GET` | `/health/ready` | Readiness information |
| `POST` | `/session` | Create conversation session |
| `POST` | `/chat` | Send message |
| `DELETE` | `/session/{session_id}` | Delete session |
| `GET` | `/api/status` | API status/configuration |
| `GET` | `/api/audit/count` | Audit record count |
| `GET` | `/api/audit/recent` | Recent audit records |

### Example: create a session

```http
POST /session
Content-Type: application/json
```

```json
{
  "user_name": "friend"
}
```

### Example: send a message

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

The response can contain:

```json
{
  "session_id": "...",
  "mode": "...",
  "risk_level": "low",
  "risk_score": 0.05,
  "signals": {},
  "context": {},
  "response_source": "...",
  "response_model": "mindcare-response-50k",
  "decision_source": "...",
  "reply": "..."
}
```

---

# 🧰 Technology Stack

### Backend

`Python 3.11` · `FastAPI` · `Uvicorn` · `Pydantic` · `python-dotenv`

### AI / ML

`NumPy` · `Pandas` · `Scikit-learn` · trained response model · retrieval/similarity pipeline · optional LLM integration

### Frontend

`HTML5` · `CSS3` · `JavaScript`

### Engineering

`Git` · `GitHub` · `pytest` · virtual environments · REST APIs · environment configuration

### Deployment

`Render`

### Containerization

`Docker` / `docker-compose` configuration is included for reproducible container workflows.

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
│   │
│   ├── ml/
│   │   ├── hybrid_engine.py
│   │   └── rule_engine.py
│   │
│   ├── logging_config.py
│   ├── production_config.py
│   ├── safety_audit.py
│   ├── security.py
│   └── session_manager.py
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
│       └── ...
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
├── docker-compose.yml
├── pytest.ini
├── requirements.txt
├── README.md
└── .env.example
```

---

# ⚙️ Local Setup

## 1. Clone

<a href="https://github.com/AnshPratap2314/AI-Mental-health-chatbot" target="_blank" rel="noopener noreferrer">Open the GitHub repository ↗</a>

```bash
git clone https://github.com/AnshPratap2314/AI-Mental-health-chatbot.git
cd AI-Mental-health-chatbot
```

## 2. Create virtual environment

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

Configure the required environment variables for your local setup.

**Never commit API keys, credentials, or production secrets.**

---

# ▶️ Run the Backend

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Backend:

```text
http://127.0.0.1:8000
```

Health:

```text
http://127.0.0.1:8000/health
```

---

# 🌐 Run the Frontend

From the frontend directory:

```bash
cd Frontend
python3 -m http.server 5500
```

Open:

```text
http://localhost:5500
```

For local development, the frontend uses:

```text
http://127.0.0.1:8000
```

For the deployed application, it uses the Render backend.

---

# ☁️ Deployment

MindCare is currently deployed as two Render services.

### Frontend

```text
Render Static Site
        ↓
https://mindcare-ai-o1e5.onrender.com
```

### Backend

```text
Render Web Service
        ↓
https://mindcare-ai-semb.onrender.com
```

### Production flow

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

The frontend/backend integration has been verified after correcting the production CORS configuration.

---

# 🐳 Docker

Docker configuration is included in the project for reproducible local/container workflows.

Docker is **not required** for the current Render deployment path.

This keeps the production deployment simpler while preserving containerization support for future deployment requirements.

---

# 📈 Engineering Highlights for Recruiters

If you are reviewing this project from an engineering perspective, the strongest areas are:

### 🧠 AI/ML Engineering

- trained a dedicated 50K-message response dataset
- created balanced train/validation/test splits
- evaluated intent/risk, mood, topic, and retrieval similarity
- implemented response routing and retrieval behavior
- considered response diversity and naturalness

### 🛡️ AI Safety

- separated safety decisions from response generation
- implemented negation-aware safety handling
- protected crisis/self-harm routing from naive keyword behavior
- added safety audit infrastructure
- wrote regression tests for safety-critical cases

### ⚙️ Backend Engineering

- built a FastAPI REST backend
- added Pydantic validation
- implemented session lifecycle management
- added rate limiting
- implemented CORS
- added security headers
- created health/live/readiness endpoints

### 🧪 Software Quality

- maintained a 238-test regression suite
- tested API security
- tested response behavior
- tested routing regressions
- validated model integration after major changes

### ☁️ Deployment

- deployed frontend and backend separately on Render
- configured frontend/backend communication
- handled production CORS
- exposed health monitoring endpoints

---

# 📊 Current Project Status

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
| Docker support | 🟢 Available |

---

# 🔮 Future Engineering Roadmap

The next potential improvements include:

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

These are **future directions**, not current functionality.

---

# ⚠️ Responsible AI

MindCare is an educational and engineering project for supportive conversational AI.

It should **not** be used as:

- a medical diagnostic system
- a clinical decision-making system
- a replacement for a therapist or doctor
- an emergency response service
- a substitute for professional treatment

The 50K training dataset is synthetic development/training data, and the reported model metrics are engineering evaluation metrics rather than clinical validation.

---

# 👨‍💻 Developer

<div align="center">

## Ansh Pratap

**B.Tech Computer Science & Engineering**  
Mewar University, Rajasthan, India

**Focus:** Artificial Intelligence · Machine Learning · Python · Software Engineering · NLP/LLM Applications · AI Safety

<br>

<a href="https://github.com/AnshPratap2314" target="_blank" rel="noopener noreferrer">
  <img src="https://img.shields.io/badge/GitHub-AnshPratap2314-181717?style=for-the-badge&logo=github&logoColor=white" alt="GitHub">
</a>
&nbsp;
<a href="https://github.com/AnshPratap2314/AI-Mental-health-chatbot" target="_blank" rel="noopener noreferrer">
  <img src="https://img.shields.io/badge/Project-AI--Mental--health--chatbot-6C63FF?style=for-the-badge&logo=github&logoColor=white" alt="Project Repository">
</a>

</div>

---

# 📄 License

Add the project's intended open-source license before public distribution.

If this repository is intended to be open source, add the selected license as a separate `LICENSE` file.

---

<div align="center">

### 🧠 MindCare AI

**Safety-first conversational AI, engineered as a complete software system.**

<br>

<a href="https://mindcare-ai-o1e5.onrender.com" target="_blank" rel="noopener noreferrer"><strong>🚀 Try the Live Demo ↗</strong></a>
&nbsp;&nbsp;•&nbsp;&nbsp;
<a href="https://github.com/AnshPratap2314/AI-Mental-health-chatbot" target="_blank" rel="noopener noreferrer"><strong>💻 View Source ↗</strong></a>

<br><br>

*Built with Python · FastAPI · Machine Learning · JavaScript · Testing · Responsible AI*

</div>
