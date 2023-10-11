from collections import defaultdict
from datetime import datetime, timedelta

import pytest
from requests import HTTPError, Request, Response

from catalog.tests.factories.github import (
    EventsConfig,
    make_branch_protection,
    make_current_pr_comment,
    make_non_urgent_events,
    make_non_urgent_reviewable_events,
    make_outdated_pr_comment,
    make_pr_comment,
    make_pull,
    make_requested_reviewer,
    make_review,
    make_urgent_events,
)
from maintenance.pr_review_reminders.pr_review_reminders import (
    Urgency,
    days_without_weekends,
    post_reminders,
)


MONDAY = datetime(2022, 6, 13)
TUESDAY = MONDAY + timedelta(days=1)
WEDNESDAY = MONDAY + timedelta(days=2)
THURSDAY = MONDAY + timedelta(days=3)
FRIDAY = MONDAY + timedelta(days=4)
SATURDAY = MONDAY + timedelta(days=5)
SUNDAY = MONDAY + timedelta(days=6)

NEXT_MONDAY = MONDAY + timedelta(days=7)
NEXT_TUESDAY = MONDAY + timedelta(days=8)
NEXT_WEDNESDAY = MONDAY + timedelta(days=9)

LAST_SUNDAY = MONDAY - timedelta(days=1)
LAST_SATURDAY = MONDAY - timedelta(days=2)
LAST_FRIDAY = MONDAY - timedelta(days=3)
LAST_THURSDAY = MONDAY - timedelta(days=4)
LAST_WEDNESDAY = MONDAY - timedelta(days=5)
LAST_TUESDAY = MONDAY - timedelta(days=6)
LAST_MONDAY = MONDAY - timedelta(days=7)


@pytest.mark.parametrize(
    "today, against, expected_days",
    (
        (MONDAY, LAST_SUNDAY, 0),
        (MONDAY, LAST_SATURDAY, 0),
        (MONDAY, LAST_FRIDAY, 1),
        (MONDAY, LAST_THURSDAY, 2),
        (MONDAY, LAST_WEDNESDAY, 3),
        (MONDAY, LAST_TUESDAY, 4),
        (MONDAY, LAST_MONDAY, 5),
        (MONDAY, MONDAY, 0),
        (TUESDAY, MONDAY, 1),
        (WEDNESDAY, MONDAY, 2),
        (THURSDAY, MONDAY, 3),
        (FRIDAY, MONDAY, 4),
        (FRIDAY, THURSDAY, 1),
        (THURSDAY, WEDNESDAY, 1),
        (WEDNESDAY, TUESDAY, 1),
        (SUNDAY, SATURDAY, 0),
        (NEXT_MONDAY, LAST_MONDAY, 10),
        (NEXT_TUESDAY, LAST_MONDAY, 11),
        (NEXT_WEDNESDAY, LAST_MONDAY, 12),
    ),
)
def test_days_without_weekends_no_weekend_days_monday(today, against, expected_days):
    assert days_without_weekends(today, against) == expected_days


@pytest.fixture
def github(monkeypatch):
    pulls = []
    pull_comments = defaultdict(list)
    posted_comments = defaultdict(list)
    deleted_comments = []
    pull_reviews = defaultdict(list)
    branch_protection = defaultdict(dict)
    events = defaultdict(list)

    def get_prs(*args, **kwargs):
        return pulls

    def get_comments(*args, **kwargs):
        pr_number = args[2]
        return pull_comments[pr_number]

    def post_comment(*args, **kwargs):
        pr_number = args[2]
        body = args[3]
        posted_comments[pr_number].append(body)

    def delete_comment(*args, **kwargs):
        comment_number = args[2]
        deleted_comments.append(comment_number)

    def get_reviews(*args, **kwargs):
        pr_number = args[2]
        return pull_reviews[pr_number]

    def get_events(*args, **kwargs):
        pr_number = args[2]
        return events[pr_number]

    def get_branch_protection(*args, **kwargs):
        repo = args[1]
        branch = args[2]
        if repo not in branch_protection or branch not in branch_protection[repo]:
            response = Response()
            response.status_code = 404
            request = Request(method="GET", url="https://api.github.com/")
            response.request = request
            raise HTTPError(response=response)

        return branch_protection[repo][branch]

    def patch_gh_fn(fn, impl):
        monkeypatch.setattr(
            f"catalog.dags.maintenance.pr_review_reminders.pr_review_reminders.GitHubAPI.{fn}",
            impl,
        )

    patch_gh_fn("get_open_prs", get_prs)
    patch_gh_fn("get_issue_comments", get_comments)
    patch_gh_fn("get_issue_events", get_events)
    patch_gh_fn("post_issue_comment", post_comment)
    patch_gh_fn("delete_issue_comment", delete_comment)
    patch_gh_fn("get_pull_reviews", get_reviews)
    patch_gh_fn("get_branch_protection", get_branch_protection)

    yield {
        "pulls": pulls,
        "pull_comments": pull_comments,
        "posted_comments": posted_comments,
        "deleted_comments": deleted_comments,
        "pull_reviews": pull_reviews,
        "branch_protection": branch_protection,
        "events": events,
    }


