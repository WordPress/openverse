from unittest import mock

import pytest
import requests
from airflow.models import TaskInstance
from pendulum import datetime
from providers import factory_utils

from tests.dags.common.test_resources import fake_provider_module
from tests.dags.common.test_resources.fake_provider_data_ingester import (
    FakeDataIngester,
)


@pytest.fixture
def ti_mock() -> TaskInstance:
    return mock.MagicMock(spec=TaskInstance)


@pytest.fixture
def internal_func_mock():
    """
    This mock, along with the value, get handed into the provided function.
    For fake_provider_module.main, the mock will be called with the provided value.
    """
    return mock.MagicMock()


fdi = FakeDataIngester()


def _set_up_ingester(mock_func, value):
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


@pytest.mark.parametrize(
    "func, media_types, stores",
    [
        # Happy path
        (fake_provider_module.main, ["image"], [fake_provider_module.image_store]),
        # Empty case, no media types provided
        (fake_provider_module.main, [], []),
        # Provided function doesn't have a store at the module level
        pytest.param(
            requests.get,
            ["image"],
            [None],
            marks=pytest.mark.raises(
                exception=ValueError, match="Expected stores in .*? were missing.*"
            ),
        ),
        # Provided function doesn't have all specified stores
        pytest.param(
            fake_provider_module.main,
            ["image", "other"],
            [None, None],
            marks=pytest.mark.raises(
                exception=ValueError, match="Expected stores in .*? were missing.*"
            ),
        ),
    ],
)
def test_load_provider_script(func, media_types, stores):
    actual_stores = factory_utils._load_provider_script_stores(
        func,
        media_types,
    )
    assert actual_stores == dict(zip(media_types, stores))


@pytest.mark.parametrize(
    "func, media_types, stores",
    [
        ##################################################
        # Function-based
        ##################################################
        # Happy path
        (fake_provider_module.main, ["image"], [fake_provider_module.image_store]),
        # Multiple types
        (
            fake_provider_module.main,
            ["image", "audio"],
            [fake_provider_module.image_store, fake_provider_module.audio_store],
        ),
        # Empty case, no media types provided
        (fake_provider_module.main, [], []),
        ##################################################
        # Class-based
        ##################################################
        # Happy path
        (FakeDataIngesterClass, ["image", "audio"], list(fdi.media_stores.values())),
        # No media types provided, ingester class still supplies stores
        (FakeDataIngesterClass, 2, list(fdi.media_stores.values())),
    ],
)
def test_generate_tsv_filenames(func, media_types, stores, ti_mock, internal_func_mock):
    value = 42
    factory_utils.generate_tsv_filenames(
        func,
        media_types,
        ti_mock,
        args=[internal_func_mock, value],
    )
    # There should be one call to xcom_push for each provided store
    # If the media_types value is an int, use that for the expected xcoms test
    expected_xcoms = len(media_types) if isinstance(media_types, list) else media_types
    actual_xcoms = ti_mock.xcom_push.call_count
    assert (
        actual_xcoms == expected_xcoms
    ), f"Expected {expected_xcoms} XComs but {actual_xcoms} pushed"
    for args, store in zip(ti_mock.xcom_push.mock_calls[:-1], stores):
        assert args.kwargs["value"] == store.output_path

    # Check that the function itself was NOT called with the provided args
    internal_func_mock.assert_not_called()


@pytest.mark.parametrize(
    "func, media_types, tsv_filenames, stores",
    [
        ##################################################
        # Function-based
        ##################################################
        # Happy path
        (
            fake_provider_module.main,
            ["image"],
            ["image_file_000.tsv"],
            [fake_provider_module.image_store],
        ),
        # Multiple types
        (
            fake_provider_module.main,
            ["image", "audio"],
            ["image_file_000.tsv", "audio_file_111.tsv"],
            [fake_provider_module.image_store, fake_provider_module.audio_store],
        ),
        # Empty case, no media types provided
        (fake_provider_module.main, [], [], []),
        # Fails if a mismatched # of items is provided
        pytest.param(
            fake_provider_module.main,
            ["image", "other"],
            ["file1.tsv"],
            [fake_provider_module.image_store, fake_provider_module.audio_store],
            marks=pytest.mark.raises(
                exception=ValueError,
                match="Provided media types and TSV filenames don't match.*",
            ),
        ),
        pytest.param(
            fake_provider_module.main,
            ["image"],
            ["file1.tsv", "file2.tsv"],
            [fake_provider_module.image_store],
            marks=pytest.mark.raises(
                exception=ValueError,
                match="Provided media types and TSV filenames don't match.*",
            ),
        ),
        ##################################################
        # Class-based
        ##################################################
        # Happy path
        (
            FakeDataIngesterClass,
            ["image", "audio"],
            ["image_file_000.tsv", "audio_file_111.tsv"],
            list(fdi.media_stores.values()),
        ),
    ],
)
def test_pull_media_wrapper(
    func, media_types, tsv_filenames, stores, ti_mock, internal_func_mock
):
    value = 42
    factory_utils.pull_media_wrapper(
        func,
        media_types,
        tsv_filenames,
        ti_mock,
        args=[internal_func_mock, value],
    )
    # We should have one XCom push for duration
    assert ti_mock.xcom_push.call_count == 1
    # Check that the duration was reported
    assert ti_mock.xcom_push.mock_calls[0].kwargs["key"] == "duration"
    # Check that the output paths for the stores were changed to the provided filenames
    for filename, store in zip(tsv_filenames, stores):
        assert store.output_path == filename

    # Check that the function itself was called with the provided args
    internal_func_mock.assert_called_once_with(value)


@pytest.mark.parametrize(
    "schedule_interval, expected",
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
def test_date_partition_for_prefix(schedule_interval, expected):
    actual = factory_utils.date_partition_for_prefix(
        schedule_interval,
        datetime(2022, 2, 3),
    )
    assert actual == expected
