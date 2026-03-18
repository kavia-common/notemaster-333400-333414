from fastapi import FastAPI, status
from fastapi.responses import JSONResponse

from src.core.errors import (
    AppError,
    ConflictError,
    ForbiddenError,
    NotFoundError,
    UnauthorizedError,
    ValidationAppError,
)


# PUBLIC_INTERFACE
def install_error_handlers(app: FastAPI) -> None:
    """Install exception handlers for structured application errors."""

    @app.exception_handler(AppError)
    def _handle_app_error(_, exc: AppError):
        if isinstance(exc, NotFoundError):
            code = status.HTTP_404_NOT_FOUND
        elif isinstance(exc, ForbiddenError):
            code = status.HTTP_403_FORBIDDEN
        elif isinstance(exc, UnauthorizedError):
            code = status.HTTP_401_UNAUTHORIZED
        elif isinstance(exc, ConflictError):
            code = status.HTTP_409_CONFLICT
        elif isinstance(exc, ValidationAppError):
            code = status.HTTP_422_UNPROCESSABLE_ENTITY
        else:
            code = status.HTTP_400_BAD_REQUEST

        return JSONResponse(status_code=code, content={"code": exc.code, "message": exc.message})
