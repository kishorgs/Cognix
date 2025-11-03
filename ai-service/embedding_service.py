from sentence_transformers import SentenceTransformer
from typing import List
import numpy as np
import os
from pathlib import Path

class EmbeddingService:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
    
    def generate_embeddings(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings for a list of texts"""
        embeddings = self.model.encode(texts, show_progress_bar=True)
        return embeddings
    
    def generate_query_embedding(self, query: str) -> np.ndarray:
        """Generate embedding for a single query"""
        return self.model.encode([query])[0]