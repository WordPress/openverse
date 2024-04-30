import smtplib
from io import StringIO

from django.core.management import call_command

import pytest

from test.factory.models.oauth2 import (
    OAuth2VerificationFactory,
)


command_module_path = "api.management.commands.sendapimoveannouncement"


@pytest.fixture
def captured_emails(monkeypatch) -> list[str]:
    captured = []

    def send_mail(*args, **kwargs):
        captured.extend(kwargs["recipient_list"])

    monkeypatch.setattr(f"{command_module_path}.send_mail", send_mail)

    yield captured


@pytest.fixture
def failed_emails(monkeypatch) -> list[str]:
    failed = []

    def send_mail(*args, **kwargs):
        failed.extend(
            kwargs["recipient_list"],
        )
        raise smtplib.SMTPAuthenticationError(1, "beep boop bad password")

    monkeypatch.setattr(f"{command_module_path}.send_mail", send_mail)

    yield failed


def call_cmd(**options):
    out = StringIO()
    err = StringIO()
    options.update(stdout=out, stderr=err)
    call_command("sendapimoveannouncement", **options)

    res = out.getvalue(), err.getvalue()
    print(res)

    return res


def make_emails(count: int, *, verified: bool):
    verifications = OAuth2VerificationFactory.create_batch(
        count, associated_application__verified=verified
    )
    return [v.email for v in verifications]


@pytest.mark.django_db
def test_should_not_resend_for_already_sent(redis, captured_emails):
    emails = make_emails(10, verified=True)
    for email in emails:
        redis.sadd("apimoveannouncement:processed", email)

    call_cmd(dry_run=False)
    assert captured_emails == []


@pytest.mark.django_db
def test_should_not_count_email_as_sent_if_failed(failed_emails, redis):
    emails = make_emails(1, verified=True)
    call_cmd(dry_run=False)
    assert failed_emails == emails

    for email in emails:
        assert not (redis.sismember("apimoveannouncement:processed", email))


@pytest.mark.django_db
def test_should_not_send_to_unverified_emails(captured_emails):
    make_emails(10, verified=False)

    call_cmd(dry_run=False)
    assert len(captured_emails) == 0