@pytest.fixture(autouse=True)
def freeze_friday(freeze_time):
    freeze_time.freeze(FRIDAY)


def _setup_branch_protection(github: dict, pr: dict, min_required_approvals: int = 2):
    repo = pr["base"]["repo"]["name"]
    branch = pr["base"]["ref"]

    _setup_branch_protection_for_branch(github, repo, branch, min_required_approvals)


def _setup_branch_protection_for_branch(
    github: dict, repo: str, branch: str, min_required_approvals: int = 2
):
    branch_protection = make_branch_protection(min_required_approvals)
    github["branch_protection"][repo][branch] = branch_protection


parametrize_urgency = pytest.mark.parametrize(
    "urgency",
    [
        pytest.param(urgency, id=f"{urgency.label}-urgency")
        for urgency in (
            Urgency.CRITICAL,
            Urgency.HIGH,
            Urgency.MEDIUM,
            Urgency.LOW,
        )
    ],
)


# We don't need to test events list where the last
# event is "convert_to_draft" because drafted PRs
# are filtered out of the scenarios where a PR would
# be eligible for a ping based on urgency.
parametrize_possible_pingable_events = pytest.mark.parametrize(
    "events",
    [
        # PRs opened "ready for review" do not have a ready for review event.
        # This covers the most common case as most PRs will only have these
        # events. There are no events for actual PR reviews or comments as those
        # are in the "comments" and "reviews" feeds for the issue/PR
        pytest.param(
            ["labeled", "review_requested"],
            id="opened_ready_for_review",
        ),
        # PRs converted to a draft after being opened will have both convert and ready events
        pytest.param(
            [
                "labeled",
                "review_requested",
                "convert_to_draft",
                EventsConfig("ready_for_review", 1),
            ],
            id="opened_then_drafted_finally_ready",
        ),
        # A PR opened as a draft does not have a "convert_to_draft" event but does still have "ready_for_review"
        pytest.param(
            ["labeled", "review_requested", EventsConfig("ready_for_review", 2)],
            id="opened_as_draft_finally_ready",
        ),
        # PRs can have multiple ready for review events if converted to draft multiple times
        pytest.param(
            [
                "labeled",
                "review_requested",
                "convert_to_draft",
                EventsConfig("ready_for_review", 1),
                "convert_to_draft",
                "ready_for_review",
            ],
            id="opened_then_drafted_redrafted_finally_ready",
        ),
        # A PR opened as a draft can be set as ready for review and then redrafted.
        # A length of time greater than the lowest urgency window is set to pass between
        # the first ready_for_review event and the next event; this ensures that the
        # first ready_for_review event is definitely out of the urgency window. This
        # tests that the date of the most *recent* ready_for_review event is what is
        # used to determine if a PR should be pinged.
        pytest.param(
            [
                "labeled",
                "review_requested",
                EventsConfig("ready_for_review", 2),
                EventsConfig("convert_to_draft", Urgency.LOW.days * 2),
                EventsConfig("ready_for_review", 1),
            ],
            id="opened_as_draft_redrafted_finally_ready",
        ),
    ],
)


