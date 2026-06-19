# 🤖 AI Customer Support Bot

A production-style RAG-powered customer support chatbot built with **LangChain**, **FastAPI**, **ChromaDB**, and **Google OAuth**.

Upload your product documentation, sign in with Google, and chat with a bot that answers strictly from your documents — every answer traceable to its source, with full conversation history saved per user.

---

## Live demo

A real chat interface is included — open `http://localhost:8000/` after setup to sign in and start chatting (not just Swagger docs).

---

## Features

- **RAG pipeline** — answers grounded in uploaded documents, not hallucinated
- **Google OAuth 2.0** — only authenticated users can chat; each session is tied to a real identity
- **Persistent chat history** — every conversation is saved in SQLite, scoped per user
- **Multi-file knowledge base** — upload multiple PDFs/TXT files; the bot searches across all of them at once, with new files added incrementally (no full re-index needed)
- **Accurate source citations** — answers only cite documents that genuinely contributed content, filtered by keyword overlap, not just "anything retrieved"
- **Custom chat UI** — a clean, branded frontend (not just an API) showing live source citations as evidence chips under each answer
- **Honest refusals** — if the answer isn't in the documents, the bot says so instead of guessing

---

## Architecture

```
Documents (PDF/TXT)
       ↓
   Chunker (LangChain TextSplitter)
       ↓
   Embedder (HuggingFace sentence-transformers, local + free)
       ↓
   ChromaDB (Vector Store, incrementally updated)
       ↑
   Retriever (Top-K similarity search across all files)
       ↑
User (Google OAuth) → FastAPI → LangChain RAG Chain → LLM (Groq Llama 3.3) → Answer + filtered sources
       ↓
   SQLite (chat history + file registry, per user)
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| API | FastAPI + Uvicorn |
| RAG Orchestration | LangChain |
| Vector Database | ChromaDB |
| Embeddings | HuggingFace `sentence-transformers/all-MiniLM-L6-v2` (local, free) |
| LLM | Groq — `llama-3.3-70b-versatile` (free tier) |
| Auth | Google OAuth 2.0 via Authlib |
| Persistence | SQLite (chat history, file registry) |
| Frontend | Vanilla HTML/CSS/JS chat UI |
| Language | Python 3.11+ |

---

## Project Structure

```
customer-support-bot/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI app — chat, ingest, auth, history endpoints
│   ├── rag.py            # LangChain RAG chain + relevance-filtered source citations
│   ├── ingest.py          # Ingestion pipeline (full + incremental single-file)
│   ├── auth.py            # Google OAuth 2.0 logic (Authlib)
│   ├── config.py          # Settings & environment variables
│   ├── database.py        # SQLite — chat history + uploaded file registry
│   └── static/
│       └── chat.html      # Frontend chat UI
├── docs/                   # Uploaded documents live here
├── vectorstore/             # ChromaDB storage (gitignored, auto-created)
├── .vscode/                  # VS Code run/debug configs
├── .env                       # Real secrets (gitignored — never committed)
├── .env.example                # Template for required environment variables
├── .gitignore
├── requirements.txt
├── support_bot.db               # SQLite database (gitignored)
└── README.md
```

---

## Quick Start

### 1. Clone & install
```bash
git clone https://github.com/Varun4b1/ai-customer-support-bot
cd ai-customer-support-bot
pip install -r requirements.txt
```

### 2. Set up environment variables
```bash
cp .env.example .env
```
Fill in `.env` with:
- `GROQ_API_KEY` — free key from [console.groq.com](https://console.groq.com)
- `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET` — from [Google Cloud Console](https://console.cloud.google.com) (OAuth 2.0 Client, redirect URI `http://127.0.0.1:8000/auth/callback`)
- `SECRET_KEY` — any random string, used to sign session cookies

### 3. Add your documents
```bash
# Drop PDF or TXT files into ./docs/
cp your_product_faq.pdf ./docs/
```

### 4. Run initial ingestion
```bash
python -m app.ingest
```

### 5. Start the server
```bash
uvicorn app.main:app --reload
```

### 6. Open the chat UI
```
http://127.0.0.1:8000/
```
Sign in with Google and start chatting.

---

## API Endpoints

| Method | Route | Description |
|---|---|---|
| `GET` | `/` | Chat UI (sign-in + chat interface) |
| `GET` | `/auth/login` | Starts Google OAuth login |
| `GET` | `/auth/callback` | Google's redirect target after login |
| `GET` | `/auth/logout` | Clears the current session |
| `GET` | `/me` | Returns the current authenticated user |
| `POST` | `/chat` | Ask a question — returns answer + filtered sources |
| `GET` | `/history` | Returns the logged-in user's past conversations |
| `POST` | `/ingest` | Upload a new document — added to the existing knowledge base |
| `GET` | `/files` | Lists every document currently indexed |
| `GET` | `/health` | Server health check |

Interactive API docs (Swagger): `http://127.0.0.1:8000/docs`

---

## How source filtering works

Naively, RAG retrieves the top-K most similar chunks regardless of whether the LLM actually used them. This bot improves on that in two ways:

1. If the answer indicates the bot doesn't know ("I don't have information on that"), **no sources are shown at all** — since nothing was meaningfully used.
2. Otherwise, each retrieved chunk's source is only shown if it has **meaningful keyword overlap** with the generated answer (at least 3 shared significant words), filtering out documents that were retrieved but not actually relevant.

This makes the "evidence chips" in the UI an honest reflection of what the model actually used, not just what was nearby in vector space.

---

## Deployment (Render.com — Free)

1. Push to GitHub
2. Go to [render.com](https://render.com) → New Web Service → connect your repo
3. Build command: `pip install -r requirements.txt`
4. Start command: `uvicorn app.main:app --host 0.0.0.0 --port 8000`
5. Add environment variables (`GROQ_API_KEY`, `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `SECRET_KEY`)
6. Update your Google OAuth redirect URI to your Render URL once deployed
7. Deploy

---

## Built With

- [LangChain](https://langchain.com)
- [FastAPI](https://fastapi.tiangolo.com)
- [ChromaDB](https://trychroma.com)
- [Groq](https://groq.com)
- [Authlib](https://docs.authlib.org)

---

*Built as a portfolio project demonstrating RAG, LLM integration, OAuth security, persistent state, and REST API design.*