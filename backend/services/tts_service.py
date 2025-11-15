import asyncio
import io
import tempfile
import os
from typing import Optional
import logging
from utils.config import (
    TTS_SERVICE, 
    AZURE_SPEECH_KEY, 
    AZURE_SPEECH_REGION,
    ELEVENLABS_API_KEY,
    ELEVENLABS_VOICE_ID
)

logger = logging.getLogger(__name__)

class TTSService:
    """Text-to-Speech service supporting multiple providers"""
    
    def __init__(self):
        self.service = TTS_SERVICE.lower()
        logger.info(f"Initializing TTS service with provider: {self.service}")
        
        if self.service == "elevenlabs" and not ELEVENLABS_API_KEY:
            logger.warning("ElevenLabs API key not configured, falling back to gTTS")
            self.service = "gtts"
        elif self.service == "azure" and not AZURE_SPEECH_KEY:
            logger.warning("Azure Speech key not configured, falling back to gTTS")
            self.service = "gtts"
    
    async def synthesize_speech(self, text: str, voice_id: Optional[str] = None) -> Optional[bytes]:
        """
        Convert text to speech audio
        
        Args:
            text: Text to convert to speech
            voice_id: Optional voice ID (provider-specific)
            
        Returns:
            Audio data as bytes or None if synthesis fails
        """
        try:
            if not text or not text.strip():
                logger.warning("Empty text provided for TTS")
                return None
            
            text = text.strip()
            
            if self.service == "elevenlabs":
                return await self._synthesize_with_elevenlabs(text, voice_id)
            elif self.service == "azure":
                return await self._synthesize_with_azure(text, voice_id)
            elif self.service == "gtts":
                return await self._synthesize_with_gtts(text)
            else:
                logger.error(f"Unsupported TTS service: {self.service}")
                return None
                
        except Exception as e:
            logger.error(f"Error synthesizing speech: {e}")
            return None
    
    async def _synthesize_with_elevenlabs(self, text: str, voice_id: Optional[str] = None) -> Optional[bytes]:
        """Synthesize speech using ElevenLabs"""
        try:
            import requests
            
            # Use provided voice_id or default
            voice = voice_id or ELEVENLABS_VOICE_ID
            
            # ElevenLabs TTS API endpoint
            url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice}"
            
            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": ELEVENLABS_API_KEY
            }
            
            data = {
                "text": text,
                "model_id": "eleven_turbo_v2",  # Free tier compatible model
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.5
                }
            }
            
            logger.info("Sending text to ElevenLabs TTS...")
            response = requests.post(url, json=data, headers=headers, timeout=30)
            
            if response.status_code == 200:
                audio_bytes = response.content
                logger.info(f"ElevenLabs TTS successful: {len(audio_bytes)} bytes")
                return audio_bytes
            else:
                logger.error(f"ElevenLabs TTS API error: {response.status_code} - {response.text}")
                return None
            
        except Exception as e:
            logger.error(f"ElevenLabs TTS error: {e}")
            return None
    
    async def _synthesize_with_azure(self, text: str, voice_id: Optional[str] = None) -> Optional[bytes]:
        """Synthesize speech using Azure Speech Services"""
        try:
            import azure.cognitiveservices.speech as speechsdk
            
            # Configure Azure Speech
            speech_config = speechsdk.SpeechConfig(
                subscription=AZURE_SPEECH_KEY, 
                region=AZURE_SPEECH_REGION
            )
            
            # Set voice (use provided voice_id or default)
            voice_name = voice_id or "en-US-AriaNeural"
            speech_config.speech_synthesis_voice_name = voice_name
            
            # Create synthesizer with in-memory stream
            audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=False)
            synthesizer = speechsdk.SpeechSynthesizer(
                speech_config=speech_config, 
                audio_config=None
            )
            
            # Synthesize speech
            result = synthesizer.speak_text_async(text).get()
            
            if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                logger.info(f"Azure TTS successful: {len(result.audio_data)} bytes")
                return result.audio_data
            elif result.reason == speechsdk.ResultReason.Canceled:
                cancellation_details = result.cancellation_details
                logger.error(f"Azure TTS canceled: {cancellation_details.reason}")
                return None
            else:
                logger.error(f"Azure TTS unexpected result: {result.reason}")
                return None
                
        except Exception as e:
            logger.error(f"Azure TTS error: {e}")
            return None
    
    async def _synthesize_with_gtts(self, text: str) -> Optional[bytes]:
        """Synthesize speech using Google Text-to-Speech (gTTS)"""
        try:
            from gtts import gTTS
            
            # Create gTTS object
            tts = gTTS(text=text, lang='en', slow=False)
            
            # Save to temporary file and read back as bytes
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_file:
                temp_file_path = temp_file.name
            
            try:
                # Save TTS to file
                tts.save(temp_file_path)
                
                # Read file as bytes
                with open(temp_file_path, 'rb') as f:
                    audio_bytes = f.read()
                
                logger.info(f"gTTS successful: {len(audio_bytes)} bytes")
                return audio_bytes
                
            finally:
                # Clean up temporary file
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
                    
        except Exception as e:
            logger.error(f"gTTS error: {e}")
            return None

# Global TTS service instance
tts_service = TTSService()
