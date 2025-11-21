from fastapi import FastAPI
from pydantic import BaseModel
from app.behavior_engine import BehaviorEngine

app= FastAPI()
engine=BehaviorEngine(user_name="friend")

class UserMessage(BaseModel):
    message:str

@app.get("/")
def home():
    return {"message": "Mental Health Chatbot API is running."}

@app.post("/chat")
def chat_endpoint(user_input: UserMessage):
    user_message=user_input.message
    response=engine.generate_reply(user_message)
    return {
        "mode": response["mode"],
        "risk_level": response["analysis"]["risk_level"],
        "risk_score": response["analysis"]["risk_score"],
        "reply":response["reply"]
    }

