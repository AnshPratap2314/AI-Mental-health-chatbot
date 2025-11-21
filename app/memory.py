class ChatMemory:
    def __init__(self,max_messages:int=10):
        self.max_messages=max_messages
        self.history=[]

    def add(self,user_message:str,bot_reply:str):
        self.history.append({
            "user":user_message,
            "bot": bot_reply
        })
        if len(self.history)>self.max_messages:
            self.history.pop(0)

    def last_user_message(self):
        if len(self.history)==0:
            return None
        return self.history[-1]["user"]

    def last_bot_reply(self):
        if len(self.history)==0:
            return None
        return self.history[-1]["bot"]

    def get_context(self)->str:
        if len(self.history)==0:
            return ""
        return " | ".join([f"User:{m['user']}" for m in self.history[-3:]])
