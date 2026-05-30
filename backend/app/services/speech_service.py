from typing import Optional
from app.config import settings
import logging

logger = logging.getLogger(__name__)

class SpeechService:
    """Service for speech-to-text transcription."""

    @staticmethod
    async def transcribe_audio_bytes(audio_bytes: bytes) -> str:
        """Upload raw audio bytes to AssemblyAI and return the transcript text."""
        if not settings.ASSEMBLYAI_API_KEY:
            logger.warning("No AssemblyAI API key configured")
            return ""

        try:
            upload_url = await SpeechService._upload_to_assemblyai(audio_bytes)
            return await SpeechService._transcribe_with_assemblyai(upload_url)
        except Exception as e:
            logger.error(f"Transcription error: {e}")
            return ""
    
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
            import asyncio
            import httpx
            
            headers = {"Authorization": settings.ASSEMBLYAI_API_KEY}
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    "https://api.assemblyai.com/v2/transcript",
                    json={"audio_url": audio_url},
                    headers=headers,
                )
                response.raise_for_status()
                transcript_id = response.json().get("id")

                if not transcript_id:
                    raise ValueError("AssemblyAI did not return a transcript id")
                
                while True:
                    result_response = await client.get(
                        f"https://api.assemblyai.com/v2/transcript/{transcript_id}",
                        headers=headers,
                    )
                    result_response.raise_for_status()
                    result = result_response.json()

                    if result.get("status") == "completed":
                        return result.get("text", "")
                    if result.get("status") == "error":
                        raise Exception(result.get("error"))

                    await asyncio.sleep(1)
        except Exception as e:
            logger.error(f"AssemblyAI error: {e}")
            return ""

    @staticmethod
    async def _upload_to_assemblyai(audio_bytes: bytes) -> str:
        """Upload audio bytes to AssemblyAI and return a temporary audio URL."""
        import httpx

        headers = {"Authorization": settings.ASSEMBLYAI_API_KEY}
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                "https://api.assemblyai.com/v2/upload",
                content=audio_bytes,
                headers=headers,
            )
            response.raise_for_status()
            upload_url = response.json().get("upload_url")

        if not upload_url:
            raise ValueError("AssemblyAI did not return an upload URL")

        return upload_url
    
    @staticmethod
    async def _transcribe_with_google(audio_url: str) -> str:
        """Transcribe using Google Speech-to-Text."""
        try:
            # Placeholder for Google Cloud Speech-to-Text
            pass
        except Exception as e:
            logger.error(f"Google Speech error: {e}")
            return ""
