from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

import jwt

from src.api.app_state import get_settings
from src.core.errors import UnauthorizedError


# PUBLIC_INTERFACE
def create_access_token(subject: str) -> str:
    """Create a signed JWT access token for a user.

    Contract:
        Inputs: subject = user id (string).
        Output: JWT string.
        Errors: Propagates unexpected exceptions (should be rare).
        Side effects: None.
    """
    settings = get_settings()
    now = datetime.now(timezone.utc)
    exp = now + timedelta(minutes=settings.jwt_access_token_expires_minutes)
    payload = {"sub": subject, "iat": int(now.timestamp()), "exp": exp}
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


# PUBLIC_INTERFACE
def decode_access_token(token: str) -> dict[str, Any]:
    """Decode a JWT access token and return its payload.

    Raises UnauthorizedError on invalid/expired tokens.
    """
    settings = get_settings()
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
        if not isinstance(payload, dict):
            raise UnauthorizedError(message="Invalid token payload")
        return payload
    except jwt.ExpiredSignatureError as e:
        raise UnauthorizedError(message="Token expired") from e
    except jwt.InvalidTokenError as e:
        raise UnauthorizedError(message="Invalid token") from e
