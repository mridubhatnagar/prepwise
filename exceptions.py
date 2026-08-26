class DatabaseError(Exception):
    """Raised when a PostgreSQL database operation fails."""


class EmbeddingError(Exception):
    """Raised when the OpenAI embedding API call fails."""


class RetrievalError(Exception):
    """Raised when a Weaviate retrieval or connection operation fails."""


class LLMError(Exception):
    """Raised when the OpenAI LLM API call fails or returns an unparseable response."""


class OAuthError(Exception):
    """Raised when Google OAuth state verification or token exchange fails."""


class TurnstileError(Exception):
    """Raised when the Cloudflare Turnstile siteverify request fails."""
