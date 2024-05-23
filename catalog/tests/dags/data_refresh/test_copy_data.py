import logging
from unittest import mock

import pytest

from common.constants import PRODUCTION
from data_refresh.copy_data import DEFAULT_DATA_REFRESH_LIMIT, get_record_limit


logger = logging.getLogger(__name__)


@pytest.mark.parametrize("configured_limit", [None, 0, 10, 10_000])
def test_get_record_limit_always_respects_configured_limit(configured_limit):
    with mock.patch("data_refresh.copy_data.Variable") as MockVariable:
        # Mock the calls to Variable.get, in order
        MockVariable.get.side_effect = [
            configured_limit,
            # Mock is not called a second time to get the environment,
            # because configured_limit is returned immediately
        ]

        actual_limit = get_record_limit.function()
        assert actual_limit == configured_limit


@pytest.mark.parametrize(
    "environment, expected_limit",
    [
        (PRODUCTION, None),
        ("local", DEFAULT_DATA_REFRESH_LIMIT),
        ("foo", DEFAULT_DATA_REFRESH_LIMIT),
    ],
)
def test_get_record_limit_defaults_accoring_to_environment(environment, expected_limit):
    with mock.patch("data_refresh.copy_data.Variable") as MockVariable:
        # Mock the calls to Variable.get, in order
        MockVariable.get.side_effect = [
            # Raise KeyError when trying to get the configured limit,
            # simulating the variable not being defined
            KeyError,
            # Return the environment on the second call
            environment,
        ]

        actual_limit = get_record_limit.function()
        assert actual_limit == expected_limit
