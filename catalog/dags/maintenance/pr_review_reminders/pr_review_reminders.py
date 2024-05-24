import datetime
import logging
from collections import defaultdict
from dataclasses import dataclass

from airflow.decorators import task
from requests import HTTPError

from common.github import GitHubAPI


logger = logging.getLogger(__name__)


REPOSITORIES = [
    "openverse",
    "openverse-infrastructure",
]
MAINTAINER_TEAM = "openverse-maintainers"
OPENVERSE_BOT = "openverse-bot"
NON_MAINTAINER_IGNORATIONS = {OPENVERSE_BOT, "renovate", "dependabot[bot]"}


class Urgency:
    @dataclass
    class Urgency:
        label: str
        days: int

    CRITICAL = Urgency("critical", 1)
    HIGH = Urgency("high", 2)
    CONTRIBUTOR = Urgency("contributor", 3)
    MEDIUM = Urgency("medium", 4)
    LOW = Urgency("low", 5)

    @classmethod
    def for_pr(cls, pr: dict, maintainers: set[str]) -> Urgency | None:
        # All contributor PRs should be treated as a special case
        if pr["user"]["login"] not in maintainers:
            return cls.CONTRIBUTOR

        priority_labels = [
            label["name"]
            for label in pr["labels"]
            if "priority" in label["name"].lower()
        ]
        if not priority_labels:
            logger.error(f"Found unlabeled PR ({pr['html_url']}). Skipping!")
            return None

        priority_label = priority_labels[0]

        if "critical" in priority_label:
            return cls.CRITICAL
        elif "high" in priority_label:
            return cls.HIGH
        elif "medium" in priority_label:
            return cls.MEDIUM
        elif "low" in priority_label:
            return cls.LOW


@dataclass
class ReviewDelta:
    urgency: Urgency.Urgency
    days: int


@task
def get_maintainers(github_pat: str) -> set[str]:
    gh = GitHubAPI(github_pat)
    maintainer_info = gh.get_team_members(MAINTAINER_TEAM)
    maintainers = {
        member["login"] for member in maintainer_info
    } ^ NON_MAINTAINER_IGNORATIONS
    return maintainers


def days_without_weekends(
    today: datetime.datetime, updated_at: datetime.datetime
) -> int:
    """
    Return the number of days between two dates, excluding weekends.

    Adapted from:
    <https://stackoverflow.com/a/3615984> CC BY-SA 2.5
    """
    if today.weekday() == 0 and (today - updated_at).days < 3:
        # shortcut mondays to 0 if last updated on the weekend
        return 0

    daygenerator = (
        updated_at + datetime.timedelta(x + 1) for x in range((today - updated_at).days)
    )
    return sum(1 for day in daygenerator if day.weekday() < 5)


def parse_gh_date(d) -> datetime.datetime:
    return datetime.datetime.fromisoformat(d.rstrip("Z"))


def get_urgency_if_urgent(
    gh: GitHubAPI, pr: dict, maintainers: set[str]
) -> ReviewDelta | None:
    events = gh.get_issue_events(base_repo_name(pr), pr["number"])
    ready_for_review_date = pr["created_at"]
    for event in reversed(events):
        # Find the latest "ready_for_review" event.
        # We don't need to check for or stop if we
        # find a draft event because drafted PRs are
        # already filtered out at this point. Any draft
        # events present in the events list would
        # be further back in time than the latest
        # (and therefore relevant) ready_for_review
        # event will appear before we reach any
        # draft events.
        if event["event"] == "ready_for_review":
            ready_for_review_date = event["created_at"]
            break

    urgency_base_date = parse_gh_date(ready_for_review_date)
    today = datetime.datetime.now()
    pr_urgency = Urgency.for_pr(pr, maintainers)
    if pr_urgency is None:
        return None

    days = days_without_weekends(today, urgency_base_date)

    return ReviewDelta(pr_urgency, days) if days >= pr_urgency.days else None


COMMENT_MARKER = (
    "This reminder is being automatically generated due to the urgency configuration."
)


COMMENT_TEMPLATE = (
    """\
Based on the {urgency_label} urgency of this PR, the following reviewers are being \
gently reminded to review this PR:

{user_logins}
"""
    f"{COMMENT_MARKER}"
    """

Excluding weekend[^1] days, this PR was ready for review {days_ready_for_review} \
day(s) ago. PRs labelled with {urgency_label} urgency are expected to be reviewed \
within {urgency_days} weekday(s)[^2].

@{pr_author}, if this PR is not ready for a review, please draft it to \
prevent reviewers from getting further unnecessary pings.

[^1]: Specifically, Saturday and Sunday.
[^2]: For the purpose of these reminders we treat Monday - Friday as weekdays. \
Please note that the operation that generates these reminders runs at midnight \
UTC on Monday - Friday. This means that depending on your timezone, \
you may be pinged outside of the expected range.
"""
)


