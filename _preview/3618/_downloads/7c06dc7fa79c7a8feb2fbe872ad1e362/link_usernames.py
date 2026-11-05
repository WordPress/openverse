"""GitHub Username Linking

Based on: https://www.sphinx-doc.org/en/master/extdev/appapi.html#event-source-read
and: https://stackoverflow.com/a/31924901/3277713  CC BY-SA 3.0 by C_Z_

This extension replaces username references of the form `@username` with a link
to the user's GitHub profile.

The plugin ignores code inside of fixed text blocks, including code blocks and backticks.
"""
import re

from docutils import nodes
from sphinx.application import Sphinx
from sphinx.transforms import SphinxTransform
from sphinx.util import logging


logger = logging.getLogger(__name__)

# Format to use for the link to the GitHub profile
GITHUB_USERNAME_TEMPLATE = "https://github.com/{username}"
# Format to use for team mentions
GITHUB_TEAM_TEMPLATE = "https://github.com/orgs/{org}/teams/{team}"

# Regex to match username references
GITHUB_USERNAME_REGEX = re.compile(
    r"""
@(?P<username>[A-Za-z0-9-]+)  # Match @ then any alphanumeric character or - for the username
(?P<team>/[A-Za-z0-9-]+)?  # If this is a team reference, match the team separately
""",
    flags=re.VERBOSE,
)


class GitHubUserMentions(SphinxTransform):
    default_priority = 999

    def apply(self) -> None:
        for node in self.document.findall(nodes.Text):
            parent = node.parent

            # ignore existing links, back ticks, and code blocks
            ignore_types = (nodes.reference, nodes.literal, nodes.FixedTextElement)
            if isinstance(parent, ignore_types):
                continue

            text = str(node)
            new_nodes = []
            prev_mention_node_ref = 0
            for match in GITHUB_USERNAME_REGEX.finditer(text):
                # The full match including the leading @
                mention = match.group(0)

                username = match.group("username")

                # `team` will be None if not a team mention
                # If it is a team mention, then `username` will be the org
                team = match.group("team")

                # extract the text between the last user mention and the
                # current user mention and put it into a new text node
                head = text[prev_mention_node_ref : match.start()]
                if head:
                    new_nodes.append(nodes.Text(head))

                # adjust the position of the last user mention in the
                # text
                prev_mention_node_ref = match.end()

                textnode = nodes.Text(mention)
                refnode = nodes.reference()

                if team:
                    url = GITHUB_TEAM_TEMPLATE.format(
                        org=username,
                        team=team.lstrip("/"),
                    )
                    title = f"Team {username}{team} on GitHub"
                else:
                    url = GITHUB_USERNAME_TEMPLATE.format(
                        username=username,
                    )
                    title = f"{username} on GitHub"

                refnode["refuri"] = url
                refnode["reftitle"] = title
                refnode.append(textnode)

                new_nodes.append(refnode)

            if not new_nodes:
                # no user mentions were found, move on to the next node
                continue

            # extract the remaining text after the last user mention, and
            # put it into a text node
            tail = text[prev_mention_node_ref:]
            if tail:
                new_nodes.append(nodes.Text(tail))
            # find and remove the original node, and insert all new nodes
            # instead
            parent.replace(node, new_nodes)


def init_transformer(app: Sphinx) -> None:
    if app.config.githubusermention:
        app.add_transform(GitHubUserMentions)


def setup(app: Sphinx):
    app.add_config_value("githubusermention", None, "env")
    app.connect("builder-inited", init_transformer)
    return {
        "version": "1.0",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
