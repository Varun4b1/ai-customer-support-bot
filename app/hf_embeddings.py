"""
hf_embeddings.py
-----------------
Lightweight local embeddings using fastembed (ONNX-based) —
no PyTorch, no network calls, fits comfortably in 512MB RAM.
"""

from fastembed import TextEmbedding
from langchain_core.embeddings import Embeddings


class HFInferenceEmbeddings(Embeddings):
    def __init__(self, model: str, api_token: str = ""):
        # api_token kept for interface compatibility, unused by fastembed
        fastembed_model = "BAAI/bge-small-en-v1.5"
        self.model = TextEmbedding(model_name=fastembed_model)

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [vec.tolist() for vec in self.model.embed(texts)]

    def embed_query(self, text: str) -> list[float]:
        return list(self.model.embed([text]))[0].tolist()