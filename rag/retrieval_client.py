import logging

import openai
import weaviate.classes as wvc

from config import config
from constants import EMBEDDING_MODEL, KNOWLEDGE_CHUNK_CLASS
from exceptions import EmbeddingError, RetrievalError
from infra import weaviate_client
from rag.constants import HYBRID_ALPHA, TOP_K

logger = logging.getLogger(__name__)


class RetrievalClient:
    """Handles embedding generation and hybrid search against the Weaviate KB."""

    def __init__(self):
        self._openai = openai.OpenAI(
            api_key=config.OPENAI_API_KEY,
            timeout=config.OPENAI_TIMEOUT,
        )
        self._weaviate = weaviate_client

    def generate_embedding(self, query: str) -> list[float]:
        """Generate an embedding vector for *query* using the configured embedding model.

        Returns:
            A list of 1536 floats.

        Raises:
            EmbeddingError: On any OpenAI API failure.
        """
        try:
            response = self._openai.embeddings.create(
                model=EMBEDDING_MODEL,
                input=query,
            )
            return response.data[0].embedding
        except (
            openai.APIError,
            openai.APITimeoutError,
            openai.RateLimitError,
        ) as exc:
            logger.error("Embedding generation failed for query=%r: %s", query[:80], exc)
            raise EmbeddingError("Failed to generate embedding") from exc

    def search(self, query: str, embedding: list[float]) -> list[dict]:
        """Run a hybrid BM25 + cosine search against Weaviate.

        Args:
            query: The raw query string used for BM25 keyword matching.
            embedding: The dense vector used for cosine similarity matching.

        Returns:
            A list of up to ``TOP_K`` dicts, each with keys:
            ``content``, ``source_doc``, ``section_title``, ``category``, ``score``.

        Raises:
            RetrievalError: On any Weaviate connection or query failure.
        """
        try:
            collection = self._weaviate.collections.get(KNOWLEDGE_CHUNK_CLASS)
            results = collection.query.hybrid(
                query=query,
                vector=embedding,
                alpha=HYBRID_ALPHA,
                limit=TOP_K,
                return_metadata=wvc.query.MetadataQuery(score=True),
            )
        except Exception as exc:
            logger.error("Weaviate hybrid search failed: %s", exc)
            raise RetrievalError("Failed to retrieve chunks from knowledge base") from exc

        chunks = []
        for obj in results.objects:
            props = obj.properties
            score = obj.metadata.score if (obj.metadata and obj.metadata.score is not None) else 0.0
            chunks.append(
                {
                    "content": props.get("content", ""),
                    "source_doc": props.get("source_doc", ""),
                    "section_title": props.get("section_title", ""),
                    "category": props.get("category", ""),
                    "score": score,
                }
            )

        logger.info(
            "Weaviate hybrid search returned %d chunks (top score=%.3f)",
            len(chunks),
            max((c["score"] for c in chunks), default=0.0),
        )
        return chunks

    def get_top_distance(self, query: str) -> float:
        """Return the cosine distance of the nearest KB chunk to *query*.

        Used by the confidence check to determine if a query is in-scope.
        A low distance (~0.25) means a relevant chunk exists; a high distance
        (~0.8+) means the query is out-of-scope.

        Raises:
            EmbeddingError: Propagated from ``generate_embedding``.
            RetrievalError: On any Weaviate failure.
        """
        embedding = self.generate_embedding(query)
        try:
            collection = self._weaviate.collections.get(KNOWLEDGE_CHUNK_CLASS)
            results = collection.query.near_vector(
                embedding,
                limit=1,
                target_vector="default",
                return_metadata=wvc.query.MetadataQuery(distance=True),
            )
        except Exception as exc:
            logger.error("Weaviate near_vector failed: %s", exc)
            raise RetrievalError("Failed to retrieve top distance from knowledge base") from exc

        if not results.objects:
            return 1.0
        return results.objects[0].metadata.distance or 1.0

    def retrieve(self, query: str) -> list[dict]:
        """Generate an embedding then run hybrid search.

        Returns:
            Ranked list of chunk dicts (see ``search`` for shape).

        Raises:
            EmbeddingError: Propagated from ``generate_embedding``.
            RetrievalError: Propagated from ``search``.
        """
        embedding = self.generate_embedding(query)
        return self.search(query, embedding)
