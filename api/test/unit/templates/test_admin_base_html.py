from django.shortcuts import resolve_url
from django.test.client import RequestFactory

import pytest

from api.admin.site import openverse_admin


class MockUser:
    is_active = True
    is_staff = True
    pk = 1

    def has_perm(self, *args):
        return True

    def has_module_perms(self, *args):
        return True


@pytest.mark.parametrize(
    "environment_value, should_be_present",
    [
        ("staging", True),
        ("local", True),
        ("production", False),
    ],
)
def test_admin_base_html_renders_message(environment_value, should_be_present, db):
    url = resolve_url("admin:index")
    request = RequestFactory().get(url)
    request.user = MockUser()

    index = openverse_admin.index(request)
    index.context_data["ENVIRONMENT"] = environment_value
    html = index.rendered_content

    assert (
        "Next staging database restore will occur in" in html
    ) == should_be_present, (
        "Rendered message about staging database restore was missing or "
        "incorrectly present in Admin UI"
    )
