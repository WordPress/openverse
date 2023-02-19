# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys

import django


# Configure Django to work with Sphinx
# Pipenv populates DJANGO_SETTINGS_MODULE and DJANGO_SECRET_KEY from .env
sys.path.append(os.path.abspath(".."))
django.setup()

from django.conf import settings  # noqa: E402 | Run ``setup`` before ``import``


# Project information
# ===================

project = "Openverse API developer docs"
author = f"Openverse <{settings.CONTACT_EMAIL}>"


# General configuration
# =====================

# Sphinx plugins
extensions = ["sphinx.ext.todo", "sphinx.ext.autodoc", "myst_parser"]

source_suffix = {".rst": "restructuredtext", ".md": "markdown"}
templates_path = ["_templates"]


# HTML
# ====

html_theme = "furo"

html_title = project
html_favicon = (
    "https://raw.githubusercontent.com/WordPress/openverse/master/brand/icon.svg"
)

html_theme_options = {
    "light_css_variables": {
        "color-brand-primary": "#c52b9b",  # pink
    },
    "dark_css_variables": {
        "color-brand-primary": "#c52b9b",  # pink
    },
    "footer_icons": [
        {
            "name": "GitHub",
            "url": "https://github.com/WordPress/openverse/",
            "html": """
                <svg stroke="currentColor" fill="currentColor" stroke-width="0" viewBox="0 0 16 16">
                    <path fill-rule="evenodd" d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0 0 16 8c0-4.42-3.58-8-8-8z"></path>
                </svg>
            """,  # noqa: E501
            "class": "",
        },
    ],
    "source_repository": "https://github.com/WordPress/openverse/",
    "source_branch": "main",
}

html_show_copyright = False

# Static
# ======

html_static_path = ["_static"]
html_css_files = ["_css/brand.css"]
