from typing import Any, Dict, Optional


class UserProfile:

    def __init__(
        self,
        user_name="friend"
    ):
        self.user_name = user_name or "friend"
        self.preferred_tone = "supportive"
        self.preferred_language = "en"
        self.preferences = {}
        self.interests = []
        self.topic_history = []
        self.mood_history = []

    def update(
        self,
        user_name: Optional[str] = None,
        tone: Optional[str] = None,
        language: Optional[str] = None,
        preferences: Optional[Dict[str, Any]] = None
    ):

        if user_name:
            self.user_name = user_name

        if tone:
            self.preferred_tone = str(
                tone
            ).lower()

        if language:
            self.preferred_language = str(
                language
            ).lower()

        if preferences:
            self.preferences.update(
                preferences
            )

    def add_topic(
        self,
        topic: Optional[str]
    ):

        if not topic:
            return

        if topic not in self.topic_history:
            self.topic_history.append(topic)

        self.topic_history = self.topic_history[-20:]

    def add_mood(
        self,
        mood: Optional[str]
    ):

        if not mood:
            return

        self.mood_history.append(mood)
        self.mood_history = self.mood_history[-20:]

    def add_interest(
        self,
        interest: Optional[str]
    ):

        if not interest:
            return

        if interest not in self.interests:
            self.interests.append(interest)

        self.interests = self.interests[-20:]

    def get(self) -> Dict[str, Any]:

        return {
            "user_name": self.user_name,
            "preferred_tone": self.preferred_tone,
            "preferred_language": self.preferred_language,
            "preferences": dict(self.preferences),
            "interests": list(self.interests),
            "topic_history": list(self.topic_history),
            "mood_history": list(self.mood_history)
        }

    def reset(self):

        self.preferred_tone = "supportive"
        self.preferred_language = "en"
        self.preferences = {}
        self.interests = []
        self.topic_history = []
        self.mood_history = []