"""
Tests ensuring the package version stays consistent across files.
"""

import re
from pathlib import Path

import python_abraflexi
from python_abraflexi import ReadOnly

ROOT = Path(__file__).resolve().parent.parent


def _version_from(path, pattern):
    text = path.read_text(encoding="utf-8")
    match = re.search(pattern, text)
    assert match, f"version not found in {path}"
    return match.group(1)


class TestVersion:
    """Verify version strings agree across the project."""

    def test_init_version(self):
        assert python_abraflexi.__version__ == "1.0.2"

    def test_read_only_lib_version_matches_package(self):
        assert ReadOnly.LIB_VERSION == python_abraflexi.__version__

    def test_pyproject_version_matches_package(self):
        version = _version_from(
            ROOT / "pyproject.toml", r'(?m)^version = "([^"]+)"'
        )
        assert version == python_abraflexi.__version__

    def test_setup_py_version_matches_package(self):
        version = _version_from(ROOT / "setup.py", r'version="([^"]+)"')
        assert version == python_abraflexi.__version__
