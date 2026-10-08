from collections import Counter
from app.response_engine import ResponseEngine


MESSAGE = "I feel lonely"
RUNS = 20

engine = ResponseEngine()

responses = []

analysis = {
    "risk_level": "low",
    "signals": {},
    "state": {},
}

for i in range(RUNS):
    result = engine.generate(
        MESSAGE,
        analysis,
        {},
    )

    reply = str(result).strip()

    responses.append(reply)

    print(f"{i + 1:02d}. {reply}")
    print(f"    SOURCE: {engine.last_source}")
    print(f"    MODEL : {engine.last_model}")
    print()

counts = Counter(responses)

unique_count = len(counts)
total_count = len(responses)

print("=" * 80)
print("DIVERSITY RESULTS")
print("=" * 80)

print("Total responses :", total_count)
print("Unique responses:", unique_count)

if total_count:
    print(
        "Unique ratio   : "
        f"{unique_count / total_count:.2%}"
    )

print()
print("DUPLICATES:")

for response, count in counts.most_common():
    if count > 1:
        print(f"{count}x -> {response}")