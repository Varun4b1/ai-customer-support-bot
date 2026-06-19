# 🤖 AI Customer Support Bot

A production-ready RAG-powered customer support chatbot built with **LangChain**, **FastAPI**, and **ChromaDB**.

Upload your product documentation and the bot answers customer questions accurately — with source citations.

---

## Architecture

```
Documents (PDF/TXT/CSV)
       ↓
   Chunker (LangChain TextSplitter)
       ↓
   Embedder (OpenAI text-embedding-3-small)
       ↓
   ChromaDB (Vector Store)
       ↑
   Retriever (Top-K similarity search)
       ↑
User Question → FastAPI → LangChain RAG Chain → LLM (GPT-4o-mini) → Answer + Sources
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| API | FastAPI + Uvicorn |
| RAG Orchestration | LangChain |
| Vector Database | ChromaDB |
| Embeddings | OpenAI text-embedding-3-small |
| LLM | GPT-4o-mini |
| Language | Python 3.11+ |

---

## Quick Start

### 1. Clone & install
```bash
git clone https://github.com/yourusername/customer-support-bot
cd customer-support-bot
pip install -r requirements.txt
```

### 2. Set up environment
```bash
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

### 3. Add your documents
```bash
# Drop your PDF, TXT, or CSV files into ./docs/
cp your_product_faq.pdf ./docs/
```

### 4. Run ingestion (one-time setup)
```bash
python -m app.ingest
```

### 5. Start the server
```bash
uvicorn app.main:app --reload
```

### 6. Test it
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "How do I reset my password?"}'
```

---

## API Endpoints

### `POST /chat`
Ask the bot a question.

**Request:**
```json
{
  "question": "How do I cancel my subscription?",
  "session_id": "user_123"
}
```

**Response:**
```json
{
  "answer": "You can cancel anytime from Settings > Billing > Cancel Subscription...",
  "sources": [
    {
      "source": "docs/faq.txt",
      "page": "",
      "snippet": "You can cancel anytime from Settings > Billing..."
    }
  ],
  "session_id": "user_123"
}
```

### `POST /ingest`
Upload a new document and re-index.

```bash
curl -X POST http://localhost:8000/ingest \
  -F "file=@new_docs.pdf"
```

### `GET /health`
Check server status.

---

## Features

- **RAG pipeline** — answers grounded in your documents, not hallucinated
- **Source citations** — every answer includes which doc it came from
- **Conversation memory** — remembers last 5 exchanges per session
- **Live ingestion** — upload new docs via API without restarting
- **Auto-rejects unknowns** — says "I don't know" instead of making things up
- **Interactive docs** — Swagger UI at `http://localhost:8000/docs`

---

## Project Structure

```
customer-support-bot/
├── app/
│   ├── main.py       # FastAPI app & endpoints
│   ├── rag.py        # LangChain RAG chain
│   ├── ingest.py     # Ingestion pipeline
│   └── config.py     # Settings & env vars
├── docs/             # Your documents go here
├── vectorstore/      # ChromaDB auto-created here
├── .env.example      # Environment template
├── requirements.txt
└── README.md
```

---

## Deployment (Render.com — Free)

1. Push to GitHub
2. Go to [render.com](https://render.com) → New Web Service
3. Connect your repo
4. Set build command: `pip install -r requirements.txt`
5. Set start command: `uvicorn app.main:app --host 0.0.0.0 --port 8000`
6. Add `OPENAI_API_KEY` in Environment Variables
7. Deploy!

---

## Built With

- [LangChain](https://langchain.com)
- [FastAPI](https://fastapi.tiangolo.com)
- [ChromaDB](https://trychroma.com)
- [OpenAI](https://openai.com)

---

*Built as a portfolio project demonstrating RAG, LLM integration, and REST API design.*
