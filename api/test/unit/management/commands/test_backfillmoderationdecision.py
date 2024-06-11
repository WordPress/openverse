from io import StringIO

from django.core.management import call_command

import pytest

from api.constants.moderation import DecisionAction
from api.models import (
    DEINDEXED,
    DMCA,
    MATURE,
    MATURE_FILTERED,
    NO_ACTION,
    OTHER,
    AudioDecision,
    AudioDecisionThrough,
    ImageDecision,
    ImageDecisionThrough,
)
from test.factory.models.audio import AudioReportFactory
from test.factory.models.image import ImageReportFactory
from test.factory.models.oauth2 import UserFactory


def call_cmd(**options):
    out = StringIO()
    err = StringIO()
    call_command(
        "backfillmoderationdecision",
        **options,
        stdout=out,
        stderr=err,
    )
    res = out.getvalue(), err.getvalue()
    print(res)

    return res


def make_reports(media_type, reason: str, status: str, count: int = 1):
    if media_type == "audio":
        return AudioReportFactory.create_batch(count, status=status, reason=reason)
    else:
        return ImageReportFactory.create_batch(count, status=status, reason=reason)


@pytest.mark.parametrize(
    ("reason", "status", "expected_action"),
    (
        (MATURE, MATURE_FILTERED, DecisionAction.MARKED_SENSITIVE),
        (DMCA, MATURE_FILTERED, DecisionAction.MARKED_SENSITIVE),
        (OTHER, MATURE_FILTERED, DecisionAction.MARKED_SENSITIVE),
        (MATURE, NO_ACTION, DecisionAction.REJECTED_REPORTS),
        (DMCA, NO_ACTION, DecisionAction.REJECTED_REPORTS),
        (OTHER, NO_ACTION, DecisionAction.REJECTED_REPORTS),
        (MATURE, DEINDEXED, DecisionAction.DEINDEXED_SENSITIVE),
        (DMCA, DEINDEXED, DecisionAction.DEINDEXED_COPYRIGHT),
        (OTHER, DEINDEXED, DecisionAction.DEINDEXED_SENSITIVE),
    ),
)
@pytest.mark.parametrize(("media_type"), ("image", "audio"))
@pytest.mark.django_db
def test_create_moderation_decision_for_reports(
    media_type, reason, status, expected_action
):
    username = "opener"
    UserFactory.create(username=username)

    report = make_reports(media_type=media_type, reason=reason, status=status)[0]

    out, err = call_cmd(dry_run=False, media_type=media_type, moderator=username)

    MediaDecision = ImageDecision if media_type == "image" else AudioDecision
    MediaDecisionThrough = (
        ImageDecisionThrough if media_type == "image" else AudioDecisionThrough
    )
    assert MediaDecision.objects.count() == 1
    assert f"Created 1 {media_type} moderation decisions from existing reports." in out

    decision = MediaDecision.objects.first()
    assert decision.media_objs.count() == 1
    assert decision.action == expected_action
    assert decision.moderator.username == username

    decision_through = MediaDecisionThrough.objects.first()
    assert decision_through.media_obj == report.media_obj
    assert decision_through.decision == decision


@pytest.mark.django_db
def test_catch_user_exception():
    make_reports(media_type="image", reason=MATURE, status=MATURE_FILTERED)
    _, err = call_cmd(dry_run=False, moderator="nonexistent")

    assert "User 'nonexistent' not found." in err
