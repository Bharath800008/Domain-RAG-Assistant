"""Pydantic request/response schemas."""
from typing import Optional, List
import datetime
from pydantic import BaseModel, EmailStr, Field


# ---------- Auth ----------
class SignupRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    role: Optional[str] = "user"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    email: str
    user_id: str


# ---------- Documents ----------
class DocumentOut(BaseModel):
    id: str
    filename: str
    filetype: str
    status: str
    error_message: Optional[str] = None
    chunk_count: int
    uploaded_at: datetime.datetime

    class Config:
        from_attributes = True


# ---------- Chat ----------
class ChatTurn(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    session_id: str
    query: str
    history: List[ChatTurn] = []
    top_k: int = 5
    hybrid_alpha: float = 0.5


class Citation(BaseModel):
    document_id: str
    document_name: str
    section: Optional[str] = None
    score: float
    text_preview: str


class ChatResponse(BaseModel):
    answer: str
    citations: List[Citation]
    confidence: float
    latency_ms: float


class FeedbackRequest(BaseModel):
    message_id: str
    rating: str  # "up" | "down"


# ---------- Explorer ----------
class ChunkSearchRequest(BaseModel):
    query: str
    top_k: int = 10
    hybrid_alpha: float = 0.5


class ChunkResult(BaseModel):
    chunk_id: str
    document_id: str
    document_name: str
    section: Optional[str]
    text: str
    score: float


# ---------- Settings / Users ----------
class UpdateUserRole(BaseModel):
    role: str


class UserOut(BaseModel):
    id: str
    email: str
    role: str
    created_at: datetime.datetime

    class Config:
        from_attributes = True


class GlobalSettingsRequest(BaseModel):
    default_top_k: Optional[int] = None
    default_hybrid_alpha: Optional[float] = None
    llm_model: Optional[str] = None
