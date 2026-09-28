from pathlib import Path

import pandas as pd

from app.ml.labels import LABELS


BASE_DIR = Path("data/mindcare_clean")


class MindCareDataset:

    def __init__(self):

        self.train_path = BASE_DIR / "train.csv"
        self.validation_path = BASE_DIR / "validation.csv"
        self.test_path = BASE_DIR / "test.csv"

        self.train = self._load(self.train_path)
        self.validation = self._load(self.validation_path)
        self.test = self._load(self.test_path)

        self.validate()

    @staticmethod
    def _load(path):

        if not path.exists():
            raise FileNotFoundError(
                f"Dataset not found: {path}"
            )

        return pd.read_csv(path)

    def validate(self):

        required_columns = {
            "message",
            "category",
            "risk_level",
            "language",
        }

        for name, df in [
            ("train", self.train),
            ("validation", self.validation),
            ("test", self.test),
        ]:

            missing = (
                required_columns
                - set(df.columns)
            )

            if missing:
                raise ValueError(
                    f"{name} missing columns: {missing}"
                )

            unknown_labels = (
                set(df["category"])
                - set(LABELS)
            )

            if unknown_labels:
                raise ValueError(
                    f"{name} has unknown labels: "
                    f"{unknown_labels}"
                )

    def get_train(self):

        return (
            self.train["message"].tolist(),
            self.train["category"].tolist(),
        )

    def get_validation(self):

        return (
            self.validation["message"].tolist(),
            self.validation["category"].tolist(),
        )

    def get_test(self):

        return (
            self.test["message"].tolist(),
            self.test["category"].tolist(),
        )

    def summary(self):

        return {
            "train": len(self.train),
            "validation": len(self.validation),
            "test": len(self.test),
            "total": (
                len(self.train)
                + len(self.validation)
                + len(self.test)
            ),
        }