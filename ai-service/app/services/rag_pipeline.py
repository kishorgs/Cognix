"""
RAG Pipeline implementation for document question-answering.
Combines document retrieval with language model generation.
"""

from typing import Dict, List, Optional
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

class RAGPipeline:
    def __init__(self, vector_store, embedding_service, llm_service):
        """Initialize the RAG Pipeline with required services.
        
        Args:
            vector_store: Vector store service for document retrieval
            embedding_service: Service for generating embeddings
            llm_service: Language model service for text generation
        """
        self.vector_store = vector_store
        self.embedding_service = embedding_service
        self.llm_service = llm_service
        
        self.prompt_template = """
        You are a helpful AI assistant specialized in providing accurate information from the given context.
        Use the following context to answer the question. If you cannot find the answer in the context,
        clearly state that you cannot answer based on the available information.
        
        Context:
        {context}
        
        Question: {question}
        
        Previous conversation:
        {conversation_history}
        
        Answer:
        """
    
    def _calculate_confidence(self, docs: List[Dict]) -> float:
        """Calculate confidence score based on retrieved documents.
        
        Args:
            docs: List of retrieved documents with similarity scores
            
        Returns:
            float: Confidence score between 0 and 1
        """
        if not docs:
            return 0.0
        
        # Average similarity scores of top documents
        scores = [doc[1] for doc in docs]
        return sum(scores) / len(scores)
    
    def _format_conversation_history(self, history: List[Dict]) -> str:
        """Format conversation history for context.
        
        Args:
            history: List of conversation turns with questions and answers
            
        Returns:
            str: Formatted conversation history
        """
        if not history:
            return ""
            
        formatted = []
        for turn in history:
            formatted.append(f"User: {turn['question']}")
            formatted.append(f"Assistant: {turn['answer']}\n")
        return "\n".join(formatted)
    
    async def generate_response(
        self, 
        query: str, 
        conversation_history: Optional[List[Dict]] = None
    ) -> Dict:
        """Generate a response using the RAG pipeline.
        
        Args:
            query: User's question
            conversation_history: Optional list of previous QA turns
            
        Returns:
            Dict containing answer, sources, and confidence score
        """
        # 1. Generate query embedding
        query_embedding = self.embedding_service.generate_query_embedding(query)
        
        # 2. Retrieve relevant documents
        relevant_docs = self.vector_store.search(query_embedding, top_k=5)
        
        # 3. Prepare context
        context = "\n\n".join([doc[0]['content'] for doc in relevant_docs])
        
        # 4. Format conversation history
        formatted_history = self._format_conversation_history(conversation_history)
        
        # 5. Generate response using LLM
        prompt = PromptTemplate(
            template=self.prompt_template,
            input_variables=["context", "question", "conversation_history"]
        )
        
        response = await self.llm_service.generate(
            query=query,
            context=context,
            conversation_history=formatted_history
        )
        
        # 6. Return response with metadata
        return {
            "answer": response,
            "sources": [doc[0] for doc in relevant_docs],
            "confidence": self._calculate_confidence(relevant_docs)
        }