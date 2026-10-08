import os
import time
from collections import defaultdict, deque
from threading import RLock
from typing import Deque, Dict, Optional
from dotenv import load_dotenv
load_dotenv()

from fastapi import Depends, FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from app.logging_config import logger
from app.production_config import ProductionConfig
from app.safety_audit import SafetyAudit
from app.security import SecurityManager
from app.session_manager import SessionManager




APP_VERSION = "1.2.0"

DEFAULT_FRONTEND_URLS = [
    "https://ai-mental-health-chatbot-nm2r.onrender.com",
]

_raw_frontend_urls = (
    os.getenv("FRONTEND_URLS")
    or os.getenv("FRONTEND_URL", "")
)

if _raw_frontend_urls.strip():
    configured_origins = [
        item.strip().rstrip("/")
        for item in _raw_frontend_urls.split(",")
        if item.strip()
    ]
else:
    configured_origins = DEFAULT_FRONTEND_URLS

ALLOWED_ORIGINS = list(
    dict.fromkeys(
        [
            "http://localhost:5500",
            "http://127.0.0.1:5500",
            "http://localhost:5501",
            "http://127.0.0.1:5501",
            *DEFAULT_FRONTEND_URLS,
            *configured_origins,
        ]
    )
)

API_PUBLIC_URL = os.getenv(
    "API_PUBLIC_URL",
    "https://mindcare-ai-semb.onrender.com",
).strip().rstrip("/")

app = FastAPI(
    title="Ethical Mental Health Chatbot",
    description="MindCare AI supportive mental health chatbot API",
    version=APP_VERSION,
)

security_manager = SecurityManager()


def require_audit_access(
    audit_key: Optional[str] = Header(
        default=None,
        alias="X-MindCare-Audit-Key",
    ),
):
    if not security_manager.audit_api_key_configured():
        raise HTTPException(
            status_code=503,
            detail="Audit API authentication is not configured.",
        )

    if not security_manager.validate_audit_api_key(
        audit_key or ""
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing audit API key.",
        )

    return True


logger.info(
    "MindCare API initialized | version=%s | origins=%d",
    APP_VERSION,
    len(ALLOWED_ORIGINS),
)


@app.middleware("http")
async def request_logging_middleware(
    request: Request,
    call_next,
):
    start_time = time.perf_counter()

    try:
        response = await call_next(request)

        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Cache-Control"] = "no-store"

        duration_ms = (
            time.perf_counter() - start_time
        ) * 1000

        logger.info(
            "HTTP request | method=%s | path=%s | "
            "status=%d | duration_ms=%.2f",
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
        )

        return response

    except Exception as exc:
        duration_ms = (
            time.perf_counter() - start_time
        ) * 1000

        logger.exception(
            "HTTP request failed | method=%s | path=%s | "
            "duration_ms=%.2f | error_type=%s",
            request.method,
            request.url.path,
            duration_ms,
            type(exc).__name__,
        )

        raise


app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=[
        "GET",
        "POST",
        "DELETE",
        "OPTIONS",
    ],
    allow_headers=[
        "Content-Type",
    ],
)

_session_manager: Optional[SessionManager] = None

_safety_audit = SafetyAudit(
    max_records=int(
        os.getenv(
            "MINDCARE_AUDIT_MAX_RECORDS",
            "1000",
        )
    ),
    persist=True,
    file_path=os.getenv(
        "MINDCARE_AUDIT_FILE",
        "logs/safety_audit.jsonl",
    ),
)

_rate_lock = RLock()

_rate_events: Dict[
    str,
    Deque[float],
] = defaultdict(deque)

_session_rate_events: Dict[
    str,
    Deque[float],
] = defaultdict(deque)

RATE_LIMIT_PER_MINUTE = max(
    1,
    int(
        os.getenv(
            "CHAT_RATE_LIMIT",
            "30",
        )
    ),
)

RATE_LIMIT_BURST = max(
    1,
    int(
        os.getenv(
            "CHAT_RATE_LIMIT_BURST",
            str(RATE_LIMIT_PER_MINUTE),
        )
    ),
)

SESSION_RATE_LIMIT_PER_MINUTE = max(
    1,
    int(
        os.getenv(
            "SESSION_RATE_LIMIT",
            "10",
        )
    ),
)

SESSION_RATE_LIMIT_BURST = max(
    1,
    int(
        os.getenv(
            "SESSION_RATE_LIMIT_BURST",
            str(SESSION_RATE_LIMIT_PER_MINUTE),
        )
    ),
)

