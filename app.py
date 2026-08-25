import logging

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from access.dependencies import require_visitor
from config import config
from constants import FEEDBACK_CHANGE_LIMIT
from dependencies import verify_docs_credentials
from infra.postgres import SessionLocal
from limiter import limiter

logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""

    if SessionLocal is None:
        raise RuntimeError("DATABASE_URL is not set — cannot start application")

    _setup_phoenix_tracing()

    app = FastAPI(
        title="PrepWise",
        docs_url=None,   # served manually at /docs with scope check
        redoc_url=None,
    )

    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    @app.middleware("http")
    async def add_security_headers(request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        return response

    app.mount("/static", StaticFiles(directory="static"), name="static")

    templates = Jinja2Templates(directory="templates")

    @app.get("/", include_in_schema=False)
    async def landing_page(request: Request):
        return templates.TemplateResponse("landing.html", {
            "request": request,
            "turnstile_site_key": config.TURNSTILE_SITE_KEY,
        })

    @app.get("/chat", include_in_schema=False)
    async def chat(request: Request):
        try:
            require_visitor(request)
        except HTTPException:
            return RedirectResponse(url="/", status_code=302)

        return templates.TemplateResponse("chat.html", {
            "request": request,
            "feedback_change_limit": FEEDBACK_CHANGE_LIMIT,
        })

    @app.get("/docs", include_in_schema=False)
    async def docs(credentials: str = Depends(verify_docs_credentials)):
        return get_swagger_ui_html(openapi_url="/openapi.json", title="PrepWise API Docs")

    @app.exception_handler(403)
    async def forbidden_handler(request: Request, exc):
        return FileResponse("templates/error.html", status_code=403)

    @app.exception_handler(404)
    async def not_found_handler(request: Request, exc):
        return FileResponse("templates/error.html", status_code=404)

    @app.get("/health", tags=["health"])
    async def health():
        return {"success": True, "data": {"status": "ok"}, "error": None}

    from access.controller import router as access_router
    from chat.controller import router as chat_router
    from documents.controller import router as documents_router
    from feedback.controller import router as feedback_router

    app.include_router(access_router)
    app.include_router(chat_router)
    app.include_router(documents_router)
    app.include_router(feedback_router)

    return app


def _setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )


def _setup_phoenix_tracing() -> None:
    """Initialise Arize Phoenix OTEL tracing and OpenAI instrumentation.

    Uses the ``phoenix.otel.register`` helper so traces are exported to the
    self-hosted Phoenix instance.  Failures are caught and logged — a tracing
    outage must never prevent the app from starting.
    """
    try:
        from openinference.instrumentation.openai import OpenAIInstrumentor
        from phoenix.otel import register

        endpoint = f"http://{config.PHOENIX_HOST}:{config.PHOENIX_PORT}/v1/traces"
        project_name = f"prepwise-{config.SETUP_ENV}"
        tracer_provider = register(
            project_name=project_name,
            endpoint=endpoint,
        )
        OpenAIInstrumentor().instrument(tracer_provider=tracer_provider)
        logger.info("Phoenix tracing initialised (endpoint=%s)", endpoint)
    except Exception as exc:
        logger.warning("Phoenix tracing setup failed — continuing without tracing: %s", exc)


_setup_logging()
app = create_app()
