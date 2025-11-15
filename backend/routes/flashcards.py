from fastapi import APIRouter, HTTPException, Depends
from routes.auth import get_current_user
from services.flashcard_service import flashcard_service
from models.schemas import FlashcardRequest
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/flashcards", tags=["flashcards"])

@router.post("/generate")
async def generate_flashcards(
    request: FlashcardRequest,
    current_user = Depends(get_current_user)
):
    """Generate flashcards for a topic"""
    try:
        flashcard_set = await flashcard_service.generate_flashcards(request, current_user.id)
        return {"flashcard_set": flashcard_set.dict()}
    except Exception as e:
        logger.error(f"Generate flashcards error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/")
async def get_flashcard_sets(current_user = Depends(get_current_user)):
    """Get all flashcard sets for the user"""
    try:
        sets = await flashcard_service.get_user_flashcard_sets(current_user.id)
        return {"flashcard_sets": sets}
    except Exception as e:
        logger.error(f"Get flashcard sets error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{set_id}")
async def get_flashcard_set(
    set_id: str,
    current_user = Depends(get_current_user)
):
    """Get a specific flashcard set"""
    try:
        flashcard_set = await flashcard_service.get_flashcard_set(set_id, current_user.id)
        return {"flashcard_set": flashcard_set}
    except Exception as e:
        logger.error(f"Get flashcard set error: {e}")
        raise HTTPException(status_code=404, detail="Flashcard set not found")

@router.delete("/{set_id}")
async def delete_flashcard_set(
    set_id: str,
    current_user = Depends(get_current_user)
):
    """Delete a flashcard set"""
    try:
        success = await flashcard_service.delete_flashcard_set(set_id, current_user.id)
        if success:
            return {"message": "Flashcard set deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Flashcard set not found")
    except Exception as e:
        logger.error(f"Delete flashcard set error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
