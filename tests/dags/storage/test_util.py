import logging

from storage import util


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s:  %(message)s", level=logging.DEBUG
)


def test_get_source_preserves_given_both():
    expect_source = "Source"
    actual_source = util.get_source(expect_source, "test_provider")
    assert actual_source == expect_source


def test_get_source_preserves_source_without_provider():
    input_provider, expect_source = None, "Source"
    actual_source = util.get_source(expect_source, input_provider)
    assert actual_source == expect_source


def test_get_source_fills_source_if_none_given():
    input_provider, input_source = "Provider", None
    actual_source = util.get_source(input_source, input_provider)
    expect_source = "Provider"
    assert actual_source == expect_source


def test_get_source_nones_if_none_given():
    actual_source = util.get_source(None, None)
    assert actual_source is None
