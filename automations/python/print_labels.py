"""Simple utility for printing all the labels from labels.yml."""
from shared.labels import get_labels


if __name__ == "__main__":
    labels = get_labels()
    for label in labels:
        print(label)
