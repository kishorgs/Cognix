"""
Document Processor Module
Handles preprocessing and preparation of already-parsed document content
"""

from typing import List, Dict, Optional, Tuple
from text_splitter import DocumentChunker
import logging
import re
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DocumentProcessor:
    """
    Processes and preprocesses already-uploaded/parsed documents.
    Handles text extraction, cleaning, chunking, and metadata enrichment.
    """
    
    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        min_chunk_size: int = 50
    ):
        """
        Initialize the DocumentProcessor.
        
        Args:
            chunk_size: Size of text chunks (default: 1000)
            chunk_overlap: Overlap between chunks (default: 200)
            min_chunk_size: Minimum characters for a valid chunk (default: 50)
        """
        self.chunker = DocumentChunker(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        self.min_chunk_size = min_chunk_size
        
        logger.info(
            f"DocumentProcessor initialized with chunk_size={chunk_size}, "
            f"min_chunk_size={min_chunk_size}"
        )
    
    def process_document(
        self,
        text: str,
        metadata: Optional[Dict] = None,
        file_name: Optional[str] = None,
        file_type: Optional[str] = None
    ) -> Dict:
        """
        Process a single document: clean, chunk, and enrich with metadata.
        
        Args:
            text: The document text content
            metadata: Optional metadata dictionary
            file_name: Optional name of the source file
            file_type: Optional type/format of the source file
            
        Returns:
            Dictionary containing processed chunks and metadata
        """
        try:
            # Build metadata
            doc_metadata = metadata or {}
            if file_name:
                doc_metadata["file_name"] = file_name
            if file_type:
                doc_metadata["file_type"] = file_type
            
            # Preprocess text
            cleaned_text = self._preprocess_text(text)
            
            if not cleaned_text:
                logger.warning("Document resulted in empty text after preprocessing")
                return {
                    "success": False,
                    "error": "Document text is empty after preprocessing",
                    "chunks": []
                }
            
            # Chunk the text
            chunks = self.chunker.chunk_text(cleaned_text, doc_metadata)
            
            # Filter out small chunks
            filtered_chunks = [
                chunk for chunk in chunks 
                if chunk["chunk_size"] >= self.min_chunk_size
            ]
            
            if not filtered_chunks:
                logger.warning("No chunks passed minimum size filter")
                return {
                    "success": False,
                    "error": f"No chunks met minimum size requirement ({self.min_chunk_size} chars)",
                    "chunks": []
                }
            
            return {
                "success": True,
                "original_length": len(text),
                "cleaned_length": len(cleaned_text),
                "chunk_count": len(filtered_chunks),
                "chunks": filtered_chunks,
                "metadata": doc_metadata
            }
            
        except Exception as e:
            logger.error(f"Error processing document: {e}")
            return {
                "success": False,
                "error": str(e),
                "chunks": []
            }
    
    def process_batch(
        self,
        documents: List[Dict],
        text_field: str = "text",
        metadata_field: str = "metadata"
    ) -> Dict:
        """
        Process multiple documents in batch.
        
        Args:
            documents: List of document dictionaries
            text_field: Key containing the text content (default: 'text')
            metadata_field: Key containing metadata (default: 'metadata')
            
        Returns:
            Dictionary containing all processed chunks and processing stats
        """
        all_chunks = []
        processing_stats = {
            "total_documents": len(documents),
            "processed_successfully": 0,
            "failed_documents": 0,
            "total_chunks": 0,
            "errors": []
        }
        
        for doc_idx, doc in enumerate(documents):
            try:
                if text_field not in doc:
                    error_msg = f"Document {doc_idx}: missing field '{text_field}'"
                    logger.error(error_msg)
                    processing_stats["errors"].append(error_msg)
                    processing_stats["failed_documents"] += 1
                    continue
                
                text = doc[text_field]
                metadata = doc.get(metadata_field, {})
                
                result = self.process_document(text, metadata)
                
                if result["success"]:
                    all_chunks.extend(result["chunks"])
                    processing_stats["processed_successfully"] += 1
                    processing_stats["total_chunks"] += len(result["chunks"])
                else:
                    processing_stats["failed_documents"] += 1
                    processing_stats["errors"].append(
                        f"Document {doc_idx}: {result.get('error', 'Unknown error')}"
                    )
                    
            except Exception as e:
                error_msg = f"Document {doc_idx}: {str(e)}"
                logger.error(error_msg)
                processing_stats["errors"].append(error_msg)
                processing_stats["failed_documents"] += 1
        
        logger.info(
            f"Batch processing complete: {processing_stats['processed_successfully']} "
            f"successful, {processing_stats['failed_documents']} failed, "
            f"{processing_stats['total_chunks']} total chunks"
        )
        
        return {
            "chunks": all_chunks,
            "stats": processing_stats
        }
    
    def _preprocess_text(self, text: str) -> str:
        """
        Preprocess text: clean, normalize, and remove noise.
        
        Args:
            text: Raw text to preprocess
            
        Returns:
            Cleaned and normalized text
        """
        if not text:
            return ""
        
        # Decode if bytes
        if isinstance(text, bytes):
            text = text.decode('utf-8', errors='replace')
        
        # Remove null characters
        text = text.replace('\x00', '')
        
        # Normalize unicode
        text = self._normalize_unicode(text)
        
        # Remove excessive whitespace
        lines = []
        for line in text.split('\n'):
            line = line.rstrip()
            if line.strip():
                lines.append(line)
        
        text = '\n'.join(lines)
        
        # Remove multiple consecutive newlines
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # Remove multiple consecutive spaces
        text = re.sub(r'[ \t]{2,}', ' ', text)
        
        # Clean special characters while preserving readability
        text = self._clean_special_chars(text)
        
        return text.strip()
    
    @staticmethod
    def _normalize_unicode(text: str) -> str:
        """Normalize unicode characters."""
        # Replace common unicode variations
        replacements = {
            '\u2018': "'",  # Left single quote
            '\u2019': "'",  # Right single quote
            '\u201c': '"',  # Left double quote
            '\u201d': '"',  # Right double quote
            '\u2013': '-',  # En dash
            '\u2014': '--', # Em dash
            '\u2022': '*',  # Bullet point
        }
        
        for old, new in replacements.items():
            text = text.replace(old, new)
        
        return text
    
    @staticmethod
    def _clean_special_chars(text: str) -> str:
        """Clean problematic special characters."""
        # Remove form feeds
        text = text.replace('\f', '\n')
        
        # Remove excessive punctuation
        text = re.sub(r'([!?.]){3,}', r'\1\1', text)
        
        # Fix broken words (words with random spaces/dashes)
        text = re.sub(r'(\w)\s{2,}(\w)', r'\1 \2', text)
        
        return text
    
    def extract_metadata(
        self,
        text: str,
        file_path: Optional[str] = None
    ) -> Dict:
        """
        Extract useful metadata from document text and file info.
        
        Args:
            text: Document text
            file_path: Optional path to the source file
            
        Returns:
            Dictionary of extracted metadata
        """
        metadata = {}
        
        # Extract from file path
        if file_path:
            path = Path(file_path)
            metadata["file_name"] = path.name
            metadata["file_type"] = path.suffix.lstrip('.')
            metadata["file_size_kb"] = path.stat().st_size / 1024 if path.exists() else None
        
        # Extract from text
        metadata["text_length"] = len(text)
        metadata["word_count"] = len(text.split())
        metadata["paragraph_count"] = len([p for p in text.split('\n\n') if p.strip()])
        metadata["line_count"] = len(text.split('\n'))
        
        # Estimate reading time (avg 200 words per minute)
        metadata["estimated_reading_time_minutes"] = max(
            1, 
            metadata["word_count"] // 200
        )
        
        # Detect language (basic - just check for common patterns)
        metadata["likely_language"] = self._detect_language(text)
        
        return metadata
    
    @staticmethod
    def _detect_language(text: str) -> str:
        """Simple language detection based on character patterns."""
        # This is a simplified version - for production, use langdetect or similar
        if not text:
            return "unknown"
        
        # Count character types
        cyrillic_chars = len([c for c in text if '\u0400' <= c <= '\u04ff'])
        chinese_chars = len([c for c in text if '\u4e00' <= c <= '\u9fff'])
        
        if cyrillic_chars > len(text) * 0.1:
            return "cyrillic"
        elif chinese_chars > len(text) * 0.1:
            return "chinese"
        else:
            return "english"
    
    def get_statistics(self) -> Dict:
        """Get processor configuration and statistics."""
        return {
            "chunk_size": self.chunker.chunk_size,
            "chunk_overlap": self.chunker.chunk_overlap,
            "min_chunk_size": self.min_chunk_size
        }