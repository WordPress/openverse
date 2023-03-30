import sys
from pathlib import Path


def add_ext_to_path():
    """Add the ``_ext`` directory to the module path"""
    cwd = Path(__file__).parent
    project_root = cwd.parent

    sys.path.insert(0, str(project_root))
    sys.path.insert(0, str(cwd / "_ext"))


add_ext_to_path()

# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "Openverse"
author = "Openverse <openverse@wordpress.org>"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ["myst_parser", "link_issues"]
myst_heading_anchors = 6  # Add anchors to all headers, this is disabled by default.

source_suffix = {".rst": "restructuredtext", ".md": "markdown"}

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "furo"
html_theme_options = {
    "light_logo": "logo_light.svg",
    "dark_logo": "logo_dark.svg",
    "sidebar_hide_name": True,
}

html_favicon = (
    "https://raw.githubusercontent.com/WordPress/openverse/master/brand/icon.svg"
)

html_static_path = ["_static"]

html_show_copyright = False

issuetracker = "github"
issuetracker_project = "WordPress/openverse"
