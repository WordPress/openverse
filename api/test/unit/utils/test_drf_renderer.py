from rest_framework.request import Request
from rest_framework.views import APIView

import pytest

from api.utils.drf_renderer import BrowsableAPIRendererWithoutForms


@pytest.fixture
def api_request(request_factory):
    return request_factory.get("/")


@pytest.fixture
def view():
    return APIView.as_view()


@pytest.fixture
def response(view, api_request):
    return view(api_request)


def test_without_forms_renderer_context_should_not_show_edit_forms(
    api_request, response
):
    """
    See https://github.com/encode/django-rest-framework/blob/master/tests/test_renderers.py
    for example of test setup.
    """
    cls = BrowsableAPIRendererWithoutForms()

    parent_context = {
        "view": APIView(),
        "request": Request(api_request),
        "response": response,
    }

    ctx = cls.get_context({}, "text/html", parent_context)

    assert ctx["display_edit_forms"] is False


parametrize_methods = pytest.mark.parametrize(
    "method", ("GET", "PUT", "POST", "DELETE", "OPTIONS")
)


@parametrize_methods
def test_without_forms_renderer_show_form_for_method_returns_false(
    method, api_request, view
):
    cls = BrowsableAPIRendererWithoutForms()

    assert cls.show_form_for_method(view, method, api_request, None) is False


@parametrize_methods
def test_without_forms_renderer_get_rendered_html_form_empty(method, api_request, view):
    cls = BrowsableAPIRendererWithoutForms()

    data = {}

    assert cls.get_rendered_html_form(data, view, method, api_request) == ""
