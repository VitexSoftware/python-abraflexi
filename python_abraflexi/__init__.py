"""
Python AbraFlexi - Python library for AbraFlexi REST API.

This library provides easy interaction with the Czech economic system AbraFlexi.
"""

__version__ = "1.1.2"
__author__ = "Vítězslav Dvořák"
__email__ = "info@vitexsoftware.cz"
__license__ = "MIT"

from .read_only import ReadOnly
from .read_write import ReadWrite
from .relation import Relation
from .changes import Changes
from .evidences import Adresar, FakturaVydana
from .exceptions import (
    AbraFlexiException,
    ConnectionException,
    AuthenticationException,
    NotFoundException,
    PermissionException,
    ValidationException,
)

__all__ = [
    "ReadOnly",
    "ReadWrite",
    "Relation",
    "Changes",
    "Adresar",
    "FakturaVydana",
    "AbraFlexiException",
    "ConnectionException",
    "AuthenticationException",
    "NotFoundException",
    "PermissionException",
    "ValidationException",
]
