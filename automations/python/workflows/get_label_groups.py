from shared.actions import write_to_github_output
from shared.labels import get_labels_by_group


def main() -> None:
    """
    Get all the grouped labels as a mapping of group name to label group.

    :return: a dict of LabelGroup objects
    """
    label_groups = get_labels_by_group()
    lines = []
    for name, group in label_groups.items():
        labels = ",".join(map(str, group.labels))
        lines.append(f"{name}={labels}")
    write_to_github_output(lines)


if __name__ == "__main__":
    main()
