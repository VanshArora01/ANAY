"""
Text-to-Speech Module
Converts text to speech using ElevenLabs API
"""
import os
import logging
import requests
from pathlib import Path

logger = logging.getLogger(__name__)

class TextToSpeech:
    """Converts text to speech audio using ElevenLabs API."""
    
    def __init__(
        self,
        api_key: str = None,
        voice_id: str = None
    ):
        """
        Initialize ElevenLabs TTS client.
        
        Args:
            api_key: ElevenLabs API key (defaults to config)
            voice_id: Voice ID to use (defaults to a high-quality voice)
        """
        from config import ELEVENLABS_API_KEY
        self.api_key = api_key or ELEVENLABS_API_KEY
        if not self.api_key:
            raise ValueError("ELEVENLABS_API_KEY not found. Please set it in api.txt or environment.")
        
        # Use a high-quality, natural-sounding voice
        # Default: Rachel (21m00Tcm4TlvDq8ikWAM) - professional, clear female voice
        # Alternative: Adam (pNInz6obpgDQGcFmaJgB) - deep male voice
        # Alternative: Antoni (ErXwobaYiN019PkySvjV) - warm male voice
        self.voice_id = voice_id or os.getenv('ELEVENLABS_VOICE_ID', '21m00Tcm4TlvDq8ikWAM')
        self.base_url = "https://api.elevenlabs.io/v1"
        
        logger.info(f"ElevenLabs TTS initialized (Voice ID: {self.voice_id})")
    
    def synthesize(
        self,
        text: str,
        output_path: str,
        stability: float = 0.5,
        similarity_boost: float = 0.75,
        style: float = 0.0,
        use_speaker_boost: bool = True
    ) -> str:
        """
        Convert text to speech and save as audio file.
        
        Args:
            text: Text to convert to speech
            output_path: Path to save audio file (MP3)
            stability: Voice stability (0.0-1.0)
            similarity_boost: Voice similarity boost (0.0-1.0)
            
        Returns:
            Path to saved audio file
        """
        try:
            logger.info(f"Synthesizing speech: {text[:50]}...")
            
            # Prepare API request
            url = f"{self.base_url}/text-to-speech/{self.voice_id}"
            
            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": self.api_key
            }
            
            data = {
                "text": text,
                "model_id": "eleven_multilingual_v2",
                "voice_settings": {
                    "stability": stability,
                    "similarity_boost": similarity_boost,
                    "style": style,
                    "use_speaker_boost": use_speaker_boost
                }
            }
            
            # Make API request
            response = requests.post(url, json=data, headers=headers)
            response.raise_for_status()
            
            # Save audio file
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'wb') as f:
                f.write(response.content)
            
            logger.info(f"Audio saved to {output_path}")
            return str(output_path)
            
        except requests.exceptions.RequestException as e:
            logger.error(f"ElevenLabs API error: {e}")
            raise
        except Exception as e:
            logger.error(f"TTS synthesis failed: {e}")
            raise
    
    def get_available_voices(self) -> list:
        """
        Get list of available voices from ElevenLabs.
        
        Returns:
            List of voice dictionaries
        """
        try:
            url = f"{self.base_url}/voices"
            headers = {"xi-api-key": self.api_key}
            
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            voices = response.json().get('voices', [])
            logger.info(f"Retrieved {len(voices)} available voices")
            return voices
            
        except Exception as e:
            logger.error(f"Failed to get voices: {e}")
            return []


if __name__ == "__main__":
    # Test TTS
    logging.basicConfig(level=logging.INFO)
    
    tts = TextToSpeech()
    
    test_text = "नमस्ते! मैं ANAY हूं, आपका AI सहायक।"
    output_file = "test_tts_output.mp3"
    
    print(f"Synthesizing: {test_text}")
    audio_path = tts.synthesize(test_text, output_file)
    print(f"Audio saved to: {audio_path}")
