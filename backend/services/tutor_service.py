import uuid
from utils.database import get_supabase_admin
from utils.chroma_client import chroma_client
from utils.mistral_client import ai_client
from models.schemas import TutorMessage, TutorResponse
import logging

logger = logging.getLogger(__name__)

class TutorService:
    def __init__(self):
        self.supabase = get_supabase_admin()
    
    async def start_session(self, user_id: str, session_type: str = "text") -> str:
        """Start a new tutor session"""
        try:
            session_id = str(uuid.uuid4())
            session_record = {
                "id": session_id,
                "user_id": user_id,
                "session_type": session_type
            }
            
            self.supabase.table("tutor_sessions").insert(session_record).execute()
            logger.info(f"Started tutor session {session_id} for user {user_id}")
            return session_id
            
        except Exception as e:
            logger.error(f"Error starting tutor session: {e}")
            raise
    
    async def process_message(self, message: TutorMessage, user_id: str) -> TutorResponse:
        """Process a tutor message and generate response"""
        try:
            session_id = message.session_id
            if not session_id:
                session_id = await self.start_session(user_id)
            
            # Store user message
            await self._store_message(session_id, user_id, "user", message.message)
            
            # Get relevant context from user's documents
            context = await self._get_relevant_context(message.message, user_id)
            
            # Generate response using LLM
            response_text = await self._generate_response(message.message, context)
            
            # Store assistant response
            await self._store_message(session_id, user_id, "assistant", response_text)
            
            # Update session message count
            await self._update_session_stats(session_id)
            
            # Extract sources from context
            sources = self._extract_sources(context) if context else None
            
            response = TutorResponse(
                response=response_text,
                session_id=session_id,
                sources=sources
            )
            
            logger.info(f"Processed tutor message for session {session_id}")
            return response
            
        except Exception as e:
            logger.error(f"Error processing tutor message: {e}")
            raise
    
    async def _get_relevant_context(self, query: str, user_id: str) -> str:
        """Get relevant context from user's documents"""
        try:
            # Generate embedding for the query
            query_embedding = await ai_client.generate_embeddings([query])
            
            # Search for relevant chunks
            results = chroma_client.query_documents(
                query_embeddings=query_embedding,
                n_results=5,
                where={"user_id": user_id}
            )
            
            if results['documents'][0]:
                return "\n\n".join(results['documents'][0])
            else:
                return ""
                
        except Exception as e:
            logger.error(f"Error getting relevant context: {e}")
            return ""
    
    async def _generate_response(self, user_message: str, context: str) -> str:
        """Generate tutor response using LLM"""
        try:
            system_prompt = """You are Kashar AI, a helpful and knowledgeable study tutor. Your role is to:
            1. Help students understand concepts from their study materials
            2. Answer questions clearly and concisely
            3. Provide explanations and examples when needed
            4. Encourage learning and critical thinking
            5. Stay focused on educational content
            
            If you have relevant study material context, use it to provide accurate answers.
            If you don't have relevant context, provide general educational guidance."""
            
            messages = [
                {"role": "system", "content": system_prompt}
            ]
            
            if context:
                messages.append({
                    "role": "system", 
                    "content": f"Relevant study material:\n{context}"
                })
            
            messages.append({
                "role": "user", 
                "content": user_message
            })
            
            response = await ai_client.chat_completion(messages, max_tokens=800)
            return response
            
        except Exception as e:
            logger.error(f"Error generating tutor response: {e}")
            raise
    
    async def _store_message(self, session_id: str, user_id: str, role: str, content: str):
        """Store a message in the database"""
        try:
            message_record = {
                "id": str(uuid.uuid4()),
                "session_id": session_id,
                "user_id": user_id,
                "role": role,
                "content": content
            }
            
            self.supabase.table("tutor_messages").insert(message_record).execute()
            
        except Exception as e:
            logger.error(f"Error storing message: {e}")
            raise
    
    async def _update_session_stats(self, session_id: str):
        """Update session statistics"""
        try:
            # Get current message count
            result = self.supabase.table("tutor_messages").select("id").eq("session_id", session_id).execute()
            message_count = len(result.data)
            
            # Update session
            self.supabase.table("tutor_sessions").update({
                "message_count": message_count
            }).eq("id", session_id).execute()
            
        except Exception as e:
            logger.error(f"Error updating session stats: {e}")
    
    def _extract_sources(self, context: str) -> list:
        """Extract source information from context"""
        # This is a simplified implementation
        # In a real system, you'd track which documents the chunks came from
        if context:
            return ["Study Material"]
        return None
    
    async def end_session(self, session_id: str, user_id: str):
        """End a tutor session"""
        try:
            # Calculate session duration (simplified)
            session_result = self.supabase.table("tutor_sessions").select("created_at, message_count").eq("id", session_id).eq("user_id", user_id).execute()
            
            if session_result.data:
                session_data = session_result.data[0]
                
                # Update session end time
                self.supabase.table("tutor_sessions").update({
                    "ended_at": "NOW()"
                }).eq("id", session_id).execute()
                
                # Log progress
                progress_record = {
                    "id": str(uuid.uuid4()),
                    "user_id": user_id,
                    "activity_type": "tutor",
                    "duration": 0,  # Would calculate actual duration
                    "metadata": {
                        "session_id": session_id,
                        "message_count": session_data.get("message_count", 0)
                    }
                }
                
                self.supabase.table("progress_logs").insert(progress_record).execute()
                
        except Exception as e:
            logger.error(f"Error ending session: {e}")
            raise
    
    async def get_session_history(self, session_id: str, user_id: str) -> list:
        """Get message history for a session"""
        try:
            result = self.supabase.table("tutor_messages").select("*").eq("session_id", session_id).eq("user_id", user_id).order("created_at").execute()
            return result.data
        except Exception as e:
            logger.error(f"Error getting session history: {e}")
            raise

tutor_service = TutorService()
