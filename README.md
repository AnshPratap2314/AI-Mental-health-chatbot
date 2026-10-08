# 🧠 MindCare AI

<p align="center">
  <strong>A safety-first AI mental health support chatbot built with Python, FastAPI, machine learning, and a dedicated 50K-message response model.</strong>
</p>

<p align="center">
  <a href="https://mindcare-ai-o1e5.onrender.com">Live Demo</a> •
  <a href="https://mindcare-ai-semb.onrender.com/health">API Health</a> •
  <a href="https://github.com/AnshPratap2314/AI-Mental-health-chatbot">GitHub Repository</a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white" alt="Python 3.11">
  <img src="https://img.shields.io/badge/FastAPI-REST%20API-009688?logo=fastapi&logoColor=white" alt="FastAPI">
  <img src="https://img.shields.io/badge/ML-Hybrid%20Safety%20%2B%20Response%20Model-orange" alt="Machine Learning">
  <img src="https://img.shields.io/badge/Tests-238%20passed-success" alt="238 tests passed">
  <img src="https://img.shields.io/badge/Dataset-50K%20messages-purple" alt="50K messages">
  <img src="https://img.shields.io/badge/Deployment-Render-46E3B7?logo=render&logoColor=black" alt="Render">
</p>

---

## 📌 Project Overview

**MindCare AI** is a supportive conversational AI application designed to help users talk about emotions, stress, worries, academic pressure, loneliness, and difficult days.

The project is built around a **safety-first architecture** rather than treating the chatbot as a generic text-generation application.

The system combines:

- deterministic safety and risk detection
- rule-based safeguards
- machine-learning decision support
- a trained **50,000-message response dataset**
- a trained response retrieval/model pipeline
- contextual response routing
- FastAPI REST APIs
- session management
- rate limiting
- safety auditing
- CORS and security controls
- automated regression testing
- production deployment on Render

> **Important:** MindCare is a supportive conversational application. It is **not a replacement for a qualified mental-health professional, medical diagnosis, treatment, or emergency services.**

---

## 🌐 Live Application

### Frontend

**https://mindcare-ai-o1e5.onrender.com**

The deployed interface provides a private conversational space with:

- supportive chat
- emotional reflection
- step-by-step conversation
- academic/exam-stress support
- loneliness support
- anxious/difficult-day conversations
- visible connection status
- safety notice

### Backend API

**https://mindcare-ai-semb.onrender.com**

Health endpoint:

```text
GET /health
```

Current response:

```json
{
  "status": "healthy",
  "service": "mindcare-api",
  "version": "1.2.0"
}
```

---

# 🎯 Why I Built MindCare

Many conversational AI systems focus primarily on generating fluent responses.

MindCare focuses on a different engineering problem:

> **How can a supportive conversational system remain useful while keeping safety and risk decisions authoritative?**

This led to a layered design where safety decisions are not delegated to the response-generation model.

The project therefore separates:

```text
USER MESSAGE
     │
     ▼
Safety / Risk Analysis
     │
     ├── Crisis / Self-Harm Detection
     ├── Negation Handling
     ├── Protective Signals
     └── Risk Level / Score
     │
     ▼
Conversation / Intent Routing
     │
     ├── Academic / Exam Stress
     ├── Loneliness
     ├── Anxiety
     ├── Difficult Day
     ├── General Conversation
     └── Other Context
     │
     ▼
Response Engine
     │
     ├── Trained Response Model
     ├── Optional LLM Support
     └── Deterministic Fallbacks
     │
     ▼
Safety-Aware Response
```

---

# ⭐ Key Features

## 🛡️ 1. Safety-First Architecture

Safety and risk analysis are treated as authoritative.

The response model does **not** decide whether a message is a crisis or self-harm case.

The architecture separates:

- risk detection
- conversation routing
- response generation
- safety auditing

This prevents a language model or response model from becoming the sole authority for safety decisions.

---

## 🧠 2. Hybrid AI/ML System

MindCare combines deterministic and ML-based components.

### Deterministic layer

Used for important safety behavior and predictable application logic.

