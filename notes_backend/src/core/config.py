import os
import secrets
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    """Application settings resolved from environment variables.

    Notes:
      - For DB connectivity, this project is expected to run with the database
        container providing the following env vars:
        POSTGRES_URL, POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB, POSTGRES_PORT
      - JWT settings must be provided via env vars in deployment.
    """

    postgres_url: str
    postgres_user: str
    postgres_password: str
    postgres_db: str
    postgres_port: str

    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_access_token_expires_minutes: int = 60 * 24  # 24h by default

    cors_allow_origins: str = "*"


def _get_env_name() -> str:
    """Get environment name (defaults to 'development').

    We keep this private to avoid expanding public surface area.
    """
    return (os.getenv("ENV") or os.getenv("APP_ENV") or "development").strip().lower()


# PUBLIC_INTERFACE
def get_settings() -> Settings:
    """Return Settings loaded from environment variables.

    In production, required environment variables must be present and the function
    fails fast with a clear error.

    In non-production (preview/dev/test), we allow JWT_SECRET_KEY to be missing by
    generating a process-local secret. This enables the API container to boot so
    the preview can become ready, while still keeping production strict.

    Raises:
        RuntimeError: If required environment variables are missing (production),
            or if required DB env vars are missing (all environments).

    Contract:
        Inputs: Environment variables.
        Output: Settings (all required values present).
        Errors: RuntimeError with a clear message listing missing keys.
        Side effects: May generate an ephemeral JWT secret in non-production.
    """
    env_name = _get_env_name()

    required_db = [
        "POSTGRES_URL",
        "POSTGRES_USER",
        "POSTGRES_PASSWORD",
        "POSTGRES_DB",
        "POSTGRES_PORT",
    ]
    missing_db = [k for k in required_db if not os.getenv(k)]
    if missing_db:
        raise RuntimeError("Missing required environment variables: " + ", ".join(missing_db))

    jwt_secret_key = os.getenv("JWT_SECRET_KEY")
    if not jwt_secret_key:
        if env_name == "production":
            raise RuntimeError("Missing required environment variables: JWT_SECRET_KEY")
        # Ephemeral secret: OK for preview; tokens will invalidate on restart.
        jwt_secret_key = secrets.token_urlsafe(32)

    return Settings(
        postgres_url=os.environ["POSTGRES_URL"],
        postgres_user=os.environ["POSTGRES_USER"],
        postgres_password=os.environ["POSTGRES_PASSWORD"],
        postgres_db=os.environ["POSTGRES_DB"],
        postgres_port=os.environ["POSTGRES_PORT"],
        jwt_secret_key=jwt_secret_key,
        jwt_algorithm=os.getenv("JWT_ALGORITHM", "HS256"),
        jwt_access_token_expires_minutes=int(
            os.getenv("JWT_ACCESS_TOKEN_EXPIRES_MINUTES", str(60 * 24))
        ),
        cors_allow_origins=os.getenv("CORS_ALLOW_ORIGINS", "*"),
    )
