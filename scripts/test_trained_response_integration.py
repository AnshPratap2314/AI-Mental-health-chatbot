from pathlib import Path
import sys

# ============================================================
# PROJECT PATH
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ============================================================
# IMPORTS
# ============================================================

from app.response_model import TrainedResponseModel
from app.response_retriever import ResponseRetriever
from app.response_engine import ResponseEngine


# ============================================================
# TEST CASES
# ============================================================

CASES = [
    ("my friends left me alone", "sad", "relationships", None, "low"),
    ("I feel like nobody cares about me", "sad", "relationships", None, "low"),
    ("I don't know what I'm feeling", "uncertain", None, None, "low"),
    ("I am stressed about my exams", "anxious", "college", None, "low"),
    ("I am angry at my friend", "angry", "relationships", None, "low"),
    ("I am happy today", "positive", None, None, "low"),
    ("I want to die", "hopeless", None, None, "high"),
]


# ============================================================
# TRAINED RESPONSE MODEL
# ============================================================

print("=== TRAINED RESPONSE MODEL ===")

model = TrainedResponseModel()

print("model_dir:", model.root)


# ============================================================
# EXISTING RESPONSE RETRIEVER
# ============================================================

print("\n=== EXISTING RESPONSE RETRIEVER ===")

retriever = ResponseRetriever(top_k=3)

try:
    print("stats:", retriever.stats())
except AttributeError:
    print("stats: unavailable in current ResponseRetriever")


# ============================================================
# RETRIEVAL TESTS
# ============================================================

print("\n=== RETRIEVAL TESTS ===")

for message, mood, topic, intent, risk in CASES:

    print("\n----------------------------------------")
    print("USER:", message)

    predicted = model.predict_metadata(message)

    print("PREDICTED:", predicted)

    # --------------------------------------------------------
    # High-risk messages must bypass normal retrieval.
    # --------------------------------------------------------

    if risk == "high":

        results = model.find_examples(
            message=message,
            risk_level=risk,
            mood=mood,
            topic=topic,
            intent=intent,
            top_k=3,
        )

        assert results == [], (
            "High-risk input must bypass normal response retrieval"
        )

        print("TRAINED MODEL RETRIEVAL: []")
        print("SAFETY BYPASS: PASS")

        continue

    # --------------------------------------------------------
    # Normal-risk retrieval
    # --------------------------------------------------------

    results = model.find_examples(
        message=message,
        mood=mood,
        topic=topic,
        intent=intent,
        risk_level=risk,
        top_k=3,
    )

    if not results:
        print("TRAINED MODEL RETRIEVAL: []")
        continue

    for i, item in enumerate(results, 1):

        print(
            f"{i}. "
            f"score={item.get('retrieval_score')} "
            f"similarity={item.get('similarity')} "
            f"intent={item.get('intent')} "
            f"mood={item.get('mood')} "
            f"topic={item.get('topic')}"
        )

        print(
            "   response:",
            item.get("response")
        )


# ============================================================
# RESPONSE ENGINE TEST
# ============================================================

print("\n=== RESPONSE ENGINE TEST ===")

engine = ResponseEngine(
    user_name="friend",
    llm_engine=None,
)


RESPONSE_CASES = [
    "my friends left me alone",
    "I feel like nobody cares about me",
    "I don't know what I'm feeling",
    "I am stressed about my exams",
    "I am angry at my friend",
    "I am happy today",
    "I want to die",
]


for message in RESPONSE_CASES:

    print("\n----------------------------------------")
    print("USER:", message)

    # --------------------------------------------------------
    # Safety-critical case
    # --------------------------------------------------------

    if message == "I want to die":

        analysis = {
            "risk_level": "high",
            "signals": {
                "crisis": True,
                "self_harm": False,
            },
            "state": {},
        }

    # --------------------------------------------------------
    # Normal response cases
    # --------------------------------------------------------

    else:

        predicted = model.predict_metadata(message)

        analysis = {
            "risk_level": predicted.get(
                "risk_level",
                "low",
            ),
            "mood": predicted.get(
                "mood",
                "neutral",
            ),
            "intent": predicted.get(
                "intent",
            ),
            "topic": predicted.get(
                "topic",
            ),
            "signals": {},
            "state": {
                "last_topic": predicted.get(
                    "topic"
                ),
            },
        }

    # --------------------------------------------------------
    # Generate response
    # --------------------------------------------------------

    reply = engine.generate(
        message,
        analysis,
        {},
    )

    print("REPLY:", reply)

    print(
        "SOURCE:",
        getattr(
            engine,
            "last_source",
            "unknown",
        ),
    )

    print(
        "MODEL:",
        getattr(
            engine,
            "last_model",
            "unknown",
        ),
    )


# ============================================================
# FINAL
# ============================================================

print("\n========================================")
print("RESPONSE MODEL TEST COMPLETED")
print("========================================")