Examples include:

- crisis patterns
- self-harm signals
- negation handling
- protective signals
- rate limits
- session validation
- API validation

### Machine-learning layer

Used for conversational classification and response behavior.

The project includes a trained response model built from a dedicated **50K-message dataset**.

This hybrid approach provides a balance between:

**predictability + ML flexibility + safety controls**

---

# 📚 3. 50,000-Message Response Dataset

MindCare's current response model is based on a dedicated dataset containing:

| Property | Value |
|---|---:|
| Total messages | **50,000** |
| Train split | **40,000** |
| Validation split | **5,000** |
| Test split | **5,000** |
| Intents | **20** |
| Messages per intent | **2,500** |
| Unique normalized messages | **50,000** |
| Unique response texts | **18,009** |
| Normalized duplicates | **0** |
| Train/validation overlap | **0** |
| Train/test overlap | **0** |
| Validation/test overlap | **0** |
| High-risk rows | **2,500** |
| English messages | **43,556** |
| Hinglish messages | **6,444** |

The dataset is synthetic development/training data and is explicitly treated as such. A separate human-written evaluation set would be appropriate before using the system for real clinical or safety-critical deployment.

### Dataset characteristics

The training data includes varied conversational situations such as:

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
- high-risk/safety-oriented messages
- other supportive conversation contexts

The dataset was audited for normalized duplicates and cross-split leakage.

---

# 🤖 4. Trained Response Model

Current model identifier:

```text
mindcare-response-50k
```

The current model was trained using:

```text
40,000 training messages
5,000 validation messages
5,000 test messages
```

### Current evaluation metrics

| Metric | Result |
|---|---:|
| Intent / Risk accuracy | **1.0000** |
| Mood accuracy | **~0.867** |
| Topic accuracy | **~0.868** |
| Mean retrieval similarity | **~0.8587** |

These metrics describe the current development/evaluation setup and should not be interpreted as clinical performance.

---

# 💬 5. Context-Aware Conversation Routing

MindCare does not treat every message as the same type of conversation.

The response engine includes targeted routing for situations such as:

### Exam stress

Example:

```text
"I have exam stress"
```

The system can route the conversation toward academic/exam context instead of returning a generic emotional response.

### Academic stress

Example:

```text
"my exams are coming and till now I have read nothing"
```

The system recognizes the academic context and responds with practical, supportive guidance.

### Loneliness

Example:

```text
"I feel lonely today"
```

Loneliness is handled as an emotional conversation rather than incorrectly treating the phrase itself as ordinary stress.

### Difficult days / overwhelm

The response system also includes routing and phrase hints for difficult-day and overwhelm-related conversations.

---

# 🔐 6. Negation-Aware Safety Detection

One important safety improvement was handling **negation** correctly.

For example:

```text
"I am not suicidal and I do not want to hurt myself"
```

should not be interpreted as an active self-harm statement merely because the message contains words such as `suicidal` or `hurt myself`.

MindCare's safety layer removes recognized negated safety phrases before evaluating the relevant crisis/self-harm patterns.

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
mode = normal
crisis = false
self_harm = false
protective = true
```

This is an example of why the project uses deterministic safety logic rather than relying only on a response-generation model.

---

# 🧩 7. Response Architecture

MindCare follows a layered response strategy:

```text
                ┌──────────────────────┐
                │   User Message       │
                └──────────┬───────────┘
                           │
                           ▼
                ┌──────────────────────┐
                │ Safety / Risk Layer  │
                └──────────┬───────────┘
                           │
                           ▼
                ┌──────────────────────┐
                │ Conversation Control │
                └──────────┬───────────┘
                           │
                           ▼
                ┌──────────────────────┐
                │ Response Engine      │
                └──────────┬───────────┘
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
       Trained Model      LLM       Deterministic
       / Retrieval      Support       Fallback
              │            │            │
              └────────────┼────────────┘
                           ▼
                ┌──────────────────────┐
                │ Safety-Aware Reply   │
                └──────────────────────┘
