const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

/**
 * Wait, retrying with exponential backoff. Render's free tier spins down
 * after 15 min idle, so the first request after a break can take 20-30s.
 */
async function withRetry(fn, attempts = 3) {
  let lastError;
  for (let i = 0; i < attempts; i++) {
    try {
      return await fn();
    } catch (err) {
      lastError = err;
      const delay = 1000 * 2 ** i; // 1s, 2s, 4s
      await new Promise((res) => setTimeout(res, delay));
    }
  }
  throw lastError;
}

async function request(path, { method = 'GET', body, token, isForm = false } = {}) {
  const headers = {};
  if (token) headers.Authorization = `Bearer ${token}`;
  if (!isForm) headers['Content-Type'] = 'application/json';

  const res = await fetch(`${API_URL}${path}`, {
    method,
    headers,
    body: isForm ? body : body ? JSON.stringify(body) : undefined,
  });

  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    const error = new Error(data.error || `Request failed (${res.status})`);
    error.status = res.status;
    error.data = data;
    throw error;
  }
  return data;
}

export const api = {
  health: () => withRetry(() => request('/health')),

  createChatbot: (name, description, token) =>
    request('/chatbots', {
      method: 'POST',
      body: { name, description, is_public: true },
      token,
    }),

  uploadDocument: (file, chatbotId, token) => {
    const form = new FormData();
    form.append('file', file);
    form.append('chatbot_id', chatbotId);
    return request('/documents/upload', { method: 'POST', body: form, token, isForm: true });
  },

  documentStatus: (documentId, token) => request(`/documents/${documentId}/status`, { token }),

  sendChatMessage: (slug, question, sessionId) =>
    request(`/chat/${slug}`, {
      method: 'POST',
      body: { question, session_id: sessionId },
    }),
};

export { API_URL, withRetry };
