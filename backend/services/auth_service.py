from utils.database import get_supabase_client, create_user_record
from models.schemas import UserCreate, UserLogin
import logging

logger = logging.getLogger(__name__)

class AuthService:
    def __init__(self):
        self.supabase = get_supabase_client()
    
    async def signup(self, user_data: UserCreate) -> dict:
        """Register a new user"""
        try:
            # Create user in Supabase Auth (trigger will create user record automatically)
            auth_response = self.supabase.auth.sign_up({
                "email": user_data.email,
                "password": user_data.password
            })
            
            if auth_response.user:
                return {
                    "user": auth_response.user,
                    "session": auth_response.session
                }
            else:
                raise Exception("Failed to create user")
                
        except Exception as e:
            logger.error(f"Signup error: {e}")
            raise
    
    async def login(self, user_data: UserLogin) -> dict:
        """Login user"""
        try:
            auth_response = self.supabase.auth.sign_in_with_password({
                "email": user_data.email,
                "password": user_data.password
            })
            
            if auth_response.user and auth_response.session:
                return {
                    "user": auth_response.user,
                    "session": auth_response.session
                }
            else:
                raise Exception("Invalid credentials")
                
        except Exception as e:
            logger.error(f"Login error: {e}")
            raise
    
    async def logout(self, access_token: str) -> bool:
        """Logout user"""
        try:
            self.supabase.auth.sign_out()
            return True
        except Exception as e:
            logger.error(f"Logout error: {e}")
            raise
    
    async def get_user_from_token(self, access_token: str) -> dict:
        """Get user from access token"""
        try:
            user_response = self.supabase.auth.get_user(access_token)
            return user_response.user
        except Exception as e:
            logger.error(f"Token validation error: {e}")
            raise

auth_service = AuthService()
