import argparse
import logging
import sys

from github import (
    Github,
    GithubException,
    Issue,
    ProjectColumn,
    ProjectCard,
)

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
    "--source-column",
    dest="source_col_name",
    metavar="source-column",
    type=str,
    default="To do",
    help="column from which to move cards containing issues with PRs",
)
parser.add_argument(
    "--target-column",
    dest="target_col_name",
    metavar="target-column",
    type=str,
    default="In progress",
    help="column in which to move cards containing issues with PRs",
)


# endregion


def get_open_issues_with_prs(
    gh: Github,
    org_handle: str,
    repo_names: list[str],
) -> list[Issue]:
    """
    From given repos in the given organization, retrieve a list of open issues
    that have PRs linked to them.

    :param gh: the GitHub client
    :param org_handle: the name of the org in which to look for issues
    :param repo_names: the name of the repos in which to look for issues
    :return: the list of open issues with linked PRs
    """

    all_issues = []
    for repo_name in repo_names:
        log.info(f"Looking for issues with PRs in {org_handle}/{repo_name}")
        issues = gh.search_issues(
            query="",
            sort="updated",
            order="desc",
            **{
                "repo": f"{org_handle}/{repo_name}",
                "is": "issue",
                "state": "open",
                "linked": "pr",
            },
        )
        issues = list(issues)
        log.info(f"Found {len(issues)} issues")
        for issue in issues:
            log.info(f"• #{issue.number} | {issue.title}")
        all_issues += issues

    log.info(f"Found a total of {len(all_issues)} open issues with linked PRs")
    return all_issues


def get_issue_cards(col: ProjectColumn) -> list[tuple[ProjectCard, Issue]]:
    """
    Get all cards linked to issues in the given column. This excludes cards that
    either have no links (just notes) or are linked to PRs.

    :param col: the project column from which to retrieve issue cards
    :return: the list of cards linked to issues in the given column
    """

    cards = col.get_cards(archived_state="not archived")
    issue_cards = []
    for card in cards:
        issue = card.get_content()
        if issue is None:
            continue
        try:
            issue.as_pull_request()
        except GithubException:
            issue_cards.append((card, issue))
    return issue_cards


if __name__ == "__main__":
    configure_logger()

    args = parser.parse_args()

    log.debug(f"Project number: {args.proj_number}")
    log.debug(f"Source column name: {args.source_col_name}")
    log.debug(f"Target column name: {args.target_col_name}")

    github_info = get_data("github.yml")
    org_handle = github_info["org"]
    log.info(f"Organization handle: {org_handle}")
    repo_names = github_info["repos"].values()
    log.info(f"Repository names: {', '.join(repo_names)}")

    gh = get_client()
    org = gh.get_organization(org_handle)

    issues_with_prs = get_open_issues_with_prs(
        gh=gh,
        org_handle=org_handle,
        repo_names=repo_names,
    )
    if len(issues_with_prs) == 0:
        log.warning("Found no issues with PRs, stopping")
        sys.exit()

    proj = get_org_project(org=org, proj_number=args.proj_number)
    log.info(f"Found project: {proj.name}")
    source_column = get_project_column(proj=proj, col_name=args.source_col_name)
    log.debug("Found source column")
    target_column = get_project_column(proj=proj, col_name=args.target_col_name)
    log.debug("Found target column")

    issue_cards = get_issue_cards(source_column)

    cards_to_move = []
    for (issue_card, issue) in issue_cards:
        if issue in issues_with_prs:
            cards_to_move.append((issue_card, issue))
    log.info(f"Found {len(cards_to_move)} cards to move")

    for (issue_card, issue) in cards_to_move:
        log.info(f"Moving card for issue {issue.html_url} to {target_column.name}")
        issue_card.move("bottom", target_column)
