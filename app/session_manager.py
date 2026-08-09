import uuid

from app.behavior_engine import BehaviorEngine


class SessionManager:

    def __init__(self):
        self.sessions = {}

    def create_session(self, user_name: str = "friend"):

        session_id = str(
            uuid.uuid4()
        )

        engine = BehaviorEngine(
            user_name=user_name
        )

        self.sessions[session_id] = engine

        return session_id

    def get_engine(self, session_id: str):

        return self.sessions.get(
            session_id
        )

    def delete_session(self, session_id: str):

        if session_id in self.sessions:

            del self.sessions[session_id]

            return True

        return False

    def has_session(self, session_id: str):

        return session_id in self.sessions

    def session_count(self):

        return len(self.sessions)