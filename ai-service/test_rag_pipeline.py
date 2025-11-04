"""
Example usage and testing of the RAG Pipeline implementation.
"""

import asyncio
import os
from dotenv import load_dotenv
from typing import List, Dict

# Import our services
from app.services.rag_pipeline import RAGPipeline
from app.services.llm_service import LLMService
from embedding_service import EmbeddingService
from vector_store_service import VectorStoreService

# Load environment variables
load_dotenv()

def prepare_test_documents():
    """Prepare some test documents for the vector store."""
    return [
        {
            "content": """
            Cognix is an AI-powered document processing and question-answering system.
            Key features include:
            - Advanced RAG pipeline for accurate responses
            - Support for multiple document formats (PDF, DOCX, TXT)
            - Real-time document processing and indexing
            - Conversational memory for context-aware responses
            """,
            "metadata": {
                "title": "Product Overview",
                "category": "Documentation"
            }
        },
        {
            "content": """
            API Integration Guide:
            1. Install the SDK: pip install cognix-sdk
            2. Initialize the client:
               from cognix import CognixClient
               client = CognixClient(api_key="your_key")
            3. Make API calls:
               response = client.process_document(file_path)
               answer = client.ask_question(question)
            """,
            "metadata": {
                "title": "API Documentation",
                "category": "Technical"
            }
        }
    ]

async def test_rag_pipeline():
    """Test the RAG pipeline with example queries."""
    
    # Initialize services
    print("Initializing services...")
    
    # Initialize vector store and add test documents
    vector_store = VectorStoreService(
        index_path="vector_store/test_faiss.index",
        documents_path="vector_store/test_documents.json"
    )
    
    # Initialize embedding service
    embedding_service = EmbeddingService(
        model_name="sentence-transformers/all-mpnet-base-v2"
    )
    
    # Add test documents to vector store
    test_docs = prepare_test_documents()
    for doc in test_docs:
        embedding = embedding_service.generate_embedding(doc["content"])
        vector_store.add_document(doc, embedding)
    
    # Initialize LLM service
    llm_service = LLMService(
        model="gpt-4-turbo",
        temperature=0.7,
        max_tokens=1000
    )
    
    # Initialize RAG pipeline
    rag = RAGPipeline(
        vector_store=vector_store,
        embedding_service=embedding_service,
        llm_service=llm_service
    )
    
    # Test queries that match our test documents
    test_queries = [
        "What are the main features of Cognix?",
        "How do I integrate the Cognix API?",
        "What document formats are supported?"
    ]
    
    # Example conversation history
    conversation_history: List[Dict] = [
        {
            "question": "What is Cognix?",
            "answer": "Cognix is an AI-powered document processing and question-answering system."
        }
    ]
    
    print("\nTesting RAG pipeline with example queries...")
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        try:
            # Generate response
            response = await rag.generate_response(
                query=query,
                conversation_history=conversation_history
            )
            
            # Print results
            print("\nAnswer:", response["answer"])
            print("\nSources:")
            for idx, source in enumerate(response["sources"], 1):
                print(f"{idx}. {source.get('title', 'Untitled')}")
                print(f"   Score: {source.get('score', 0):.2f}")
            print(f"\nConfidence Score: {response['confidence']:.2f}")
            
            # Add to conversation history
            conversation_history.append({
                "question": query,
                "answer": response["answer"]
            })
            
        except Exception as e:
            print(f"Error processing query: {e}")

async def main():
    """Main function to run the tests."""
    print("Starting RAG Pipeline tests...")
    await test_rag_pipeline()
    print("\nTests completed!")

if __name__ == "__main__":
    # Run the async test
    asyncio.run(main())