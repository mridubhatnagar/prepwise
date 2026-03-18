# Data Schema

## PostgreSQL Tables

### users
| Column | Type | Constraints |
|---|---|---|
| id | UUID | PK, default gen_random_uuid() |
| google_auth_id | VARCHAR(255) | UNIQUE NOT NULL |
| email | VARCHAR(255) | NOT NULL |
| name | VARCHAR(255) | |
| avatar_url | TEXT | |
| created_at | TIMESTAMP | default NOW() |

### chat_sessions
| Column | Type | Constraints |
|---|---|---|
| id | UUID | PK, default gen_random_uuid() |
| user_id | UUID | FK → users(id) ON DELETE CASCADE |
| is_active | BOOLEAN | NOT NULL, default true |
| created_at | TIMESTAMP | default NOW() |

### chat_messages
| Column | Type | Constraints |
|---|---|---|
| id | UUID | PK, default gen_random_uuid() |
| user_id | UUID | FK → users(id) ON DELETE CASCADE |
| session_id | UUID | FK → chat_sessions(id) ON DELETE CASCADE |
| role | VARCHAR(10) | NOT NULL, CHECK IN ('user', 'assistant') |
| content | TEXT | NOT NULL |
| citations | JSONB | assistant only: [{ doc_name, section_title, category }] |
| follow_up_questions | JSONB | assistant only: ["question1", "question2"] |
| message_index | INTEGER | NOT NULL, sequential counter per user |
| token_count | INTEGER | NOT NULL, default 0 |
| created_at | TIMESTAMP | default NOW() |

Index: `(user_id, message_index)`

### allowed_users
| Column | Type | Constraints |
|---|---|---|
| id | UUID | PK, default gen_random_uuid() |
| email | VARCHAR(255) | UNIQUE NOT NULL |
| scope | VARCHAR(50) | NOT NULL — comma-separated: 'app' or 'app,docs' |
| added_at | TIMESTAMP | default NOW() |

### access_attempts
| Column | Type | Constraints |
|---|---|---|
| id | UUID | PK, default gen_random_uuid() |
| email | VARCHAR(255) | NOT NULL |
| attempted_at | TIMESTAMP | default NOW() |

### spend_log
| Column | Type | Constraints |
|---|---|---|
| id | UUID | PK, default gen_random_uuid() |
| user_id | UUID | FK → users(id) ON DELETE SET NULL |
| model | VARCHAR(100) | NOT NULL — e.g. 'gpt-4o', 'text-embedding-3-small' |
| input_tokens | INTEGER | NOT NULL, default 0 |
| output_tokens | INTEGER | NOT NULL, default 0 |
| estimated_cost_usd | NUMERIC(10,6) | NOT NULL |
| endpoint | VARCHAR(50) | e.g. '/api/chat/messages' |
| logged_at | TIMESTAMP | default NOW() |

Index: `(logged_at)`

### feedback
| Column | Type | Constraints |
|---|---|---|
| id | UUID | PK, default gen_random_uuid() |
| message_id | UUID | FK → chat_messages(id) ON DELETE CASCADE, NOT NULL, UNIQUE |
| user_id | UUID | FK → users(id) ON DELETE CASCADE, NOT NULL |
| rating | VARCHAR(10) | NOT NULL, CHECK IN ('up', 'down') |
| created_at | TIMESTAMP | default NOW() |

Index: `(user_id)`

---

## Weaviate Schema

**Class:** `KnowledgeChunk`

| Property | Type | Notes |
|---|---|---|
| content | text | vectorized by text-embedding-3-small |
| source_doc | string | e.g. "cap_theorem.md" |
| section_title | string | e.g. "Trade-offs" |
| category | string | e.g. "system_design", "database", "ai" |
| chunk_index | int | order within source doc |

- Vectorizer: none (bring your own vectors — 1536 dims, OpenAI text-embedding-3-small)
- BM25 index enabled for hybrid search
