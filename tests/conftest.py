import pytest


def pytest_addoption(parser):
    """
    Add options to pytest.

    This functions alters the pytest CLI command options. It adds an "extended" flag
    which will run tests that take a significant amount of time that may not be useful
    for rapid local iteration.

    Adapted from:
    https://stackoverflow.com/a/43938191/3277713 CC BY-SA 4.0
    """
    parser.addoption(
        "--extended",
        action="store_true",
        dest="extended",
        default=False,
        help="Run time-consuming 'extended' tests",
    )


# Use this decorator on tests which are expected to take a long time and would best be
# run on CI only
mark_extended = pytest.mark.skipif("not config.getoption('extended')")