@parametrize_urgency
@parametrize_possible_pingable_events
def test_pings_past_due(github, urgency, events):
    past_due_pull = make_pull(urgency, old=True)
    past_due_pull["requested_reviewers"] = [
        make_requested_reviewer(f"reviewer-due-{i}") for i in range(2)
    ]
    not_due_pull = make_pull(urgency, old=False)
    not_due_pull["requested_reviewers"] = [
        make_requested_reviewer(f"reviewer-not-due-{i}") for i in range(2)
    ]
    old_but_not_due_pull = make_pull(urgency, old=True)
    old_but_not_due_pull["requested_reviewers"] = [
        make_requested_reviewer(f"reviewer-old-but-not-due-{i}") for i in range(2)
    ]

    for pr in [past_due_pull, not_due_pull, old_but_not_due_pull]:
        _setup_branch_protection(github, pr)

    github["pulls"] += [past_due_pull, not_due_pull, old_but_not_due_pull]
    github["pull_comments"][past_due_pull["number"]].append(
        make_pr_comment(is_reminder=False)
    )

    github["events"][past_due_pull["number"]] = make_urgent_events(urgency, events)
    github["events"][not_due_pull["number"]] = make_non_urgent_events(events)
    github["events"][
        old_but_not_due_pull["number"]
    ] = make_non_urgent_reviewable_events(events)

    post_reminders("not_set", dry_run=False)

    assert past_due_pull["number"] in github["posted_comments"]
    assert not_due_pull["number"] not in github["posted_comments"]
    assert old_but_not_due_pull["number"] not in github["posted_comments"]

    comments = github["posted_comments"][past_due_pull["number"]]
    for reviewer in past_due_pull["requested_reviewers"]:
        for comment in comments:
            assert f"@{reviewer['login']}" in comment


@parametrize_urgency
@parametrize_possible_pingable_events
def test_does_not_reping_past_due_if_reminder_is_current(github, urgency, events):
    past_due_pull = make_pull(urgency, old=True)
    past_due_pull["requested_reviewers"] = [
        make_requested_reviewer(f"reviewer-due-{i}") for i in range(2)
    ]
    not_due_pull = make_pull(urgency, old=False)
    not_due_pull["requested_reviewers"] = [
        make_requested_reviewer(f"reviewer-not-due-{i}") for i in range(2)
    ]
    old_but_not_due_pull = make_pull(urgency, old=True)
    old_but_not_due_pull["requested_reviewers"] = [
        make_requested_reviewer(f"reviewer-old-but-not-due-{i}") for i in range(2)
    ]

    for pr in [past_due_pull, not_due_pull, old_but_not_due_pull]:
        _setup_branch_protection(github, pr)

    github["pulls"] += [past_due_pull, not_due_pull, old_but_not_due_pull]
    github["pull_comments"][past_due_pull["number"]].append(
        make_current_pr_comment(past_due_pull)
    )

    github["events"][past_due_pull["number"]] = make_urgent_events(urgency, events)
    github["events"][not_due_pull["number"]] = make_non_urgent_events(events)
    github["events"][
        old_but_not_due_pull["number"]
    ] = make_non_urgent_reviewable_events(events)

    post_reminders("not_set", dry_run=False)

    assert past_due_pull["number"] not in github["posted_comments"]
    assert not_due_pull["number"] not in github["posted_comments"]
    assert old_but_not_due_pull["number"] not in github["posted_comments"]


@parametrize_urgency
@parametrize_possible_pingable_events
def test_does_reping_past_due_if_reminder_is_outdated(github, urgency, events):
    past_due_pull = make_pull(urgency, old=True)
    past_due_pull["requested_reviewers"] = [
        make_requested_reviewer(f"reviewer-due-{i}") for i in range(2)
    ]
    not_due_pull = make_pull(urgency, old=False)
    not_due_pull["requested_reviewers"] = [
        make_requested_reviewer(f"reviewer-not-due-{i}") for i in range(2)
    ]
    old_but_not_due_pull = make_pull(urgency, old=True)
    old_but_not_due_pull["requested_reviewers"] = [
        make_requested_reviewer(f"reviewer-old-but-not-due-{i}") for i in range(2)
    ]

    for pr in [past_due_pull, not_due_pull]:
        _setup_branch_protection(github, pr)

    github["pulls"] += [past_due_pull, not_due_pull]
    reminder_comment = make_outdated_pr_comment(past_due_pull)
    github["pull_comments"][past_due_pull["number"]].append(reminder_comment)

    github["events"][past_due_pull["number"]] = make_urgent_events(urgency, events)
    github["events"][not_due_pull["number"]] = make_non_urgent_events(events)
    github["events"][
        old_but_not_due_pull["number"]
    ] = make_non_urgent_reviewable_events(events)

    post_reminders("not_set", dry_run=False)

    assert past_due_pull["number"] in github["posted_comments"]
    assert not_due_pull["number"] not in github["posted_comments"]
    assert old_but_not_due_pull["number"] not in github["posted_comments"]

    assert reminder_comment["id"] in github["deleted_comments"]


