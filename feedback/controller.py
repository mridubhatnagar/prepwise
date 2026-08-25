import logging
import uuid
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, field_validator

from access.dependencies import require_visitor
from chat.dao import ChatMessageDAO, IChatMessageDAO
from chat.service import ChatService
from exceptions import DatabaseError
from feedback.dao import FeedbackDAO, IFeedbackDAO
from feedback.service import FeedbackService

logger = logging.getLogger(__name__)

router = APIRouter(tags=["feedback"])


class _FeedbackData(BaseModel):
    message_id: str
    rating: Literal["up", "down"] | None

    @field_validator("message_id")
    @classmethod
    def must_be_valid_uuid(cls, v: str) -> str:
        try:
            uuid.UUID(v)
        except ValueError:
            raise ValueError("message_id must be a valid UUID")
        return v


class PostFeedbackRequest(BaseModel):
    data: _FeedbackData


def get_feedback_dao() -> FeedbackDAO:
    return FeedbackDAO()


def get_chat_message_dao() -> ChatMessageDAO:
    return ChatMessageDAO()


def get_feedback_service(
    feedback_dao: IFeedbackDAO = Depends(get_feedback_dao),
) -> FeedbackService:
    return FeedbackService(feedback_dao=feedback_dao)


def get_chat_service(
    chat_message_dao: IChatMessageDAO = Depends(get_chat_message_dao),
) -> ChatService:
    return ChatService(chat_message_dao=chat_message_dao)


@router.post("/api/feedback")
async def post_feedback(
    body: PostFeedbackRequest,
    visitor=Depends(require_visitor),
    feedback_service: FeedbackService = Depends(get_feedback_service),
    chat_service: ChatService = Depends(get_chat_service),
):
    """Submit, update, or remove a thumbs up/down rating for an AI message.

    rating null deselects existing feedback.
    message_id must belong to the requesting visitor.
    """
    message_id = body.data.message_id
    rating = body.data.rating

    try:
        message = chat_service.get_message_by_id(message_id)
    except DatabaseError:
        raise HTTPException(status_code=503, detail="Something went wrong. Please try again.")

    if message is None or str(message.visitor_id) != str(visitor.id):
        logger.warning(
            "Feedback ownership check failed: message_id=%s visitor_id=%s",
            message_id,
            visitor.id,
        )
        raise HTTPException(status_code=404, detail="Message not found.")

    try:
        feedback_service.submit_feedback(
            visitor_id=str(visitor.id),
            message_id=message_id,
            rating=rating,
        )
    except DatabaseError:
        raise HTTPException(status_code=503, detail="Something went wrong. Please try again.")

    return {"success": True, "data": None, "error": None}