```

### Important design principle

**The trained response model is not the safety authority.**

Safety/risk decisions are handled separately.

---

# 🏗️ System Architecture

```text
┌───────────────────────────────────────────────────────────┐
│                     MindCare Frontend                     │
│                 HTML / CSS / JavaScript                   │
└──────────────────────────┬────────────────────────────────┘
                           │ HTTPS / REST
                           ▼
┌───────────────────────────────────────────────────────────┐
│                    FastAPI Backend                         │
│                                                           │
│  ┌─────────────┐   ┌──────────────┐   ┌──────────────┐  │
│  │ Validation  │   │ Rate Limiter │   │ Session Mgmt │  │
│  └─────────────┘   └──────────────┘   └──────────────┘  │
│                                                           │
│  ┌─────────────────────────────────────────────────────┐  │
│  │               Behavior / Safety Engine             │  │
│  └─────────────────────────┬───────────────────────────┘  │
│                            │                              │
│  ┌─────────────────────────▼───────────────────────────┐  │
│  │                  Response Engine                    │  │
│  └─────────────────────────┬───────────────────────────┘  │
│                            │                              │
│  ┌─────────────────────────▼───────────────────────────┐  │
│  │             mindcare-response-50k                  │  │
│  └─────────────────────────────────────────────────────┘  │
│                                                           │
│  ┌──────────────────┐       ┌──────────────────────────┐ │
│  │ Safety Audit     │       │ Security / CORS Controls │ │
│  └──────────────────┘       └──────────────────────────┘ │
└──────────────────────────┬────────────────────────────────┘
                           │
                           ▼
                    Render Web Service
```

---

# 🔒 Security & Reliability

MindCare includes several production-oriented backend controls.

### Input validation

FastAPI/Pydantic models validate API payloads.

For example:

- session IDs have length constraints
- messages have minimum/maximum lengths
- user names are validated
- malformed requests are rejected

### Rate limiting

The API includes separate rate limits for:

- chat requests
- session creation

### Session management

Conversations use isolated server-side sessions with:

- session IDs
- session expiration
- session lookup
- session deletion
- maximum session controls

### CORS

The API explicitly controls allowed frontend origins.

Current deployed frontend:

```text
https://mindcare-ai-o1e5.onrender.com
```

The previous/alternate frontend origin is also supported:

```text
https://ai-mental-health-chatbot-nm2r.onrender.com
```

### Security headers

The backend applies headers including:

```text
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
Referrer-Policy: no-referrer
Cache-Control: no-store
```

### Safety auditing

Safety-related decisions can be recorded through the project's `SafetyAudit` component.

Audit endpoints are protected using an audit access key when configured.

---

# 🧪 Testing

MindCare currently has a comprehensive regression suite.

Latest full test result:

```text
238 passed in 81.84s
```

The test suite covers areas including:

- API behavior
- API security
- CORS/security configuration
- safety behavior
- natural response behavior
- response-model integration
- regression cases
- session behavior
- routing behavior

### Run the complete test suite

```bash
pytest -q
```

Expected result:

```text
238 passed
```

---

# 📊 Response Quality & Evaluation

The project also contains evaluation tooling for response behavior and diversity.

The response evaluation work focuses on:

- routing correctness
- response source
- natural language quality
- response diversity
- retrieval similarity
- model metadata
- regression behavior

This is important because a chatbot should not repeatedly return the same sentence for different but related messages.

---

# 🛠️ Tech Stack

## Backend

- **Python 3.11**
- **FastAPI**
- **Uvicorn**
- **Pydantic**
- **python-dotenv**

## AI / Machine Learning

- **Python ML ecosystem**
- **NumPy**
- **Pandas**
- **Scikit-learn**
- trained response model
- retrieval/similarity-based response selection
- optional LLM integration

## Frontend

- **HTML5**
- **CSS3**
- **JavaScript**
- responsive conversational UI

## Engineering / Security

- REST APIs
- session management
- rate limiting
- CORS
- security headers
- safety audit logging
- automated regression testing
- environment-based configuration

## Deployment

- **Render**
- separate frontend/static site and backend web service
- production FastAPI deployment

## Development

- Git
- GitHub
- VS Code / PyCharm
- pytest
- virtual environments

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

> Backup model directories and temporary development artifacts are intentionally excluded from the production model structure.

---

# 🚀 Getting Started

## 1. Clone the repository

```bash
git clone https://github.com/AnshPratap2314/AI-Mental-health-chatbot.git
cd AI-Mental-health-chatbot
```

---

## 2. Create a virtual environment

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

---

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## 4. Configure environment variables

Create a `.env` file from the project's example configuration:

```bash
cp .env.example .env
```

Configure the variables required by your deployment/environment.

Do **not** commit secrets such as:

```text
API keys
authentication secrets
private credentials
production environment secrets
```

---

# ▶️ Run the Backend

Start FastAPI with:

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

The API will be available at:

```text
http://127.0.0.1:8000
```

Health check:

```text
http://127.0.0.1:8000/health
```

---

# 🌐 Run the Frontend

The frontend is a static HTML/CSS/JavaScript application.

For local development, serve the `Frontend` directory using a local static server.

For example:

```bash
cd Frontend
python3 -m http.server 5500
```

Then open:

```text
http://localhost:5500
```

The frontend automatically uses:

```text
http://127.0.0.1:8000
```

for local backend development and the deployed Render API for the production frontend.

---

# 🔌 API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/` | API information |
| `GET` | `/health` | Health check |
| `GET` | `/health/live` | Liveness check |
| `GET` | `/health/ready` | Readiness information |
| `POST` | `/session` | Create a conversation session |
| `POST` | `/chat` | Send a message |
| `DELETE` | `/session/{session_id}` | Delete a session |
| `GET` | `/api/status` | API status/configuration |
| `GET` | `/api/audit/count` | Audit record count |
| `GET` | `/api/audit/recent` | Recent audit records |

