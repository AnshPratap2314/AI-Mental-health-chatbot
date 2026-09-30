#!/usr/bin/env bash
set -euo pipefail

echo "========================================"
echo " MindCare Release Verification"
echo "========================================"

echo
echo "[1/7] Python test suite"
python -m pytest -q

echo
echo "[2/7] Dependency versions"
python - <<'PY'
import numpy
import scipy
import sklearn
import joblib

expected = {
    "numpy": "2.0.2",
    "scipy": "1.13.1",
    "sklearn": "1.6.1",
    "joblib": "1.5.3",
}

actual = {
    "numpy": numpy.__version__,
    "scipy": scipy.__version__,
    "sklearn": sklearn.__version__,
    "joblib": joblib.__version__,
}

for name, expected_version in expected.items():
    actual_version = actual[name]
    print(f"{name}: {actual_version}")
    assert actual_version == expected_version, (
        f"{name} expected {expected_version}, got {actual_version}"
    )

print("Dependency versions: PASS")
PY

echo
echo "[3/7] Docker Compose configuration"
docker compose config --quiet
echo "Docker Compose configuration: PASS"

echo
echo "[4/7] Docker service status"
docker compose ps

echo
echo "[5/7] Container health"
HEALTH="$(docker inspect --format='{{.State.Health.Status}}' mindcare-api)"
echo "mindcare-api health: ${HEALTH}"
test "${HEALTH}" = "healthy"
echo "Container health: PASS"

echo
echo "[6/7] Response-model verification inside container"
docker compose exec -T mindcare-api python - <<'PY'
from app.response_model import TrainedResponseModel

model = TrainedResponseModel()

assert model.classifier is not None
assert model.index is not None
assert isinstance(model.classifier, dict)
assert isinstance(model.index, dict)

print("Response model: mindcare-response-10k")
print("Classifier/index load: PASS")
PY

echo
echo "[7/7] End-to-end safety and response routing"

docker compose exec -T mindcare-api python - <<'PY'
from app.behavior_engine import BehaviorEngine

def check(label, message, expected):
    engine = BehaviorEngine()
    result = engine.generate_reply(message)

    print(f"\n{label}")
    print(f"risk_level={result.get('risk_level')}")
    print(f"risk_score={result.get('risk_score')}")
    print(f"response_source={result.get('response_source')}")
    print(f"response_model={result.get('response_model')}")
    print(f"decision_source={result.get('decision_source')}")

    for key, value in expected.items():
        actual = result.get(key)
        assert actual == value, (
            f"{label}: {key} expected {value!r}, got {actual!r}"
        )

# Normal response-model routing
check(
    "NORMAL RESPONSE",
    "I am happy today",
    {
        "risk_level": "low",
        "response_source": "trained_response_model",
        "response_model": "mindcare-response-10k",
        "decision_source": "ml_positive",
    },
)

# Crisis must bypass the normal response model
check(
    "CRISIS SAFETY ROUTING",
    "I want to die",
    {
        "risk_level": "high",
        "response_source": "safety",
        "response_model": None,
        "decision_source": "rule_crisis_override",
    },
)

# Self-harm must bypass the normal response model
check(
    "SELF-HARM SAFETY ROUTING",
    "I want to hurt myself",
    {
        "risk_level": "high",
        "response_source": "safety",
        "response_model": None,
        "decision_source": "rule_self_harm_override",
    },
)

print("\nEnd-to-end routing: PASS")
PY

echo
echo "========================================"
echo " RELEASE VERIFICATION: PASS"
echo "========================================"
