from __future__ import annotations

from sqlalchemy.orm import Session

from src.core.errors import ForbiddenError, NotFoundError
from src.db.models import Tag
from src.repos.notes_repo import NotesRepo
from src.repos.tags_repo import TagsRepo


class NotesService:
    """Use-case service for notes operations."""

    def __init__(self, db: Session):
        self._db = db
        self._notes_repo = NotesRepo(db)
        self._tags_repo = TagsRepo(db)

    def _resolve_tags_owned_by_user(self, user_id: int, tag_ids: list[int]) -> list[Tag]:
        tags: list[Tag] = []
        for tag_id in tag_ids:
            tag = self._tags_repo.get_for_user(user_id=user_id, tag_id=tag_id)
            if not tag:
                raise ForbiddenError(message=f"Tag {tag_id} does not exist or is not owned by user")
            tags.append(tag)
        return tags

    def create_note(self, user_id: int, title: str, content: str, tag_ids: list[int]):
        tags = self._resolve_tags_owned_by_user(user_id, tag_ids)
        return self._notes_repo.create(user_id=user_id, title=title, content=content, tags=tags)

    def get_note(self, user_id: int, note_id: int):
        note = self._notes_repo.get_for_user(user_id=user_id, note_id=note_id)
        if not note:
            raise NotFoundError(message="Note not found")
        return note

    def list_notes(self, user_id: int, limit: int, offset: int, tag_id: int | None, pinned: bool | None, favorite: bool | None):
        return self._notes_repo.list_for_user(
            user_id=user_id,
            limit=limit,
            offset=offset,
            tag_id=tag_id,
            pinned=pinned,
            favorite=favorite,
        )

    def search_notes(self, user_id: int, query: str, limit: int, offset: int):
        return self._notes_repo.search_for_user(user_id=user_id, query=query, limit=limit, offset=offset)

    def update_note(self, user_id: int, note_id: int, title: str | None, content: str | None, tag_ids: list[int] | None):
        note = self.get_note(user_id=user_id, note_id=note_id)
        note = self._notes_repo.update_fields(note=note, title=title, content=content)
        if tag_ids is not None:
            tags = self._resolve_tags_owned_by_user(user_id, tag_ids)
            note = self._notes_repo.replace_tags(note=note, tags=tags)
        return note

    def delete_note(self, user_id: int, note_id: int) -> None:
        note = self.get_note(user_id=user_id, note_id=note_id)
        self._notes_repo.delete(note)

    def set_pinned(self, user_id: int, note_id: int, value: bool):
        note = self.get_note(user_id=user_id, note_id=note_id)
        return self._notes_repo.set_pinned(note, value=value)

    def set_favorite(self, user_id: int, note_id: int, value: bool):
        note = self.get_note(user_id=user_id, note_id=note_id)
        return self._notes_repo.set_favorite(note, value=value)