Audit endpoints require the configured audit access mechanism.

---

# 📨 Example API Flow

### Create a session

```http
POST /session
Content-Type: application/json
```

```json
{
  "user_name": "friend"
}
```

Response contains a `session_id`.

### Send a message

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

The response contains information such as:

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

# ☁️ Deployment

MindCare is currently deployed using **Render** with separate services.

### Frontend

```text
Render Static Site
        │
        ▼
https://mindcare-ai-o1e5.onrender.com
```

### Backend

```text
Render Web Service
        │
        ▼
https://mindcare-ai-semb.onrender.com
```

### Production request flow

```text
Browser
   │
   │ HTTPS
   ▼
MindCare Static Frontend
   │
   │ REST API
   ▼
FastAPI Backend
   │
   ├── Safety Engine
   ├── Session Manager
   ├── Response Engine
   ├── 50K Response Model
   └── Safety Audit
```

The current deployment has been tested end-to-end after resolving the frontend/backend CORS configuration.

---

# 🐳 Docker

Docker configuration is also present in the project for reproducible local/container workflows.

However, the current production deployment uses Render's web-service deployment directly rather than requiring Docker for the primary deployment path.

Docker is therefore treated as an additional deployment/reproducibility option rather than a requirement for the application to run.

---

# 📈 Engineering Highlights

This project demonstrates more than simply building a chatbot UI.

### 1. Safety architecture

Designed a layered system where safety/risk decisions remain independent from response generation.

### 2. ML response pipeline

Built and integrated a dedicated 50K-message response dataset and trained response model.

### 3. Dataset engineering

Performed:

- normalization
- duplicate auditing
- split validation
- cross-split leakage checks
- intent balancing
- response diversity analysis

### 4. Regression engineering

Maintained a full regression suite with:

```text
238 passing tests
```

after major model and safety changes.

### 5. Production API

Implemented a FastAPI backend with:

- validation
- sessions
- rate limiting
- CORS
- security headers
- audit support
- health/readiness endpoints

### 6. Real deployment

The application is not limited to a local prototype.

It is deployed with:

- public frontend
- public backend API
- production health endpoint
- frontend/backend integration
- CORS configuration
- Render deployment

---

# 🧪 Important Regression Cases

