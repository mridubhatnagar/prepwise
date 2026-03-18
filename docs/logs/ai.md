# 🤖 AI Learning Logs

# 2026-01-15
- Completed AI for Everyone course.

## 2026-01-20
- Purchased ChatGPT API subscription.
- Resumed "ChatGPT Prompting for Developers" course on deeplearning.ai.
- Completed lectures on transforming and expanding prompts.
- Planned to cover chatbot lecture next day.
- Installed Jupyter Notebook and started implementing examples alongside the course.

---

## 2026-01-21
- Started using OpenAI API in Jupyter.
- Faced rate limit and quota issues.
- Added billing and credits.
- Learned difference between `chat.completions` and `responses` API.
- Fixed issues with temperature and model compatibility.

Key Insight:
- Newer OpenAI models behave differently from older GPT-3.5 APIs.

---

## 2026-01-22
- Explored Moderation API.
- Learned how to use `omni-moderation-latest`.
- Understood that moderation response is structured, not plain text.
- Fixed parsing issues with Moderation API responses.

Key Insight:
- Moderation API is separate from generation models.

---

## 2026-01-23
- Learned about prompt injection.
- Understood difference between:
  - system prompts
  - user prompts
  - delimiters
- Realized that prompt injection is a security problem, not just a prompt design issue.

Key Insight:
- Delimiters help separate trusted instructions from untrusted user input.

---

## 2026-01-24
- Completed sections on:
  - chaining prompts
  - chain-of-thought reasoning
  - output evaluation
- Learned that complex tasks should be broken into multiple prompts.
- Explored deterministic vs non-deterministic outputs.

Key Insight:
- Prompt chaining improves reliability and debuggability.

---

## 2026-01-25
- Completed Evaluation Part I and II from "Building Systems with ChatGPT API".
- Learned about evaluating deterministic and non-deterministic outputs.
- Felt confusion around non-deterministic evaluation and planned to explore more resources.

---

## 2026-01-26
- Started AI Evals for Everyone course.
- Learned:
  - difference between model evals and product evals
  - evaluation = input, expected output, actual output
  - evaluation approaches: human, code, LLM judge
  - rubric as evaluation criteria.

Key Insight:
- AI evaluation is not just testing, but product design.

---

## 2026-01-27
- Continued AI Evals course.
- Learned that evaluation datasets evolve based on:
  - user feedback
  - logs
  - signals.
- Understood that metrics and rubrics change with product maturity.

Key Insight:
- Evaluation is a continuous process.
- start simple, avoid overengineering evaluation systems
- choose LLM judges with broader context when needed.


## 2026-01-28
- Started "How Transformer LLMs Work" course.
- Learned about:
  - tokens and tokenization
  - difference between words and tokens
  - encoder vs decoder models
  - vocabulary and embeddings.
  - bag of words
  - Word2Vec
  - limitations of static embeddings
  - RNNs and context embeddings.

Key Insight:
- Tokens are not equal to words; they depend on tokenizer vocabulary.
- Static embeddings lack contextual understanding.


## 2026-01-29
- Covered:
  - transformers
  - attention mechanism
  - transformer blocks
  - positional embeddings.
- Understood why transformers replaced RNNs.

Key Insight:
- Attention enables parallelism and better context handling.

---

## 2026-01-30
- Learned about:
  - self-attention
  - mixture of experts (MoE)
  - transformer architecture overview.
- Tried running a model locally but faced disk space issues.
- Completed "How Transformer LLMs Work" course.
- Took quiz and scored 50/70.
- Understood deeper aspects of transformer architecture.
- Completed Prompt Engineering for Developers quiz.
- Scored 70/70 and earned certificate.

Key Insight:
- LLMs are modular systems, not monolithic models.
- Prompt engineering is about controlling model behavior, not just writing prompts.

---

## 2026-01-31
- Learnt About:
  - RAG 101
  - What is a RAG system?
  - What are components of RAG system?
- Gave quiz for Module 1. Got 100/100
---

## 2026-02-01

- Completed RAG Module 1 coding assignment.
- Scored 20/20 in the assignment.
- Started RAG Module 2: Information Retrieval Basics.
- Learned different types of search:
  - Keyword search
  - Semantic search
- Understood high-level RAG data flow:
  - User prompt → retriever → knowledge base → Relevant Docs -> Augmented Prompt -> LLM → response.
- Learned about hybrid search (keyword + semantic).
- Learned about metadata filtering and why it is important in retrieval.

