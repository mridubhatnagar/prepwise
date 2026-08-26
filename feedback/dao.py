import logging
import uuid
from abc import ABC, abstractmethod

from sqlalchemy.exc import OperationalError, IntegrityError, DatabaseError as SADatabaseError

from exceptions import DatabaseError
from feedback.models import Feedback
from infra.postgres import SessionLocal

logger = logging.getLogger(__name__)


class IFeedbackDAO(ABC):
    @abstractmethod
    def create(self, message_id: str, visitor_id: str, rating: str) -> Feedback: ...

    @abstractmethod
    def update(self, feedback_id: str, rating: str) -> Feedback: ...

    @abstractmethod
    def delete_by_id(self, feedback_id: str) -> None: ...

    @abstractmethod
    def get_by_id(self, feedback_id: str) -> Feedback | None: ...

    @abstractmethod
    def get_by_message_id(self, message_id: str) -> Feedback | None: ...

    @abstractmethod
    def get_by_message_ids(self, message_ids: list[str]) -> list[Feedback]: ...


class FeedbackDAO(IFeedbackDAO):
    def __init__(self):
        self.db = SessionLocal()

    def __del__(self):
        self.db.close()

    def create(self, message_id: str, visitor_id: str, rating: str) -> Feedback:
        try:
            feedback = Feedback(
                id=uuid.uuid4(),
                message_id=uuid.UUID(message_id),
                visitor_id=uuid.UUID(visitor_id),
                rating=rating,
            )
            self.db.add(feedback)
            self.db.commit()
            self.db.refresh(feedback)
            return feedback
        except (OperationalError, IntegrityError, SADatabaseError) as exc:
            logger.error(
                "FeedbackDAO.create failed for message_id=%s visitor_id=%s: %s",
                message_id,
                visitor_id,
                exc,
            )
            raise DatabaseError("Failed to create feedback") from exc

    def update(self, feedback_id: str, rating: str) -> Feedback:
        try:
            feedback = self.db.get(Feedback, uuid.UUID(feedback_id))
            if feedback is None:
                raise ValueError(f"Feedback {feedback_id} not found")
            feedback.rating = rating
            self.db.commit()
            self.db.refresh(feedback)
            return feedback
        except (OperationalError, SADatabaseError) as exc:
            logger.error(
                "FeedbackDAO.update failed for feedback_id=%s: %s", feedback_id, exc
            )
            raise DatabaseError("Failed to update feedback") from exc

    def delete_by_id(self, feedback_id: str) -> None:
        try:
            feedback = self.db.get(Feedback, uuid.UUID(feedback_id))
            if feedback is not None:
                self.db.delete(feedback)
                self.db.commit()
        except (OperationalError, SADatabaseError) as exc:
            logger.error(
                "FeedbackDAO.delete_by_id failed for feedback_id=%s: %s", feedback_id, exc
            )
            raise DatabaseError("Failed to delete feedback") from exc

    def get_by_id(self, feedback_id: str) -> Feedback | None:
        try:
            return self.db.get(Feedback, uuid.UUID(feedback_id))
        except (OperationalError, SADatabaseError) as exc:
            logger.error(
                "FeedbackDAO.get_by_id failed for feedback_id=%s: %s", feedback_id, exc
            )
            raise DatabaseError("Failed to fetch feedback") from exc

    def get_by_message_id(self, message_id: str) -> Feedback | None:
        try:
            return (
                self.db.query(Feedback)
                .filter(Feedback.message_id == uuid.UUID(message_id))
                .first()
            )
        except (OperationalError, SADatabaseError) as exc:
            logger.error(
                "FeedbackDAO.get_by_message_id failed for message_id=%s: %s",
                message_id,
                exc,
            )
            raise DatabaseError("Failed to fetch feedback by message_id") from exc

    def get_by_message_ids(self, message_ids: list[str]) -> list[Feedback]:
        try:
            uuids = [uuid.UUID(mid) for mid in message_ids]
            return (
                self.db.query(Feedback)
                .filter(Feedback.message_id.in_(uuids))
                .all()
            )
        except (OperationalError, SADatabaseError) as exc:
            logger.error("FeedbackDAO.get_by_message_ids failed: %s", exc)
            raise DatabaseError("Failed to fetch feedbacks by message_ids") from exc
