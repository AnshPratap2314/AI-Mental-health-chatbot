import time

from app.session_manager import SessionManager


def test_sessions_expire():
    manager = SessionManager(session_ttl_seconds=60, max_sessions=10)
    session_id = manager.create_session()
    record = manager.sessions[session_id]
    record.last_access = time.monotonic() - 61

    assert manager.get_engine(session_id) is None
    assert manager.session_count() == 0


def test_session_capacity_evicts_oldest():
    manager = SessionManager(session_ttl_seconds=600, max_sessions=2)
    first = manager.create_session()
    second = manager.create_session()
    manager.sessions[first].last_access -= 10

    third = manager.create_session()

    assert manager.has_session(first) is False
    assert manager.has_session(second) is True
    assert manager.has_session(third) is True


def test_new_sessions_have_llm_engine():
    manager = SessionManager(max_sessions=5)
    session_id = manager.create_session()
    engine = manager.get_engine(session_id)

    assert engine is not None
    assert engine.llm_engine is not None
