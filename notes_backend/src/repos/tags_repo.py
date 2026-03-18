from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.db.models import Tag


class TagsRepo:
    """DB adapter for tag operations (scoped per-user)."""

    def __init__(self, db: Session):
        self._db = db

    def list_for_user(self, user_id: int) -> list[Tag]:
        stmt = select(Tag).where(Tag.user_id == user_id).order_by(Tag.name.asc())
        return list(self._db.execute(stmt).scalars().all())

    def get_for_user(self, user_id: int, tag_id: int) -> Tag | None:
        tag = self._db.get(Tag, tag_id)
        if not tag or tag.user_id != user_id:
            return None
        return tag

    def get_by_name_for_user(self, user_id: int, name: str) -> Tag | None:
        stmt = select(Tag).where(Tag.user_id == user_id, Tag.name == name)
        return self._db.execute(stmt).scalar_one_or_none()

    def create(self, user_id: int, name: str) -> Tag:
        tag = Tag(user_id=user_id, name=name)
        self._db.add(tag)
        self._db.commit()
        self._db.refresh(tag)
        return tag

    def update_name(self, tag: Tag, name: str) -> Tag:
        tag.name = name
        self._db.add(tag)
        self._db.commit()
        self._db.refresh(tag)
        return tag

    def delete(self, tag: Tag) -> None:
        self._db.delete(tag)
        self._db.commit()
