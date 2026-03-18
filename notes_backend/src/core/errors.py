from dataclasses import dataclass


@dataclass
class AppError(Exception):
    """Base application error with a stable, structured shape."""

    code: str
    message: str


@dataclass
class NotFoundError(AppError):
    """Raised when a requested resource does not exist."""

    code: str = "not_found"
    message: str = "Resource not found"


@dataclass
class ForbiddenError(AppError):
    """Raised when access is denied for a resource."""

    code: str = "forbidden"
    message: str = "Access denied"


@dataclass
class ConflictError(AppError):
    """Raised when a requested operation conflicts with existing state."""

    code: str = "conflict"
    message: str = "Conflict"


@dataclass
class UnauthorizedError(AppError):
    """Raised when authentication is required or fails."""

    code: str = "unauthorized"
    message: str = "Not authenticated"


@dataclass
class ValidationAppError(AppError):
    """Raised when higher-level business validation fails."""

    code: str = "validation_error"
    message: str = "Invalid request"
