from __future__ import annotations

from pathlib import Path

import re
import unicodedata

from typing import Any, Dict, List, Optional

import joblib

import numpy as np

from sklearn.metrics.pairwise import cosine_similarity

class TrainedResponseModel:

    """

    Select safe, context-relevant response examples from the trained

    MindCare response model.

    This component improves response selection only.

    It does NOT:

        - make authoritative risk decisions

        - override the deterministic safety layer

        - diagnose the user

        - generate crisis decisions

    The deterministic safety/risk layer remains authoritative.

    """

# Conservative response-routing thresholds. Safety decisions remain
# authoritative in BehaviorEngine; intent is primary metadata, while
# mood/topic are only weak reranking hints.
    MIN_SIMILARITY = 0.20

    # Explicit phrase hints may retrieve from a wider semantic neighborhood.
    PHRASE_HINT_SIMILARITY = 0.18

    SHORT_MESSAGE_SIMILARITY = 0.40

    INTENT_WEIGHT = 0.18

    MOOD_WEIGHT = 0.03

    TOPIC_WEIGHT = 0.03

    def __init__(

        self,

        model_dir: Optional[str] = None,

        top_k: int = 3,

    ):

        root = (

            Path(model_dir)

            if model_dir

            else (

                Path(__file__).resolve().parent.parent

                / "models"

                / "response_model"

        )

        )

        self.root = root

        self.top_k = max(1, int(top_k))

        self.classifier = None

        self.index = None

        self._load()

# ============================================================
# MODEL LOADING
# ============================================================
    def _load(self) -> None:

        """Load the trained classifier and response retrieval index."""

        classifier_path = (

            self.root / "response_classifier.joblib"

        )

        index_path = (

            self.root / "response_index.joblib"

        )

        if not classifier_path.exists():

            raise FileNotFoundError(

                f"Response classifier not found: {classifier_path}"

            )

        if not index_path.exists():

            raise FileNotFoundError(

                f"Response index not found: {index_path}"

            )

# Load both artifacts only after both paths have been validated.
        self.classifier = joblib.load(classifier_path)

        self.index = joblib.load(index_path)

        if not isinstance(self.classifier, dict):

            raise TypeError("Invalid response classifier bundle")

        if not isinstance(self.index, dict):

            raise TypeError("Invalid response retrieval index")

        required_classifier_keys = {"features", "models", "targets"}

        missing_classifier = required_classifier_keys.difference(

            self.classifier.keys()

        )

        if missing_classifier:

            raise ValueError(

                "Response classifier missing keys: "

                + ", ".join(sorted(missing_classifier))

            )

        required_index_keys = {"vectorizer", "matrix", "records"}

        missing_index = required_index_keys.difference(self.index.keys())

        if missing_index:

            raise ValueError(

                "Response index missing keys: "

                + ", ".join(sorted(missing_index))

            )

# ============================================================
# RAW CLASSIFIER PREDICTION
# ============================================================
    def _predict_classifier_metadata(

        self,

        text: str,

    ) -> Dict[str, Any]:

        """

        Return raw classifier predictions.

        This method intentionally does not perform semantic

        reconciliation. It is used internally by retrieval so

        metadata prediction cannot recursively call retrieval.

        """

        text = str(text or "").strip()

        if not text:

            return {}

        X = self.classifier[

            "features"

        ].transform([text])

        result: Dict[str, Any] = {}

        for target in self.classifier["targets"]:

            model = self.classifier[

                "models"

            ][target]

            prediction = model.predict(X)[0]

            result[target] = str(

                prediction

            )

            if hasattr(

                model,

                "predict_proba",

            ):

                probabilities = (

                    model.predict_proba(X)[0]

                )

                result[

                    f"{target}_confidence"

                ] = round(

                    float(

                        np.max(probabilities)

                    ),

                    4,

                )

        return result

