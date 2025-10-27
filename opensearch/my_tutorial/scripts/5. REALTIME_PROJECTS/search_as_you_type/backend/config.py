"""Configuration settings for the application."""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # OpenSearch Configuration
    opensearch_host: str = "https://localhost:9200"
    opensearch_username: str = "admin"
    opensearch_password: str = "Developer@123"
    opensearch_index: str = "ecommerce"
    opensearch_verify_ssl: bool = False
    
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    # Frontend Configuration (not used by backend, but allowed in .env)
    api_base_url: str = "http://127.0.0.1:8000"
    streamlit_port: int = 8501
    gradio_port: int = 7860
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"  # Ignore extra fields in .env


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
