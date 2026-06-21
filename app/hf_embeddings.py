"""
hf_embeddings.py
-----------------
A minimal LangChain-compatible embedding class that calls
HuggingFace's current Inference API directly via huggingface_hub,
avoiding langchain-huggingface's version conflicts and deprecated
endpoint issues.
"""

from huggingface_hub import InferenceClient
from langchain_core.embeddings import Embeddings


class HFInferenceEmbeddings(Embeddings):
    def __init__(self, model: str, api_token: str):
        self.client = InferenceClient(model=model, token=api_token)

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self.client.feature_extraction(text).tolist() for text in texts]

    def embed_query(self, text: str) -> list[float]:
        return self.client.feature_extraction(text).tolist()