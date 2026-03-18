"""One-time document ingestion script.

Walks the knowledge-base document folders, chunks each markdown file by
section headers, embeds each chunk via OpenAI text-embedding-3-small, and
uploads to the Weaviate KnowledgeChunk collection.

Re-runnable (idempotent): existing KnowledgeChunk objects are deleted before
each run so stale data is never left behind.

Usage:
    python scripts/ingest.py
"""

import logging
import sys
from pathlib import Path

import openai
import weaviate
from langchain_text_splitters import MarkdownHeaderTextSplitter

# Allow imports from project root when running this script directly.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import config  # noqa: E402 — must come after sys.path patch
from constants import EMBEDDING_MODEL, KNOWLEDGE_CHUNK_CLASS  # noqa: E402
from infra.weaviate import ensure_schema, weaviate_client  # noqa: E402

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

DOCS_ROOT = Path(__file__).resolve().parent.parent / "docs"

# Only these sub-folders are ingested. docs/logs/ is intentionally excluded.
INGEST_FOLDERS = ["concepts", "systems", "playbook", "checklist"]

_MD_SPLITTER = MarkdownHeaderTextSplitter(
    headers_to_split_on=[("##", "section_title")]
)


def _infer_category(file_path: Path) -> str:
    """Return a category label based on the file's path relative to DOCS_ROOT."""
    relative = file_path.relative_to(DOCS_ROOT)
    parts = relative.parts  # e.g. ('concepts', 'system_design', 'cap_theorem.md')

    if parts[0] == "concepts":
        if len(parts) >= 3:
            # e.g. concepts/system_design/... → system_design
            # e.g. concepts/database/...     → database
            # e.g. concepts/ai/...           → ai
            # e.g. concepts/dsa/...          → dsa
            return parts[1]
        return "concepts"

    # playbook, systems, checklist → use the top-level folder name
    return parts[0]


def _build_chunks(file_path: Path, source_doc: str, category: str) -> list[dict]:
    """Parse a markdown file and return a list of chunk metadata dicts.

    Each dict has the shape expected by Weaviate:
        { content, source_doc, section_title, category, chunk_index }
    """
    raw_text = file_path.read_text(encoding="utf-8")
    sections = _MD_SPLITTER.split_text(raw_text)

    chunks: list[dict] = []
    for section in sections:
        content = section.page_content.strip()
        if not content:
            continue
        chunks.append(
            {
                "content": content,
                "source_doc": source_doc,
                "section_title": section.metadata.get("section_title", ""),
                "category": category,
                "chunk_index": len(chunks),
            }
        )

    return chunks


class Embedder:
    """Thin wrapper around the OpenAI embeddings API."""

    def __init__(self) -> None:
        self._client = openai.OpenAI(
            api_key=config.OPENAI_API_KEY,
            timeout=config.OPENAI_TIMEOUT,
        )

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Embed a batch of texts and return their vectors.

        Raises openai.APIError on failure — caller handles retry/abort.
        """
        response = self._client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=texts,
        )
        # Response items are guaranteed to be in the same order as input.
        return [item.embedding for item in response.data]


EMBED_BATCH_SIZE = 100  # texts per OpenAI embeddings call


def _delete_existing(client: weaviate.WeaviateClient) -> None:
    """Delete all existing KnowledgeChunk objects so the run is idempotent."""
    collection = client.collections.get(KNOWLEDGE_CHUNK_CLASS)
    deleted = collection.data.delete_many(
        where=weaviate.classes.query.Filter.by_property("source_doc").like("*")
    )
    logger.info("Deleted %s existing KnowledgeChunk objects", deleted.successful)


def _upload_chunks(
    client: weaviate.WeaviateClient,
    chunks: list[dict],
    vectors: list[list[float]],
) -> None:
    """Upload chunks with their pre-computed vectors to Weaviate."""
    collection = client.collections.get(KNOWLEDGE_CHUNK_CLASS)
    for chunk, vector in zip(chunks, vectors):
        collection.data.insert(properties=chunk, vector={"default": vector})


def collect_files() -> list[Path]:
    """Return all .md files from the ingest folders, sorted for determinism."""
    files: list[Path] = []
    for folder_name in INGEST_FOLDERS:
        folder = DOCS_ROOT / folder_name
        if not folder.exists():
            logger.warning("Ingest folder does not exist, skipping: %s", folder)
            continue
        files.extend(sorted(folder.rglob("*.md")))
    return files


def main() -> None:
    if weaviate_client is None:
        logger.error("Weaviate client is not available — aborting ingestion.")
        sys.exit(1)

    logger.info("Ensuring Weaviate schema...")
    ensure_schema(weaviate_client)

    logger.info("Clearing existing KnowledgeChunk objects...")
    _delete_existing(weaviate_client)

    files = collect_files()
    if not files:
        logger.warning("No markdown files found under %s — nothing to ingest.", DOCS_ROOT)
        sys.exit(0)

    logger.info("Found %d markdown file(s) to ingest.", len(files))

    embedder = Embedder()
    all_chunks: list[dict] = []

    for file_path in files:
        source_doc = file_path.name
        category = _infer_category(file_path)
        file_chunks = _build_chunks(file_path, source_doc, category)
        logger.info(
            "  %s  →  %d chunk(s)  [category=%s]",
            file_path.relative_to(DOCS_ROOT),
            len(file_chunks),
            category,
        )
        all_chunks.extend(file_chunks)

    logger.info("Total chunks to embed: %d", len(all_chunks))

    # Embed in batches to avoid exceeding API payload limits.
    all_vectors: list[list[float]] = []
    for i in range(0, len(all_chunks), EMBED_BATCH_SIZE):
        batch_texts = [c["content"] for c in all_chunks[i : i + EMBED_BATCH_SIZE]]
        try:
            vectors = embedder.embed_batch(batch_texts)
        except openai.APIError as exc:
            logger.error("OpenAI embedding API error on batch %d: %s", i // EMBED_BATCH_SIZE, exc)
            sys.exit(1)
        all_vectors.extend(vectors)
        logger.info(
            "  Embedded batch %d/%d",
            min(i + EMBED_BATCH_SIZE, len(all_chunks)),
            len(all_chunks),
        )

    logger.info("Uploading %d chunks to Weaviate...", len(all_chunks))
    _upload_chunks(weaviate_client, all_chunks, all_vectors)

    docs_processed = len(files)
    chunks_created = len(all_chunks)
    print(f"\nIngestion complete: {docs_processed} doc(s) processed, {chunks_created} chunk(s) created.")
    logger.info("Ingestion complete: %d doc(s), %d chunk(s).", docs_processed, chunks_created)


if __name__ == "__main__":
    main()
