from __future__ import annotations

import logging
import uuid
from abc import ABC, abstractmethod

from sqlalchemy import func
from sqlalchemy.exc import OperationalError, IntegrityError, DatabaseError as SADatabaseError

from enums import MessageRole
from exceptions import DatabaseError
from infra.postgres import SessionLocal
from chat.models import ChatMessage, ChatSession

logger = logging.getLogger(__name__)


class IChatMessageDAO(ABC):
    @abstractmethod
    def create(
        self,
        session_id: str,
        visitor_id: str,
        role: MessageRole,
        content: str,
        token_count: int,
        citations: list | None,
        follow_up_questions: list | None,
    ) -> ChatMessage: ...

    @abstractmethod
    def list(self, visitor_id: str, limit: int | None = None) -> list[ChatMessage]: ...

    @abstractmethod
    def list_by_session_id(self, session_id: str) -> list[ChatMessage]: ...

    @abstractmethod
    def get_current_context_details(self, session_id: str) -> dict: ...

    @abstractmethod
    def get_by_id(self, message_id: str) -> ChatMessage | None: ...


class ChatMessageDAO(IChatMessageDAO):
    def __init__(self):
        self.db = SessionLocal()

    def __del__(self):
        self.db.close()

    def create(
        self,
        session_id: str,
        visitor_id: str,
        role: MessageRole,
        content: str,
        token_count: int,
        citations: list | None,
        follow_up_questions: list | None,
    ) -> ChatMessage:
        """Persist a new chat message.

        message_index is MAX(message_index) + 1 for this visitor, or 0 if no prior messages.
        """
        try:
            max_index = (
                self.db.query(func.max(ChatMessage.message_index))
                .filter(ChatMessage.visitor_id == uuid.UUID(visitor_id))
                .scalar()
            )
            next_index = 0 if max_index is None else max_index + 1

            message = ChatMessage(
                id=uuid.uuid4(),
                session_id=uuid.UUID(session_id),
                visitor_id=uuid.UUID(visitor_id),
                role=role,
                content=content,
                token_count=token_count,
                citations=citations,
                follow_up_questions=follow_up_questions,
                message_index=next_index,
            )
            self.db.add(message)
            self.db.commit()
            self.db.refresh(message)
            return message
        except (OperationalError, IntegrityError, SADatabaseError) as exc:
            logger.error("ChatMessageDAO.create failed for visitor_id=%s: %s", visitor_id, exc)
            raise DatabaseError("Failed to create chat message") from exc

    def list(self, visitor_id: str, limit: int = None) -> list[ChatMessage]:
        try:
            query = (
                self.db.query(ChatMessage)
                .filter(ChatMessage.visitor_id == uuid.UUID(visitor_id))
                .order_by(ChatMessage.message_index.asc())
            )
            if limit is not None:
                subq = query.order_by(ChatMessage.message_index.desc()).limit(limit).subquery()
                query = (
                    self.db.query(ChatMessage)
                    .filter(ChatMessage.id.in_(self.db.query(subq.c.id)))
                    .order_by(ChatMessage.message_index.asc())
                )
            return query.all()
        except (OperationalError, SADatabaseError) as exc:
            logger.error("ChatMessageDAO.list failed for visitor_id=%s: %s", visitor_id, exc)
            raise DatabaseError("Failed to list chat messages") from exc

    def list_by_session_id(self, session_id: str) -> list[ChatMessage]:
        try:
            return (
                self.db.query(ChatMessage)
                .filter(ChatMessage.session_id == uuid.UUID(session_id))
                .order_by(ChatMessage.message_index.asc())
                .all()
            )
        except (OperationalError, SADatabaseError) as exc:
            logger.error(
                "ChatMessageDAO.list_by_session_id failed for session_id=%s: %s",
                session_id,
                exc,
            )
            raise DatabaseError("Failed to list chat messages for session") from exc

    def get_current_context_details(self, session_id: str) -> dict:
        """Return message count and cumulative token count for a session.

        Returns a dict with keys: message_count, token_count.
        """
        try:
            row = (
                self.db.query(
                    func.count(ChatMessage.id).label("message_count"),
                    func.coalesce(func.sum(ChatMessage.token_count), 0).label("token_count"),
                )
                .filter(ChatMessage.session_id == uuid.UUID(session_id))
                .one()
            )
            return {
                "message_count": row.message_count,
                "token_count": row.token_count,
            }
        except (OperationalError, SADatabaseError) as exc:
            logger.error(
                "ChatMessageDAO.get_current_context_details failed for session_id=%s: %s",
                session_id,
                exc,
            )
            raise DatabaseError("Failed to fetch context details") from exc

    def get_by_id(self, message_id: str) -> ChatMessage | None:
        try:
            return self.db.get(ChatMessage, uuid.UUID(message_id))
        except (OperationalError, SADatabaseError) as exc:
            logger.error(
                "ChatMessageDAO.get_by_id failed for message_id=%s: %s", message_id, exc
            )
            raise DatabaseError("Failed to fetch chat message") from exc


class IChatSessionDAO(ABC):
    @abstractmethod
    def create(self, visitor_id: str) -> ChatSession: ...

    @abstractmethod
    def get_active(self, visitor_id: str) -> ChatSession | None: ...

    @abstractmethod
    def update_status(self, session_id: str, is_active: bool) -> None: ...


class ChatSessionDAO(IChatSessionDAO):
    def __init__(self):
        self.db = SessionLocal()

    def __del__(self):
        self.db.close()

    def create(self, visitor_id: str) -> ChatSession:
        try:
            session = ChatSession(
                id=uuid.uuid4(),
                visitor_id=uuid.UUID(visitor_id),
                is_active=True,
            )
            self.db.add(session)
            self.db.commit()
            self.db.refresh(session)
            return session
        except (OperationalError, IntegrityError, SADatabaseError) as exc:
            logger.error("ChatSessionDAO.create failed for visitor_id=%s: %s", visitor_id, exc)
            raise DatabaseError("Failed to create chat session") from exc

    def get_active(self, visitor_id: str) -> ChatSession | None:
        try:
            return (
                self.db.query(ChatSession)
                .filter(
                    ChatSession.visitor_id == uuid.UUID(visitor_id),
                    ChatSession.is_active.is_(True),
                )
                .first()
            )
        except (OperationalError, SADatabaseError) as exc:
            logger.error(
                "ChatSessionDAO.get_active failed for visitor_id=%s: %s", visitor_id, exc
            )
            raise DatabaseError("Failed to fetch active chat session") from exc

    def update_status(self, session_id: str, is_active: bool) -> None:
        try:
            session = self.db.get(ChatSession, uuid.UUID(session_id))
            if session is None:
                logger.warning(
                    "ChatSessionDAO.update_status: session_id=%s not found", session_id
                )
                return
            session.is_active = is_active
            self.db.commit()
        except (OperationalError, SADatabaseError) as exc:
            logger.error(
                "ChatSessionDAO.update_status failed for session_id=%s: %s", session_id, exc
            )
            raise DatabaseError("Failed to update chat session status") from exc
