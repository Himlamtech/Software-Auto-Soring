"""Scoring API router."""

from typing import List
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, UploadFile, File
from fastapi.responses import JSONResponse
import uuid
import asyncio
from app.api.schemas.scoring_schemas import (
    SubmissionRequest,
    ScoringResponse,
    BatchScoringRequest,
    BatchScoringResponse,
    ValidationRequest,
    ValidationResponse,
    ComponentScoreResponse,
    FeedbackResponse
)
from app.core.models.input_output import StudentSubmission, ScoringRequest
from app.core.pipeline.scoring_pipeline import ScoringPipeline
from app.api.dependencies.services import get_scoring_pipeline, get_storage_service


router = APIRouter(prefix="/scoring", tags=["scoring"])


@router.post("/submit", response_model=ScoringResponse)
async def submit_for_scoring(
    request: SubmissionRequest,
    pipeline: ScoringPipeline = Depends(get_scoring_pipeline),
    storage = Depends(get_storage_service)
) -> ScoringResponse:
    """
    Submit a PlantUML diagram for automatic scoring.
    
    Args:
        request: Submission request with PlantUML code and problem ID
        pipeline: Scoring pipeline service
        storage: Storage service
        
    Returns:
        Scoring response with results and feedback
    """
    try:
        # Generate unique IDs
        submission_id = str(uuid.uuid4())
        result_id = str(uuid.uuid4())
        
        # Load problem description
        problem = await storage.load_problem_description(request.problem_id)
        if not problem:
            raise HTTPException(status_code=404, detail="Problem not found")
        
        # Create submission object
        submission = StudentSubmission(
            student_id=request.student_id,
            plantuml_code=request.plantuml_code,
            file_name=request.file_name
        )
        
        # Save submission
        await storage.save_submission(submission, submission_id)
        
        # Create scoring request
        scoring_request = ScoringRequest(
            submission=submission,
            problem=problem,
            options=request.scoring_options
        )
        
        # Process scoring
        result = await pipeline.process_scoring_request(scoring_request)
        
        # Save result
        await storage.save_scoring_result(result, submission_id, result_id)
        
        return ScoringResponse(
            submission_id=submission_id,
            result_id=result_id,
            final_score=result.score.final_score,
            processing_time=result.processing_time,
            detailed_results=result
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scoring failed: {str(e)}")


@router.post("/upload", response_model=ScoringResponse)
async def upload_plantuml_file(
    problem_id: str,
    student_id: str = None,
    file: UploadFile = File(...),
    pipeline: ScoringPipeline = Depends(get_scoring_pipeline),
    storage = Depends(get_storage_service)
) -> ScoringResponse:
    """
    Upload a PlantUML file for automatic scoring.
    
    Args:
        problem_id: Problem identifier
        student_id: Optional student identifier
        file: Uploaded PlantUML file
        pipeline: Scoring pipeline service
        storage: Storage service
        
    Returns:
        Scoring response with results and feedback
    """
    try:
        # Read file content
        content = await file.read()
        plantuml_code = content.decode('utf-8')
        
        # Create submission request
        request = SubmissionRequest(
            student_id=student_id,
            plantuml_code=plantuml_code,
            problem_id=problem_id,
            file_name=file.filename
        )
        
        # Process using the submit endpoint logic
        return await submit_for_scoring(request, pipeline, storage)
        
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="File must be a valid text file")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")


