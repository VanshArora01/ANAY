"""
Groq LLM Module
Super fast AI responses using Groq API
"""
import os
import logging
from groq import Groq
from typing import Optional
from memory import ConversationMemory

logger = logging.getLogger(__name__)

class GroqLLM:
    """Groq AI Language Model client (Ultra Fast)."""
    
    def __init__(
        self,
        api_key: str = None,
        model_name: str = "llama-3.3-70b-versatile",  # Latest stable flagship model
        memory: Optional[ConversationMemory] = None
    ):
        """Initialize Groq client."""
        self.api_key = api_key or os.getenv('GROQ_API_KEY')
        if not self.api_key:
            logger.warning("GROQ_API_KEY not found in environment, falling back to dummy/error mode")
        
        self.client = Groq(api_key=self.api_key) if self.api_key else None
        self.model_name = model_name
        self.memory = memory or ConversationMemory()
        
        # System prompt (English, Intelligent, Helpful)
        self.system_prompt = """You are ANAY, an extremely intelligent and helpful AI assistant. 
        You communicate exclusively in English. 
        Keep your responses concise and helpful (max 2-3 sentences). 
        """

        logger.info(f"Groq LLM initialized ({model_name})")
    
    def generate_response(self, user_input: str, system_prompt: str = None) -> str:
        """Generate AI response to user input."""
        if not self.client:
            return "I apologize, but the Groq API key is missing. I've switched to Gemini for now. How can I help you?"

        try:
            # Get conversation history
            # history = self.memory.get_context() 
            
            # Use provided system_prompt (for Planning) or default (for Chat)
            effective_system = system_prompt if system_prompt else self.system_prompt
            
            # Simple approach: Build messages for Groq
            messages = [{"role": "system", "content": effective_system}]
            
            # Add context from memory ONLY if it's a chat (no custom system prompt)
            # If we are planning, we don't want the chat history confusing the JSON output
            if not system_prompt:
                for msg in self.memory.history[-5:]: # Last 5 messages for speed/context
                    role = "user" if msg["role"] == "user" else "assistant"
                    messages.append({"role": role, "content": msg["content"]})
            
            messages.append({"role": "user", "content": user_input})
            
            # Generate response
            chat_completion = self.client.chat.completions.create(
                messages=messages,
                model=self.model_name,
                max_tokens=1024 if system_prompt else 100, # More tokens for planning
                temperature=0.1 if system_prompt else 0.8, # Lower temp for planning
            )
            
            ai_response = chat_completion.choices[0].message.content.strip()
            
            # Update memory only for normal chat
            if not system_prompt:
                self.memory.add_user_message(user_input)
                self.memory.add_assistant_message(ai_response)
            
            return ai_response
            
        except Exception as e:
            logger.error(f"Groq API error: {e}")
            return f"I'm sorry, I'm having some trouble processing that right now. Error: {str(e)}"

    def clear_context(self):
        """Clear conversation history."""
        self.memory.clear()
        logger.info("Conversation context cleared")
