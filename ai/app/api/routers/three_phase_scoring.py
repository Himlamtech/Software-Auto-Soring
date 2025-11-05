"""API endpoints for 3-phase diagram scoring."""

from typing import Optional, Dict, Any, List
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
import asyncio

from app.core.pipeline.three_phase_pipeline import ThreePhasePipeline
from app.core.models.diagrams.diagram_factory import DiagramType
from app.config.settings import get_settings


# Request/Response Models
class DiagramSubmissionRequest(BaseModel):
    """Request model for diagram submission."""
    student_plantuml: str = Field(..., description="Student's PlantUML code")
    teacher_plantuml: str = Field(..., description="Teacher's reference PlantUML code")
    problem_description: str = Field(..., description="Problem description for context")
    diagram_type: Optional[DiagramType] = Field(None, description="Diagram type (auto-detected if not provided)")
    custom_weights: Optional[Dict[str, float]] = Field(None, description="Custom scoring weights")


class DiagramScoringResponse(BaseModel):
    """Response model for diagram scoring."""
    success: bool
    diagram_type: str
    final_score: float
    grade_letter: str
    feedback_summary: str
    processing_time: float
    confidence: float

    # Detailed results
    detailed_feedback: Dict[str, Any] = {}
    metrics: Dict[str, Any] = {}
    phase_results: Dict[str, Any] = {}

    # AI Generation Logs for Evidence
    ai_generation_logs: List[Dict[str, Any]] = []
    logs_summary: Dict[str, Any] = {}

    warnings: list[str] = []
    errors: list[str] = []


class PipelineStatusResponse(BaseModel):
    """Response model for pipeline status."""
    pipeline: str
    phases: Dict[str, Any]
    supported_diagrams: list[str]
    llm_model: str
    rate_limit: str
    scoring_scale: str


# Router setup
router = APIRouter(prefix="/three-phase", tags=["3-Phase Scoring"])


# Dependency to get pipeline instance
async def get_pipeline() -> ThreePhasePipeline:
    """Get configured pipeline instance."""
    settings = get_settings()
    
    config = {
        "gemini_api_key": settings.gemini_api_key,
        "gemini_model": settings.gemini_model,
        "gemini_rate_limit_rpm": settings.gemini_rate_limit_rpm,
        "normalization_temperature": settings.normalization_temperature,
        "feedback_temperature": settings.feedback_temperature,
        "normalization_max_retries": settings.normalization_max_retries,
        "similarity_threshold": 0.85,
        "supported_diagram_types": settings.supported_diagram_types
    }
    
    return ThreePhasePipeline(config)


