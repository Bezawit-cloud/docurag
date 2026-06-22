# DocuRAG — Web Frontend

Next.js frontend for DocuRAG, replacing the original Gradio UI. Talks to the
existing FastAPI backend (Week 2) and Supabase Auth directly from the browser.

## Pages

- `/login` — sign up / log in (Supabase Auth)
- `/dashboard` — create a chatbot, upload a document, watch it get processed
- `/chat/[slug]` — public chat page, no login required. Answers show their
  sources as clickable margin tabs.

## Local setup

```bash
npm install
cp .env.example .env.local   # fill in your values
npm run dev
```

Make sure your FastAPI backend is running (`uvicorn main:app --reload`) and
has CORS enabled for `http://localhost:3000`:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://your-app.vercel.app"],
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Environment variables

| Variable | Description |
|---|---|
| `NEXT_PUBLIC_API_URL` | FastAPI backend URL (localhost in dev, Render URL in prod) |
| `NEXT_PUBLIC_SUPABASE_URL` | From Supabase project settings → API |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | From Supabase project settings → API (anon/public key — never the service_role key here) |

## Deploying to Vercel

1. Push this folder to GitHub.
2. Import the repo on [vercel.com](https://vercel.com) (free tier).
3. Set the three env vars above in the Vercel project settings.
4. Deploy. Add the resulting `*.vercel.app` domain to your backend's
   `allow_origins` list.

## Notes on Render cold starts

The free Render tier spins down after 15 minutes idle. The first request
after a break can take 20-30 seconds. `lib/api.js` retries failed requests
with exponential backoff (1s, 2s, 4s) so the dashboard and chat page recover
gracefully instead of just erroring out.
