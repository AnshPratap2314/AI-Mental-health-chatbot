from datetime import datetime, timezone
from typing import Any, Dict


class HealthManager:

    def __init__(self):
        self.started_at = datetime.now(timezone.utc)

    def check(
        self,
        behavior_engine=None
    ) -> Dict[str, Any]:

        result = {
            "status": "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "service": "mindcare",
            "python": True,
            "behavior_engine": behavior_engine is not None
        }

        if behavior_engine is not None:

            try:
                result["memory_size"] = len(
                    behavior_engine.get_memory()
                )
            except Exception:
                result["behavior_engine"] = False
                result["status"] = "degraded"

        return result