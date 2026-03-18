TOP_K: int = 5
HYBRID_ALPHA: float = 0.7  # 0 = pure BM25, 1 = pure vector

CONFIDENCE_DISTANCE_THRESHOLD: float = 0.6
OUT_OF_SCOPE_ANSWER: str = (
    "Sorry, that's outside my current scope. "
    "Try asking from the curated list of topics present in the left sidebar."
)