UNAPPROVED_REVIEW_STATES = ("CHANGES_REQUESTED", "COMMENTED")


@parametrize_urgency
@pytest.mark.parametrize(
    "first_review_state",
    # None represents not having a review so we can test the
    # one review state.
    (None,) + UNAPPROVED_REVIEW_STATES,
)
@pytest.mark.parametrize(
    "second_review_state",
    # No none here otherwise we'd duplicate the single review states
    # and we don't need to test the "no review" state because that's
    # tested elsewhere.
    ("APPROVED",) + UNAPPROVED_REVIEW_STATES,
)
@pytest.mark.parametrize("base_branch", ("main", "not_main"))
@parametrize_possible_pingable_events
def test_does_ping_if_pr_has_less_than_min_required_approvals(
    github, urgency, first_review_state, second_review_state, base_branch, events
):
    reviews = [
        make_review(state)
        for state in (first_review_state, second_review_state)
        if state is not None
    ]
    past_due_pull = make_pull(urgency, old=True, base_branch=base_branch)
    past_due_pull["requested_reviewers"] = [
        make_requested_reviewer(f"reviewer-due-{i}") for i in range(2)
    ]

    # Always use `main` to exercise fallback for non-main branches
    _setup_branch_protection_for_branch(
        github,
        repo="openverse",
        branch="main",
        min_required_approvals=2,
    )

    github["pulls"] += [past_due_pull]
    github["pull_reviews"][past_due_pull["number"]] = reviews
    github["events"][past_due_pull["number"]] = make_urgent_events(urgency, events)

    post_reminders("not_set", dry_run=False)

    assert past_due_pull["number"] in github["posted_comments"]


@parametrize_urgency
@pytest.mark.parametrize(
    ("base_branch"),
    (
        "main",
        "not_main",  # should fallback to use `main`
    ),
)
@parametrize_possible_pingable_events
def test_does_not_ping_if_pr_has_min_required_approvals(
    github, urgency, base_branch, events
):
    past_due_pull = make_pull(urgency, old=True, base_branch=base_branch)
    past_due_pull["requested_reviewers"] = [
        make_requested_reviewer(f"reviewer-due-{i}") for i in range(2)
    ]

    min_required_approvals = 4

    # Always use `main` to exercise fallback for non-main branches
    _setup_branch_protection_for_branch(
        github,
        repo="openverse",
        branch="main",
        min_required_approvals=min_required_approvals,
    )

    github["pulls"] += [past_due_pull]
    github["pull_reviews"][past_due_pull["number"]] = [
        make_review("APPROVED"),
    ] * min_required_approvals
    github["events"][past_due_pull["number"]] = make_urgent_events(urgency, events)

    post_reminders("not_set", dry_run=False)

    assert past_due_pull["number"] not in github["posted_comments"]


@parametrize_urgency
@parametrize_possible_pingable_events
def test_does_not_ping_if_no_reviewers(github, urgency, events):
    past_due_pull = make_pull(urgency, old=True)
    past_due_pull["requested_reviewers"] = []
    not_due_pull = make_pull(urgency, old=False)
    not_due_pull["requested_reviewers"] = []
    old_but_not_due_pull = make_pull(urgency, old=True)

    github["pulls"] += [past_due_pull, not_due_pull, old_but_not_due_pull]
    github["pull_comments"][past_due_pull["number"]].append(
        make_pr_comment(is_reminder=False)
    )

    github["events"][past_due_pull["number"]] = make_urgent_events(urgency, events)
    github["events"][not_due_pull["number"]] = make_non_urgent_events(events)
    github["events"][
        old_but_not_due_pull["number"]
    ] = make_non_urgent_reviewable_events(events)

    for pr in [past_due_pull, not_due_pull]:
        _setup_branch_protection(github, pr)

    post_reminders("not_set", dry_run=False)

    assert past_due_pull["number"] not in github["posted_comments"]
    assert not_due_pull["number"] not in github["posted_comments"]
    assert old_but_not_due_pull["number"] not in github["posted_comments"]