RATE_WINDOW_SECONDS = 60.0


def get_session_manager() -> SessionManager:
    global _session_manager

    if _session_manager is None:
        _session_manager = SessionManager(
            session_ttl_seconds=(
                ProductionConfig.SESSION_TTL_SECONDS
            ),
            max_sessions=(
                ProductionConfig.MAX_SESSIONS
            ),
        )

        logger.info(
            "Session manager initialized | "
            "max_sessions=%d | ttl_seconds=%d",
            ProductionConfig.MAX_SESSIONS,
            ProductionConfig.SESSION_TTL_SECONDS,
        )

    return _session_manager


def _client_key(request: Request) -> str:
    return (
        request.client.host
        if request.client
        else "unknown"
    )


def _check_rate_limit(key: str) -> bool:
    now = time.monotonic()
    cutoff = now - RATE_WINDOW_SECONDS

    with _rate_lock:
        events = _rate_events[key]

        while events and events[0] <= cutoff:
            events.popleft()

        if len(events) >= RATE_LIMIT_BURST:
            return False

        events.append(now)

        if len(_rate_events) > 5000:
            stale_keys = [
                candidate
                for candidate, candidate_events
                in _rate_events.items()
                if (
                    not candidate_events
                    or candidate_events[-1] <= cutoff
                )
            ]

            for candidate in stale_keys[:1000]:
                _rate_events.pop(
                    candidate,
                    None,
                )

        return True


def _check_session_rate_limit(key: str) -> bool:
    now = time.monotonic()
    cutoff = now - RATE_WINDOW_SECONDS

    with _rate_lock:
        events = _session_rate_events[key]

        while events and events[0] <= cutoff:
            events.popleft()

        if len(events) >= SESSION_RATE_LIMIT_BURST:
            return False

        events.append(now)

        if len(_session_rate_events) > 5000:
            stale_keys = [
                candidate
                for candidate, candidate_events
                in _session_rate_events.items()
                if (
                    not candidate_events
                    or candidate_events[-1] <= cutoff
                )
            ]

            for candidate in stale_keys[:1000]:
                _session_rate_events.pop(
                    candidate,
                    None,
                )

        return True


class CreateSessionRequest(BaseModel):
    user_name: str = Field(
        default="friend",
        min_length=1,
        max_length=100,
    )


class ChatRequest(BaseModel):
    session_id: str = Field(
        min_length=36,
        max_length=100,
    )

    message: str = Field(
        min_length=1,
        max_length=4000,
    )


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
            "llm_configured": bool(
                os.getenv(
                    "OPENAI_API_KEY",
                    "",
                ).strip()
            ),
            "llm_enabled": ProductionConfig.llm_enabled(),
            "llm_model": ProductionConfig.OPENAI_MODEL,
        }

    except Exception as exc:
        logger.exception(
            "Readiness check failed | error_type=%s",
            type(exc).__name__,
        )

        return JSONResponse(
            status_code=503,
            content={
                "status": "degraded",
                "service": "mindcare-api",
            },
        )


@app.post("/session")
def create_session(
    request: CreateSessionRequest,
    http_request: Request,
):
    client_key = _client_key(http_request)

    if not _check_session_rate_limit(client_key):
        logger.warning(
            "Session creation rate limit exceeded | client=%s",
            client_key,
        )

        return JSONResponse(
            status_code=429,
            headers={
                "Retry-After": "60",
            },
            content={
                "detail": (
                    "Too many session creation requests. "
                    "Please wait a moment and try again."
                )
            },
        )

    user_name = (
        request.user_name.strip()
        or "friend"
    )

    try:
        session_id = (
            get_session_manager().create_session(
                user_name=user_name
            )
        )

        logger.info(
            "Session created | active_sessions=%d",
            get_session_manager().session_count(),
        )

        return {
            "session_id": session_id,
            "message": "Session created successfully.",
            "expires_in_seconds": (
                ProductionConfig.SESSION_TTL_SECONDS
            ),
        }

    except Exception as exc:
        logger.exception(
            "Session creation failed | error_type=%s",
            type(exc).__name__,
        )

        raise HTTPException(
            status_code=500,
            detail="Unable to create session.",
        )


