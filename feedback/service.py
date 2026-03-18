import logging

from opentelemetry import trace

from feedback.dao import IFeedbackDAO
from feedback.models import Feedback

logger = logging.getLogger(__name__)

_tracer = trace.get_tracer(__name__)


class FeedbackService:
    def __init__(self, feedback_dao: IFeedbackDAO):
        self.feedback_dao = feedback_dao

    def get_by_message_id(self, message_id: str) -> Feedback | None:
        return self.feedback_dao.get_by_message_id(message_id)

    def get_ratings_by_message_ids(self, message_ids: list[str]) -> dict[str, str]:
        """Return a map of message_id → rating for all messages that have feedback."""
        feedbacks = self.feedback_dao.get_by_message_ids(message_ids)
        return {str(f.message_id): f.rating for f in feedbacks}

    def create_feedback(self, message_id: str, user_id: str, rating: str) -> Feedback:
        return self.feedback_dao.create(message_id=message_id, user_id=user_id, rating=rating)

    def update_feedback(self, feedback_id: str, rating: str) -> Feedback:
        return self.feedback_dao.update(feedback_id=feedback_id, rating=rating)

    def delete_feedback(self, feedback_id: str) -> None:
        self.feedback_dao.delete_by_id(feedback_id=feedback_id)

    def submit_feedback(self, user_id: str, message_id: str, rating: str | None) -> None:
        """Upsert or delete feedback for a message.

        If rating is None, existing feedback is removed.
        If rating is non-null and no feedback exists, a new row is created.
        If rating is non-null and feedback already exists, it is updated.
        A Phoenix OTEL span is emitted for each call.
        """
        with _tracer.start_as_current_span("feedback.submit") as span:
            span.set_attribute("message_id", message_id)
            span.set_attribute("user_id", user_id)
            span.set_attribute("rating", rating if rating is not None else "null")

            existing = self.get_by_message_id(message_id)

            if rating is None:
                if existing is not None:
                    self.delete_feedback(str(existing.id))
                    logger.info(
                        "Feedback removed for message_id=%s user_id=%s", message_id, user_id
                    )
                return

            if existing is None:
                self.create_feedback(message_id=message_id, user_id=user_id, rating=rating)
                logger.info(
                    "Feedback created for message_id=%s user_id=%s rating=%s",
                    message_id,
                    user_id,
                    rating,
                )
            else:
                self.update_feedback(feedback_id=str(existing.id), rating=rating)
                logger.info(
                    "Feedback updated for message_id=%s user_id=%s rating=%s",
                    message_id,
                    user_id,
                    rating,
                )
