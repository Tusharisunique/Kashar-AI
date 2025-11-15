from agora_token_builder import RtcTokenBuilder, RtmTokenBuilder
from utils.config import AGORA_APP_ID, AGORA_APP_CERTIFICATE
from models.schemas import AgoraTokenRequest
import time
import logging

logger = logging.getLogger(__name__)

class AgoraService:
    def __init__(self):
        self.app_id = AGORA_APP_ID
        self.app_certificate = AGORA_APP_CERTIFICATE
        self.token_expiration = 3600  # 1 hour
    
    def generate_rtc_token(self, channel_name: str, user_id: str, role: str = "publisher") -> str:
        """Generate RTC token for voice communication"""
        try:
            # Set role (using integer values for Agora roles)
            if role == "publisher":
                role_value = 1  # Publisher role
            else:
                role_value = 2  # Subscriber role
            
            # Calculate expiration time
            current_timestamp = int(time.time())
            privilege_expired_ts = current_timestamp + self.token_expiration
            
            # Generate token with consistent user ID handling
            # Convert user_id to integer for Agora token generation
            if isinstance(user_id, str):
                if user_id.isdigit():
                    uid = int(user_id)
                else:
                    # Create a consistent hash for string user IDs
                    uid = abs(hash(user_id)) % (2**31)  # Use 31 bits to avoid negative numbers
            else:
                uid = int(user_id)
            
            token = RtcTokenBuilder.buildTokenWithUid(
                self.app_id,
                self.app_certificate,
                channel_name,
                uid,
                role_value,
                privilege_expired_ts
            )
            
            logger.info(f"Generated RTC token for channel: {channel_name}, user: {user_id} (uid: {uid})")
            return token
            
        except Exception as e:
            logger.error(f"Error generating RTC token: {e}")
            raise
    
    def generate_rtm_token(self, user_id: str) -> str:
        """Generate RTM token for messaging"""
        try:
            # Calculate expiration time
            current_timestamp = int(time.time())
            privilege_expired_ts = current_timestamp + self.token_expiration
            
            # Generate token
            token = RtmTokenBuilder.buildToken(
                self.app_id,
                self.app_certificate,
                user_id,
                1,  # RTM User role
                privilege_expired_ts
            )
            
            logger.info(f"Generated RTM token for user: {user_id}")
            return token
            
        except Exception as e:
            logger.error(f"Error generating RTM token: {e}")
            raise
    
    def generate_tokens(self, request: AgoraTokenRequest) -> dict:
        """Generate both RTC and RTM tokens"""
        try:
            # Calculate the UID that will be used for token generation
            user_id = request.user_id
            if isinstance(user_id, str):
                if user_id.isdigit():
                    uid = int(user_id)
                else:
                    uid = abs(hash(user_id)) % (2**31)
            else:
                uid = int(user_id)
            
            rtc_token = self.generate_rtc_token(
                request.channel_name,
                request.user_id,
                request.role
            )
            
            rtm_token = self.generate_rtm_token(request.user_id)
            
            return {
                "rtc_token": rtc_token,
                "rtm_token": rtm_token,
                "app_id": self.app_id,
                "channel_name": request.channel_name,
                "user_id": request.user_id,
                "user_uid": uid,  # Include the actual UID used for token generation
                "expires_at": int(time.time()) + self.token_expiration
            }
            
        except Exception as e:
            logger.error(f"Error generating tokens: {e}")
            raise

agora_service = AgoraService()
