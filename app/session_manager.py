import time
import uuid
from typing import Optional

from app.behavior_engine import BehaviorEngine
from app.production_config import ProductionConfig


class SessionManager:
    """
    Holds in-memory chat sessions.

    Sessions expire after SESSION_TTL_SECONDS of inactivity, and the
    total number of sessions is capped at MAX_SESSIONS (oldest sessions
    are evicted first). Without this, a long-running deployment with no
    session cleanup will grow memory usage without bound.
    """

    def __init__(
        self,
        session_ttl_seconds: Optional[int] = None,
        max_sessions: Optional[int] = None,
    ):
        self.sessions = {}
        self._last_active = {}

        self.session_ttl_seconds = (
            session_ttl_seconds
            if session_ttl_seconds is not None
            else ProductionConfig.SESSION_TTL_SECONDS
        )

        self.max_sessions = (
            max_sessions
            if max_sessions is not None
            else ProductionConfig.MAX_SESSIONS
        )

    def create_session(self, user_name: str = "friend"):
        self._evict_expired()
        self._evict_over_capacity()

        session_id = str(uuid.uuid4())

        engine = BehaviorEngine(
            user_name=user_name,
            max_memory=ProductionConfig.MAX_MEMORY,
            session_id=session_id,
        )

        self.sessions[session_id] = engine
        self._last_active[session_id] = time.monotonic()

        return session_id

    def get_engine(self, session_id: str):
        self._evict_expired()

        engine = self.sessions.get(session_id)

        if engine is not None:
            self._last_active[session_id] = time.monotonic()

        return engine

    def delete_session(self, session_id: str):
        self._last_active.pop(session_id, None)

        if session_id in self.sessions:
            del self.sessions[session_id]
            return True

        return False

    def has_session(self, session_id: str):
        self._evict_expired()
        return session_id in self.sessions

    def session_count(self):
        self._evict_expired()
        return len(self.sessions)

    def _evict_expired(self):
        if self.session_ttl_seconds <= 0:
            return

        now = time.monotonic()
        expired = [
            session_id
            for session_id, last_active in self._last_active.items()
            if now - last_active > self.session_ttl_seconds
        ]

        for session_id in expired:
            self.sessions.pop(session_id, None)
            self._last_active.pop(session_id, None)

    def _evict_over_capacity(self):
        if self.max_sessions <= 0:
            return

        while len(self.sessions) >= self.max_sessions:
            oldest_id = min(
                self._last_active,
                key=self._last_active.get,
                default=None,
            )

            if oldest_id is None:
                break

            self.sessions.pop(oldest_id, None)
            self._last_active.pop(oldest_id, None)
