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

extensions = [
    "myst_parser",
    "sphinxcontrib.mermaid",
    "link_issues",
    "link_usernames",
    "sphinx_copybutton",
    "notfound.extension",
    "sphinx_reredirects",
    "sphinx.ext.todo",
]
myst_heading_anchors = 6  # Add anchors to all headers, this is disabled by default.

todo_include_todos = True

source_suffix = {".rst": "restructuredtext", ".md": "markdown"}

exclude_patterns = ["_build", "Thumbs.db", ".DS_Store", ".venv", "README.md"]
suppress_warnings = [
    # Pygments does not fully support language features we use
    # in code blocks in the documentation. Unfortunately the best
    # way to deal with that is to just ignore highlighting failures.
    "misc.highlighting_failure",
]

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "furo"
html_theme_options = {
    "light_logo": "logo_light.svg",
    "dark_logo": "logo_dark.svg",
    "sidebar_hide_name": True,
    "source_repository": "https://github.com/WordPress/openverse/",
    "source_branch": "main",
    "source_directory": "documentation/",
    "footer_icons": [
        {
            "name": "GitHub",
            "url": "https://github.com/WordPress/openverse",
            "html": '<svg fill="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path d="M12 .297c-6.63 0-12 5.373-12 12 0 5.303 3.438 9.8 8.205 11.385.6.113.82-.258.82-.577 0-.285-.01-1.04-.015-2.04-3.338.724-4.042-1.61-4.042-1.61C4.422 18.07 3.633 17.7 3.633 17.7c-1.087-.744.084-.729.084-.729 1.205.084 1.838 1.236 1.838 1.236 1.07 1.835 2.809 1.305 3.495.998.108-.776.417-1.305.76-1.605-2.665-.3-5.466-1.332-5.466-5.93 0-1.31.465-2.38 1.235-3.22-.135-.303-.54-1.523.105-3.176 0 0 1.005-.322 3.3 1.23.96-.267 1.98-.399 3-.405 1.02.006 2.04.138 3 .405 2.28-1.552 3.285-1.23 3.285-1.23.645 1.653.24 2.873.12 3.176.765.84 1.23 1.91 1.23 3.22 0 4.61-2.805 5.625-5.475 5.92.42.36.81 1.096.81 2.22 0 1.606-.015 2.896-.015 3.286 0 .315.21.69.825.57C20.565 22.092 24 17.592 24 12.297c0-6.627-5.373-12-12-12"/></svg>',  # noqa: E501
        },
    ],
}

html_favicon = "_static/favicon.ico"

html_static_path = ["_static"]
html_extra_path = ["robots.txt", "ai.txt"]

html_show_copyright = False

issuetracker = "github"
issuetracker_project = "WordPress/openverse"
githubusermention = True

# The default for this is a sensible one for ReadTheDocs but
# our site is served directly at the root docs.openverse.org URL
# so the prefix should be the root
notfound_urls_prefix = "/"

redirects = {
    "meta/traffic/index": "/meta/monitoring/traffic/index.html",
    "meta/traffic/runbooks/identifying-and-blocking-traffic-anomalies": "/meta/monitoring/traffic/runbooks/identifying-and-blocking-traffic-anomalies.html",  # noqa: E501
    "meta/codespell": "/general/contribution/codespell.html",
    "meta/communication_aliases": "/general/contribution/communication_aliases.html",
    "meta/dev_flow": "/general/contribution/dev_flow.html",
    "meta/github_contribution_practices": "/general/contribution/github_contribution_practices.html",
    "meta/maintainer_tasks": "/general/contribution/maintainer_tasks.html",
    "meta/contribution/github_contribution_practices": "/general/contribution/github_contribution_practices.html",
    "meta/contribution/dev_flow": "/general/contribution/dev_flow.html",
    "meta/contribution/current_maintainers": "/general/contribution/current_maintainers.html",
    "meta/contribution/communication_aliases": "/general/contribution/communication_aliases.html",
    "meta/contribution/becoming_a_committer": "/general/contribution/becoming_a_committer.html",
    "meta/contribution/maintainer_tasks": "/general/contribution/maintainer_tasks.html",
    "meta/contribution/codespell": "/general/contribution/codespell.html",
    "meta/contribution/good_first_and_help_wanted_issues": "/general/contribution/good_first_and_help_wanted_issues.html",
    "frontend/reference/playwright_tests.html": "/frontend/reference/testing_guidelines.html#playwright-tests",
    "frontend/reference/storybook_tests.html": "/frontend/reference/testing_guidelines.html#storybook-tests",
    "frontend/guides/deploy": "/meta/release_and_deployment/runbooks/frontend.html",
    "api/guides/deploy": "/meta/release_and_deployment/runbooks/api.html",
    "catalog/guides/deploy": "/meta/release_and_deployment/runbooks/catalog.html",
    "catalog/guides/deployment": "/meta/release_and_deployment/index.html#catalog",
    "ingestion_server/guides/deploy": "/meta/release_and_deployment/runbooks/ingestion_server.html",
    "packages/eslint_plugin/index": "/packages/js/eslint_plugin/index.html",
    "packages/eslint_plugin/analytics_configuration": "/packages/js/eslint_plugin/analytics_configuration.html",
    "packages/eslint_plugin/no-unexplained-disabled-test": "/packages/js/eslint_plugin/no-unexplained-disabled-test.html",
    "packages/openverse_attribution/index": "/packages/python/openverse_attribution/index.html",
}

myst_enable_extensions = ["linkify"]
