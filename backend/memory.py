"""
Memory Module
Maintains conversation context for the AI assistant
"""
import logging
from typing import List, Dict
from datetime import datetime

logger = logging.getLogger(__name__)

class ConversationMemory:
    """Stores and manages conversation history."""
    
    def __init__(self, max_messages: int = 10):
        """
        Initialize conversation memory.
        
        Args:
            max_messages: Maximum number of message pairs to remember
        """
        self.max_messages = max_messages
        self.history: List[Dict[str, str]] = []
        logger.info(f"Conversation memory initialized (max: {max_messages} messages)")
    
    def add_user_message(self, message: str):
        """
        Add user message to history.
        
        Args:
            message: User's message text
        """
        self.history.append({
            "role": "user",
            "content": message,
            "timestamp": datetime.now().isoformat()
        })
        self._trim_history()
        logger.debug(f"Added user message: {message[:50]}...")
    
    def add_assistant_message(self, message: str):
        """
        Add assistant response to history.
        
        Args:
            message: Assistant's response text
        """
        self.history.append({
            "role": "assistant",
            "content": message,
            "timestamp": datetime.now().isoformat()
        })
        self._trim_history()
        logger.debug(f"Added assistant message: {message[:50]}...")
    
    def _trim_history(self):
        """Keep only the most recent messages."""
        if len(self.history) > self.max_messages * 2:  # *2 for user+assistant pairs
            self.history = self.history[-(self.max_messages * 2):]
            logger.debug("Trimmed conversation history")
    
    def get_context(self) -> str:
        """
        Get formatted conversation history for LLM context.
        
        Returns:
            Formatted conversation history string
        """
        if not self.history:
            return ""
        
        context_parts = []
        for msg in self.history:
            role = "User" if msg["role"] == "user" else "Assistant"
            context_parts.append(f"{role}: {msg['content']}")
        
        return "\n".join(context_parts)
    
    def get_gemini_history(self) -> List[Dict[str, str]]:
        """
        Get history in Gemini API format.
        
        Returns:
            List of message dictionaries for Gemini
        """
        gemini_history = []
        for msg in self.history:
            role = "user" if msg["role"] == "user" else "model"
            gemini_history.append({
                "role": role,
                "parts": [msg["content"]]
            })
        return gemini_history
    
    def clear(self):
        """Clear all conversation history."""
        self.history.clear()
        logger.info("Conversation history cleared")
    
    def get_last_n_messages(self, n: int) -> List[Dict[str, str]]:
        """
        Get last N messages.
        
        Args:
            n: Number of messages to retrieve
            
        Returns:
            List of last N messages
        """
        return self.history[-n:] if self.history else []
    
    def __len__(self) -> int:
        """Return number of messages in history."""
        return len(self.history)
    
    def __str__(self) -> str:
        """String representation of memory."""
        return f"ConversationMemory({len(self)} messages)"


if __name__ == "__main__":
    # Test the memory
    logging.basicConfig(level=logging.DEBUG)
    
    memory = ConversationMemory(max_messages=3)
    
    memory.add_user_message("Hello, who are you?")
    memory.add_assistant_message("I am ANAY, your AI assistant.")
    memory.add_user_message("What can you do?")
    memory.add_assistant_message("I can help with tasks and conversations.")
    
    print("\nConversation Context:")
    print(memory.get_context())
    
    print("\nGemini History Format:")
    print(memory.get_gemini_history())
