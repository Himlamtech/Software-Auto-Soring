"""Application settings using Pydantic v2."""

from typing import Optional, List, Dict, Any
from pydantic import BaseSettings, Field, validator
from functools import lru_cache
from dotenv import load_dotenv
import os

load_dotenv()


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Application
    app_name: str = Field(default="UML Auto Scoring AI", description="Application name")
    app_version: str = Field(default="0.1.0", description="Application version")
    debug: bool = Field(default=False, description="Debug mode")
    
    # API Configuration
    api_host: str = Field(default="0.0.0.0", description="API host")
    api_port: int = Field(default=2012, description="API port")
    api_workers: int = Field(default=1, description="Number of API workers")
    cors_origins: List[str] = Field(default=["*"], description="CORS allowed origins")
    
    # Storage Configuration
    storage_path: str = Field(default="./data", description="Base path for file storage")
    max_file_size: int = Field(default=10485760, description="Maximum file size in bytes (10MB)")
    allowed_file_extensions: List[str] = Field(
        default=[".puml", ".txt", ".plantuml"],
        description="Allowed file extensions for uploads"
    )
    
    # Openai Configuration
    openai_api_key: os.getenv("OPENAI_API_KEY") = Field(default=None, description="OpenAI API key")
    llm_model: str = Field(default="gpt-4.1-nano", description="LLM model to use")
    llm_temperature: Optional[float] = Field(default=0.1, description="LLM temperature for extraction")
    llm_max_tokens: Optional[int] = Field(default=2000, description="Maximum tokens for LLM responses")
    llm_timeout: Optional[int] = Field(default=60, description="LLM request timeout in seconds")
    
    # Gemini Configuration
    gemini_api_key: os.getenv("GEMINI_API_KEY") = Field(default=None, description="Gemini API key")
    gemini_model: str = Field(default="gemini-2.5-flash", description="Gemini model to use")
    gemini_temperature: Optional[float] = Field(default=0.1, description="Gemini temperature for extraction")
    gemini_max_tokens: Optional[int] = Field(default=2000, description="Maximum tokens for Gemini responses")
    gemini_timeout: Optional[int] = Field(default=60, description="Gemini request timeout in seconds")
    
    # Scoring Configuration
    default_actor_weight: float = Field(default=0.3, description="Default weight for actor scoring")
    default_usecase_weight: float = Field(default=0.5, description="Default weight for use case scoring")
    default_relationship_weight: float = Field(default=0.2, description="Default weight for relationship scoring")
    similarity_threshold: float = Field(default=0.8, description="Similarity threshold for component matching")
    
    # PlantUML Configuration
    plantuml_jar_path: Optional[str] = Field(default=None, description="Path to plantuml.jar file")
    use_online_plantuml: bool = Field(default=False, description="Use online PlantUML service")
    plantuml_online_url: str = Field(
        default="http://www.plantuml.com/plantuml",
        description="Online PlantUML service URL"
    )
    
    # Processing Configuration
    max_concurrent_requests: int = Field(default=10, description="Maximum concurrent scoring requests")
    request_timeout: int = Field(default=300, description="Request timeout in seconds")
    batch_size: int = Field(default=50, description="Maximum batch size for batch processing")
    
    # Logging Configuration
    log_level: str = Field(default="INFO", description="Logging level")
    log_file: Optional[str] = Field(default=None, description="Log file path")
    log_rotation: str = Field(default="1 day", description="Log rotation schedule")
    log_retention: str = Field(default="30 days", description="Log retention period")
    
    # Security Configuration
    api_key_header: str = Field(default="X-API-Key", description="API key header name")
    rate_limit_requests: int = Field(default=100, description="Rate limit requests per minute")
    rate_limit_window: int = Field(default=60, description="Rate limit window in seconds")
    
    # Cache Configuration
    cache_enabled: bool = Field(default=True, description="Enable caching")
    cache_ttl: int = Field(default=3600, description="Cache TTL in seconds")
    cache_max_size: int = Field(default=1000, description="Maximum cache size")
    
    # Analytics Configuration
    enable_analytics: bool = Field(default=True, description="Enable analytics tracking")
    analytics_retention_days: int = Field(default=90, description="Analytics data retention in days")
    
    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"
    
    @validator("llm_temperature")
    def validate_temperature(cls, v):
        """Validate LLM temperature is in valid range."""
        if not 0.0 <= v <= 2.0:
            raise ValueError("LLM temperature must be between 0.0 and 2.0")
        return v
    
    @validator("similarity_threshold")
    def validate_similarity_threshold(cls, v):
        """Validate similarity threshold is in valid range."""
        if not 0.0 <= v <= 1.0:
            raise ValueError("Similarity threshold must be between 0.0 and 1.0")
        return v
    
    @validator("default_actor_weight", "default_usecase_weight", "default_relationship_weight")
    def validate_weights(cls, v):
        """Validate weights are positive."""
        if v < 0.0:
            raise ValueError("Weights must be non-negative")
        return v
    
    @validator("log_level")
    def validate_log_level(cls, v):
        """Validate log level is valid."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"Log level must be one of: {valid_levels}")
        return v.upper()
    
    def get_scoring_weights(self) -> Dict[str, float]:
        """Get scoring weights as dictionary."""
        return {
            "actor": self.default_actor_weight,
            "use_case": self.default_usecase_weight,
            "relationship": self.default_relationship_weight
        }
    
    def get_openai_config(self) -> Dict[str, Any]:
        """Get LLM configuration as dictionary."""
        return {
            "api_key": self.openai_api_key,
            "model": self.llm_model,
            "temperature": self.llm_temperature,
            "max_tokens": self.llm_max_tokens,
            "timeout": self.llm_timeout
        }
    
    def get_gemini_config(self) -> Dict[str, Any]:
        """Get Gemini configuration as dictionary."""
        return {
            "api_key": self.gemini_api_key,
            "model": self.gemini_model,
            "temperature": self.gemini_temperature,
            "max_tokens": self.gemini_max_tokens,
            "timeout": self.gemini_timeout
        }
    
    def get_storage_config(self) -> Dict[str, Any]:
        """Get storage configuration as dictionary."""
        return {
            "base_path": self.storage_path,
            "max_file_size": self.max_file_size,
            "allowed_extensions": self.allowed_file_extensions
        }


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached application settings.
    
    Returns:
        Application settings instance
    """
    return Settings()
