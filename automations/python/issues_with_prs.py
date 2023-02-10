#!/usr/bin/env python3
import argparse
import logging
import sys
from collections import defaultdict

from github import Github, GithubException, Issue, ProjectCard, ProjectColumn
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
parser.add_argument(
    "--linked-pr-state",
    dest="linked_pr_state",
    metavar="linked-pr-state",
    type=str,
    default="open",
    help="filter issues by this state of their linked PRs",
)

# TODO: Add a new argument, which is like "closed PRs" or something which tells the
# TODO: script logic to only filter down to issues with linked PRs which are closed.
# TODO: The rest of the logic can be the same because we're just moving issue from
# TODO: one column to another

# endregion


def get_open_issues_with_prs(
    gh: Github,
    org_handle: str,
    repo_names: list[str],
    linked_pr_state: str,
) -> list[Issue]:
    """
    Retrieve open issues with linked PRs.

    :param gh: the GitHub client
    :param org_handle: the name of the org in which to look for issues
    :param repo_names: the name of the repos in which to look for issues
    :param linked_pr_state: the state of the linked PRs to filter by
    :return: the list of open issues with linked PRs
    """

    issues_by_repo = {}
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
        issues_by_repo[repo_name] = issues

    # Have to either make individual queries per-PR or search by PR ID. Problem with the
    # latter is that it also returns PRs which reference the number inside it.
    # So we will further have to filter out PRs which are returned from the search but
    # are not in any of the PRs supplied
    # Extract the PR ID
    # FIXME: This doesn't work because the pull request key is only available for pull requests actually
    pr_mapping: dict[str, dict[str, Issue]] = {
        repo_name: {issue.pull_request.html_url.rsplit("/", 1)[-1]: issue for issue in issues}
        for repo_name, issues in issues_by_repo.items()
    }
    all_issues = []
    for repo_name, pr_issue_mapping in pr_mapping.items():
        pr_ids = set(pr_issue_mapping.keys())
        log.info(
            f"Looking for {linked_pr_state} PRs with the following IDs in "
            f"{org_handle}/{repo_name}: {pr_ids}"
        )
        prs = gh.search_issues(
            query=" ".join(pr_ids),
            sort="updated",
            order="desc",
            **{
                "repo": f"{org_handle}/{repo_name}",
                "is": "pr",
                "state": linked_pr_state,
            },
        )
        # Ensure PR actually *is* within the listed IDs rather than just referencing it
        prs = [pr for pr in prs if pr.number in pr_ids]
        # Match PRs back to issues
        for pr in prs:
            all_issues.append(pr_issue_mapping[str(pr.number)])

    log.info(f"Found a total of {len(all_issues)} open issues with linked PRs")
    return all_issues


def get_issue_cards(col: ProjectColumn) -> list[tuple[ProjectCard, Issue]]:
    """
    Get all cards linked to issues in the given column.

    This excludes cards that either have no links (just notes) or are linked to PRs.

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
    for (issue_card, issue) in issue_cards:
        if issue in issues_with_prs:
            cards_to_move.append((issue_card, issue))
    log.info(f"Found {len(cards_to_move)} cards to move")

    for (issue_card, issue) in cards_to_move:
        log.info(f"Moving card for issue {issue.html_url} to {target_column.name}")
        # issue_card.move("bottom", target_column)


if __name__ == "__main__":
    main()
