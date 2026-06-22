'use client';

import { useState, useRef, useEffect } from 'react';
import { api } from '@/lib/api';

function getSessionId() {
  const key = 'docurag_session_id';
  let id = sessionStorage.getItem(key);
  if (!id) {
    id = crypto.randomUUID();
    sessionStorage.setItem(key, id);
  }
  return id;
}

function SourceTabs({ sources }) {
  const [openIndex, setOpenIndex] = useState(null);
  if (!sources || sources.length === 0) return null;

  return (
    <div className="mt-2 flex flex-wrap gap-2">
      {sources.map((s, i) => (
        <div key={s.chunk_id || i}>
          <button
            type="button"
            className="citation-tab"
            onClick={() => setOpenIndex(openIndex === i ? null : i)}
            aria-expanded={openIndex === i}
          >
            {s.document || `Source ${i + 1}`}
          </button>
          {openIndex === i && (
            <div className="citation-panel rounded-md mt-1 max-w-md">
              <p>{s.content}</p>
              {typeof s.similarity === 'number' && (
                <p className="text-slate mt-1 text-xs">
                  Match confidence: {Math.round(s.similarity * 100)}%
                </p>
              )}
            </div>
          )}
        </div>
      ))}
    </div>
  );
}

export default function ChatPage({ params }) {
  const { slug } = params;
  const [messages, setMessages] = useState([]); // { role, content, sources? }
  const [question, setQuestion] = useState('');
  const [sending, setSending] = useState(false);
  const [error, setError] = useState('');
  const sessionIdRef = useRef(null);
  const bottomRef = useRef(null);

  useEffect(() => {
    sessionIdRef.current = getSessionId();
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  async function handleSend(e) {
    e.preventDefault();
    const q = question.trim();
    if (!q || sending) return;

    setMessages((prev) => [...prev, { role: 'user', content: q }]);
    setQuestion('');
    setSending(true);
    setError('');

    try {
      const res = await api.sendChatMessage(slug, q, sessionIdRef.current);
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: res.answer, sources: res.sources },
      ]);
    } catch (err) {
      const message =
        err.status === 404
          ? 'This chatbot doesn\u2019t exist or isn\u2019t public.'
          : err.status === 402
          ? 'This chatbot has hit its monthly message limit.'
          : err.data?.error || 'Something went wrong. Try again.';
      setError(message);
    } finally {
      setSending(false);
    }
  }

  return (
    <main className="min-h-screen flex flex-col max-w-2xl mx-auto px-4 py-6">
      <header className="mb-6">
        <p className="text-xs font-semibold tracking-[0.2em] text-teal uppercase mb-1">
          DocuRAG
        </p>
        <h1 className="font-display text-2xl font-semibold text-ink">{slug.replace(/-/g, ' ')}</h1>
        <p className="text-sm text-slate mt-1">
          Answers are grounded in the uploaded document. Tap a source tab to see the exact passage.
        </p>
      </header>

      <div className="flex-1 space-y-4 mb-4 overflow-y-auto">
        {messages.length === 0 && (
          <div className="border border-line rounded-lg p-6 text-center text-slate text-sm bg-white">
            Ask a question to get started.
          </div>
        )}

        {messages.map((m, i) => (
          <div key={i} className={m.role === 'user' ? 'flex justify-end' : 'flex justify-start'}>
            <div
              className={`max-w-[85%] rounded-lg px-4 py-3 text-sm ${
                m.role === 'user' ? 'bg-teal text-white' : 'bg-white border border-line text-ink'
              }`}
            >
              <p className="whitespace-pre-wrap">{m.content}</p>
              {m.role === 'assistant' && <SourceTabs sources={m.sources} />}
            </div>
          </div>
        ))}
        <div ref={bottomRef} />
      </div>

      {error && (
        <p className="text-sm text-clay bg-clay/10 border border-clay/30 rounded-md px-3 py-2 mb-3">
          {error}
        </p>
      )}

      <form onSubmit={handleSend} className="flex gap-2">
        <input
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="What does this document say about…"
          disabled={sending}
          className="flex-1 border border-line rounded-md px-3 py-2 text-sm focus:border-teal outline-none disabled:opacity-60"
        />
        <button
          type="submit"
          disabled={sending || !question.trim()}
          className="bg-teal hover:bg-teal-dark text-white text-sm font-medium px-4 py-2 rounded-md transition-colors disabled:opacity-60"
        >
          {sending ? 'Asking…' : 'Send'}
        </button>
      </form>
    </main>
  );
}
