import argparse
import logging

from github import (
    Github,
    GithubException,
    Issue,
    Organization,
    Project,
    ProjectColumn,
    ProjectCard,
)

from shared.data import get_data
from shared.github import get_client
from shared.log import configure_logger

configure_logger()

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
    org_name: str,
    repo_names: list[str],
) -> list[Issue]:
    """
    From given repos in the given organization, retrieve a list of open issues
    that have PRs linked to them.

    :param gh: the GitHub client
    :param org_name: the name of the org in which to look for issues
    :param repo_names: the name of the repos in which to look for issues
    :return: the list of open issues with linked PRs
    """

    all_issues = []
    for repo_name in repo_names:
        log.info(f"Looking for issues with PRs in {org_name}/{repo_name}")
        issues = gh.search_issues(
            query=f"",
            sort="updated",
            order="desc",
            **{
                "repo": f"{org_name}/{repo_name}",
                "linked": "pr",
                "is": "open",
            },
        )
        all_issues += list(issues)
    log.info(f"Found {len(all_issues)} open issues with linked PRs")
    return all_issues


def get_org_project(org: Organization, proj_number: int) -> Project:
    """
    Get the project with the given number in the given organization.

    :param org: the organization in which to find the project
    :param proj_number: the number of the project to find in the organization
    :return: the project being searched for
    :raise: ValueError if no project found with given number
    """

    log.info(f"Getting project {proj_number} in org {org.name}")
    projects = org.get_projects()
    project = next(proj for proj in projects if proj.number == proj_number)
    if project is None:
        log.error(f"No project was found with number {proj_number}.")
        raise ValueError(f"Project not found")
    return project


def get_project_column(proj: Project, col_name: str) -> ProjectColumn:
    """
    Get the project column with the given name in the given project.

    :param proj: the project in which to find the column
    :param col_name: the name of the project column to find in the project
    :return: the project column being searched for
    :raise: ValueError if no project column found with given name
    """

    log.info(f"Getting column {col_name} in project {proj.name}")
    columns = proj.get_columns()
    column = next(col for col in columns if col.name == col_name)
    if column is None:
        log.error(f"No column was found with name {col_name}.")
        raise ValueError(f"Column not found")
    return column


def get_issue_cards(col: ProjectColumn) -> list[ProjectCard]:
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
    args = parser.parse_args()

    log.debug(f"Project number: {args.proj_number}")
    log.debug(f"Source column name: {args.source_col_name}")
    log.debug(f"Target column name: {args.target_col_name}")

    github_info = get_data("github.yml")
    org_name = github_info["org"]
    log.info(f"Organization name: {org_name}")
    repo_names = github_info["repos"].values()
    log.info(f"Repository names: {', '.join(repo_names)}")

    gh = get_client()
    org = gh.get_organization(org_name)

    issues_with_prs = get_open_issues_with_prs(
        gh=gh,
        org_name=org_name,
        repo_names=repo_names,
    )

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
            cards_to_move.append(issue_card)
    log.info(f"Found {len(cards_to_move)} cards to move")

    for card in cards_to_move:
        log.info(f"Moving card {card.id} to {target_column.name}")
        card.move("bottom", target_column)
