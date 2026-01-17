import os
import asyncio
import json
import aiohttp
from dotenv import load_dotenv

async def test_elevenlabs():
    load_dotenv(os.path.join('backend', '.env'))
    api_key = os.getenv('ELEVENLABS_API_KEY')
    voice_id = os.getenv('ELEVENLABS_VOICE_ID', '7b9mYhmnp0y2qSH1FnBL')
    
    if not api_key:
        print("❌ ELEVENLABS_API_KEY not found in .env")
        return

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {
        "xi-api-key": api_key,
        "Content-Type": "application/json"
    }
    data = {"text": "Hello", "model_id": "eleven_multilingual_v2"}
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=data, headers=headers) as response:
            if response.status == 200:
                print("✅ Success! TTS generation works.")
            else:
                print(f"❌ TTS Failed! Status: {response.status}")
                print(await response.text())

if __name__ == "__main__":
    asyncio.run(test_elevenlabs())
