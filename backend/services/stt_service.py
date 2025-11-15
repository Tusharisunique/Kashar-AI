import asyncio
import io
import tempfile
import os
from typing import Optional
import logging
from utils.config import STT_SERVICE, AZURE_SPEECH_KEY, AZURE_SPEECH_REGION, ELEVENLABS_API_KEY

logger = logging.getLogger(__name__)

class STTService:
    """Speech-to-Text service supporting multiple providers"""
    
    def __init__(self):
        self.service = STT_SERVICE.lower()
        logger.info(f"Initializing STT service with provider: {self.service}")
        
        if self.service == "elevenlabs" and not ELEVENLABS_API_KEY:
            logger.warning("ElevenLabs API key not configured, falling back to Whisper")
            self.service = "whisper"
        elif self.service == "azure" and not AZURE_SPEECH_KEY:
            logger.warning("Azure Speech key not configured, falling back to Whisper")
            self.service = "whisper"
    
    async def transcribe_audio(self, audio_data: bytes, audio_format: str = "wav") -> Optional[str]:
        """
        Transcribe audio data to text
        
        Args:
            audio_data: Raw audio bytes
            audio_format: Audio format (wav, mp3, etc.)
            
        Returns:
            Transcribed text or None if transcription fails
        """
        try:
            if self.service == "elevenlabs":
                return await self._transcribe_with_elevenlabs(audio_data, audio_format)
            elif self.service == "whisper":
                return await self._transcribe_with_whisper(audio_data, audio_format)
            elif self.service == "azure":
                return await self._transcribe_with_azure(audio_data, audio_format)
            else:
                logger.error(f"Unsupported STT service: {self.service}")
                return None
                
        except Exception as e:
            logger.error(f"Error transcribing audio: {e}")
            return None
    
    async def _transcribe_with_whisper(self, audio_data: bytes, audio_format: str) -> Optional[str]:
        """Transcribe using OpenAI Whisper"""
        try:
            import whisper
            
            # Save audio data to temporary file
            with tempfile.NamedTemporaryFile(suffix=f".{audio_format}", delete=False) as temp_file:
                temp_file.write(audio_data)
                temp_file_path = temp_file.name
            
            try:
                # Load Whisper model (using base model for balance of speed/accuracy)
                model = whisper.load_model("base")
                
                # Transcribe audio
                result = model.transcribe(temp_file_path)
                text = result["text"].strip()
                
                logger.info(f"Whisper transcription successful: {len(text)} characters")
                return text if text else None
                
            finally:
                # Clean up temporary file
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
                    
        except Exception as e:
            logger.error(f"Whisper transcription error: {e}")
            return None
    
    async def _transcribe_with_azure(self, audio_data: bytes, audio_format: str) -> Optional[str]:
        """Transcribe using Azure Speech Services"""
        try:
            import azure.cognitiveservices.speech as speechsdk
            
            # Configure Azure Speech
            speech_config = speechsdk.SpeechConfig(
                subscription=AZURE_SPEECH_KEY, 
                region=AZURE_SPEECH_REGION
            )
            speech_config.speech_recognition_language = "en-US"
            
            # Create audio stream from bytes
            audio_stream = speechsdk.audio.PushAudioInputStream()
            audio_config = speechsdk.audio.AudioConfig(stream=audio_stream)
            
            # Create speech recognizer
            speech_recognizer = speechsdk.SpeechRecognizer(
                speech_config=speech_config, 
                audio_config=audio_config
            )
            
            # Push audio data to stream
            audio_stream.write(audio_data)
            audio_stream.close()
            
            # Perform recognition
            result = speech_recognizer.recognize_once()
            
            if result.reason == speechsdk.ResultReason.RecognizedSpeech:
                logger.info(f"Azure STT transcription successful: {len(result.text)} characters")
                return result.text.strip() if result.text.strip() else None
            elif result.reason == speechsdk.ResultReason.NoMatch:
                logger.warning("Azure STT: No speech could be recognized")
                return None
            elif result.reason == speechsdk.ResultReason.Canceled:
                cancellation_details = result.cancellation_details
                logger.error(f"Azure STT canceled: {cancellation_details.reason}")
                return None
            else:
                logger.error(f"Azure STT unexpected result: {result.reason}")
                return None
                
        except Exception as e:
            logger.error(f"Azure STT error: {e}")
            return None
    
    async def _transcribe_with_elevenlabs(self, audio_data: bytes, audio_format: str) -> Optional[str]:
        """Transcribe using ElevenLabs Speech-to-Text"""
        try:
            import requests
            
            # ElevenLabs STT API endpoint
            url = "https://api.elevenlabs.io/v1/speech-to-text"
            
            headers = {
                "xi-api-key": ELEVENLABS_API_KEY
            }
            
            # Prepare audio file for upload - ElevenLabs expects 'file' parameter
            files = {
                "file": (f"audio.{audio_format}", io.BytesIO(audio_data), f"audio/{audio_format}")
            }
            
            # Optional parameters for better transcription
            data = {
                "model_id": "scribe_v2",  # ElevenLabs STT model
                "language": "en"          # Language parameter
            }
            
            logger.info("Sending audio to ElevenLabs STT...")
            response = requests.post(url, headers=headers, files=files, data=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                text = result.get("text", "").strip()
                
                if text:
                    logger.info(f"ElevenLabs STT transcription successful: {len(text)} characters")
                    return text
                else:
                    logger.warning("ElevenLabs STT returned empty transcription")
                    return None
            else:
                logger.error(f"ElevenLabs STT API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"ElevenLabs STT error: {e}")
            return None

# Global STT service instance
stt_service = STTService()
