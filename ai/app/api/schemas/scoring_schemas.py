"""API schemas for scoring endpoints."""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from app.core.models.scoring import ScoringResult, ComponentScore, FeedbackItem


class SubmissionRequest(BaseModel):
    """Request schema for submitting PlantUML for scoring."""
    
    student_id: Optional[str] = Field(None, description="Student identifier")
    plantuml_code: str = Field(..., description="PlantUML code to be scored")
    problem_id: str = Field(..., description="Problem identifier")
    file_name: Optional[str] = Field(None, description="Original file name")
    scoring_options: Optional[Dict[str, Any]] = Field(None, description="Custom scoring options")


class ProblemRequest(BaseModel):
    """Request schema for creating a new problem."""
    
    title: str = Field(..., description="Problem title")
    description: str = Field(..., description="Detailed problem description")
    functional_requirements: Optional[str] = Field(None, description="Functional requirements")
    expected_actors: Optional[str] = Field(None, description="Expected actors description")
    expected_use_cases: Optional[str] = Field(None, description="Expected use cases description")
    grading_criteria: Optional[str] = Field(None, description="Grading criteria")


class ScoringResponse(BaseModel):
    """Response schema for scoring results."""
    
    submission_id: str = Field(..., description="Unique submission identifier")
    result_id: str = Field(..., description="Unique result identifier")
    final_score: float = Field(..., description="Final score out of 10")
    processing_time: Optional[float] = Field(None, description="Processing time in seconds")
    detailed_results: ScoringResult = Field(..., description="Detailed scoring results")


class ComponentScoreResponse(BaseModel):
    """Response schema for component-specific scores."""
    
    component_type: str = Field(..., description="Type of component (actor, use_case, relationship)")
    precision: float = Field(..., description="Precision score")
    recall: float = Field(..., description="Recall score")
    f1_score: float = Field(..., description="F1 score")
    accuracy: float = Field(..., description="Accuracy score")
    true_positives: List[str] = Field(..., description="Correctly identified components")
    false_positives: List[str] = Field(..., description="Incorrectly included components")
    false_negatives: List[str] = Field(..., description="Missing expected components")


class FeedbackResponse(BaseModel):
    """Response schema for feedback items."""
    
    feedback_items: List[FeedbackItem] = Field(..., description="List of feedback items")
    strengths: List[str] = Field(default_factory=list, description="Identified strengths")
    improvements: List[str] = Field(default_factory=list, description="Suggested improvements")
    missing_components: List[str] = Field(default_factory=list, description="Missing components")


class BatchScoringRequest(BaseModel):
    """Request schema for batch scoring multiple submissions."""
    
    submissions: List[SubmissionRequest] = Field(..., description="List of submissions to score")
    problem_id: str = Field(..., description="Common problem identifier")
    batch_options: Optional[Dict[str, Any]] = Field(None, description="Batch processing options")


class BatchScoringResponse(BaseModel):
    """Response schema for batch scoring results."""
    
    batch_id: str = Field(..., description="Unique batch identifier")
    total_submissions: int = Field(..., description="Total number of submissions")
    completed_submissions: int = Field(..., description="Number of completed submissions")
    failed_submissions: int = Field(..., description="Number of failed submissions")
    results: List[ScoringResponse] = Field(..., description="Individual scoring results")
    processing_time: float = Field(..., description="Total batch processing time")


class ValidationRequest(BaseModel):
    """Request schema for PlantUML validation."""
    
    plantuml_code: str = Field(..., description="PlantUML code to validate")
    validation_level: str = Field(default="basic", description="Validation level (basic, strict)")


class ValidationResponse(BaseModel):
    """Response schema for PlantUML validation."""
    
    is_valid: bool = Field(..., description="Whether the PlantUML code is valid")
    errors: List[str] = Field(default_factory=list, description="Validation errors")
    warnings: List[str] = Field(default_factory=list, description="Validation warnings")
    suggestions: List[str] = Field(default_factory=list, description="Improvement suggestions")


class AnalyticsRequest(BaseModel):
    """Request schema for scoring analytics."""
    
    problem_id: Optional[str] = Field(None, description="Filter by problem ID")
    student_id: Optional[str] = Field(None, description="Filter by student ID")
    date_from: Optional[str] = Field(None, description="Start date filter (ISO format)")
    date_to: Optional[str] = Field(None, description="End date filter (ISO format)")
    include_details: bool = Field(default=False, description="Include detailed breakdowns")


class AnalyticsResponse(BaseModel):
    """Response schema for scoring analytics."""
    
    total_submissions: int = Field(..., description="Total number of submissions")
    average_score: float = Field(..., description="Average score across submissions")
    score_distribution: Dict[str, int] = Field(..., description="Score distribution by ranges")
    component_averages: Dict[str, float] = Field(..., description="Average scores by component type")
    common_issues: List[str] = Field(..., description="Most common issues identified")
    processing_stats: Dict[str, Any] = Field(..., description="Processing time statistics")
