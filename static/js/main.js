/**
 * PrepIt — Alpine.js global app state
 *
 * All dynamic state lives here. API calls are wired in Phase 2.
 */

/** @returns {string} Current time formatted as "h:mm AM/PM" */
function currentTime() {
  return new Date().toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' });
}

/**
 * Render message content as HTML.
 * AI messages are parsed as markdown; user messages are HTML-escaped (plain text).
 *
 * @param {{ role: string, content: string }} msg
 * @returns {string} Safe HTML string for x-html binding.
 */
function renderContent(msg) {
  if (msg.role === 'assistant') {
    const html = marked.parse(msg.content);
    const div = document.createElement('div');
    div.innerHTML = html;
    div.querySelectorAll('a').forEach(a => {
      const span = document.createElement('span');
      span.textContent = a.textContent;
      a.replaceWith(span);
    });
    return div.innerHTML;
  }
  return msg.content
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');
}

/** @returns {Array} Citations deduplicated by doc_name. */
function uniqueCitations(citations) {
  if (!citations) return [];
  const seen = new Set();
  return citations.filter(c => {
    if (seen.has(c.doc_name)) return false;
    seen.add(c.doc_name);
    return true;
  });
}

/** @returns {Array} String array with duplicates removed. */
function uniqueStrings(items) {
  if (!items) return [];
  return [...new Set(items)];
}

/** @returns {string} Two-letter initials derived from a display name. */
function computeInitials(name) {
  if (!name) return '?';
  const parts = name.trim().split(/\s+/);
  if (parts.length === 1) return parts[0][0].toUpperCase();
  return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
}

/**
 * Main Alpine.js data object for the chat page.
 *
 * State contract (must stay in sync with plan.md):
 *   messages           — array of message objects (user + AI)
 *   documents          — array of { name, category } — drives sidebar
 *   suggestions        — empty-state suggestion chips
 *   user               — { name, initials } — drives app bar
 *   inputText          — bound to textarea via x-model
 *   isLoading          — shows typing indicator while awaiting response
 *   contextLimitReached — shows/hides context limit banner
 *   sidebarCollapsed   — sidebar collapsed state (desktop)
 *   mobileSidebarOpen  — sidebar drawer open state (mobile only)
 *   sendDisabled       — true while error cooldown is active
 *   sendCooldownLabel  — button label during cooldown ("Wait 60s…")
 *   feedbacks          — map of message_id → 'up' | 'down' | null; tracks active rating per AI message
 *   sessionId          — active chat session UUID; loaded from GET /api/chat/messages, updated on Clear Chat
 */
