import logging

from documents.dao import IDocumentDAO

logger = logging.getLogger(__name__)

_DOC_DISPLAY_NAMES: dict[str, str] = {
    "api_paradigm_and_design.md":        "API Paradigms & Design",
    "caching.md":                        "Caching",
    "cap_theorem.md":                    "CAP Theorem",
    "cdn.md":                            "CDN",
    "consistent_hashing.md":             "Consistent Hashing",
    "dns.md":                            "DNS",
    "eventual_consistency.md":           "Eventual Consistency",
    "forward_vs_reverse_proxy.md":       "Forward vs Reverse Proxy",
    "http.md":                           "HTTP",
    "latency_vs_throughput.md":          "Latency vs Throughput",
    "load_balancer.md":                  "Load Balancer",
    "message_queue.md":                  "Message Queue",
    "object_storage.md":                 "Object Storage",
    "replication.md":                    "Replication",
    "replication_vs_sharding.md":        "Replication vs Sharding",
    "sharding.md":                       "Sharding",
    "sql_vs_nosql.md":                   "SQL vs NoSQL",
    "tcp_vs_udp.md":                     "TCP vs UDP",
    "terminologies.md":                  "Terminologies",
    "websocket.md":                      "WebSocket",
    "data_modelling_concepts.md":        "Data Modelling Concepts",
    "llm_architecture.md":               "LLM Architecture",
    "transformer.md":                    "Transformer",
    "knn-vs-ann.md":                     "KNN vs ANN",
    "sparse-vs-dense-hybrid-search.md":  "Sparse vs Dense & Hybrid Search",
    "vectorizer-vs-manual-embeddings.md": "Vectorizer vs Manual Embeddings",
    "ES256.md":                          "ES256",
    "er_modeling_workflow.md":           "ER Modeling Workflow",
    "schema_design_checklist.md":        "Schema Design Checklist",
}

_CATEGORY_DISPLAY_NAMES: dict[str, str] = {
    "system_design": "System Design",
    "database":      "Database",
    "ai":            "AI",
    "systems":       "Systems",
    "playbook":      "Playbook",
    "checklist":     "Checklist",
}


class DocumentService:
    def __init__(self, document_dao: IDocumentDAO):
        self.document_dao = document_dao

    def list_documents_by_categories(self) -> dict[str, list[str]]:
        """Return documents grouped by category with human-readable display names.

        Calls the DAO to fetch all documents, applies display name mappings for
        both document filenames and category slugs, then groups by category.
        Returns a dict mapping each display category to a sorted list of display names.
        """
        documents = self.document_dao.list()

        grouped: dict[str, list[str]] = {}
        for doc in documents:
            display_name = _DOC_DISPLAY_NAMES.get(doc.name, doc.name)
            display_category = _CATEGORY_DISPLAY_NAMES.get(doc.category, doc.category)
            grouped.setdefault(display_category, []).append(display_name)

        logger.info(
            "list_documents_by_categories returned %d categories, %d total documents",
            len(grouped),
            len(documents),
        )
        return grouped
