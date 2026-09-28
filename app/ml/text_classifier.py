from pathlib import Path

import joblib

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline


MODEL_DIR = Path("models")
MODEL_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

MODEL_PATH = MODEL_DIR / "mindcare_tfidf.joblib"


class MindCareTextClassifier:

    def __init__(self):

        self.pipeline = Pipeline([
            (
                "tfidf",
                TfidfVectorizer(
                    lowercase=True,
                    ngram_range=(1, 2),
                    min_df=1,
                    max_df=0.95,
                    sublinear_tf=True,
                ),
            ),
            (
                "classifier",
                LogisticRegression(
                    max_iter=2000,
                    class_weight="balanced",
                    random_state=42,
                ),
            ),
        ])

    def train(
        self,
        messages,
        labels,
    ):

        self.pipeline.fit(
            messages,
            labels,
        )

    def predict(
        self,
        message,
    ):

        return self.pipeline.predict(
            [message]
        )[0]

    def predict_many(
        self,
        messages,
    ):

        return self.pipeline.predict(
            messages
        )

    def predict_proba(
        self,
        message,
    ):

        return self.pipeline.predict_proba(
            [message]
        )[0]

    def save(self):

        joblib.dump(
            self.pipeline,
            MODEL_PATH,
        )

        print(
            f"Model saved to: {MODEL_PATH}"
        )

    def load(self):

        if not MODEL_PATH.exists():
            raise FileNotFoundError(
                f"Model not found: {MODEL_PATH}. "
                "Train the model first."
            )

        self.pipeline = joblib.load(
            MODEL_PATH
        )