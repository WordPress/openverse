from datetime import datetime
from unittest import mock

import pytest
from airflow.models import DagRun, TaskInstance
from tests.dags.common.test_resources.fake_provider_data_ingester import (
    FakeDataIngester,
)

from providers import factory_utils


@pytest.fixture
def ti_mock() -> TaskInstance:
    return mock.MagicMock(spec=TaskInstance)


@pytest.fixture
def dagrun_mock() -> DagRun:
    return mock.MagicMock(spec=DagRun)


@pytest.fixture
def internal_func_mock():
    """
    Get an empty ``MagicMock`` instance.

    This mock, along with the value, get handed into the provided function.
    For fake_provider_module.main, the mock will be called with the provided value.
    """
    return mock.MagicMock()


fdi = FakeDataIngester()


def _set_up_ingester(mock_conf, mock_dag_id, mock_func, value):
    """
    Set up ingest records as a proxy for calling the mock function, then return
    the instance. This is necessary because the args are only handed in during
    instance initialization, *not* while calling ingest_records.

    This also effectively checks that ingest_records does not receive the `*args` passed
    into pull_media_wrapper, since this lambda doesn't accept any arguments!
    """
    fdi.ingest_records = lambda: mock_func(value)
    return fdi


# We have to pass a class down into the various functions, but we want to access
# entities inside the produced object (e.g. stores) in order to test that they
# were altered correctly. Best way to do that is to set up a mock that just returns
# the class when called.
FakeDataIngesterClass = mock.MagicMock()
FakeDataIngesterClass.__name__ = "FakeDataIngesterClass"
FakeDataIngesterClass.side_effect = _set_up_ingester


def test_pull_media_wrapper(ti_mock, dagrun_mock, internal_func_mock):
    value = 42

    factory_utils.pull_media_wrapper(
        FakeDataIngesterClass,
        ["image", "audio"],
        ti_mock,
        dagrun_mock,
        args=[internal_func_mock, value],
    )
    # We should have one XCom push for duration, and two for the tsv filenames
    assert ti_mock.xcom_push.call_count == 3
    push_calls = ti_mock.xcom_push.mock_calls
    # Check that the tsv filenames were reported
    assert push_calls[0].kwargs["key"] == "image_tsv"
    assert push_calls[1].kwargs["key"] == "audio_tsv"
    # Check that the duration was reported
    assert push_calls[2].kwargs["key"] == "duration"

    # Check that the function itself was called with the provided args
    internal_func_mock.assert_called_once_with(value)


def test_pull_media_wrapper_checks_media_types(ti_mock, dagrun_mock):
    value = 42
    # The FakeDataIngester class has stores for `audio` and `image`. Calling
    # `pull_media_wrapper` with only `image` will raise an error due to the
    # mismatch in media types.
    error_message = (
        "Provided media types and media stores don't match: "
        r"media_types=\['image'\] stores=\['image', 'audio'\]"
    )
    with pytest.raises(ValueError, match=error_message):
        factory_utils.pull_media_wrapper(
            FakeDataIngesterClass,
            ["image"],  # Only pass in `image` for media_types
            ti_mock,
            dagrun_mock,
            args=[internal_func_mock, value],
        )

    # We should fail early with no XCom pushes
    assert ti_mock.xcom_push.call_count == 0


def test_pull_media_wrapper_always_pushes_duration(ti_mock, dagrun_mock):
    # Force `ingest_records` to throw an error, and verify that duration
    # is still reported to XComs.
    error_message = "Whoops!"

    def _raise_an_error(text):
        raise ValueError(text)

    with pytest.raises(ValueError, match=error_message):
        factory_utils.pull_media_wrapper(
            FakeDataIngesterClass,
            ["image", "audio"],
            ti_mock,
            dagrun_mock,
            args=[_raise_an_error, error_message],
        )
    # We should have one XCom push for duration, and two for the tsv filenames
    assert ti_mock.xcom_push.call_count == 3
    push_calls = ti_mock.xcom_push.mock_calls
    # Check that the tsv was reported for each media type
    assert push_calls[0].kwargs["key"] == "image_tsv"
    assert push_calls[1].kwargs["key"] == "audio_tsv"
    # Check that the duration was reported
    assert push_calls[2].kwargs["key"] == "duration"
    # Check that duration was *not* None (it should always be recorded)
    duration = push_calls[2].kwargs["value"]
    assert duration is not None
    assert duration > 0


# Set up parametrizations for the schedule and reingestion_date,
# which result in different components of the path
@pytest.mark.parametrize(
    "schedule, expected_schedule_prefix",
    [
        # Hourly should have year/month/day
        ("@hourly", "year=2022/month=02/day=03"),
        ("0 * * * *", "year=2022/month=02/day=03"),
        # Daily should only have year/month
        ("@daily", "year=2022/month=02"),
        ("0 0 * * *", "year=2022/month=02"),
        # Everything else is year only
        ("@weekly", "year=2022"),
        ("@monthly", "year=2022"),
        ("@quarterly", "year=2022"),
        ("@yearly", "year=2022"),
        ("0 */5 * * *", "year=2022"),
        ("🪄", "year=2022"),
        (None, "year=2022"),
    ],
)
@pytest.mark.parametrize(
    "reingestion_date, expected_reingestion_prefix",
    [
        # No reingestion date provided
        (None, ""),
        ("2022-01-01", "/reingestion=2022-01-01"),
    ],
)
def test_date_partition_for_prefix(
    schedule,
    expected_schedule_prefix,
    reingestion_date,
    expected_reingestion_prefix,
):
    actual = factory_utils.date_partition_for_prefix(
        schedule, datetime(2022, 2, 3), reingestion_date
    )
    assert actual == expected_schedule_prefix + expected_reingestion_prefix
