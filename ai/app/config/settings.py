"""Application settings using Pydantic v2."""

from typing import Optional, List, Dict, Any
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings
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
    api_port: int = Field(default=8000, description="API port")
    api_workers: int = Field(default=1, description="Number of API workers")
    cors_origins: List[str] = Field(default=["*"], description="CORS allowed origins")
    
    # Storage Configuration
    storage_path: str = Field(default="./data", description="Base path for file storage")
    max_file_size: int = Field(default=10485760, description="Maximum file size in bytes (10MB)")
    allowed_file_extensions: List[str] = Field(
        default=[".puml", ".txt", ".plantuml"],
        description="Allowed file extensions for uploads"
    )
    
    # OpenAI Configuration
    openai_api_key: Optional[str] = Field(default=None, description="OpenAI API key")
    llm_model: str = Field(default="gpt-4o-mini", description="LLM model to use")
    llm_temperature: float = Field(default=0.1, description="LLM temperature for extraction")
    llm_max_tokens: int = Field(default=2000, description="Maximum tokens for LLM responses")
    llm_timeout: int = Field(default=60, description="LLM request timeout in seconds")
    
    # Gemini Configuration
    gemini_api_key: Optional[str] = Field(default=None, description="Gemini API key")
    gemini_model: str = Field(default="gemini-2.5-flash-lite", description="Gemini model to use")
    gemini_temperature: float = Field(default=0.1, description="Gemini temperature for extraction")
    gemini_max_tokens: int = Field(default=4096, description="Maximum tokens for Gemini responses")
    gemini_timeout: int = Field(default=60, description="Gemini request timeout in seconds")
    gemini_rate_limit_rpm: int = Field(default=15, description="Gemini rate limit requests per minute (free tier)")

    # 3-Phase Pipeline Configuration
    # Phase 1: Convention Normalization
    normalization_max_retries: int = Field(default=3, description="Max retries for normalization chain")
    normalization_temperature: float = Field(default=0.1, description="Temperature for convention normalization")

    # Phase 2: Code-based Extraction
    enable_semantic_matching: bool = Field(default=True, description="Enable semantic component matching")
    component_similarity_threshold: float = Field(default=0.85, description="Threshold for component similarity matching")

    # Phase 3: Feedback Generation
    feedback_temperature: float = Field(default=0.3, description="Temperature for feedback generation (higher for creativity)")
    max_feedback_items: int = Field(default=10, description="Maximum number of feedback items to generate")

    # Multi-diagram Support
    supported_diagram_types: List[str] = Field(
        default=["use_case", "class", "sequence"],
        description="Supported UML diagram types"
    )

    # Scoring Weights by Diagram Type
    use_case_weights: Dict[str, float] = Field(
        default={"actor": 0.3, "use_case": 0.5, "relationship": 0.2},
        description="Component weights for use case diagrams"
    )
    class_diagram_weights: Dict[str, float] = Field(
        default={"class": 0.4, "attribute": 0.3, "method": 0.2, "relationship": 0.1},
        description="Component weights for class diagrams"
    )
    sequence_diagram_weights: Dict[str, float] = Field(
        default={"participant": 0.3, "message": 0.5, "activation": 0.2},
        description="Component weights for sequence diagrams"
    )
    
    # LLM Provider Selection
    llm_provider: str = Field(default="gemini", description="LLM provider to use (openai, gemini)")
    
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
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "ignore"
    }
    
    @field_validator("llm_temperature", "gemini_temperature", "normalization_temperature", "feedback_temperature")
    @classmethod
    def validate_temperature(cls, v):
        """Validate LLM temperature is in valid range."""
        if v is not None and not 0.0 <= v <= 2.0:
            raise ValueError("LLM temperature must be between 0.0 and 2.0")
        return v
    
    @field_validator("llm_provider")
    @classmethod
    def validate_llm_provider(cls, v):
        """Validate LLM provider."""
        valid_providers = ["openai", "gemini"]
        if v.lower() not in valid_providers:
            raise ValueError(f"LLM provider must be one of: {valid_providers}")
        return v.lower()
    
    @field_validator("similarity_threshold", "component_similarity_threshold")
    @classmethod
    def validate_similarity_threshold(cls, v):
        """Validate similarity threshold is in valid range."""
        if not 0.0 <= v <= 1.0:
            raise ValueError("Similarity threshold must be between 0.0 and 1.0")
        return v

    @field_validator("supported_diagram_types")
    @classmethod
    def validate_diagram_types(cls, v):
        """Validate supported diagram types."""
        valid_types = ["use_case", "class", "sequence"]
        for diagram_type in v:
            if diagram_type not in valid_types:
                raise ValueError(f"Unsupported diagram type: {diagram_type}. Valid types: {valid_types}")
        return v
    
    @field_validator("default_actor_weight", "default_usecase_weight", "default_relationship_weight")
    @classmethod
    def validate_weights(cls, v):
        """Validate weights are positive."""
        if v < 0.0:
            raise ValueError("Weights must be non-negative")
        return v
    
    @field_validator("log_level")
    @classmethod
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
    
    def get_active_llm_config(self) -> Dict[str, Any]:
        """Get configuration for the currently selected LLM provider."""
        if self.llm_provider == "openai":
            return self.get_openai_config()
        elif self.llm_provider == "gemini":
            return self.get_gemini_config()
        else:
            raise ValueError(f"Unknown LLM provider: {self.llm_provider}")
    
    def get_llm_config(self) -> Dict[str, Any]:
        """Backward compatibility method for get_active_llm_config."""
        return self.get_active_llm_config()
    
    def get_storage_config(self) -> Dict[str, Any]:
        """Get storage configuration as dictionary."""
        return {
            "base_path": self.storage_path,
            "max_file_size": self.max_file_size,
            "allowed_extensions": self.allowed_file_extensions
        }

    def get_diagram_weights(self, diagram_type: str) -> Dict[str, float]:
        """Get scoring weights for specific diagram type."""
        weights_map = {
            "use_case": self.use_case_weights,
            "class": self.class_diagram_weights,
            "sequence": self.sequence_diagram_weights
        }
        return weights_map.get(diagram_type, self.use_case_weights)

    def get_phase_one_config(self) -> Dict[str, Any]:
        """Get Phase 1 (Convention Normalization) configuration."""
        return {
            "max_retries": self.normalization_max_retries,
            "temperature": self.normalization_temperature,
            "model": self.gemini_model,
            "rate_limit_rpm": self.gemini_rate_limit_rpm
        }

    def get_phase_two_config(self) -> Dict[str, Any]:
        """Get Phase 2 (Code-based Extraction) configuration."""
        return {
            "enable_semantic_matching": self.enable_semantic_matching,
            "similarity_threshold": self.component_similarity_threshold,
            "supported_diagrams": self.supported_diagram_types
        }

    def get_phase_three_config(self) -> Dict[str, Any]:
        """Get Phase 3 (AI Feedback Generation) configuration."""
        return {
            "temperature": self.feedback_temperature,
            "max_feedback_items": self.max_feedback_items,
            "model": self.gemini_model
        }


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached application settings.
    
    Returns:
        Application settings instance
    """
    return Settings()
