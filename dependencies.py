import logging
import secrets

from fastapi import Depends, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from config import config

logger = logging.getLogger(__name__)

_basic_auth = HTTPBasic()


def verify_docs_credentials(credentials: HTTPBasicCredentials = Depends(_basic_auth)) -> str:
    """FastAPI dependency enforcing HTTP Basic Auth on the ``/docs`` route.

    Checked against ``config.DOCS_USERNAME`` / ``config.DOCS_PASSWORD`` using
    ``secrets.compare_digest`` to avoid timing attacks. There is no per-person
    identity here — a single shared credential gates one internal route.

    Raises:
        HTTPException(401): If the username or password does not match.
    """
    valid_username = secrets.compare_digest(credentials.username, config.DOCS_USERNAME)
    valid_password = secrets.compare_digest(credentials.password, config.DOCS_PASSWORD)
    if not (valid_username and valid_password):
        logger.warning("Docs Basic Auth rejected for username=%s", credentials.username)
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username
