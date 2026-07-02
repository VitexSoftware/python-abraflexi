"""Sphinx configuration for python-abraflexi documentation."""

import os
import sys

# Resolve relative to this file, not the current working directory: the
# packaging build (debian/rules) invokes sphinx-build from the repo root,
# not from docs/, so a cwd-relative ".." would point one level too high.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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
html_logo = "_static/python-abraflexi.svg"
html_favicon = "_static/python-abraflexi.svg"
html_theme_options = {
    "github_user": "VitexSoftware",
    "github_repo": "python-abraflexi",
    "github_button": True,
    "github_type": "star",
    "description": "Python client library for the AbraFlexi (FlexiBee) REST API",
}

# Compatibility shim: the installed shibuya theme hardcodes pygments style
# names ("github-light-default"/"github-dark-default") that only exist in
# newer pygments releases than the one available here. Fall back to
# built-in styles so `-D html_theme=shibuya` builds don't crash.
try:
    from pygments.styles import get_style_by_name

    get_style_by_name("github-light-default")
except Exception:
    try:
        import shibuya._pygments as _shibuya_pygments

        _shibuya_pygments.ShibuyaPygmentsBridge.light_style_name = "default"
        _shibuya_pygments.ShibuyaPygmentsBridge.dark_style_name = "github-dark"
    except ImportError:
        pass

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
}

_ALABASTER_ONLY_OPTIONS = (
    "github_user",
    "github_repo",
    "github_button",
    "github_type",
    "description",
)


def setup(app):
    """Drop alabaster-only theme options when building with another theme
    (e.g. ``-D html_theme=shibuya`` for the PDF export), so unrelated themes
    don't warn about options they don't understand."""

    def _strip_incompatible_theme_options(app, config):
        if config.html_theme != "alabaster":
            config.html_theme_options = {
                key: value
                for key, value in config.html_theme_options.items()
                if key not in _ALABASTER_ONLY_OPTIONS
            }

    app.connect("config-inited", _strip_incompatible_theme_options)
