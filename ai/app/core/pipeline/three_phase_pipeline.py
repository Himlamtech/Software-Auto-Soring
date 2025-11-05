"""Main 3-Phase Pipeline for Automated Diagram Grading."""

from typing import Dict, Any, Optional
from pydantic import BaseModel
import time
from loguru import logger

from app.services.normalization.normalization_orchestrator import NormalizationOrchestrator
from app.services.parsing.phase_two_extractor import PhaseTwoExtractor
from app.services.feedback.phase_three_orchestrator import PhaseThreeOrchestrator
from app.core.models.diagrams.diagram_factory import DiagramType, DiagramFactory
from app.infra.llm_providers.gemini_provider import GeminiLLMService


class PipelineResult(BaseModel):
    """Complete result of the 3-phase pipeline."""
    success: bool
    diagram_type: DiagramType
    
    # Phase results
    phase_one_result: Dict[str, Any]  # Convention normalization
    phase_two_result: Dict[str, Any]  # Extraction and metrics
    phase_three_result: Dict[str, Any]  # Feedback and scoring
    
    # Final outputs
    final_score: float
    grade_letter: str
    feedback_summary: str
    
    # Pipeline metadata
    total_processing_time: float
    phase_timings: Dict[str, float]
    overall_confidence: float
    warnings: list[str]
    errors: list[str]


