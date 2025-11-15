import uuid
from utils.database import get_supabase_admin
from utils.chroma_client import chroma_client
from utils.mistral_client import ai_client
from models.schemas import FlashcardRequest, FlashcardSet
import logging

logger = logging.getLogger(__name__)

class FlashcardService:
    def __init__(self):
        self.supabase = get_supabase_admin()
    
    async def generate_flashcards(self, request: FlashcardRequest, user_id: str) -> FlashcardSet:
        """Generate flashcards for a topic"""
        try:
            # Get relevant chunks from ChromaDB
            query_embedding = await ai_client.generate_embeddings([request.topic])
            
            results = chroma_client.query_documents(
                query_embeddings=query_embedding,
                n_results=10,
                where={"user_id": user_id}
            )
            
            if not results['documents'][0]:
                raise Exception(f"No study material found for topic: {request.topic}")
            
            # Combine relevant chunks
            context = "\n\n".join(results['documents'][0])
            
            # Generate flashcards using LLM
            cards = await ai_client.generate_flashcards(
                context=context,
                topic=request.topic,
                num_cards=request.num_cards
            )
            
            # Create flashcard set record
            set_id = str(uuid.uuid4())
            flashcard_record = {
                "id": set_id,
                "user_id": user_id,
                "topic": request.topic,
                "cards": cards
            }
            
            self.supabase.table("flashcard_sets").insert(flashcard_record).execute()
            
            # Log progress
            progress_record = {
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "activity_type": "flashcard",
                "topic": request.topic,
                "metadata": {
                    "set_id": set_id,
                    "card_count": len(cards)
                }
            }
            
            self.supabase.table("progress_logs").insert(progress_record).execute()
            
            flashcard_set = FlashcardSet(
                id=set_id,
                topic=request.topic,
                cards=cards
            )
            
            logger.info(f"Generated {len(cards)} flashcards for user {user_id}, topic: {request.topic}")
            return flashcard_set
            
        except Exception as e:
            logger.error(f"Error generating flashcards: {e}")
            raise
    
    async def get_user_flashcard_sets(self, user_id: str) -> list:
        """Get all flashcard sets for a user"""
        try:
            result = self.supabase.table("flashcard_sets").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
            return result.data
        except Exception as e:
            logger.error(f"Error getting flashcard sets: {e}")
            raise
    
    async def get_flashcard_set(self, set_id: str, user_id: str) -> dict:
        """Get a specific flashcard set"""
        try:
            result = self.supabase.table("flashcard_sets").select("*").eq("id", set_id).eq("user_id", user_id).execute()
            
            if not result.data:
                raise Exception("Flashcard set not found")
            
            return result.data[0]
        except Exception as e:
            logger.error(f"Error getting flashcard set: {e}")
            raise
    
    async def delete_flashcard_set(self, set_id: str, user_id: str) -> bool:
        """Delete a flashcard set"""
        try:
            result = self.supabase.table("flashcard_sets").delete().eq("id", set_id).eq("user_id", user_id).execute()
            return len(result.data) > 0
        except Exception as e:
            logger.error(f"Error deleting flashcard set: {e}")
            raise

flashcard_service = FlashcardService()
