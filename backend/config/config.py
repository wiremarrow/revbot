"""
Configuration management for RevBot backend.
"""
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    """Application settings with validation."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # API Configuration
    app_name: str = "RevBot"
    api_version: str = "v1"
    debug: bool = Field(default=False, description="Debug mode")
    
    # Anthropic Configuration
    anthropic_api_key: str = Field(..., description="Anthropic API key")
    claude_model: str = Field(
        default="claude-3-5-sonnet-20241022",
        description="Claude model to use"
    )
    claude_max_tokens: int = Field(
        default=4096,
        description="Maximum tokens for Claude responses"
    )
    
    # pyRevit Configuration
    pyrevit_port: Optional[int] = Field(
        default=None,
        description="Port for pyRevit communication (None = CLI mode)"
    )
    pyrevit_timeout: int = Field(
        default=30,
        description="Timeout for pyRevit execution in seconds"
    )
    
    # Server Configuration
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, description="Server port")
    reload: bool = Field(default=True, description="Auto-reload on code changes")
    
    # Security
    cors_origins: list[str] = Field(
        default=["http://localhost:3000", "http://localhost:5173"],
        description="Allowed CORS origins"
    )
    
    # Logging
    log_level: str = Field(default="INFO", description="Logging level")
    log_format: str = Field(default="json", description="Log format (json or text)")


# Singleton instance
settings = Settings()