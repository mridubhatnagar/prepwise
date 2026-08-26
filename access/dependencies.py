import logging
import uuid
from dataclasses import dataclass

from fastapi import HTTPException, Request

from constants import VISITOR_COOKIE_NAME

logger = logging.getLogger(__name__)


@dataclass
class Visitor:
    """Represents the anonymous visitor identified by the visitor_id cookie."""

    id: str


def require_visitor(request: Request) -> Visitor:
    """FastAPI dependency that validates the visitor_id cookie and returns the visitor.

    Unlike ``get_current_user``, ``visitor_id`` is an opaque UUID minted by
    ``POST /api/access/verify`` — there is no signature to verify and no
    database row to look up, so this only checks that the cookie is present
    and well-formed.

    Raises:
        HTTPException(401): If the ``visitor_id`` cookie is missing or is not
            a valid UUID.
    """
    visitor_id = _extract_visitor_id(request)
    return Visitor(id=visitor_id)


def _extract_visitor_id(request: Request) -> str:
    """Return the raw visitor_id string from the request cookie."""
    visitor_id = request.cookies.get(VISITOR_COOKIE_NAME)
    if not visitor_id:
        logger.warning("require_visitor rejected: %s cookie missing", VISITOR_COOKIE_NAME)
        raise HTTPException(status_code=401, detail="Visitor verification required")

    try:
        uuid.UUID(visitor_id)
    except ValueError:
        logger.warning("require_visitor rejected: malformed visitor_id cookie value")
        raise HTTPException(status_code=401, detail="Visitor verification required")

    return visitor_id
