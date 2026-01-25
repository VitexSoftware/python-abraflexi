"""
Python AbraFlexi - Python library for AbraFlexi REST API.

This library provides easy interaction with the Czech economic system AbraFlexi.
"""

__version__ = "1.0.0"
__author__ = "Vítězslav Dvořák"
__email__ = "info@vitexsoftware.cz"
__license__ = "MIT"

from .read_only import ReadOnly
from .read_write import ReadWrite
from .relation import Relation
from .exceptions import (
    AbraFlexiException,
    ConnectionException,
    AuthenticationException,
    NotFoundException,
    ValidationException,
)

__all__ = [
    "ReadOnly",
    "ReadWrite",
    "Relation",
    "AbraFlexiException",
    "ConnectionException",
    "AuthenticationException",
    "NotFoundException",
    "ValidationException",
]
