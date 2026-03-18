from __future__ import annotations

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.app_state import set_state
from src.api.error_handlers import install_error_handlers
from src.api.routers.auth import router as auth_router
from src.api.routers.notes import router as notes_router
from src.api.routers.tags import router as tags_router
from src.core.config import get_settings
from src.db.init_db import init_db
from src.db.session import create_engine_and_sessionmaker

logger = logging.getLogger("notes_backend")

openapi_tags = [
    {"name": "health", "description": "Service health checks"},
    {"name": "auth", "description": "JWT authentication (register/login/me)"},
    {"name": "notes", "description": "Notes CRUD, search, pin and favorite"},
    {"name": "tags", "description": "Tags CRUD and listing"},
]

app = FastAPI(
    title="NoteMaster API",
    description=(
        "Backend API for the NoteMaster app.\n\n"
        "Auth: Obtain a JWT via `/auth/login` and send it as `Authorization: Bearer <token>`.\n"
        "All note/tag data is isolated per-user."
    ),
    version="1.0.0",
    openapi_tags=openapi_tags,
)

# CORS (frontend will call this API from browser)
settings = get_settings()
allow_origins = [o.strip() for o in settings.cors_allow_origins.split(",")] if settings.cors_allow_origins != "*" else ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize DB + app state
engine, SessionLocal = create_engine_and_sessionmaker(settings)
set_state(settings=settings, engine=engine, session_local=SessionLocal)
init_db(engine)

# Error mapping for domain errors
install_error_handlers(app)

# Routers
app.include_router(auth_router)
app.include_router(tags_router)
app.include_router(notes_router)


@app.get(
    "/",
    tags=["health"],
    summary="Health check",
    description="Simple health check endpoint.",
)
def health_check():
    return {"message": "Healthy"}
