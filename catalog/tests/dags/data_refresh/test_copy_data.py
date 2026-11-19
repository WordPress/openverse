import json
import logging

import pytest

from common.constants import PRODUCTION
from data_refresh.copy_data import DEFAULT_DATA_REFRESH_LIMIT, get_record_limit


logger = logging.getLogger(__name__)


@pytest.mark.parametrize("configured_limit", [None, 0, 10, 10_000])
def test_get_record_limit_always_respects_configured_limit(
    configured_limit, monkeypatch
):
    monkeypatch.setenv("AIRFLOW_VAR_DATA_REFRESH_LIMIT", json.dumps(configured_limit))
    monkeypatch.setenv("AIRFLOW_VAR_ENVIRONMENT", PRODUCTION)

    assert get_record_limit.function() == configured_limit


@pytest.mark.parametrize(
    "environment, expected_limit",
    [
        (PRODUCTION, None),
        ("local", DEFAULT_DATA_REFRESH_LIMIT),
    ],
)
def test_get_record_limit_defaults_according_to_environment(
    environment, expected_limit, monkeypatch
):
    monkeypatch.delenv("AIRFLOW_VAR_DATA_REFRESH_LIMIT", raising=False)
    monkeypatch.setenv("AIRFLOW_VAR_ENVIRONMENT", environment)

    assert get_record_limit.function() == expected_limit
