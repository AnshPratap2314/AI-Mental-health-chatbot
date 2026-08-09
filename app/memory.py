from typing import Dict, List, Optional


class ChatMemory:

    def __init__(self, max_messages: int = 10):

        self.max_messages = max_messages
        self.history: List[Dict[str, str]] = []

    def add(
        self,
        user_message: str,
        bot_reply: str
    ):

        self.history.append({
            "user": user_message,
            "bot": bot_reply
        })

        if len(self.history) > self.max_messages:
            self.history.pop(0)

    def last_user_message(self) -> Optional[str]:

        if not self.history:
            return None

        return self.history[-1]["user"]

    def last_bot_reply(self) -> Optional[str]:

        if not self.history:
            return None

        return self.history[-1]["bot"]

    def get_recent_messages(
        self,
        count: int = 3
    ) -> List[Dict[str, str]]:

        return self.history[-count:]

    def get_context(
        self,
        count: int = 3
    ) -> str:

        recent = self.get_recent_messages(count)

        if not recent:
            return ""

        context = []

        for item in recent:
            context.append(
                f"User: {item['user']}"
            )
            context.append(
                f"Bot: {item['bot']}"
            )

        return "\n".join(context)

    def clear(self):

        self.history.clear()

    def message_count(self) -> int:

        return len(self.history)