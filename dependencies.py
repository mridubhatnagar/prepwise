import logging
import secrets
from dataclasses import dataclass

from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from jose import ExpiredSignatureError, JWTError, jwt

from auth.dao import UserDAO
from auth.service import UserService
from config import config
from exceptions import DatabaseError

logger = logging.getLogger(__name__)

_http_basic = HTTPBasic()


def verify_docs_credentials(credentials: HTTPBasicCredentials = Depends(_http_basic)) -> None:
    """FastAPI dependency gating internal-only routes (/docs, /api/spend/monthly).

    Compares the supplied username/password against config.DOCS_USERNAME /
    config.DOCS_PASSWORD using secrets.compare_digest to avoid timing attacks.
    """
    username_ok = secrets.compare_digest(credentials.username, config.DOCS_USERNAME)
    password_ok = secrets.compare_digest(credentials.password, config.DOCS_PASSWORD)

    if not (username_ok and password_ok):
        logger.warning("Basic Auth rejected for username=%s", credentials.username)
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )


@dataclass
class AuthenticatedUser:
    """Represents the verified user extracted from a JWT."""

    id: str
    scopes: list[str]


def get_current_user(request: Request) -> AuthenticatedUser:
    """FastAPI dependency that validates the JWT and returns the authenticated user.

    Reads the token from the ``jwt`` HttpOnly cookie (browser) or the
    ``Authorization: Bearer <token>`` header (curl / testing).  Raises
    ``HTTPException(401)`` if the token is missing, invalid, or expired, or if
    the referenced user does not exist in the database.
    """
    token = _extract_token(request)

    try:
        payload = jwt.decode(token, config.JWT_SECRET, algorithms=[config.JWT_ALGORITHM])
    except ExpiredSignatureError:
        logger.warning("JWT validation failed: token expired")
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    except JWTError as exc:
        logger.warning("JWT validation failed: %s", exc)
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user_id: str | None = payload.get("user_id")
    scopes: list[str] = payload.get("scopes", [])

    if not user_id:
        logger.warning("JWT payload missing user_id")
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    _verify_user_exists(user_id)

    return AuthenticatedUser(id=user_id, scopes=scopes)


def _extract_token(request: Request) -> str:
    """Return the raw JWT string from the request cookie or Authorization header."""
    token = request.cookies.get("jwt")
    if token:
        return token

    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        return auth_header[len("Bearer "):]

    raise HTTPException(status_code=401, detail="Invalid or expired token")


def _verify_user_exists(user_id: str) -> None:
    """Confirm the user referenced by the JWT is present in the database."""
    try:
        user = UserService(UserDAO()).get_user_by_id(user_id)
    except DatabaseError:
        logger.error("Database error while verifying user_id=%s", user_id)
        raise HTTPException(status_code=503, detail="Something went wrong. Please try again.")

    if user is None:
        logger.warning("JWT references unknown user_id=%s", user_id)
        raise HTTPException(status_code=401, detail="User not found")
