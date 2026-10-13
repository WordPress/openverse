import pytest

from api.utils.sentry import FILTERED, make_sensitive_value_scrubber


def test_redacts_hostname_anywhere_in_a_nested_event():
    scrub = make_sensitive_value_scrubber(["db.internal.example.com"])
    event = {
        "message": "could not connect to db.internal.example.com:5432",
        "breadcrumbs": {
            "values": [{"message": "SELECT 1 -- db.internal.example.com"}],
        },
        "extra": {"hosts": ("db.internal.example.com", "unrelated-host")},
    }

    scrubbed = scrub(event)

    assert "db.internal.example.com" not in repr(scrubbed)
    assert FILTERED in scrubbed["message"]
    assert scrubbed["breadcrumbs"]["values"][0]["message"].endswith(FILTERED)
    # unrelated values are left untouched (and tuples stay tuples)
    assert scrubbed["extra"]["hosts"] == (FILTERED, "unrelated-host")


@pytest.mark.parametrize("hostname", ["", "localhost", "127.0.0.1", "::1"])
def test_ignores_non_sensitive_default_hosts(hostname):
    scrub = make_sensitive_value_scrubber([hostname])
    event = {"message": f"connected to {hostname}"}

    # nothing to redact, so the event is returned unchanged
    assert scrub(event) is event


def test_returns_event_unchanged_when_no_hostnames_given():
    scrub = make_sensitive_value_scrubber([])
    event = {"message": "hello"}

    assert scrub(event) is event


def test_redacts_longer_overlapping_hostname_first():
    scrub = make_sensitive_value_scrubber(["db.example.com", "replica.db.example.com"])
    event = {"message": "replica.db.example.com and db.example.com"}

    scrubbed = scrub(event)

    assert "example.com" not in scrubbed["message"]
    assert scrubbed["message"] == f"{FILTERED} and {FILTERED}"
