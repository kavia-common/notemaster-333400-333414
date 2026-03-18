from __future__ import annotations

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from src.core.errors import UnauthorizedError
from src.security.jwt import decode_access_token
from src.services.users_service import UsersService


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


# PUBLIC_INTERFACE
def get_db_session() -> Session:
    """FastAPI dependency that yields a request-scoped DB session."""
    from src.api.app_state import get_sessionmaker  # local import to avoid cycles

    SessionLocal = get_sessionmaker()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# PUBLIC_INTERFACE
def get_current_user_id(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db_session),
) -> int:
    """FastAPI dependency to extract current user's id from Authorization: Bearer JWT."""
    payload = decode_access_token(token)
    user_id = payload.get("sub")
    if not user_id:
        raise UnauthorizedError(message="Invalid token (missing subject)")
    # Ensure the user still exists.
    svc = UsersService(db)
    user = svc.get_user_by_id(int(user_id))
    if not user:
        raise UnauthorizedError(message="User not found")
    return int(user_id)
