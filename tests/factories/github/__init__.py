import datetime
import json
from pathlib import Path

from openverse_catalog.dags.maintenance.pr_review_reminders.pr_review_reminders import (
    COMMENT_MARKER,
    Urgency,
)


def _read_fixture(fixture: str) -> dict:
    with open(Path(__file__).parent / f"{fixture}.json") as file:
        return json.loads(file.read())


def _make_label(priority: Urgency) -> dict:
    return {"name": f"priority: {priority.label}"}


def walk_backwards_in_time_until_weekday_count(today: datetime.datetime, count: int):
    test_date = today
    weekday_count = 0
    while weekday_count < count:
        test_date = test_date - datetime.timedelta(days=1)
        if test_date.weekday() < 5:
            weekday_count += 1

    return test_date


_pr_count = 1


def make_pull(urgency: Urgency, past_due: bool) -> dict:
    """
    Creates a PR object like the one returned by the GitHub API.
    The PR will also be created specifically to have the priority
    label associated with the passed in urgency.

    A "past due" PR is one that has an ``updated_at`` value that is
    further in the past than the number of days allowed by the
    urgency of the PR.

    :param urgency: The priority to apply to the PR.
    :param past_due: Whether to create a PR that is "past due".
    """
    global _pr_count
    pull = _read_fixture("pull")
    pull["number"] = pull["id"] = _pr_count
    _pr_count += 1

    for label in pull["labels"]:
        if "priority" in label["name"]:
            label.update(**_make_label(urgency))
            break

    if past_due:
        updated_at = walk_backwards_in_time_until_weekday_count(
            datetime.datetime.now(), urgency.days
        )
    else:
        updated_at = datetime.datetime.now()

    pull["updated_at"] = f"{updated_at.isoformat()}Z"

    return pull


def make_requested_reviewer(login: str) -> dict:
    requested_reviewer = _read_fixture("requested_reviewer")

    requested_reviewer["login"] = login

    return requested_reviewer


def make_pr_comment(is_reminder: bool) -> dict:
    comment = _read_fixture("comment")

    if is_reminder:
        comment["user"]["login"] = "openverse-bot"

    comment["body"] = (
        ("This is a comment\n" f"{COMMENT_MARKER}\n\n" "Please review me :)")
        if is_reminder
        else (
            "This looks great! Amazing work :tada: "
            "You're lovely and valued as a contributor "
            "and as a whole person."
        )
    )

    return comment


def make_issue(state: str) -> dict:
    issue = _read_fixture("issue")

    issue["state"] = state

    return issue
