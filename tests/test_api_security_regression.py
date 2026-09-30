from fastapi.testclient import TestClient

import app.main as main_module
from app.main import app


client = TestClient(app)

VALID_ORIGIN = "https://mindcare-ai-o1e5.onrender.com"
INVALID_ORIGIN = "https://evil-example.invalid"


def security_headers(response):
    assert response.headers.get("X-Content-Type-Options") == "nosniff"
    assert response.headers.get("X-Frame-Options") == "DENY"
    assert response.headers.get("Referrer-Policy") == "no-referrer"
    assert response.headers.get("Cache-Control") == "no-store"


def test_health_endpoint_is_public_and_secure():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

    security_headers(response)


def test_chat_get_method_not_allowed():
    response = client.get("/chat")

    assert response.status_code == 405
    assert response.headers.get("allow") == "POST"

    security_headers(response)


def test_session_get_method_not_allowed():
    response = client.get("/session")

    assert response.status_code == 405
    assert response.headers.get("allow") == "POST"

    security_headers(response)


def test_chat_delete_method_not_allowed():
    response = client.delete("/chat")

    assert response.status_code == 405
    assert response.headers.get("allow") == "POST"

    security_headers(response)


def test_unknown_endpoint_returns_404():
    response = client.get("/api/nonexistent")

    assert response.status_code == 404

    security_headers(response)


def test_malformed_session_json_rejected():
    response = client.post(
        "/session",
        content='{"user_name":',
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code == 422
    security_headers(response)


def test_malformed_chat_json_rejected():
    response = client.post(
        "/chat",
        content='{"session_id":',
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code == 422
    security_headers(response)


def test_chat_missing_required_fields_rejected():
    response = client.post("/chat", json={})

    assert response.status_code == 422
    security_headers(response)


def test_chat_short_session_id_rejected():
    response = client.post(
        "/chat",
        json={
            "session_id": "short",
            "message": "hello",
        },
    )

    assert response.status_code == 422
    security_headers(response)


def test_chat_oversized_session_id_rejected():
    response = client.post(
        "/chat",
        json={
            "session_id": "a" * 101,
            "message": "hello",
        },
    )

    assert response.status_code == 422
    security_headers(response)


def test_chat_oversized_message_rejected():
    response = client.post(
        "/chat",
        json={
            "session_id": "a" * 36,
            "message": "a" * 4001,
        },
    )

    assert response.status_code == 422
    security_headers(response)


def test_session_oversized_username_rejected():
    response = client.post(
        "/session",
        json={
            "user_name": "a" * 101,
        },
    )

    assert response.status_code == 422
    security_headers(response)


def test_chat_empty_message_rejected():
    response = client.post(
        "/chat",
        json={
            "session_id": "a" * 36,
            "message": "",
        },
    )

    assert response.status_code == 422
    security_headers(response)


def test_chat_whitespace_message_rejected():
    response = client.post(
        "/chat",
        json={
            "session_id": "a" * 36,
            "message": "   ",
        },
    )

    assert response.status_code == 422
    assert response.json()["detail"] == (
        "Message cannot be empty or whitespace only."
    )
    security_headers(response)


def test_text_plain_request_rejected():
    response = client.post(
        "/session",
        content="hello",
        headers={"Content-Type": "text/plain"},
    )

    assert response.status_code == 422
    security_headers(response)


def test_valid_cors_origin_allowed():
    response = client.options(
        "/session",
        headers={
            "Origin": VALID_ORIGIN,
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        },
    )

    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == VALID_ORIGIN
    assert "POST" in response.headers.get(
        "access-control-allow-methods",
        "",
    )
    assert "content-type" in response.headers.get(
        "access-control-allow-headers",
        "",
    ).lower()


def test_invalid_cors_origin_rejected():
    response = client.options(
        "/session",
        headers={
            "Origin": INVALID_ORIGIN,
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        },
    )

    assert response.status_code == 400
    assert "Disallowed CORS origin" in response.text


def test_audit_count_requires_authentication():
    response = client.get("/api/audit/count")

    assert response.status_code == 401
    security_headers(response)


def test_audit_recent_requires_authentication():
    response = client.get("/api/audit/recent")

    assert response.status_code == 401
    security_headers(response)


def test_audit_count_rejects_wrong_key(monkeypatch):
    monkeypatch.setenv(
        "MINDCARE_AUDIT_API_KEY",
        "test-real-key",
    )

    response = client.get(
        "/api/audit/count",
        headers={"X-MindCare-Audit-Key": "wrong-key"},
    )

    assert response.status_code == 401
    security_headers(response)


def test_audit_recent_rejects_wrong_key(monkeypatch):
    monkeypatch.setenv(
        "MINDCARE_AUDIT_API_KEY",
        "test-real-key",
    )

    response = client.get(
        "/api/audit/recent",
        headers={"X-MindCare-Audit-Key": "wrong-key"},
    )

    assert response.status_code == 401
    security_headers(response)


def test_chat_rate_limit_returns_429():
    original_burst = main_module.RATE_LIMIT_BURST

    try:
        main_module.RATE_LIMIT_BURST = 2

        with main_module._rate_lock:
            main_module._rate_events.clear()

        session_response = client.post(
            "/session",
            json={"user_name": "rate-limit-test"},
        )

        assert session_response.status_code == 200

        session_id = session_response.json()["session_id"]

        responses = [
            client.post(
                "/chat",
                json={
                    "session_id": session_id,
                    "message": "hello",
                },
            )
            for _ in range(3)
        ]

        assert responses[0].status_code == 200
        assert responses[1].status_code == 200
        assert responses[2].status_code == 429

        assert responses[2].headers.get("Retry-After") == "60"

        assert responses[2].json()["detail"] == (
            "Too many messages. "
            "Please wait a moment and try again."
        )

        security_headers(responses[2])

    finally:
        main_module.RATE_LIMIT_BURST = original_burst

        with main_module._rate_lock:
            main_module._rate_events.clear()


def test_session_creation_rate_limit_returns_429():
    original_burst = main_module.SESSION_RATE_LIMIT_BURST

    try:
        main_module.SESSION_RATE_LIMIT_BURST = 2

        with main_module._rate_lock:
            main_module._session_rate_events.clear()

        responses = [
            client.post(
                "/session",
                json={"user_name": "rate-limit-test"},
            )
            for _ in range(3)
        ]

        assert responses[0].status_code == 200
        assert responses[1].status_code == 200
        assert responses[2].status_code == 429

        assert responses[2].headers.get("Retry-After") == "60"

        assert responses[2].json()["detail"] == (
            "Too many session creation requests. "
            "Please wait a moment and try again."
        )

        security_headers(responses[2])

    finally:
        main_module.SESSION_RATE_LIMIT_BURST = original_burst

        with main_module._rate_lock:
            main_module._session_rate_events.clear()