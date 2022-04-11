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
author = "Openverse"
project_copyright = f"{author} <{settings.CONTACT_EMAIL}>"


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
}

# Static
# ======

html_static_path = ["_static"]
html_css_files = ["_css/brand.css"]
