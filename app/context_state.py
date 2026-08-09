class ContextState:

    def __init__(self):
        self.current_mood = None
        self.previous_mood = None
        self.current_risk = None
        self.previous_risk = None
        self.last_topic = None
        self.previous_topic = None
        self.message_count = 0

    def update(
        self,
        mood="neutral",
        risk_level="low",
        topic=None
    ):
        self.previous_mood = self.current_mood
        self.previous_risk = self.current_risk
        self.previous_topic = self.last_topic

        self.current_mood = mood
        self.current_risk = risk_level

        if topic is not None:
            self.last_topic = topic

        self.message_count += 1

    def record_follow_up(
        self,
        mood=None,
        risk_level=None
    ):
        self.previous_mood = self.current_mood
        self.previous_risk = self.current_risk

        if mood is not None:
            self.current_mood = mood

        if risk_level is not None:
            self.current_risk = risk_level

        self.message_count += 1

    def get_state(self):
        return {
            "current_mood": self.current_mood,
            "previous_mood": self.previous_mood,
            "current_risk": self.current_risk,
            "previous_risk": self.previous_risk,
            "last_topic": self.last_topic,
            "previous_topic": self.previous_topic,
            "message_count": self.message_count
        }

    def reset(self):
        self.current_mood = None
        self.previous_mood = None
        self.current_risk = None
        self.previous_risk = None
        self.last_topic = None
        self.previous_topic = None
        self.message_count = 0