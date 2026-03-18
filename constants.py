# Weaviate — used by infra/weaviate.py, rag/, and documents/
KNOWLEDGE_CHUNK_CLASS: str = "KnowledgeChunk"

# OpenAI models
LLM_MODEL: str = "gpt-4o"
LLM_MAX_RESPONSE_WORDS: int = 500
EMBEDDING_MODEL: str = "text-embedding-3-small"

# OpenAI token pricing (USD per 1 million tokens)
GPT4O_INPUT_COST_PER_1M: float = 2.50
GPT4O_OUTPUT_COST_PER_1M: float = 10.00
EMBEDDING_INPUT_COST_PER_1M: float = 0.02

# Chat context limits
CONTEXT_MESSAGE_LIMIT: int = 20
CONTEXT_TOKEN_LIMIT: int = 8000

# Feedback
FEEDBACK_CHANGE_LIMIT: int = 3

# Number of recent messages passed to the LLM as conversational history
LLM_HISTORY_WINDOW: int = 10

# Google OAuth endpoints
GOOGLE_AUTH_URL: str = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL: str = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL: str = "https://www.googleapis.com/oauth2/v3/userinfo"
