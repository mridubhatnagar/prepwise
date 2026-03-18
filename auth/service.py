import logging
import secrets
from urllib.parse import urlencode

import httpx

from auth.dao import IAccessAttemptDAO, IAllowedUserDAO, IUserDAO
from auth.models import AllowedUser, User
from auth.utils import generate_jwt_token
from config import config
from constants import GOOGLE_AUTH_URL, GOOGLE_TOKEN_URL, GOOGLE_USERINFO_URL
from exceptions import OAuthError

logger = logging.getLogger(__name__)


class UserService:
    def __init__(self, user_dao: IUserDAO):
        self.user_dao = user_dao

    def get_user_by_auth_id(self, google_auth_id: str) -> User | None:
        return self.user_dao.get_by_auth_id(google_auth_id)

    def get_user_by_id(self, user_id: str) -> User | None:
        return self.user_dao.get_by_id(user_id)

    def create_user(self, google_auth_id: str, email: str, name: str, avatar_url: str) -> User:
        return self.user_dao.create(
            google_auth_id=google_auth_id,
            email=email,
            name=name,
            avatar_url=avatar_url,
        )

    def update_user(self, user_id: str, name: str, avatar_url: str) -> User:
        return self.user_dao.update(user_id=user_id, name=name, avatar_url=avatar_url)


class AllowedUserService:
    def __init__(self, allowed_user_dao: IAllowedUserDAO):
        self.allowed_user_dao = allowed_user_dao

    def is_user_allowed(self, email: str) -> AllowedUser | None:
        return self.allowed_user_dao.is_allowed(email)


class AccessAttemptService:
    def __init__(self, access_attempt_dao: IAccessAttemptDAO):
        self.access_attempt_dao = access_attempt_dao

    def create_user_access_attempt(self, email: str) -> None:
        self.access_attempt_dao.create(email)


class AuthService:
    def __init__(
        self,
        user_service: UserService,
        allowed_user_service: AllowedUserService,
        access_attempt_service: AccessAttemptService,
    ):
        self.user_service = user_service
        self.allowed_user_service = allowed_user_service
        self.access_attempt_service = access_attempt_service

    def prepare_oauth_redirect(self) -> tuple[str, str]:
        """Generate an anti-CSRF state nonce and the Google consent URL.

        Returns:
            A tuple of ``(google_auth_url, state)`` where ``state`` is a
            cryptographically random hex string that the caller should store in
            an HttpOnly cookie and Google will echo back on the callback.
        """
        state = secrets.token_hex(32)
        params = {
            "client_id": config.GOOGLE_CLIENT_ID,
            "redirect_uri": config.GOOGLE_REDIRECT_URI,
            "response_type": "code",
            "scope": "openid email profile",
            "state": state,
            "access_type": "offline",
            "prompt": "select_account",
        }
        google_auth_url = f"{GOOGLE_AUTH_URL}?{urlencode(params)}"
        return google_auth_url, state

    def fetch_oauth_user_info(self, code: str, state: str, stored_state: str) -> dict:
        """Verify the OAuth state and exchange the code for user info from Google.

        Args:
            code: The authorisation code received from Google.
            state: The state value echoed back by Google in the callback URL.
            stored_state: The state value stored in the HttpOnly ``oauth_state`` cookie.

        Returns:
            A dict containing the raw Google userinfo payload
            (``sub``, ``email``, ``email_verified``, ``name``, ``picture``).

        Raises:
            OAuthError: On CSRF state mismatch, network failure, or non-200
                response from any Google endpoint.
        """
        if state != stored_state:
            logger.warning("OAuth state mismatch — possible CSRF attempt")
            raise OAuthError("State mismatch")

        try:
            token_response = httpx.post(
                GOOGLE_TOKEN_URL,
                data={
                    "code": code,
                    "client_id": config.GOOGLE_CLIENT_ID,
                    "client_secret": config.GOOGLE_CLIENT_SECRET,
                    "redirect_uri": config.GOOGLE_REDIRECT_URI,
                    "grant_type": "authorization_code",
                },
                timeout=config.GOOGLE_API_TIMEOUT,
            )
        except httpx.HTTPError as exc:
            logger.error("Google token endpoint request failed: %s", exc)
            raise OAuthError("Failed to reach Google token endpoint") from exc

        if token_response.status_code != 200:
            logger.error(
                "Google token endpoint returned %s: %s",
                token_response.status_code,
                token_response.text,
            )
            raise OAuthError("Google token exchange failed")

        access_token = token_response.json().get("access_token")

        try:
            userinfo_response = httpx.get(
                GOOGLE_USERINFO_URL,
                headers={"Authorization": f"Bearer {access_token}"},
                timeout=config.GOOGLE_API_TIMEOUT,
            )
        except httpx.HTTPError as exc:
            logger.error("Google userinfo request failed: %s", exc)
            raise OAuthError("Failed to reach Google userinfo endpoint") from exc

        if userinfo_response.status_code != 200:
            logger.error(
                "Google userinfo endpoint returned %s: %s",
                userinfo_response.status_code,
                userinfo_response.text,
            )
            raise OAuthError("Google userinfo request failed")

        return userinfo_response.json()

    def handle_oauth_callback(
        self, code: str, state: str, stored_state: str
    ) -> tuple[User, str]:
        """Orchestrate the full OAuth callback: verify identity, check allowlist, upsert user, issue JWT.

        Args:
            code: The authorisation code from Google.
            state: The state echoed back by Google.
            stored_state: The state stored in the ``oauth_state`` cookie.

        Returns:
            A tuple of ``(user, jwt_token)``.

        Raises:
            OAuthError: Propagated from ``fetch_oauth_user_info`` on state
                mismatch or Google API failure.
            ValueError: When the user's email is not verified by Google.
            PermissionError: When the user's email is not in the allowlist.
        """
        user_info = self.fetch_oauth_user_info(code, state, stored_state)

        if not user_info.get("email_verified"):
            logger.warning(
                "OAuth callback: unverified email=%s", user_info.get("email")
            )
            raise ValueError("Email not verified")

        email = user_info["email"]
        allowed_user = self.allowed_user_service.is_user_allowed(email)

        if allowed_user is None:
            logger.warning("OAuth callback: invite-only rejection for email=%s", email)
            self.access_attempt_service.create_user_access_attempt(email)
            raise PermissionError("User not in allowlist")

        google_auth_id = user_info["sub"]
        name = user_info.get("name", "")
        avatar_url = user_info.get("picture", "")

        existing_user = self.user_service.get_user_by_auth_id(google_auth_id)

        if existing_user is None:
            user = self.user_service.create_user(
                google_auth_id=google_auth_id,
                email=email,
                name=name,
                avatar_url=avatar_url,
            )
            logger.info("New user created via OAuth: email=%s", email)
        else:
            profile_changed = (
                existing_user.name != name or existing_user.avatar_url != avatar_url
            )
            if profile_changed:
                user = self.user_service.update_user(
                    user_id=str(existing_user.id),
                    name=name,
                    avatar_url=avatar_url,
                )
            else:
                user = existing_user
            logger.info("Existing user signed in via OAuth: email=%s", email)

        scopes = [s.strip() for s in allowed_user.scope.split(",") if s.strip()]
        token = generate_jwt_token(user_id=str(user.id), scopes=scopes)

        return user, token
