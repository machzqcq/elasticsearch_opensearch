"""Configuration management for OpenSearch MCP Server App."""

import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field, validator


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # OpenSearch Configuration
    opensearch_url: str = Field(
        default="https://localhost:9200",
        description="OpenSearch cluster endpoint"
    )
    opensearch_username: str = Field(
        default="admin",
        description="OpenSearch username"
    )
    opensearch_password: str = Field(
        default="Developer@123",
        description="OpenSearch password"
    )
    opensearch_ssl_verify: str = Field(
        default="false",
        description="Verify SSL certificates"
    )
    
    # OpenAI Configuration
    openai_api_key: str = Field(
        ...,
        description="OpenAI API key for GPT-4"
    )
    openai_model: str = Field(
        default="gpt-4o",
        description="OpenAI model to use"
    )
    
    # MCP Server Configuration
    mcp_server_url: str = Field(
        default="http://localhost:9900/sse",
        description="MCP server SSE endpoint"
    )
    mcp_server_port: int = Field(
        default=9900,
        description="MCP server port"
    )
    
    # Application Configuration
    app_title: str = Field(
        default="OpenSearch MCP Server - Educational Demo",
        description="Application title"
    )
    app_port: int = Field(
        default=7860,
        description="Gradio app port"
    )
    app_share: bool = Field(
        default=False,
        description="Create public Gradio link"
    )
    
    # Feature Flags
    verbose_mode: bool = Field(
        default=True,
        description="Show agent reasoning process"
    )
    show_query_details: bool = Field(
        default=True,
        description="Display generated queries"
    )
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
    
    @validator("opensearch_ssl_verify")
    def parse_ssl_verify(cls, v):
        """Convert string to boolean."""
        if isinstance(v, str):
            return v.lower() in ("true", "1", "yes")
        return v
    
    def get_opensearch_env(self) -> dict:
        """Get environment variables for OpenSearch."""
        return {
            "OPENSEARCH_URL": self.opensearch_url,
            "OPENSEARCH_USERNAME": self.opensearch_username,
            "OPENSEARCH_PASSWORD": self.opensearch_password,
            "OPENSEARCH_SSL_VERIFY": str(self.opensearch_ssl_verify).lower(),
        }
    
    def get_openai_env(self) -> dict:
        """Get environment variables for OpenAI."""
        return {
            "OPENAI_API_KEY": self.openai_api_key,
        }


# Global settings instance
settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get or create settings instance."""
    global settings
    if settings is None:
        settings = Settings()
    return settings


def initialize_settings():
    """Initialize and validate settings."""
    global settings
    settings = Settings()
    
    # Set environment variables
    os.environ.update(settings.get_opensearch_env())
    os.environ.update(settings.get_openai_env())
    
    return settings
