from __future__ import annotations

from pathlib import Path

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

        """Predict response-routing metadata using classifier + semantic evidence.

        Risk is informational here. The deterministic safety engine remains

        authoritative and is never replaced by this model.

        """

        text = str(message or "").strip()

        if not text:

            return {}

        result = self._predict_classifier_metadata(text)

        if not result:

            return {}

        semantic = self._semantic_metadata_consensus(text, top_n=5)

        hints = self._phrase_hints(text)

        threshold = 0.70

        for field in ("intent", "mood", "topic"):

            classifier_value = result.get(field)

            classifier_conf = float(

                result.get(f"{field}_confidence", 0.0) or 0.0

            )

            semantic_value = semantic.get(field)

            semantic_conf = float(

                semantic.get(f"{field}_semantic_confidence", 0.0) or 0.0

            )

            result[f"{field}_classifier_prediction"] = classifier_value

            result[f"{field}_classifier_confidence"] = round(

                classifier_conf, 4

            )

            result[f"{field}_semantic_prediction"] = semantic_value

            result[f"{field}_semantic_confidence"] = round(

                semantic_conf, 4

            )

            if field in hints:

                result[field] = hints[field]

                result[f"{field}_source"] = "phrase_hint"

            elif semantic_value and classifier_conf < threshold:

                result[field] = semantic_value

                result[f"{field}_source"] = "semantic_consensus"

            else:

                result[f"{field}_source"] = "classifier"

        return result

# PHRASE HINTS
# ============================================================
    @staticmethod

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

            )

        ):

            return {

                "intent": "loneliness",

                "mood": "sad",

                "topic": "social",

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
    def find_examples(

        self,

        message: str,

        risk_level: Optional[str] = None,

        mood: Optional[str] = None,

        intent: Optional[str] = None,

        topic: Optional[str] = None,

        top_k: Optional[int] = None,

    ) -> List[Dict[str, Any]]:

        """Retrieve safe, context-relevant response examples.

        Ranking combines TF-IDF similarity, metadata agreement, semantic

        consensus and explicit phrase evidence. This is response routing only;

        it never decides safety risk.

        """

        text = str(message or "").strip()

        if not text:

            return []

        if str(risk_level or "").strip().lower() == "high":

            return []

        metadata = self._predict_classifier_metadata(text)

        hints = self._phrase_hints(text)

        semantic = self._semantic_metadata_consensus(text, top_n=5)

        requested = {}

        for field, explicit in (

            ("intent", intent),

            ("mood", mood),

            ("topic", topic),

        ):

# Explicit phrase evidence is strongest for response routing.
            value = hints.get(field) or explicit

            if not value:

                classifier_conf = float(

                    metadata.get(f"{field}_confidence", 0.0) or 0.0

                )

                semantic_value = semantic.get(field)

                semantic_conf = float(

                    semantic.get(f"{field}_semantic_confidence", 0.0) or 0.0

                )

                if semantic_value and (

                    classifier_conf < 0.70 or semantic_conf >= 0.66

                ):

                    value = semantic_value

                else:

                    value = metadata.get(field, "")

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

        for idx in np.argsort(-similarities):

            record = records[int(idx)]

            if str(record.get("risk_level", "")).strip().lower() == "high":

                continue

            similarity = float(similarities[int(idx)])

            matches: List[str] = []

            score = similarity

            for field, weight in (("intent", 0.12), ("mood", 0.08), ("topic", 0.08)):

                expected = requested.get(field, "")

                actual = str(record.get(field, "")).strip().lower()

                if expected and actual == expected:

                    matches.append(field)

                    score += weight

                    if field in hint_fields:

                        score += 0.12

            item = dict(record)

            item.update({

                "similarity": round(similarity, 4),

                "retrieval_score": round(score, 4),

                "metadata_matches": matches,

                "metadata_match_count": len(matches),

                "phrase_hint": bool(hint_fields),

                "predicted_metadata": metadata,

                "response_routing_metadata": requested,

                "semantic_metadata": semantic,

            })

            candidates.append(item)

# Route by contextual relevance first. Raw TF-IDF similarity alone
# can rank a lexically similar but emotionally wrong example above a
# slightly less-overlapping example that agrees with the explicit
# intent/mood/topic routing.
#
# Example: "I am angry at my friend" can retrieve an \`\`anger\`\`
# example with higher lexical similarity, while the phrase hint says
# relationship + angry + relationships. The latter must win.
        candidates.sort(

            key=lambda item: (

                float(item.get("retrieval_score", 0.0)),

                int(item.get("metadata_match_count", 0)),

                float(item.get("similarity", 0.0)),

            ),

            reverse=True,

        )

        limit = max(1, int(top_k or self.top_k))

        results: List[Dict[str, Any]] = []

        seen = set()

        for item in candidates:

            response_text = str(item.get("response", "")).strip()

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

# CONTEXT BUILDER
# ============================================================
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