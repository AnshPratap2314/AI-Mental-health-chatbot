LABELS = {
    "crisis": 0,
    "self_harm": 1,
    "negated": 2,
    "contextual": 3,
    "neutral": 4,
    "positive": 5,
}


ID_TO_LABEL = {
    value: key
    for key, value in LABELS.items()
}


HIGH_RISK_LABELS = {
    "crisis",
    "self_harm",
}


def encode_label(label: str) -> int:
    if label not in LABELS:
        raise ValueError(
            f"Unknown label: {label}"
        )

    return LABELS[label]


def decode_label(label_id: int) -> str:
    if label_id not in ID_TO_LABEL:
        raise ValueError(
            f"Unknown label ID: {label_id}"
        )

    return ID_TO_LABEL[label_id]


def is_high_risk(label: str) -> bool:
    return label in HIGH_RISK_LABELS