import asyncio
import uuid
import json
import logging
from typing import Optional, Dict, Any
from datetime import datetime

from utils.database import get_supabase_admin
from utils.chroma_client import chroma_client
from utils.mistral_client import ai_client
from services.stt_service import stt_service
from services.tts_service import tts_service
from services.agora_service import agora_service

logger = logging.getLogger(__name__)

class VoiceTutorService:
    """Voice-enabled AI tutor service with complete audio processing pipeline"""
    
    def __init__(self):
        self.supabase = get_supabase_admin()
        self.active_sessions = {}  # Store active voice sessions
    
    async def start_voice_session(self, user_id: str, channel_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Start a new voice tutor session
        
        Args:
            user_id: User identifier
            channel_name: Optional Agora channel name
            
        Returns:
            Session details with Agora tokens
        """
        try:
            # Generate unique session ID and channel name
            session_id = str(uuid.uuid4())
            if not channel_name:
                channel_name = f"tutor_{user_id}_{session_id[:8]}"
            
            # Generate Agora tokens
            from models.schemas import AgoraTokenRequest
            token_request = AgoraTokenRequest(
                channel_name=channel_name,
                user_id=user_id,
                role="publisher"
            )
            
            tokens = agora_service.generate_tokens(token_request)
            
            # Create session record in database (using existing schema)
            session_db_data = {
                "id": session_id,
                "user_id": user_id,
                "session_type": "voice",
                "created_at": datetime.utcnow().isoformat()
            }
            
            # Store in database
            self.supabase.table("tutor_sessions").insert(session_db_data).execute()
            
            # Store in memory for quick access
            self.active_sessions[session_id] = {
                "user_id": user_id,
                "channel_name": channel_name,
                "created_at": datetime.utcnow(),
                "message_count": 0
            }
            
            logger.info(f"Started voice tutor session: {session_id} for user: {user_id}")
            
            return {
                "session_id": session_id,
                "channel_name": channel_name,
                "agora_tokens": tokens,
                "status": "active"
            }
            
        except Exception as e:
            logger.error(f"Error starting voice session: {e}")
            raise
    
    async def process_voice_message(self, session_id: str, audio_data: bytes, audio_format: str = "wav") -> Dict[str, Any]:
        """
        Process voice message through the complete pipeline:
        Audio → STT → Vector DB → LLM → TTS → Audio Response
        
        Args:
            session_id: Active session ID
            audio_data: Raw audio bytes from user
            audio_format: Audio format (wav, mp3, etc.)
            
        Returns:
            Response with text and audio data
        """
        try:
            # Validate session
            if session_id not in self.active_sessions:
                raise Exception("Invalid or expired session")
            
            session = self.active_sessions[session_id]
            user_id = session["user_id"]
            
            logger.info(f"Processing voice message for session: {session_id}")
            
            # Step 1: Speech-to-Text
            logger.info("Step 1: Converting speech to text...")
            user_text = await stt_service.transcribe_audio(audio_data, audio_format)
            
            if not user_text:
                return {
                    "error": "Could not understand the audio. Please try speaking more clearly.",
                    "session_id": session_id
                }
            
            logger.info(f"STT Result: {user_text}")
            
            # Step 2: Process through text pipeline (same as regular tutor)
            logger.info("Step 2: Processing through AI pipeline...")
            response_data = await self._process_text_message(session_id, user_text)
            
            # Step 3: Text-to-Speech for AI response
            logger.info("Step 3: Converting AI response to speech...")
            ai_text = response_data.get("response", "")
            
            if ai_text:
                audio_response = await tts_service.synthesize_speech(ai_text)
                if audio_response:
                    # Encode binary audio data as base64 for JSON serialization
                    import base64
                    response_data["audio_response"] = base64.b64encode(audio_response).decode('utf-8')
                    response_data["has_audio"] = True
                else:
                    response_data["has_audio"] = False
            else:
                response_data["has_audio"] = False
            
            # Update session stats
            session["message_count"] += 1
            
            logger.info(f"Voice message processed successfully for session: {session_id}")
            return response_data
            
        except Exception as e:
            logger.error(f"Error processing voice message: {e}")
            return {
                "error": f"Failed to process voice message: {str(e)}",
                "session_id": session_id
            }
    
    async def process_text_message(self, session_id: str, message: str) -> Dict[str, Any]:
        """
        Process text message (from RTM) through the pipeline
        
        Args:
            session_id: Active session ID
            message: Text message from user
            
        Returns:
            Response with text and optional audio
        """
        try:
            # Validate session
            if session_id not in self.active_sessions:
                raise Exception("Invalid or expired session")
            
            logger.info(f"Processing text message for session: {session_id}")
            
            # Process through text pipeline
            response_data = await self._process_text_message(session_id, message)
            
            # Optionally generate audio response for text messages too
            ai_text = response_data.get("response", "")
            if ai_text:
                audio_response = await tts_service.synthesize_speech(ai_text)
                if audio_response:
                    # Encode binary audio data as base64 for JSON serialization
                    import base64
                    response_data["audio_response"] = base64.b64encode(audio_response).decode('utf-8')
                    response_data["has_audio"] = True
                else:
                    response_data["has_audio"] = False
            
            # Update session stats
            session = self.active_sessions[session_id]
            session["message_count"] += 1
            
            return response_data
            
        except Exception as e:
            logger.error(f"Error processing text message: {e}")
            return {
                "error": f"Failed to process text message: {str(e)}",
                "session_id": session_id
            }
    
    async def _process_text_message(self, session_id: str, user_message: str) -> Dict[str, Any]:
        """
        Internal method to process text through the AI pipeline
        """
        session = self.active_sessions[session_id]
        user_id = session["user_id"]
        
        # Get relevant context from documents
        context = await self._get_relevant_context(user_message, user_id)
        
        # Generate AI response
        ai_response = await self._generate_response(user_message, context, user_id)
        
        # Store interaction in database
        await self._store_interaction(session_id, user_message, ai_response, user_id)
        
        return {
            "session_id": session_id,
            "user_message": user_message,
            "response": ai_response,
            "context_used": bool(context),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _get_relevant_context(self, query: str, user_id: str) -> str:
        """Get relevant context from user's documents"""
        try:
            # Generate embeddings for the query
            query_embedding = await ai_client.generate_embeddings([query])
            
            if not query_embedding:
                return ""
            
            # Search for relevant documents
            results = chroma_client.query_documents(
                query_embeddings=[query_embedding[0]],
                n_results=5,
                where={"user_id": user_id}
            )
            
            if not results["documents"] or not results["documents"][0]:
                return ""
            
            # Combine relevant chunks
            context_chunks = results["documents"][0]
            context = "\n\n".join(context_chunks)
            
            logger.info(f"Retrieved context: {len(context)} characters from {len(context_chunks)} chunks")
            return context
            
        except Exception as e:
            logger.error(f"Error getting relevant context: {e}")
            return ""
    
    async def _generate_response(self, user_message: str, context: str, user_id: str) -> str:
        """Generate AI response using LLM"""
        try:
            # Prepare messages for the AI
            system_prompt = """You are Kashar AI, a helpful and knowledgeable tutor. You help students learn by:

1. Answering questions clearly and concisely
2. Using the provided study material context when relevant
3. Encouraging further learning and curiosity
4. Speaking in a friendly, conversational tone suitable for voice interaction
5. Keeping responses focused and not too lengthy for voice delivery

If you have relevant study material context, use it to provide accurate, detailed answers. If not, provide general educational guidance and suggest the student upload relevant materials."""
            
            messages = [
                {"role": "system", "content": system_prompt}
            ]
            
            # Add context if available
            if context:
                context_message = f"Here is relevant study material context:\n\n{context}\n\nBased on this context and your knowledge, please answer the student's question."
                messages.append({"role": "system", "content": context_message})
            
            # Add user message
            messages.append({"role": "user", "content": user_message})
            
            # Generate response
            response = await ai_client.chat_completion(messages)
            
            if not response:
                return "I'm sorry, I'm having trouble generating a response right now. Please try again."
            
            logger.info(f"Generated AI response: {len(response)} characters")
            return response
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return "I apologize, but I encountered an error while processing your question. Please try again."
    
    async def _store_interaction(self, session_id: str, user_message: str, ai_response: str, user_id: str):
        """Store the interaction in the database"""
        try:
            interaction_data = {
                "id": str(uuid.uuid4()),
                "session_id": session_id,
                "user_id": user_id,
                "user_message": user_message,
                "ai_response": ai_response,
                "message_type": "voice",
                "created_at": datetime.utcnow().isoformat()
            }
            
            self.supabase.table("tutor_messages").insert(interaction_data).execute()
            logger.info(f"Stored interaction for session: {session_id}")
            
        except Exception as e:
            logger.error(f"Error storing interaction: {e}")
    
    async def end_voice_session(self, session_id: str) -> bool:
        """End a voice tutor session"""
        try:
            if session_id not in self.active_sessions:
                logger.warning(f"Attempted to end non-existent session: {session_id}")
                return False
            
            session = self.active_sessions[session_id]
            
            # Update session in database (using existing schema)
            # Note: Only updating if there are compatible fields
            # The session end is tracked in memory for now
            
            # Remove from active sessions
            del self.active_sessions[session_id]
            
            logger.info(f"Ended voice session: {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error ending voice session: {e}")
            return False
    
    def get_active_sessions(self, user_id: str) -> list:
        """Get active sessions for a user"""
        return [
            {
                "session_id": sid,
                "channel_name": session["channel_name"],
                "created_at": session["created_at"].isoformat(),
                "message_count": session["message_count"]
            }
            for sid, session in self.active_sessions.items()
            if session["user_id"] == user_id
        ]

# Global voice tutor service instance
voice_tutor_service = VoiceTutorService()
