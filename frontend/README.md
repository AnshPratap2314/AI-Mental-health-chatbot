# MindCare Frontend

This is a responsive vanilla HTML/CSS/JavaScript frontend for the Ethical Mental Health Chatbot.

## Project structure

frontend/
├── index.html
├── style.css
├── script.js
└── README.md

## 1. Copy the frontend

Put the `frontend` folder inside:

Mental health chatbot/

So the structure becomes:

Mental health chatbot/
├── app/
├── tests/
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── script.js
└── ...

## 2. Enable CORS in FastAPI

In `app/main.py`, add:

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
        "http://127.0.0.1:5501",
        "http://localhost:5501",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Place this immediately after:

app = FastAPI(...)

and before your routes.

## 3. Start backend

Terminal 1:

cd ~/Downloads/python/PythonProject/"Mental health chatbot"
source venv/bin/activate
python -m uvicorn app.main:app --reload

Keep this terminal running.

## 4. Start frontend

Open a second terminal:

cd ~/Downloads/python/PythonProject/"Mental health chatbot"/frontend
python3 -m http.server 5500

Then open:

http://127.0.0.1:5500

## 5. Test

1. Enter your name.
2. Send "I feel lonely".
3. Send "Tell me more".
4. Confirm both requests use the same session.
5. Test "I feel hopeless".
6. Test "I want to die" only as a safety-system test in a controlled development environment.

The frontend expects:

POST /session
{
  "user_name": "friend"
}

and:

POST /chat
{
  "session_id": "...",
  "message": "I feel lonely"
}

The `/chat` response should contain at least:

{
  "session_id": "...",
  "mode": "...",
  "risk_level": "...",
  "risk_score": 0.0,
  "signals": {},
  "context": {},
  "reply": "..."
}
