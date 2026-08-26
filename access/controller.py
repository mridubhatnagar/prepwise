import logging

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from access.service import AccessService
from config import config
from constants import VISITOR_COOKIE_MAX_AGE_SECONDS, VISITOR_COOKIE_NAME
from exceptions import TurnstileError
from limiter import limiter

logger = logging.getLogger(__name__)

router = APIRouter(tags=["access"])


class _VerifyData(BaseModel):
    token: str


class VerifyAccessRequest(BaseModel):
    data: _VerifyData


def get_access_service() -> AccessService:
    return AccessService()


@router.post("/api/access/verify")
@limiter.limit(f"{config.AUTH_RATE_LIMIT}/minute")
async def verify_access(
    request: Request,
    body: VerifyAccessRequest,
    access_service: AccessService = Depends(get_access_service),
):
    """Verify a Cloudflare Turnstile token and, on success, mint a visitor_id cookie.

    Stateless: no database row is created here. The first row referencing
    this visitor_id is created later, on the first ``chat_sessions`` insert.

    Rate limited to ``AUTH_RATE_LIMIT`` requests per minute per IP address.
    """
    try:
        verified = access_service.verify_turnstile_token(
            token=body.data.token,
            remote_ip=request.client.host if request.client else None,
        )
    except TurnstileError:
        logger.error("Turnstile verification service failure")
        raise HTTPException(status_code=503, detail="Something went wrong. Please try again.")

    if not verified:
        logger.warning("Turnstile verification rejected — no visitor_id issued")
        raise HTTPException(status_code=401, detail="Verification failed. Please try again.")

    visitor_id = access_service.mint_visitor_id()
    logger.info("Turnstile verification passed — visitor_id=%s minted", visitor_id)

    response = JSONResponse({"success": True, "data": None, "error": None})
    response.set_cookie(
        key=VISITOR_COOKIE_NAME,
        value=visitor_id,
        httponly=True,
        samesite="lax",
        max_age=VISITOR_COOKIE_MAX_AGE_SECONDS,
        secure=config.COOKIE_SECURE,
    )
    return response
