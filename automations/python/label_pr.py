#!/usr/bin/env python3
from __future__ import annotations

import argparse
import logging
import os
import re
from http.cookiejar import CookieJar

import mechanize
import pyotp
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

REQUIRED_LABEL_CATEGORIES = ["aspect", "priority", "goal", "stack"]
# Categories where all labels should be retrievd rather than first only
GET_ALL_LABEL_CATEGORIES = {"stack"}

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


def get_authenticated_html(url: str) -> str:
    """
    Retrieve HTML for GitHub webpages that require authentication to view.

    Login to the GitHub UI using the username and password, followed by 2FA.
    Then navigate to the specified URL as the authenticated user and scrape the
    text body.

    :param url: the URL to scrape after authenticating in GitHub
    :return: the text content of the scraped page
    """

    browser = mechanize.Browser()
    browser.set_cookiejar(CookieJar())
    browser.open("https://github.com/login/")
    try:
        browser.select_form(nr=0)  # focus on the first (and only) form on the page
        browser.form["login"] = os.getenv("GH_LOGIN")
        browser.form["password"] = os.getenv("GH_PASSWORD")
        browser.submit()

        browser.select_form(nr=0)  # focus on the first (and only) form on the page
        browser.form["app_otp"] = pyotp.TOTP(os.getenv("GH_2FA_SECRET")).now()
        browser.submit()
    except mechanize.ControlNotFoundError as err:
        form_name = err.args[0].replace("no control matching name ", "").strip("'")
        raise ValueError(
            f"Unable to locate form input '{form_name}' on GitHub login page, "
            "perhaps its name has changed?"
        )

    browser.open(url)
    return browser.response().read()


def get_linked_issues(url: str) -> list[str]:
    """
    Get the list of linked issues from the GitHub UI by parsing the HTML.

    This is a workaround because GitHub API does not provide a reliable way
    to find the linked issues for a PR.

    If the page returns a 404 response, it is assumed that the page belongs to a private
    repository and needs authentication. In these cases, ``get_authenticated_html`` is
    used to scrape the page.

    :param url: the URL to the GitHub UI for a PR
    :return: the list of HTML URLs for linked issues
    """

    res = requests.get(url)
    if res.status_code == 404:
        text = get_authenticated_html(url)
    elif res.status_code == 200:
        text = res.text
    else:
        return []

    soup = BeautifulSoup(text, "html.parser")
    form = soup.find("form", **{"aria-label": "Link issues"})
    if form is None:
        return []
    return [a["href"] for a in form.find_all("a")]


def get_all_labels_of_cat(cat: str, labels: list[Label]) -> list[Label]:
    """
    Get all of the available labels from a category from a given list of
    labels.

    :param cat: the category to which the label should belong
    :param labels: the list of labels to choose from
    :return: the labels matching the given category
    """
    available_labels = []
    for label in labels:
        if cat in label.name:
            available_labels.append(label)
    return available_labels


def get_label_of_cat(cat: str, labels: list[Label]) -> Label | None:
    """
    Get the label of a particular category from the given list of labels.

    :param cat: the category to which the label should belong
    :param labels: the list of labels to choose from
    :return: the label matching the given category
    """
    return next(iter(get_all_labels_of_cat(cat, labels)), None)


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
        labels_to_add = []

        for category in REQUIRED_LABEL_CATEGORIES:
            if category in GET_ALL_LABEL_CATEGORIES and (
                available_labels := get_all_labels_of_cat(category, labels)
            ):
                log.info(f"Found labels for category {category}: {available_labels}")
                labels_to_add.extend(available_labels)
            elif label := get_label_of_cat(category, labels):
                log.info(f"Found label for category {category}: {label}")
                labels_to_add.append(label)

        if labels_to_add:
            pr.set_labels(*labels_to_add)
            # Only break when all labels are applied, if we're missing any
            # then continue to the else to apply the awaiting triage label.
            # Stack can have more than one label so this is not an exact check
            if len(labels_to_add) >= len(REQUIRED_LABEL_CATEGORIES):
                break
    else:
        log.info("Could not find properly labelled issue")
        pr.set_labels("🚦 status: awaiting triage")


if __name__ == "__main__":
    main()
