import datetime
import json
import random
from collections import namedtuple
from functools import partial
from pathlib import Path
from typing import Literal

from dags.maintenance.pr_review_reminders.pr_review_reminders import (
    COMMENT_MARKER,
    Urgency,
    parse_gh_date,
)


def _read_fixture(fixture: str) -> dict:
    with open(Path(__file__).parent / f"{fixture}.json") as file:
        return json.loads(file.read())


def _make_label(priority: Urgency.Urgency) -> dict:
    return {"name": f"priority: {priority.label}"}


def _gh_date(d: datetime.datetime) -> str:
    return f"{d.isoformat()}Z"


def walk_backwards_in_time_until_weekday_count(today: datetime.datetime, count: int):
    test_date = today
    weekday_count = 0
    while weekday_count < count:
        test_date = test_date - datetime.timedelta(days=1)
        if test_date.weekday() < 5:
            weekday_count += 1

    return test_date


_pr_count = 1

_id_offset = 1000000


def make_pull(urgency: Urgency, old: bool, base_branch: str = "main") -> dict:
    """
    Create a PR object like the one returned by the GitHub API.

    The PR will also be created specifically to have the priority
    label associated with the passed in urgency.

    A "past due" PR is one that has an ``updated_at`` value that is
    further in the past than the number of days allowed by the
    urgency of the PR.

    :param urgency: The priority to apply to the PR.
    :param old: Whether to create a PR with a created_at date beyond
    the urgency window for ``urgency``.
    :param base_branch: The target branch for the PR.
    """
    global _pr_count
    pull = _read_fixture("pull")
    # PR "number" is the number for the repository
    # that we're used to
    pull["number"] = _pr_count
    # PR "id" is GitHub's internal unique identifier
    # for the PR across all PRs on GitHub. It must
    # be different from the "number" to ensure
    # we're not confusing the two in code.
    # Instead of tracking a separate number,
    # we can add a huge number to the _pr_count.
    # This would only ever be a problem if our
    # function was used to generate more
    # PR fixtures than the id offset accounts
    # for. If that ever becomes the case, just add
    # a 0 to the end of ``_id_offset`` above
    # and it will resolve the issue.
    # Note: We could use a UUID for this to prevent
    # all possible collision with ``number`` from
    # but GitHub uses integers for this property
    # so to keep realistic-ish fixture data we
    # should prefer an integer here as well.
    pull["id"] = _pr_count + _id_offset
    _pr_count += 1

    for label in pull["labels"]:
        if "priority" in label["name"]:
            label.update(**_make_label(urgency))
            break

    if old:
        created_at = walk_backwards_in_time_until_weekday_count(
            datetime.datetime.now(), urgency.days
        )
    else:
        created_at = datetime.datetime.now()

    pull["created_at"] = _gh_date(created_at)

    base = pull["base"]
    base["ref"] = base_branch
    base["label"] = f"WordPress:{base_branch}"

    return pull


def make_requested_reviewer(login: str) -> dict:
    requested_reviewer = _read_fixture("requested_reviewer")

    requested_reviewer["login"] = login

    return requested_reviewer


_comment_count = 1


def make_pr_comment(
    is_reminder: bool, created_at: datetime.datetime | None = None
) -> dict:
    global _comment_count

    comment = _read_fixture("comment")
    comment["id"] = _comment_count
    _comment_count += 1

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

    if created_at:
        comment["created_at"] = _gh_date(created_at)

    return comment


def make_issue(state: str) -> dict:
    issue = _read_fixture("issue")

    issue["state"] = state

    return issue


def make_current_pr_comment(pull: dict) -> dict:
    return make_pr_comment(
        True, parse_gh_date(pull["updated_at"]) + datetime.timedelta(minutes=1)
    )


def make_outdated_pr_comment(pull: dict) -> dict:
    return make_pr_comment(
        True, parse_gh_date(pull["updated_at"]) - datetime.timedelta(minutes=1)
    )


def make_review(state: Literal["APPROVED", "CHANGES_REQUESTED", "COMMENTED"]):
    review = _read_fixture("review")

    review["state"] = state

    return review


def make_branch_protection(required_reviewers: int = 2) -> dict:
    branch_protection = _read_fixture("branch_protection")

    branch_protection["required_pull_request_reviews"][
        "required_approving_review_count"
    ] = required_reviewers

    return branch_protection


EventsConfig = namedtuple("EventsConfig", "event_name, days_since_previous_event")


def make_events(origin_days_ago: int, events: list[str | EventsConfig]) -> list[dict]:
    """
    Create an issue events list with events starting at the origin.

    The complexity of this fixture function is necessary to ease building
    events list and testing the various states an events list can be in.

    :param origin_days_ago: The number of days ago to treat as the origin
    for the events list. If 0 then all events will be treated as being created the
    same day and days lapsed configured for individual events will be ignored.
    :param events: A list of mixed strings and (string, int) tuples. The string
    must always be an event name. If a tuple, the int should be the number
    of days to increment the event past the previous event.
    """
    result = []
    previous_event_days_ago = origin_days_ago
    for event_name in events:
        days_since_previous_event = 0
        if isinstance(event_name, tuple):
            if origin_days_ago == 0:
                # If origin days is 0 then treat all events as occurring today,
                # otherwise events configured with days lapsed would end up
                # in the future.
                days_since_previous_event = 0
            else:
                days_since_previous_event = event_name[1]

            event_name = event_name[0]

        # Example: If the previous event was 2 days ago, and it has been
        # 1 day since that previous event, then this event was 1 day ago.
        days_ago = previous_event_days_ago - days_since_previous_event
        created_at = walk_backwards_in_time_until_weekday_count(
            datetime.datetime.now(), days_ago
        )

        event = _read_fixture(f"events/{event_name}")
        event["created_at"] = _gh_date(created_at)

        previous_event_days_ago = days_ago
        result.append(event)

    return result


def make_non_urgent_events(events: list[str | EventsConfig]) -> list[dict]:
    """
    Create an events list where all events happened today.

    By setting ``origin_days_ago`` to 0 we force the entire
    events list to happen _now_ which necessarily means
    none of the events could be considered urgent.
    """
    return make_events(0, events)


def make_non_urgent_reviewable_events(events: list[str | EventsConfig]) -> list[dict]:
    """
    Create a reviewable but non-urgent events list.

    By adding a "ready_for_review" event at the
    end of the events list, we create valid events for
    a reviewable PR.

    We set the origin_days_ago to ensure that the last
    `ready_for_review` event happened today, guaranteeing
    that despite the reviewable status, the events will not
    be considered urgent. We do this by summing the days between
    each event in the event list.

    Suitable for testing old PRs that _must_ be
    reviewable but non-urgent. This allows us to
    combine tests that would otherwise need to be
    split out due to old PRs automatically being
    urgent if they do not have a non-urgent ready
    for review event. As this is the most common case
    for urgent PRs (i.e, PRs that have never been
    drafted or undrafted, just opened as ready for review)
    it is included in the "pingable" events examples
    but needs to be patched for old but non-urgent PRs.
    """
    events_list_days = sum(
        [event[1] if isinstance(event, tuple) else 0 for event in events]
    )

    return make_events(events_list_days, events + ["ready_for_review"])


def make_urgent_events(
    urgency: Urgency.Urgency, events: list[str | EventsConfig]
) -> list[dict]:
    """
    Create an events list ending in an event older than the urgency days.

    Allows parametrizing events without while setting origin days
    in the test function.
    """
    events_list_days = sum(
        [event[1] if isinstance(event, tuple) else 0 for event in events]
    )
    return make_events(events_list_days + urgency.days, events)
