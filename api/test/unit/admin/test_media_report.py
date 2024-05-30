from unittest import mock

import pytest

from api.admin.media_report import _non_production_deferred, _production_deferred


@pytest.mark.parametrize(
    "values, environment, prod_expected, non_prod_expected",
    [
        ([1, 2, 3], "local", (1, 2, 3), ()),
        ([1, 2, 3], "production", (), (1, 2, 3)),
        ([], "local", (), ()),
        ([], "production", (), ()),
    ],
)
def test_production_deferred(values, environment, prod_expected, non_prod_expected):
    with mock.patch("api.admin.media_report.settings") as mock_settings:
        mock_settings.ENVIRONMENT = environment
        prod_deferred = _production_deferred(*values)
        non_prod_deferred = _non_production_deferred(*values)
    assert prod_deferred == prod_expected
    assert non_prod_deferred == non_prod_expected
