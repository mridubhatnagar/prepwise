import logging

from chat.dao import IChatMessageDAO, IChatSessionDAO
from chat.models import ChatMessage, ChatSession
from constants import CONTEXT_MESSAGE_LIMIT, CONTEXT_TOKEN_LIMIT
from enums import MessageRole

logger = logging.getLogger(__name__)


class ChatService:
    def __init__(self, chat_message_dao: IChatMessageDAO):
        self.chat_message_dao = chat_message_dao

    def get_chat_context_details(self, session_id: str) -> dict:
        """Return context consumption details for a session.

        Returns a dict with keys: message_count, token_count, limit_reached.
        limit_reached is True when message_count >= 20 OR token_count >= 2000.
        """
        details = self.chat_message_dao.get_current_context_details(session_id)
        limit_reached = (
            details["message_count"] >= CONTEXT_MESSAGE_LIMIT
            or details["token_count"] >= CONTEXT_TOKEN_LIMIT
        )
        return {
            "message_count": details["message_count"],
            "token_count": details["token_count"],
            "limit_reached": limit_reached,
        }

    def list_chat_messages(self, user_id: str, limit: int | None = None) -> list[ChatMessage]:
        return self.chat_message_dao.list(user_id, limit)

    def list_chat_messages_by_session(self, session_id: str) -> list[ChatMessage]:
        return self.chat_message_dao.list_by_session_id(session_id)

    def create_chat_message(
        self,
        session_id: str,
        user_id: str,
        role: MessageRole,
        content: str,
        token_count: int,
        citations: list | None = None,
        follow_up_questions: list | None = None,
    ) -> ChatMessage:
        return self.chat_message_dao.create(
            session_id=session_id,
            user_id=user_id,
            role=role,
            content=content,
            token_count=token_count,
            citations=citations,
            follow_up_questions=follow_up_questions,
        )

    def get_message_by_id(self, message_id: str) -> ChatMessage | None:
        return self.chat_message_dao.get_by_id(message_id)


class ChatSessionService:
    def __init__(self, chat_session_dao: IChatSessionDAO):
        self.chat_session_dao = chat_session_dao

    def get_active_session(self, user_id: str) -> ChatSession | None:
        return self.chat_session_dao.get_active(user_id)

    def create_session(self, user_id: str) -> ChatSession:
        session = self.chat_session_dao.create(user_id)
        logger.info("Created new chat session session_id=%s for user_id=%s", session.id, user_id)
        return session

    def update_session_status(self, session_id: str, is_active: bool) -> None:
        self.chat_session_dao.update_status(session_id, is_active)
