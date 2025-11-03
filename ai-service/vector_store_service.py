import faiss
import numpy as np
import pickle
from pathlib import Path
from typing import List, Tuple, Dict

class VectorStoreService:
    def __init__(self, dimension: int = 384, index_path: str = None):
        self.dimension = dimension
        self.index = faiss.IndexFlatL2(dimension)
        self.documents = []
        self.index_path = Path(index_path) if index_path else None
        
        # Create index directory if it doesn't exist
        if self.index_path:
            self.index_path.mkdir(parents=True, exist_ok=True)
    
    def add_documents(self, embeddings: np.ndarray, documents: List[dict]):
        """Add documents and their embeddings to the index"""
        self.index.add(embeddings.astype('float32'))
        self.documents.extend(documents)
    
    def search(self, query_embedding: np.ndarray, top_k: int = 5) -> List[Tuple[dict, float]]:
        """Search for similar documents"""
        distances, indices = self.index.search(
            query_embedding.reshape(1, -1).astype('float32'), 
            top_k
        )
        results = [
            (self.documents[idx], float(dist)) 
            for idx, dist in zip(indices[0], distances[0])
            if idx != -1 and idx < len(self.documents)
        ]
        return results
    
    def save(self):
        """Save index and documents to disk"""
        if self.index_path:
            faiss.write_index(self.index, str(self.index_path / "faiss.index"))
            with open(str(self.index_path / "documents.pkl"), 'wb') as f:
                pickle.dump(self.documents, f)
    
    def load(self):
        """Load index and documents from disk"""
        if self.index_path:
            if (self.index_path / "faiss.index").exists():
                self.index = faiss.read_index(str(self.index_path / "faiss.index"))
            if (self.index_path / "documents.pkl").exists():
                with open(str(self.index_path / "documents.pkl"), 'rb') as f:
                    self.documents = pickle.load(f)