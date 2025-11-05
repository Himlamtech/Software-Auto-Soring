"""Phase 2: Code-Based Extraction and Metrics Calculation."""

from typing import Dict, Any, Optional
from pydantic import BaseModel
import time
from loguru import logger

from .use_case_parser import UseCaseParser
from .class_diagram_parser import ClassDiagramParser
from .metrics_engine import MetricsEngine, DiagramMetrics
from app.core.models.diagrams.diagram_factory import DiagramType, DiagramFactory, DiagramUnion


class ExtractionResult(BaseModel):
    """Result of Phase 2 extraction and metrics calculation."""
    success: bool
    diagram_type: DiagramType
    
    # Extracted diagrams
    teacher_diagram: Dict[str, Any]  # Serialized diagram
    student_diagram: Dict[str, Any]  # Serialized diagram
    
    # Metrics
    metrics: Dict[str, Any]  # Serialized DiagramMetrics
    
    # Metadata
    processing_time: float
    errors: list[str]
    warnings: list[str]


class PhaseTwoExtractor:
    """
    Phase 2 orchestrator for code-based extraction and metrics calculation.
    
    This service:
    1. Parses both teacher and student diagrams using code-based parsers
    2. Extracts structured components
    3. Calculates quantitative metrics (F1, Precision, Recall, Accuracy)
    4. Identifies specific errors and discrepancies
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Phase 2 extractor.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        
        # Initialize parsers
        self.use_case_parser = UseCaseParser()
        self.class_parser = ClassDiagramParser()
        # TODO: Add sequence parser when implemented
        
        # Initialize metrics engine
        similarity_threshold = config.get("similarity_threshold", 0.85)
        self.metrics_engine = MetricsEngine(similarity_threshold)
    
    async def extract_and_calculate_metrics(
        self,
        normalized_student_plantuml: str,
        teacher_plantuml: str,
        diagram_type: DiagramType
    ) -> ExtractionResult:
        """
        Extract components and calculate metrics for both diagrams.
        
        Args:
            normalized_student_plantuml: Student's normalized PlantUML code
            teacher_plantuml: Teacher's reference PlantUML code
            diagram_type: Type of diagram being processed
            
        Returns:
            ExtractionResult with extracted components and calculated metrics
        """
        start_time = time.time()
        errors = []
        warnings = []
        
        try:
            logger.info(f"Starting Phase 2: Code-based extraction for {diagram_type.value} diagram")
            
            # Extract teacher diagram
            logger.info("Extracting teacher diagram components...")
            teacher_diagram = self._extract_diagram_components(teacher_plantuml, diagram_type)
            
            # Extract student diagram
            logger.info("Extracting student diagram components...")
            student_diagram = self._extract_diagram_components(normalized_student_plantuml, diagram_type)
            
            # Calculate metrics
            logger.info("Calculating quantitative metrics...")
            metrics = self.metrics_engine.calculate_diagram_metrics(
                teacher_diagram, student_diagram, diagram_type
            )
            
            # Log metrics summary
            logger.info(f"Metrics calculated - Overall F1: {metrics.overall_metrics.f1_score:.3f}, "
                       f"Precision: {metrics.overall_metrics.precision:.3f}, "
                       f"Recall: {metrics.overall_metrics.recall:.3f}")
            
            processing_time = time.time() - start_time
            
            return ExtractionResult(
                success=True,
                diagram_type=diagram_type,
                teacher_diagram=self._serialize_diagram(teacher_diagram),
                student_diagram=self._serialize_diagram(student_diagram),
                metrics=self._serialize_metrics(metrics),
                processing_time=processing_time,
                errors=errors,
                warnings=warnings
            )
            
        except Exception as e:
            logger.error(f"Phase 2 extraction failed: {str(e)}")
            processing_time = time.time() - start_time
            
            return ExtractionResult(
                success=False,
                diagram_type=diagram_type,
                teacher_diagram={},
                student_diagram={},
                metrics={},
                processing_time=processing_time,
                errors=[str(e)],
                warnings=warnings
            )
    
    def _extract_diagram_components(self, plantuml_code: str, diagram_type: DiagramType) -> DiagramUnion:
        """Extract components from PlantUML code based on diagram type."""
        
        if diagram_type == DiagramType.USE_CASE:
            return self.use_case_parser.parse_diagram(plantuml_code)
        
        elif diagram_type == DiagramType.CLASS:
            return self.class_parser.parse_diagram(plantuml_code)
        
        elif diagram_type == DiagramType.SEQUENCE:
            # TODO: Implement sequence parser
            logger.warning("Sequence diagram parsing not yet implemented")
            return DiagramFactory.create_diagram(diagram_type)
        
        else:
            raise ValueError(f"Unsupported diagram type: {diagram_type}")
    
    def _serialize_diagram(self, diagram: DiagramUnion) -> Dict[str, Any]:
        """Serialize diagram to dictionary for JSON storage."""
        return diagram.model_dump()
    
    def _serialize_metrics(self, metrics: DiagramMetrics) -> Dict[str, Any]:
        """Serialize metrics to dictionary for JSON storage."""
        # Convert ComponentMetrics dataclasses to dicts
        component_metrics_dict = {}
        for component_type, metrics_obj in metrics.component_metrics.items():
            component_metrics_dict[component_type] = {
                'true_positives': metrics_obj.true_positives,
                'false_positives': metrics_obj.false_positives,
                'false_negatives': metrics_obj.false_negatives,
                'precision': metrics_obj.precision,
                'recall': metrics_obj.recall,
                'f1_score': metrics_obj.f1_score,
                'accuracy': metrics_obj.accuracy
            }
        
        overall_metrics_dict = {
            'true_positives': metrics.overall_metrics.true_positives,
            'false_positives': metrics.overall_metrics.false_positives,
            'false_negatives': metrics.overall_metrics.false_negatives,
            'precision': metrics.overall_metrics.precision,
            'recall': metrics.overall_metrics.recall,
            'f1_score': metrics.overall_metrics.f1_score,
            'accuracy': metrics.overall_metrics.accuracy
        }
        
        return {
            'diagram_type': metrics.diagram_type.value,
            'component_metrics': component_metrics_dict,
            'overall_metrics': overall_metrics_dict,
            'similarity_score': metrics.similarity_score,
            'total_expected': metrics.total_expected,
            'total_actual': metrics.total_actual,
            'total_matched': metrics.total_matched
        }
    
    def get_component_differences(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract specific component differences for Phase 3 feedback generation.
        
        Args:
            metrics: Serialized metrics from extraction result
            
        Returns:
            Dictionary with detailed component differences
        """
        differences = {
            'missing_components': [],
            'extra_components': [],
            'incorrect_relationships': [],
            'component_details': {}
        }
        
        # Analyze each component type
        for component_type, component_metrics in metrics.get('component_metrics', {}).items():
            false_negatives = component_metrics.get('false_negatives', 0)
            false_positives = component_metrics.get('false_positives', 0)
            
            if false_negatives > 0:
                differences['missing_components'].append({
                    'type': component_type,
                    'count': false_negatives,
                    'severity': 'high' if component_type in ['class', 'use_case', 'participant'] else 'medium'
                })
            
            if false_positives > 0:
                differences['extra_components'].append({
                    'type': component_type,
                    'count': false_positives,
                    'severity': 'medium'
                })
            
            differences['component_details'][component_type] = {
                'precision': component_metrics.get('precision', 0),
                'recall': component_metrics.get('recall', 0),
                'f1_score': component_metrics.get('f1_score', 0)
            }
        
        return differences
    
    def calculate_final_score(self, metrics: Dict[str, Any], weights: Dict[str, float] = None) -> float:
        """
        Calculate final score on 10-point scale from metrics.
        
        Args:
            metrics: Serialized metrics
            weights: Component weights for scoring
            
        Returns:
            Final score (0-10)
        """
        if not weights:
            # Default weights
            weights = {
                'precision': 0.3,
                'recall': 0.3,
                'f1_score': 0.4
            }
        
        overall_metrics = metrics.get('overall_metrics', {})
        
        precision = overall_metrics.get('precision', 0)
        recall = overall_metrics.get('recall', 0)
        f1_score = overall_metrics.get('f1_score', 0)
        
        # Weighted score
        weighted_score = (
            precision * weights.get('precision', 0.3) +
            recall * weights.get('recall', 0.3) +
            f1_score * weights.get('f1_score', 0.4)
        )
        
        # Convert to 10-point scale
        final_score = weighted_score * 10
        
        # Apply penalties for severe issues
        similarity_score = metrics.get('similarity_score', 1.0)
        if similarity_score < 0.5:
            final_score *= 0.8  # 20% penalty for very low similarity
        
        return round(final_score, 2)
    
    async def get_extraction_status(self) -> Dict[str, Any]:
        """Get status information about the extraction service."""
        return {
            "service": "PhaseTwoExtractor",
            "phase": "Phase 2 - Code-based Extraction and Metrics",
            "capabilities": [
                "PlantUML parsing",
                "Component extraction",
                "Quantitative metrics calculation",
                "Semantic similarity matching"
            ],
            "supported_diagrams": [dt.value for dt in DiagramType],
            "metrics_calculated": [
                "Precision",
                "Recall", 
                "F1-Score",
                "Accuracy"
            ],
            "similarity_threshold": self.metrics_engine.similarity_threshold
        }
