<div align="center">

# 🧠 MindCare AI

### Safety-First Supportive Conversational AI

**A production-deployed AI/ML application that combines independent safety/risk analysis, context-aware conversation routing, a 50K-message response model, FastAPI backend engineering, automated regression testing, Docker support, and a live web interface.**

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
  <img src="https://img.shields.io/badge/Python-3.11-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python 3.11">
  <img src="https://img.shields.io/badge/FastAPI-REST%20API-009688?style=flat-square&logo=fastapi&logoColor=white" alt="FastAPI">
  <img src="https://img.shields.io/badge/ML-Hybrid%20Architecture-F59E0B?style=flat-square" alt="Hybrid ML">
  <img src="https://img.shields.io/badge/Response%20Model-50K%20Messages-7C3AED?style=flat-square" alt="50K Response Model">
  <img src="https://img.shields.io/badge/Tests-238%20Passing-16A34A?style=flat-square" alt="238 tests passing">
  <img src="https://img.shields.io/badge/Deployment-Render-46E3B7?style=flat-square&logo=render&logoColor=111827" alt="Render">
</p>

</div>

---

## 🎯 Why I Built This

Most conversational-AI projects focus primarily on generating a response.

MindCare focuses on the **engineering around the response**: determining risk independently, routing the conversation appropriately, generating a useful response, validating the API, testing regressions, and deploying the complete application.

> **Core design principle:** safety/risk decisions should not depend solely on the response-generation model.

This separation makes the system easier to test, reason about, audit, and evolve.

---

## 🚀 At a Glance

| | |
|---|---|
| **Project** | MindCare AI |
| **Type** | Full-stack AI/ML conversational application |
| **Primary focus** | Safety-aware supportive conversation |
| **Backend** | Python 3.11 + FastAPI |
| **Frontend** | HTML + CSS + JavaScript |
| **Response model** | `mindcare-response-50k` |
| **Response dataset** | 50,000 messages |
| **Model split** | 40K train / 5K validation / 5K test |
| **Regression suite** | **238 passed** |
| **API version** | `1.2.0` |
| **Deployment** | Render |
| **Containerization** | Docker / Docker Compose |

### 🔗 Live

- **Live application:** https://mindcare-ai-o1e5.onrender.com
- **Backend health:** https://mindcare-ai-semb.onrender.com/health
- **Source code:** https://github.com/AnshPratap2314/AI-Mental-health-chatbot

---

# 🧠 What MindCare Does

MindCare provides supportive conversations around:

- everyday emotions
- stress and difficult days
- loneliness
- anxiety
- academic pressure
- exam stress
- uncertainty and overwhelm

The application is deliberately **not** presented as a medical diagnostic or treatment system.

Its engineering focus is building a conversational system with explicit safety controls and predictable behavior.

---

# ⭐ Engineering Highlights

### 1. Independent safety layer

Safety/risk analysis is separated from response generation.

The response model is **not the authority for crisis or self-harm decisions**.

The safety layer evaluates signals such as:

- crisis indicators
- self-harm indicators
- intent
- plan
- hopelessness
- worthlessness
- protective signals
- negation
- temporal/context signals

This allows safety-critical behavior to be tested independently from response quality.

### 2. Negation-aware safety handling

A keyword-only system can make a serious mistake with a message such as:

```text
I am not suicidal and I do not want to hurt myself
```

MindCare handles recognized negated safety phrases before evaluating relevant crisis/self-harm patterns.

Verified examples include:

```text
I am not suicidal
I don't want to hurt myself
I am not suicidal and I do not want to hurt myself
```

These are expected to remain **low risk** rather than being incorrectly escalated because of isolated keywords.

### 3. Context-aware routing

The system has dedicated routing behavior for cases such as:

```text
I have exam stress
```

```text
my exams are coming and till now I have read nothing
```

```text
I feel lonely today
```

This prevents every emotional message from being treated as the same generic category.

### 4. 50K-message response system

The current response model is:

```text
mindcare-response-50k
```

The dataset contains:

- **50,000 messages**
- **40,000 training**
- **5,000 validation**
- **5,000 test**
- **20 balanced intents**
- **2,500 messages per intent**
- **18,009 unique response texts**
- **0 normalized message duplicates**
- **0 cross-split message overlap**

The dataset contains English and Hinglish examples and includes conversational, emotional, academic, work, sleep, uncertainty, and safety-oriented cases.

### 5. Production-style backend

The project is not only an ML model.

The FastAPI backend includes:

