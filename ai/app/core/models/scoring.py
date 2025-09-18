"""Domain models for scoring and evaluation."""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from enum import Enum


class ComponentType(str, Enum):
    """Types of UML components that can be scored."""
    
    ACTOR = "actor"
    USE_CASE = "use_case"
    RELATIONSHIP = "relationship"


class ComparisonResult(BaseModel):
    """Result of comparing expected vs actual components."""
    
    component_type: ComponentType = Field(..., description="Type of component being compared")
    true_positives: List[str] = Field(default_factory=list, description="Correctly identified components")
    false_positives: List[str] = Field(default_factory=list, description="Incorrectly included components")
    false_negatives: List[str] = Field(default_factory=list, description="Missing expected components")


class ScoringMetrics(BaseModel):
    """Scoring metrics for evaluation."""
    
    precision: float = Field(..., ge=0.0, le=1.0, description="Precision score")
    recall: float = Field(..., ge=0.0, le=1.0, description="Recall score")
    f1_score: float = Field(..., ge=0.0, le=1.0, description="F1 score")
    accuracy: float = Field(..., ge=0.0, le=1.0, description="Accuracy score")


class ComponentScore(BaseModel):
    """Score for a specific component type."""
    
    component_type: ComponentType = Field(..., description="Type of component")
    metrics: ScoringMetrics = Field(..., description="Metrics for this component type")
    comparison: ComparisonResult = Field(..., description="Detailed comparison results")
    weight: float = Field(default=1.0, ge=0.0, description="Weight for this component in final score")


class OverallScore(BaseModel):
    """Overall scoring result for the entire diagram."""
    
    final_score: float = Field(..., ge=0.0, le=10.0, description="Final score out of 10")
    component_scores: List[ComponentScore] = Field(..., description="Scores for each component type")
    overall_metrics: ScoringMetrics = Field(..., description="Overall aggregated metrics")
    
    
class FeedbackItem(BaseModel):
    """Individual feedback item."""
    
    type: str = Field(..., description="Type of feedback (strength, weakness, suggestion)")
    component_type: Optional[ComponentType] = Field(None, description="Related component type")
    message: str = Field(..., description="Feedback message")
    severity: str = Field(default="medium", description="Severity level (low, medium, high)")


class ScoringResult(BaseModel):
    """Complete scoring result with feedback."""
    
    score: OverallScore = Field(..., description="Scoring details and metrics")
    feedback: List[FeedbackItem] = Field(default_factory=list, description="Generated feedback items")
    processing_time: Optional[float] = Field(None, description="Time taken to process in seconds")
    llm_model_used: Optional[str] = Field(None, description="LLM model used for extraction")
