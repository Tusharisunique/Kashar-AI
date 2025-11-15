from fastapi import APIRouter, HTTPException, Depends
from routes.auth import get_current_user
from services.quiz_service import quiz_service
from models.schemas import QuizRequest, QuizSubmission
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/quiz", tags=["quiz"])

@router.post("/generate")
async def generate_quiz(
    quiz_request: QuizRequest,
    current_user = Depends(get_current_user)
):
    """Generate a new quiz"""
    try:
        quiz = await quiz_service.generate_quiz(quiz_request, current_user.id)
        return {"quiz": quiz.dict()}
    except Exception as e:
        logger.error(f"Generate quiz error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/submit")
async def submit_quiz(
    submission: QuizSubmission,
    current_user = Depends(get_current_user)
):
    """Submit quiz answers"""
    try:
        result = await quiz_service.submit_quiz(submission, current_user.id)
        return {"result": result.dict()}
    except Exception as e:
        logger.error(f"Submit quiz error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history")
async def get_quiz_history(current_user = Depends(get_current_user)):
    """Get user's quiz history"""
    try:
        history = await quiz_service.get_user_quiz_history(current_user.id)
        return {"history": history}
    except Exception as e:
        logger.error(f"Get quiz history error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