class ThreePhasePipeline:
    """
    Main orchestrator for the 3-phase automated diagram grading pipeline.
    
    Phase 1: Convention Normalization (Multi-prompt AI chain)
    Phase 2: Code-based Extraction and Metrics Calculation
    Phase 3: AI Feedback Generation and Final Scoring
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the 3-phase pipeline.
        
        Args:
            config: Configuration dictionary with all settings
        """
        self.config = config
        
        # Initialize LLM service
        self.llm_service = GeminiLLMService(
            api_key=config.get("gemini_api_key"),
            model=config.get("gemini_model", "gemini-2.5-flash-lite"),
            temperature=config.get("normalization_temperature", 0.1)
        )
        
        # Initialize phase orchestrators
        self.phase_one = NormalizationOrchestrator(self.llm_service, config)
        self.phase_two = PhaseTwoExtractor(config)
        self.phase_three = PhaseThreeOrchestrator(self.llm_service, config)
    
    async def process_diagram(
        self,
        student_plantuml: str,
        teacher_plantuml: str,
        problem_description: str,
        diagram_type: Optional[DiagramType] = None,
        custom_weights: Optional[Dict[str, float]] = None
    ) -> PipelineResult:
        """
        Process a student diagram through the complete 3-phase pipeline.
        
        Args:
            student_plantuml: Student's PlantUML code
            teacher_plantuml: Teacher's reference PlantUML code
            problem_description: Problem description for context
            diagram_type: Type of diagram (auto-detected if None)
            custom_weights: Custom scoring weights
            
        Returns:
            PipelineResult with complete analysis and scoring
        """
        start_time = time.time()
        phase_timings = {}
        warnings = []
        errors = []
        
        try:
            # Clear previous logs for new session
            self.llm_service.clear_logs()

            logger.info("Starting 3-Phase Automated Diagram Grading Pipeline")

            # Auto-detect diagram type if not provided
            if diagram_type is None:
                diagram_type = DiagramFactory.detect_diagram_type_from_plantuml(student_plantuml)
                logger.info(f"Auto-detected diagram type: {diagram_type.value}")
            
            # PHASE 1: Convention Normalization
            logger.info("=" * 50)
            logger.info("PHASE 1: Convention Normalization (Multi-prompt AI chain)")
            logger.info("=" * 50)
            
            phase_start = time.time()
            phase_one_result = await self.phase_one.normalize_conventions(
                student_plantuml=student_plantuml,
                teacher_plantuml=teacher_plantuml,
                problem_description=problem_description,
                diagram_type=diagram_type
            )
            phase_timings['phase_one'] = time.time() - phase_start
            
            if not phase_one_result.success:
                errors.extend(phase_one_result.errors)
                warnings.extend(phase_one_result.warnings)
                logger.error("Phase 1 failed - using original student code")
                normalized_code = student_plantuml
            else:
                normalized_code = phase_one_result.normalized_plantuml
                warnings.extend([w.description if hasattr(w, 'description') else str(w) for w in phase_one_result.warnings])
                logger.info(f"Phase 1 completed in {phase_timings['phase_one']:.2f}s")
            
            # PHASE 2: Code-based Extraction and Metrics
            logger.info("=" * 50)
            logger.info("PHASE 2: Code-based Extraction and Metrics Calculation")
            logger.info("=" * 50)
            
            phase_start = time.time()
            phase_two_result = await self.phase_two.extract_and_calculate_metrics(
                normalized_student_plantuml=normalized_code,
                teacher_plantuml=teacher_plantuml,
                diagram_type=diagram_type
            )
            phase_timings['phase_two'] = time.time() - phase_start
            
            if not phase_two_result.success:
                errors.extend(phase_two_result.errors)
                warnings.extend(phase_two_result.warnings)
                raise Exception("Phase 2 extraction failed - cannot proceed to Phase 3")
            
            warnings.extend(phase_two_result.warnings)
            logger.info(f"Phase 2 completed in {phase_timings['phase_two']:.2f}s")
            
            # PHASE 3: AI Feedback Generation and Scoring
            logger.info("=" * 50)
            logger.info("PHASE 3: AI Feedback Generation and Final Scoring")
            logger.info("=" * 50)
            
            phase_start = time.time()
            phase_three_result = await self.phase_three.generate_feedback_and_score(
                teacher_diagram=phase_two_result.teacher_diagram,
                student_diagram=phase_two_result.student_diagram,
                metrics=phase_two_result.metrics,
                problem_description=problem_description,
                diagram_type=diagram_type,
                custom_weights=custom_weights
            )
            phase_timings['phase_three'] = time.time() - phase_start
            
            if not phase_three_result.success:
                errors.extend(["Phase 3 feedback generation failed"])
                warnings.extend(phase_three_result.warnings)
                # Continue with basic scoring from Phase 2
                final_score = self.phase_two.calculate_final_score(phase_two_result.metrics)
                grade_letter = self._get_letter_grade(final_score)
                feedback_summary = "Automated feedback generation failed. Please review manually."
            else:
                warnings.extend(phase_three_result.warnings)
                final_score = phase_three_result.final_score
                grade_letter = phase_three_result.grade_letter
                feedback_summary = phase_three_result.summary
            
            logger.info(f"Phase 3 completed in {phase_timings['phase_three']:.2f}s")
            
            # Calculate overall metrics
            total_processing_time = time.time() - start_time
            overall_confidence = self._calculate_overall_confidence(
                phase_one_result, phase_two_result, phase_three_result
            )
            
            logger.info("=" * 50)
            logger.info(f"PIPELINE COMPLETED - Final Score: {final_score}/10 ({grade_letter})")
            logger.info(f"Total Processing Time: {total_processing_time:.2f}s")
            logger.info("=" * 50)
            
            return PipelineResult(
                success=True,
                diagram_type=diagram_type,
                phase_one_result=self._serialize_phase_result(phase_one_result),
                phase_two_result=self._serialize_phase_result(phase_two_result),
                phase_three_result=self._serialize_phase_result(phase_three_result),
                final_score=final_score,
                grade_letter=grade_letter,
                feedback_summary=feedback_summary,
                total_processing_time=total_processing_time,
                phase_timings=phase_timings,
                overall_confidence=overall_confidence,
                warnings=warnings,
                errors=errors
            )
            
        except Exception as e:
            logger.error(f"Pipeline failed: {str(e)}")
            total_processing_time = time.time() - start_time
            
            return PipelineResult(
                success=False,
                diagram_type=diagram_type or DiagramType.USE_CASE,
                phase_one_result={},
                phase_two_result={},
                phase_three_result={},
                final_score=0.0,
                grade_letter='F',
                feedback_summary="Pipeline processing failed. Please check your diagram and try again.",
                total_processing_time=total_processing_time,
                phase_timings=phase_timings,
                overall_confidence=0.0,
                warnings=warnings,
                errors=errors + [str(e)]
            )
    
    def _serialize_phase_result(self, result) -> Dict[str, Any]:
        """Serialize phase result to dictionary."""
        if hasattr(result, 'model_dump'):
            return result.model_dump()
        elif hasattr(result, '__dict__'):
            return result.__dict__
        else:
            return {}
    
    def _calculate_overall_confidence(self, phase_one, phase_two, phase_three) -> float:
        """Calculate overall pipeline confidence."""
        confidences = []
        
        # Phase 1 confidence (if available)
        if hasattr(phase_one, 'confidence') and phase_one.confidence > 0:
            confidences.append(phase_one.confidence)
        
        # Phase 2 is code-based, so high confidence
        if hasattr(phase_two, 'success') and phase_two.success:
            confidences.append(0.9)
        
        # Phase 3 confidence
        if hasattr(phase_three, 'confidence') and phase_three.confidence > 0:
            confidences.append(phase_three.confidence)
        
        return sum(confidences) / len(confidences) if confidences else 0.5
    
    def _get_letter_grade(self, score: float) -> str:
        """Convert numerical score to letter grade."""
        if score >= 9.0:
            return 'A'
        elif score >= 8.0:
            return 'B'
        elif score >= 7.0:
            return 'C'
        elif score >= 6.0:
            return 'D'
        else:
            return 'F'
    
    async def get_pipeline_status(self) -> Dict[str, Any]:
        """Get comprehensive status of the pipeline."""
        return {
            "pipeline": "3-Phase Automated Diagram Grading",
            "phases": {
                "phase_1": {
                    "name": "Convention Normalization",
                    "type": "Multi-prompt AI chain",
                    "description": "Normalizes student code to match teacher conventions"
                },
                "phase_2": {
                    "name": "Code-based Extraction and Metrics",
                    "type": "Code-based parsing",
                    "description": "Extracts components and calculates quantitative metrics"
                },
                "phase_3": {
                    "name": "AI Feedback Generation and Scoring",
                    "type": "AI-based analysis",
                    "description": "Generates feedback and calculates final score"
                }
            },
            "supported_diagrams": [dt.value for dt in DiagramType],
            "llm_model": self.config.get("gemini_model", "gemini-2.5-flash-lite"),
            "rate_limit": f"{self.config.get('gemini_rate_limit_rpm', 15)} RPM",
            "scoring_scale": "0-10 points with letter grades"
        }
    
    def format_final_output(self, result: PipelineResult) -> Dict[str, Any]:
        """Format pipeline result for final output/API response."""
        return {
            "success": result.success,
            "diagram_type": result.diagram_type.value,
            "final_score": result.final_score,
            "grade_letter": result.grade_letter,
            "feedback_summary": result.feedback_summary,
            "processing_time": result.total_processing_time,
            "confidence": result.overall_confidence,
            
            # Phase-specific results
            "normalization_success": result.phase_one_result.get('success', False),
            "extraction_success": result.phase_two_result.get('success', False),
            "feedback_success": result.phase_three_result.get('success', False),
            
            # Detailed feedback (if available)
            "detailed_feedback": result.phase_three_result.get('feedback_result', {}),
            "metrics": result.phase_two_result.get('metrics', {}),
            
            "warnings": result.warnings,
            "errors": result.errors
        }
