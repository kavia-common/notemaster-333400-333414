from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker

from src.core.config import Settings


def _build_sqlalchemy_url(settings: Settings) -> str:
    """
    Build SQLAlchemy URL from the container env vars.

    Env vars come from the database container:
      POSTGRES_URL, POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB, POSTGRES_PORT

    Example db_connection.txt (for local psql CLI):
      psql postgresql://appuser:dbuser123@localhost:5000/myapp
    """
    # POSTGRES_URL is typically host, e.g. "localhost" or a service name.
    # Use psycopg3 driver.
    return (
        f"postgresql+psycopg://{settings.postgres_user}:{settings.postgres_password}"
        f"@{settings.postgres_url}:{settings.postgres_port}/{settings.postgres_db}"
    )


# PUBLIC_INTERFACE
def create_engine_and_sessionmaker(settings: Settings) -> tuple[Engine, sessionmaker]:
    """Create SQLAlchemy Engine and sessionmaker.

    Contract:
        Inputs: Settings with Postgres connection fields.
        Outputs: (Engine, sessionmaker) ready for request-scoped sessions.
        Errors: Propagates SQLAlchemy/DBAPI errors on invalid configuration.
        Side effects: Creates engine (lazy connects by default).
    """
    url = _build_sqlalchemy_url(settings)
    engine = create_engine(url, pool_pre_ping=True)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    return engine, SessionLocal
