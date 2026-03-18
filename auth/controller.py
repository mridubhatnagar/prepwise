import logging

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse, RedirectResponse

from auth.dao import AccessAttemptDAO, AllowedUserDAO, UserDAO
from auth.service import AccessAttemptService, AllowedUserService, AuthService, UserService
from config import config
from dependencies import get_current_user
from exceptions import DatabaseError, OAuthError
from limiter import limiter

logger = logging.getLogger(__name__)

router = APIRouter(tags=["auth"])


def get_user_dao() -> UserDAO:
    return UserDAO()


def get_allowed_user_dao() -> AllowedUserDAO:
    return AllowedUserDAO()


def get_access_attempt_dao() -> AccessAttemptDAO:
    return AccessAttemptDAO()


def get_user_service(user_dao: UserDAO = Depends(get_user_dao)) -> UserService:
    return UserService(user_dao=user_dao)


def get_allowed_user_service(
    allowed_user_dao: AllowedUserDAO = Depends(get_allowed_user_dao),
) -> AllowedUserService:
    return AllowedUserService(allowed_user_dao=allowed_user_dao)


def get_access_attempt_service(
    access_attempt_dao: AccessAttemptDAO = Depends(get_access_attempt_dao),
) -> AccessAttemptService:
    return AccessAttemptService(access_attempt_dao=access_attempt_dao)


def get_auth_service(
    user_service: UserService = Depends(get_user_service),
    allowed_user_service: AllowedUserService = Depends(get_allowed_user_service),
    access_attempt_service: AccessAttemptService = Depends(get_access_attempt_service),
) -> AuthService:
    return AuthService(
        user_service=user_service,
        allowed_user_service=allowed_user_service,
        access_attempt_service=access_attempt_service,
    )


@router.get("/api/auth/initiate")
@limiter.limit(f"{config.AUTH_RATE_LIMIT}/minute")
async def initiate_oauth(
    request: Request,
    auth_service: AuthService = Depends(get_auth_service),
):
    """Generate an anti-CSRF state nonce, store it in an HttpOnly cookie, and
    redirect the browser to Google's consent URL.

    Rate limited to ``AUTH_RATE_LIMIT`` requests per minute per IP address.
    """
    google_auth_url, state = auth_service.prepare_oauth_redirect()

    response = RedirectResponse(url=google_auth_url, status_code=302)
    response.set_cookie(
        key="oauth_state",
        value=state,
        httponly=True,
        samesite="lax",
        max_age=300,
        secure=config.JWT_COOKIE_SECURE,
    )
    return response


@router.get("/auth/callback")
async def oauth_callback(
    request: Request,
    code: str = "",
    state: str = "",
    error: str = "",
    auth_service: AuthService = Depends(get_auth_service),
):
    """Handle the Google OAuth redirect, verify state, issue JWT cookie, and
    redirect to ``/chat`` on success or ``/`` with an error param on failure.
    """
    stored_state = request.cookies.get("oauth_state", "")

    def _redirect(url: str) -> RedirectResponse:
        """Return a redirect response that also clears the oauth_state cookie."""
        resp = RedirectResponse(url=url, status_code=302)
        resp.delete_cookie("oauth_state")
        return resp

    if error:
        logger.warning("Google OAuth returned error param: %s", error)
        return _redirect("/?error=auth_failed")

    try:
        user, token = auth_service.handle_oauth_callback(
            code=code,
            state=state,
            stored_state=stored_state,
        )
    except OAuthError as exc:
        logger.warning("OAuth callback failed: %s", exc)
        return _redirect("/?error=auth_failed")
    except ValueError:
        # Unverified Google email — handle_oauth_callback logged the detail.
        return _redirect("/?error=unverified_email")
    except PermissionError:
        # Email not in allowlist — handle_oauth_callback logged the detail.
        return _redirect("/?error=invite_only")
    except DatabaseError:
        logger.error("Database error during OAuth callback")
        return _redirect("/?error=auth_failed")
    response = _redirect("/chat")
    response.set_cookie(
        key="jwt",
        value=token,
        httponly=True,
        samesite="lax",
        max_age=config.JWT_EXPIRY_SECONDS,
        secure=config.JWT_COOKIE_SECURE,
    )
    return response


@router.post("/api/auth/logout")
async def logout(user=Depends(get_current_user)):
    """Clear the JWT cookie and confirm sign-out."""
    logger.info("User id=%s signed out", user.id)
    response = JSONResponse({"success": True, "data": None, "error": None})
    response.delete_cookie("jwt")
    return response


@router.get("/api/auth/me")
async def get_me(
    user=Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
):
    """Return the authenticated user's profile."""
    try:
        db_user = user_service.get_user_by_id(user.id)
    except DatabaseError:
        logger.error("Database error fetching profile for user_id=%s", user.id)
        raise HTTPException(
            status_code=503, detail="Something went wrong. Please try again."
        )

    if db_user is None:
        raise HTTPException(status_code=401, detail="User not found")

    return {
        "success": True,
        "data": {
            "user": {
                "id": str(db_user.id),
                "name": db_user.name,
                "email": db_user.email,
                "avatar_url": db_user.avatar_url,
            }
        },
        "error": None,
    }
