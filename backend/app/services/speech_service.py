from typing import Optional
from app.config import settings
import logging
import asyncio

logger = logging.getLogger(__name__)

class SpeechService:
    """Service for speech-to-text transcription."""
    
    MAX_RETRIES = 3
    RETRY_DELAY = 1.0
    REQUEST_TIMEOUT = 120.0
    POLL_TIMEOUT = 300.0

    @staticmethod
    async def transcribe_audio_bytes(audio_bytes: bytes, max_retries: int = None) -> str:
        """Upload raw audio bytes to AssemblyAI and return the transcript text."""
        if not settings.ASSEMBLYAI_API_KEY:
            logger.error("No AssemblyAI API key configured")
            raise ValueError("AssemblyAI API key is not configured")
        
        if not audio_bytes or len(audio_bytes) == 0:
            logger.error("Empty audio bytes provided")
            raise ValueError("Audio file is empty")
        
        logger.info(f"Starting transcription for {len(audio_bytes)} bytes of audio")
        retries = max_retries if max_retries is not None else SpeechService.MAX_RETRIES
        
        for attempt in range(retries):
            try:
                upload_url = await SpeechService._upload_to_assemblyai(audio_bytes)
                logger.info(f"Successfully uploaded audio to AssemblyAI: {upload_url}")
                
                transcript = await SpeechService._transcribe_with_assemblyai(upload_url)
                if transcript:
                    logger.info(f"Successfully transcribed audio: {len(transcript)} chars")
                    return transcript
                else:
                    logger.warning("Transcription returned empty result")
                    raise ValueError("Empty transcription result")
                    
            except Exception as e:
                logger.warning(f"Transcription attempt {attempt + 1}/{retries} failed: {e}")
                if attempt < retries - 1:
                    await asyncio.sleep(SpeechService.RETRY_DELAY * (attempt + 1))
                else:
                    logger.error(f"All {retries} transcription attempts failed")
                    raise
    
    @staticmethod
    async def transcribe_audio(audio_file_path: str) -> str:
        """Transcribe audio file to text."""
        try:
            if settings.ASSEMBLYAI_API_KEY:
                return await SpeechService._transcribe_with_assemblyai(audio_file_path)
            else:
                raise ValueError("No speech-to-text API configured")
        except Exception as e:
            logger.error(f"Transcription error: {e}")
            raise
    
    @staticmethod
    async def _transcribe_with_assemblyai(audio_url: str) -> str:
        """Transcribe using AssemblyAI API with polling and timeout."""
        try:
            import httpx
            
            headers = {"Authorization": settings.ASSEMBLYAI_API_KEY}
            
            logger.info(f"Requesting transcription for audio URL: {audio_url}")
            
            async with httpx.AsyncClient(timeout=httpx.Timeout(SpeechService.REQUEST_TIMEOUT)) as client:
                # Submit transcription request
                response = await client.post(
                    "https://api.assemblyai.com/v2/transcript",
                    json={"audio_url": audio_url},
                    headers=headers,
                )
                
                if response.status_code != 200:
                    logger.error(f"AssemblyAI transcription request failed: {response.status_code} - {response.text}")
                    response.raise_for_status()
                
                transcript_id = response.json().get("id")
                if not transcript_id:
                    logger.error("AssemblyAI did not return a transcript ID")
                    raise ValueError("AssemblyAI did not return a transcript id")
                
                logger.info(f"Transcription ID: {transcript_id}, polling for status...")
                
                # Poll for completion
                start_time = asyncio.get_event_loop().time()
                poll_count = 0
                
                while True:
                    poll_count += 1
                    elapsed = asyncio.get_event_loop().time() - start_time
                    
                    if elapsed > SpeechService.POLL_TIMEOUT:
                        logger.error(f"Polling timeout after {poll_count} attempts ({elapsed:.1f}s)")
                        raise TimeoutError(f"Transcription polling timeout after {SpeechService.POLL_TIMEOUT}s")
                    
                    result_response = await client.get(
                        f"https://api.assemblyai.com/v2/transcript/{transcript_id}",
                        headers=headers,
                    )
                    
                    if result_response.status_code != 200:
                        logger.error(f"Poll failed: {result_response.status_code} - {result_response.text}")
                        result_response.raise_for_status()
                    
                    result = result_response.json()
                    status = result.get("status")
                    
                    logger.info(f"Poll {poll_count}: Status = {status} (elapsed: {elapsed:.1f}s)")
                    
                    if status == "completed":
                        text = result.get("text", "")
                        logger.info(f"Transcription completed: {len(text)} chars")
                        return text
                    
                    if status == "error":
                        error_msg = result.get("error", "Unknown error")
                        logger.error(f"AssemblyAI transcription error: {error_msg}")
                        raise Exception(f"AssemblyAI error: {error_msg}")
                    
                    if status not in ["queued", "processing"]:
                        logger.warning(f"Unexpected status: {status}")
                    
                    await asyncio.sleep(1)
                    
        except asyncio.TimeoutError as e:
            logger.error(f"AssemblyAI request timeout: {e}")
            raise
        except Exception as e:
            logger.error(f"AssemblyAI error: {e}")
            raise
    
    @staticmethod
    async def _upload_to_assemblyai(audio_bytes: bytes) -> str:
        """Upload audio bytes to AssemblyAI and return a temporary audio URL."""
        try:
            import httpx
            
            headers = {"Authorization": settings.ASSEMBLYAI_API_KEY}
            logger.info(f"Uploading {len(audio_bytes)} bytes to AssemblyAI")
            
            async with httpx.AsyncClient(timeout=httpx.Timeout(SpeechService.REQUEST_TIMEOUT)) as client:
                response = await client.post(
                    "https://api.assemblyai.com/v2/upload",
                    content=audio_bytes,
                    headers=headers,
                )
                
                if response.status_code != 200:
                    logger.error(f"Upload failed: {response.status_code} - {response.text}")
                    response.raise_for_status()
                
                upload_url = response.json().get("upload_url")
                if not upload_url:
                    logger.error("AssemblyAI did not return an upload URL")
                    raise ValueError("AssemblyAI did not return an upload URL")
                
                logger.info(f"Upload successful: {upload_url}")
                return upload_url
                
        except Exception as e:
            logger.error(f"Upload to AssemblyAI failed: {e}")
            raise
    
    @staticmethod
    async def _transcribe_with_google(audio_url: str) -> str:
        """Transcribe using Google Speech-to-Text (placeholder)."""
        try:
            logger.info("Google Speech-to-Text not yet implemented")
            raise NotImplementedError("Google Speech-to-Text is not yet implemented")
        except Exception as e:
            logger.error(f"Google Speech error: {e}")
            raise
