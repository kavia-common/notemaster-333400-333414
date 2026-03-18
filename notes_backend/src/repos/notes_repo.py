from __future__ import annotations

from sqlalchemy import and_, func, or_, select
from sqlalchemy.orm import Session, selectinload

from src.db.models import Note, Tag


class NotesRepo:
    """DB adapter for note operations (scoped per-user)."""

    def __init__(self, db: Session):
        self._db = db

    def create(self, user_id: int, title: str, content: str, tags: list[Tag]) -> Note:
        note = Note(user_id=user_id, title=title, content=content)
        note.tags = tags
        self._db.add(note)
        self._db.commit()
        self._db.refresh(note)
        return note

    def get_for_user(self, user_id: int, note_id: int) -> Note | None:
        stmt = (
            select(Note)
            .where(and_(Note.id == note_id, Note.user_id == user_id))
            .options(selectinload(Note.tags))
        )
        return self._db.execute(stmt).scalar_one_or_none()

    def list_for_user(
        self,
        user_id: int,
        limit: int,
        offset: int,
        tag_id: int | None = None,
        pinned: bool | None = None,
        favorite: bool | None = None,
    ) -> tuple[list[Note], int]:
        stmt = select(Note).where(Note.user_id == user_id).options(selectinload(Note.tags))

        if tag_id is not None:
            stmt = stmt.join(Note.tags).where(Tag.id == tag_id)
        if pinned is not None:
            stmt = stmt.where(Note.pinned == pinned)
        if favorite is not None:
            stmt = stmt.where(Note.favorite == favorite)

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = int(self._db.execute(count_stmt).scalar_one())

        stmt = stmt.order_by(Note.pinned.desc(), Note.updated_at.desc()).limit(limit).offset(offset)
        items = list(self._db.execute(stmt).scalars().unique().all())
        return items, total

    def search_for_user(self, user_id: int, query: str, limit: int, offset: int) -> tuple[list[Note], int]:
        q = f"%{query.strip()}%"
        stmt = (
            select(Note)
            .where(
                and_(
                    Note.user_id == user_id,
                    or_(
                        Note.title.ilike(q),
                        Note.content.ilike(q),
                    ),
                )
            )
            .options(selectinload(Note.tags))
        )
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = int(self._db.execute(count_stmt).scalar_one())

        stmt = stmt.order_by(Note.pinned.desc(), Note.updated_at.desc()).limit(limit).offset(offset)
        items = list(self._db.execute(stmt).scalars().unique().all())
        return items, total

    def update_fields(self, note: Note, title: str | None, content: str | None) -> Note:
        if title is not None:
            note.title = title
        if content is not None:
            note.content = content
        self._db.add(note)
        self._db.commit()
        self._db.refresh(note)
        return note

    def replace_tags(self, note: Note, tags: list[Tag]) -> Note:
        note.tags = tags
        self._db.add(note)
        self._db.commit()
        self._db.refresh(note)
        return note

    def delete(self, note: Note) -> None:
        self._db.delete(note)
        self._db.commit()

    def set_pinned(self, note: Note, value: bool) -> Note:
        note.pinned = value
        self._db.add(note)
        self._db.commit()
        self._db.refresh(note)
        return note

    def set_favorite(self, note: Note, value: bool) -> Note:
        note.favorite = value
        self._db.add(note)
        self._db.commit()
        self._db.refresh(note)
        return note
