from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
from embedding_service import EmbeddingService
from vector_store_service import VectorStoreService
import numpy as np

import signal
import sys
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Load the vector store
    try:
        vector_store.load()
        yield
    finally:
        # Shutdown: Save the vector store and clean up
        try:
            vector_store.save()
        except Exception as e:
            print(f"Error during shutdown: {e}")

# Initialize FastAPI app with lifespan handler
app = FastAPI(
    title="Document Processing API",
    description="API for processing documents and generating embeddings",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=False,  # Must be False for allow_origins=["*"]
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "Accept"],
    max_age=3600  # Cache preflight requests for 1 hour
)

# Initialize services
embedding_service = EmbeddingService()
vector_store = VectorStoreService(
    dimension=384,  # default dimension for all-MiniLM-L6-v2
    index_path="vector_store"
)

# Load existing index if available
vector_store.load()

# Pydantic models for request/response validation
class DocumentRequest(BaseModel):
    text: str
    metadata: Dict[str, str]

class SearchRequest(BaseModel):
    query: str
    top_k: Optional[int] = 5

class SearchResult(BaseModel):
    text: str
    metadata: Dict[str, str]
    similarity: float

class SearchResponse(BaseModel):
    results: List[SearchResult]

@app.post("/api/process-document", status_code=200)
async def process_document(request: DocumentRequest):
    try:
        # Generate embedding
        embedding = embedding_service.generate_embeddings([request.text])
        
        # Create document object
        document = {
            'text': request.text,
            'metadata': request.metadata
        }
        
        # Add to vector store
        vector_store.add_documents(embedding, [document])
        
        # Save the updated index
        vector_store.save()
        
        return {"success": True, "message": "Document processed successfully"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/search", response_model=SearchResponse)
async def search_documents(request: SearchRequest):
    try:
        # Generate query embedding
        query_embedding = embedding_service.generate_query_embedding(request.query)
        
        # Search for similar documents
        results = vector_store.search(query_embedding, top_k=request.top_k)
        
        # Format results
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
        raise HTTPException(status_code=500, detail=str(e))

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    vector_store.load()

def handle_shutdown(signum, frame):
    print("\nShutting down gracefully...")
    try:
        vector_store.save()
        print("Vector store saved successfully")
    except Exception as e:
        print(f"Error saving vector store: {e}")
    sys.exit(0)

if __name__ == "__main__":
    # Register shutdown handlers
    signal.signal(signal.SIGINT, handle_shutdown)
    signal.signal(signal.SIGTERM, handle_shutdown)

    import uvicorn
    config = uvicorn.Config(
        "app:app",
        host="0.0.0.0",
        port=5000,
        reload=True,
        log_level="info",
        workers=1
    )
    server = uvicorn.Server(config)
    server.run()