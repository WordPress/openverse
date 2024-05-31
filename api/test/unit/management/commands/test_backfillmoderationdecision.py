from io import StringIO
import pytest

from django.core.management import call_command

from api.models import AudioDecision, ImageDecision
from api.models import DMCA, MATURE, OTHER, MATURE_FILTERED, NO_ACTION, DEINDEXED
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
        AudioReportFactory.create_batch(count, status=status, reason=reason)
    else:
        ImageReportFactory.create_batch(count, status=status, reason=reason)

@pytest.mark.parametrize(
    ("reason", "status", "expected_action"),
    (
        (MATURE, MATURE_FILTERED, "confirmed_sensitive"),
        (DMCA, MATURE_FILTERED, "confirmed_sensitive"),
        (OTHER, MATURE_FILTERED, "confirmed_sensitive"),
        (MATURE, NO_ACTION, "rejected_reports"),
        (DMCA, NO_ACTION, "rejected_reports"),
        (OTHER, NO_ACTION, "rejected_reports"),
        (MATURE, DEINDEXED, "deindexed_sensitive"),
        (DMCA, DEINDEXED, "deindexed_copyright"),
        (OTHER, DEINDEXED, "deindexed_sensitive"),
    )
)
@pytest.mark.parametrize(("media_type"), ("image", "audio"))
@pytest.mark.django_db
def test_create_moderation_decision_for_reports(media_type, reason, status, expected_action):
    username = "opener"
    UserFactory.create(username=username)

    make_reports(media_type=media_type, reason=reason, status=status)

    out , err = call_cmd(dry_run=False, media_type=media_type, moderator=username)

    MediaDecision = ImageDecision if media_type == "image" else AudioDecision
    assert MediaDecision.objects.count() == 1
    assert f"Created 1 {media_type} moderation decisions from existing reports." in out

    decision = MediaDecision.objects.first()
    assert decision.action == expected_action
    assert decision.moderator.username == username


@pytest.mark.django_db
def test_catch_user_exception():
    make_reports(media_type="image", reason=MATURE, status=MATURE_FILTERED)
    _, err = call_cmd(dry_run=False, moderator="nonexistent")

    assert "User 'nonexistent' not found." in err