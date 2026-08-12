from typing import Any, Dict, List, Optional


class ContextState:
    def __init__(self):
        self.current_mood = None
        self.previous_mood = None
        self.current_risk = None
        self.previous_risk = None
        self.last_topic = None
        self.previous_topic = None
        self.message_count = 0
        self.same_topic_streak = 0
        self.last_intent = None
        self.previous_intent = None
        self.last_strategy = None
        self.previous_strategy = None
        self.strategy_streak = 0
        self.recent_strategies: List[str] = []

    def update(
        self,
        mood="neutral",
        risk_level="low",
        topic=None,
        intent=None
    ):
        self.previous_mood = self.current_mood
        self.previous_risk = self.current_risk
        self.previous_topic = self.last_topic
        self.previous_intent = self.last_intent

        self.current_mood = mood
        self.current_risk = risk_level
        self.last_intent = intent

        if topic is not None:
            if topic == self.last_topic:
                self.same_topic_streak += 1
            else:
                self.same_topic_streak = 0
            self.last_topic = topic

        self.message_count += 1

    def record_follow_up(
        self,
        mood=None,
        risk_level=None,
        intent=None
    ):
        self.previous_mood = self.current_mood
        self.previous_risk = self.current_risk
        self.previous_intent = self.last_intent

        if mood is not None:
            self.current_mood = mood

        if risk_level is not None:
            self.current_risk = risk_level

        if intent is not None:
            self.last_intent = intent

        if self.last_topic is not None:
            self.same_topic_streak += 1

        self.message_count += 1

    def record_strategy(self, strategy: Optional[str]):
        if not strategy:
            return

        self.previous_strategy = self.last_strategy

        if strategy == self.last_strategy:
            self.strategy_streak += 1
        else:
            self.strategy_streak = 1

        self.last_strategy = strategy
        self.recent_strategies.append(strategy)

        if len(self.recent_strategies) > 8:
            self.recent_strategies = self.recent_strategies[-8:]

    def get_state(self) -> Dict[str, Any]:
        return {
            "current_mood": self.current_mood,
            "previous_mood": self.previous_mood,
            "current_risk": self.current_risk,
            "previous_risk": self.previous_risk,
            "last_topic": self.last_topic,
            "previous_topic": self.previous_topic,
            "message_count": self.message_count,
            "same_topic_streak": self.same_topic_streak,
            "last_intent": self.last_intent,
            "previous_intent": self.previous_intent,
            "last_strategy": self.last_strategy,
            "previous_strategy": self.previous_strategy,
            "strategy_streak": self.strategy_streak,
            "recent_strategies": list(self.recent_strategies)
        }

    def reset(self):
        self.current_mood = None
        self.previous_mood = None
        self.current_risk = None
        self.previous_risk = None
        self.last_topic = None
        self.previous_topic = None
        self.message_count = 0
        self.same_topic_streak = 0
        self.last_intent = None
        self.previous_intent = None
        self.last_strategy = None
        self.previous_strategy = None
        self.strategy_streak = 0
        self.recent_strategies = []