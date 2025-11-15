from fastapi import APIRouter, HTTPException, Depends, File, UploadFile, Form
from routes.auth import get_current_user
from services.tutor_service import tutor_service
from services.voice_tutor_service import voice_tutor_service
from models.schemas import TutorMessage, VoiceTextMessage
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/tutor", tags=["tutor"])

@router.post("/start-session")
async def start_session(
    session_type: str = "text",
    current_user = Depends(get_current_user)
):
    """Start a new tutor session"""
    try:
        session_id = await tutor_service.start_session(current_user.id, session_type)
        return {"session_id": session_id}
    except Exception as e:
        logger.error(f"Start session error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/message")
async def send_message(
    message: TutorMessage,
    current_user = Depends(get_current_user)
):
    """Send a message to the tutor"""
    try:
        response = await tutor_service.process_message(message, current_user.id)
        return {"response": response.dict()}
    except Exception as e:
        logger.error(f"Send message error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/end-session/{session_id}")
async def end_session(
    session_id: str,
    current_user = Depends(get_current_user)
):
    """End a tutor session"""
    try:
        await tutor_service.end_session(session_id, current_user.id)
        return {"message": "Session ended successfully"}
    except Exception as e:
        logger.error(f"End session error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/session/{session_id}/history")
async def get_session_history(
    session_id: str,
    current_user = Depends(get_current_user)
):
    """Get message history for a session"""
    try:
        history = await tutor_service.get_session_history(session_id, current_user.id)
        return {"history": history}
    except Exception as e:
        logger.error(f"Get session history error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Voice Tutor Endpoints

@router.post("/voice/start-session")
async def start_voice_session(
    channel_name: str = None,
    current_user = Depends(get_current_user)
):
    """Start a new voice tutor session with Agora tokens"""
    try:
        session_data = await voice_tutor_service.start_voice_session(
            current_user.id, 
            channel_name
        )
        return session_data
    except Exception as e:
        logger.error(f"Start voice session error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/voice/process-audio")
async def process_voice_message(
    session_id: str = Form(...),
    audio_file: UploadFile = File(...),
    current_user = Depends(get_current_user)
):
    """Process voice message through STT → LLM → TTS pipeline"""
    try:
        # Read audio data
        audio_data = await audio_file.read()
        
        # Determine audio format from filename
        audio_format = "wav"
        if audio_file.filename:
            if audio_file.filename.endswith('.mp3'):
                audio_format = "mp3"
            elif audio_file.filename.endswith('.m4a'):
                audio_format = "m4a"
        
        # Process through voice pipeline
        response = await voice_tutor_service.process_voice_message(
            session_id, 
            audio_data, 
            audio_format
        )
        
        return response
    except Exception as e:
        logger.error(f"Process voice message error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/voice/process-text")
async def process_text_in_voice_session(
    payload: VoiceTextMessage,
    current_user = Depends(get_current_user)
):
    """Process text message in voice session (RTM messaging)"""
    try:
        response = await voice_tutor_service.process_text_message(payload.session_id, payload.message)
        return response
    except Exception as e:
        logger.error(f"Process text in voice session error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/voice/end-session/{session_id}")
async def end_voice_session(
    session_id: str,
    current_user = Depends(get_current_user)
):
    """End a voice tutor session"""
    try:
        success = await voice_tutor_service.end_voice_session(session_id)
        if success:
            return {"message": "Voice session ended successfully"}
        else:
            raise HTTPException(status_code=404, detail="Session not found")
    except Exception as e:
        logger.error(f"End voice session error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/voice/active-sessions")
async def get_active_voice_sessions(
    current_user = Depends(get_current_user)
):
    """Get active voice sessions for current user"""
    try:
        sessions = voice_tutor_service.get_active_sessions(current_user.id)
        return {"sessions": sessions}
    except Exception as e:
        logger.error(f"Get active voice sessions error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
