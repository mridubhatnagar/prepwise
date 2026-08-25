import logging

from fastapi import APIRouter, Depends, HTTPException, Request

from access.dependencies import require_visitor
from chat.dao import ChatMessageDAO, ChatSessionDAO, IChatMessageDAO, IChatSessionDAO
from chat.request_handler import ChatRequestHandler
from chat.service import ChatService, ChatSessionService
from chat.validators import PostMessageRequest
from config import config
from constants import VISITOR_COOKIE_NAME
from enums import MessageRole
from exceptions import (
    DatabaseError,
    EmbeddingError,
    LLMError,
    RetrievalError,
    SpendCapExceededError,
)
from feedback.dao import FeedbackDAO, IFeedbackDAO
from feedback.service import FeedbackService
from limiter import limiter
from rag.llm_client import LLMClient
from rag.orchestrator import RAGOrchestrator
from rag.retrieval_client import RetrievalClient
from spend.dao import ISpendDAO, SpendDAO
from spend.service import SpendService

logger = logging.getLogger(__name__)

router = APIRouter(tags=["chat"])


def get_chat_message_dao() -> ChatMessageDAO:
    return ChatMessageDAO()


def get_chat_session_dao() -> ChatSessionDAO:
    return ChatSessionDAO()


def get_spend_dao() -> SpendDAO:
    return SpendDAO()


def get_feedback_dao() -> FeedbackDAO:
    return FeedbackDAO()


def get_feedback_service(
    feedback_dao: IFeedbackDAO = Depends(get_feedback_dao),
) -> FeedbackService:
    return FeedbackService(feedback_dao=feedback_dao)


def get_chat_service(
    chat_message_dao: IChatMessageDAO = Depends(get_chat_message_dao),
) -> ChatService:
    return ChatService(chat_message_dao=chat_message_dao)


def get_chat_session_service(
    chat_session_dao: IChatSessionDAO = Depends(get_chat_session_dao),
) -> ChatSessionService:
    return ChatSessionService(chat_session_dao=chat_session_dao)


def get_spend_service(
    spend_dao: ISpendDAO = Depends(get_spend_dao),
) -> SpendService:
    return SpendService(spend_dao=spend_dao)


def get_rag_orchestrator() -> RAGOrchestrator:
    return RAGOrchestrator(
        retrieval_client=RetrievalClient(),
        llm_client=LLMClient(),
    )


def get_chat_request_handler(
    chat_service: ChatService = Depends(get_chat_service),
    rag_orchestrator: RAGOrchestrator = Depends(get_rag_orchestrator),
    spend_service: SpendService = Depends(get_spend_service),
) -> ChatRequestHandler:
    return ChatRequestHandler(
        chat_service=chat_service,
        rag_orchestrator=rag_orchestrator,
        spend_service=spend_service,
    )


def _get_visitor_id_key(request: Request) -> str:
    """Return the visitor_id cookie value for per-visitor rate limiting.

    Falls back to the remote IP address if the cookie is missing.
    """
    visitor_id = request.cookies.get(VISITOR_COOKIE_NAME)
    if visitor_id:
        return visitor_id

    return request.client.host if request.client else "unknown"


def _resolve_session(visitor_id: str, chat_session_service: ChatSessionService) -> str:
    """Return the active session_id for the visitor, creating one if none exists."""
    session = chat_session_service.get_active_session(visitor_id)
    if session is None:
        session = chat_session_service.create_session(visitor_id)
    return str(session.id)


@router.post("/api/chat/messages")
@limiter.limit(f"{config.CHAT_RATE_LIMIT}/minute", key_func=_get_visitor_id_key)
async def post_message(
    request: Request,
    body: PostMessageRequest,
    visitor=Depends(require_visitor),
    handler: ChatRequestHandler = Depends(get_chat_request_handler),
    chat_session_service: ChatSessionService = Depends(get_chat_session_service),
):
    """Submit a chat message and receive an AI-generated response.

    Rate limited per visitor_id.
    """
    query = body.data.message

    try:
        session_id = _resolve_session(str(visitor.id), chat_session_service)
        result = handler.handle_chat_message(
            visitor_id=str(visitor.id), session_id=session_id, query=query
        )
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Unable to process your request. Please try again.",
        )
    except SpendCapExceededError:
        raise HTTPException(
            status_code=503,
            detail="Chat is temporarily unavailable — we've reached today's usage limit. Please try again tomorrow.",
        )
    except (EmbeddingError, RetrievalError):
        raise HTTPException(
            status_code=503,
            detail="Couldn't reach the knowledge base. Please try again in a moment.",
        )
    except LLMError:
        raise HTTPException(
            status_code=503,
            detail="Couldn't generate a response. Please try again.",
        )
    except DatabaseError:
        raise HTTPException(
            status_code=503,
            detail="Something went wrong. Please try again.",
        )

    return {"success": True, "data": {"message": result}, "error": None}


@router.get("/api/chat/messages")
async def get_messages(
    visitor=Depends(require_visitor),
    handler: ChatRequestHandler = Depends(get_chat_request_handler),
    chat_session_service: ChatSessionService = Depends(get_chat_session_service),
    feedback_service: FeedbackService = Depends(get_feedback_service),
):
    """Return the message history for the visitor's active session."""
    try:
        session_id = _resolve_session(str(visitor.id), chat_session_service)
        messages = handler.list_messages(session_id=session_id)
    except DatabaseError:
        raise HTTPException(
            status_code=503,
            detail="Something went wrong. Please try again.",
        )

    assistant_message_ids = [
        str(msg.id) for msg in messages if msg.role == MessageRole.ASSISTANT
    ]
    ratings = feedback_service.get_ratings_by_message_ids(assistant_message_ids)

    serialized = []
    for msg in messages:
        entry: dict = {
            "id": str(msg.id),
            "role": msg.role.value if isinstance(msg.role, MessageRole) else msg.role,
            "content": msg.content,
            "created_at": msg.created_at.isoformat(),
        }
        if msg.role == MessageRole.ASSISTANT:
            entry["citations"] = msg.citations or []
            entry["follow_up_questions"] = msg.follow_up_questions or []
            entry["rating"] = ratings.get(str(msg.id))
        serialized.append(entry)

    return {
        "success": True,
        "data": {"session_id": session_id, "messages": serialized},
        "error": None,
    }


@router.post("/api/chat/sessions")
async def create_session(
    visitor=Depends(require_visitor),
    chat_session_service: ChatSessionService = Depends(get_chat_session_service),
):
    """Clear Chat — deactivate the current session and create a new one.

    Messages from the previous session are retained in the database.
    """
    try:
        existing = chat_session_service.get_active_session(str(visitor.id))
        if existing is not None:
            chat_session_service.update_session_status(str(existing.id), False)
            logger.info(
                "Deactivated session session_id=%s for visitor_id=%s",
                existing.id,
                visitor.id,
            )

        new_session = chat_session_service.create_session(str(visitor.id))
    except DatabaseError:
        raise HTTPException(
            status_code=503,
            detail="Something went wrong. Please try again.",
        )

    logger.info("Chat cleared for visitor_id=%s new_session_id=%s", visitor.id, new_session.id)
    return {
        "success": True,
        "data": {"session_id": str(new_session.id)},
        "error": None,
    }
