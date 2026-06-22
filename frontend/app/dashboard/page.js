'use client';

import { useEffect, useState, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { supabase } from '@/lib/supabaseClient';
import { api, API_URL } from '@/lib/api';

const POLL_INTERVAL_MS = 3000;
const MAX_POLLS = 30; // ~90 seconds

export default function DashboardPage() {
  const router = useRouter();
  const [session, setSession] = useState(null);
  const [checkingSession, setCheckingSession] = useState(true);

  const [botName, setBotName] = useState('');
  const [botDescription, setBotDescription] = useState('');
  const [chatbot, setChatbot] = useState(null); // { id, slug, chat_url }
  const [creating, setCreating] = useState(false);
  const [createError, setCreateError] = useState('');

  const [file, setFile] = useState(null);
  const [uploadState, setUploadState] = useState('idle'); // idle | uploading | processing | ready | failed
  const [uploadMessage, setUploadMessage] = useState('');

  useEffect(() => {
    supabase.auth.getSession().then(({ data }) => {
      if (!data.session) {
        router.replace('/login');
        return;
      }
      setSession(data.session);
      setCheckingSession(false);
    });
  }, [router]);

  async function handleCreateChatbot(e) {
    e.preventDefault();
    setCreateError('');
    setCreating(true);
    try {
      const res = await api.createChatbot(botName, botDescription, session.access_token);
      setChatbot(res);
    } catch (err) {
      setCreateError(err.data?.error || err.message);
    } finally {
      setCreating(false);
    }
  }

  const pollStatus = useCallback(
    async (documentId) => {
      for (let i = 0; i < MAX_POLLS; i++) {
        await new Promise((res) => setTimeout(res, POLL_INTERVAL_MS));
        try {
          const status = await api.documentStatus(documentId, session.access_token);
          if (status.status === 'ready') {
            setUploadState('ready');
            setUploadMessage(`Ready — ${status.chunk_count} chunks indexed.`);
            return;
          }
          if (status.status === 'failed') {
            setUploadState('failed');
            setUploadMessage(status.error_msg || 'Processing failed.');
            return;
          }
        } catch (err) {
          // keep polling through transient errors (e.g. cold start)
        }
      }
      setUploadState('failed');
      setUploadMessage('Still processing — refresh in a bit to check again.');
    },
    [session]
  );

  async function handleUpload(e) {
    e.preventDefault();
    if (!file || !chatbot) return;
    setUploadState('uploading');
    setUploadMessage('Uploading…');
    try {
      const res = await api.uploadDocument(file, chatbot.id, session.access_token);
      setUploadState('processing');
      setUploadMessage('Processing your document…');
      pollStatus(res.document_id);
    } catch (err) {
      setUploadState('failed');
      setUploadMessage(err.data?.error || err.message);
    }
  }

  async function handleLogout() {
    await supabase.auth.signOut();
    router.replace('/login');
  }

  if (checkingSession) {
    return (
      <main className="min-h-screen flex items-center justify-center">
        <p className="text-slate text-sm">Loading…</p>
      </main>
    );
  }

  return (
    <main className="min-h-screen px-6 py-10 max-w-2xl mx-auto">
      <div className="flex items-center justify-between mb-10">
        <div>
          <p className="text-xs font-semibold tracking-[0.2em] text-teal uppercase mb-1">
            DocuRAG
          </p>
          <h1 className="font-display text-2xl font-semibold text-ink">Dashboard</h1>
        </div>
        <button
          onClick={handleLogout}
          className="text-sm text-slate hover:text-ink underline underline-offset-2"
        >
          Log out
        </button>
      </div>

      {/* Step 1: create chatbot */}
      <section className="bg-white border border-line rounded-lg p-6 mb-6">
        <h2 className="font-display text-lg font-semibold text-ink mb-1">1. Create a chatbot</h2>
        <p className="text-sm text-slate mb-4">Give it a name. You can add documents next.</p>

        {chatbot ? (
          <div className="citation-panel rounded-md">
            <p className="text-ink font-medium">{chatbot.name || botName}</p>
            <p className="text-slate mt-1">
              Public link:{' '}
              <a
                href={chatbot.chat_url || `/chat/${chatbot.slug}`}
                className="text-teal underline underline-offset-2"
              >
                {chatbot.chat_url || `/chat/${chatbot.slug}`}
              </a>
            </p>
          </div>
        ) : (
          <form onSubmit={handleCreateChatbot} className="space-y-3">
            <input
              type="text"
              required
              value={botName}
              onChange={(e) => setBotName(e.target.value)}
              placeholder="e.g. Acme Product FAQ"
              className="w-full border border-line rounded-md px-3 py-2 text-sm focus:border-teal outline-none"
            />
            <input
              type="text"
              value={botDescription}
              onChange={(e) => setBotDescription(e.target.value)}
              placeholder="What should it answer questions about? (optional)"
              className="w-full border border-line rounded-md px-3 py-2 text-sm focus:border-teal outline-none"
            />
            {createError && (
              <p className="text-sm text-clay bg-clay/10 border border-clay/30 rounded-md px-3 py-2">
                {createError}
              </p>
            )}
            <button
              type="submit"
              disabled={creating}
              className="bg-teal hover:bg-teal-dark text-white text-sm font-medium px-4 py-2 rounded-md transition-colors disabled:opacity-60"
            >
              {creating ? 'Creating…' : 'Create chatbot'}
            </button>
          </form>
        )}
      </section>

      {/* Step 2: upload document */}
      <section className="bg-white border border-line rounded-lg p-6">
        <h2 className="font-display text-lg font-semibold text-ink mb-1">2. Add a document</h2>
        <p className="text-sm text-slate mb-4">PDF, DOCX, or TXT.</p>

        {!chatbot ? (
          <p className="text-sm text-slate italic">Create a chatbot first.</p>
        ) : (
          <form onSubmit={handleUpload} className="space-y-3">
            <input
              type="file"
              accept=".pdf,.docx,.txt"
              onChange={(e) => setFile(e.target.files?.[0] || null)}
              className="block w-full text-sm text-slate file:mr-3 file:py-2 file:px-4 file:rounded-md file:border-0 file:bg-paper file:border file:border-line file:text-ink file:text-sm"
            />
            <button
              type="submit"
              disabled={!file || uploadState === 'uploading' || uploadState === 'processing'}
              className="bg-teal hover:bg-teal-dark text-white text-sm font-medium px-4 py-2 rounded-md transition-colors disabled:opacity-60"
            >
              {uploadState === 'uploading' || uploadState === 'processing'
                ? 'Working…'
                : 'Upload & process'}
            </button>

            {uploadMessage && (
              <p
                className={`text-sm rounded-md px-3 py-2 border ${
                  uploadState === 'failed'
                    ? 'text-clay bg-clay/10 border-clay/30'
                    : uploadState === 'ready'
                    ? 'text-teal bg-teal/5 border-teal/30'
                    : 'text-slate bg-paper border-line'
                }`}
              >
                {uploadMessage}
              </p>
            )}
          </form>
        )}
      </section>

      {chatbot && uploadState === 'ready' && (
        <a
          href={`/chat/${chatbot.slug}`}
          className="mt-6 inline-block text-sm font-medium text-teal underline underline-offset-2"
        >
          Try the live chatbot →
        </a>
      )}
    </main>
  );
}
