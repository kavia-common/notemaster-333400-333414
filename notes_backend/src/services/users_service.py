from __future__ import annotations

from sqlalchemy.orm import Session

from src.core.errors import ConflictError, UnauthorizedError
from src.repos.users_repo import UsersRepo
from src.security.passwords import hash_password, verify_password


class UsersService:
    """Use-case service for user operations."""

    def __init__(self, db: Session):
        self._db = db
        self._repo = UsersRepo(db)

    def register(self, email: str, password: str):
        existing = self._repo.get_by_email(email=email.lower().strip())
        if existing:
            raise ConflictError(message="Email already registered")
        return self._repo.create(email=email.lower().strip(), password_hash=hash_password(password))

    def authenticate(self, email: str, password: str):
        user = self._repo.get_by_email(email=email.lower().strip())
        if not user or not verify_password(password, user.password_hash):
            raise UnauthorizedError(message="Invalid email or password")
        return user

    def get_user_by_id(self, user_id: int):
        return self._repo.get_by_id(user_id)