## 2026-02-02

- Completed modules on keyword search using TF-IDF.
- Studied BM25 as an improved keyword-based ranking method.
- Completed semantic search concepts.
- Understood differences between:
  - keyword search (lexical matching)
  - semantic search (meaning-based matching)
- Recognized where each search method fits in a RAG system.

## 2025-02-03

- Rewatched video on semantic search.
- Understood the core idea:
  - semantic search uses embedding models
  - semantically similar sentences/documents are placed closer together in embedding space.
- Learned difference between similarity metrics:
  - cosine similarity measures the angle between two vectors
  - euclidean distance measures the distance between two vectors.
- Understood the output range and intuition behind cosine similarity and euclidean distance.
- Used `sentence-transformers` to encode sentences into embeddings.
- Watched video on hybrid search.
- Learned that the beta parameter can be tuned to balance:
  - keyword search importance
  - semantic search importance.

## 2025-02-05

- Started RAG Module 3.
- Studied Approximate Nearest Neighbour (ANN) search.
- Understood:
  - KNN vs ANN
  - Why ANN is used for large-scale vector search.
- Learned about proximity graph-based ANN methods:
  - Navigable Small World (NSW)
  - Hierarchical Navigable Small World (HNSW).
- Understood advantages of ANN over KNN:
  - faster retrieval
  - better scalability.
- Learned tradeoff:
  - ANN does not guarantee perfectly closest neighbors.
- Watched lecture on Weaviate vector database.
- Understood that vector DBs expose library methods for different search types.
- Went through vector database code examples.
- Watched lecture on chunking.
- Learned different chunking strategies and limitations of each.
- Understood why mixing chunking approaches works better than relying on a single strategy.
- Skimmed chunking notebook using Pro Git book as demo.
- Yet to try hands-on implementation.


# 📅 Feb 6, 2026 — Learning Log

## ✅ Hands-on
- Played around with **SentenceTransformer** locally.
- Used Sentence transformer python documentation. 
- Used model "BAAI/bge-base-en-v1.5".

## 🧠 Concepts Clarified
- **Vector space**: Embeddings live in a shared high-dimensional vector space.
- **Embedding models** use **transformer encoders** under the hood.
- **Dimensionality** of the embedding space is determined by the **model**, not by the sentence length or content.
- **All sentences** embedded by the same model are part of the **same vector space**.
- A sentence embedding can be thought of as a **point (vector) in that space**.
- **Similarity** (e.g., cosine similarity) is **not learned behavior** of the embedding model; it is a **separate mathematical operation** applied *after* embeddings are generated.

## 🔑 Key Insight
- Embedding models learn a **semantic geometry**; similarity search operates **on top of that geometry**, typically inside a vector database.

# 📅 Feb 12, 2026 — Learning Log

## ✅ Completed
- Finished **Module 3 Quiz** (RAG Course)
- Completed **Module 2 Code Assignment**

## 🧠 Concepts Reinforced
- **BM25 (Lexical Retrieval)** — keyword-based scoring using term frequency and inverse document frequency.
- **Semantic Search (Bi-encoder + Similarity)** — embedding-based retrieval using vector similarity.
- **Hybrid Retrieval** — combining BM25 and semantic search for more robust results.
- Retrieval functions return **indices**, not documents, for evaluation purposes.
- Importance of correct **argument ordering** in APIs (positional vs keyword arguments).
- Notebook state management (kernel restart, execution order, indexing state).

## 🔑 Key Insights
- BM25 excels at exact keyword matching and rare terms.
- Semantic search handles paraphrasing and conceptual similarity.
- Hybrid search often improves robustness by combining lexical and semantic signals.
- Debugging retrieval systems often involves checking:
  - Corpus size
  - Index state
  - Data structure shapes
  - Function argument order

## 🚀 Next Steps
- Begin **Vector Database (Weaviate) Course**
- Complete **Module 3 Code Assignment** (Weaviate-based)
- Resume remaining RAG modules after vector DB foundation



# March 5, 2026 - Learning Log

## Progress

### Module 4 — Prompt Engineering
Covered:
- Context window
- How to choose an LLM
- Hallucinations

Quiz score: **93/100**

---

### Module 5 — RAG in Production (partially completed)

Covered topics:
- LLM as a judge
- Human evaluation of LLM responses
- Observability for RAG systems (RAGAS)
- System monitoring tools (Datadog, Grafana)
- RAG vs Fine-tuning
