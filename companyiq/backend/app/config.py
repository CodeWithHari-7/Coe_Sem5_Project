"""
CompanyIQ Backend — Application Configuration
Reads all settings from environment variables / .env file.
"""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = "CompanyIQ"
    app_env: str = "development"
    secret_key: str = "change-me"
    access_token_expire_minutes: int = 60
    refresh_token_expire_days: int = 7

    # Database
    database_url: str = "sqlite:///./companyiq.db"

    # Vector DB
    vector_db_type: str = "chroma"
    vector_db_path: str = "./chroma_db"

    # LLM
    llm_provider: str = "openai"
    llm_api_key: str = ""
    model_name: str = "gpt-4o-mini"
    embedding_model: str = "text-embedding-3-small"
    max_tokens: int = 4096
    temperature: float = 0.2

    # Demo Mode
    demo_mode: bool = True

    # Files
    upload_dir: str = "./uploads"
    max_upload_size_mb: int = 50

    # Chunking
    chunk_size: int = 512
    chunk_overlap: int = 64

    # Retrieval
    top_k_chunks: int = 10
    hybrid_alpha: float = 0.7

    # CORS
    frontend_url: str = "http://localhost:5173"

    # Logging
    log_level: str = "INFO"

    # Rate limiting
    rate_limit_per_minute: int = 60

    # Opportunity scoring weights
    score_weight_business_relevance: float = 0.30
    score_weight_recent_activity: float = 0.25
    score_weight_product_fit: float = 0.20
    score_weight_historical_similarity: float = 0.15
    score_weight_evidence_confidence: float = 0.10


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