@router.post("/batch", response_model=BatchScoringResponse)
async def batch_scoring(
    request: BatchScoringRequest,
    background_tasks: BackgroundTasks,
    pipeline: ScoringPipeline = Depends(get_scoring_pipeline),
    storage = Depends(get_storage_service)
) -> BatchScoringResponse:
    """
    Submit multiple PlantUML diagrams for batch scoring.
    
    Args:
        request: Batch scoring request
        background_tasks: Background task handler
        pipeline: Scoring pipeline service
        storage: Storage service
        
    Returns:
        Batch scoring response with all results
    """
    try:
        batch_id = str(uuid.uuid4())
        results = []
        completed = 0
        failed = 0
        
        # Process each submission
        for submission_request in request.submissions:
            try:
                result = await submit_for_scoring(submission_request, pipeline, storage)
                results.append(result)
                completed += 1
            except Exception as e:
                # Log error and continue with other submissions
                failed += 1
                continue
        
        return BatchScoringResponse(
            batch_id=batch_id,
            total_submissions=len(request.submissions),
            completed_submissions=completed,
            failed_submissions=failed,
            results=results,
            processing_time=0.0  # Will be calculated properly in implementation
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch scoring failed: {str(e)}")


@router.post("/validate", response_model=ValidationResponse)
async def validate_plantuml(
    request: ValidationRequest,
    pipeline: ScoringPipeline = Depends(get_scoring_pipeline)
) -> ValidationResponse:
    """
    Validate PlantUML code syntax and structure.
    
    Args:
        request: Validation request with PlantUML code
        pipeline: Scoring pipeline service
        
    Returns:
        Validation response with errors and suggestions
    """
    try:
        # Implementation placeholder for validation logic
        return ValidationResponse(
            is_valid=True,
            errors=[],
            warnings=[],
            suggestions=[]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Validation failed: {str(e)}")


@router.get("/result/{result_id}", response_model=ScoringResponse)
async def get_scoring_result(
    result_id: str,
    storage = Depends(get_storage_service)
) -> JSONResponse:
    """
    Retrieve scoring result by ID.
    
    Args:
        result_id: Unique result identifier
        storage: Storage service
        
    Returns:
        Scoring result details
    """
    try:
        result_data = await storage.load_scoring_result(result_id)
        if not result_data:
            raise HTTPException(status_code=404, detail="Result not found")
        
        return JSONResponse(content=result_data)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve result: {str(e)}")


@router.get("/component-scores/{result_id}", response_model=List[ComponentScoreResponse])
async def get_component_scores(
    result_id: str,
    storage = Depends(get_storage_service)
) -> List[ComponentScoreResponse]:
    """
    Get detailed component scores for a result.
    
    Args:
        result_id: Unique result identifier
        storage: Storage service
        
    Returns:
        List of component scores
    """
    try:
        result_data = await storage.load_scoring_result(result_id)
        if not result_data:
            raise HTTPException(status_code=404, detail="Result not found")
        
        # Convert component scores to response format
        component_responses = []
        for component_score in result_data.get("component_scores", []):
            comparison = component_score.get("comparison", {})
            metrics = component_score.get("metrics", {})
            
            component_responses.append(ComponentScoreResponse(
                component_type=component_score.get("component_type", ""),
                precision=metrics.get("precision", 0.0),
                recall=metrics.get("recall", 0.0),
                f1_score=metrics.get("f1_score", 0.0),
                accuracy=metrics.get("accuracy", 0.0),
                true_positives=comparison.get("true_positives", []),
                false_positives=comparison.get("false_positives", []),
                false_negatives=comparison.get("false_negatives", [])
            ))
        
        return component_responses
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve component scores: {str(e)}")


@router.get("/feedback/{result_id}", response_model=FeedbackResponse)
async def get_feedback(
    result_id: str,
    storage = Depends(get_storage_service)
) -> FeedbackResponse:
    """
    Get feedback and suggestions for a result.
    
    Args:
        result_id: Unique result identifier
        storage: Storage service
        
    Returns:
        Structured feedback response
    """
    try:
        result_data = await storage.load_scoring_result(result_id)
        if not result_data:
            raise HTTPException(status_code=404, detail="Result not found")
        
        feedback_items = result_data.get("feedback", [])
        
        # Categorize feedback
        strengths = [item["message"] for item in feedback_items if item.get("type") == "strength"]
        improvements = [item["message"] for item in feedback_items if item.get("type") == "suggestion"]
        missing = [item["message"] for item in feedback_items if item.get("type") == "weakness"]
        
        return FeedbackResponse(
            feedback_items=feedback_items,
            strengths=strengths,
            improvements=improvements,
            missing_components=missing
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve feedback: {str(e)}")
