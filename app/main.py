import os
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.session_manager import SessionManager


APP_VERSION = "1.0.0"

DEFAULT_FRONTEND_URL = (
    "https://ai-mental-health-chatbot-nm2r.onrender.com"
)

FRONTEND_URL = os.getenv(
    "FRONTEND_URL",
    DEFAULT_FRONTEND_URL
).strip().rstrip("/")

ALLOWED_ORIGINS = [
    "http://localhost:5500",
    "http://127.0.0.1:5500",
    FRONTEND_URL,
]

# Remove empty or duplicate origins
ALLOWED_ORIGINS = list(
    dict.fromkeys(
        origin
        for origin in ALLOWED_ORIGINS
        if origin
    )
)


app = FastAPI(
    title="Ethical Mental Health Chatbot",
    description="MindCare AI supportive mental health chatbot API",
    version=APP_VERSION,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


_session_manager: Optional[SessionManager] = None


def get_session_manager() -> SessionManager:
    global _session_manager

    if _session_manager is None:
        _session_manager = SessionManager()

    return _session_manager


class CreateSessionRequest(BaseModel):
    user_name: str = "friend"


class ChatRequest(BaseModel):
    session_id: str
    message: str


@app.get("/")
def home():
    return {
        "message": "Mental Health Chatbot API is running.",
        "version": APP_VERSION,
        "status": "healthy",
        "service": "mindcare-api",
    }


@app.get("/health")
def health():
    """
    Lightweight health endpoint.

    Do not initialize the chatbot/session manager here.
    """
    return {
        "status": "healthy",
        "service": "mindcare-api",
        "version": APP_VERSION,
    }


@app.get("/health/live")
def health_live():
    return {
        "status": "alive",
        "service": "mindcare-api",
    }


@app.get("/health/ready")
def health_ready():
    """
    Readiness endpoint.

    Unlike /health, this verifies that the session manager
    can actually be initialized.
    """
    try:
        get_session_manager()

        return {
            "status": "ready",
            "service": "mindcare-api",
        }

    except Exception as exc:
        return {
            "status": "degraded",
            "service": "mindcare-api",
            "error": str(exc),
        }


@app.post("/session")
def create_session(
    request: CreateSessionRequest
):
    user_name = (
        request.user_name or "friend"
    ).strip()

    if not user_name:
        user_name = "friend"

    try:
        session_manager = get_session_manager()

        session_id = session_manager.create_session(
            user_name=user_name
        )

        return {
            "session_id": session_id,
            "message": "Session created successfully.",
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to create session: {str(exc)}",
        )


@app.delete("/session/{session_id}")
def delete_session(
    session_id: str
):
    session_id = (
        session_id or ""
    ).strip()

    if not session_id:
        raise HTTPException(
            status_code=400,
            detail="Session ID cannot be empty.",
        )

    try:
        session_manager = get_session_manager()

        deleted = session_manager.delete_session(
            session_id
        )

        if not deleted:
            raise HTTPException(
                status_code=404,
                detail="Session not found.",
            )

        return {
            "message": "Session deleted successfully.",
        }

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to delete session: {str(exc)}",
        )


@app.post("/chat")
def chat_endpoint(
    request: ChatRequest
):
    session_id = (
        request.session_id or ""
    ).strip()

    message = (
        request.message or ""
    ).strip()

    if not session_id:
        raise HTTPException(
            status_code=400,
            detail="Session ID cannot be empty.",
        )

    if not message:
        raise HTTPException(
            status_code=400,
            detail="Message cannot be empty.",
        )

    try:
        session_manager = get_session_manager()

        engine = session_manager.get_engine(
            session_id
        )

        if engine is None:
            raise HTTPException(
                status_code=404,
                detail="Session not found.",
            )

        response = engine.generate_reply(
            message
        )

        if not isinstance(response, dict):
            raise HTTPException(
                status_code=500,
                detail="Invalid response from chatbot engine.",
            )

        analysis = response.get(
            "analysis",
            {}
        )

        if not isinstance(analysis, dict):
            analysis = {}

        return {
            "session_id": session_id,

            "mode": response.get(
                "mode",
                "supportive",
            ),

            "risk_level": analysis.get(
                "risk_level",
                "low",
            ),

            "risk_score": analysis.get(
                "risk_score",
                0.0,
            ),

            "signals": analysis.get(
                "signals",
                {},
            ),

            "context": analysis.get(
                "context",
                {},
            ),

            "reply": response.get(
                "reply",
                "I'm here to listen. Tell me what's on your mind.",
            ),
        }

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Chatbot error: {str(exc)}",
        )


@app.get("/api/status")
def api_status():
    return {
        "service": "MindCare AI",
        "api_version": APP_VERSION,
        "status": "online",
        "frontend": FRONTEND_URL,
        "endpoints": {
            "home": "/",
            "health": "/health",
            "live": "/health/live",
            "ready": "/health/ready",
            "create_session": "/session",
            "chat": "/chat",
            "delete_session": "/session/{session_id}",
        },
    }