# ============================================================
# SEMANTIC METADATA CONSENSUS
# ============================================================
    def _semantic_metadata_consensus(

        self,

        text: str,

        top_n: int = 5,

    ) -> Dict[str, Any]:

        """

        Infer response-routing metadata from the strongest

        semantic neighbors in the trained response index.

        This is NOT a safety mechanism.

        Risk decisions remain exclusively owned by the

        deterministic safety/risk layer.

        """

        if not self.index:

            return {}

        vectorizer = self.index.get(

            "vectorizer"

        )

        matrix = self.index.get(

            "matrix"

        )

        records = self.index.get(

            "records"

        )

        if (

            vectorizer is None

            or matrix is None

            or not records

        ):

            return {}

        query = vectorizer.transform(

            [text]

        )

        similarities = cosine_similarity(

            query,

            matrix,

        )[0]

        neighbors = []

        for idx in np.argsort(

            -similarities

        ):

            record = records[int(idx)]

# Never use high-risk examples
# for normal response metadata.
            if (

                str(

                    record.get(

                        "risk_level",

                        "",

                    )

                )

                .strip()

                .lower()

                == "high"

            ):

                continue

            similarity = float(

                similarities[idx]

            )

            neighbors.append(

                (

                    similarity,

                    record,

                )

            )

            if len(neighbors) >= top_n:

                break

        if not neighbors:

            return {}

        result: Dict[str, Any] = {}

        for field in (

            "intent",

            "mood",

            "topic",

        ):

            votes: Dict[

                str,

                float,

            ] = {}

            for rank, (

                similarity,

                record,

            ) in enumerate(neighbors):

                value = str(

                    record.get(

                        field,

                        "",

                    )

                ).strip().lower()

                if not value:

                    continue

# Give stronger weight to higher-ranked
# semantic neighbors.
                rank_weight = (

                    1.0 / (rank + 1)

                )

                similarity_weight = max(

                    similarity,

                    0.05,

                )

                weight = (

                    rank_weight

                    * similarity_weight

                )

                votes[value] = (

                    votes.get(

                        value,

                        0.0,

                    )

                    + weight

                )

            if not votes:

                continue

            ordered = sorted(

                votes.items(),

                key=lambda item: item[1],

                reverse=True,

            )

            best_value = ordered[0][0]

            total_weight = sum(

                votes.values()

            )

            confidence = (

                ordered[0][1]

                / total_weight

                if total_weight

                else 0.0

            )

            result[field] = best_value

            result[

                f"{field}_semantic_confidence"

            ] = round(

                confidence,

                4,

            )

        return result

# ============================================================
# METADATA PREDICTION
# ============================================================
    def predict_metadata(

        self,

        message: str,

    ) -> Dict[str, Any]:

        """Predict routing metadata without a full 50K-vector scan."""

        text = str(message or "").strip()

        if not text:

            return {}

        result = self._predict_classifier_metadata(text)

        if not result:

            return {}

        hints = self._phrase_hints(text)

        for field in ("intent", "mood", "topic"):

            classifier_value = result.get(field)

            classifier_conf = float(

                result.get(f"{field}_confidence", 0.0) or 0.0

            )

            result[f"{field}_classifier_prediction"] = classifier_value

            result[f"{field}_classifier_confidence"] = round(classifier_conf, 4)

            result[f"{field}_semantic_prediction"] = None

            result[f"{field}_semantic_confidence"] = 0.0

            if field in hints:

                result[field] = hints[field]

                result[f"{field}_source"] = "phrase_hint"

            else:

                result[f"{field}_source"] = "classifier"

        return result

    def _phrase_hints(

        text: str,

    ) -> Dict[str, str]:

        """

        Correct common response-routing phrases that a generic

        classifier may misinterpret.

        Phrase hints affect response retrieval only.

        They NEVER modify authoritative risk decisions.

        """

        t = " ".join(

            str(text or "")

            .lower()

            .split()

        )

# --------------------------------------------------------
# LONELINESS
# --------------------------------------------------------
        if any(

            phrase in t

            for phrase in (

                "nobody cares",

                "no one cares",

                "left me alone",

                "feel alone",

                "feeling alone",

                "nobody is there",

                "no one is there",

                "nobody understands",

                "no one understands",

                "feel isolated",

                "so isolated",

                "completely alone",
                "feel lonely",
                "feeling lonely",
                "i feel lonely",
                "i'm lonely",
                "i am lonely",
                "lonely",

            )

        ):

            return {

                "intent": "loneliness",

                "mood": "sad",

                "topic": "social",

            }