function chatApp() {
  return {
    messages:  [],
    documents: [],
    sessionId: null,

    suggestions: [
      'What is the CAP theorem?',
      'Explain consistent hashing',
      'SQL vs NoSQL — when to use which?',
      'How does a vector database work?',
      'What is sharding?',
      'Explain the Transformer architecture',
    ],

    user: {
      name:     '',
      initials: '',
    },

    inputText:           '',
    isLoading:           false,
    contextLimitReached: false,
    sidebarCollapsed:    false,
    mobileSidebarOpen:   false,

    feedbacks:           {},
    feedbackChanges:     {},
    feedbackChangeLimit: FEEDBACK_CHANGE_LIMIT,

    sendDisabled:      false,
    sendCooldownLabel: '',
    _cooldownTimer:    null,
    _errorBanner:      '',

    /**
     * Returns documents grouped by category, preserving insertion order.
     * Shape: [ { category: string, docs: [{ name, category }] } ]
     */
    get groupedDocuments() {
      const order = [];
      const map   = {};
      for (const doc of this.documents) {
        if (!map[doc.category]) {
          map[doc.category] = [];
          order.push(doc.category);
        }
        map[doc.category].push(doc);
      }
      return order.map(cat => ({ category: cat, docs: map[cat] }));
    },

    async init() {
      await Promise.all([
        this._loadUser(),
        this._loadDocuments(),
        this._loadMessages(),
      ]);
    },

    async _loadUser() {
      try {
        const res = await fetch('/api/auth/me');
        if (res.status === 401) { this._redirectUnauthorized(); return; }
        if (!res.ok) return;
        const { data } = await res.json();
        this.user.name     = data.user.name || '';
        this.user.initials = computeInitials(data.user.name);
      } catch (_) {}
    },

    async _loadDocuments() {
      try {
        const res = await fetch('/api/documents');
        if (res.status === 401) { this._redirectUnauthorized(); return; }
        if (!res.ok) return;
        const { data } = await res.json();
        // API returns { category: [doc_names] } — flatten to [{ name, category }]
        const flat = [];
        for (const [category, names] of Object.entries(data.documents)) {
          for (const name of names) {
            flat.push({ name, category });
          }
        }
        this.documents = flat;
      } catch (_) {}
    },

    async _loadMessages() {
      try {
        const res = await fetch('/api/chat/messages');
        if (res.status === 401) { this._redirectUnauthorized(); return; }
        if (!res.ok) return;
        const { data } = await res.json();
        this.sessionId = data.session_id || null;
        this.messages = data.messages.map(msg => ({
          id:                  msg.id,
          role:                msg.role.toLowerCase(),
          content:             msg.content,
          citations:           uniqueCitations(msg.citations),
          follow_up_questions: uniqueStrings(msg.follow_up_questions),
          isHistory:           true,
          time: new Date(msg.created_at).toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' }),
        }));
        const loadedFeedbacks = {};
        for (const msg of data.messages) {
          if (msg.rating) loadedFeedbacks[msg.id] = msg.rating;
        }
        this.feedbacks = loadedFeedbacks;
        this._scrollToBottom();
      } catch (_) {}
    },

    /**
     * Send a message via POST /api/chat/messages.
     * Appends the user message immediately, then awaits the AI response.
     * Handles 401 (session expired), 429 (rate limit), and 503 (service error).
     *
     * Called by: Send button, suggestion chips, follow-up pills.
     *
     * @param {string} text - The message text to send.
     */
    async sendMessage(text) {
      const trimmed = (text || this.inputText).trim();
      if (!trimmed || this.isLoading || this.sendDisabled) return;

      this.messages.push({
        role:                'user',
        content:             trimmed,
        citations:           [],
        follow_up_questions: [],
        time:                currentTime(),
      });

      this.inputText = '';
      this.isLoading = true;
      this._scrollToBottom();

      try {
        const res = await fetch('/api/chat/messages', {
          method:  'POST',
          headers: { 'Content-Type': 'application/json' },
          body:    JSON.stringify({ data: { message: trimmed, session_id: this.sessionId } }),
        });

        if (res.status === 401) { this._redirectUnauthorized(); return; }

        if (!res.ok) {
          const body = await res.json().catch(() => ({}));
          this._handleApiError(res.status, body.detail || '');
          this.isLoading = false;
          return;
        }

        const { data } = await res.json();
        const msg = data.message;

        this.isLoading = false;
        this.messages = this.messages.map(m => ({ ...m, isHistory: true }));
        this.messages.push({
          id:                  msg.assistant_message_id || null,
          role:                'assistant',
          content:             msg.answer,
          citations:           uniqueCitations(msg.citations),
          follow_up_questions: uniqueStrings(msg.follow_up_questions),
          time:                currentTime(),
        });

        if (msg.context_status && msg.context_status.limit_reached) {
          this.contextLimitReached = true;
        }

        this._scrollToBottom();
      } catch (_) {
        this.isLoading = false;
      }
    },

    /**
     * Clear the conversation via POST /api/chat/sessions.
     * Deactivates the current session and creates a new one, then resets local state.
     * Messages from the old session are retained in the database — never deleted.
     */
    async clearChat() {
      try {
        const res = await fetch('/api/chat/sessions', { method: 'POST' });
        if (res.status === 401) { this._redirectUnauthorized(); return; }
        if (res.ok) {
          const { data } = await res.json();
          this.sessionId = data.session_id || null;
        }
      } catch (_) {}

      this.messages            = [];
      this.contextLimitReached = false;
      this._errorBanner        = '';
    },

    /**
     * Sign out via POST /api/auth/logout, then redirect to the landing page.
     */
    async signOut() {
      try {
        await fetch('/api/auth/logout', { method: 'POST' });
      } catch (_) {}
      window.location.href = '/';
    },

    /**
     * Submit thumbs up/down feedback for an AI message via POST /api/feedback.
     * Re-clicking the active rating deselects it (sends rating: null).
     * Updates feedbacks map in local state on success.
     *
     * @param {string} messageId - The assistant message ID.
     * @param {'up'|'down'} rating - The rating to apply.
     */
    async submitFeedback(messageId, rating) {
      if (!messageId) return;
      const changes = this.feedbackChanges[messageId] || 0;
      if (changes >= this.feedbackChangeLimit) return;

      const current   = this.feedbacks[messageId] || null;
      const newRating = current === rating ? null : rating;

      this.feedbacks       = { ...this.feedbacks,       [messageId]: newRating };
      this.feedbackChanges = { ...this.feedbackChanges, [messageId]: changes + 1 };

      try {
        const res = await fetch('/api/feedback', {
          method:  'POST',
          headers: { 'Content-Type': 'application/json' },
          body:    JSON.stringify({ data: { message_id: messageId, rating: newRating } }),
        });

        if (res.status === 401) { this._redirectUnauthorized(); return; }

        if (!res.ok) {
          this.feedbacks       = { ...this.feedbacks,       [messageId]: current };
          this.feedbackChanges = { ...this.feedbackChanges, [messageId]: changes };
          this._errorBanner = 'Could not save feedback. Please try again.';
          setTimeout(() => { this._errorBanner = ''; }, 4000);
        }
      } catch (_) {
        this.feedbacks       = { ...this.feedbacks,       [messageId]: current };
        this.feedbackChanges = { ...this.feedbackChanges, [messageId]: changes };
        this._errorBanner = 'Could not save feedback. Please try again.';
        setTimeout(() => { this._errorBanner = ''; }, 4000);
      }
    },

    _redirectUnauthorized() {
      window.location.href = '/?error=session_expired';
    },

    /**
     * Disable the Send button for `seconds` seconds with a countdown label.
     *
     * @param {number} seconds - Duration of the cooldown.
     * @param {string} label   - Text to show during the first second.
     */
    _startCooldown(seconds, label) {
      this.sendDisabled      = true;
      this.sendCooldownLabel = label;

      let remaining = seconds;
      const tick = () => {
        remaining--;
        if (remaining <= 0) {
          this.sendDisabled      = false;
          this.sendCooldownLabel = '';
          return;
        }
        if (seconds >= 60) {
          this.sendCooldownLabel = `Wait ${remaining}s`;
        }
        this._cooldownTimer = setTimeout(tick, 1000);
      };
      this._cooldownTimer = setTimeout(tick, 1000);
    },

    /**
     * Handle API error responses.
     * 503 → disable Send for 5s, show detail.
     * 429 → disable Send for 60s with countdown, show rate-limit message.
     *
     * @param {number} status - HTTP status code.
     * @param {string} detail - Error detail from API response body.
     */
    _handleApiError(status, detail) {
      if (status === 503) {
        this._errorBanner = detail || 'Service temporarily unavailable. Please try again shortly.';
        this._startCooldown(5, 'Wait 5s');
      } else if (status === 429) {
        this._errorBanner = "You're sending messages too fast. Please wait a moment.";
        this._startCooldown(60, 'Wait 60s');
      }
    },

    /**
     * Scroll the messages area to the bottom after DOM update.
     */
    _scrollToBottom() {
      this.$nextTick(() => {
        const el = document.getElementById('messages-area');
        if (el) el.scrollTop = el.scrollHeight;
      });
    },
  };
}
