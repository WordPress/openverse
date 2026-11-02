from unittest import mock

from django.urls import reverse

import pytest

from api.admin.media_report import (
    ImageReportAdmin,
    _non_production_deferred,
    _production_deferred,
)
from api.admin.site import openverse_admin
from api.models import ImageReport


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


def test_media_id_escapes_media_representation():
    model_admin = ImageReportAdmin(ImageReport, openverse_admin)
    report = mock.MagicMock()
    report.media_obj.id = 1
    report.media_obj.__str__.return_value = "<b>Image</b>"

    html = model_admin.media_id(report)

    assert f'href="{reverse("admin:api_image_change", args=(1,))}"' in html
    assert "&lt;b&gt;Image&lt;/b&gt;" in html
    assert "<b>" not in html
