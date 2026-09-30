from pathlib import Path
import shutil
import re
import pandas as pd


ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data" / "mindcare_responses"

FILES = [
    DATA_DIR / "train.csv",
    DATA_DIR / "validation.csv",
    DATA_DIR / "test.csv",
]


REPLACEMENTS = {
    # Common generated-word concatenations
    "Examstress": "Exam stress",
    "Careeruncertainty": "Career uncertainty",
    "That'sokay": "That's okay",
    "Wecan": "We can",
    "youcan": "you can",
    "Youcan": "You can",
    "takeyour": "take your",
    "figureeverything": "figure everything",
    "talkabout": "talk about",
    "rightnow": "right now",
    "atonce": "at once",
    "feelslike": "feels like",
    "hasbeen": "has been",
    "coulduse": "could use",
    "getto": "get to",
    "safeplace": "safe place",
    "anotherperson": "another person",
    "localor": "local or",
    "crisisor": "crisis or",
    "worriedabout": "worried about",
    "stressedabout": "stressed about",
    "myfriend": "my friend",
    "myfriends": "my friends",
    "somethingelse": "something else",
    "somethinggood": "something good",
    "partof": "part of",
    "kindof": "kind of",
    "sortof": "sort of",
    "helpedme": "helped me",
    "whatshappening": "what's happening",
    "whatishappening": "what is happening",

    # Known generated phrase artifacts
    "at pretty the moment": "right now",
    "these pretty days": "these days",
    "at just the moment": "right now",
}


def clean_text(value):
    if pd.isna(value):
        return value

    text = str(value).strip()

    # Exact known phrase replacements
    for old, new in REPLACEMENTS.items():
        text = text.replace(old, new)

    # Normalize whitespace
    text = re.sub(r"\s+", " ", text).strip()

    # Fix punctuation artifacts such as "something?."
    text = re.sub(r"\?\.", "?", text)

    # Fix repeated punctuation
    text = re.sub(r"\.{2,}", ".", text)
    text = re.sub(r"!{2,}", "!", text)

    # Remove spaces before punctuation
    text = re.sub(r"\s+([,.!?])", r"\1", text)

    return text


def main():
    print("=" * 70)
    print("MindCare Response Dataset Quality Cleanup")
    print("=" * 70)

    total_changes = 0

    for path in FILES:
        if not path.exists():
            print(f"\nERROR: Missing file: {path}")
            continue

        backup = path.with_suffix(path.suffix + ".before_quality_cleanup")

        if not backup.exists():
            shutil.copy2(path, backup)
            print(f"\nBackup created: {backup.name}")

        df = pd.read_csv(path)

        required = {"message", "response"}
        missing = required - set(df.columns)

        if missing:
            print(f"ERROR: {path.name} missing columns: {sorted(missing)}")
            continue

        before = df["response"].fillna("").astype(str).tolist()

        df["message"] = df["message"].apply(clean_text)
        df["response"] = df["response"].apply(clean_text)

        after = df["response"].fillna("").astype(str).tolist()

        changed = sum(a != b for a, b in zip(before, after))
        total_changes += changed

        df.to_csv(path, index=False)

        print(f"\n{path.name}")
        print(f"Rows: {len(df)}")
        print(f"Response rows changed: {changed}")

    print("\n" + "=" * 70)
    print(f"TOTAL RESPONSE CHANGES: {total_changes}")
    print("=" * 70)

    # Post-cleanup scan
    print("\nPost-cleanup validation:")

    suspicious_patterns = [
        r"\?\.",
        r"That'sokay",
        r"Wecan",
        r"youcan",
        r"Examstress",
        r"Careeruncertainty",
        r"at pretty the moment",
        r"these pretty days",
        r"takeyour",
        r"figureeverything",
        r"talkabout",
        r"rightnow",
        r"atonce",
    ]

    combined = re.compile(
        "|".join(suspicious_patterns),
        flags=re.IGNORECASE,
    )

    for path in FILES:
        if not path.exists():
            continue

        df = pd.read_csv(path)

        mask = df["response"].fillna("").astype(str).apply(
            lambda x: bool(combined.search(x))
        )

        print(f"{path.name}: suspicious responses = {int(mask.sum())}")

    print("\nCleanup complete.")
    print("Backups have been retained.")
    print("Do NOT retrain until the validation results look correct.")


if __name__ == "__main__":
    main()