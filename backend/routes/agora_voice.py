"""
Agora Voice API Routes
Real-time voice communication endpoints using Agora RTC
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from typing import Dict, Any, Optional
import logging

from models.schemas import User
from routes.auth import get_current_user
from services.agora_voice_service import agora_voice_service
from services.voice_tutor_service import voice_tutor_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/agora/voice", tags=["agora-voice"])

@router.post("/start-session")
async def start_agora_voice_session(current_user: User = Depends(get_current_user)) -> Dict[str, Any]:
    """
    Start a new Agora voice session for real-time communication
    """
    try:
        logger.info(f"Starting Agora voice session for user: {current_user.id}")
        
        # First create a regular voice session
        session_data = await voice_tutor_service.start_voice_session(
            user_id=current_user.id,
            channel_name=None  # Let it generate automatically
        )
        
        # Then enhance it with Agora voice capabilities
        agora_session = await agora_voice_service.start_agora_voice_session(
            user_id=current_user.id,
            session_data=session_data
        )
        
        logger.info(f"Agora voice session started: {agora_session['session_id']}")
        
        return {
            "status": "success",
            "message": "Agora voice session started",
            **agora_session
        }
        
    except Exception as e:
        logger.error(f"Error starting Agora voice session: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start voice session: {str(e)}")

@router.post("/stream-audio")
async def process_agora_audio_stream(
    session_id: str = Form(...),
    audio_file: UploadFile = File(...),
    audio_format: str = Form(default="opus"),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Process audio stream from Agora RTC
    """
    try:
        logger.info(f"Processing Agora audio stream for session: {session_id}")
        
        # Read audio data
        audio_data = await audio_file.read()
        
        if not audio_data:
            raise HTTPException(status_code=400, detail="No audio data received")
        
        # Process through Agora voice service
        result = await agora_voice_service.process_agora_voice_stream(
            session_id=session_id,
            audio_data=audio_data,
            audio_format=audio_format
        )
        
        if result.get("status") == "error":
            raise HTTPException(status_code=500, detail=result.get("error", "Audio processing failed"))
        
        logger.info(f"Agora audio stream processed successfully: {session_id}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing Agora audio stream: {e}")
        raise HTTPException(status_code=500, detail=f"Audio processing failed: {str(e)}")

@router.post("/user-joined")
async def handle_agora_user_joined(
    request_data: dict,
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Handle Agora user joined event
    """
    try:
        session_id = request_data.get("session_id")
        user_id = request_data.get("user_id")
        
        if not session_id or not user_id:
            raise HTTPException(status_code=400, detail="session_id and user_id are required")
        
        logger.info(f"Agora user joined: {user_id} in session: {session_id}")
        
        result = await agora_voice_service.handle_agora_user_joined(session_id, user_id)
        return result
        
    except Exception as e:
        logger.error(f"Error handling user joined: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/user-left")
async def handle_agora_user_left(
    request_data: dict,
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Handle Agora user left event
    """
    try:
        session_id = request_data.get("session_id")
        user_id = request_data.get("user_id")
        
        if not session_id or not user_id:
            raise HTTPException(status_code=400, detail="session_id and user_id are required")
        
        logger.info(f"Agora user left: {user_id} in session: {session_id}")
        
        result = await agora_voice_service.handle_agora_user_left(session_id, user_id)
        return result
        
    except Exception as e:
        logger.error(f"Error handling user left: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/end-session/{session_id}")
async def end_agora_voice_session(
    session_id: str,
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    End Agora voice session
    """
    try:
        logger.info(f"Ending Agora voice session: {session_id}")
        
        # End Agora voice session
        agora_ended = await agora_voice_service.end_agora_voice_session(session_id)
        
        # End regular voice session
        voice_ended = await voice_tutor_service.end_voice_session(session_id)
        
        return {
            "status": "success",
            "message": "Agora voice session ended",
            "session_id": session_id,
            "agora_cleanup": agora_ended,
            "voice_cleanup": voice_ended
        }
        
    except Exception as e:
        logger.error(f"Error ending Agora voice session: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/active-sessions")
async def get_active_agora_sessions(current_user: User = Depends(get_current_user)) -> Dict[str, Any]:
    """
    Get active Agora voice sessions
    """
    try:
        sessions = agora_voice_service.get_active_sessions()
        return {
            "status": "success",
            **sessions
        }
        
    except Exception as e:
        logger.error(f"Error getting active sessions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/session/{session_id}/status")
async def get_agora_session_status(
    session_id: str,
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get Agora voice session status
    """
    try:
        if session_id in agora_voice_service.active_voice_sessions:
            session = agora_voice_service.active_voice_sessions[session_id]
            return {
                "status": "active",
                "session_id": session_id,
                "voice_enabled": session.get("voice_enabled", False),
                "agora_connected": session.get("agora_connected", False),
                "created_at": session.get("created_at").isoformat() if session.get("created_at") else None,
                "message_count": len(session.get("conversation_context", []))
            }
        else:
            return {
                "status": "not_found",
                "session_id": session_id
            }
            
    except Exception as e:
        logger.error(f"Error getting session status: {e}")
        raise HTTPException(status_code=500, detail=str(e))
