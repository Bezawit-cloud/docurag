'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { supabase } from '@/lib/supabaseClient';

export default function LoginPage() {
  const router = useRouter();
  const [mode, setMode] = useState('login'); // 'login' | 'signup'
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setError('');
    setLoading(true);

    const action =
      mode === 'login'
        ? supabase.auth.signInWithPassword({ email, password })
        : supabase.auth.signUp({ email, password });

    const { data, error: authError } = await action;
    setLoading(false);

    if (authError) {
      setError(authError.message);
      return;
    }
    if (data.session) {
      router.push('/dashboard');
    } else if (mode === 'signup') {
      setError('Check your inbox to confirm your email, then log in.');
    }
  }

  return (
    <main className="min-h-screen flex items-center justify-center px-6 py-12">
      <div className="w-full max-w-md">
        <header className="mb-10 text-center">
          <p className="text-xs font-semibold tracking-[0.2em] text-teal uppercase mb-2">
            DocuRAG
          </p>
          <h1 className="font-display text-3xl font-semibold text-ink mb-2">
            Ask your documents anything
          </h1>
          <p className="text-slate text-sm">
            Upload a document, get a chatbot that answers with the receipts.
          </p>
        </header>

        <div className="bg-white border border-line rounded-lg p-8 shadow-sm">
          <div className="flex gap-1 mb-6 bg-paper rounded-md p-1 border border-line">
            <button
              type="button"
              onClick={() => setMode('login')}
              className={`flex-1 text-sm font-medium py-2 rounded-md transition-colors ${
                mode === 'login' ? 'bg-teal text-white' : 'text-slate hover:text-ink'
              }`}
            >
              Log in
            </button>
            <button
              type="button"
              onClick={() => setMode('signup')}
              className={`flex-1 text-sm font-medium py-2 rounded-md transition-colors ${
                mode === 'signup' ? 'bg-teal text-white' : 'text-slate hover:text-ink'
              }`}
            >
              Sign up
            </button>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-ink mb-1">
                Email
              </label>
              <input
                id="email"
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full border border-line rounded-md px-3 py-2 text-sm focus:border-teal outline-none"
                placeholder="you@example.com"
              />
            </div>
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-ink mb-1">
                Password
              </label>
              <input
                id="password"
                type="password"
                required
                minLength={6}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full border border-line rounded-md px-3 py-2 text-sm focus:border-teal outline-none"
                placeholder="At least 6 characters"
              />
            </div>

            {error && (
              <p className="text-sm text-clay bg-clay/10 border border-clay/30 rounded-md px-3 py-2">
                {error}
              </p>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-teal hover:bg-teal-dark text-white text-sm font-medium py-2.5 rounded-md transition-colors disabled:opacity-60"
            >
              {loading ? 'Working…' : mode === 'login' ? 'Log in' : 'Create account'}
            </button>
          </form>
        </div>
      </div>
    </main>
  );
}
