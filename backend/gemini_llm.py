"""
Gemini LLM Module
Google Gemini API integration for AI responses
"""
import os
import logging
import google.generativeai as genai
from typing import Optional
from memory import ConversationMemory

logger = logging.getLogger(__name__)

class GeminiLLM:
    """Google Gemini AI Language Model client."""
    
    def __init__(
        self,
        api_key: str = None,
        model_name: str = "gemini-2.5-flash",  # Latest stable model
        memory: Optional[ConversationMemory] = None
    ):
        """
        Initialize Gemini client.
        
        Args:
            api_key: Gemini API key (defaults to env variable)
            model_name: Model to use
            memory: Optional conversation memory instance
        """
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment")
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(model_name)
        self.memory = memory or ConversationMemory()
        
        # System prompt (English, Intelligent, Helpful)
        self.system_prompt = """You are ANAY, an extremely intelligent and helpful AI assistant. 
        You communicate exclusively in English and are professional and friendly.
        Keep your responses concise and helpful (max 2-3 sentences)."""

        logger.info(f"Gemini client initialized ({model_name})")
    
    def generate_response(self, user_input: str) -> str:
        """
        Generate AI response to user input.
        
        Args:
            user_input: User's message/question
            
        Returns:
            AI-generated response
        """
        try:
            logger.info(f"Generating response for: {user_input[:50]}...")
            
            # Get conversation history
            history = self.memory.get_gemini_history()
            
            # Start chat with history
            chat = self.model.start_chat(history=history)
            
            # Prepare prompt with system context if first message
            if len(history) == 0:
                prompt = f"{self.system_prompt}\n\nUser: {user_input}"
            else:
                prompt = user_input
            
            # Generate response
            response = chat.send_message(prompt)
            ai_response = response.text.strip()
            
            # Update memory
            self.memory.add_user_message(user_input)
            self.memory.add_assistant_message(ai_response)
            
            logger.info(f"Response generated: {ai_response[:50]}...")
            return ai_response
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Gemini API error: {error_msg}")
            
            # Check for specific error types
            if "429" in error_msg or "quota" in error_msg.lower() or "RESOURCE_EXHAUSTED" in error_msg:
                logger.error("⚠️ QUOTA EXCEEDED - API rate limit reached")
                return "I'm currently experiencing high demand. My API quota has been exceeded. Please try again later or contact the administrator to upgrade the API plan."
            
            elif "API_KEY" in error_msg or "authentication" in error_msg.lower():
                logger.error("⚠️ AUTHENTICATION ERROR - Invalid API key")
                return "There's an authentication issue with my AI service. Please check the API configuration."
            
            else:
                # Generic fallback with helpful message
                logger.error(f"⚠️ Unknown error type: {type(e).__name__}")
                
                # Provide a basic response based on input
                user_lower = user_input.lower()
                
                if any(word in user_lower for word in ['hi', 'hello', 'hey']):
                    return "Hello! I'm ANAY, your AI assistant. I'm currently experiencing some technical difficulties with my AI service, but I'm here to help!"
                
                elif 'open' in user_lower:
                    return "I can help you open applications! However, my AI service is temporarily unavailable. The command has been noted for system execution."
                
                else:
                    return "I'm currently experiencing technical difficulties connecting to my AI service. Please try again in a moment."
    
    def clear_context(self):
        """Clear conversation history."""
        self.memory.clear()
        logger.info("Conversation context cleared")
    
    def get_memory_summary(self) -> str:
        """
        Get summary of current conversation context.
        
        Returns:
            Formatted memory summary
        """
        return f"Conversation: {len(self.memory)} messages\n{self.memory.get_context()}"


if __name__ == "__main__":
    # Test Gemini LLM
    logging.basicConfig(level=logging.INFO)
    
    llm = GeminiLLM()
    
    print("Testing Gemini LLM...")
    
    # Test conversation
    response1 = llm.generate_response("Hello! Who are you?")
    print(f"Response 1: {response1}\n")
    
    response2 = llm.generate_response("What can you help me with?")
    print(f"Response 2: {response2}\n")
    
    response3 = llm.generate_response("Tell me a joke in Hindi")
    print(f"Response 3: {response3}\n")
    
    print("\nMemory Summary:")
    print(llm.get_memory_summary())