- Pydantic request validation
- session lifecycle management
- session expiration and limits
- separate chat/session rate limits
- CORS configuration
- security headers
- health/live/readiness endpoints
- safety audit infrastructure
- response-model integration
- regression testing

### 6. Regression-driven development

The current full regression suite reports:

```text
238 passed
```

The suite covers API behavior, security, CORS configuration, safety behavior, session behavior, routing, response-model integration, and regression cases.

---

# 🏗️ Architecture

```text
                         ┌──────────────────────────┐
                         │      USER / BROWSER      │
                         └────────────┬─────────────┘
                                      │ HTTPS
                                      ▼
                         ┌──────────────────────────┐
                         │     MindCare Frontend    │
                         │    HTML / CSS / JS       │
                         └────────────┬─────────────┘
                                      │ REST
                                      ▼
                 ┌────────────────────────────────────────┐
                 │             FastAPI Backend             │
                 │                                        │
                 │ Validation · Sessions · Rate Limiting │
                 │ CORS · Security Headers · Audit       │
                 └───────────────────┬────────────────────┘
                                     │
                                     ▼
                 ┌────────────────────────────────────────┐
                 │          Safety / Risk Layer            │
                 │                                        │
                 │ Crisis · Self-Harm · Negation         │
                 │ Protective Signals · Risk Score       │
                 └───────────────────┬────────────────────┘
                                     │
                                     ▼
                 ┌────────────────────────────────────────┐
                 │       Conversation / Intent Routing    │
                 │                                        │
                 │ Exam · Academic · Loneliness · Mood   │
                 │ Anxiety · Difficult Day · General     │
                 └───────────────────┬────────────────────┘
                                     │
                                     ▼
                 ┌────────────────────────────────────────┐
                 │             Response Engine             │
                 └───────────────┬────────────────────────┘
                                 │
                    ┌────────────┼────────────┐
                    ▼            ▼            ▼
             ┌────────────┐ ┌───────────┐ ┌────────────┐
             │ 50K Trained│ │ Optional  │ │Deterministic│
             │ Response   │ │    LLM    │ │  Fallback  │
             │ Model      │ │  Support  │ │            │
             └────────────┘ └───────────┘ └────────────┘
                    │            │            │
                    └────────────┼────────────┘
                                 ▼
                    ┌─────────────────────────┐
                    │ Safety-Aware Response   │
                    └─────────────────────────┘
```

---

# 🤖 AI / ML System

## Current model

```text
Model: mindcare-response-50k
```

### Development evaluation

| Metric | Result |
|---|---:|
| Intent / Risk accuracy | **1.0000** |
| Mood accuracy | **~0.867** |
| Topic accuracy | **~0.868** |
| Mean retrieval similarity | **~0.8587** |

These are **engineering/development evaluation metrics**, not clinical validation metrics.

### Response generation architecture

The response pipeline follows a layered approach:

```text
User message
     │
     ▼
Safety / Risk Analysis
     │
     ▼
Conversation Controls / Routing
     │
     ▼
Response Engine
     │
     ├── Trained Response Model
     ├── Optional LLM Support
     └── Deterministic Fallback
```

The separation is intentional: response quality can evolve without making the response model responsible for safety decisions.

---

# 📚 Dataset

The current response dataset contains:

| Property | Value |
|---|---:|
| Total messages | **50,000** |
| Training | **40,000** |
| Validation | **5,000** |
| Test | **5,000** |
| Intents | **20** |
| Messages / intent | **2,500** |
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

- greetings and general conversation
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

> **Dataset note:** the 50K dataset is synthetic development/training data. It should not be represented as clinically validated human data.

---

# 🧪 Testing & Quality

The current regression suite reports:

```text
238 passed
```

Run locally with:

```bash
pytest -q
```

Testing covers areas including:

- API behavior
- API security
- CORS/security configuration
- safety behavior
- natural response behavior
- response-model integration
- session behavior
- conversation routing
- regression cases

The project uses regression testing because changes to an ML response system or routing logic can unintentionally alter previously correct behavior.

---

# 🔐 Backend Engineering

## Validation

FastAPI/Pydantic validation covers request data such as:

- session IDs
- required fields
- message length
- request payload structure

## Session management

The backend supports:

- session creation
- isolated conversation sessions
- session lookup
- session expiration
- session deletion
- configurable session limits

## Rate limiting

Separate controls are available for:

- chat requests
- session creation

## Security headers

The API applies headers including:

```text
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
Referrer-Policy: no-referrer
Cache-Control: no-store
```

## CORS

The production backend explicitly controls allowed frontend origins.

The current production frontend is:

```text
https://mindcare-ai-o1e5.onrender.com
```

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

