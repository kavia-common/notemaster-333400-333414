from __future__ import annotations

from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker

from src.core.config import Settings

_SETTINGS: Settings | None = None
_ENGINE: Engine | None = None
_SESSIONMAKER: sessionmaker | None = None


# PUBLIC_INTERFACE
def set_state(settings: Settings, engine: Engine, session_local: sessionmaker) -> None:
    """Set global app state for dependency injection.

    Contract:
        Inputs: settings, engine, sessionmaker.
        Output: None.
        Errors: None.
        Side effects: Stores global singletons for process lifetime.
    """
    global _SETTINGS, _ENGINE, _SESSIONMAKER
    _SETTINGS = settings
    _ENGINE = engine
    _SESSIONMAKER = session_local


# PUBLIC_INTERFACE
def get_settings() -> Settings:
    """Get Settings singleton."""
    if _SETTINGS is None:
        raise RuntimeError("App state not initialized (settings missing)")
    return _SETTINGS


# PUBLIC_INTERFACE
def get_engine() -> Engine:
    """Get Engine singleton."""
    if _ENGINE is None:
        raise RuntimeError("App state not initialized (engine missing)")
    return _ENGINE


# PUBLIC_INTERFACE
def get_sessionmaker() -> sessionmaker:
    """Get sessionmaker singleton."""
    if _SESSIONMAKER is None:
        raise RuntimeError("App state not initialized (sessionmaker missing)")
    return _SESSIONMAKER
