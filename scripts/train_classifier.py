from app.ml.dataset import MindCareDataset
from app.ml.text_classifier import MindCareTextClassifier


def main():

    dataset = MindCareDataset()

    train_messages, train_labels = (
        dataset.get_train()
    )

    print("=" * 60)
    print("MINDCARE ML TRAINING")
    print("=" * 60)

    print(
        f"\nTraining examples: "
        f"{len(train_messages)}"
    )

    print(
        "\nTraining TF-IDF + "
        "Logistic Regression..."
    )

    model = MindCareTextClassifier()

    model.train(
        train_messages,
        train_labels,
    )

    model.save()

    print("\nTraining completed successfully.")


if __name__ == "__main__":
    main()