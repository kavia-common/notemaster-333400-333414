from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    code: str = Field(..., description="Stable machine-readable error code.")
    message: str = Field(..., description="Human-readable error message.")


class TokenResponse(BaseModel):
    access_token: str = Field(..., description="JWT access token.")
    token_type: str = Field("bearer", description="Token type (always 'bearer').")


class RegisterRequest(BaseModel):
    email: str = Field(..., description="User email address.")
    password: str = Field(..., min_length=8, description="User password (min 8 chars).")


class LoginRequest(BaseModel):
    email: str = Field(..., description="User email address.")
    password: str = Field(..., description="User password.")


class UserMeResponse(BaseModel):
    id: int = Field(..., description="User id.")
    email: str = Field(..., description="User email.")


class TagCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=64, description="Tag name.")


class TagUpdateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=64, description="Tag name.")


class TagResponse(BaseModel):
    id: int
    name: str
    created_at: datetime


class NoteCreateRequest(BaseModel):
    title: str = Field("", max_length=200, description="Note title.")
    content: str = Field("", description="Note content.")
    tag_ids: list[int] = Field(default_factory=list, description="List of tag ids to attach.")


class NoteUpdateRequest(BaseModel):
    title: Optional[str] = Field(None, max_length=200, description="Note title.")
    content: Optional[str] = Field(None, description="Note content.")
    tag_ids: Optional[list[int]] = Field(None, description="Replace tags with these tag ids.")


class NoteResponse(BaseModel):
    id: int
    title: str
    content: str
    pinned: bool
    favorite: bool
    tags: list[TagResponse]
    created_at: datetime
    updated_at: datetime


class NoteListResponse(BaseModel):
    items: list[NoteResponse]
    total: int = Field(..., description="Total count for the query (before pagination).")


class NoteSearchResponse(NoteListResponse):
    query: str = Field(..., description="Echo of the search query.")


class ToggleResponse(BaseModel):
    id: int = Field(..., description="Note id.")
    value: bool = Field(..., description="New boolean value.")