@parametrize_urgency
# We cannot use the ``possible_pingable_events`` fixture
# because this test is only relevant for PRs that have
# ready for review events (i.e., were at one point drafts).
# Possible pingable events includes the one case where
# a PR would not have a ready for review event but still
# be eligible: PRs that were never drafts. As there's no
# easy way to combine parametrized fixtures or to abstract
# this without a great deal of displacement, it's easier
# to just copy the relevant cases.
@pytest.mark.parametrize(
    "events",
    (
        # PRs converted to a draft after being opened will have both convert and ready events
        (
            "labeled",
            "review_requested",
            "convert_to_draft",
            EventsConfig("ready_for_review", 1),
        ),
        # A PR opened as a draft does not have a "convert_to_draft" event but does still have "ready_for_review"
        ("labeled", "review_requested", EventsConfig("ready_for_review", 2)),
        # PRs can have multiple ready for review events if converted to draft multiple times
        (
            "labeled",
            "review_requested",
            "convert_to_draft",
            EventsConfig("ready_for_review", 1),
            "convert_to_draft",
            "ready_for_review",
        ),
        # A PR opened as a draft can be set as ready for review and then redrafted
        (
            "labeled",
            "review_requested",
            EventsConfig("ready_for_review", 2),
            EventsConfig("convert_to_draft", 1),
            EventsConfig("ready_for_review", 1),
        ),
    ),
)
def test_ignores_created_at_and_pings_if_urgent_ready_for_review_event_exists(
    github, urgency, events
):
    """
    Artificial case to confirm ready for review events are respected.

    This case never happens in reality because it's impossible to have an event
    that occurs before the creation of the PR. However, while the other tests
    show that pings happen for past due PRs and do not happen for
    PRs not past due, they don't definitely show that the ready_for_review
    event date is what marked the PR urgent.

    This test creates a PR with a created_at timestamp that by itself
    would _not_ cause the PR to be urgent. However, the PR's events
    list has a ready_for_review event
    """

    # old=False ensures the PR's created_at date will not
    # be the cause of it being eligible for a ping
    pull = make_pull(urgency, old=False)
    pull["requested_reviewers"] = [
        make_requested_reviewer(f"reviewer-due-{i}") for i in range(2)
    ]

    github["pulls"] += [pull]

    # Create urgent events to cause a ping
    github["events"][pull["number"]] = make_urgent_events(urgency, events)

    _setup_branch_protection(github, pull)

    post_reminders("not_set", dry_run=False)

    assert pull["number"] in github["posted_comments"]


def test_falls_back_to_main_on_multiple_branch_levels(
    github,
):
    # No need to parametrize this, only need to test the one case
    # Make branch protection rules for a branch one-off main
    github["branch_protection"]["openverse"]["non_main"] = {}
    past_due_pull = make_pull(Urgency.LOW, old=True, base_branch="not_main")
    past_due_pull["requested_reviewers"] = [
        make_requested_reviewer(f"reviewer-due-{i}") for i in range(2)
    ]

    min_required_approvals = 4

    # Always use `main` to exercise fallback for non-main branches
    _setup_branch_protection_for_branch(
        github,
        repo="openverse",
        branch="main",
        min_required_approvals=min_required_approvals,
    )

    github["pulls"] += [past_due_pull]
    github["pull_reviews"][past_due_pull["number"]] = [
        make_review("APPROVED"),
    ] * min_required_approvals
    github["events"][past_due_pull["number"]] = make_urgent_events(
        Urgency.LOW, ["review_requested"]
    )

    post_reminders("not_set", dry_run=False)

    assert past_due_pull["number"] not in github["posted_comments"]
