from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from src.api.deps import get_current_user_id, get_db_session
from src.api.schemas import ErrorResponse, TagCreateRequest, TagResponse, TagUpdateRequest
from src.services.tags_service import TagsService

router = APIRouter(prefix="/tags", tags=["tags"])


@router.get(
    "",
    response_model=list[TagResponse],
    summary="List tags",
    description="List all tags for the current user.",
    responses={401: {"model": ErrorResponse}},
)
def list_tags(user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db_session)):
    svc = TagsService(db)
    return svc.list_tags(user_id=user_id)


@router.post(
    "",
    response_model=TagResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create tag",
    description="Create a new tag for the current user.",
    responses={401: {"model": ErrorResponse}, 409: {"model": ErrorResponse}},
)
def create_tag(payload: TagCreateRequest, user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db_session)):
    svc = TagsService(db)
    return svc.create_tag(user_id=user_id, name=payload.name)


@router.put(
    "/{tag_id}",
    response_model=TagResponse,
    summary="Update tag",
    description="Rename a tag owned by the current user.",
    responses={401: {"model": ErrorResponse}, 404: {"model": ErrorResponse}, 409: {"model": ErrorResponse}},
)
def update_tag(tag_id: int, payload: TagUpdateRequest, user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db_session)):
    svc = TagsService(db)
    return svc.update_tag(user_id=user_id, tag_id=tag_id, name=payload.name)


@router.delete(
    "/{tag_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete tag",
    description="Delete a tag owned by the current user.",
    responses={401: {"model": ErrorResponse}, 404: {"model": ErrorResponse}},
)
def delete_tag(tag_id: int, user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db_session)):
    svc = TagsService(db)
    svc.delete_tag(user_id=user_id, tag_id=tag_id)
    return None