def build_comment(review_delta: ReviewDelta, pr: dict):
    user_handles = [f"@{req['login']}" for req in pr["requested_reviewers"]]
    return user_handles, COMMENT_TEMPLATE.format(
        urgency_label=review_delta.urgency.label,
        urgency_days=review_delta.urgency.days,
        user_logins="\n".join(user_handles),
        days_ready_for_review=review_delta.days,
        pr_author=pr["user"]["login"],
    )


def base_repo_name(pr: dict):
    return pr["base"]["repo"]["name"]


_BRANCH_PROTECTION_CACHE = defaultdict(dict)


def get_branch_protection(gh: GitHubAPI, repo: str, branch_name: str) -> dict:
    if branch_name not in _BRANCH_PROTECTION_CACHE[repo]:
        _BRANCH_PROTECTION_CACHE[repo][branch_name] = gh.get_branch_protection(
            repo, branch_name
        )

    return _BRANCH_PROTECTION_CACHE[repo][branch_name]


def get_min_required_approvals(gh: GitHubAPI, pr: dict) -> int:
    repo = base_repo_name(pr)
    branch_name = pr["base"]["ref"]

    try:
        branch_protection_rules = get_branch_protection(gh, repo, branch_name)
    except HTTPError as e:
        # If the base branch does not have protection rules, the request
        # above will 404. In that case, fall back to the rules for `main`
        # as a safe default.
        if e.response is not None and e.response.status_code == 404:
            branch_protection_rules = get_branch_protection(gh, repo, "main")
        else:
            raise e

    if "required_pull_request_reviews" not in branch_protection_rules:
        # This can happen in the rare case where a PR is multiple branches deep,
        # e.g. it depends on a branch which depends on a branch which depends on main.
        # In that case, default to the rules for `main` as a safe default.
        branch_protection_rules = get_branch_protection(gh, repo, "main")

    return branch_protection_rules["required_pull_request_reviews"][
        "required_approving_review_count"
    ]


@task(task_id="pr_review_reminder_operator")
def post_reminders(maintainers: set[str], github_pat: str, dry_run: bool):
    gh = GitHubAPI(github_pat)

    open_prs = []
    for repo in REPOSITORIES:
        open_prs += [pr for pr in gh.get_open_prs(repo) if not pr["draft"]]

    urgent_prs = []
    for pr in open_prs:
        review_delta = get_urgency_if_urgent(gh, pr, maintainers)
        if review_delta:
            urgent_prs.append((pr, review_delta))

    to_ping = []
    for pr, review_delta in urgent_prs:
        repo = base_repo_name(pr)
        previous_comments = gh.get_issue_comments(repo, pr["number"])

        reminder_comments = [
            comment
            for comment in previous_comments
            if (
                comment["user"]["login"] == OPENVERSE_BOT
                and COMMENT_MARKER in comment["body"]
            )
        ]

        # While this version of the DAG will only ever allow a single
        # current reminder comment to exist, we still need to split this out
        # so that comments left by previous iterations will still get picked
        # up, read as current or not, and also recorded for deletion by the
        # script so that the final step can delete all but the most recently
        # left reminder comment.
        current_reminder = next(
            iter(
                [
                    r
                    for r in reminder_comments
                    if parse_gh_date(r["created_at"]) > parse_gh_date(pr["updated_at"])
                ]
            ),
            None,
        )

        if current_reminder:
            continue

        if pr["requested_reviewers"] == []:
            # no requested reviewers to ping, maybe in the future we ping
            # the PR author or the whole openverse maintainers team?
            continue

        existing_reviews = gh.get_pull_reviews(base_repo_name(pr), pr["number"])

        approved_reviews = [r for r in existing_reviews if r["state"] == "APPROVED"]
        if len(approved_reviews) >= get_min_required_approvals(gh, pr):
            # if PR already has sufficient reviews to be merged, do not ping
            # the requested reviewers.
            continue

        to_ping.append(
            (
                pr,
                review_delta,
                reminder_comments,
            )
        )

    for pr, review_delta, previous_comments in to_ping:
        user_handles, comment_body = build_comment(review_delta, pr)

        logger.info(f"Pinging {', '.join(user_handles)} to review {pr['title']}")
        if not dry_run:
            gh.post_issue_comment(base_repo_name(pr), pr["number"], comment_body)
            for comment in previous_comments:
                gh.delete_issue_comment(base_repo_name(pr), comment["id"])

    if dry_run:
        logger.info(
            "This was a dry run. None of the pings listed above were actually sent."
        )
