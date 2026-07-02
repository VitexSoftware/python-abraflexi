"""Sphinx configuration for python-abraflexi documentation."""

import os
import sys

sys.path.insert(0, os.path.abspath(".."))

project = "python-abraflexi"
copyright = "2026, Vítězslav Dvořák"
author = "Vítězslav Dvořák"

from python_abraflexi import __version__ as release  # noqa: E402

version = release

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

napoleon_google_docstring = True
napoleon_numpy_docstring = False

autodoc_member_order = "bysource"
autodoc_typehints = "description"

html_theme = "alabaster"
html_static_path = ["_static"]

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
}
