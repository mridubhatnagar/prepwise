from datetime import datetime, timedelta, timezone

from jose import jwt

from config import config


def generate_jwt_token(user_id: str, scopes: list[str]) -> str:
    """Generate a signed HS256 JWT for the given user.

    Args:
        user_id: The user's UUID string (primary key from the ``users`` table).
        scopes: List of scope strings from ``allowed_users.scope`` (e.g. ``["app", "docs"]``).

    Returns:
        A signed JWT string valid for ``JWT_EXPIRY_SECONDS`` seconds.
    """
    expiry = datetime.now(tz=timezone.utc) + timedelta(seconds=config.JWT_EXPIRY_SECONDS)
    payload = {
        "user_id": user_id,
        "scopes": scopes,
        "exp": expiry,
    }
    return jwt.encode(payload, config.JWT_SECRET, algorithm=config.JWT_ALGORITHM)
