#!/usr/bin/env python3
import argparse
import logging
import sys
from typing import Literal

import requests
from github import Github, ProjectCard, ProjectColumn
from shared.data import get_data
from shared.github import get_access_token, get_client
from shared.log import configure_logger
from shared.project import get_org_project, get_project_column


log = logging.getLogger(__name__)

CLOSED = "closed"
OPEN = "open"
IssueState = Literal[CLOSED, OPEN]
# Unique identifier of repo + issue
RepoIssue = tuple[str, str]

LINKED_PR_QUERY = """
{
    repository(owner: "%s", name: "%s") {
        pullRequests(first: 100, states:%s,
                     orderBy:{field:UPDATED_AT, direction:DESC}) {
            nodes {
                number
                title
                closingIssuesReferences (first: 50) {
                    edges {
                        node {
                            number
                            title
                            state
                        }
                    }
                }
            }
        }
    }
}
"""


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
parser.add_argument(
    "--linked-pr-state",
    dest="linked_pr_state",
    metavar="linked-pr-state",
    type=str,
    default=OPEN,
    choices=[OPEN, CLOSED],
    help="filter issues by this state of their linked PRs",
)

# endregion


def run_query(
    query,
) -> dict:
    """
    Run a GitHub GraphQL query.
    Taken from https://gist.github.com/gbaman/b3137e18c739e0cf98539bf4ec4366ad
    """
    log.debug(f"{query=}")
    request = requests.post(
        "https://api.github.com/graphql",
        json={"query": query},
        headers={"Authorization": f"Bearer {get_access_token()}"},
    )
    if request.status_code == 200:
        results = request.json()
        log.debug(f"{results=}")
        return request.json().get("data")
    else:
        raise Exception(
            "Query failed to run by returning code of {}. {}".format(
                request.status_code, query
            )
        )


def get_pulls_with_linked_issues(
    org_handle: str, repo_name: str, state: IssueState
) -> dict[str, str]:
    """
    Query all the pull requests with issues of a linked state.

    This uses the GraphQL API since the REST API doesn't support querying for linked
    issues.

    :return: a dict of issue numbers to issue titles
    """
    results = run_query(LINKED_PR_QUERY % (org_handle, repo_name, state.upper()))
    pulls = results["repository"]["pullRequests"]["nodes"]
    log.info(f"Found {len(pulls)} {state} PRs in {org_handle}/{repo_name}")
    return {
        issue["node"]["number"]: issue["node"]["title"]
        for pull in pulls
        for issue in pull["closingIssuesReferences"]["edges"]
    }


def get_open_issues_with_prs(
    gh: Github,
    org_handle: str,
    repo_names: list[str],
    linked_pr_state: str,
) -> set[RepoIssue]:
    """
    Retrieve open issues with linked PRs.

    :param gh: the GitHub client
    :param org_handle: the name of the org in which to look for issues
    :param repo_names: the name of the repos in which to look for issues
    :param linked_pr_state: the state of the linked PRs to filter by
    :return: a set of tuples containing the repo name and issue number for each issue
    """

    all_issues = set()
    for repo_name in repo_names:
        log.info(
            f"Looking for {linked_pr_state} PRs in {org_handle}/{repo_name} "
            f"with linked issues"
        )
        issues = get_pulls_with_linked_issues(org_handle, repo_name, linked_pr_state)
        # In the case where we're querying for closed PRs, we'll also need to consider
        # open PRs - if there's an issue with both an open PR and a closed PR, we should
        # not take any action on it
        open_issues = {}
        if linked_pr_state == CLOSED:
            open_issues = get_pulls_with_linked_issues(org_handle, repo_name, OPEN)

        log.info(f"Found {len(issues)} issues")
        for number, title in issues.items():
            log.info(f"• #{number: >5} | {title}")
            if linked_pr_state == CLOSED and number in open_issues:
                log.info(f"{' ' * 11}(skipped because there's an open PR)")
                continue
            all_issues.add((repo_name, number))

    log.info(
        f"Found a total of {len(all_issues)} open issues "
        f"with linked {linked_pr_state} PRs"
    )
    return all_issues


def get_issue_cards(col: ProjectColumn) -> list[tuple[ProjectCard, RepoIssue]]:
    """
    Get all cards linked to issues in the given column.

    This excludes cards that either have no links (just notes) or are linked to PRs.

    :param col: the project column from which to retrieve issue cards
    :return: the list of cards linked to issues in the given column
    """

    cards = col.get_cards(archived_state="not archived")
    issue_cards = []
    for card in cards:
        # Example URL: https://api.github.com/repos/api-playground/project-test/issues/3
        # See: https://docs.github.com/en/rest/projects/cards?apiVersion=2022-11-28
        url = card.content_url
        try:
            url_parts = url.split("/")
            # Repo + issue
            issue = (url_parts[-3], url_parts[-1])
        except Exception:
            log.debug(f"Could not decode card with content_url: {url}")
            continue
        issue_cards.append((card, issue))
    return issue_cards


def main():
    configure_logger()

    args = parser.parse_args()

    log.debug(f"Project number: {args.proj_number}")
    log.debug(f"Source column name: {args.source_col_name}")
    log.debug(f"Target column name: {args.target_col_name}")
    log.debug(f"Linked issue PR state: {args.linked_pr_state}")

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
        linked_pr_state=args.linked_pr_state,
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
    for issue_card, issue in issue_cards:
        if issue in issues_with_prs:
            cards_to_move.append((issue_card, issue))
    log.info(f"Found {len(cards_to_move)} cards to move")

    for (issue_card, issue) in cards_to_move:
        log.info(f"Moving card for issue {issue.html_url} to {target_column.name}")
        issue_card.move("bottom", target_column)


if __name__ == "__main__":
    main()
