from supabase import create_client, Client
from utils.config import SUPABASE_URL, SUPABASE_KEY, SUPABASE_SERVICE_KEY
import logging

logger = logging.getLogger(__name__)

# Client for user operations (with RLS)
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Service client for admin operations (bypasses RLS)
supabase_admin: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

def get_supabase_client() -> Client:
    """Get Supabase client for user operations"""
    return supabase

def get_supabase_admin() -> Client:
    """Get Supabase admin client for service operations"""
    return supabase_admin

async def create_user_record(user_id: str, email: str) -> dict:
    """Create user record in users table"""
    try:
        result = supabase_admin.table("users").insert({
            "id": user_id,
            "email": email
        }).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        logger.error(f"Error creating user record: {e}")
        raise

async def get_user_by_id(user_id: str) -> dict:
    """Get user by ID"""
    try:
        result = supabase.table("users").select("*").eq("id", user_id).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        logger.error(f"Error getting user: {e}")
        raise
