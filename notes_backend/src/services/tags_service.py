from __future__ import annotations

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.core.errors import ConflictError, NotFoundError
from src.repos.tags_repo import TagsRepo


class TagsService:
    """Use-case service for tag operations."""

    def __init__(self, db: Session):
        self._db = db
        self._repo = TagsRepo(db)

    def list_tags(self, user_id: int):
        return self._repo.list_for_user(user_id)

    def create_tag(self, user_id: int, name: str):
        name = name.strip()
        if not name:
            raise ConflictError(message="Tag name cannot be empty")
        try:
            return self._repo.create(user_id=user_id, name=name)
        except IntegrityError as e:
            self._db.rollback()
            raise ConflictError(message="Tag with this name already exists") from e

    def update_tag(self, user_id: int, tag_id: int, name: str):
        tag = self._repo.get_for_user(user_id=user_id, tag_id=tag_id)
        if not tag:
            raise NotFoundError(message="Tag not found")
        try:
            return self._repo.update_name(tag=tag, name=name.strip())
        except IntegrityError as e:
            self._db.rollback()
            raise ConflictError(message="Tag with this name already exists") from e

    def delete_tag(self, user_id: int, tag_id: int) -> None:
        tag = self._repo.get_for_user(user_id=user_id, tag_id=tag_id)
        if not tag:
            raise NotFoundError(message="Tag not found")
        self._repo.delete(tag)
