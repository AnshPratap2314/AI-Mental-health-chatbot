import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.session_manager import SessionManager


app = FastAPI(
    title="Ethical Mental Health Chatbot",
    version="1.0.0"
)


frontend_url = os.getenv(
    "FRONTEND_URL",
    "https://ai-mental-health-chatbot-nm2r.onrender.com"
)


allowed_origins = [
    "http://127.0.0.1:5500",
    "http://localhost:5500",
    "http://127.0.0.1:8000",
    "http://localhost:8000",
    frontend_url
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=list(set(allowed_origins)),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


session_manager = SessionManager()


class CreateSessionRequest(BaseModel):
    user_name: str = "friend"


class ChatRequest(BaseModel):
    session_id: str
    message: str


@app.get("/")
def home():
    return {
        "message": "Mental Health Chatbot API is running.",
        "version": "1.0.0",
        "status": "healthy"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "mindcare-api",
        "version": "1.0.0"
    }


@app.post("/session")
def create_session(request: CreateSessionRequest):
    user_name = (
        request.user_name.strip()
        if request.user_name
        else "friend"
    )

    if not user_name:
        user_name = "friend"

    session_id = session_manager.create_session(
        user_name=user_name
    )

    return {
        "session_id": session_id,
        "message": "Session created successfully."
    }


@app.delete("/session/{session_id}")
def delete_session(session_id: str):
    deleted = session_manager.delete_session(
        session_id
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Session not found."
        )

    return {
        "message": "Session deleted successfully."
    }


@app.post("/chat")
def chat_endpoint(request: ChatRequest):
    session_id = (
        request.session_id.strip()
        if request.session_id
        else ""
    )

    message = (
        request.message.strip()
        if request.message
        else ""
    )

    if not session_id:
        raise HTTPException(
            status_code=400,
            detail="Session ID is required."
        )

    if not message:
        raise HTTPException(
            status_code=400,
            detail="Message cannot be empty."
        )

    engine = session_manager.get_engine(
        session_id
    )

    if engine is None:
        raise HTTPException(
            status_code=404,
            detail="Session not found."
        )

    try:
        response = engine.generate_reply(
            message
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Unable to generate a response."
        ) from exc

    analysis = response.get(
        "analysis",
        {}
    )

    return {
        "session_id": session_id,
        "mode": response.get(
            "mode",
            "supportive"
        ),
        "risk_level": analysis.get(
            "risk_level",
            "low"
        ),
        "risk_score": analysis.get(
            "risk_score",
            0.0
        ),
        "signals": analysis.get(
            "signals",
            {}
        ),
        "context": analysis.get(
            "context",
            {}
        ),
        "reply": response.get(
            "reply",
            "I'm here to listen."
        )
    }