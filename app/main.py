import os
import time
from collections import defaultdict, deque
from threading import RLock
from typing import Deque, Dict, Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from app.production_config import ProductionConfig
from app.session_manager import SessionManager


APP_VERSION = "1.2.0"

# The API URL and frontend origin are configurable. Keep the known Render
# deployments as compatibility defaults while allowing production to provide
# an explicit FRONTEND_URLS value.
DEFAULT_FRONTEND_URLS = [
    "https://ai-mental-health-chatbot-nm2r.onrender.com",
]

_raw_frontend_urls = os.getenv("FRONTEND_URLS") or os.getenv("FRONTEND_URL", "")
if _raw_frontend_urls.strip():
    configured_origins = [
        item.strip().rstrip("/")
        for item in _raw_frontend_urls.split(",")
        if item.strip()
    ]
else:
    configured_origins = DEFAULT_FRONTEND_URLS

ALLOWED_ORIGINS = list(dict.fromkeys([
    "http://localhost:5500",
    "http://127.0.0.1:5500",
    "http://localhost:5501",
    "http://127.0.0.1:5501",
    "https://mindcare-ai-o1e5.onrender.com",
    *configured_origins,
]))

API_PUBLIC_URL = os.getenv(
    "API_PUBLIC_URL",
    "https://mindcare-ai-semb.onrender.com",
).strip().rstrip("/")


app = FastAPI(
    title="Ethical Mental Health Chatbot",
    description="MindCare AI supportive mental health chatbot API",
    version=APP_VERSION,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type"],
)


_session_manager: Optional[SessionManager] = None
_rate_lock = RLock()
_rate_events: Dict[str, Deque[float]] = defaultdict(deque)
RATE_LIMIT_PER_MINUTE = max(1, int(os.getenv("CHAT_RATE_LIMIT", "30")))
RATE_WINDOW_SECONDS = 60.0


def get_session_manager() -> SessionManager:
    global _session_manager
    if _session_manager is None:
        _session_manager = SessionManager(
            session_ttl_seconds=ProductionConfig.SESSION_TTL_SECONDS,
            max_sessions=ProductionConfig.MAX_SESSIONS,
        )
    return _session_manager


def _client_key(request: Request) -> str:
    # Never use forwarded headers as identity unless the deployment explicitly
    # provides trusted proxy handling. FastAPI's direct client address is safe
    # for the simple in-memory limiter used here.
    return request.client.host if request.client else "unknown"


def _check_rate_limit(key: str) -> bool:
    now = time.monotonic()
    cutoff = now - RATE_WINDOW_SECONDS
    with _rate_lock:
        events = _rate_events[key]
        while events and events[0] <= cutoff:
            events.popleft()
        if len(events) >= RATE_LIMIT_PER_MINUTE:
            return False
        events.append(now)
        # Bound the dictionary as well as each deque.
        if len(_rate_events) > 5000:
            stale_keys = [
                candidate
                for candidate, candidate_events in _rate_events.items()
                if not candidate_events or candidate_events[-1] <= cutoff
            ]
            for candidate in stale_keys[:1000]:
                _rate_events.pop(candidate, None)
        return True


class CreateSessionRequest(BaseModel):
    user_name: str = Field(default="friend", min_length=1, max_length=100)


class ChatRequest(BaseModel):
    session_id: str = Field(min_length=36, max_length=100)
    message: str = Field(min_length=1, max_length=4000)


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
    try:
        manager = get_session_manager()
        return {
            "status": "ready",
            "service": "mindcare-api",
            "active_sessions": manager.session_count(),
            "llm_configured": bool(os.getenv("OPENAI_API_KEY", "").strip()),
        }
    except Exception:
        return JSONResponse(
            status_code=503,
            content={
                "status": "degraded",
                "service": "mindcare-api",
            },
        )


@app.post("/session")
def create_session(request: CreateSessionRequest):
    user_name = request.user_name.strip() or "friend"
    try:
        session_id = get_session_manager().create_session(user_name=user_name)
        return {
            "session_id": session_id,
            "message": "Session created successfully.",
            "expires_in_seconds": ProductionConfig.SESSION_TTL_SECONDS,
        }
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Unable to create session.",
        )


@app.delete("/session/{session_id}")
def delete_session(session_id: str):
    session_id = session_id.strip()
    if not session_id:
        raise HTTPException(status_code=400, detail="Session ID cannot be empty.")

    try:
        deleted = get_session_manager().delete_session(session_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Session not found.")
        return {"message": "Session deleted successfully."}
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Unable to delete session.")


@app.post("/chat")
def chat_endpoint(request: ChatRequest, http_request: Request):
    if not _check_rate_limit(_client_key(http_request)):
        return JSONResponse(
            status_code=429,
            headers={"Retry-After": "60"},
            content={"detail": "Too many messages. Please wait a moment and try again."},
        )

    session_id = request.session_id.strip()
    message = request.message.strip()

    try:
        engine = get_session_manager().get_engine(session_id)
        if engine is None:
            raise HTTPException(status_code=404, detail="Session not found or expired.")

        response = engine.generate_reply(message)
        if not isinstance(response, dict):
            raise HTTPException(status_code=500, detail="Invalid response from chatbot engine.")

        analysis = response.get("analysis", {})
        if not isinstance(analysis, dict):
            analysis = {}

        return {
            "session_id": session_id,
            "mode": response.get("mode", "supportive"),
            "risk_level": analysis.get("risk_level", "low"),
            "risk_score": analysis.get("risk_score", 0.0),
            "signals": analysis.get("signals", {}),
            "context": analysis.get("context", {}),
            "reply": response.get(
                "reply",
                "I'm here to listen. Tell me what's on your mind.",
            ),
        }

    except HTTPException:
        raise
    except Exception:
        # Do not leak stack traces, API details, keys, or internal paths.
        raise HTTPException(status_code=500, detail="Chatbot error. Please try again.")


@app.get("/api/status")
def api_status():
    return {
        "service": "MindCare AI",
        "api_version": APP_VERSION,
        "status": "online",
        "api": API_PUBLIC_URL,
        "allowed_origins": ALLOWED_ORIGINS,
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
