from pydantic import BaseModel


class Document(BaseModel):
    """API response shape for a single document entry.

    This is a Pydantic model only — it is NOT a Weaviate schema.
    The Weaviate KnowledgeChunk schema is defined in infra/weaviate.py.
    """

    name: str
    category: str
