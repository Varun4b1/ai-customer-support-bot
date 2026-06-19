from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader, TextLoader, DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from app.config import EMBED_MODEL, CHROMA_DIR, COLLECTION, CHUNK_SIZE, CHUNK_OVERLAP

DOCS_DIR = Path("./docs")


def load_documents():
    loaders = [
        DirectoryLoader(str(DOCS_DIR), glob="**/*.pdf", loader_cls=PyPDFLoader),
        DirectoryLoader(str(DOCS_DIR), glob="**/*.txt", loader_cls=TextLoader),
    ]
    all_docs = []
    for loader in loaders:
        try:
            docs = loader.load()
            all_docs.extend(docs)
            print(f"  Loaded {len(docs)} docs with {loader.__class__.__name__}")
        except Exception as e:
            print(f"  Warning: {e}")
    return all_docs


def chunk_documents(documents):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )
    chunks = splitter.split_documents(documents)
    print(f"  Split into {len(chunks)} chunks")
    return chunks


def embed_and_store(chunks):
    """Embed and store ALL chunks in ONE shared collection.
    Each chunk's metadata already includes 'source' (the filename),
    so multi-file search works automatically — no extra setup needed."""
    embeddings = HuggingFaceEmbeddings(model_name=EMBED_MODEL)
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        collection_name=COLLECTION,
        persist_directory=CHROMA_DIR,
    )
    print(f"  Stored {len(chunks)} chunks in ChromaDB at '{CHROMA_DIR}'")
    return vectorstore


def ingest_single_file(filepath: Path):
    """Ingest ONE new file and ADD it to the existing collection
    (instead of rebuilding everything from scratch)."""
    ext = filepath.suffix.lower()

    if ext == ".pdf":
        loader = PyPDFLoader(str(filepath))
    elif ext == ".txt":
        loader = TextLoader(str(filepath))
    else:
        raise ValueError(f"Unsupported file type: {ext}")

    documents = loader.load()
    chunks = chunk_documents(documents)

    embeddings = HuggingFaceEmbeddings(model_name=EMBED_MODEL)
    vectorstore = Chroma(
        collection_name=COLLECTION,
        embedding_function=embeddings,
        persist_directory=CHROMA_DIR,
    )
    vectorstore.add_documents(chunks)   # ADDS without wiping existing data

    print(f"  Added {len(chunks)} chunks from '{filepath.name}'")
    return len(chunks)


def run_ingestion():
    """Full re-ingestion of everything in ./docs/ — used for initial setup."""
    print("\nStarting ingestion pipeline...")
    if not DOCS_DIR.exists() or not any(DOCS_DIR.iterdir()):
        print("No files found in ./docs/")
        return
    print("Loading documents...")
    documents = load_documents()
    if not documents:
        print("No documents loaded.")
        return
    print("Chunking documents...")
    chunks = chunk_documents(documents)
    print("Embedding and storing in ChromaDB...")
    embed_and_store(chunks)
    print("Ingestion complete!\n")


if __name__ == "__main__":
    run_ingestion()