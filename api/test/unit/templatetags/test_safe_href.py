from django.template import Context, Template
from django.template.loader import render_to_string

import pytest

from api.models import Image


@pytest.mark.parametrize(
    "url, expected",
    [
        ("https://example.com/a", "https://example.com/a"),
        ("example.com/a", "https://example.com/a"),
        ("javascript:void(0)", ""),
        (None, ""),
    ],
)
def test_safe_href_filter(url, expected):
    rendered = Template("{% load safe_href %}{{ url|safe_href }}").render(
        Context({"url": url})
    )
    assert rendered == expected


def test_media_report_attribution_drops_unsafe_links():
    media_obj = Image(
        title="A title",
        creator="A creator",
        url="javascript:void(0)",
        creator_url="javascript:void(1)",
        license="by",
        license_version="4.0",
    )

    rendered = render_to_string(
        "admin/api/media_report/attribution.html",
        {"media_obj": media_obj, "license": "CC BY 4.0"},
    )

    assert "javascript:" not in rendered
    assert "<a " not in rendered
    assert "A title" in rendered
    assert "A creator" in rendered


def test_media_report_attribution_keeps_safe_links():
    media_obj = Image(
        title="A title",
        creator="A creator",
        url="example.com/a",
        creator_url="https://example.com/jane",
        license="by",
        license_version="4.0",
    )

    rendered = render_to_string(
        "admin/api/media_report/attribution.html",
        {"media_obj": media_obj, "license": "CC BY 4.0"},
    )

    assert '<a href="https://example.com/a">A title</a>' in rendered
    assert '<a href="https://example.com/jane">A creator</a>' in rendered
