import faiss
import numpy as np
import pickle
import logging
from pathlib import Path
from typing import List, Tuple, Dict, Optional
from threading import Lock

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VectorStoreService:
    """
    A service class for managing FAISS vector store operations.
    
    Provides methods to add documents, search for similar vectors,
    and persist/load the index to/from disk.
    """
    
    def __init__(
        self, 
        dimension: int = 384, 
        index_path: Optional[str] = None,
        index_type: str = "flat"
    ):
        """
        Initialize the VectorStoreService.
        
        Args:
            dimension: Dimensionality of the vectors (default: 384 for MiniLM)
            index_path: Path to save/load the index (default: None)
            index_type: Type of FAISS index to use (default: "flat")
        """
        self.dimension = dimension
        self.index_type = index_type
        self.documents: List[Dict] = []
        self.index_path = Path(index_path) if index_path else None
        self._lock = Lock()  # Thread safety for concurrent operations
        
        # Initialize the FAISS index
        self.index = self._create_index()
        
        # Create index directory if it doesn't exist
        if self.index_path:
            self.index_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Index directory created/verified at: {self.index_path}")
    
    def _create_index(self) -> faiss.Index:
        """
        Create a FAISS index based on the specified type.
        
        Returns:
            A FAISS index instance
        """
        if self.index_type == "flat":
            return faiss.IndexFlatL2(self.dimension)
        elif self.index_type == "ivf":
            # For larger datasets, use IVF (Inverted File Index)
            quantizer = faiss.IndexFlatL2(self.dimension)
            return faiss.IndexIVFFlat(quantizer, self.dimension, 100)
        else:
            logger.warning(f"Unknown index type '{self.index_type}', defaulting to flat")
            return faiss.IndexFlatL2(self.dimension)
    
    def add_documents(
        self, 
        embeddings: np.ndarray, 
        documents: List[Dict]
    ) -> None:
        """
        Add documents and their embeddings to the index.
        
        Args:
            embeddings: Numpy array of embeddings (shape: [n, dimension])
            documents: List of document dictionaries with metadata
            
        Raises:
            ValueError: If embeddings and documents don't match in count
        """
        with self._lock:
            try:
                # Validate inputs
                if len(embeddings) != len(documents):
                    raise ValueError(
                        f"Embeddings count ({len(embeddings)}) doesn't match "
                        f"documents count ({len(documents)})"
                    )
                
                # Validate embedding dimensions
                if embeddings.shape[1] != self.dimension:
                    raise ValueError(
                        f"Embedding dimension ({embeddings.shape[1]}) doesn't match "
                        f"expected dimension ({self.dimension})"
                    )
                
                # Add to index
                embeddings_float32 = embeddings.astype('float32')
                self.index.add(embeddings_float32)
                self.documents.extend(documents)
                
                logger.info(
                    f"Added {len(documents)} documents. "
                    f"Total documents: {len(self.documents)}"
                )
                
            except Exception as e:
                logger.error(f"Error adding documents: {e}")
                raise
    
    def search(
        self, 
        query_embedding: np.ndarray, 
        top_k: int = 5,
        threshold: Optional[float] = None
    ) -> List[Tuple[Dict, float]]:
        """
        Search for similar documents based on query embedding.
        
        Args:
            query_embedding: Query vector (shape: [dimension])
            top_k: Number of results to return (default: 5)
            threshold: Optional distance threshold to filter results
            
        Returns:
            List of tuples containing (document, distance_score)
        """
        with self._lock:
            try:
                # Validate index has data
                if self.index.ntotal == 0:
                    logger.warning("Index is empty. No documents to search.")
                    return []
                
                # Ensure top_k doesn't exceed available documents
                top_k = min(top_k, len(self.documents))
                
                # Perform search
                query_float32 = query_embedding.reshape(1, -1).astype('float32')
                distances, indices = self.index.search(query_float32, top_k)
                
                # Build results with validation
                results = []
                for idx, dist in zip(indices[0], distances[0]):
                    # Skip invalid indices
                    if idx == -1 or idx >= len(self.documents):
                        continue
                    
                    # Apply threshold filter if specified
                    if threshold is not None and dist > threshold:
                        continue
                    
                    results.append((self.documents[idx], float(dist)))
                
                logger.info(f"Search returned {len(results)} results")
                return results
                
            except Exception as e:
                logger.error(f"Error during search: {e}")
                raise
    
    def save(self) -> bool:
        """
        Save the index and documents to disk.
        
        Returns:
            True if successful, False otherwise
        """
        if not self.index_path:
            logger.warning("No index path specified. Cannot save.")
            return False
        
        with self._lock:
            try:
                index_file = self.index_path / "faiss.index"
                docs_file = self.index_path / "documents.pkl"
                
                # Save FAISS index
                faiss.write_index(self.index, str(index_file))
                logger.info(f"FAISS index saved to {index_file}")
                
                # Save documents
                with open(docs_file, 'wb') as f:
                    pickle.dump(self.documents, f)
                logger.info(f"Documents saved to {docs_file}")
                
                return True
                
            except Exception as e:
                logger.error(f"Error saving index: {e}")
                return False
    
    def load(self) -> bool:
        """
        Load the FAISS index and documents from disk.
        
        Returns:
            True if loaded successfully, False if creating new index
        """
        if not self.index_path:
            logger.warning("No index path specified. Using new index.")
            return False
        
        with self._lock:
            try:
                index_file = self.index_path / "faiss.index"
                docs_file = self.index_path / "documents.pkl"
                
                # Check if index file exists and is valid
                if index_file.exists() and index_file.stat().st_size > 0:
                    try:
                        self.index = faiss.read_index(str(index_file))
                        logger.info(
                            f"Loaded FAISS index with {self.index.ntotal} vectors "
                            f"from {index_file}"
                        )
                    except RuntimeError as e:
                        logger.error(f"Corrupted index file: {e}. Creating new index.")
                        self.index = self._create_index()
                        return False
                else:
                    logger.info("No existing index found. Creating new index.")
                    self.index = self._create_index()
                    return False
                
                # Load documents if they exist
                if docs_file.exists() and docs_file.stat().st_size > 0:
                    with open(docs_file, 'rb') as f:
                        self.documents = pickle.load(f)
                    logger.info(f"Loaded {len(self.documents)} documents from {docs_file}")
                else:
                    logger.info("No existing documents found. Starting with empty list.")
                    self.documents = []
                    return False
                
                return True
                
            except Exception as e:
                logger.error(f"Error loading index: {e}. Creating new index.")
                self.index = self._create_index()
                self.documents = []
                return False
    
    def delete_document(self, doc_index: int) -> bool:
        """
        Delete a document by index (requires rebuilding the index).
        
        Args:
            doc_index: Index of the document to delete
            
        Returns:
            True if successful, False otherwise
        """
        with self._lock:
            try:
                if doc_index < 0 or doc_index >= len(self.documents):
                    logger.error(f"Invalid document index: {doc_index}")
                    return False
                
                # Remove document
                del self.documents[doc_index]
                
                # Rebuild index (FAISS doesn't support direct deletion)
                if len(self.documents) > 0:
                    self.index = self._create_index()
                    logger.warning("Index rebuilt after document deletion")
                else:
                    self.index = self._create_index()
                
                logger.info(f"Deleted document at index {doc_index}")
                return True
                
            except Exception as e:
                logger.error(f"Error deleting document: {e}")
                return False
    
    def get_stats(self) -> Dict[str, any]:
        """
        Get statistics about the vector store.
        
        Returns:
            Dictionary with statistics
        """
        return {
            "total_vectors": self.index.ntotal,
            "total_documents": len(self.documents),
            "dimension": self.dimension,
            "index_type": self.index_type,
            "index_path": str(self.index_path) if self.index_path else None
        }
    
    def clear(self) -> None:
        """Clear all documents and reset the index."""
        with self._lock:
            self.index = self._create_index()
            self.documents = []
            logger.info("Vector store cleared")
