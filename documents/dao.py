import logging
from abc import ABC, abstractmethod

from weaviate.exceptions import WeaviateConnectionError, WeaviateQueryError, WeaviateTimeoutError

from constants import KNOWLEDGE_CHUNK_CLASS
from exceptions import RetrievalError
from infra.weaviate import weaviate_client
from documents.models import Document

logger = logging.getLogger(__name__)

# Upper bound on objects fetched for deduplication.
# With ~45 docs and reasonable chunk sizes this is well within Weaviate limits.
_MAX_FETCH_LIMIT = 10_000


class IDocumentDAO(ABC):
    @abstractmethod
    def list(self) -> list[Document]: ...


class DocumentDAO(IDocumentDAO):
    def __init__(self):
        self.client = weaviate_client

    def list(self) -> list[Document]:
        """Return a deduplicated list of Documents from Weaviate KnowledgeChunk metadata.

        Weaviate has no native DISTINCT, so all chunk metadata is fetched and
        deduplicated in Python by (source_doc, category) pair.
        """
        try:
            collection = self.client.collections.get(KNOWLEDGE_CHUNK_CLASS)
            response = collection.query.fetch_objects(
                limit=_MAX_FETCH_LIMIT,
                return_properties=["source_doc", "category"],
                include_vector=False,
            )
        except (WeaviateConnectionError, WeaviateQueryError, WeaviateTimeoutError) as exc:
            logger.error("DocumentDAO.list failed: %s", exc)
            raise RetrievalError("Failed to list documents from Weaviate") from exc

        seen: set[tuple[str, str]] = set()
        documents: list[Document] = []
        for obj in response.objects:
            source_doc = obj.properties.get("source_doc", "")
            category = obj.properties.get("category", "")
            key = (source_doc, category)
            if key not in seen:
                seen.add(key)
                documents.append(Document(name=source_doc, category=category))

        documents.sort(key=lambda d: (d.category, d.name))
        logger.info("DocumentDAO.list returned %d unique documents", len(documents))
        return documents
