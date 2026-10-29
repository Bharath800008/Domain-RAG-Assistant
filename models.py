"""SQLAlchemy ORM models."""
import datetime
import uuid

from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, ForeignKey, Text
)
from sqlalchemy.orm import relationship

from database import Base


def gen_id():
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=gen_id)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="user")  # "admin" | "user"
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class Document(Base):
    __tablename__ = "documents"

    id = Column(String, primary_key=True, default=gen_id)
    filename = Column(String, nullable=False)
    filepath = Column(String, nullable=False)
    filetype = Column(String, nullable=False)
    status = Column(String, default="processing")  # processing | indexed | failed
    error_message = Column(String, nullable=True)
    chunk_count = Column(Integer, default=0)
    uploaded_by = Column(String, ForeignKey("users.id"), nullable=True)
    uploaded_at = Column(DateTime, default=datetime.datetime.utcnow)

    chunks = relationship("Chunk", back_populates="document", cascade="all, delete-orphan")


class Chunk(Base):
    __tablename__ = "chunks"

    id = Column(String, primary_key=True, default=gen_id)
    document_id = Column(String, ForeignKey("documents.id"), nullable=False)
    section = Column(String, nullable=True)
    text = Column(Text, nullable=False)
    chunk_index = Column(Integer, default=0)
    vector_row = Column(Integer, nullable=True)  # row index inside the FAISS index

    document = relationship("Document", back_populates="chunks")


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(String, primary_key=True, default=gen_id)
    session_id = Column(String, index=True, nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=True)
    role = Column(String, nullable=False)  # "user" | "assistant"
    content = Column(Text, nullable=False)
    citations_json = Column(Text, nullable=True)  # JSON string of citation list
    confidence = Column(Float, nullable=True)
    latency_ms = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(String, primary_key=True, default=gen_id)
    message_id = Column(String, ForeignKey("chat_messages.id"), nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=True)
    rating = Column(String, nullable=False)  # "up" | "down"
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class QueryLog(Base):
    __tablename__ = "query_logs"

    id = Column(String, primary_key=True, default=gen_id)
    user_id = Column(String, ForeignKey("users.id"), nullable=True)
    query = Column(Text, nullable=False)
    top_k = Column(Integer, default=5)
    hybrid_alpha = Column(Float, default=0.5)
    latency_ms = Column(Float, nullable=True)
    faithfulness_score = Column(Float, nullable=True)
    retrieved_doc_ids = Column(Text, nullable=True)  # comma-separated document ids
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
