from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
from embedding_service import EmbeddingService
from vector_store_service import VectorStoreService
from document_processor import DocumentProcessor
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Load the vector store
    try:
        vector_store.load()
        print("Vector store loaded/initialized successfully")
        yield
    finally:
        # Shutdown: Save the vector store
        try:
            vector_store.save()
            print("Vector store saved successfully")
        except Exception as e:
            print(f"Error during shutdown: {e}")

# Initialize FastAPI app
app = FastAPI(
    title="Document Processing API",
    description="API for processing documents and generating embeddings",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    max_age=3600
)

# Initialize services
embedding_service = EmbeddingService()
vector_store = VectorStoreService(
    dimension=384,
    index_path="vector_store"
)
document_processor = DocumentProcessor(
    chunk_size=1000,
    chunk_overlap=200,
    min_chunk_size=50
)

# Pydantic models
class DocumentRequest(BaseModel):
    text: str
    metadata: Optional[Dict[str, str]] = None
    file_name: Optional[str] = None
    file_type: Optional[str] = None

class BatchDocumentRequest(BaseModel):
    documents: List[DocumentRequest]

class ChunkInfo(BaseModel):
    content: str
    chunk_index: int
    chunk_size: int
    metadata: Dict[str, str]

class ProcessingStats(BaseModel):
    total_documents: int
    processed_successfully: int
    failed_documents: int
    total_chunks: int
    errors: List[str]

class ProcessDocumentResponse(BaseModel):
    success: bool
    message: str
    chunks_count: Optional[int] = None
    chunks: Optional[List[ChunkInfo]] = None

class BatchProcessingResponse(BaseModel):
    success: bool
    message: str
    total_chunks: int
    stats: ProcessingStats

class SearchRequest(BaseModel):
    query: str
    top_k: Optional[int] = 5

class SearchResult(BaseModel):
    text: str
    metadata: Dict[str, str]
    similarity: float

class SearchResponse(BaseModel):
    results: List[SearchResult]

@app.post("/api/process-document", response_model=ProcessDocumentResponse)
async def process_document(request: DocumentRequest):
    """
    Process a single document: chunk it and add to vector store.
    """
    try:
        # Process the document (chunk + preprocess)
        result = document_processor.process_document(
            text=request.text,
            metadata=request.metadata,
            file_name=request.file_name,
            file_type=request.file_type
        )
        
        if not result["success"]:
            return ProcessDocumentResponse(
                success=False,
                message=result.get("error", "Failed to process document"),
                chunks_count=0,
                chunks=[]
            )
        
        # Generate embeddings for each chunk and add to vector store
        chunks = result["chunks"]
        chunk_texts = [chunk["content"] for chunk in chunks]
        
        embeddings = embedding_service.generate_embeddings(chunk_texts)
        
        # Create document objects with chunk information
        documents_to_store = []
        for chunk, embedding in zip(chunks, embeddings):
            documents_to_store.append({
                'text': chunk['content'],
                'chunk_index': chunk['chunk_index'],
                'chunk_size': chunk['chunk_size'],
                'metadata': chunk['metadata']
            })
        
        # Add to vector store
        vector_store.add_documents(embeddings, documents_to_store)
        vector_store.save()
        
        # Prepare response with chunk information
        chunk_info_list = [
            ChunkInfo(
                content=chunk['content'],
                chunk_index=chunk['chunk_index'],
                chunk_size=chunk['chunk_size'],
                metadata=chunk['metadata']
            )
            for chunk in chunks
        ]
        
        return ProcessDocumentResponse(
            success=True,
            message=f"Document processed successfully into {len(chunks)} chunks",
            chunks_count=len(chunks),
            chunks=chunk_info_list
        )
    
    except Exception as e:
        print(f"Error processing document: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/process-batch", response_model=BatchProcessingResponse)
async def process_batch(request: BatchDocumentRequest):
    """
    Process multiple documents in batch: chunk and add to vector store.
    """
    try:
        # Convert DocumentRequest objects to dictionaries
        documents = [
            {
                "text": doc.text,
                "metadata": doc.metadata or {},
                "file_name": doc.file_name,
                "file_type": doc.file_type
            }
            for doc in request.documents
        ]
        
        # Process batch
        result = document_processor.process_batch(documents, text_field="text")
        
        if result["chunks"]:
            # Generate embeddings and add to vector store
            chunk_texts = [chunk["content"] for chunk in result["chunks"]]
            embeddings = embedding_service.generate_embeddings(chunk_texts)
            
            documents_to_store = [
                {
                    'text': chunk['content'],
                    'chunk_index': chunk['chunk_index'],
                    'chunk_size': chunk['chunk_size'],
                    'metadata': chunk['metadata']
                }
                for chunk in result["chunks"]
            ]
            
            vector_store.add_documents(embeddings, documents_to_store)
            vector_store.save()
        
        stats_obj = ProcessingStats(**result["stats"])
        
        return BatchProcessingResponse(
            success=True,
            message=f"Batch processing completed. {result['stats']['total_chunks']} chunks created.",
            total_chunks=result["stats"]["total_chunks"],
            stats=stats_obj
        )
    
    except Exception as e:
        print(f"Error in batch processing: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/processor-stats")
async def get_processor_stats():
    """
    Get document processor configuration and statistics.
    """
    try:
        stats = document_processor.get_statistics()
        vector_store_stats = vector_store.get_stats()
        
        return {
            "processor_config": stats,
            "vector_store_stats": vector_store_stats
        }
    
    except Exception as e:
        print(f"Error getting processor stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/search", response_model=SearchResponse)
async def search_documents(request: SearchRequest):
    try:
        query_embedding = embedding_service.generate_query_embedding(request.query)
        results = vector_store.search(query_embedding, top_k=request.top_k)
        
        formatted_results = [
            SearchResult(
                text=doc['text'],
                metadata=doc['metadata'],
                similarity=float(score)
            )
            for doc, score in results
        ]
        
        return SearchResponse(results=formatted_results)
    
    except Exception as e:
        print(f"Error searching documents: {e}")  # Add logging
        raise HTTPException(status_code=500, detail=str(e))

# REMOVE the @app.on_event("startup") - it conflicts with lifespan

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=5000,
        reload=True,
        log_level="info"
    )
