import json
import os
from datetime import datetime, timezone
from pathlib import Path
from threading import RLock
from typing import Any, Dict, Optional

try:
    import fcntl
except ImportError:
    fcntl = None


class SafetyAudit:
    """
    Safety audit recorder.

    By default, instances are in-memory only. This keeps unit tests isolated.

    For production persistence, initialize with:
        SafetyAudit(persist=True)

    or provide:
        SafetyAudit(persist=True, file_path="logs/safety_audit.jsonl")
    """

    def __init__(
        self,
        max_records: int = 1000,
        persist: bool = False,
        file_path: Optional[str] = None,
    ):
        self.max_records = max(1, int(max_records))
        self.persist = bool(persist)

        default_file = os.getenv(
            "MINDCARE_AUDIT_FILE",
            "logs/safety_audit.jsonl",
        )

        self.file_path = Path(file_path or default_file)
        self.records = []
        self._lock = RLock()

        if self.persist:
            self._load_records()

    def _read_persisted_records(self):
        """
        Read the latest valid records directly from persistent storage.

        Persistent reads use the JSONL file as the source of truth so
        multiple Gunicorn workers observe the same audit history.
        """
        if not self.file_path.exists():
            return []

        loaded = []

        try:
            with self.file_path.open("r", encoding="utf-8") as file:
                if fcntl is not None:
                    fcntl.flock(file.fileno(), fcntl.LOCK_SH)

                try:
                    for line in file:
                        line = line.strip()

                        if not line:
                            continue

                        try:
                            record = json.loads(line)

                            if isinstance(record, dict):
                                loaded.append(record)

                        except json.JSONDecodeError:
                            continue
                finally:
                    if fcntl is not None:
                        fcntl.flock(file.fileno(), fcntl.LOCK_UN)

        except OSError:
            return []

        return loaded[-self.max_records:]

    def _load_records(self) -> None:
        """Load recent valid records from the JSONL audit file."""
        self.records = self._read_persisted_records()

    def _append_to_file(self, record: Dict[str, Any]) -> bool:
        """
        Append one audit record to JSONL storage.

        An exclusive file lock prevents multiple worker processes from
        writing to the audit file at the same time.
        """
        try:
            self.file_path.parent.mkdir(parents=True, exist_ok=True)

            with self.file_path.open("a", encoding="utf-8") as file:
                if fcntl is not None:
                    fcntl.flock(file.fileno(), fcntl.LOCK_EX)

                try:
                    file.write(
                        json.dumps(
                            record,
                            ensure_ascii=False,
                        )
                        + "\n"
                    )
                    file.flush()
                    os.fsync(file.fileno())
                finally:
                    if fcntl is not None:
                        fcntl.flock(file.fileno(), fcntl.LOCK_UN)

            return True

        except OSError:
            return False

    def record(
        self,
        risk_level: str,
        action: str,
        mode: str,
        signals: Optional[Dict[str, Any]] = None,
        session_id: Optional[str] = None,
        risk_score: Optional[float] = None,
        decision_source: Optional[str] = None,
        requires_human_support: Optional[bool] = None,
        requires_immediate_guidance: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """
        Record a safety decision.

        Privacy:
        - message text is never stored
        - username is never stored
        - IP address is never stored
        - authentication data is never stored
        - full session ID is not persisted
        """
        signals = dict(signals or {})

        record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "risk_level": risk_level,
            "risk_score": risk_score,
            "action": action,
            "mode": mode,
            "signals": signals,
            "decision_source": decision_source,
            "requires_human_support": requires_human_support,
            "requires_immediate_guidance": requires_immediate_guidance,
        }

        with self._lock:
            if self.persist:
                persisted = self._append_to_file(record)

                if persisted:
                    self.records = self._read_persisted_records()
                else:
                    self.records.append(record)
                    self.records = self.records[-self.max_records:]
            else:
                self.records.append(record)
                self.records = self.records[-self.max_records:]

        return dict(record)

    def get_records(self):
        with self._lock:
            if self.persist:
                self.records = self._read_persisted_records()

            return [dict(record) for record in self.records]

    def clear(self):
        with self._lock:
            self.records.clear()

            if self.persist:
                try:
                    self.file_path.parent.mkdir(parents=True, exist_ok=True)

                    with self.file_path.open("w", encoding="utf-8") as file:
                        if fcntl is not None:
                            fcntl.flock(file.fileno(), fcntl.LOCK_EX)

                        try:
                            file.flush()
                            os.fsync(file.fileno())
                        finally:
                            if fcntl is not None:
                                fcntl.flock(file.fileno(), fcntl.LOCK_UN)

                except OSError:
                    pass

    def count(self):
        with self._lock:
            if self.persist:
                self.records = self._read_persisted_records()

            return len(self.records)