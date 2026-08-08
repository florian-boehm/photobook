"""Application configuration using Pydantic Settings."""

from pathlib import Path
from typing import Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )
    
    # Application settings
    app_name: str = "Photobook"
    app_version: str = "0.1.0"
    debug: bool = False
    
    # Server settings
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Media directory settings
    media_root_path: Path = Field(
        default=Path("/media"),
        description="Root directory containing all media files",
    )
    
    # Mapping file settings
    mapping_file_path: Path = Field(
        default=Path("/data/mapping.json"),
        description="Path to the JSON mapping file for album/file to path resolution",
    )
    
    # Streaming settings
    chunk_size: int = 8192  # 8KB chunks for streaming
    max_chunk_size: int = 1048576  # 1MB max chunk size
    
    # CORS settings (for future GUI)
    cors_origins: str = "*"
    
    @field_validator("media_root_path", mode="before")
    @classmethod
    def validate_media_root_path(cls, v):
        """Convert string to Path and ensure it exists."""
        path = Path(v) if isinstance(v, str) else v
        return path
    
    @field_validator("mapping_file_path", mode="before")
    @classmethod
    def validate_mapping_file_path(cls, v):
        """Convert string to Path."""
        path = Path(v) if isinstance(v, str) else v
        return path


# Global settings instance
settings = Settings()
