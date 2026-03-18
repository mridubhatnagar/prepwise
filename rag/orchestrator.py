import logging
import re

from chat.models import ChatMessage
from exceptions import LLMError
from rag.constants import CONFIDENCE_DISTANCE_THRESHOLD, OUT_OF_SCOPE_ANSWER
from rag.llm_client import LLMClient
from rag.retrieval_client import RetrievalClient

logger = logging.getLogger(__name__)

# Regex patterns checked against the user query before any LLM call.
# Matched case-insensitively. Generic 400 message is returned on any match
# so the presence of filtering is not disclosed.
_INJECTION_PATTERNS: list[re.Pattern] = [
    re.compile(r"ignore (previous|prior|above) instructions", re.IGNORECASE),
    re.compile(r"you are now", re.IGNORECASE),
    re.compile(r"pretend (you are|to be)", re.IGNORECASE),
    re.compile(r"disregard your", re.IGNORECASE),
    re.compile(r"forget (everything|all instructions)", re.IGNORECASE),
    re.compile(r"act as (a|an)", re.IGNORECASE),
    re.compile(r"your new (instructions|role|persona)", re.IGNORECASE),
    re.compile(r"system prompt", re.IGNORECASE),
    re.compile(r"jailbreak", re.IGNORECASE),
]


class RAGOrchestrator:
    """Coordinates retrieval, confidence checking, prompt injection defence,
    LLM generation, and output guardrails for a single chat query."""

    def __init__(self, retrieval_client: RetrievalClient, llm_client: LLMClient):
        self.retrieval_client = retrieval_client
        self.llm_client = llm_client

    def retrieve_chunks(self, query: str) -> list[dict]:
        """Retrieve the top-K KB chunks for *query* via hybrid search.

        Returns:
            Ranked list of chunk dicts with keys:
            ``content``, ``source_doc``, ``section_title``, ``category``, ``score``.

        Raises:
            EmbeddingError: Propagated from ``RetrievalClient.generate_embedding``.
            RetrievalError: Propagated from ``RetrievalClient.search``.
        """
        return self.retrieval_client.retrieve(query)

    def is_confident(self, query: str) -> bool:
        """Return ``True`` when the nearest KB chunk is close enough to *query*.

        Uses cosine distance from ``near_vector``: a distance below
        ``CONFIDENCE_DISTANCE_THRESHOLD`` means a relevant chunk exists.
        """
        distance = self.retrieval_client.get_top_distance(query)
        confident = distance < CONFIDENCE_DISTANCE_THRESHOLD
        logger.info(
            "Confidence check: query=%r distance=%.3f threshold=%.2f confident=%s",
            query[:80],
            distance,
            CONFIDENCE_DISTANCE_THRESHOLD,
            confident,
        )
        return confident

    def build_response(self, query: str, chunks: list[dict], history: list[ChatMessage]) -> dict:
        """Run prompt injection check, call the LLM, and apply output guardrails.

        Args:
            query: The current user question.
            chunks: Retrieved KB chunks from ``retrieve_chunks``.
            history: Recent ``ChatMessage`` ORM objects for conversational context.

        Returns:
            A dict with keys: ``answer``, ``citations``, ``follow_up_questions``,
            ``input_tokens``, ``output_tokens``.

        Raises:
            ValueError: When the query matches a prompt injection pattern.
                The caller (controller) should return HTTP 400 with a generic message.
            LLMError: Propagated from ``LLMClient.generate_response``.
        """
        self._check_injection(query)

        messages = self.llm_client.build_prompt(query, chunks, history)
        response = self.llm_client.generate_response(messages)

        response["citations"] = self._strip_hallucinated_citations(
            response.get("citations", []), chunks
        )

        return response

    def _check_injection(self, query: str) -> None:
        """Raise ``ValueError`` if the query matches any injection pattern."""
        for pattern in _INJECTION_PATTERNS:
            if pattern.search(query):
                logger.warning(
                    "Prompt injection pattern matched query=%r (pattern=%r)",
                    query[:80],
                    pattern.pattern,
                )
                raise ValueError("Prompt injection detected")

    def _strip_hallucinated_citations(
        self, citations: list[dict], chunks: list[dict]
    ) -> list[dict]:
        """Remove citations whose ``doc_name`` was not in the retrieved chunks.

        Only ``source_doc`` values present in *chunks* are considered valid.
        This prevents the LLM from citing documents it was not given.
        """
        valid_source_docs = {c["source_doc"] for c in chunks}
        filtered = [
            cit for cit in citations if cit.get("doc_name") in valid_source_docs
        ]
        stripped_count = len(citations) - len(filtered)
        if stripped_count:
            logger.warning(
                "Output guardrail stripped %d hallucinated citation(s)", stripped_count
            )
        return filtered
