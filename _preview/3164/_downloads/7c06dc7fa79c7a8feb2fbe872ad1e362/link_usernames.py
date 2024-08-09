"""GitHub Username Linking

Based on: https://www.sphinx-doc.org/en/master/extdev/appapi.html#event-source-read
and: https://stackoverflow.com/a/31924901/3277713  CC BY-SA 3.0 by C_Z_

This extension replaces username references of the form `@username` with a link
to the user's GitHub profile. In order to prevent adding references to existing
existing links (e.g. `[@username](...)`, whitespace is required in front of the `@`.

The GITHUB_IGNORE_USERNAMES set contains usernames that should not be linked but may
appear to be usernames in the documentation.
"""
import re

from sphinx.application import Sphinx
from sphinx.util import logging


logger = logging.getLogger(__name__)

# Format to use for the link to the GitHub profile
GITHUB_USERNAME_TEMPLATE = "https://github.com/{}"
# Regex to match username references
GITHUB_USERNAME_REGEX = re.compile(
    r"""
\ # Required initial whitespace
@([A-Za-z0-9-]+)  # Match @ then any alphanumeric character or - for the username
""",
    flags=re.VERBOSE,
)
GITHUB_IGNORE_USERNAMES = {"todo", "WordPress", "username", "defaultValue"}


def _replace_username(match: re.Match) -> str:
    username = match.group(1)
    if username in GITHUB_IGNORE_USERNAMES:
        logger.debug(f"Ignoring username reference: {username}")
        return match.group(0)
    logger.debug(f"Replacing username reference: {username}")
    return f" [@{username}]({GITHUB_USERNAME_TEMPLATE.format(username)})"


def replace_username_references(app, docname, source):
    logger.debug(f"In file: {docname}")
    source[0] = GITHUB_USERNAME_REGEX.sub(_replace_username, source[0])


def setup(app: Sphinx):
    # Hook for running the replace username references when the source file is read
    app.connect("source-read", replace_username_references)
