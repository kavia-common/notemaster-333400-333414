import os
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


# PUBLIC_INTERFACE
def get_settings() -> Settings:
    """Return Settings loaded from environment variables.

    Raises:
        RuntimeError: If required environment variables are missing.

    Contract:
        Inputs: Environment variables.
        Output: Settings (all required values present).
        Errors: RuntimeError with a clear message listing missing keys.
        Side effects: None.
    """
    required = [
        "POSTGRES_URL",
        "POSTGRES_USER",
        "POSTGRES_PASSWORD",
        "POSTGRES_DB",
        "POSTGRES_PORT",
        "JWT_SECRET_KEY",
    ]
    missing = [k for k in required if not os.getenv(k)]
    if missing:
        raise RuntimeError(
            "Missing required environment variables: " + ", ".join(missing)
        )

    return Settings(
        postgres_url=os.environ["POSTGRES_URL"],
        postgres_user=os.environ["POSTGRES_USER"],
        postgres_password=os.environ["POSTGRES_PASSWORD"],
        postgres_db=os.environ["POSTGRES_DB"],
        postgres_port=os.environ["POSTGRES_PORT"],
        jwt_secret_key=os.environ["JWT_SECRET_KEY"],
        jwt_algorithm=os.getenv("JWT_ALGORITHM", "HS256"),
        jwt_access_token_expires_minutes=int(
            os.getenv("JWT_ACCESS_TOKEN_EXPIRES_MINUTES", str(60 * 24))
        ),
        cors_allow_origins=os.getenv("CORS_ALLOW_ORIGINS", "*"),
    )
