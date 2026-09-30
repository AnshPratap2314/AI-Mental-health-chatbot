from pathlib import Path
import json
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.response_model import TrainedResponseModel


DATA_DIR = ROOT / "data" / "mindcare_responses"
MODEL_DIR = ROOT / "models" / "response_model"
OUTPUT = ROOT / "evaluation" / "response_model_quality.json"


def evaluate_split(model, path):
    df = pd.read_csv(path)

    results = []

    for _, row in df.iterrows():
        message = str(row["message"])

        prediction = model.predict_metadata(message)
        examples = model.find_examples(message, top_k=3)

        results.append({
            "message": message,
            "expected_intent": row["intent"],
            "expected_mood": row["mood"],
            "expected_topic": row["topic"],
            "expected_risk": row["risk_level"],
            "predicted_intent": prediction.get("intent"),
            "predicted_mood": prediction.get("mood"),
            "predicted_topic": prediction.get("topic"),
            "predicted_risk": prediction.get("risk_level"),
            "retrieval_count": len(examples),
            "top_similarity": (
                examples[0].get("similarity", 0)
                if examples
                else 0
            ),
            "top_retrieval_score": (
                examples[0].get("retrieval_score", 0)
                if examples
                else 0
            ),
        })

    return pd.DataFrame(results)


def accuracy(df, expected, predicted):
    return float(
        (df[expected].astype(str) == df[predicted].astype(str)).mean()
    )


def main():
    model = TrainedResponseModel(
        model_dir=MODEL_DIR
    )

    reports = {}

    for split in ["validation", "test"]:
        path = DATA_DIR / f"{split}.csv"

        df = evaluate_split(model, path)

        reports[split] = {
            "rows": len(df),
            "intent_accuracy": accuracy(
                df, "expected_intent", "predicted_intent"
            ),
            "mood_accuracy": accuracy(
                df, "expected_mood", "predicted_mood"
            ),
            "topic_accuracy": accuracy(
                df, "expected_topic", "predicted_topic"
            ),
            "risk_accuracy": accuracy(
                df, "expected_risk", "predicted_risk"
            ),
            "retrieval": {
                "with_examples": int(
                    (df["retrieval_count"] > 0).sum()
                ),
                "mean_top_similarity": float(
                    df["top_similarity"].mean()
                ),
                "mean_top_retrieval_score": float(
                    df["top_retrieval_score"].mean()
                ),
            },
        }

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    OUTPUT.write_text(
        json.dumps(reports, indent=2),
        encoding="utf-8",
    )

    print("\nRESPONSE MODEL QUALITY")
    print("=" * 60)

    for split, report in reports.items():
        print(f"\n{split.upper()}")

        print(
            f"Intent accuracy : "
            f"{report['intent_accuracy']:.4f}"
        )

        print(
            f"Mood accuracy   : "
            f"{report['mood_accuracy']:.4f}"
        )

        print(
            f"Topic accuracy  : "
            f"{report['topic_accuracy']:.4f}"
        )

        print(
            f"Risk accuracy   : "
            f"{report['risk_accuracy']:.4f}"
        )

        print(
            f"Retrieved       : "
            f"{report['retrieval']['with_examples']}/"
            f"{report['rows']}"
        )

        print(
            f"Mean similarity : "
            f"{report['retrieval']['mean_top_similarity']:.4f}"
        )

        print(
            f"Mean score      : "
            f"{report['retrieval']['mean_top_retrieval_score']:.4f}"
        )

    print(f"\nSaved: {OUTPUT}")


if __name__ == "__main__":
    main()