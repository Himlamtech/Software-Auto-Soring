"""Phase 1 Orchestrator: Multi-Prompt Convention Normalization Chain."""

from typing import Dict, Any, Optional
from pydantic import BaseModel
import asyncio
import time
from loguru import logger

from .convention_analyzer import ConventionAnalyzer, ConventionAnalysisResult
from .difference_detector import DifferenceDetector, DifferenceDetectionResult
from .code_normalizer import CodeNormalizer, CodeNormalizationResult
from .normalization_validator import NormalizationValidator, ValidationResult, ValidationIssue
from app.core.models.diagrams.diagram_factory import DiagramType, DiagramFactory


class NormalizationChainResult(BaseModel):
    """Complete result of the Phase 1 normalization chain."""
    success: bool
    normalized_plantuml: str
    original_plantuml: str
    diagram_type: DiagramType
    
    # Results from each step
    convention_analysis: ConventionAnalysisResult
    difference_detection: DifferenceDetectionResult
    code_normalization: CodeNormalizationResult
    validation_result: ValidationResult
    
    # Metadata
    processing_time: float
    retries_used: int
    final_confidence: float
    warnings: list[ValidationIssue]


class NormalizationOrchestrator:
    """
    Orchestrates the multi-prompt AI chain for Phase 1 convention normalization.
    
    This is the main service that coordinates all 4 steps of Phase 1:
    1. Convention Analysis
    2. Difference Detection  
    3. Code Normalization
    4. Validation
    """
    
    def __init__(self, llm_service, config: Dict[str, Any]):
        """
        Initialize the normalization orchestrator.
        
        Args:
            llm_service: LLM service for AI operations
            config: Configuration dictionary with settings
        """
        self.llm_service = llm_service
        self.config = config
        
        # Initialize step services
        self.convention_analyzer = ConventionAnalyzer(llm_service)
        self.difference_detector = DifferenceDetector(llm_service)
        self.code_normalizer = CodeNormalizer(llm_service)
        self.validator = NormalizationValidator(llm_service)
        
        # Configuration
        self.max_retries = config.get("max_retries", 3)
        self.rate_limit_delay = 60 / config.get("rate_limit_rpm", 15)  # Convert RPM to seconds
    
    async def normalize_conventions(
        self,
        student_plantuml: str,
        teacher_plantuml: str,
        problem_description: str,
        diagram_type: Optional[DiagramType] = None
    ) -> NormalizationChainResult:
        """
        Execute the complete multi-prompt normalization chain.
        
        Args:
            student_plantuml: Student's original PlantUML code
            teacher_plantuml: Teacher's reference PlantUML code
            problem_description: Problem description for context
            diagram_type: Type of diagram (auto-detected if None)
            
        Returns:
            NormalizationChainResult with complete normalization results
        """
        start_time = time.time()
        retries_used = 0
        warnings = []
        
        try:
            # Auto-detect diagram type if not provided
            if diagram_type is None:
                diagram_type = DiagramFactory.detect_diagram_type_from_plantuml(teacher_plantuml)
                logger.info(f"Auto-detected diagram type: {diagram_type}")
            
            # Execute the 4-step chain with retries
            for attempt in range(self.max_retries + 1):
                try:
                    result = await self._execute_normalization_chain(
                        student_plantuml,
                        teacher_plantuml,
                        problem_description,
                        diagram_type
                    )
                    
                    processing_time = time.time() - start_time
                    
                    return NormalizationChainResult(
                        success=True,
                        normalized_plantuml=result["validation_result"].validated_plantuml,
                        original_plantuml=student_plantuml,
                        diagram_type=diagram_type,
                        convention_analysis=result["convention_analysis"],
                        difference_detection=result["difference_detection"],
                        code_normalization=result["code_normalization"],
                        validation_result=result["validation_result"],
                        processing_time=processing_time,
                        retries_used=retries_used,
                        final_confidence=result["validation_result"].confidence,
                        warnings=warnings + result["validation_result"].issues
                    )
                    
                except Exception as e:
                    retries_used += 1
                    logger.warning(f"Normalization attempt {attempt + 1} failed: {str(e)}")
                    
                    if attempt < self.max_retries:
                        warnings.append(f"Retry {attempt + 1}: {str(e)}")
                        await asyncio.sleep(self.rate_limit_delay * 2)  # Longer delay on retry
                    else:
                        raise e
            
        except Exception as e:
            logger.error(f"Normalization chain failed after {retries_used} retries: {str(e)}")
            processing_time = time.time() - start_time
            
            # Return failure result with original code
            return NormalizationChainResult(
                success=False,
                normalized_plantuml=student_plantuml,  # Return original on failure
                original_plantuml=student_plantuml,
                diagram_type=diagram_type or DiagramType.USE_CASE,
                convention_analysis=self._create_empty_convention_analysis(diagram_type or DiagramType.USE_CASE),
                difference_detection=self._create_empty_difference_detection(diagram_type or DiagramType.USE_CASE),
                code_normalization=self._create_empty_normalization(student_plantuml),
                validation_result=self._create_empty_validation(student_plantuml),
                processing_time=processing_time,
                retries_used=retries_used,
                final_confidence=0.0,
                warnings=warnings + [f"Normalization failed: {str(e)}"]
            )
    
    async def _execute_normalization_chain(
        self,
        student_plantuml: str,
        teacher_plantuml: str,
        problem_description: str,
        diagram_type: DiagramType
    ) -> Dict[str, Any]:
        """Execute the 4-step normalization chain."""
        
        logger.info("Starting Phase 1: Convention Normalization Chain")
        
        # Step 1: Analyze teacher conventions
        logger.info("Step 1: Analyzing teacher conventions...")
        convention_analysis = await self.convention_analyzer.analyze_teacher_conventions(
            teacher_plantuml, problem_description, diagram_type, step_name="Phase 1 Step 1: Convention Analysis"
        )
        await asyncio.sleep(self.rate_limit_delay)  # Rate limiting

        # Step 2: Detect differences
        logger.info("Step 2: Detecting convention differences...")
        difference_detection = await self.difference_detector.detect_differences(
            student_plantuml, convention_analysis, problem_description, step_name="Phase 1 Step 2: Difference Detection"
        )
        await asyncio.sleep(self.rate_limit_delay)  # Rate limiting

        # Step 3: Normalize code
        logger.info("Step 3: Generating normalized code...")
        code_normalization = await self.code_normalizer.normalize_code(
            student_plantuml, convention_analysis, difference_detection, problem_description, step_name="Phase 1 Step 3: Code Normalization"
        )
        await asyncio.sleep(self.rate_limit_delay)  # Rate limiting

        # Step 4: Validate normalization
        logger.info("Step 4: Validating normalized code...")
        validation_result = await self.validator.validate_normalization(
            student_plantuml, code_normalization, convention_analysis, problem_description, step_name="Phase 1 Step 4: Validation"
        )
        
        logger.info("Phase 1 normalization chain completed successfully")
        
        return {
            "convention_analysis": convention_analysis,
            "difference_detection": difference_detection,
            "code_normalization": code_normalization,
            "validation_result": validation_result
        }
    
    def _create_empty_convention_analysis(self, diagram_type: DiagramType) -> ConventionAnalysisResult:
        """Create empty convention analysis for failure cases."""
        return ConventionAnalysisResult(
            diagram_type=diagram_type,
            naming_conventions=[],
            structural_patterns=[],
            style_preferences=[],
            overall_confidence=0.0
        )
    
    def _create_empty_difference_detection(self, diagram_type: DiagramType) -> DifferenceDetectionResult:
        """Create empty difference detection for failure cases."""
        return DifferenceDetectionResult(
            diagram_type=diagram_type,
            differences=[],
            total_differences=0,
            severity_breakdown={"low": 0, "medium": 0, "high": 0},
            overall_confidence=0.0
        )
    
    def _create_empty_normalization(self, original_code: str) -> CodeNormalizationResult:
        """Create empty normalization result for failure cases."""
        return CodeNormalizationResult(
            normalized_plantuml=original_code,
            applied_rules=[],
            changes_made=[],
            confidence=0.0,
            warnings=["Normalization failed"]
        )
    
    def _create_empty_validation(self, code: str) -> ValidationResult:
        """Create empty validation result for failure cases."""
        return ValidationResult(
            is_valid=False,
            validated_plantuml=code,
            issues=[],
            syntax_valid=False,
            logic_preserved=True,  # Assume preserved since we're using original
            conventions_matched=False,
            confidence=0.0
        )
    
    async def get_normalization_status(self) -> Dict[str, Any]:
        """Get status information about the normalization service."""
        return {
            "service": "NormalizationOrchestrator",
            "phase": "Phase 1 - Convention Normalization",
            "steps": [
                "1. Convention Analysis",
                "2. Difference Detection", 
                "3. Code Normalization",
                "4. Validation"
            ],
            "max_retries": self.max_retries,
            "rate_limit_delay": self.rate_limit_delay,
            "supported_diagrams": [dt.value for dt in DiagramType]
        }
