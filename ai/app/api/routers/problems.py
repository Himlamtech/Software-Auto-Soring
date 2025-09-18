"""Problems management API router."""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
import uuid
from app.api.schemas.scoring_schemas import ProblemRequest
from app.core.models.input_output import ProblemDescription
from app.api.dependencies.services import get_storage_service


router = APIRouter(prefix="/problems", tags=["problems"])


@router.post("/", response_model=dict)
async def create_problem(
    request: ProblemRequest,
    storage = Depends(get_storage_service)
) -> dict:
    """
    Create a new problem for scoring assignments.
    
    Args:
        request: Problem creation request
        storage: Storage service
        
    Returns:
        Created problem details with ID
    """
    try:
        problem_id = str(uuid.uuid4())
        
        problem = ProblemDescription(
            title=request.title,
            description=request.description,
            functional_requirements=request.functional_requirements,
            expected_actors=request.expected_actors,
            expected_use_cases=request.expected_use_cases,
            grading_criteria=request.grading_criteria
        )
        
        await storage.save_problem_description(problem, problem_id)
        
        return {
            "problem_id": problem_id,
            "title": problem.title,
            "description": problem.description,
            "status": "created"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create problem: {str(e)}")


@router.get("/{problem_id}", response_model=dict)
async def get_problem(
    problem_id: str,
    storage = Depends(get_storage_service)
) -> dict:
    """
    Retrieve a problem by ID.
    
    Args:
        problem_id: Unique problem identifier
        storage: Storage service
        
    Returns:
        Problem details
    """
    try:
        problem = await storage.load_problem_description(problem_id)
        if not problem:
            raise HTTPException(status_code=404, detail="Problem not found")
        
        return {
            "problem_id": problem_id,
            "title": problem.title,
            "description": problem.description,
            "functional_requirements": problem.functional_requirements,
            "expected_actors": problem.expected_actors,
            "expected_use_cases": problem.expected_use_cases,
            "grading_criteria": problem.grading_criteria
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve problem: {str(e)}")


@router.put("/{problem_id}", response_model=dict)
async def update_problem(
    problem_id: str,
    request: ProblemRequest,
    storage = Depends(get_storage_service)
) -> dict:
    """
    Update an existing problem.
    
    Args:
        problem_id: Unique problem identifier
        request: Problem update request
        storage: Storage service
        
    Returns:
        Updated problem details
    """
    try:
        # Check if problem exists
        existing_problem = await storage.load_problem_description(problem_id)
        if not existing_problem:
            raise HTTPException(status_code=404, detail="Problem not found")
        
        # Update problem
        updated_problem = ProblemDescription(
            title=request.title,
            description=request.description,
            functional_requirements=request.functional_requirements,
            expected_actors=request.expected_actors,
            expected_use_cases=request.expected_use_cases,
            grading_criteria=request.grading_criteria
        )
        
        await storage.save_problem_description(updated_problem, problem_id)
        
        return {
            "problem_id": problem_id,
            "title": updated_problem.title,
            "description": updated_problem.description,
            "status": "updated"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update problem: {str(e)}")


@router.delete("/{problem_id}")
async def delete_problem(
    problem_id: str,
    storage = Depends(get_storage_service)
) -> dict:
    """
    Delete a problem (soft delete by moving to archive).
    
    Args:
        problem_id: Unique problem identifier
        storage: Storage service
        
    Returns:
        Deletion confirmation
    """
    try:
        # Check if problem exists
        problem = await storage.load_problem_description(problem_id)
        if not problem:
            raise HTTPException(status_code=404, detail="Problem not found")
        
        # Implementation placeholder for soft delete logic
        # In a real implementation, this would move the problem to an archive
        
        return {
            "problem_id": problem_id,
            "status": "deleted"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete problem: {str(e)}")


@router.get("/", response_model=List[dict])
async def list_problems(
    limit: int = 50,
    offset: int = 0,
    search: Optional[str] = None,
    storage = Depends(get_storage_service)
) -> List[dict]:
    """
    List all problems with pagination and search.
    
    Args:
        limit: Maximum number of problems to return
        offset: Number of problems to skip
        search: Optional search term
        storage: Storage service
        
    Returns:
        List of problems
    """
    try:
        # Implementation placeholder for listing problems
        # In a real implementation, this would query the storage for problems
        
        return [
            {
                "problem_id": "example-id",
                "title": "Example Problem",
                "description": "Example problem description",
                "created_at": "2024-01-01T00:00:00Z"
            }
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list problems: {str(e)}")


@router.get("/{problem_id}/submissions")
async def get_problem_submissions(
    problem_id: str,
    limit: int = 50,
    offset: int = 0,
    storage = Depends(get_storage_service)
) -> List[dict]:
    """
    Get all submissions for a specific problem.
    
    Args:
        problem_id: Unique problem identifier
        limit: Maximum number of submissions to return
        offset: Number of submissions to skip
        storage: Storage service
        
    Returns:
        List of submissions for the problem
    """
    try:
        # Check if problem exists
        problem = await storage.load_problem_description(problem_id)
        if not problem:
            raise HTTPException(status_code=404, detail="Problem not found")
        
        # Implementation placeholder for getting submissions by problem
        submissions = await storage.list_submissions()
        
        return [
            {
                "submission_id": sub["submission_id"],
                "student_id": sub.get("student_id"),
                "timestamp": sub["timestamp"],
                "file_name": sub.get("file_name")
            }
            for sub in submissions[:limit]
        ]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get submissions: {str(e)}")


@router.post("/{problem_id}/validate")
async def validate_problem_requirements(
    problem_id: str,
    storage = Depends(get_storage_service)
) -> dict:
    """
    Validate problem requirements and extract expected components.
    
    Args:
        problem_id: Unique problem identifier
        storage: Storage service
        
    Returns:
        Validation results and extracted components
    """
    try:
        problem = await storage.load_problem_description(problem_id)
        if not problem:
            raise HTTPException(status_code=404, detail="Problem not found")
        
        # Implementation placeholder for problem validation
        # This would use LLM services to extract expected components
        
        return {
            "problem_id": problem_id,
            "is_valid": True,
            "extracted_actors": [],
            "extracted_use_cases": [],
            "extracted_relationships": [],
            "suggestions": []
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to validate problem: {str(e)}")
