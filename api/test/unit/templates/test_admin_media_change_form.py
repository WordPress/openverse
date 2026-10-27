import re

from django.template.loader import get_template


HTML_STRING_SINKS = re.compile(
    r"innerHTML|outerHTML|insertAdjacentHTML|document\.write"
)


def test_change_form_script_keeps_field_text_as_text():
    """
    The script that turns URLs into links must build DOM nodes from the field
    text so that the escaping applied by the server is preserved.
    """

    source = get_template("admin/api/media/change_form.html").template.source

    assert not HTML_STRING_SINKS.search(source)
