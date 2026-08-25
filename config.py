import os

from dotenv import load_dotenv

load_dotenv(".env.local")


class Config:
    """Centralised configuration loaded from environment variables.

    All application components must read values from this class — never
    call ``os.environ`` directly in any module.
    """

    # General
    SETUP_ENV: str = os.environ.get("SETUP_ENV", "local")
    SECRET_KEY: str = os.environ.get("SECRET_KEY", "")

    # Cloudflare Turnstile
    TURNSTILE_SITE_KEY: str = os.environ.get("TURNSTILE_SITE_KEY", "")
    TURNSTILE_SECRET_KEY: str = os.environ.get("TURNSTILE_SECRET_KEY", "")

    # Cookies
    COOKIE_SECURE: bool = os.environ.get("COOKIE_SECURE", "false").lower() == "true"

    # /docs Basic Auth
    DOCS_USERNAME: str = os.environ.get("DOCS_USERNAME", "")
    DOCS_PASSWORD: str = os.environ.get("DOCS_PASSWORD", "")

    # PostgreSQL
    DATABASE_URL: str = os.environ.get("DATABASE_URL")

    # Weaviate
    WEAVIATE_HOST: str = os.environ.get("WEAVIATE_HOST")
    WEAVIATE_PORT: int = int(os.environ.get("WEAVIATE_PORT", "8080"))
    WEAVIATE_GRPC_HOST: str = os.environ.get("WEAVIATE_GRPC_HOST", "localhost")
    WEAVIATE_GRPC_PORT: int = int(os.environ.get("WEAVIATE_GRPC_PORT", "50051"))

    # OpenAI
    OPENAI_API_KEY: str = os.environ.get("OPENAI_API_KEY", "")
    OPENAI_TIMEOUT: int = int(os.environ.get("OPENAI_TIMEOUT", "60"))

    # External API timeouts
    TURNSTILE_API_TIMEOUT: int = int(os.environ.get("TURNSTILE_API_TIMEOUT", "10"))

    # Rate limiting
    CHAT_RATE_LIMIT: str = os.environ.get("CHAT_RATE_LIMIT", "20")
    AUTH_RATE_LIMIT: str = os.environ.get("AUTH_RATE_LIMIT", "10")


    # Spend alerting
    SPEND_ALERT_THRESHOLD: float = float(os.environ.get("SPEND_ALERT_THRESHOLD", "5.0"))
    ALERT_EMAIL: str = os.environ.get("ALERT_EMAIL", "")

    # Hard daily spend cap — blank/unset means no cap is enforced, so chat is
    # never blocked unless a value is explicitly configured.
    DAILY_SPEND_CAP_USD: float | None = (
        float(os.environ.get("DAILY_SPEND_CAP_USD"))
        if os.environ.get("DAILY_SPEND_CAP_USD")
        else None
    )

    # SMTP
    SMTP_HOST: str = os.environ.get("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT: int = int(os.environ.get("SMTP_PORT", "587"))
    SMTP_USER: str = os.environ.get("SMTP_USER", "")
    SMTP_PASSWORD: str = os.environ.get("SMTP_PASSWORD", "")

    # Phoenix observability
    PHOENIX_HOST: str = os.environ.get("PHOENIX_HOST", "localhost")
    PHOENIX_PORT: int = int(os.environ.get("PHOENIX_PORT", "6006"))
    PHOENIX_GRPC_PORT: int = int(os.environ.get("PHOENIX_GRPC_PORT", "4317"))


config = Config()
