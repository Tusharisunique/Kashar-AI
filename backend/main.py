from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from dotenv import load_dotenv
import os
import logging

from routes import auth, documents, tutor, quiz, flashcards, progress, agora, agora_voice

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Kashar AI Backend", 
    version="1.0.0",
    docs_url="/docs" if os.getenv("ENVIRONMENT") != "production" else None,
    redoc_url="/redoc" if os.getenv("ENVIRONMENT") != "production" else None
)

# Security middleware
allowed_hosts_env = os.getenv("ALLOWED_HOSTS")
if allowed_hosts_env:
    allowed_hosts = [h.strip() for h in allowed_hosts_env.split(",") if h.strip()]
else:
    allowed_hosts = ["localhost", "127.0.0.1", "*.kashar-ai.com"]

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=allowed_hosts
)

# CORS middleware with security considerations
cors_origins_env = os.getenv("CORS_ORIGINS")
if cors_origins_env:
    cors_origins = [o.strip() for o in cors_origins_env.split(",") if o.strip()]
else:
    cors_origins = [
        # Local development
        "http://localhost:3000",
        "https://localhost:3000",
        
        # Vercel preview deployments (your-app-name.vercel.app)
        "https://*.vercel.app",
        
        # Vercel production deployment (your-custom-domain.com)
        # Add your production domain here or via CORS_ORIGINS env var
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Security headers middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    
    # Security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'"
    
    # HSTS header for HTTPS
    if request.url.scheme == "https":
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    
    return response

# Global exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.warning(f"HTTP {exc.status_code} error on {request.url}: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "status_code": exc.status_code}
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning(f"Validation error on {request.url}: {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content={
            "detail": "Validation error",
            "errors": exc.errors()
        }
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception on {request.url}: {exc}", exc_info=True)
    
    # Don't expose internal errors in production
    if os.getenv("ENVIRONMENT") == "production":
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"}
        )
    else:
        return JSONResponse(
            status_code=500,
            content={"detail": str(exc)}
        )

# Include routers
app.include_router(auth.router, tags=["Authentication"])
app.include_router(documents.router, tags=["Documents"])
app.include_router(tutor.router, tags=["Tutor"])
app.include_router(quiz.router, tags=["Quiz"])
app.include_router(flashcards.router, tags=["Flashcards"])
app.include_router(progress.router, tags=["Progress"])
app.include_router(agora.router, tags=["Agora"])
app.include_router(agora_voice.router, tags=["Agora Voice"])

@app.get("/")
async def root():
    return {"message": "Kashar AI Backend API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
