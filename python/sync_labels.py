import logging
from copy import deepcopy

from github import Repository
from models.label import Label
from models.label_group import LabelGroup
from shared.data import get_data
from shared.github import get_client
from shared.log import configure_logger


log = logging.getLogger(__name__)


def get_labels() -> list[Label]:
    """
    Get all the standard labels as a list.

    :return: a list of Label objects
    """

    labels_file = deepcopy(get_data("labels.yml"))
    standard_labels = []
    for group_info in labels_file["groups"]:
        labels = group_info.pop("labels", [])
        group = LabelGroup(**group_info)
        for label_info in labels:
            label = Label(**label_info, group=group)
            standard_labels.append(label)
    for label_info in labels_file["standalone"]:
        label = Label(**label_info)
        standard_labels.append(label)
    return standard_labels


def set_labels(repo: Repository, labels: list[Label]):
    """
    Set the given list of labels on the given repository. Missing labels will
    be added, but extraneous labels will be left intact.

    :param repo: the repo in which to set the given labels
    :param labels: the list of labels to define on the repo
    """

    log.info(f"Fetching existing labels from {repo.full_name}")
    existing_labels = {
        label.name.casefold(): label for label in repo.get_labels()
    }
    log.info(f"Found {len(existing_labels)} existing labels")

    for label in labels:
        qualified_name = label.qualified_name
        folded_name = qualified_name.casefold()
        if folded_name not in existing_labels:
            log.info(f"Creating label {qualified_name}")
            repo.create_label(**label.api_arguments)
        elif label != existing_labels[folded_name]:
            log.info(f"Updating label {qualified_name}")
            existing_label = existing_labels[folded_name]
            existing_label.edit(**label.api_arguments)
        else:
            log.info(f"Label {qualified_name} already exists")


def main():
    configure_logger()

    github_info = get_data("github.yml")
    org_handle = github_info["org"]
    log.info(f"Organization handle: {org_handle}")
    repo_names = github_info["repos"].values()
    log.info(f"Repository names: {', '.join(repo_names)}")

    gh = get_client()
    org = gh.get_organization(org_handle)

    labels = get_labels()
    log.info(f"Synchronizing {len(labels)} standard labels")
    for label in labels:
        log.info(f"• {label.qualified_name}")
    repos = [org.get_repo(repo_name) for repo_name in repo_names]
    for repo in repos:
        set_labels(repo, get_labels())


if __name__ == "__main__":
    main()
