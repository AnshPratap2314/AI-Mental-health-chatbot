import os
import time
import uuid
from dataclasses import dataclass
from threading import RLock
from typing import Dict, Optional

from app.behavior_engine import BehaviorEngine
from app.llm_engine import LLMEngine


@dataclass
class _SessionRecord:
    engine: BehaviorEngine
    created_at: float
    last_access: float


class SessionManager:
    """In-memory session store with TTL and bounded capacity.

    Session IDs are high-entropy UUIDs and act as bearer credentials. They
    should be treated as secrets by the frontend and never logged.
    """

    def __init__(
        self,
        session_ttl_seconds: Optional[int] = None,
        max_sessions: Optional[int] = None,
    ):
        self.session_ttl_seconds = max(
            60,
            int(
                session_ttl_seconds
                if session_ttl_seconds is not None
                else os.getenv("SESSION_TTL_SECONDS", "1800")
            ),
        )
        self.max_sessions = max(
            1,
            int(
                max_sessions
                if max_sessions is not None
                else os.getenv("MAX_SESSIONS", "1000")
            ),
        )
        self.sessions: Dict[str, _SessionRecord] = {}
        self._lock = RLock()

    def _build_llm_engine(self) -> LLMEngine:
        enabled_env = os.getenv("ENABLE_LLM")
        if enabled_env is None:
            enabled = bool(os.getenv("OPENAI_API_KEY", "").strip())
        else:
            enabled = enabled_env.strip().lower() in {
                "1", "true", "yes", "on"
            }

        return LLMEngine(
            model=os.getenv("OPENAI_MODEL", "gpt-5-mini"),
            enabled=enabled,
        )

    def cleanup_expired(self) -> int:
        now = time.monotonic()
        removed = 0
        with self._lock:
            expired = [
                session_id
                for session_id, record in self.sessions.items()
                if now - record.last_access > self.session_ttl_seconds
            ]
            for session_id in expired:
                self.sessions.pop(session_id, None)
                removed += 1
        return removed

    def create_session(self, user_name: str = "friend") -> str:
        with self._lock:
            self.cleanup_expired()

            # Prevent unbounded memory growth. Remove the least recently used
            # sessions first when the configured capacity is reached.
            while len(self.sessions) >= self.max_sessions:
                oldest_id = min(
                    self.sessions,
                    key=lambda key: self.sessions[key].last_access,
                )
                self.sessions.pop(oldest_id, None)

            session_id = str(uuid.uuid4())
            now = time.monotonic()
            engine = BehaviorEngine(
                user_name=user_name,
                llm_engine=self._build_llm_engine(),
            )
            self.sessions[session_id] = _SessionRecord(
                engine=engine,
                created_at=now,
                last_access=now,
            )
            return session_id

    def get_engine(self, session_id: str):
        if not session_id:
            return None

        with self._lock:
            self.cleanup_expired()
            record = self.sessions.get(session_id)
            if record is None:
                return None
            record.last_access = time.monotonic()
            return record.engine

    def delete_session(self, session_id: str) -> bool:
        with self._lock:
            return self.sessions.pop(session_id, None) is not None

    def has_session(self, session_id: str) -> bool:
        with self._lock:
            self.cleanup_expired()
            return session_id in self.sessions

    def session_count(self) -> int:
        with self._lock:
            self.cleanup_expired()
            return len(self.sessions)
