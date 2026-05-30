from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from app.services.auth_service import AuthService
from app.services.speech_service import SpeechService
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/speech", tags=["speech"])
security = HTTPBearer()


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current authenticated user."""
    user_id = AuthService.decode_access_token(credentials.credentials)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
    return user_id


@router.post("/transcribe")
async def transcribe_audio(
    file: UploadFile = File(...),
    user_id: str = Depends(get_current_user),
):
    """Transcribe an uploaded audio recording with AssemblyAI."""
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No filename provided")
        
        if file.content_type and not file.content_type.startswith("audio/"):
            logger.warning(f"Unexpected content type: {file.content_type}")
        
        # Read audio bytes
        audio_bytes = await file.read()
        
        if not audio_bytes:
            logger.error("Received empty audio file")
            raise HTTPException(status_code=400, detail="Audio file is empty")
        
        logger.info(f"Received audio file: {file.filename} ({len(audio_bytes)} bytes)")
        
        # Transcribe
        try:
            text = await SpeechService.transcribe_audio_bytes(audio_bytes)
        except ValueError as e:
            logger.error(f"Validation error: {e}")
            raise HTTPException(status_code=400, detail=str(e))
        except TimeoutError as e:
            logger.error(f"Transcription timeout: {e}")
            raise HTTPException(status_code=504, detail="Transcription service timeout. Please try again.")
        except Exception as e:
            logger.error(f"Transcription service error: {e}")
            raise HTTPException(
                status_code=502,
                detail=f"Transcription failed: {str(e)}"
            )
        
        if not text:
            logger.warning("Transcription returned empty text")
            raise HTTPException(
                status_code=502,
                detail="Transcription service returned empty result"
            )
        
        logger.info(f"Successfully transcribed: {len(text)} characters")
        return {"text": text, "status": "success"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Unexpected error in transcribe endpoint: {e}")
        raise HTTPException(
            status_code=500,
            detail="Unexpected server error"
        )


@router.post("/text-to-speech")
async def text_to_speech(
    data: dict,
    user_id: str = Depends(get_current_user),
):
    """Convert text to speech (returns text for frontend Web Speech API)."""
    try:
        text = data.get("text", "").strip()
        
        if not text:
            raise HTTPException(status_code=400, detail="No text provided")
        
        if len(text) > 5000:
            logger.warning(f"Text too long for TTS: {len(text)} chars")
            raise HTTPException(status_code=400, detail="Text too long (max 5000 characters)")
        
        logger.info(f"Preparing text-to-speech for {len(text)} characters")
        
        # Return text for frontend Web Speech API to handle
        # The frontend will use the Web Speech API to convert text to speech
        return {
            "status": "ready",
            "text": text,
            "message": "Use Web Speech API in frontend to play audio"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Text-to-speech error: {e}")
        raise HTTPException(status_code=500, detail="Text-to-speech service error")
