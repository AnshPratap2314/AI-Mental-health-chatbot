from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from app.session_manager import SessionManager


app = FastAPI(
    title="Ethical Mental Health Chatbot",
    version="1.0.0"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
session_manager = SessionManager()


class CreateSessionRequest(BaseModel):
    user_name: str = "friend"


class ChatRequest(BaseModel):
    session_id: str
    message: str


@app.get("/")
def home():

    return {
        "message": "Mental Health Chatbot API is running.",
        "version": "1.0.0"
    }


@app.post("/session")
def create_session(
    request: CreateSessionRequest
):

    session_id = session_manager.create_session(
        user_name=request.user_name
    )

    return {
        "session_id": session_id,
        "message": "Session created successfully."
    }


@app.delete("/session/{session_id}")
def delete_session(
    session_id: str
):

    deleted = session_manager.delete_session(
        session_id
    )

    if not deleted:

        raise HTTPException(
            status_code=404,
            detail="Session not found."
        )

    return {
        "message": "Session deleted successfully."
    }


@app.post("/chat")
def chat_endpoint(
    request: ChatRequest
):

    engine = session_manager.get_engine(
        request.session_id
    )

    if engine is None:

        raise HTTPException(
            status_code=404,
            detail="Session not found."
        )

    response = engine.generate_reply(
        request.message
    )

    return {
        "session_id": request.session_id,
        "mode": response["mode"],
        "risk_level": response["analysis"]["risk_level"],
        "risk_score": response["analysis"]["risk_score"],
        "signals": response["analysis"]["signals"],
        "context": response["analysis"]["context"],
        "reply": response["reply"]
    }