#!/usr/bin/env python3
from __future__ import annotations

import argparse
import logging
import re
from typing import Optional

import requests
from bs4 import BeautifulSoup
from github import Github
from github.Issue import Issue
from github.Label import Label
from github.PullRequest import PullRequest
from shared.data import get_data
from shared.github import get_client
from shared.log import configure_logger


log = logging.getLogger(__name__)

# region argparse
parser = argparse.ArgumentParser(description="")
parser.add_argument(
    "--pr-url",
    dest="pr_url",
    metavar="pr-url",
    required=True,
    help="the URL for the PR to label and/or check for labels",
)


# endregion


def get_owner_repo_num(html_url: str) -> tuple[str, str, int]:
    """
    Get the owner and repo name and issue/PR number from the HTML URL.

    :param html_url: the URL from which to get the owner and repo name and issue/PR num
    :return: the owner and repo name and the issue/PR number
    :raise: ``ValueError``, if the data URL does not match the pattern
    """

    pattern = re.compile(
        r"https://github.com/(?P<owner>.+)/(?P<repo>.+)/(issues|pull)/(?P<num>\d+)"
    )
    if (match := pattern.match(html_url)) is not None:
        return match.group("owner"), match.group("repo"), int(match.group("num"))
    raise ValueError("Could not identify owner and repo name and issue/PR number")


def get_issue(gh: Github, html_url: str) -> Issue:
    """
    Get the ``Issue`` instance from a GitHub issue's HTML URL.

    :param gh: the GitHub client
    :param html_url: the HTML URL of the issue
    :return: the ``Issue`` instance corresponding to the given URL
    """

    org, repo, issue_num = get_owner_repo_num(html_url)
    return gh.get_organization(org).get_repo(repo).get_issue(issue_num)


def get_pull_request(gh: Github, html_url: str) -> PullRequest:
    """
    Get the ``PullRequest`` instance from a GitHub PR's HTML URL.

    :param gh: the GitHub client
    :param html_url: the HTML URL of the PR
    :return: the ``PullRequest`` instance corresponding to the given URL
    """

    org, repo, pr_num = get_owner_repo_num(html_url)
    return gh.get_organization(org).get_repo(repo).get_pull(pr_num)


def get_linked_issues(url: str) -> list[str]:
    """
    Get the list of linked issues from the GitHub UI by parsing the HTML. This is a
    workaround because GitHub API does not provide a reliable way to find the linked
    issues for a PR.

    :param url: the URL to the GitHub UI for a PR
    :return: the list of HTML URLs for linked issues
    """

    res = requests.get(url)
    if res.status_code != 200:
        return []

    soup = BeautifulSoup(res.text, "html.parser")
    divs = soup.find_all("div", **{"class": re.compile("css-truncate my-1")})
    anchors = [div.a["href"] for div in divs]
    return anchors


def get_label_of_cat(cat: str, labels: list[Label]) -> Optional[Label]:
    """
    Get the label of a particular category from the given list of labels.

    :param cat: the category to which the label should belong
    :param labels: the list of labels to choose from
    :return: the label matching the given category
    """

    for label in labels:
        if cat in label.name:
            return label
    return None

def main():
    configure_logger()

    args = parser.parse_args()

    log.debug(f"PR URL: {args.pr_url}")

    github_info = get_data("github.yml")
    org_handle = github_info["org"]
    log.info(f"Organization handle: {org_handle}")

    gh = get_client()

    pr = get_pull_request(gh, args.pr_url)
    log.info(f"Found PR: {pr.title}")

    if pr.labels:
        log.info("PR already labelled")
        return

    linked_issues = get_linked_issues(pr.html_url)
    log.info(f"Found {len(linked_issues)} linked issues")

    for issue in linked_issues:
        issue = get_issue(gh, issue)
        labels = issue.labels
        if all(
            [
                (aspect := get_label_of_cat("aspect", labels)),
                (priority := get_label_of_cat("priority", labels)),
                (goal := get_label_of_cat("goal", labels)),
            ]
        ):
            log.info(f"Aspect label: {aspect}")
            log.info(f"Priority label: {priority}")
            log.info(f"Goal label: {goal}")
            pr.set_labels(aspect, priority, goal)
            break
        # check whether the word "sentry" is in issue body. 
        elif "sentry" in issue.body:
            tooling = get_label_of_cat("tooling", labels)
            log.info(f"Tooling label: {tooling}")
            pr.set_labels(tooling)
    else:
        log.info("Could not find properly labelled issue")
        pr.set_labels("🚦 status: awaiting triage")


if __name__ == "__main__":
    main()
