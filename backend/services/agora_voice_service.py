"""
Agora Voice Service for real-time voice communication with AI
This service handles Agora RTC integration for streaming voice conversations
"""
import asyncio
import logging
import json
import base64
from typing import Dict, Any, Optional
from datetime import datetime
import uuid

from services.stt_service import stt_service
from services.tts_service import tts_service
from services.tutor_service import tutor_service
from utils.config import AGORA_APP_ID, AGORA_APP_CERTIFICATE

logger = logging.getLogger(__name__)

class AgoraVoiceService:
    """Service for handling Agora-based real-time voice conversations"""
    
    def __init__(self):
        self.active_voice_sessions = {}  # session_id -> session_data
        self.voice_buffers = {}  # session_id -> audio_buffer
        self.processing_queue = {}  # session_id -> processing_status
        
    async def start_agora_voice_session(self, user_id: str, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Initialize Agora voice session for real-time communication
        
        Args:
            user_id: User identifier
            session_data: Session data from voice tutor service
            
        Returns:
            Enhanced session data with Agora voice configuration
        """
        try:
            session_id = session_data["session_id"]
            
            # Initialize voice session
            self.active_voice_sessions[session_id] = {
                "user_id": user_id,
                "session_id": session_id,
                "channel_name": session_data["channel_name"],
                "agora_tokens": session_data["agora_tokens"],
                "created_at": datetime.utcnow(),
                "voice_enabled": True,
                "processing_status": "ready",
                "conversation_context": []
            }
            
            # Initialize voice buffer for this session
            self.voice_buffers[session_id] = {
                "incoming_audio": [],
                "processing": False,
                "last_activity": datetime.utcnow()
            }
            
            logger.info(f"Agora voice session initialized: {session_id}")
            
            return {
                **session_data,
                "voice_streaming_enabled": True,
                "real_time_processing": True,
                "agora_voice_config": {
                    "app_id": AGORA_APP_ID,
                    "channel_name": session_data["channel_name"],
                    "rtc_token": session_data["agora_tokens"]["rtc_token"],
                    "user_id": user_id,
                    "voice_codec": "opus",
                    "sample_rate": 48000,
                    "channels": 1
                }
            }
            
        except Exception as e:
            logger.error(f"Error starting Agora voice session: {e}")
            raise
    
    async def process_agora_voice_stream(self, session_id: str, audio_data: bytes, 
                                       audio_format: str = "opus") -> Dict[str, Any]:
        """
        Process incoming voice stream from Agora RTC
        
        Args:
            session_id: Active session ID
            audio_data: Raw audio data from Agora
            audio_format: Audio format (opus, pcm, etc.)
            
        Returns:
            Processing result with AI response
        """
        try:
            if session_id not in self.active_voice_sessions:
                raise Exception("Invalid voice session")
            
            session = self.active_voice_sessions[session_id]
            user_id = session["user_id"]
            
            logger.info(f"Processing Agora voice stream for session: {session_id}")
            
            # Step 1: Convert audio format if needed (Agora typically uses Opus)
            processed_audio = await self._convert_agora_audio(audio_data, audio_format)
            
            # Step 2: Speech-to-Text
            logger.info("Converting speech to text...")
            user_text = await stt_service.transcribe_audio(processed_audio, "wav")
            
            if not user_text:
                return {
                    "session_id": session_id,
                    "status": "no_speech_detected",
                    "message": "No speech detected in audio stream"
                }
            
            logger.info(f"Transcribed text: {user_text}")
            
            # Step 3: Get AI response
            logger.info("Generating AI response...")
            
            # Add to conversation context
            session["conversation_context"].append({
                "role": "user",
                "content": user_text,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            # Get AI response using tutor service
            ai_response = await self._get_ai_response(user_text, user_id, session["conversation_context"])
            
            # Add AI response to context
            session["conversation_context"].append({
                "role": "assistant", 
                "content": ai_response,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            # Step 4: Text-to-Speech for Agora streaming
            logger.info("Converting AI response to speech...")
            audio_response = await tts_service.synthesize_speech(ai_response)
            
            # Step 5: Prepare for Agora RTC streaming
            streaming_audio = None
            if audio_response:
                streaming_audio = await self._prepare_audio_for_agora(audio_response)
            
            result = {
                "session_id": session_id,
                "user_message": user_text,
                "ai_response": ai_response,
                "status": "success",
                "timestamp": datetime.utcnow().isoformat(),
                "agora_streaming": {
                    "has_audio": bool(streaming_audio),
                    "audio_format": "opus",
                    "sample_rate": 48000
                }
            }
            
            if streaming_audio:
                # Encode for JSON transport
                result["agora_streaming"]["audio_data"] = base64.b64encode(streaming_audio).decode('utf-8')
            
            logger.info(f"Agora voice processing completed for session: {session_id}")
            return result
            
        except Exception as e:
            logger.error(f"Error processing Agora voice stream: {e}")
            return {
                "session_id": session_id,
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def _convert_agora_audio(self, audio_data: bytes, format: str) -> bytes:
        """Convert Agora audio format to format suitable for STT"""
        try:
            # For now, assume the audio is already in a compatible format
            # In production, you might need to convert Opus to WAV/PCM
            logger.info(f"Converting audio format: {format} -> wav")
            
            if format.lower() == "opus":
                # TODO: Implement Opus to WAV conversion if needed
                # For now, return as-is and let STT service handle it
                pass
            
            return audio_data
            
        except Exception as e:
            logger.error(f"Error converting audio format: {e}")
            return audio_data
    
    async def _prepare_audio_for_agora(self, audio_data: bytes) -> bytes:
        """Prepare TTS audio for Agora RTC streaming"""
        try:
            # Convert TTS output (usually MP3) to format suitable for Agora (Opus/PCM)
            logger.info("Preparing audio for Agora streaming")
            
            # For now, return the audio as-is
            # In production, you might need to convert to Opus or PCM
            return audio_data
            
        except Exception as e:
            logger.error(f"Error preparing audio for Agora: {e}")
            return audio_data
    
    async def _get_ai_response(self, user_message: str, user_id: str, context: list) -> str:
        """Get AI response using the tutor service"""
        try:
            # Use the existing tutor service for consistent AI responses
            response = await tutor_service.get_response(user_message, user_id)
            return response.get("response", "I'm sorry, I couldn't process your request.")
            
        except Exception as e:
            logger.error(f"Error getting AI response: {e}")
            return "I'm sorry, I'm having trouble processing your request right now."
    
    async def handle_agora_user_joined(self, session_id: str, user_id: str) -> Dict[str, Any]:
        """Handle when user joins Agora channel"""
        try:
            if session_id in self.active_voice_sessions:
                session = self.active_voice_sessions[session_id]
                session["agora_connected"] = True
                session["connected_at"] = datetime.utcnow()
                
                logger.info(f"User {user_id} joined Agora channel for session: {session_id}")
                
                return {
                    "status": "user_joined",
                    "session_id": session_id,
                    "message": "Voice streaming ready"
                }
            else:
                raise Exception("Session not found")
                
        except Exception as e:
            logger.error(f"Error handling user join: {e}")
            return {"status": "error", "error": str(e)}
    
    async def handle_agora_user_left(self, session_id: str, user_id: str) -> Dict[str, Any]:
        """Handle when user leaves Agora channel"""
        try:
            if session_id in self.active_voice_sessions:
                session = self.active_voice_sessions[session_id]
                session["agora_connected"] = False
                session["disconnected_at"] = datetime.utcnow()
                
                logger.info(f"User {user_id} left Agora channel for session: {session_id}")
                
                return {
                    "status": "user_left",
                    "session_id": session_id
                }
            else:
                logger.warning(f"Session {session_id} not found for user leave event")
                
        except Exception as e:
            logger.error(f"Error handling user leave: {e}")
            return {"status": "error", "error": str(e)}
    
    async def end_agora_voice_session(self, session_id: str) -> bool:
        """End Agora voice session and cleanup"""
        try:
            if session_id in self.active_voice_sessions:
                session = self.active_voice_sessions[session_id]
                session["ended_at"] = datetime.utcnow()
                
                # Cleanup
                del self.active_voice_sessions[session_id]
                if session_id in self.voice_buffers:
                    del self.voice_buffers[session_id]
                if session_id in self.processing_queue:
                    del self.processing_queue[session_id]
                
                logger.info(f"Agora voice session ended: {session_id}")
                return True
            else:
                logger.warning(f"Session {session_id} not found for cleanup")
                return False
                
        except Exception as e:
            logger.error(f"Error ending Agora voice session: {e}")
            return False
    
    def get_active_sessions(self) -> Dict[str, Any]:
        """Get all active Agora voice sessions"""
        return {
            "active_sessions": len(self.active_voice_sessions),
            "sessions": list(self.active_voice_sessions.keys())
        }

# Global service instance
agora_voice_service = AgoraVoiceService()
