from sqlalchemy.engine import Engine

from src.db.models import Base


# PUBLIC_INTERFACE
def init_db(engine: Engine) -> None:
    """Initialize database schema.

    Contract:
        Inputs: SQLAlchemy Engine.
        Outputs: None.
        Errors: Propagates SQLAlchemy/DBAPI errors if schema creation fails.
        Side effects: Creates tables if missing.
    """
    Base.metadata.create_all(bind=engine)
