import logging

import weaviate
from weaviate.classes.config import Configure, Property, DataType, Tokenization, VectorDistances

from config import config
from constants import KNOWLEDGE_CHUNK_CLASS

logger = logging.getLogger(__name__)


def _build_client() -> weaviate.WeaviateClient | None:
    try:
        client = weaviate.connect_to_custom(
            http_host=config.WEAVIATE_HOST,
            http_port=config.WEAVIATE_PORT,
            http_secure=False,
            grpc_host=config.WEAVIATE_GRPC_HOST,
            grpc_port=config.WEAVIATE_GRPC_PORT,
            grpc_secure=False,
        )
        logger.info(
            "Weaviate client initialised at %s:%s", config.WEAVIATE_HOST, config.WEAVIATE_PORT
        )
        return client
    except Exception as exc:
        logger.error("Failed to initialise Weaviate client: %s", exc)
        return None


def ensure_schema(client: weaviate.WeaviateClient) -> None:
    """Create the KnowledgeChunk collection if it does not already exist.

    Called once by the ingestion script on first run.
    Safe to call repeatedly — skips creation if the collection is present.
    """
    if client.collections.exists(KNOWLEDGE_CHUNK_CLASS):
        logger.info("Weaviate collection '%s' already exists — skipping creation", KNOWLEDGE_CHUNK_CLASS)
        return

    client.collections.create(
        name=KNOWLEDGE_CHUNK_CLASS,
        description="A single text chunk from a knowledge-base markdown document.",
        # Bring-your-own vectors: embeddings are generated externally via
        # OpenAI text-embedding-3-small (1536 dims) and supplied at insert time.
        vector_config=Configure.Vectors.self_provided(
            vector_index_config=Configure.VectorIndex.hnsw(
                distance_metric=VectorDistances.COSINE,
            ),
        ),
        # Enable BM25 inverted index for hybrid (keyword + vector) search.
        inverted_index_config=Configure.inverted_index(),
        properties=[
            Property(
                name="content",
                data_type=DataType.TEXT,
                description="Full text of the chunk.",
                tokenization=Tokenization.WORD,
            ),
            Property(
                name="source_doc",
                data_type=DataType.TEXT,
                description="Source markdown filename (e.g. 'cap_theorem.md').",
                tokenization=Tokenization.FIELD,
            ),
            Property(
                name="section_title",
                data_type=DataType.TEXT,
                description="Markdown heading that introduces this chunk (e.g. 'Trade-offs').",
                tokenization=Tokenization.WORD,
            ),
            Property(
                name="category",
                data_type=DataType.TEXT,
                description="Topic category inferred from the doc path (e.g. 'system_design').",
                tokenization=Tokenization.FIELD,
            ),
            Property(
                name="chunk_index",
                data_type=DataType.INT,
                description="Sequential position of this chunk within its source document.",
            ),
        ],
    )
    logger.info("Weaviate collection '%s' created", KNOWLEDGE_CHUNK_CLASS)


weaviate_client = _build_client()
