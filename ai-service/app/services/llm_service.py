"""
Language Model service for text generation using OpenAI's GPT models.
"""

from typing import Optional, Dict, List
import os
from openai import AsyncOpenAI

class LLMService:
    def __init__(
        self,
        model: str = "gpt-4-turbo",
        temperature: float = 0.7,
        max_tokens: int = 1000
    ):
        """Initialize LLM service with OpenAI client.
        
        Args:
            model: OpenAI model identifier
            temperature: Control randomness (0-1)
            max_tokens: Maximum tokens in response
        """
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        self.system_prompt = """
        You are a helpful AI assistant that provides accurate and relevant information
        based on the given context. Always strive to:
        1. Answer directly from the provided context
        2. Acknowledge when information is not available in the context
        3. Maintain a professional and helpful tone
        4. Cite specific sources when possible
        """
    
    async def generate(
        self,
        query: str,
        context: str,
        conversation_history: Optional[str] = None
    ) -> str:
        """Generate response using the language model.
        
        Args:
            query: User's question
            context: Retrieved document context
            conversation_history: Optional formatted conversation history
            
        Returns:
            str: Generated response
        """
        messages = [
            {"role": "system", "content": self.system_prompt}
        ]
        
        # Add conversation history if available
        if conversation_history:
            messages.append({
                "role": "system",
                "content": f"Previous conversation:\n{conversation_history}"
            })
        
        # Add context and query
        messages.extend([
            {
                "role": "system",
                "content": f"Context:\n{context}"
            },
            {
                "role": "user",
                "content": query
            }
        ])
        
        # Generate response
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
            max_tokens=self.max_tokens
        )
        
        return response.choices[0].message.content
    
    async def batch_generate(
        self,
        queries: List[str],
        contexts: List[str],
        conversation_histories: Optional[List[str]] = None
    ) -> List[str]:
        """Generate responses for multiple queries in batch.
        
        Args:
            queries: List of user questions
            contexts: List of retrieved contexts
            conversation_histories: Optional list of conversation histories
            
        Returns:
            List[str]: Generated responses
        """
        if conversation_histories is None:
            conversation_histories = [None] * len(queries)
            
        responses = []
        for query, context, history in zip(
            queries, contexts, conversation_histories
        ):
            response = await self.generate(
                query=query,
                context=context,
                conversation_history=history
            )
            responses.append(response)
            
        return responses