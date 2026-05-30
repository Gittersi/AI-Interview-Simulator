from typing import Optional
from app.config import settings
import logging

logger = logging.getLogger(__name__)

class SpeechService:
    """Service for speech-to-text transcription."""
    
    @staticmethod
    async def transcribe_audio(audio_file_path: str) -> str:
        """Transcribe audio file to text."""
        try:
            if settings.ASSEMBLYAI_API_KEY:
                return await SpeechService._transcribe_with_assemblyai(audio_file_path)
            else:
                logger.warning("No speech-to-text API configured")
                return ""
        except Exception as e:
            logger.error(f"Transcription error: {e}")
            return ""
    
    @staticmethod
    async def _transcribe_with_assemblyai(audio_url: str) -> str:
        """Transcribe using AssemblyAI API."""
        try:
            import aiohttp
            import asyncio
            
            headers = {"Authorization": settings.ASSEMBLYAI_API_KEY}
            
            async with aiohttp.ClientSession() as session:
                # Submit transcription job
                async with session.post(
                    "https://api.assemblyai.com/v2/transcript",
                    json={"audio_url": audio_url},
                    headers=headers
                ) as resp:
                    data = await resp.json()
                    transcript_id = data.get("id")
                
                # Poll for results
                while True:
                    async with session.get(
                        f"https://api.assemblyai.com/v2/transcript/{transcript_id}",
                        headers=headers
                    ) as resp:
                        result = await resp.json()
                        if result.get("status") == "completed":
                            return result.get("text", "")
                        elif result.get("status") == "error":
                            raise Exception(result.get("error"))
                        
                        await asyncio.sleep(1)
        except Exception as e:
            logger.error(f"AssemblyAI error: {e}")
            return ""
    
    @staticmethod
    async def _transcribe_with_google(audio_url: str) -> str:
        """Transcribe using Google Speech-to-Text."""
        try:
            # Placeholder for Google Cloud Speech-to-Text
            pass
        except Exception as e:
            logger.error(f"Google Speech error: {e}")
            return ""