@app.delete("/session/{session_id}")
def delete_session(
    session_id: str,
):
    session_id = session_id.strip()

    if not session_id:
        raise HTTPException(
            status_code=400,
            detail="Session ID cannot be empty.",
        )

    try:
        deleted = (
            get_session_manager()
            .delete_session(session_id)
        )

        if not deleted:
            logger.warning(
                "Session deletion requested for unknown session"
            )

            raise HTTPException(
                status_code=404,
                detail="Session not found.",
            )

        logger.info(
            "Session deleted | active_sessions=%d",
            get_session_manager().session_count(),
        )

        return {
            "message": "Session deleted successfully."
        }

    except HTTPException:
        raise

    except Exception as exc:
        logger.exception(
            "Session deletion failed | error_type=%s",
            type(exc).__name__,
        )

        raise HTTPException(
            status_code=500,
            detail="Unable to delete session.",
        )


@app.post("/chat")
def chat_endpoint(
    request: ChatRequest,
    http_request: Request,
):
    client_key = _client_key(http_request)

    if not _check_rate_limit(client_key):
        logger.warning(
            "Chat rate limit exceeded | client=%s",
            client_key,
        )

        return JSONResponse(
            status_code=429,
            headers={
                "Retry-After": "60",
            },
            content={
                "detail": (
                    "Too many messages. "
                    "Please wait a moment and try again."
                )
            },
        )

    session_id = request.session_id.strip()
    message = request.message.strip()
    if not session_id:
        raise HTTPException(
            status_code=400,
            detail="Session ID cannot be empty.",
        )

    if not message:
        raise HTTPException(
            status_code=422,
            detail="Message cannot be empty or whitespace only.",
        )

    try:
        engine = (
            get_session_manager()
            .get_engine(session_id)
        )

        if engine is None:
            logger.warning(
                "Chat request rejected | session_not_found=true"
            )

            raise HTTPException(
                status_code=404,
                detail="Session not found or expired.",
            )

        response = engine.generate_reply(message)

        if not isinstance(response, dict):
            logger.error(
                "Chatbot returned invalid response type | type=%s",
                type(response).__name__,
            )

            raise HTTPException(
                status_code=500,
                detail="Invalid response from chatbot engine.",
            )

        analysis = response.get(
            "analysis",
            {},
        )

        if not isinstance(analysis, dict):
            analysis = {}

        risk_level = analysis.get(
            "risk_level",
            "low",
        )

        risk_score = analysis.get(
            "risk_score",
            0.0,
        )

        signals = analysis.get(
            "signals",
            {},
        )

        if not isinstance(signals, dict):
            signals = {}

        mode = response.get(
            "mode",
            "supportive",
        )

        crisis_result = analysis.get(
            "crisis",
            {},
        )

        if not isinstance(crisis_result, dict):
            crisis_result = {}

        requires_human_support = bool(
            crisis_result.get(
                "requires_human_support",
                False,
            )
            or (
                risk_level == "high"
                and response.get("safety")
            )
        )

        requires_immediate_guidance = bool(
            crisis_result.get(
                "immediate_guidance",
                False,
            )
        )

        decision_source = analysis.get(
            "decision_source"
        )

        try:
            _safety_audit.record(
                risk_level=risk_level,
                risk_score=risk_score,
                action=mode,
                mode=mode,
                signals=signals,
                session_id=session_id,
                decision_source=decision_source,
                requires_human_support=(
                    requires_human_support
                ),
                requires_immediate_guidance=(
                    requires_immediate_guidance
                ),
            )

        except Exception as audit_error:
            logger.exception(
                "Safety audit recording failed | error_type=%s",
                type(audit_error).__name__,
            )

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
            "response_source": response.get(
                "response_source",
                "deterministic",
            ),
            "response_model": response.get(
                "response_model"
            ),
            "decision_source": analysis.get(
                "decision_source"
            ),
            "reply": response.get(
                "reply",
                (
                    "I'm here to listen. "
                    "Tell me what's on your mind."
                ),
            ),
        }

    except HTTPException:
        raise

    except Exception as exc:
        logger.exception(
            "Chatbot request failed | error_type=%s",
            type(exc).__name__,
        )

        raise HTTPException(
            status_code=500,
            detail="Chatbot error. Please try again.",
        )


@app.get("/api/audit/count")
def audit_count(
    _: bool = Depends(require_audit_access),
):
    return {
        "count": _safety_audit.count(),
    }


@app.get("/api/audit/recent")
def recent_audit_records(
    _: bool = Depends(require_audit_access),
):
    return {
        "records": _safety_audit.get_records(),
    }


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
            "audit_count": "/api/audit/count",
            "audit_recent": "/api/audit/recent",
        },
    }