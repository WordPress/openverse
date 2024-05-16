from unittest import mock

import pytest

from api.admin.media_report import _production_deferred


@pytest.mark.parametrize(
    "values, environment, expected",
    [
        ([1, 2, 3], "local", (1, 2, 3)),
        ([1, 2, 3], "production", ()),
        ([], "local", ()),
        ([], "production", ()),
    ],
)
def test_production_deferred(values, environment, expected):
    with mock.patch("api.admin.media_report.settings") as mock_settings:
        mock_settings.ENVIRONMENT = environment
        actual = _production_deferred(*values)
    assert actual == expected
