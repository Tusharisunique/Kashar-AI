from fastapi import APIRouter, HTTPException, Depends, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from models.schemas import UserCreate, UserLogin, User
from services.auth_service import auth_service
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/auth", tags=["authentication"])
security = HTTPBearer()

@router.get("/test")
async def test_endpoint():
    """Test endpoint to verify API is working"""
    try:
        # Test Supabase connection
        from utils.database import get_supabase_client
        supabase = get_supabase_client()
        # Simple test query
        result = supabase.table('users').select('*').limit(1).execute()
        return {
            "status": "API is working", 
            "message": "Authentication routes are accessible",
            "supabase_connected": True,
            "test_query_success": True
        }
    except Exception as e:
        return {
            "status": "API is working", 
            "message": "Authentication routes are accessible",
            "supabase_connected": False,
            "error": str(e)
        }

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Dependency to get current authenticated user"""
    try:
        # Validate token format
        token = credentials.credentials
        if not token or len(token) < 10:
            raise HTTPException(status_code=401, detail="Invalid authentication token format")
        
        # Get user from token
        user = await auth_service.get_user_from_token(token)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid authentication token")
            
        return user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        raise HTTPException(status_code=401, detail="Authentication failed")

@router.post("/signup")
async def signup(user_data: UserCreate):
    """Register a new user"""
    try:
        result = await auth_service.signup(user_data)
        return {
            "message": "User created successfully",
            "user": {
                "id": result["user"].id,
                "email": result["user"].email
            },
            "access_token": result["session"].access_token if result["session"] else None,
            "refresh_token": result["session"].refresh_token if result["session"] else None
        }
    except Exception as e:
        logger.error(f"Signup endpoint error: {e}")
        error_msg = str(e)
        if "Email address" in error_msg and "invalid" in error_msg:
            raise HTTPException(status_code=400, detail=f"Email validation failed: {error_msg}")
        raise HTTPException(status_code=400, detail=f"Signup failed: {error_msg}")

@router.post("/login")
async def login(user_data: UserLogin):
    """Login user"""
    try:
        result = await auth_service.login(user_data)
        return {
            "message": "Login successful",
            "user": {
                "id": result["user"].id,
                "email": result["user"].email
            },
            "access_token": result["session"].access_token,
            "refresh_token": result["session"].refresh_token
        }
    except Exception as e:
        logger.error(f"Login endpoint error: {e}")
        raise HTTPException(status_code=401, detail="Invalid credentials")

@router.post("/logout")
async def logout(current_user = Depends(get_current_user)):
    """Logout user"""
    try:
        await auth_service.logout("")
        return {"message": "Logout successful"}
    except Exception as e:
        logger.error(f"Logout endpoint error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/me")
async def get_current_user_info(current_user = Depends(get_current_user)):
    """Get current user information"""
    return {
        "user": {
            "id": current_user.id,
            "email": current_user.email
        }
    }
