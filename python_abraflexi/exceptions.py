"""
Exceptions for Python AbraFlexi library.
"""


class AbraFlexiException(Exception):
    """Base exception for AbraFlexi library."""

    pass


class ConnectionException(AbraFlexiException):
    """Exception raised when connection to AbraFlexi fails."""

    pass


class AuthenticationException(AbraFlexiException):
    """Exception raised when authentication fails."""

    pass


class NotFoundException(AbraFlexiException):
    """Exception raised when requested resource is not found."""

    pass


class ValidationException(AbraFlexiException):
    """Exception raised when data validation fails."""

    def __init__(self, message: str, errors: list = None):
        """
        Initialize validation exception.

        Args:
            message: Error message
            errors: List of validation errors
        """
        super().__init__(message)
        self.errors = errors or []
