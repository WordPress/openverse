import argparse
import logging

from shared.data import get_data
from shared.github import get_client
from shared.log import configure_logger
from shared.project import get_org_project, get_project_column

log = logging.getLogger(__name__)

# region argparse
parser = argparse.ArgumentParser(
    description="Move issues to the correct columns in projects",
)
parser.add_argument(
    "--project-number",
    dest="proj_number",
    metavar="project-number",
    type=int,
    required=True,
    help="the project in which to move cards containing issues with PRs",
)
parser.add_argument(
    "--column",
    dest="col_name",
    metavar="column",
    type=str,
    required=True,
    help="column from which to archive cards for PRs",
)


# endregion


def main():
    configure_logger()

    args = parser.parse_args()

    log.debug(f"Project number: {args.proj_number}")
    log.debug(f"Column name: {args.col_name}")

    github_info = get_data("github.yml")
    org_handle = github_info["org"]
    log.info(f"Organization handle: {org_handle}")

    gh = get_client()
    org = gh.get_organization(org_handle)

    proj = get_org_project(org=org, proj_number=args.proj_number)
    log.info(f"Found project: {proj.name}")
    column = get_project_column(proj=proj, col_name=args.col_name)
    log.debug("Found column")

    cards_to_archive = list(column.get_cards(archived_state="not archived"))
    log.info(f"Found {len(cards_to_archive)} cards")
    for card in cards_to_archive:
        card.edit(archived=True)
    log.info("Archived all cards in column")


if __name__ == "__main__":
    main()
