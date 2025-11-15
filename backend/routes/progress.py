from fastapi import APIRouter, HTTPException, Depends, Query
from routes.auth import get_current_user
from services.progress_service import progress_service
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/progress", tags=["progress"])

@router.get("/")
async def get_progress(
    days: int = Query(30, description="Number of days to include in progress data"),
    current_user = Depends(get_current_user)
):
    """Get user progress data"""
    try:
        progress_data = await progress_service.get_user_progress(current_user.id, days)
        return {"progress": progress_data.dict()}
    except Exception as e:
        logger.error(f"Get progress error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/streaks")
async def get_learning_streaks(current_user = Depends(get_current_user)):
    """Get learning streak information"""
    try:
        streaks = await progress_service.get_learning_streaks(current_user.id)
        return {"streaks": streaks}
    except Exception as e:
        logger.error(f"Get streaks error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics")
async def get_performance_analytics(current_user = Depends(get_current_user)):
    """Get performance analytics"""
    try:
        analytics = await progress_service.get_performance_analytics(current_user.id)
        return {"analytics": analytics}
    except Exception as e:
        logger.error(f"Get analytics error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
