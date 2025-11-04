from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
from embedding_service import EmbeddingService
from vector_store_service import VectorStoreService
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

# Pydantic models
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
        embedding = embedding_service.generate_embeddings([request.text])
        document = {
            'text': request.text,
            'metadata': request.metadata
        }
        vector_store.add_documents(embedding, [document])
        vector_store.save()
        
        return {"success": True, "message": "Document processed successfully"}
    
    except Exception as e:
        print(f"Error processing document: {e}")  # Add logging
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
