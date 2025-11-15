import os
from dotenv import load_dotenv

load_dotenv()

# Supabase Configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

# OpenRouter AI Configuration
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
if not OPENROUTER_API_KEY:
    raise ValueError("OPENROUTER_API_KEY environment variable is required")

# Agora Configuration
AGORA_APP_ID = os.getenv("AGORA_APP_ID")
AGORA_APP_CERTIFICATE = os.getenv("AGORA_APP_CERTIFICATE")

# ChromaDB Configuration
CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", os.path.join(os.path.dirname(os.path.dirname(__file__)), "chroma_db"))

# Flask parsing service
PARSING_SERVICE_URL = os.getenv("PARSING_SERVICE_URL", "http://localhost:5001")

# Audio Services Configuration
AZURE_SPEECH_KEY = os.getenv("AZURE_SPEECH_KEY")
AZURE_SPEECH_REGION = os.getenv("AZURE_SPEECH_REGION", "eastus")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")  # Default voice

# Audio Processing Settings
STT_SERVICE = os.getenv("STT_SERVICE", "elevenlabs")  # elevenlabs, whisper, or azure
TTS_SERVICE = os.getenv("TTS_SERVICE", "elevenlabs")  # elevenlabs, azure, or gtts
AUDIO_SAMPLE_RATE = int(os.getenv("AUDIO_SAMPLE_RATE", "16000"))
AUDIO_CHUNK_SIZE = int(os.getenv("AUDIO_CHUNK_SIZE", "1024"))

# Validate required environment variables
required_vars = [
    "SUPABASE_URL", "SUPABASE_KEY", 
    "AGORA_APP_ID", "AGORA_APP_CERTIFICATE"
]

missing_vars = [var for var in required_vars if not os.getenv(var)]
if missing_vars:
    raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
