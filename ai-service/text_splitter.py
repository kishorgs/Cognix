"""
Text Splitter Module
Handles chunking of text content using RecursiveCharacterTextSplitter
"""

from typing import List, Dict, Optional
from langchain_text_splitters import RecursiveCharacterTextSplitter
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DocumentChunker:
    """
    Splits documents into chunks while preserving context.
    Uses RecursiveCharacterTextSplitter from LangChain for intelligent splitting.
    """
    
    def __init__(
        self, 
        chunk_size: int = 1000, 
        chunk_overlap: int = 200,
        separators: Optional[List[str]] = None
    ):
        """
        Initialize the DocumentChunker.
        
        Args:
            chunk_size: Maximum size of each chunk in characters (default: 1000)
            chunk_overlap: Number of overlapping characters between chunks (default: 200)
            separators: List of separators to use for splitting (default: smart separators)
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        # Default separators for intelligent text splitting
        if separators is None:
            separators = ["\n\n", "\n", ". ", " ", ""]
        
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=separators,
            length_function=len,
            is_separator_regex=False
        )
        
        logger.info(
            f"DocumentChunker initialized with chunk_size={chunk_size}, "
            f"chunk_overlap={chunk_overlap}"
        )
    
    def chunk_text(
        self, 
        text: str, 
        metadata: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Split text into chunks with metadata.
        
        Args:
            text: The text content to chunk
            metadata: Optional metadata dictionary to attach to each chunk
            
        Returns:
            List of chunk dictionaries with content, metadata, and chunk_index
            
        Raises:
            ValueError: If text is empty
            TypeError: If text is not a string
        """
        try:
            # Validate input
            if not isinstance(text, str):
                raise TypeError(f"Expected str, got {type(text).__name__}")
            
            if not text.strip():
                logger.warning("Empty text provided for chunking")
                raise ValueError("Text content cannot be empty")
            
            # Clean text
            text = self._clean_text(text)
            
            # Split text into chunks
            chunks = self.splitter.split_text(text)
            
            if not chunks:
                logger.warning("No chunks generated from text")
                return []
            
            # Create chunk objects with metadata
            result = []
            for idx, chunk in enumerate(chunks):
                result.append({
                    "content": chunk,
                    "metadata": metadata or {},
                    "chunk_index": idx,
                    "chunk_size": len(chunk)
                })
            
            logger.info(
                f"Text chunked successfully: {len(result)} chunks "
                f"from {len(text)} characters"
            )
            
            return result
            
        except (ValueError, TypeError) as e:
            logger.error(f"Error chunking text: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during chunking: {e}")
            raise
    
    def chunk_multiple(
        self, 
        documents: List[Dict],
        text_field: str = "content",
        metadata_fields: Optional[List[str]] = None
    ) -> List[Dict]:
        """
        Chunk multiple documents at once.
        
        Args:
            documents: List of document dictionaries
            text_field: Key containing the text to chunk (default: 'content')
            metadata_fields: List of fields to preserve as metadata (default: all non-text fields)
            
        Returns:
            List of all chunks from all documents
        """
        all_chunks = []
        
        for doc_idx, doc in enumerate(documents):
            try:
                if text_field not in doc:
                    logger.warning(
                        f"Document {doc_idx} missing text field '{text_field}'"
                    )
                    continue
                
                text = doc[text_field]
                
                # Preserve metadata from original document
                metadata = {
                    "document_index": doc_idx,
                    **(metadata_fields and {k: v for k, v in doc.items() 
                       if k in metadata_fields} or {k: v for k, v in doc.items() 
                       if k != text_field})
                }
                
                chunks = self.chunk_text(text, metadata)
                all_chunks.extend(chunks)
                
            except Exception as e:
                logger.error(f"Error chunking document {doc_idx}: {e}")
                continue
        
        logger.info(f"Chunked {len(documents)} documents into {len(all_chunks)} total chunks")
        return all_chunks
    
    @staticmethod
    def _clean_text(text: str) -> str:
        """
        Clean text by removing excessive whitespace and normalizing content.
        
        Args:
            text: Text to clean
            
        Returns:
            Cleaned text
        """
        # Remove multiple consecutive newlines
        text = "\n".join([line.rstrip() for line in text.split("\n")])
        
        # Remove multiple consecutive spaces
        text = " ".join(text.split())
        
        return text.strip()
    
    def get_config(self) -> Dict:
        """Get current chunker configuration."""
        return {
            "chunk_size": self.chunk_size,
            "chunk_overlap": self.chunk_overlap
        }