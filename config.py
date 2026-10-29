"""Central configuration loaded from environment / .env file."""
import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    USE_LLM: bool = os.getenv("USE_LLM", "false").lower() == "true"
    CLAUDE_MODEL: str = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-6")

    JWT_SECRET: str = os.getenv("JWT_SECRET", "insecure-dev-secret-change-me")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_EXPIRE_MINUTES: int = int(os.getenv("JWT_EXPIRE_MINUTES", "60"))

    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./rag_app.db")
    DOCUMENTS_DIR: str = os.getenv("DOCUMENTS_DIR", "./data/documents")

    # Retrieval defaults (overridable per-request from the settings drawer)
    DEFAULT_TOP_K: int = int(os.getenv("DEFAULT_TOP_K", "5"))
    DEFAULT_HYBRID_ALPHA: float = float(os.getenv("DEFAULT_HYBRID_ALPHA", "0.5"))
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "800"))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "120"))
    MAX_HISTORY_TURNS: int = int(os.getenv("MAX_HISTORY_TURNS", "6"))

    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")


settings = Settings()

os.makedirs(settings.DOCUMENTS_DIR, exist_ok=True)