The project specifically protects against several classes of regression.

### Negated self-harm language

```text
"I am not suicidal"
```

must not automatically become a high-risk classification.

### Loneliness

```text
"I feel lonely today"
```

must be handled as a loneliness/emotional conversation rather than incorrectly triggering an ordinary-stress rule.

### Exam stress

```text
"I have exam stress"
```

should be routed toward an academic/exam context.

### Academic overwhelm

```text
"my exams are coming and till now I have read nothing"
```

should produce a supportive academic response rather than a generic unrelated response.

---

# 🧠 Design Philosophy

MindCare follows five major principles:

### 1. Safety before fluency

A fluent response is not useful if the underlying safety decision is wrong.

### 2. Deterministic controls where predictability matters

Critical safety and application controls should be testable and reproducible.

### 3. ML where flexibility adds value

Machine learning is used for conversational understanding and response behavior.

### 4. Test every important behavior

New functionality should be accompanied by regression coverage.

### 5. Be transparent about limitations

MindCare is a supportive AI application, not a medical or clinical system.

---

# 📊 Current Project Status

| Area | Status |
|---|---|
| Frontend | ✅ Deployed |
| Backend API | ✅ Deployed |
| Backend health check | ✅ Healthy |
| Frontend/backend connection | ✅ Working |
| CORS configuration | ✅ Fixed |
| 50K response dataset | ✅ Integrated |
| Response model | ✅ Integrated |
| Safety/risk engine | ✅ Implemented |
| Negation handling | ✅ Implemented |
| Exam-stress routing | ✅ Implemented |
| Loneliness routing | ✅ Implemented |
| Session management | ✅ Implemented |
| Rate limiting | ✅ Implemented |
| Safety auditing | ✅ Implemented |
| Security headers | ✅ Implemented |
| Automated regression suite | ✅ 238 tests passing |
| Render deployment | ✅ Live |
| Docker support | ✅ Available |

---

# 🔮 Future Improvements

Potential next steps include:

- larger human-written evaluation datasets
- stronger multilingual/Hinglish evaluation
- better semantic evaluation of supportive responses
- more rigorous safety benchmarking
- human review workflows
- improved observability and production monitoring
- model/version management
- richer conversation memory with privacy controls
- additional accessibility improvements
- stronger deployment automation
- containerized production deployment where appropriate

These are future engineering directions, not claims about current functionality.

---

# ⚠️ Responsible AI Notice

MindCare is an educational and engineering project focused on supportive conversational AI.

It should **not** be used as:

- a medical diagnostic system
- a replacement for a therapist or doctor
- an emergency response service
- a clinical decision-making system

For immediate danger or a mental-health emergency, users should contact appropriate local emergency services or qualified professionals.

The project's synthetic training dataset and development metrics should not be interpreted as clinical validation.

---

# 👨‍💻 Developer

**Ansh Pratap**

B.Tech Computer Science & Engineering  
Mewar University, Rajasthan, India

### Focus Areas

- Artificial Intelligence & Machine Learning
- Python
- Software Engineering
- NLP / LLM Applications
- Backend Development
- AI Safety & Responsible AI

### GitHub

https://github.com/AnshPratap2314

### Project Repository

https://github.com/AnshPratap2314/AI-Mental-health-chatbot

---

# 📄 License

Add the project's intended open-source license here before public distribution.

If this repository is intended to be open source, a standard license such as MIT can be added explicitly as a separate `LICENSE` file.

---

# ⭐ Final Note

MindCare AI is an ongoing engineering project focused on combining **AI/ML, backend engineering, safety controls, dataset engineering, testing, and production deployment** into one practical application.

The central goal is not simply to generate chatbot responses, but to build a system where:

```text
Safety
   +
Machine Learning
   +
Context
   +
Reliable APIs
   +
Testing
   +
Responsible AI
```

work together as one architecture.

If you are reviewing this project as a recruiter, the most important engineering areas to explore are the **safety-first architecture, 50K response-model pipeline, dataset auditing, FastAPI backend, regression suite, and production deployment**.
