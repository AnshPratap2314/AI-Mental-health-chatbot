import re
import random
from typing import Dict,Tuple,Optional
from app.memory import ChatMemory


def contains_pattern(text: str,patterns)->bool:
    text=text.lower()
    for p in patterns:
        if re.search(p,text):
            return True
    return False

def find_first_pattern(text:str, patterns)->Optional[str]:
    text=text.lower()
    for p in patterns:
        m=re.search(p,text)
        if m:
            return m.group(0)
    return None

CASUAL_MARKERS = [
    r"\bbro\b", r"\bbruh\b", r"\blol\b", r"\blmao\b",
    r"😂", r"🤣", r"😅", r"😎", r"🙂", r"brooo", r"broo"
]

SAD_MARKERS = [
    r"\bsad\b", r"\bdown\b", r"\blower\b", r"\bempty\b",
    r"\bnot okay\b", r"\bcry\b", r"😔", r"😞", r"😭", r"😢"
]

SERIOUS_MARKERS = [
    r"\bhelpless\b", r"\bhopeless\b", r"\bworthless\b",
    r"\bfalling apart\b", r"\bcannot handle\b", r"\bi can't\b"
]

CRISIS_MARKERS = [
    r"\bwant to die\b", r"\bi want to die\b", r"\bsuicide\b",
    r"\bsuicidal\b", r"\bhurt myself\b", r"\bkill myself\b",
    r"\bno reason to live\b"
]

PLAN_MARKERS = [
    r"\bplan\b", r"\bplanning\b", r"\btonight\b",
    r"\bpills\b", r"\bknife\b", r"\brope\b"
]

PROTECTIVE_MARKERS = [
    r"\bfamily\b", r"\bfriends\b", r"\bpet\b",
    r"\bfuture\b", r"\btomorrow\b"
]
def detect_mood(msg: str) -> str:
    msg = msg.lower()

    if contains_pattern(msg, CRISIS_MARKERS):
        return "crisis"
    if contains_pattern(msg, SAD_MARKERS):
        return "sad"
    if contains_pattern(msg, SERIOUS_MARKERS):
        return "serious"
    if contains_pattern(msg, CASUAL_MARKERS):
        return "casual"

    return "neutral"

def detect_tone(msg: str) -> str:
    return detect_mood(msg)

def risk_score(message: str) -> Tuple[str, float]:
    msg = message.lower()
    score = 0.0

    if contains_pattern(msg, CRISIS_MARKERS):
        score += 0.7
    if contains_pattern(msg, SERIOUS_MARKERS):
        score += 0.25
    if contains_pattern(msg, SAD_MARKERS):
        score += 0.15
    if contains_pattern(msg, PLAN_MARKERS):
        score += 0.20

    if not contains_pattern(msg, PROTECTIVE_MARKERS):
        score += 0.05

    score = min(max(score, 0), 1)

    if score >= 0.7:
        return "high", round(score, 2)
    elif score >= 0.35:
        return "moderate", round(score, 2)
    return "low", round(score, 2)

TEMPLATES = {
    "casual": [
        "Bro, I get you 😅. What happened?",
        "Haha I feel you bro 😂. Tell me more!",
        "Brooo I understand you 💀. what’s going on?"
    ],
    "sad": [
        "I’m really sorry you're feeling this way 😔. Want to talk about it?",
        "That sounds really tough… I’m here with you 🤍.",
        "Thank you for sharing that. What’s making you feel this way?"
    ],
    "serious": [
        "That sounds extremely heavy. I’m right here with you.",
        "I hear you… that must be very overwhelming.",
        "I’m here with you. What’s been hurting you the most?"
    ],
    "crisis": [
        "I’m really sorry you’re feeling this kind of pain. You deserve safety and help.",
        "This is serious and you matter. If you’re in danger, please contact your local emergency number."
    ],
    "neutral": [
        "I'm here for you. Tell me what's going on.",
        "I'm listening — tell me anything.",
        "What’s on your mind?"
    ]
}

MOTIVATION = [
    "You’ve survived all your hardest days so far — that’s strength.",
    "It’s okay to take things one step at a time.",
    "Your feelings are valid and important.",
    "You're doing the best you can, and that's enough."
]

GROUNDING = [
    "Let’s try grounding: name 5 things you can see around you.",
    "Name 4 things you can touch right now.",
    "Name 3 things you can hear.",
    "Name 2 things you can smell.",
    "Name 1 thing you can taste."
]

BREATHING = [
    "Try this: breathe in for 4s… hold 4s… exhale for 6s. Repeat 4 times."
]
def generate_ai_comfort(message:str,mood:str,tone:str,risk:str)->str:
    msg=message.lower()
    if risk == "high":
        return (
            "I’m really sorry you're feeling such intense pain. You don’t deserve to face this alone. "
            "I’m here with you right now — your safety matters more than anything."
        )

    if mood == "serious" or tone == "serious":
        return (
            "I can hear how heavy this feels. It takes courage to say it out loud. "
            "You’re not alone — I’m right here with you."
        )

    if mood == "sad":
        return (
            "Your feelings are real, and they matter. It’s okay to feel this way. "
            "I’m here to support you through it."
        )

    if mood == "casual":
        return (
            "Brooo I get you 😂😭. Life really be wild sometimes. Tell me what’s up?"
        )

    return "I'm here with you — whatever you're feeling, you can talk to me."


class BehaviorEngine:
    def __init__(self,user_name="friend"):
        self.user_name=user_name
        self.last_user_message=None
        self.repetition_count=0

    def analyze(self,message:str)->Dict:
        mood=detect_mood(message)
        tone=detect_tone(message)
        risk_level,score=risk_score(message)
        return{
            "message": message,
            "mood": mood,
            "tone": tone,
            "risk_level": risk_level,
            "risk_score": score
        }

    def choose_mode(self, analysis: Dict) -> str:
        if analysis["risk_level"] == "high" or analysis["tone"] == "crisis":
            return "crisis"
        if analysis["risk_level"] == "moderate" or analysis["tone"] == "serious":
            return "serious"
        if analysis["tone"] == "sad":
            return "sad"
        if analysis["tone"] == "casual":
            return "casual"
        return "neutral"

    def memory_context_reply(self,current:str)->Optional[str]:
        if not self.last_user_message:
            return None
        if current.lower() == self.last_user_message.lower():
            self.repetition_count += 1
        else:
            self.repetition_count = 0

        if self.repetition_count >= 2:
            return "It seems this thought is really repeating for you… I'm here."

        return None

    def generate_reply(self, message: str) -> Dict:
        analysis = self.analyze(message)
        mode = self.choose_mode(analysis)
        memory=self.memory_context_reply(message)
        self.last_user_message=message
        base=random.choice(TEMPLATES[mode])
        ai=generate_ai_comfort(
            message,
            analysis["mood"],
            analysis["tone"],
            analysis["risk_level"]
        )

        comfort = ""
        if mode in ["sad", "serious"] and random.random() < 0.5:
            comfort = " " + random.choice(MOTIVATION)
        breathing=""
        if mode == "sad" and random.random() < 0.25:
            breathing = " " + random.choice(BREATHING)
        if memory:
            reply = memory + " " + base
        else:
            reply = base + comfort + breathing

        return {"mode": mode, "analysis": analysis, "reply": reply}

