import logging

from fastapi import Depends, HTTPException

from dependencies import get_current_user
from enums import Scope

logger = logging.getLogger(__name__)


def require_scope(scope: Scope):
    """Return a FastAPI dependency that enforces the required scope.

    Usage::

        @router.get("/api/chat/messages")
        def get_messages(user = Depends(require_scope(Scope.APP))):
            ...

    Raises ``HTTPException(403)`` when the authenticated user's scopes do not
    include ``scope``.  ``get_current_user`` (called first in the chain) raises
    ``HTTPException(401)`` for missing or invalid tokens.
    """

    def dependency(user=Depends(get_current_user)):
        if scope not in user.scopes:
            logger.warning("Scope rejection: user_id=%s required=%s has=%s", user.id, scope, user.scopes)
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return user

    return dependency
