"""Phase 3 Orchestrator: AI Feedback Generation and Scoring."""

from typing import Dict, Any
from pydantic import BaseModel
import time
from loguru import logger

from .error_analyzer import ErrorAnalyzer, ErrorAnalysisResult
from .feedback_generator import FeedbackGenerator, FeedbackGenerationResult
from .score_calculator import ScoreCalculator, ScoreBreakdown
from app.core.models.diagrams.diagram_factory import DiagramType


class PhaseThreeResult(BaseModel):
    """Complete result of Phase 3 feedback generation and scoring."""
    success: bool
    diagram_type: DiagramType
    
    # Analysis results
    error_analysis: Dict[str, Any]  # Serialized ErrorAnalysisResult
    feedback_result: Dict[str, Any]  # Serialized FeedbackGenerationResult
    score_breakdown: Dict[str, Any]  # Serialized ScoreBreakdown
    
    # Final outputs
    final_score: float  # 0-10 scale
    grade_letter: str
    summary: str
    
    # Metadata
    processing_time: float
    confidence: float
    warnings: list[str]


class PhaseThreeOrchestrator:
    """
    Orchestrates Phase 3: AI-based error analysis, feedback generation, and final scoring.
    
    This service:
    1. Analyzes errors from Phase 2 metrics
    2. Generates human-readable feedback and suggestions
    3. Calculates final score on 10-point scale
    4. Provides comprehensive educational feedback
    """
    
    def __init__(self, llm_service, config: Dict[str, Any]):
        """
        Initialize Phase 3 orchestrator.
        
        Args:
            llm_service: LLM service for AI-based analysis and feedback
            config: Configuration dictionary
        """
        self.llm_service = llm_service
        self.config = config
        
        # Initialize services
        self.error_analyzer = ErrorAnalyzer(llm_service)
        self.feedback_generator = FeedbackGenerator(llm_service)
        self.score_calculator = ScoreCalculator(config)
    
    async def generate_feedback_and_score(
        self,
        teacher_diagram: Dict[str, Any],
        student_diagram: Dict[str, Any],
        metrics: Dict[str, Any],
        problem_description: str,
        diagram_type: DiagramType,
        custom_weights: Dict[str, float] = None
    ) -> PhaseThreeResult:
        """
        Generate comprehensive feedback and calculate final score.
        
        Args:
            teacher_diagram: Teacher's reference diagram (serialized)
            student_diagram: Student's diagram (serialized)
            metrics: Quantitative metrics from Phase 2
            problem_description: Problem description for context
            diagram_type: Type of diagram being analyzed
            custom_weights: Custom scoring weights
            
        Returns:
            PhaseThreeResult with complete feedback and scoring
        """
        start_time = time.time()
        warnings = []
        
        try:
            logger.info(f"Starting Phase 3: AI feedback generation for {diagram_type.value} diagram")
            
            # Step 1: Analyze errors
            logger.info("Step 1: Analyzing errors from metrics...")
            error_analysis = await self.error_analyzer.analyze_errors(
                teacher_diagram, student_diagram, metrics, problem_description, diagram_type, step_name="Phase 3 Step 1: Error Analysis"
            )

            # Step 2: Generate feedback
            logger.info("Step 2: Generating educational feedback...")
            feedback_result = await self.feedback_generator.generate_feedback(
                error_analysis, teacher_diagram, student_diagram, metrics, problem_description, step_name="Phase 3 Step 2: Feedback Generation"
            )
            
            # Step 3: Calculate final score
            logger.info("Step 3: Calculating final score...")
            score_breakdown = self.score_calculator.calculate_final_score(
                metrics, error_analysis, feedback_result, diagram_type, custom_weights
            )
            
            # Collect confidence and warnings
            confidence = min(error_analysis.confidence, feedback_result.confidence)
            
            if confidence < 0.7:
                warnings.append("Analysis confidence is below 70% - results may be less reliable")
            
            if error_analysis.total_errors == 0 and score_breakdown.final_score < 8.0:
                warnings.append("No errors detected but score is low - may indicate analysis issues")
            
            processing_time = time.time() - start_time
            
            logger.info(f"Phase 3 completed - Final score: {score_breakdown.final_score}/10 "
                       f"({score_breakdown.grade_letter})")
            
            return PhaseThreeResult(
                success=True,
                diagram_type=diagram_type,
                error_analysis=self._serialize_error_analysis(error_analysis),
                feedback_result=self._serialize_feedback_result(feedback_result),
                score_breakdown=self._serialize_score_breakdown(score_breakdown),
                final_score=score_breakdown.final_score,
                grade_letter=score_breakdown.grade_letter,
                summary=feedback_result.summary,
                processing_time=processing_time,
                confidence=confidence,
                warnings=warnings
            )
            
        except Exception as e:
            logger.error(f"Phase 3 feedback generation failed: {str(e)}")
            processing_time = time.time() - start_time
            
            # Return failure result with minimal feedback
            return PhaseThreeResult(
                success=False,
                diagram_type=diagram_type,
                error_analysis={},
                feedback_result={},
                score_breakdown={},
                final_score=0.0,
                grade_letter='F',
                summary="Feedback generation failed. Please review your diagram manually.",
                processing_time=processing_time,
                confidence=0.0,
                warnings=[f"Phase 3 failed: {str(e)}"]
            )
    
    def _serialize_error_analysis(self, error_analysis: ErrorAnalysisResult) -> Dict[str, Any]:
        """Serialize error analysis result."""
        return {
            'diagram_type': error_analysis.diagram_type.value,
            'total_errors': error_analysis.total_errors,
            'error_categories': [
                {
                    'category': cat.category,
                    'severity': cat.severity,
                    'count': cat.count,
                    'description': cat.description,
                    'examples': cat.examples
                }
                for cat in error_analysis.error_categories
            ],
            'severity_breakdown': error_analysis.severity_breakdown,
            'primary_issues': error_analysis.primary_issues,
            'confidence': error_analysis.confidence
        }
    
    def _serialize_feedback_result(self, feedback_result: FeedbackGenerationResult) -> Dict[str, Any]:
        """Serialize feedback generation result."""
        return {
            'diagram_type': feedback_result.diagram_type.value,
            'feedback_items': [
                {
                    'type': item.type,
                    'category': item.category,
                    'message': item.message,
                    'severity': item.severity,
                    'actionable': item.actionable,
                    'examples': item.examples
                }
                for item in feedback_result.feedback_items
            ],
            'summary': feedback_result.summary,
            'strengths': feedback_result.strengths,
            'areas_for_improvement': feedback_result.areas_for_improvement,
            'confidence': feedback_result.confidence
        }
    
    def _serialize_score_breakdown(self, score_breakdown: ScoreBreakdown) -> Dict[str, Any]:
        """Serialize score breakdown result."""
        return {
            'base_score': score_breakdown.base_score,
            'penalties': score_breakdown.penalties,
            'bonuses': score_breakdown.bonuses,
            'final_score': score_breakdown.final_score,
            'grade_letter': score_breakdown.grade_letter,
            'explanation': score_breakdown.explanation
        }
    
    def format_final_result(self, result: PhaseThreeResult) -> Dict[str, Any]:
        """Format the final result for API response or display."""
        return {
            'success': result.success,
            'diagram_type': result.diagram_type.value,
            'final_score': result.final_score,
            'grade_letter': result.grade_letter,
            'summary': result.summary,
            'processing_time': result.processing_time,
            'confidence': result.confidence,
            
            # Detailed feedback
            'feedback': {
                'strengths': result.feedback_result.get('strengths', []),
                'areas_for_improvement': result.feedback_result.get('areas_for_improvement', []),
                'detailed_items': result.feedback_result.get('feedback_items', [])
            },
            
            # Error analysis
            'errors': {
                'total_errors': result.error_analysis.get('total_errors', 0),
                'primary_issues': result.error_analysis.get('primary_issues', []),
                'severity_breakdown': result.error_analysis.get('severity_breakdown', {})
            },
            
            # Scoring details
            'scoring': {
                'base_score': result.score_breakdown.get('base_score', 0),
                'penalties': result.score_breakdown.get('penalties', {}),
                'bonuses': result.score_breakdown.get('bonuses', {}),
                'explanation': result.score_breakdown.get('explanation', '')
            },
            
            'warnings': result.warnings
        }
    
    async def get_feedback_status(self) -> Dict[str, Any]:
        """Get status information about the feedback service."""
        return {
            "service": "PhaseThreeOrchestrator",
            "phase": "Phase 3 - AI Feedback Generation and Scoring",
            "capabilities": [
                "Error analysis from metrics",
                "Educational feedback generation",
                "Final score calculation (0-10 scale)",
                "Letter grade assignment"
            ],
            "supported_diagrams": [dt.value for dt in DiagramType],
            "scoring_components": [
                "Base score from metrics",
                "Error-based penalties",
                "Quality bonuses",
                "Final score normalization"
            ],
            "feedback_types": [
                "Errors and corrections",
                "Suggestions for improvement", 
                "Strengths identification",
                "Educational explanations"
            ]
        }
