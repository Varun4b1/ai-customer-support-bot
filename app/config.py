import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY          = os.getenv("GROQ_API_KEY", "")
LLM_MODEL             = "llama-3.3-70b-versatile"
EMBED_MODEL           = "sentence-transformers/all-MiniLM-L6-v2"
HF_API_TOKEN          = os.getenv("HF_API_TOKEN", "")

CHROMA_DIR            = "./vectorstore"
COLLECTION            = "support_docs"
CHUNK_SIZE            = 800
CHUNK_OVERLAP         = 100
TOP_K                 = 4

GOOGLE_CLIENT_ID      = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET  = os.getenv("GOOGLE_CLIENT_SECRET", "")
SECRET_KEY            = os.getenv("SECRET_KEY", "supersecretkey")