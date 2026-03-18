from __future__ import annotations

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from src.api.deps import get_current_user_id, get_db_session
from src.api.schemas import (
    ErrorResponse,
    NoteCreateRequest,
    NoteListResponse,
    NoteResponse,
    NoteSearchResponse,
    NoteUpdateRequest,
    ToggleResponse,
)
from src.services.notes_service import NotesService

router = APIRouter(prefix="/notes", tags=["notes"])


def _to_note_response(note) -> NoteResponse:
    return NoteResponse(
        id=note.id,
        title=note.title,
        content=note.content,
        pinned=note.pinned,
        favorite=note.favorite,
        tags=[
            # TagResponse shape
            {"id": t.id, "name": t.name, "created_at": t.created_at}
            for t in (note.tags or [])
        ],
        created_at=note.created_at,
        updated_at=note.updated_at,
    )


@router.get(
    "",
    response_model=NoteListResponse,
    summary="List notes",
    description="List notes for the current user. Supports filtering by tag/pinned/favorite and pagination.",
    responses={401: {"model": ErrorResponse}},
)
def list_notes(
    limit: int = Query(50, ge=1, le=200, description="Page size."),
    offset: int = Query(0, ge=0, description="Pagination offset."),
    tag_id: int | None = Query(None, description="Filter notes having this tag id."),
    pinned: bool | None = Query(None, description="Filter by pinned state."),
    favorite: bool | None = Query(None, description="Filter by favorite state."),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db_session),
):
    svc = NotesService(db)
    items, total = svc.list_notes(
        user_id=user_id,
        limit=limit,
        offset=offset,
        tag_id=tag_id,
        pinned=pinned,
        favorite=favorite,
    )
    return NoteListResponse(items=[_to_note_response(n) for n in items], total=total)


@router.get(
    "/search",
    response_model=NoteSearchResponse,
    summary="Search notes",
    description="Search notes by substring match on title/content (case-insensitive) within the current user's notes.",
    responses={401: {"model": ErrorResponse}},
)
def search_notes(
    q: str = Query(..., min_length=1, description="Search query."),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db_session),
):
    svc = NotesService(db)
    items, total = svc.search_notes(user_id=user_id, query=q, limit=limit, offset=offset)
    return NoteSearchResponse(query=q, items=[_to_note_response(n) for n in items], total=total)


@router.post(
    "",
    response_model=NoteResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create note",
    description="Create a new note for the current user.",
    responses={401: {"model": ErrorResponse}, 403: {"model": ErrorResponse}},
)
def create_note(payload: NoteCreateRequest, user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db_session)):
    svc = NotesService(db)
    note = svc.create_note(user_id=user_id, title=payload.title, content=payload.content, tag_ids=payload.tag_ids)
    return _to_note_response(note)


@router.get(
    "/{note_id}",
    response_model=NoteResponse,
    summary="Get note",
    description="Get a single note by id (must be owned by the current user).",
    responses={401: {"model": ErrorResponse}, 404: {"model": ErrorResponse}},
)
def get_note(note_id: int, user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db_session)):
    svc = NotesService(db)
    note = svc.get_note(user_id=user_id, note_id=note_id)
    return _to_note_response(note)


@router.put(
    "/{note_id}",
    response_model=NoteResponse,
    summary="Update note",
    description="Update note fields and optionally replace tag associations.",
    responses={401: {"model": ErrorResponse}, 403: {"model": ErrorResponse}, 404: {"model": ErrorResponse}},
)
def update_note(note_id: int, payload: NoteUpdateRequest, user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db_session)):
    svc = NotesService(db)
    note = svc.update_note(
        user_id=user_id,
        note_id=note_id,
        title=payload.title,
        content=payload.content,
        tag_ids=payload.tag_ids,
    )
    return _to_note_response(note)


@router.delete(
    "/{note_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete note",
    description="Delete a note owned by the current user.",
    responses={401: {"model": ErrorResponse}, 404: {"model": ErrorResponse}},
)
def delete_note(note_id: int, user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db_session)):
    svc = NotesService(db)
    svc.delete_note(user_id=user_id, note_id=note_id)
    return None


@router.post(
    "/{note_id}/pin",
    response_model=ToggleResponse,
    summary="Pin note",
    description="Set pinned=true for a note owned by the current user.",
    responses={401: {"model": ErrorResponse}, 404: {"model": ErrorResponse}},
)
def pin_note(note_id: int, user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db_session)):
    svc = NotesService(db)
    note = svc.set_pinned(user_id=user_id, note_id=note_id, value=True)
    return ToggleResponse(id=note.id, value=note.pinned)


@router.post(
    "/{note_id}/unpin",
    response_model=ToggleResponse,
    summary="Unpin note",
    description="Set pinned=false for a note owned by the current user.",
    responses={401: {"model": ErrorResponse}, 404: {"model": ErrorResponse}},
)
def unpin_note(note_id: int, user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db_session)):
    svc = NotesService(db)
    note = svc.set_pinned(user_id=user_id, note_id=note_id, value=False)
    return ToggleResponse(id=note.id, value=note.pinned)


@router.post(
    "/{note_id}/favorite",
    response_model=ToggleResponse,
    summary="Favorite note",
    description="Set favorite=true for a note owned by the current user.",
    responses={401: {"model": ErrorResponse}, 404: {"model": ErrorResponse}},
)
def favorite_note(note_id: int, user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db_session)):
    svc = NotesService(db)
    note = svc.set_favorite(user_id=user_id, note_id=note_id, value=True)
    return ToggleResponse(id=note.id, value=note.favorite)


@router.post(
    "/{note_id}/unfavorite",
    response_model=ToggleResponse,
    summary="Unfavorite note",
    description="Set favorite=false for a note owned by the current user.",
    responses={401: {"model": ErrorResponse}, 404: {"model": ErrorResponse}},
)
def unfavorite_note(note_id: int, user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db_session)):
    svc = NotesService(db)
    note = svc.set_favorite(user_id=user_id, note_id=note_id, value=False)
    return ToggleResponse(id=note.id, value=note.favorite)