# --------------------------------------------------------
# SLEEP
# --------------------------------------------------------
        if any(

            phrase in t

            for phrase in (

                "can't sleep",

                "cannot sleep",

                "couldn't sleep",

                "could not sleep",

                "not sleeping",

                "trouble sleeping",

                "having trouble sleeping",

                "sleep is difficult",

                "sleeping badly",

            )

        ):

            return {

                "intent": "sleep",

                "mood": "tired",

                "topic": "sleep",

            }

# --------------------------------------------------------
# GENERAL STRESS / OVERWHELM
# --------------------------------------------------------
        if any(

            phrase in t

            for phrase in (

                "getting stressed",

                "feeling stressed",

                "feel stressed",

                "so stressed",

                "really stressed",

                "too stressed",

                "very stressed",

                "feeling overwhelmed",

                "feel overwhelmed",

                "too much to handle",

                "too much on my mind",

            )

        ):

            return {

                "intent": "overwhelm",

                "mood": "stressed",

                "topic": "workload",

            }

# --------------------------------------------------------
# SADNESS / FEELING TERRIBLE
# --------------------------------------------------------
        if any(

            phrase in t

            for phrase in (

                "i feel terrible",

                "i feel awful",

                "i feel horrible",

                "feeling terrible",

                "feeling awful",

                "feeling horrible",

                "i feel really bad",

                "i feel very bad",

            )

        ):

            return {

                "intent": "sadness",

                "mood": "sad",

                "topic": "emotions",

            }

# --------------------------------------------------------
# UNCERTAINTY / MENTAL STUCKNESS
# --------------------------------------------------------
        if any(

            phrase in t

            for phrase in (

                "my mind feels stuck",

                "my mind is stuck",

                "i feel stuck",

                "i am stuck",

                "don't know what i'm feeling",

                "dont know what im feeling",

                "do not know what i'm feeling",

                "do not know what i am feeling",

                "not sure what i'm feeling",

                "not sure what i am feeling",

            )

        ):

            return {

                "intent": "self_reflection",

                "mood": "confused",

                "topic": "self_reflection",

            }

# --------------------------------------------------------
# GENERAL WELLBEING / NOT FEELING WELL
# --------------------------------------------------------
        if any(

            phrase in t

            for phrase in (

                "not feeling well",

                "don't feel well",

                "dont feel well",

                "do not feel well",

                "not doing well",

                "i am not well",

                "i'm not well",

                "im not well",

            )

        ):

            return {

                "intent": "sadness",

                "mood": "low",

                "topic": "wellbeing",

            }

# --------------------------------------------------------
# SELF REFLECTION / UNCERTAINTY
# --------------------------------------------------------
        if any(

            phrase in t

            for phrase in (

                "don't know what i'm feeling",

                "dont know what i'm feeling",

                "don't know what i am feeling",

                "not sure what i'm feeling",

                "can't tell what i'm feeling",

                "cant tell what i'm feeling",

                "confused about how i feel",

                "not sure how i feel",

            )

        ):

            return {

                "intent": "self_reflection",

                "mood": "reflective",

                "topic": "self_reflection",

            }

# --------------------------------------------------------
# EXAM STRESS
# --------------------------------------------------------
        if any(

            phrase in t

            for phrase in (

                "stressed about my exam",

                "stressed about exams",
                "stressed about my exams",
                "i am stressed about my exams",
                "i'm stressed about my exams",

                "stress about my exam",

                "exam stress",

                "exams are stressing me",

            )

        ):

            return {

                "intent": "exam_stress",

                "mood": "anxious",

                "topic": "college",

            }

# --------------------------------------------------------
# RELATIONSHIP ANGER
# --------------------------------------------------------
        if any(

            phrase in t

            for phrase in (

                "angry at my friend",

                "angry with my friend",

                "mad at my friend",

                "mad with my friend",

                "friend made me angry",

                "angry because of my friend",

            )

        ):

            return {

                "intent": "relationship",

                "mood": "angry",

                "topic": "relationships",

            }

# --------------------------------------------------------
# POSITIVE
# --------------------------------------------------------
        if any(

            phrase in t

            for phrase in (

                "happy today",

                "feeling happy",

                "i am happy",

                "i'm happy",

                "good day",

                "feeling great",

                "i feel great",

                "excited today",

            )

        ):

            return {

                "intent": "positive",

                "mood": "positive",

                "topic": "personal",

            }

        return {}

