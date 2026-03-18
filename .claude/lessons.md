# Lessons — Security & Architecture Concepts

## What is CSRF?

**CSRF (Cross-Site Request Forgery)** is an attack where a malicious site tricks a user's browser into making a request the user didn't intend.

### Classic CSRF Example
1. User is logged into `bank.com` (cookie is stored in browser)
2. User visits `evil.com` which has a hidden form: `<form action="https://bank.com/transfer" method="POST">`
3. The form auto-submits → browser sends the bank cookie along → transfer happens without user's knowledge

### CSRF in OAuth (what we protected against)
OAuth has its own CSRF variant:
1. Attacker starts a Google login flow for *their own* account, gets a `?code=` from Google
2. Attacker tricks the victim into visiting: `http://localhost:8000/auth/callback?code=ATTACKER_CODE`
3. The victim's browser completes the flow → victim is now logged into the **attacker's account**
4. Victim's actions (chat messages, etc.) are stored under the attacker's account — attacker can read them

### How the State Parameter Prevents It
- When the user clicks Sign In, browser navigates to `GET /api/auth/initiate`
- Backend generates a random nonce (e.g. `a3f9bc12`), stores it in an HttpOnly cookie (`oauth_state`), passes it to Google as `&state=a3f9bc12` in the redirect URL
- Google echoes it back: `/auth/callback?code=...&state=a3f9bc12`
- Backend checks: does returned `state` match the `oauth_state` cookie? If not → abort
- Cookie is cleared immediately after verification — prevents replay attacks
- The attacker cannot know the victim's nonce, so their forged callback URL will fail the check
- No frontend JS involved in state management — fully server-side

### Why SameSite=Strict Doesn't Help Here
`SameSite=Strict` prevents cookies from being sent on cross-site requests — protecting authenticated API calls. But `/auth/callback` is a **public endpoint with no JWT cookie**. The browser sends no JWT cookie, so `SameSite` provides no protection for this specific flow. The `oauth_state` cookie uses `SameSite=Lax` intentionally — it must be sent when Google redirects back to our callback.

### Key Distinction
- The state nonce is **not PII** — it's a temporary random value discarded after verification
- Storing it in an HttpOnly cookie is more secure than sessionStorage — not accessible to JavaScript at all

---

## RAG Chunking Strategy

### Pattern: Hierarchical Chunking with Overlap

This is a standard RAG chunking approach. The goal is to produce chunks in the **150–600 word range** — large enough to carry meaning, small enough for focused retrieval.

### Three-Stage Pipeline

**Stage 1 — Split by headings** (`_split_into_sections`)
- Markdown files are split at `##` and `###` boundaries into `(title, body)` pairs
- Preamble (text before the first heading) is prepended to the first section so context isn't lost
- Semantic boundaries are preferred over fixed-size splits because headings naturally group related content

**Stage 2 — Merge tiny sections**
- Adjacent sections under 150 words are merged into the preceding section
- Prevents low-signal chunks (e.g. a heading + one sentence) from being embedded on their own
- Merging is scoped within the same file — no cross-document merging
- Risk: adjacent sections could be unrelated. Acceptable tradeoff for now — tune based on retrieval quality

**Stage 3 — Split large sections at paragraph boundaries** (`_split_at_paragraphs`)
- Sections over 600 words are split further at paragraph (`\n\n`) boundaries
- Paragraph-boundary splitting preserves sentence integrity vs. fixed character/token splits
- The last **50 words** of each chunk are prepended to the next — this is the **overlap**, preventing context loss at chunk edges

### Tuning Philosophy
Ship with reasonable defaults, measure retrieval quality against real queries, then adjust. No point optimizing before you have signal.

### Production RAG Chunking Strategies
Production systems pick the strategy that matches their content type:

- **Fixed-size** — split every N tokens regardless of content. Simple baseline, breaks sentences mid-way.
- **Sentence-level** — use NLP (spaCy, NLTK) to detect sentence boundaries. Cleaner but sentences alone are often too short.
- **Semantic chunking** — embed every sentence, group where similarity drops (topic shift). Sophisticated, higher cost.
- **Recursive character splitting** — try `\n\n` → `\n` → `.` → space progressively until chunk fits target size. LangChain's `RecursiveCharacterTextSplitter` does this.
- **Document-aware (structural)** — use headings/sections as boundaries. Only works for structured formats like markdown.

### For PrepWise
Curated markdown with controlled structure → structural chunking (split at `##`) is the right choice, not a simplification.

If docs ever become user-configurable (arbitrary formats), switch to LangChain's `RecursiveCharacterTextSplitter` and configure chunk size + overlap via config. No need for V1.
