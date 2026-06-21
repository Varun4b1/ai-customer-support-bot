import json
import shutil
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, UploadFile, File, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, HTMLResponse, FileResponse
from starlette.middleware.sessions import SessionMiddleware
from pydantic import BaseModel

from app.rag import build_rag_chain, format_sources
from app.ingest import run_ingestion, ingest_single_file
from app.auth import oauth, get_current_user
from app.config import SECRET_KEY
from app.database import init_db, save_chat, get_chat_history, register_file, list_files

rag_chain = None
retriever = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global rag_chain, retriever
    print("Initializing database...")
    init_db()
    print("Loading RAG chain...")
    try:
        rag_chain, retriever = build_rag_chain()
        print("RAG chain ready.")
    except Exception as e:
        print(f"Could not load RAG chain: {e}")
    yield


app = FastAPI(
    title="AI Customer Support Bot",
    description="RAG bot with chat history + multi-file support",
    version="3.0.0",
    lifespan=lifespan,
)

app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    question: str
    session_id: str = "default"

class SourceDoc(BaseModel):
    source: str
    page: str | int
    snippet: str

class ChatResponse(BaseModel):
    answer: str
    sources: list[SourceDoc]
    session_id: str
    user: str


# ── Auth ─────────────────────────────────────────────────
@app.get("/auth/login", tags=["Auth"])
async def login(request: Request):
    redirect_uri = request.url_for("auth_callback")
    return await oauth.google.authorize_redirect(request, redirect_uri)


@app.get("/auth/callback", tags=["Auth"])
async def auth_callback(request: Request):
    token = await oauth.google.authorize_access_token(request)
    user = token.get("userinfo")
    request.session["user"] = {
        "email": user["email"],
        "name": user["name"],
        "picture": user.get("picture", ""),
    }
    return RedirectResponse(url="/")


@app.get("/auth/logout", tags=["Auth"])
async def logout(request: Request):
    request.session.clear()
    return {"message": "Logged out successfully."}


@app.get("/me", tags=["Auth"])
async def get_me(user=Depends(get_current_user)):
    return {"user": user}


# ── System ───────────────────────────────────────────────
@app.get("/health", tags=["System"])
def health_check():
    return {"status": "ok", "rag_loaded": rag_chain is not None}


@app.get("/", tags=["System"], response_class=HTMLResponse)
def home():
    return FileResponse("app/static/chat.html")


# ── Chat (protected) — now saves to DB ─────────────────────
@app.post("/chat", response_model=ChatResponse, tags=["Chat"])
async def chat(request: ChatRequest, user=Depends(get_current_user)):
    if rag_chain is None:
        raise HTTPException(status_code=503, detail="RAG chain not loaded.")
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")
    try:
        answer = rag_chain.invoke(request.question)
        docs = retriever.invoke(request.question)

        # Only attach sources if the bot actually used them.
        # If the answer says it doesn't know, the retrieved chunks
        # weren't relevant enough to use — don't show them as "evidence".
        no_info_phrases = ["i don't have information", "i do not have information", "contact our support"]
        answer_lower = answer.lower()
        used_context = not any(phrase in answer_lower for phrase in no_info_phrases)

        sources = format_sources(docs, answer) if used_context else []

        # Save this exchange to the database
        save_chat(
            user_email=user["email"],
            session_id=request.session_id,
            question=request.question,
            answer=answer,
            sources=json.dumps(sources),
        )

        return ChatResponse(
            answer=answer,
            sources=sources,
            session_id=request.session_id,
            user=user["email"],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chain error: {str(e)}")


# ── NEW: Chat history endpoint ──────────────────────────────
@app.get("/history", tags=["Chat"])
async def chat_history(user=Depends(get_current_user), limit: int = 50):
    """Returns this user's past conversations, most recent first."""
    history = get_chat_history(user["email"], limit=limit)
    for item in history:
        item["sources"] = json.loads(item["sources"]) if item["sources"] else []
    return {"user": user["email"], "count": len(history), "history": history}


# ── Ingest (protected) — multi-file aware ──────────────────
@app.post("/ingest", tags=["Documents"])
async def ingest_document(file: UploadFile = File(...), user=Depends(get_current_user)):
    """
    Upload a document — it gets ADDED to the existing knowledge base.
    Previously uploaded files are NOT deleted or overwritten.
    The bot can now search across ALL uploaded files at once.
    """
    allowed = {".pdf", ".txt"}
    ext = Path(file.filename).suffix.lower()
    if ext not in allowed:
        raise HTTPException(status_code=400, detail=f"Unsupported file type '{ext}'. Allowed: {allowed}")

    docs_dir = Path("./docs")
    docs_dir.mkdir(exist_ok=True)
    dest = docs_dir / file.filename

    with dest.open("wb") as f:
        shutil.copyfileobj(file.file, f)

    try:
        chunk_count = ingest_single_file(dest)

        register_file(
            filename=file.filename,
            uploaded_by=user["email"],
            chunk_count=chunk_count,
        )

        # Reload chain so retriever sees the newly added chunks
        global rag_chain, retriever
        rag_chain, retriever = build_rag_chain()

        return {
            "message": f"'{file.filename}' added to knowledge base.",
            "chunks_added": chunk_count,
            "uploaded_by": user["email"],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")


# ── NEW: List all uploaded files ────────────────────────────
@app.get("/files", tags=["Documents"])
async def get_files(user=Depends(get_current_user)):
    """Shows every file currently in the knowledge base."""
    return {"files": list_files()}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)