# ============================================================
# RESPONSE RETRIEVAL
# ============================================================
    @staticmethod

    def _short_message_route(text: str) -> Optional[str]:

        """Route tiny conversational inputs without semantic retrieval."""

        normalized = " ".join(str(text or "").strip().lower().split())

        if normalized in {

            "hi", "hii", "hiii", "hello", "helo", "hey", "heyy",

            "heyyy", "hiya", "yo", "good morning", "good afternoon",

            "good evening",

        }:

            return "greeting"

        if normalized in {

            "hmm", "hmmm", "hm", "umm", "um", "uh", "uhh", "okay",

            "ok", "k", "right", "yeah", "yep", "nah", "nope",

        }:

            return "follow_up"

        if normalized in {

            "idk", "i dk", "idontknow", "i dont know", "i don't know",

            "dont know", "don't know", "not sure", "unsure", "no idea",

        }:

            return "uncertainty"

        return None

    @staticmethod
    def _clean_response_text(response: str) -> str:
        """Clean retrieved response text before it reaches the response engine."""
        text = unicodedata.normalize("NFKC", str(response or ""))
        text = re.sub(r"[\u200b-\u200f\u2060\ufeff]", "", text)
        text = " ".join(text.split()).strip()
        repairs = (
            (r"\borsomething\b", "or something"), (r"\bisto\b", "is to"),
            (r"\bimmediatedanger\b", "immediate danger"),
            (r"\bpracticaloption\b", "practical option"),
            (r"\bworryingyou\b", "worrying you"), (r"\bwhatkind\b", "what kind"),
            (r"\batime\b", "a time"), (r"\bonestep\b", "one step"),
            (r"\bonesmall\b", "one small"), (r"\bmightreach\b", "might reach"),
            (r"\bmightfind\b", "might find"), (r"\btogive\b", "to give"),
            (r"\btostart\b", "to start"), (r"\btoseparate\b", "to separate"),
            (r"\btounderstanding\b", "to understanding"),
            (r"\bonunderstanding\b", "on understanding"), (r"\bonfocus\b", "on focus"),
            (r"\btheimmediate\b", "the immediate"), (r"\bitmay\b", "it may"),
            (r"\bwrite downwhat\b", "write down what"), (r"\bcouldbe\b", "could be"),
            (r"\bstepcould\b", "step could"), (r"\bgiveyourself\b", "give yourself"),
            (r"\bandthink\b", "and think"), (r"\btakethe\b", "take the"),
            (r"\bthesituation\b", "the situation"),
        )
        for pattern, replacement in repairs:
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        for pattern, replacement in (
            (r"\bsituation\s+situation\b", "situation"),
            (r"\bconsider\s+take\b", "consider taking"),
            (r"\bconsider\s+write\b", "consider writing"),
            (r"\bconsider\s+separate\b", "consider separating"),
            (r"\bconsider\s+give\b", "consider giving"),
            (r"\bconsider\s+focus\b", "consider focusing"),
        ):
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        return re.sub(r"\s+([,.!?;:])", r"\1", " ".join(text.split()).strip())

    def find_examples(

        self,

        message: str,

        risk_level: Optional[str] = None,

        mood: Optional[str] = None,

        intent: Optional[str] = None,

        topic: Optional[str] = None,

        top_k: Optional[int] = None,

    ) -> List[Dict[str, Any]]:

        """Retrieve safe, semantically relevant response examples.

        Similarity is the primary relevance signal. Intent is a secondary

        routing signal. Mood/topic are weak tie-breakers only. Metadata can

        never compensate for negligible semantic similarity.

        """

        text = str(message or "").strip()

        if not text:

            return []

        if str(risk_level or "").strip().lower() == "high":

            return []

        if self._short_message_route(text) is not None:

            return []

        metadata = self._predict_classifier_metadata(text)

        hints = self._phrase_hints(text)

        requested = {}

        for field, explicit in (

            ("intent", intent),

            ("mood", mood),

            ("topic", topic),

        ):

            value = hints.get(field) or explicit or metadata.get(field, "")

            requested[field] = str(value or "").strip().lower()

        vectorizer = self.index.get("vectorizer")

        matrix = self.index.get("matrix")

        records = self.index.get("records")

        if vectorizer is None or matrix is None or not records:

            return []

        query = vectorizer.transform([text])

        similarities = cosine_similarity(query, matrix)[0]

        candidates: List[Dict[str, Any]] = []

        hint_fields = set(hints)

        short_input = len(text.split()) <= 2

        minimum_similarity = (

            self.SHORT_MESSAGE_SIMILARITY

            if short_input

            else self.MIN_SIMILARITY

        )

        for idx in np.argsort(-similarities):

            record = records[int(idx)]

            if str(record.get("risk_level", "")).strip().lower() == "high":

                continue

            similarity = float(similarities[int(idx)])

            if similarity < minimum_similarity:

                break

            matches: List[str] = []

            score = similarity

            actual_intent = str(record.get("intent", "")).strip().lower()

            actual_mood = str(record.get("mood", "")).strip().lower()

            actual_topic = str(record.get("topic", "")).strip().lower()

            expected_intent = requested.get("intent", "")

            expected_mood = requested.get("mood", "")

            expected_topic = requested.get("topic", "")

            if expected_intent and actual_intent == expected_intent:

                matches.append("intent")

                score += self.INTENT_WEIGHT

                if "intent" in hint_fields:

                    score += 0.08

            if expected_mood and actual_mood == expected_mood:

                matches.append("mood")

                score += self.MOOD_WEIGHT

                if "mood" in hint_fields:

                    score += 0.02

            if expected_topic and actual_topic == expected_topic:

                matches.append("topic")

                score += self.TOPIC_WEIGHT

                if "topic" in hint_fields:

                    score += 0.02

            item = dict(record)

            item.update({

                "similarity": round(similarity, 4),

                "retrieval_score": round(score, 4),

                "metadata_matches": matches,

                "metadata_match_count": len(matches),

                "phrase_hint": bool(hint_fields),

                "predicted_metadata": metadata,

                "response_routing_metadata": requested,

                "semantic_metadata": {},

            })

            candidates.append(item)

        # Retrieval score is semantic similarity plus small metadata boosts.
        # This lets an explicit intent/phrase hint refine ranking without
        # allowing a weak semantic match to dominate.
        candidates.sort(
            key=lambda item: (
                float(item.get("retrieval_score", 0.0)),
                int("intent" in item.get("metadata_matches", [])),
                int(item.get("metadata_match_count", 0)),
                float(item.get("similarity", 0.0)),
            ),
            reverse=True,
        )

        limit = max(1, int(top_k or self.top_k))

        results: List[Dict[str, Any]] = []

        seen = set()

        for item in candidates:

            response_text = self._clean_response_text(item.get("response", ""))

            if not response_text:

                continue

            key = response_text.casefold()

            if key in seen:

                continue

            seen.add(key)

            results.append(item)

            if len(results) >= limit:

                break

        return results

    def build_context(

        self,

        message: str,

        risk_level: Optional[str] = None,

        **kwargs: Any,

    ) -> str:

        """

        Build context for an optional downstream response generator.

        Examples are guidance only. The downstream generator should

        create a fresh response rather than copying examples verbatim.

        """

        examples = self.find_examples(

            message,

            risk_level=risk_level,

            **kwargs,

        )

        if not examples:

            return ""

        lines = [

            (

                "Relevant MindCare response examples "

                "from the trained response model:"

            ),

            (

                "Use them as style and relevance guidance; "

                "write a fresh response and do not copy them verbatim."

            ),

            "",

        ]

        for i, item in enumerate(

            examples,

            1,

        ):

            lines.extend(

                [

                    f"Example {i}:",

                    f"User: {item['message']}",

                    (

                        "Response style: "

                        f"{item['response']}"

                    ),

                    (

                        "Intent: "

                        f"{item['intent']}"

                    ),

                    (

                        "Mood: "

                        f"{item['mood']}"

                    ),

                    (

                        "Topic: "

                        f"{item['topic']}"

                    ),

                    (

                        "Retrieval score: "

                        f"{item['retrieval_score']}"

                    ),

                    "",

                ]

            )

        return "\n".join(

            lines

        )

