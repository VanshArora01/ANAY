"""
ElevenLabs Text-to-Speech Streaming Module
Real-time audio streaming via WebSocket API
"""
import os
import asyncio
import logging
import aiohttp
import json
from typing import AsyncGenerator

logger = logging.getLogger(__name__)


class ElevenLabsStreamer:
    """Handles real-time text-to-speech using ElevenLabs Streaming API."""
    
    def __init__(self, api_key: str, voice_id: str = None):
        """
        Initialize ElevenLabs streamer.
        
        Args:
            api_key: ElevenLabs API key
            voice_id: Voice ID to use (defaults to env or Rachel voice)
        """
        self.api_key = api_key
        self.voice_id = voice_id or os.getenv('ELEVENLABS_VOICE_ID', '21m00Tcm4TlvDq8ikWAM')
        self.model_id = "eleven_multilingual_v2"
        
        # REST API endpoint (more reliable than WebSocket for simple TTS)
        self.base_url = "https://api.elevenlabs.io/v1"
        
        logger.info(f"ElevenLabs Streamer initialized (Voice: {self.voice_id})")

    async def stream_text(self, text: str) -> AsyncGenerator[bytes, None]:
        """
        Stream text to speech and yield audio chunks.
        
        Args:
            text: Text to convert to speech
            
        Yields:
            Audio bytes chunks (MP3 format)
        """
        if not text or not text.strip():
            logger.warning("Empty text provided to TTS")
            return
            
        url = f"{self.base_url}/text-to-speech/{self.voice_id}/stream"
        
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self.api_key
        }
        
        data = {
            "text": text,
            "model_id": self.model_id,
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75
            }
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=data, headers=headers) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise Exception(f"ElevenLabs API error {response.status}: {error_text}")
                    
                    # Stream audio chunks
                    # Increased chunk size to 64KB to reduce choppiness in browser playback
                    chunk_size = 65536
                    async for chunk in response.content.iter_chunked(chunk_size):
                        if chunk:
                            yield chunk
                            
            logger.info(f"TTS streaming completed for: {text[:50]}...")
            
        except aiohttp.ClientError as e:
            logger.error(f"HTTP error during TTS: {e}")
        except Exception as e:
            logger.error(f"TTS streaming failed: {e}")

    async def synthesize_full(self, text: str) -> bytes:
        """
        Synthesize full audio for text (non-streaming).
        
        Args:
            text: Text to convert to speech
            
        Returns:
            Complete audio bytes (MP3 format)
        """
        chunks = []
        async for chunk in self.stream_text(text):
            chunks.append(chunk)
        return b''.join(chunks)
