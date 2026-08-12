from typing import Any, Dict, List, Optional
import re


class ContextEngine:
    def __init__(self, max_context_messages: int = 8):
        self.max_context_messages = max(1, int(max_context_messages))

    def _safe_history(self, history: Optional[List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        if not isinstance(history, list):
            return []
        return [item for item in history if isinstance(item, dict)][-self.max_context_messages:]

    def get_recent_user_messages(self, history: List[Dict[str, Any]]) -> List[str]:
        return [
            str(item.get("user", "")).strip()
            for item in self._safe_history(history)
            if str(item.get("user", "")).strip()
        ]

    def get_recent_bot_messages(self, history: List[Dict[str, Any]]) -> List[str]:
        return [
            str(item.get("bot", "")).strip()
            for item in self._safe_history(history)
            if str(item.get("bot", "")).strip()
        ]

    def get_turns(self, history: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        turns = []
        for item in self._safe_history(history):
            user = str(item.get("user", "")).strip()
            bot = str(item.get("bot", "")).strip()
            if user or bot:
                turns.append({"user": user, "bot": bot})
        return turns

    def build_context(self, history: List[Dict[str, Any]]) -> str:
        parts = []
        for item in self.get_turns(history):
            if item["user"]:
                parts.append(f"User: {item['user']}")
            if item["bot"]:
                parts.append(f"MindCare: {item['bot']}")
        return "\n".join(parts)

    def build_structured_context(self, history: List[Dict[str, Any]]) -> Dict[str, Any]:
        turns = self.get_turns(history)
        last_turn = turns[-1] if turns else {"user": "", "bot": ""}
        return {
            "message_count": len(turns),
            "has_previous_context": bool(turns),
            "recent_user_messages": [x["user"] for x in turns if x["user"]],
            "recent_bot_messages": [x["bot"] for x in turns if x["bot"]],
            "recent_assistant_messages": [x["bot"] for x in turns if x["bot"]],
            "turns": turns,
            "last_user_message": last_turn["user"],
            "last_bot_reply": last_turn["bot"],
            "conversation_text": self.build_context(history)
        }

    def analyze_context(self, history: List[Dict[str, Any]]) -> Dict[str, Any]:
        return self.build_structured_context(history)

    def has_previous_signal(self, history: List[Dict[str, Any]], keywords: List[str]) -> bool:
        text = self.build_context(history).lower()
        return any(str(keyword).lower() in text for keyword in keywords)

    def context_risk_boost(self, history: List[Dict[str, Any]]) -> float:
        text = self.build_context(history).lower()
        if not text:
            return 0.0
        serious = ["hopeless", "helpless", "worthless", "can't cope", "cannot cope", "can't handle", "cannot handle", "feel trapped"]
        crisis = ["suicide", "kill myself", "end my life", "hurt myself", "harm myself"]
        boost = 0.0
        if any(x in text for x in serious):
            boost += 0.10
        if any(x in text for x in crisis):
            boost += 0.20
        return min(round(boost, 3), 0.25)

    def detect_follow_up(self, message: str) -> bool:
        text = re.sub(r"\s+", " ", str(message or "").lower().strip())
        phrases = ["tell me more", "go on", "continue", "what do you mean", "and then", "what else", "why", "how", "what should i do", "what can i do", "what do i do", "more about that", "can you explain", "then what"]
        return text in phrases or any(text.startswith(p) for p in phrases if len(p) > 5)

    def extract_focus(self, message: str, previous_topic: Optional[str] = None) -> Dict[str, Any]:
        text = str(message or "").lower()
        patterns = {
            "college": ["college", "exam", "semester", "assignment", "university", "class", "marks", "grades"],
            "career": ["job", "career", "internship", "interview", "placement", "resume", "work", "office"],
            "relationships": ["relationship", "breakup", "girlfriend", "boyfriend", "partner", "dating", "love"],
            "family": ["family", "mother", "father", "mom", "dad", "parents", "brother", "sister"],
            "friends": ["friend", "friendship", "best friend", "friends"],
            "health": ["health", "sleep", "pain", "sick", "doctor", "medicine", "symptom"],
            "money": ["money", "financial", "finance", "debt", "salary", "rent", "expenses"],
            "social": ["alone", "lonely", "social", "isolated", "isolation", "people"],
            "future": ["future", "tomorrow", "next year", "life ahead", "career path"]
        }
        scores = {key: sum(1 for term in terms if term in text) for key, terms in patterns.items()}
        focus = max(scores, key=scores.get) if any(scores.values()) else (previous_topic or "general")
        return {
            "focus": focus,
            "is_follow_up": self.detect_follow_up(message),
            "confidence": min(max(scores.values(), default=0) / 3.0, 1.0)
        }
