"""Domain models for system input and output."""

from typing import Optional
from pydantic import BaseModel, Field


class StudentSubmission(BaseModel):
    """Student's submission containing PlantUML code."""
    
    student_id: Optional[str] = Field(None, description="Student identifier")
    plantuml_code: str = Field(..., description="PlantUML code for the diagram")
    submission_time: Optional[str] = Field(None, description="When the submission was made")
    file_name: Optional[str] = Field(None, description="Original file name")


class ProblemDescription(BaseModel):
    """Problem description with expected requirements."""
    
    title: str = Field(..., description="Problem title")
    description: str = Field(..., description="Detailed problem description")
    functional_requirements: Optional[str] = Field(None, description="Functional requirements")
    expected_actors: Optional[str] = Field(None, description="Hint about expected actors")
    expected_use_cases: Optional[str] = Field(None, description="Hint about expected use cases")
    grading_criteria: Optional[str] = Field(None, description="Specific grading criteria")


class ScoringRequest(BaseModel):
    """Complete request for scoring a student submission."""
    
    submission: StudentSubmission = Field(..., description="Student's submission")
    problem: ProblemDescription = Field(..., description="Problem description and requirements")
    scoring_weights: Optional[dict] = Field(None, description="Custom weights for different components")
    options: Optional[dict] = Field(None, description="Additional scoring options")
