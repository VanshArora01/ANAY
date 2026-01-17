"""
ANAY Voice Assistant - Standalone Mode
Automatically listens and responds via voice
"""
import asyncio
import time
import logging
from speech_to_text import SpeechToText
from gemini_llm import GeminiLLM
from tts.elevenlabs_stream import ElevenLabsStreamer
import os
from dotenv import load_dotenv
import pyaudio
import wave

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'  # Simple format for clean output
)
logger = logging.getLogger(__name__)

# Audio settings
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
RECORD_SECONDS = 5  # Record in 5-second chunks

class VoiceAssistant:
    def __init__(self):
        self.stt = SpeechToText()
        self.llm = GeminiLLM()
        self.tts = ElevenLabsStreamer(os.getenv('ELEVENLABS_API_KEY'))
        self.audio = pyaudio.PyAudio()
        
    def record_audio(self):
        """Record audio from microphone"""
        stream = self.audio.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK
        )
        
        logger.info("Listening...")
        frames = []
        
        for _ in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
            data = stream.read(CHUNK)
            frames.append(data)
        
        logger.info("Done listening")
        stream.stop_stream()
        stream.close()
        
        # Convert to bytes
        audio_data = b''.join(frames)
        return audio_data
    
    async def process_voice_input(self):
        """Main voice processing loop"""
        while True:
            try:
                # Record audio
                audio_data = self.record_audio()
                
                # Transcribe
                transcribe_start = time.time()
                transcript = self.stt.transcribe(audio_data)
                transcribe_time = time.time() - transcribe_start
                
                if not transcript or transcript.strip() == "":
                    continue
                    
                logger.info(f"Finished transcribing in {transcribe_time:.2f} seconds.")
                logger.info(f"You said: {transcript}")
                
                # Generate response
                response_start = time.time()
                ai_response = self.llm.generate_response(transcript)
                response_time = time.time() - response_start
                logger.info(f"Finished generating response in {response_time:.2f} seconds.")
                logger.info(f"ANAY: {ai_response}")
                
                # Generate and play audio
                audio_start = time.time()
                audio_chunks = []
                async for chunk in self.tts.stream_text(ai_response):
                    audio_chunks.append(chunk)
                audio_time = time.time() - audio_start
                logger.info(f"Finished generating audio in {audio_time:.2f} seconds.")
                
                # Play audio
                logger.info("Speaking...")
                self.play_audio(b''.join(audio_chunks))
                
            except KeyboardInterrupt:
                logger.info("\nShutting down...")
                break
            except Exception as e:
                logger.error(f"Error: {e}")
                continue
    
    def play_audio(self, audio_data):
        """Play audio through speakers"""
        stream = self.audio.open(
            format=FORMAT,
            channels=1,
            rate=24000,  # ElevenLabs default
            output=True
        )
        stream.write(audio_data)
        stream.stop_stream()
        stream.close()
    
    def cleanup(self):
        """Cleanup resources"""
        self.audio.terminate()

async def main():
    """Main entry point"""
    logger.info("=" * 50)
    logger.info("ANAY Voice Assistant - Standalone Mode")
    logger.info("=" * 50)
    logger.info("Press Ctrl+C to exit\n")
    
    assistant = VoiceAssistant()
    
    try:
        await assistant.process_voice_input()
    finally:
        assistant.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