@router.post("/score-diagram", response_model=DiagramScoringResponse)
async def score_diagram(
    request: DiagramSubmissionRequest,
    pipeline: ThreePhasePipeline = Depends(get_pipeline)
) -> DiagramScoringResponse:
    """
    Score a student diagram using the complete 3-phase pipeline.
    
    This endpoint processes a student's UML diagram through:
    1. Phase 1: Convention normalization (multi-prompt AI chain)
    2. Phase 2: Code-based extraction and metrics calculation
    3. Phase 3: AI feedback generation and final scoring
    
    Returns comprehensive feedback and a score on a 10-point scale.
    """
    try:
        # Validate inputs
        if not request.student_plantuml.strip():
            raise HTTPException(status_code=400, detail="Student PlantUML code cannot be empty")
        
        if not request.teacher_plantuml.strip():
            raise HTTPException(status_code=400, detail="Teacher PlantUML code cannot be empty")
        
        if not request.problem_description.strip():
            raise HTTPException(status_code=400, detail="Problem description cannot be empty")
        
        # Process through pipeline
        result = await pipeline.process_diagram(
            student_plantuml=request.student_plantuml,
            teacher_plantuml=request.teacher_plantuml,
            problem_description=request.problem_description,
            diagram_type=request.diagram_type,
            custom_weights=request.custom_weights
        )
        
        # Format response
        formatted_output = pipeline.format_final_output(result)

        # Get detailed AI generation logs
        ai_logs = pipeline.llm_service.get_detailed_logs()
        logs_summary = pipeline.llm_service.get_logs_summary()

        return DiagramScoringResponse(
            success=result.success,
            diagram_type=result.diagram_type.value,
            final_score=result.final_score,
            grade_letter=result.grade_letter,
            feedback_summary=result.feedback_summary,
            processing_time=result.total_processing_time,
            confidence=result.overall_confidence,
            detailed_feedback=formatted_output.get("detailed_feedback", {}),
            metrics=formatted_output.get("metrics", {}),
            phase_results={
                "phase_one": result.phase_one_result,
                "phase_two": result.phase_two_result,
                "phase_three": result.phase_three_result,
                "phase_timings": result.phase_timings
            },
            ai_generation_logs=ai_logs,
            logs_summary=logs_summary,
            warnings=result.warnings,
            errors=result.errors
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline processing failed: {str(e)}")


@router.get("/status", response_model=PipelineStatusResponse)
async def get_pipeline_status(
    pipeline: ThreePhasePipeline = Depends(get_pipeline)
) -> PipelineStatusResponse:
    """Get status and capabilities of the 3-phase pipeline."""
    try:
        status = await pipeline.get_pipeline_status()
        
        return PipelineStatusResponse(
            pipeline=status["pipeline"],
            phases=status["phases"],
            supported_diagrams=status["supported_diagrams"],
            llm_model=status["llm_model"],
            rate_limit=status["rate_limit"],
            scoring_scale=status["scoring_scale"]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get pipeline status: {str(e)}")


@router.post("/score-batch", response_model=list[DiagramScoringResponse])
async def score_diagrams_batch(
    requests: list[DiagramSubmissionRequest],
    pipeline: ThreePhasePipeline = Depends(get_pipeline)
) -> list[DiagramScoringResponse]:
    """
    Score multiple diagrams in batch.
    
    Processes multiple student diagrams with rate limiting to respect API limits.
    Each diagram is processed through the complete 3-phase pipeline.
    """
    if len(requests) > 10:
        raise HTTPException(status_code=400, detail="Batch size limited to 10 diagrams")
    
    if not requests:
        raise HTTPException(status_code=400, detail="No diagrams provided")
    
    results = []
    
    try:
        for i, request in enumerate(requests):
            # Add delay between requests for rate limiting
            if i > 0:
                await asyncio.sleep(4)  # 4 second delay for 15 RPM limit
            
            # Process individual diagram
            result = await pipeline.process_diagram(
                student_plantuml=request.student_plantuml,
                teacher_plantuml=request.teacher_plantuml,
                problem_description=request.problem_description,
                diagram_type=request.diagram_type,
                custom_weights=request.custom_weights
            )
            
            # Format response
            formatted_output = pipeline.format_final_output(result)
            
            results.append(DiagramScoringResponse(
                success=result.success,
                diagram_type=result.diagram_type.value,
                final_score=result.final_score,
                grade_letter=result.grade_letter,
                feedback_summary=result.feedback_summary,
                processing_time=result.total_processing_time,
                confidence=result.overall_confidence,
                detailed_feedback=formatted_output.get("detailed_feedback", {}),
                metrics=formatted_output.get("metrics", {}),
                phase_results={
                    "phase_one": result.phase_one_result,
                    "phase_two": result.phase_two_result,
                    "phase_three": result.phase_three_result,
                    "phase_timings": result.phase_timings
                },
                warnings=result.warnings,
                errors=result.errors
            ))
        
        return results
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch processing failed: {str(e)}")


@router.get("/supported-diagrams")
async def get_supported_diagrams() -> Dict[str, Any]:
    """Get list of supported diagram types and their descriptions."""
    return {
        "supported_types": [
            {
                "type": "use_case",
                "name": "Use Case Diagram",
                "description": "Shows actors, use cases, and their relationships"
            },
            {
                "type": "class",
                "name": "Class Diagram", 
                "description": "Shows classes, attributes, methods, and relationships"
            },
            {
                "type": "sequence",
                "name": "Sequence Diagram",
                "description": "Shows participants and message interactions over time"
            }
        ],
        "auto_detection": True,
        "description": "The system can automatically detect diagram types from PlantUML code"
    }


@router.get("/health")
async def health_check() -> Dict[str, str]:
    """Health check endpoint for the 3-phase scoring service."""
    try:
        settings = get_settings()
        
        # Basic configuration check
        if not settings.gemini_api_key:
            return {"status": "unhealthy", "reason": "GEMINI_API_KEY not configured"}
        
        return {
            "status": "healthy",
            "service": "3-Phase Diagram Scoring",
            "model": settings.gemini_model,
            "version": "1.0.0"
        }
        
    except Exception as e:
        return {"status": "unhealthy", "reason": str(e)}
