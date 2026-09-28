import os

from fastapi.testclient import TestClient

import app.main as main_module
from app.main import app


client = TestClient(app)

SYNTHETIC_HIGH_RISK_MESSAGE = "I want to die"


def security_headers(response):
    assert response.headers.get("X-Content-Type-Options") == "nosniff"
    assert response.headers.get("X-Frame-Options") == "DENY"
    assert response.headers.get("Referrer-Policy") == "no-referrer"
    assert response.headers.get("Cache-Control") == "no-store"


def test_safety_audit_end_to_end():
    """
    End-to-end verification:

    session creation
        -> normal chat
        -> synthetic high-risk chat
        -> safety decision
        -> persistent audit record
        -> authenticated audit retrieval
        -> privacy verification
    """

    audit = main_module._safety_audit

    # Keep this test isolated from records created by other tests.
    original_records = audit.get_records()

    try:
        audit.clear()

        # ---------------------------------------------------------
        # 1. Create a session
        # ---------------------------------------------------------
        session_response = client.post(
            "/session",
            json={"user_name": "e2e-test-user"},
        )

        assert session_response.status_code == 200
        security_headers(session_response)

        session_data = session_response.json()

        assert "session_id" in session_data
        assert session_data["session_id"]

        session_id = session_data["session_id"]

        # ---------------------------------------------------------
        # 2. Send a normal message
        # ---------------------------------------------------------
        normal_response = client.post(
            "/chat",
            json={
                "session_id": session_id,
                "message": "I had a difficult day and feel stressed.",
            },
        )

        assert normal_response.status_code == 200
        security_headers(normal_response)

        normal_data = normal_response.json()

        assert normal_data["session_id"] == session_id
        assert "risk_level" in normal_data
        assert "risk_score" in normal_data
        assert "signals" in normal_data
        assert "mode" in normal_data
        assert "reply" in normal_data

        # ---------------------------------------------------------
        # 3. Send existing synthetic high-risk test fixture
        # ---------------------------------------------------------
        high_risk_response = client.post(
            "/chat",
            json={
                "session_id": session_id,
                "message": SYNTHETIC_HIGH_RISK_MESSAGE,
            },
        )

        assert high_risk_response.status_code == 200
        security_headers(high_risk_response)

        high_risk_data = high_risk_response.json()

        # ---------------------------------------------------------
        # 4. Verify the safety response/action
        # ---------------------------------------------------------
        assert high_risk_data["risk_level"] == "high"
        assert high_risk_data["mode"] == "crisis"

        assert "risk_score" in high_risk_data
        assert isinstance(
            high_risk_data["risk_score"],
            (int, float),
        )

        assert high_risk_data["risk_score"] >= 0.0
        assert high_risk_data["risk_score"] <= 1.0

        assert "signals" in high_risk_data
        assert isinstance(high_risk_data["signals"], dict)

        # The crisis signal should be present for the existing
        # synthetic high-risk fixture.
        assert high_risk_data["signals"].get("crisis") is True

        assert "reply" in high_risk_data
        assert high_risk_data["reply"]

        # ---------------------------------------------------------
        # 5. Verify an audit record was created
        # ---------------------------------------------------------
        records = audit.get_records()

        assert len(records) >= 2

        high_risk_records = [
            record
            for record in records
            if record.get("risk_level") == "high"
        ]

        assert high_risk_records

        audit_record = high_risk_records[-1]

        # ---------------------------------------------------------
        # 6. Verify expected audit fields
        # ---------------------------------------------------------
        assert audit_record["risk_level"] == "high"

        assert "risk_score" in audit_record
        assert isinstance(
            audit_record["risk_score"],
            (int, float),
        )

        assert audit_record["risk_score"] >= 0.0
        assert audit_record["risk_score"] <= 1.0

        assert audit_record["action"] == "crisis"
        assert audit_record["mode"] == "crisis"

        assert "signals" in audit_record
        assert isinstance(
            audit_record["signals"],
            dict,
        )

        assert audit_record["signals"].get("crisis") is True

        assert "decision_source" in audit_record

        assert audit_record["requires_human_support"] is True
        assert audit_record["requires_immediate_guidance"] is True

        # Timestamp should be present.
        assert "timestamp" in audit_record
        assert audit_record["timestamp"]

        # ---------------------------------------------------------
        # 7. Verify sensitive content is NOT stored
        # ---------------------------------------------------------
        serialized_record = str(audit_record)

        assert SYNTHETIC_HIGH_RISK_MESSAGE not in serialized_record
        assert "e2e-test-user" not in serialized_record
        assert session_id not in serialized_record

        assert "message" not in audit_record
        assert "username" not in audit_record
        assert "user_name" not in audit_record
        assert "ip" not in audit_record
        assert "ip_address" not in audit_record
        assert "api_key" not in audit_record
        assert "auth" not in audit_record
        assert "authentication" not in audit_record

        # ---------------------------------------------------------
        # 8. Verify audit endpoint authentication
        # ---------------------------------------------------------

        # No API key.
        unauthorized_response = client.get(
            "/api/audit/recent",
        )

        assert unauthorized_response.status_code == 401
        security_headers(unauthorized_response)

        # Wrong API key.
        wrong_key_response = client.get(
            "/api/audit/recent",
            headers={
                "X-MindCare-Audit-Key": "definitely-wrong-key",
            },
        )

        assert wrong_key_response.status_code == 401
        security_headers(wrong_key_response)

        # Correct API key.
        audit_key = os.getenv("MINDCARE_AUDIT_API_KEY")

        if not audit_key:
            raise AssertionError(
                "MINDCARE_AUDIT_API_KEY must be configured "
                "to run the authenticated audit E2E test."
            )

        authorized_response = client.get(
            "/api/audit/recent",
            headers={
                "X-MindCare-Audit-Key": audit_key,
            },
        )

        assert authorized_response.status_code == 200
        security_headers(authorized_response)

        authorized_data = authorized_response.json()

        assert "records" in authorized_data
        assert isinstance(
            authorized_data["records"],
            list,
        )

        retrieved_high_risk_records = [
            record
            for record in authorized_data["records"]
            if record.get("risk_level") == "high"
        ]

        assert retrieved_high_risk_records

        retrieved_record = retrieved_high_risk_records[-1]

        assert retrieved_record["risk_level"] == "high"
        assert retrieved_record["action"] == "crisis"
        assert retrieved_record["mode"] == "crisis"
        assert retrieved_record["requires_human_support"] is True
        assert retrieved_record["requires_immediate_guidance"] is True

        # Verify privacy after retrieval as well.
        retrieved_serialized = str(retrieved_record)

        assert SYNTHETIC_HIGH_RISK_MESSAGE not in retrieved_serialized
        assert "e2e-test-user" not in retrieved_serialized
        assert session_id not in retrieved_serialized

        assert "message" not in retrieved_record
        assert "username" not in retrieved_record
        assert "user_name" not in retrieved_record
        assert "ip" not in retrieved_record
        assert "ip_address" not in retrieved_record
        assert "api_key" not in retrieved_record
        assert "auth" not in retrieved_record
        assert "authentication" not in retrieved_record

    finally:
        # Restore the audit state that existed before this test.
        audit.clear()

        for record in original_records:
            audit.record(
                risk_level=record.get("risk_level", "low"),
                risk_score=record.get("risk_score"),
                action=record.get("action", "unknown"),
                mode=record.get("mode", "unknown"),
                signals=record.get("signals", {}),
                decision_source=record.get("decision_source"),
                requires_human_support=record.get(
                    "requires_human_support"
                ),
                requires_immediate_guidance=record.get(
                    "requires_immediate_guidance"
                ),
            )