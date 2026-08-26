import logging
import uuid

import httpx

from config import config
from constants import TURNSTILE_VERIFY_URL
from exceptions import TurnstileError

logger = logging.getLogger(__name__)


class AccessService:
    """Verifies Cloudflare Turnstile tokens and mints anonymous visitor ids.

    Stateless — no DAO is involved. A ``visitor_id`` is just an opaque UUID
    handed back to the caller for cookie storage; the first row referencing it
    is created later, on the first ``chat_sessions`` insert.
    """

    def verify_turnstile_token(self, token: str, remote_ip: str | None = None) -> bool:
        """Verify a client-side Turnstile response token with Cloudflare.

        Args:
            token: The Turnstile response token produced by the widget.
            remote_ip: The requester's IP address, forwarded to Cloudflare as
                an additional (optional) verification signal.

        Returns:
            True if Cloudflare confirms the token is valid, False if the
            token is missing or Cloudflare rejects it.

        Raises:
            TurnstileError: On network failure or a non-200 response from the
                Cloudflare siteverify endpoint.
        """
        if not token:
            logger.warning("Turnstile verification attempted with no token")
            return False

        payload = {
            "secret": config.TURNSTILE_SECRET_KEY,
            "response": token,
        }
        if remote_ip:
            payload["remoteip"] = remote_ip

        try:
            response = httpx.post(
                TURNSTILE_VERIFY_URL,
                data=payload,
                timeout=config.TURNSTILE_API_TIMEOUT,
            )
        except httpx.HTTPError as exc:
            logger.error("Turnstile siteverify request failed: %s", exc)
            raise TurnstileError("Failed to reach Turnstile siteverify endpoint") from exc

        if response.status_code != 200:
            logger.error(
                "Turnstile siteverify returned %s: %s",
                response.status_code,
                response.text,
            )
            raise TurnstileError("Turnstile siteverify request failed")

        result = response.json()
        verified = bool(result.get("success"))
        if not verified:
            logger.warning(
                "Turnstile verification rejected: error-codes=%s",
                result.get("error-codes"),
            )
        return verified

    def mint_visitor_id(self) -> str:
        """Generate a new random opaque visitor id."""
        return str(uuid.uuid4())
