import logging

import tiktoken

from chat.models import ChatMessage
from chat.service import ChatService
from constants import EMBEDDING_MODEL, LLM_HISTORY_WINDOW, LLM_MODEL
from enums import MessageRole
from rag.constants import OUT_OF_SCOPE_ANSWER
from rag.orchestrator import RAGOrchestrator
from spend.service import SpendService

logger = logging.getLogger(__name__)

_CONTEXT_LIMIT_ANSWER = "You've reached the conversation limit. Clear your chat to continue."
_CHAT_ENDPOINT = "/api/chat/messages"


def _count_tokens(text: str) -> int:
    """Return the tiktoken token count for the given text using cl100k_base."""
    enc = tiktoken.get_encoding("cl100k_base")
    return len(enc.encode(text))


class ChatRequestHandler:
    def __init__(
        self,
        chat_service: ChatService,
        rag_orchestrator: RAGOrchestrator,
        spend_service: SpendService,
    ):
        self.chat_service = chat_service
        self.rag_orchestrator = rag_orchestrator
        self.spend_service = spend_service

    def handle_chat_message(self, user_id: str, session_id: str, query: str) -> dict:
        """Orchestrate the full RAG pipeline for a single user query.

        Returns a response dict matching the POST /api/chat/messages envelope:
        { answer, assistant_message_id, citations, follow_up_questions, context_status }
        """
        context_status = self._check_context(session_id)

        if context_status is not None:
            logger.info(
                "Context limit reached for user_id=%s session_id=%s",
                user_id,
                session_id,
            )
            return context_status

        history = self._get_history(session_id)
        response = self._generate_response(query, history)

        assistant_message_id = self._persist(user_id, session_id, query, response)

        if response.get("input_tokens", 0) > 0 or response.get("output_tokens", 0) > 0:
            self._log_spend(user_id, response)

        updated_details = self.chat_service.get_chat_context_details(session_id)

        return {
            "answer": response["answer"],
            "assistant_message_id": assistant_message_id,
            "citations": response["citations"],
            "follow_up_questions": response["follow_up_questions"],
            "context_status": {
                "message_count": updated_details["message_count"],
                "token_count": updated_details["token_count"],
                "limit_reached": updated_details["limit_reached"],
            },
        }

    def list_messages(self, session_id: str) -> list[ChatMessage]:
        return self.chat_service.list_chat_messages_by_session(session_id)

    def _check_context(self, session_id: str) -> dict | None:
        """Return an early-exit response dict if context limit is reached, else None."""
        details = self.chat_service.get_chat_context_details(session_id)
        if not details["limit_reached"]:
            return None

        logger.info(
            "Context limit hit for session_id=%s (messages=%d tokens=%d)",
            session_id,
            details["message_count"],
            details["token_count"],
        )
        return {
            "answer": _CONTEXT_LIMIT_ANSWER,
            "assistant_message_id": None,
            "citations": [],
            "follow_up_questions": [],
            "context_status": {
                "message_count": details["message_count"],
                "token_count": details["token_count"],
                "limit_reached": True,
            },
        }

    def _get_history(self, session_id: str) -> list[ChatMessage]:
        """Return the last LLM_HISTORY_WINDOW messages from this session for LLM context."""
        messages = self.chat_service.list_chat_messages_by_session(session_id)
        return messages[-LLM_HISTORY_WINDOW:] if len(messages) > LLM_HISTORY_WINDOW else messages

    def _generate_response(self, query: str, history: list[ChatMessage]) -> dict:
        """Run retrieval, confidence check, and LLM generation.

        Returns a dict with keys: answer, citations, follow_up_questions,
        input_tokens, output_tokens.
        When confidence is low, skips the LLM call and returns the
        out-of-scope answer with zero token counts.
        """
        chunks = self.rag_orchestrator.retrieve_chunks(query)

        if not self.rag_orchestrator.is_confident(query):
            logger.info(
                "Out-of-scope query (low confidence): query=%r", query[:80]
            )
            return {
                "answer": OUT_OF_SCOPE_ANSWER,
                "citations": [],
                "follow_up_questions": [],
                "input_tokens": 0,
                "output_tokens": 0,
            }

        return self.rag_orchestrator.build_response(query, chunks, history)

    def _persist(self, user_id: str, session_id: str, query: str, response: dict) -> str:
        """Save user message and assistant response; return the assistant message id."""
        user_token_count = _count_tokens(query)
        assistant_token_count = _count_tokens(response["answer"])

        self.chat_service.create_chat_message(
            session_id=session_id,
            user_id=user_id,
            role=MessageRole.USER,
            content=query,
            token_count=user_token_count,
        )
        assistant_msg = self.chat_service.create_chat_message(
            session_id=session_id,
            user_id=user_id,
            role=MessageRole.ASSISTANT,
            content=response["answer"],
            token_count=assistant_token_count,
            citations=response.get("citations"),
            follow_up_questions=response.get("follow_up_questions"),
        )
        return str(assistant_msg.id)

    def _log_spend(self, user_id: str, response: dict) -> None:
        """Record LLM and embedding token spend, then trigger crossing-point alert check."""
        try:
            llm_spend = self.spend_service.create_spend(
                user_id=user_id,
                model=LLM_MODEL,
                input_tokens=response.get("input_tokens", 0),
                output_tokens=response.get("output_tokens", 0),
                endpoint=_CHAT_ENDPOINT,
            )
            self.spend_service.spend_email_alert(current_cost=llm_spend.estimated_cost_usd)

            embedding_tokens = response.get("embedding_tokens", 0)
            if embedding_tokens > 0:
                embed_spend = self.spend_service.create_spend(
                    user_id=user_id,
                    model=EMBEDDING_MODEL,
                    input_tokens=embedding_tokens,
                    output_tokens=0,
                    endpoint=_CHAT_ENDPOINT,
                )
                self.spend_service.spend_email_alert(
                    current_cost=embed_spend.estimated_cost_usd
                )
        except Exception as exc:
            logger.error("Spend logging failed for user_id=%s: %s", user_id, exc)
