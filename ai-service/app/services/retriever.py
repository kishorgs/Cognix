"""
Document retriever service for fetching relevant documents from vector store.
"""

from typing import List, Dict, Tuple
import numpy as np

class Retriever:
    def __init__(self, vector_store):
        """Initialize retriever with vector store.
        
        Args:
            vector_store: Vector store instance for document storage and retrieval
        """
        self.vector_store = vector_store
    
    def retrieve(
        self, 
        query_embedding: np.ndarray, 
        top_k: int = 5,
        score_threshold: float = 0.7
    ) -> List[Tuple[Dict, float]]:
        """Retrieve relevant documents based on query embedding.
        
        Args:
            query_embedding: Embedding vector of the query
            top_k: Number of documents to retrieve
            score_threshold: Minimum similarity score threshold
            
        Returns:
            List of tuples containing (document, similarity_score)
        """
        # Search vector store
        results = self.vector_store.search(
            query_embedding,
            top_k=top_k
        )
        
        # Filter by score threshold
        filtered_results = [
            (doc, score) for doc, score in results 
            if score >= score_threshold
        ]
        
        return filtered_results
    
    def batch_retrieve(
        self, 
        query_embeddings: List[np.ndarray],
        top_k: int = 5,
        score_threshold: float = 0.7
    ) -> List[List[Tuple[Dict, float]]]:
        """Retrieve relevant documents for multiple queries.
        
        Args:
            query_embeddings: List of query embedding vectors
            top_k: Number of documents to retrieve per query
            score_threshold: Minimum similarity score threshold
            
        Returns:
            List of results for each query
        """
        results = []
        for embedding in query_embeddings:
            query_results = self.retrieve(
                embedding,
                top_k=top_k,
                score_threshold=score_threshold
            )
            results.append(query_results)
        return results