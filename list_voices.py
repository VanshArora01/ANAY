import asyncio
import aiohttp
from dotenv import load_dotenv

async def list_voices():
    load_dotenv(os.path.join('backend', '.env'))
    api_key = os.getenv('ELEVENLABS_API_KEY')
    
    url = "https://api.elevenlabs.io/v1/voices"
    headers = {"xi-api-key": api_key}
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                for voice in data.get('voices', []):
                    labels = voice.get('labels', {})
                    if 'hindi' in str(voice).lower() or 'indian' in str(voice).lower():
                         print(f"ID: {voice['voice_id']} | Name: {voice['name']} | Labels: {labels}")
            else:
                print(f"❌ Failed! Status: {response.status}")

if __name__ == "__main__":
    asyncio.run(list_voices())
