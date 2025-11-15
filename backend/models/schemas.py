from pydantic import BaseModel, Field, validator, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime
import re

def validate_email(email: str) -> str:
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        raise ValueError('Invalid email format')
    return email

def validate_password_strength(password: str) -> str:
    """Validate password meets security requirements"""
    if len(password) < 8:
        raise ValueError('Password must be at least 8 characters long')
    if not re.search(r'[A-Z]', password):
        raise ValueError('Password must contain at least one uppercase letter')
    if not re.search(r'[a-z]', password):
        raise ValueError('Password must contain at least one lowercase letter')
    if not re.search(r'\d', password):
        raise ValueError('Password must contain at least one digit')
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        raise ValueError('Password must contain at least one special character')
    return password

# User Models
class UserCreate(BaseModel):
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, max_length=128, description="User password")
    
    @validator('password')
    def validate_password(cls, v):
        return validate_password_strength(v)
    
    @validator('email')
    def validate_email_format(cls, v):
        # Additional email validation beyond EmailStr
        if len(v) > 254:  # RFC 5321 limit
            raise ValueError('Email address too long')
        return v.lower()

class UserLogin(BaseModel):
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=1, max_length=128, description="User password")
    
    @validator('email')
    def validate_email_format(cls, v):
        return v.lower()

class User(BaseModel):
    id: str
    email: str
    created_at: datetime

# Document Models
class DocumentUpload(BaseModel):
    title: str
    content: str
    topics: List[str]

class Document(BaseModel):
    id: str
    user_id: str
    title: str
    topics: List[str]
    created_at: datetime

# Quiz Models
class QuizRequest(BaseModel):
    topic: str
    difficulty: Optional[str] = "medium"
    num_questions: Optional[int] = 5

class QuizQuestion(BaseModel):
    question: str
    options: List[str]
    correct_answer: int

class Quiz(BaseModel):
    id: str
    questions: List[QuizQuestion]
    topic: str
    difficulty: str

class QuizSubmission(BaseModel):
    quiz_id: str
    answers: List[int]

class QuizResult(BaseModel):
    quiz_id: str
    score: int
    total_questions: int
    percentage: float
    new_difficulty: str

# Tutor Models
class TutorMessage(BaseModel):
    message: str
    session_id: Optional[str] = None

class VoiceTextMessage(BaseModel):
    session_id: str
    message: str

class TutorResponse(BaseModel):
    response: str
    session_id: str
    sources: Optional[List[str]] = None

# Flashcard Models
class FlashcardRequest(BaseModel):
    topic: str
    num_cards: Optional[int] = 10

class Flashcard(BaseModel):
    question: str
    answer: str

class FlashcardSet(BaseModel):
    id: str
    topic: str
    cards: List[Flashcard]

# Progress Models
class ProgressData(BaseModel):
    quiz_scores: List[Dict[str, Any]]
    tutor_sessions: List[Dict[str, Any]]
    topics_studied: List[str]
    total_study_time: int

# Agora Models
class AgoraTokenRequest(BaseModel):
    channel_name: str
    user_id: str
    role: Optional[str] = "publisher"
