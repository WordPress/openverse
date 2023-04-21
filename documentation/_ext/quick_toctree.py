from docutils.parsers.rst import directives
from sphinx.application import Sphinx
from sphinx.directives.other import TocTree


def quick_toctree_type(argument):
    return directives.choice(argument, ("flat", "stack_root"))


class QuickTocTree(TocTree):
    """
    Extend TocTree to add reusable Quick TocTree types.

    This direction adds one new option to TocTree: ``type``.
    ``type`` can be any of the following:

        ``flat``: Automatically glob one level of headings at the toctree level

        ``stack_root``: Glob the current directory and any nested directories
        for index files.

    Both support passing a normal list of documents to list, in source order,
    at the top of the generated ToC. All ``TocTree`` options are supported
    and explicitly set options are respected.
    """

    option_spec = TocTree.option_spec | {
        "type": quick_toctree_type,
    }

    type_configs = {
        "flat": {"content": ["*"], "options": {"maxdepth": 1, "glob": True}},
        "stack_root": {
            "content": ["*", "*/index"],
            "options": {"titlesonly": True, "maxdepth": 2, "glob": True},
        },
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        type_opt = self.options.get("type")
        if not type_opt:
            return

        config = QuickTocTree.type_configs.get(type_opt)
        if not config:
            raise ValueError(
                f"`{type_opt}` is not a valid setting for `type` in `quicktoctree`."
            )

        for content in config["content"]:
            self.content.append(content, source="quicktoctree")

        self.options = config["options"] | self.options


def setup(app: Sphinx) -> dict:
    directives.register_directive("quicktoctree", QuickTocTree)
    return {
        "version": "0.1",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
