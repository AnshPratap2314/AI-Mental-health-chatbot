from app.session_manager import SessionManager


def test_create_session():

    manager = SessionManager()

    session_id = manager.create_session(
        user_name="Ansh"
    )

    assert session_id is not None
    assert manager.has_session(
        session_id
    ) is True


def test_sessions_are_unique():

    manager = SessionManager()

    session_one = manager.create_session(
        user_name="Ansh"
    )

    session_two = manager.create_session(
        user_name="Ansh"
    )

    assert session_one != session_two


def test_session_memory_is_isolated():

    manager = SessionManager()

    session_one = manager.create_session(
        user_name="Ansh"
    )

    session_two = manager.create_session(
        user_name="Ansh"
    )

    engine_one = manager.get_engine(
        session_one
    )

    engine_two = manager.get_engine(
        session_two
    )

    engine_one.generate_reply(
        "I feel lonely"
    )

    result_one = engine_one.generate_reply(
        "Tell me more"
    )

    result_two = engine_two.generate_reply(
        "Tell me more"
    )

    context_one = result_one[
        "analysis"
    ]["context"]

    context_two = result_two[
        "analysis"
    ]["context"]

    assert context_one[
        "has_previous_context"
    ] is True

    assert context_two[
        "has_previous_context"
    ] is False


def test_session_memory_contains_correct_message():

    manager = SessionManager()

    session_one = manager.create_session()

    session_two = manager.create_session()

    engine_one = manager.get_engine(
        session_one
    )

    engine_two = manager.get_engine(
        session_two
    )

    engine_one.generate_reply(
        "I feel hopeless"
    )

    result_one = engine_one.generate_reply(
        "Tell me more"
    )

    result_two = engine_two.generate_reply(
        "Tell me more"
    )

    messages_one = result_one[
        "analysis"
    ]["context"]["recent_user_messages"]

    messages_two = result_two[
        "analysis"
    ]["context"]["recent_user_messages"]

    assert "I feel hopeless" in messages_one
    assert "I feel hopeless" not in messages_two


def test_delete_session():

    manager = SessionManager()

    session_id = manager.create_session()

    assert manager.has_session(
        session_id
    ) is True

    deleted = manager.delete_session(
        session_id
    )

    assert deleted is True

    assert manager.has_session(
        session_id
    ) is False

    assert manager.get_engine(
        session_id
    ) is None


def test_delete_unknown_session():

    manager = SessionManager()

    deleted = manager.delete_session(
        "unknown-session"
    )

    assert deleted is False


def test_session_count():

    manager = SessionManager()

    assert manager.session_count() == 0

    session_one = manager.create_session()
    assert manager.session_count() == 1

    session_two = manager.create_session()
    assert manager.session_count() == 2

    manager.delete_session(session_one)

    assert manager.session_count() == 1

    manager.delete_session(session_two)

    assert manager.session_count() == 0
