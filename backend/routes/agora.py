from fastapi import APIRouter, HTTPException, Depends
from routes.auth import get_current_user
from services.agora_service import agora_service
from models.schemas import AgoraTokenRequest
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/agora", tags=["agora"])

@router.post("/tokens")
async def generate_tokens(
    request: AgoraTokenRequest,
    current_user = Depends(get_current_user)
):
    """Generate Agora RTC and RTM tokens"""
    try:
        # Use authenticated user ID
        request.user_id = current_user.id
        
        tokens = agora_service.generate_tokens(request)
        return {"tokens": tokens}
        
    except Exception as e:
        logger.error(f"Generate tokens error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/rtc-token")
async def generate_rtc_token(
    channel_name: str,
    role: str = "publisher",
    current_user = Depends(get_current_user)
):
    """Generate RTC token for voice communication"""
    try:
        token = agora_service.generate_rtc_token(channel_name, current_user.id, role)
        return {
            "rtc_token": token,
            "app_id": agora_service.app_id,
            "channel_name": channel_name,
            "user_id": current_user.id
        }
    except Exception as e:
        logger.error(f"Generate RTC token error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/rtm-token")
async def generate_rtm_token(current_user = Depends(get_current_user)):
    """Generate RTM token for messaging"""
    try:
        token = agora_service.generate_rtm_token(current_user.id)
        return {
            "rtm_token": token,
            "app_id": agora_service.app_id,
            "user_id": current_user.id
        }
    except Exception as e:
        logger.error(f"Generate RTM token error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
