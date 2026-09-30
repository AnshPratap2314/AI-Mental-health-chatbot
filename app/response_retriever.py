from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class ResponseRetriever:
    """
    Retrieves relevant response examples from the MindCare response dataset.

    This component improves response generation by finding examples
    that are semantically similar to the current user message.

    It does NOT perform:
        - risk detection
        - crisis classification
        - diagnosis
        - safety decisions

    The deterministic safety/risk layer remains authoritative.
    """

    DEFAULT_DATASET_PATH = (
        Path(__file__).resolve().parent.parent
        / "data"
        / "mindcare_responses"
        / "train.csv"
    )

    REQUIRED_COLUMNS = {
        "message",
        "response",
        "intent",
        "mood",
        "topic",
        "risk_level",
    }

    def __init__(
        self,
        dataset_path: Optional[str] = None,
        top_k: int = 3,
        min_similarity: float = 0.20,
    ):
        self.dataset_path = Path(
            dataset_path or self.DEFAULT_DATASET_PATH
        )

        self.top_k = max(1, int(top_k))
        self.min_similarity = max(0.0, float(min_similarity))

        self.dataset: Optional[pd.DataFrame] = None
        self.vectorizer: Optional[TfidfVectorizer] = None
        self.message_vectors = None

        self._loaded = False

    # =========================================================
    # DATASET LOADING
    # =========================================================

    def _load(self) -> None:
        """
        Load and vectorize the training dataset lazily.
        """

        if self._loaded:
            return

        if not self.dataset_path.exists():
            raise FileNotFoundError(
                f"Response dataset not found: {self.dataset_path}"
            )

        df = pd.read_csv(self.dataset_path)

        missing = self.REQUIRED_COLUMNS - set(df.columns)

        if missing:
            raise ValueError(
                "Response dataset is missing required columns: "
                + ", ".join(sorted(missing))
            )

        df = df.copy()

        # -----------------------------------------------------
        # Clean message and response fields
        # -----------------------------------------------------

        df["message"] = (
            df["message"]
            .fillna("")
            .astype(str)
            .str.strip()
        )

        df["response"] = (
            df["response"]
            .fillna("")
            .astype(str)
            .str.strip()
        )

        # Remove empty examples.
        df = df[
            (df["message"] != "")
            & (df["response"] != "")
        ].reset_index(drop=True)

        # -----------------------------------------------------
        # Normalize metadata
        # -----------------------------------------------------

        for column in [
            "intent",
            "mood",
            "topic",
            "risk_level",
        ]:
            df[column] = (
                df[column]
                .fillna("")
                .astype(str)
                .str.strip()
                .str.lower()
            )

        self.dataset = df

        # -----------------------------------------------------
        # TF-IDF
        # -----------------------------------------------------

        self.vectorizer = TfidfVectorizer(
            lowercase=True,
            strip_accents="unicode",
            ngram_range=(1, 2),
            min_df=1,
            max_df=0.98,
            sublinear_tf=True,
        )

        self.message_vectors = (
            self.vectorizer.fit_transform(
                self.dataset["message"]
            )
        )

        self._loaded = True

    # =========================================================
    # RESPONSE RETRIEVAL
    # =========================================================

    def find_examples(
        self,
        message: str,
        mood: Optional[str] = None,
        topic: Optional[str] = None,
        intent: Optional[str] = None,
        risk_level: Optional[str] = None,
        top_k: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Retrieve the most relevant response examples.

        Retrieval strategy:

            1. Load safe training examples.
            2. Calculate TF-IDF semantic similarity.
            3. Apply small metadata boosts for:
                   - mood
                   - topic
                   - intent
            4. Rank by final retrieval score.
            5. Remove duplicate responses.
            6. Return top-k examples.

        Mood/topic/intent are SOFT signals.

        They never act as hard filters because a semantically
        relevant example should not be discarded just because
        its metadata differs slightly.

        Safety:

            - High-risk requests return no examples.
            - High-risk dataset examples are excluded from normal
              response retrieval.
            - This component never decides whether a user is high risk.
        """

        self._load()

        # -----------------------------------------------------
        # Validate input
        # -----------------------------------------------------

        if not message or not str(message).strip():
            return []

        message = str(message).strip()

        # -----------------------------------------------------
        # Normalize requested metadata
        # -----------------------------------------------------

        normalized_mood = self._normalize(mood)
        normalized_topic = self._normalize(topic)
        normalized_intent = self._normalize(intent)
        normalized_risk = self._normalize(risk_level)

        # -----------------------------------------------------
        # SAFETY BOUNDARY
        # -----------------------------------------------------
        #
        # The deterministic safety/risk engine owns high-risk
        # decisions. The response retriever must not provide
        # normal response-generation examples for high-risk
        # conversations.
        #

        if normalized_risk == "high":
            return []

        if self.dataset is None or self.dataset.empty:
            return []

        # -----------------------------------------------------
        # EXCLUDE HIGH-RISK TRAINING EXAMPLES
        # -----------------------------------------------------

        candidates = self.dataset[
            self.dataset["risk_level"]
            .fillna("")
            .str.lower()
            != "high"
        ].copy()

        if candidates.empty:
            return []

        # -----------------------------------------------------
        # CREATE QUERY VECTOR
        # -----------------------------------------------------

        query_vector = self.vectorizer.transform(
            [message]
        )

        candidate_indices = candidates.index.tolist()

        candidate_vectors = self.message_vectors[
            candidate_indices
        ]

        # -----------------------------------------------------
        # CALCULATE TF-IDF COSINE SIMILARITY
        # -----------------------------------------------------

        similarities = cosine_similarity(
            query_vector,
            candidate_vectors,
        )[0]

        scored: List[Dict[str, Any]] = []

        # -----------------------------------------------------
        # SCORE EACH EXAMPLE
        # -----------------------------------------------------

        for index, similarity in zip(
            candidate_indices,
            similarities,
        ):
            similarity = float(similarity)

            # Ignore completely unrelated examples.
            if similarity < self.min_similarity:
                continue

            row = self.dataset.loc[index]

            row_mood = self._normalize(
                row["mood"]
            )

            row_topic = self._normalize(
                row["topic"]
            )

            row_intent = self._normalize(
                row["intent"]
            )

            # Start with semantic similarity.
            retrieval_score = similarity

            # -------------------------------------------------
            # SOFT METADATA BOOSTS
            # -------------------------------------------------
            #
            # These are intentionally small.
            #
            # Semantic similarity remains the dominant signal.
            #

            mood_match = (
                bool(normalized_mood)
                and row_mood == normalized_mood
            )

            topic_match = (
                bool(normalized_topic)
                and row_topic == normalized_topic
            )

            intent_match = (
                bool(normalized_intent)
                and row_intent == normalized_intent
            )

            if mood_match:
                retrieval_score += 0.08

            if topic_match:
                retrieval_score += 0.08

            if intent_match:
                retrieval_score += 0.10

            scored.append(
                {
                    "message": row["message"],
                    "response": row["response"],
                    "intent": row["intent"],
                    "mood": row["mood"],
                    "topic": row["topic"],
                    "risk_level": row["risk_level"],
                    "similarity": round(
                        similarity,
                        4,
                    ),
                    "retrieval_score": round(
                        retrieval_score,
                        4,
                    ),
                    "mood_match": mood_match,
                    "topic_match": topic_match,
                    "intent_match": intent_match,
                }
            )

        # -----------------------------------------------------
        # SORT
        # -----------------------------------------------------

        scored.sort(
            key=lambda item: item["retrieval_score"],
            reverse=True,
        )

        # -----------------------------------------------------
        # REMOVE DUPLICATE RESPONSES
        # -----------------------------------------------------

        results: List[Dict[str, Any]] = []

        seen_responses = set()

        limit = (
            max(1, int(top_k))
            if top_k is not None
            else self.top_k
        )

        for item in scored:
            response_key = (
                item["response"]
                .strip()
                .lower()
            )

            if response_key in seen_responses:
                continue

            seen_responses.add(response_key)

            results.append(item)

            if len(results) >= limit:
                break

        return results

    # =========================================================
    # BUILD LLM CONTEXT
    # =========================================================

    def build_context(
        self,
        message: str,
        mood: Optional[str] = None,
        topic: Optional[str] = None,
        intent: Optional[str] = None,
        risk_level: Optional[str] = None,
        top_k: Optional[int] = None,
    ) -> str:
        """
        Convert retrieved examples into compact context
        that can later be supplied to the LLM.

        The examples are guidance only.

        The LLM should:
            - understand the style
            - understand the conversational direction
            - use the relevant context
            - create a new response

        It should NOT copy examples verbatim.
        """

        examples = self.find_examples(
            message=message,
            mood=mood,
            topic=topic,
            intent=intent,
            risk_level=risk_level,
            top_k=top_k,
        )

        if not examples:
            return ""

        lines = [
            "Relevant MindCare response examples:",
            "",
        ]

        for number, example in enumerate(
            examples,
            start=1,
        ):
            lines.append(
                f"Example {number}:"
            )

            lines.append(
                f"User: {example['message']}"
            )

            lines.append(
                f"Response style: {example['response']}"
            )

            lines.append(
                f"Intent: {example['intent']}"
            )

            lines.append(
                f"Mood: {example['mood']}"
            )

            lines.append(
                f"Topic: {example['topic']}"
            )

            lines.append(
                f"Similarity: {example['similarity']}"
            )

            lines.append(
                f"Retrieval score: "
                f"{example['retrieval_score']}"
            )

            lines.append("")

        lines.append(
            "Use these examples only as guidance. "
            "Create a fresh response specific to the current user. "
            "Do not copy any example verbatim."
        )

        return "\n".join(lines)

    # =========================================================
    # DATASET STATISTICS
    # =========================================================

    def stats(self) -> Dict[str, Any]:
        """
        Return basic information about the loaded dataset.
        """

        self._load()

        if self.dataset is None:
            return {
                "loaded": False,
                "rows": 0,
            }

        return {
            "loaded": True,
            "rows": int(
                len(self.dataset)
            ),
            "path": str(
                self.dataset_path
            ),
            "intents": int(
                self.dataset["intent"]
                .nunique()
            ),
            "moods": int(
                self.dataset["mood"]
                .nunique()
            ),
            "topics": int(
                self.dataset["topic"]
                .nunique()
            ),
            "risk_levels": (
                self.dataset["risk_level"]
                .value_counts()
                .to_dict()
            ),
        }

    # =========================================================
    # HELPER METHODS
    # =========================================================

    @staticmethod
    def _normalize(
        value: Optional[str],
    ) -> str:
        """
        Normalize optional metadata values.
        """

        if value is None:
            return ""

        return (
            str(value)
            .strip()
            .lower()
        )