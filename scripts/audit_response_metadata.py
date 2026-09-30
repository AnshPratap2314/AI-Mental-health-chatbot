from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "mindcare_responses"

EXPECTED = {
    "greeting": ({"neutral", "positive"}, {"conversation", "social", "casual"}),
    "positive": ({"positive", "good", "hopeful"}, {"good_news", "personal", "daily_life"}),
    "sadness": ({"sad", "low"}, {"emotions", "daily_life"}),
    "loneliness": ({"sad", "lonely"}, {"social", "relationships"}),
    "exam_stress": ({"anxious", "stressed", "worried"}, {"college", "exams"}),
    "anxiety": ({"anxious", "worried"}, {"daily_life", "worry", "uncertainty"}),
    "relationship": ({"angry", "sad", "uncertain"}, {"friends", "relationships"}),
    "family": ({"sad", "frustrated", "uncertain"}, {"family", "home"}),
    "career": ({"worried", "uncertain", "motivated"}, {"career", "future"}),
    "work_stress": ({"stressed", "overwhelmed", "anxious"}, {"work", "productivity"}),
    "motivation": ({"motivated", "hopeful", "unmotivated"}, {"goals", "productivity"}),
    "overwhelm": ({"overwhelmed", "stressed", "anxious"}, {"stress", "tasks", "daily_life"}),
    "gratitude": ({"grateful", "positive"}, {"reflection", "relationships", "good_news"}),
    "uncertainty": ({"uncertain", "confused"}, {"decisions", "future"}),
    "anger": ({"angry", "frustrated"}, {"conflict", "relationships"}),
    "sleep": ({"tired", "worried", "stressed"}, {"sleep", "routine"}),
    "self_reflection": ({"reflective", "confused", "sad"}, {"self_reflection", "emotions"}),
    "casual": ({"neutral", "positive"}, {"conversation", "daily_life"}),
    "negated_distress": ({"neutral", "positive"}, {"clarification", "daily_life"}),
    "high_risk": ({"distressed", "crisis"}, {"safety", "immediate_support"}),
}

for split in ("train", "validation", "test"):
    df = pd.read_csv(DATA / f"{split}.csv")
    invalid = []
    for _, row in df.iterrows():
        moods, topics = EXPECTED[row["intent"]]
        if row["mood"] not in moods or row["topic"] not in topics:
            invalid.append((row["message"], row["intent"], row["mood"], row["topic"]))

    print(f"{split}: rows={len(df)} unique_messages={df.message.nunique()} "
          f"unique_responses={df.response.nunique()} invalid_metadata={len(invalid)}")
    if invalid:
        print(invalid[:5])

print("metadata audit complete")
