from copy import deepcopy

from models.label import Label
from models.label_group import LabelGroup

from shared.data import get_data


def get_labels_by_group(labels_file: dict = None) -> dict[str, LabelGroup]:
    """Get all the grouped labels as a mapping of group name to label group."""

    labels_file = labels_file or deepcopy(get_data("labels.yml"))
    grouped_labels = {}
    for group_info in labels_file["groups"]:
        labels = group_info.pop("labels", [])
        group = LabelGroup(**group_info)
        for label_info in labels:
            # Set up the labels
            Label(**label_info, group=group)
        grouped_labels[group.name] = group
    return grouped_labels


def get_labels() -> list[Label]:
    """
    Get all the standard labels as a list.

    :return: a list of Label objects
    """
    labels_file = deepcopy(get_data("labels.yml"))
    grouped_labels = get_labels_by_group(labels_file)
    standard_labels = [
        label for group in grouped_labels.values() for label in group.labels
    ]
    # Also grab standard labels
    for label_info in labels_file["standalone"]:
        label = Label(**label_info)
        standard_labels.append(label)
    return standard_labels
