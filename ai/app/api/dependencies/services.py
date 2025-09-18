"""Service dependency injection for FastAPI."""

from typing import Annotated
from fastapi import Depends
from app.core.pipeline.scoring_pipeline import ScoringPipeline
from app.core.scoring.component_matcher import ComponentMatcher
from app.core.scoring.metrics_calculator import MetricsCalculator
from app.infra.storage.file_storage import FileStorageService
from app.infra.llm_providers.openai_provider import OpenAIExtractionProvider, OpenAIFeedbackProvider
from app.infra.llm_providers.gemini_provider import GeminiExtractionProvider, GeminiFeedbackProvider
from app.infra.external.plantuml_external import PlantUMLExternalService
from app.config.settings import get_settings


def get_settings_dependency():
    """Get application settings."""
    return get_settings()


def get_component_matcher() -> ComponentMatcher:
    """Get component matcher service."""
    return ComponentMatcher()


def get_metrics_calculator() -> MetricsCalculator:
    """Get metrics calculator service."""
    return MetricsCalculator()


def get_storage_service(
    settings = Depends(get_settings_dependency)
) -> FileStorageService:
    """
    Get storage service with configuration.
    
    Args:
        settings: Application settings
        
    Returns:
        Configured storage service
    """
    return FileStorageService(base_path=settings.storage_path)


def get_llm_extraction_service(
    settings = Depends(get_settings_dependency)
):
    """
    Get LLM extraction service based on configured provider.
    
    Args:
        settings: Application settings
        
    Returns:
        Configured LLM extraction service
    """
    if settings.llm_provider == "openai":
        return OpenAIExtractionProvider(
            api_key=settings.openai_api_key,
            model=settings.llm_model
        )
    elif settings.llm_provider == "gemini":
        return GeminiExtractionProvider(
            api_key=settings.gemini_api_key,
            model=settings.gemini_model
        )
    else:
        raise ValueError(f"Unknown LLM provider: {settings.llm_provider}")


def get_llm_feedback_service(
    settings = Depends(get_settings_dependency)
):
    """
    Get LLM feedback service based on configured provider.
    
    Args:
        settings: Application settings
        
    Returns:
        Configured LLM feedback service
    """
    if settings.llm_provider == "openai":
        return OpenAIFeedbackProvider(
            api_key=settings.openai_api_key,
            model=settings.llm_model
        )
    elif settings.llm_provider == "gemini":
        return GeminiFeedbackProvider(
            api_key=settings.gemini_api_key,
            model=settings.gemini_model
        )
    else:
        raise ValueError(f"Unknown LLM provider: {settings.llm_provider}")


def get_plantuml_service(
    settings = Depends(get_settings_dependency)
) -> PlantUMLExternalService:
    """
    Get PlantUML service.
    
    Args:
        settings: Application settings
        
    Returns:
        Configured PlantUML service
    """
    return PlantUMLExternalService(
        plantuml_jar_path=settings.plantuml_jar_path,
        use_online_service=settings.use_online_plantuml
    )


def get_scoring_pipeline(
    component_matcher: Annotated[ComponentMatcher, Depends(get_component_matcher)],
    metrics_calculator: Annotated[MetricsCalculator, Depends(get_metrics_calculator)]
) -> ScoringPipeline:
    """
    Get scoring pipeline with all dependencies.
    
    Args:
        component_matcher: Component matching service
        metrics_calculator: Metrics calculation service
        
    Returns:
        Configured scoring pipeline
    """
    return ScoringPipeline(
        component_matcher=component_matcher,
        metrics_calculator=metrics_calculator
    )
