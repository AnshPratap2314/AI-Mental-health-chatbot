from datetime import datetime, timezone
from typing import Any, Dict, Optional


class SafetyAudit:

    def __init__(self, max_records=100):
        self.max_records = max(
            1,
            int(max_records)
        )
        self.records = []

    def record(
        self,
        risk_level: str,
        action: str,
        mode: str,
        signals: Optional[Dict[str, Any]] = None,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:

        signals = signals or {}

        record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "risk_level": risk_level,
            "action": action,
            "mode": mode,
            "signals": dict(signals),
            "session_id": session_id
        }

        self.records.append(record)

        if len(self.records) > self.max_records:
            self.records = self.records[
                -self.max_records:
            ]

        return dict(record)

    def get_records(self):
        return [
            dict(record)
            for record in self.records
        ]

    def clear(self):
        self.records.clear()

    def count(self):
        return len(self.records)