### Example request

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

A successful response can include:

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

### Testing & Engineering

`pytest` · `Git` · `GitHub` · virtual environments · REST APIs · environment configuration

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

Configure the required variables for your environment.

> **Never commit API keys, credentials, or production secrets.**

## 5. Start the backend

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

# 🐳 Docker

Docker support is included for reproducible local/container workflows.

Build and start:

```bash
docker compose up -d --build
```

Check the service:

```bash
docker compose ps
```

Health:

```bash
curl http://127.0.0.1:8001/health
```

Stop:

```bash
docker compose down
```

> Docker is supported for local/container workflows. The current Render deployment uses separate native Render services rather than requiring Docker.

---

# ☁️ Production Deployment

MindCare is deployed as two Render services.

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
   ├── Safety / Risk Layer
   ├── Session Manager
   ├── Conversation Routing
   ├── Response Engine
   ├── 50K Response Model
   └── Safety Audit
```

The production integration has been verified through:

- backend health check
- CORS preflight
- session creation
- production `/chat`
- live frontend interaction

---

# 📈 What This Demonstrates to a Recruiter

### AI / ML Engineering

- Designed a dedicated **50K-message response dataset**
- Built balanced train/validation/test splits
- Evaluated intent/risk, mood, topic, and retrieval similarity
- Implemented response routing and retrieval behavior
- Evaluated response naturalness/diversity

### AI Safety

- Separated safety decisions from response generation
- Implemented negation-aware safety handling
- Protected crisis/self-harm routing from naive keyword behavior
- Added safety audit infrastructure
- Added regression tests for safety-critical cases

### Backend Engineering

- Built a FastAPI REST backend
- Implemented Pydantic validation
- Implemented session lifecycle management
- Added rate limiting
- Configured production CORS
- Added security headers
- Added health/live/readiness endpoints

### Software Quality

- Maintained a **238-test regression suite**
- Tested API security and configuration
- Tested response behavior and routing
- Verified model integration after major changes
- Used Git/GitHub for version-controlled development

### Deployment

- Deployed frontend and backend independently on Render
- Configured frontend/backend communication
- Verified production CORS
- Added Docker/Docker Compose support
- Exposed health monitoring endpoints

---

# 📊 Current Status

| Component | Status |
|---|:---:|
| Frontend | 🟢 Live |
| Backend API | 🟢 Live |
| `/health` | 🟢 Healthy |
| Frontend ↔ Backend | 🟢 Connected |
| Production CORS | 🟢 Verified |
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

# 🔮 Future Engineering Work

Potential next improvements:

- human-written evaluation datasets
- stronger multilingual/Hinglish evaluation
- more rigorous safety benchmarking
- semantic evaluation of supportive responses
- human review workflows
- improved production observability
- model/version management
- privacy-aware conversation memory
- accessibility improvements
- stronger CI/CD automation
- containerized production deployment where appropriate

These are **future directions, not current functionality**.

---

# ⚠️ Responsible AI

MindCare is an educational and engineering project for supportive conversational AI.

It should **not** be used as:

- a medical diagnostic system
- a clinical decision-making system
- a replacement for a therapist or doctor
- an emergency response service
- a substitute for professional treatment

The 50K dataset is synthetic development/training data, and the reported metrics are engineering evaluation metrics rather than clinical validation.

---

# 👨‍💻 Developer

<div align="center">

## Ansh Pratap

**B.Tech Computer Science & Engineering**  
Mewar University, Rajasthan, India

**Focus:** Artificial Intelligence · Machine Learning · Python · Software Engineering · NLP/LLM Applications · AI Safety

<p>
  <a href="https://github.com/AnshPratap2314">
    <img src="https://img.shields.io/badge/GitHub-AnshPratap2314-181717?style=for-the-badge&logo=github&logoColor=white" alt="GitHub">
  </a>
  <a href="https://github.com/AnshPratap2314/AI-Mental-health-chatbot">
    <img src="https://img.shields.io/badge/Project-MindCare%20AI-6C63FF?style=for-the-badge&logo=github&logoColor=white" alt="Project Repository">
  </a>
</p>

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

<a href="https://mindcare-ai-o1e5.onrender.com"><strong>🚀 Try the Live Demo ↗</strong></a>
&nbsp;&nbsp;•&nbsp;&nbsp;
<a href="https://github.com/AnshPratap2314/AI-Mental-health-chatbot"><strong>💻 View Source ↗</strong></a>

<br><br>

*Built with Python · FastAPI · Machine Learning · JavaScript · Testing · Responsible AI*

</div>
