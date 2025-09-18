"""Main scoring pipeline orchestration."""

from typing import List, Dict, Any, Optional
import time
from app.core.models.input_output import ScoringRequest
from app.core.models.scoring import ScoringResult, ComponentScore, OverallScore
from app.core.models.uml_components import UMLDiagram
from app.core.scoring.component_matcher import ComponentMatcher
from app.core.scoring.metrics_calculator import MetricsCalculator


class ScoringPipeline:
    """
    Main pipeline for processing UML diagram scoring requests.
    
    Orchestrates the 5-step process:
    1. Input Collection & Validation
    2. LLM-based Extraction
    3. Semantic Comparison
    4. Metrics Calculation
    5. Feedback Generation
    """
    
    def __init__(
        self,
        component_matcher: Optional[ComponentMatcher] = None,
        metrics_calculator: Optional[MetricsCalculator] = None
    ):
        """
        Initialize scoring pipeline.
        
        Args:
            component_matcher: Component matching service
            metrics_calculator: Metrics calculation service
        """
        self.component_matcher = component_matcher or ComponentMatcher()
        self.metrics_calculator = metrics_calculator or MetricsCalculator()
        
        # Default weights for component types
        self.default_weights = {
            "actor": 0.3,
            "use_case": 0.5,
            "relationship": 0.2
        }
    
    async def process_scoring_request(self, request: ScoringRequest) -> ScoringResult:
        """
        Process a complete scoring request through the pipeline.
        
        Args:
            request: Scoring request with submission and problem description
            
        Returns:
            Complete scoring result with metrics and feedback
        """
        start_time = time.time()
        
        # Step 1: Validate input (implemented in pipeline)
        self._validate_request(request)
        
        # Step 2: Extract components using LLM services (to be injected)
        expected_diagram = await self._extract_expected_components(request.problem)
        actual_diagram = await self._extract_actual_components(request.submission)
        
        # Step 3: Compare components
        component_scores = self._compare_components(expected_diagram, actual_diagram)
        
        # Step 4: Calculate overall score
        overall_score = self._calculate_overall_score(
            component_scores,
            request.scoring_weights or self.default_weights
        )
        
        # Step 5: Generate feedback (to be implemented with LLM service)
        feedback_items = await self._generate_feedback(
            component_scores,
            overall_score,
            expected_diagram,
            actual_diagram
        )
        
        processing_time = time.time() - start_time
        
        return ScoringResult(
            score=overall_score,
            feedback=feedback_items,
            processing_time=processing_time,
            llm_model_used="placeholder"  # Will be set by LLM service
        )
    
    def _validate_request(self, request: ScoringRequest) -> None:
        """
        Validate the scoring request.
        
        Args:
            request: Scoring request to validate
            
        Raises:
            ValueError: If request is invalid
        """
        if not request.submission.plantuml_code.strip():
            raise ValueError("PlantUML code cannot be empty")
        
        if not request.problem.description.strip():
            raise ValueError("Problem description cannot be empty")
    
    async def _extract_expected_components(self, problem) -> UMLDiagram:
        """
        Extract expected components from problem description.
        
        Args:
            problem: Problem description
            
        Returns:
            UMLDiagram with expected components
        """
        # Placeholder - will be implemented with LLM service injection
        return UMLDiagram(actors=[], use_cases=[], relationships=[])
    
    async def _extract_actual_components(self, submission) -> UMLDiagram:
        """
        Extract actual components from student submission.
        
        Args:
            submission: Student submission
            
        Returns:
            UMLDiagram with actual components
        """
        # Placeholder - will be implemented with LLM service injection
        return UMLDiagram(actors=[], use_cases=[], relationships=[])
    
    def _compare_components(
        self,
        expected: UMLDiagram,
        actual: UMLDiagram
    ) -> List[ComponentScore]:
        """
        Compare expected and actual components.
        
        Args:
            expected: Expected UML diagram
            actual: Actual UML diagram
            
        Returns:
            List of component scores
        """
        component_scores = []
        
        # Compare actors
        actor_comparison = self.component_matcher.match_actors(
            expected.actors, actual.actors
        )
        actor_metrics = self.metrics_calculator.calculate_metrics(actor_comparison)
        component_scores.append(ComponentScore(
            component_type=actor_comparison.component_type,
            metrics=actor_metrics,
            comparison=actor_comparison,
            weight=self.default_weights["actor"]
        ))
        
        # Compare use cases
        usecase_comparison = self.component_matcher.match_use_cases(
            expected.use_cases, actual.use_cases
        )
        usecase_metrics = self.metrics_calculator.calculate_metrics(usecase_comparison)
        component_scores.append(ComponentScore(
            component_type=usecase_comparison.component_type,
            metrics=usecase_metrics,
            comparison=usecase_comparison,
            weight=self.default_weights["use_case"]
        ))
        
        # Compare relationships
        rel_comparison = self.component_matcher.match_relationships(
            expected.relationships, actual.relationships
        )
        rel_metrics = self.metrics_calculator.calculate_metrics(rel_comparison)
        component_scores.append(ComponentScore(
            component_type=rel_comparison.component_type,
            metrics=rel_metrics,
            comparison=rel_comparison,
            weight=self.default_weights["relationship"]
        ))
        
        return component_scores
    
    def _calculate_overall_score(
        self,
        component_scores: List[ComponentScore],
        weights: Dict[str, float]
    ) -> OverallScore:
        """
        Calculate overall score from component scores.
        
        Args:
            component_scores: List of component scores
            weights: Weights for each component type
            
        Returns:
            Overall score with aggregated metrics
        """
        metrics_list = [cs.metrics for cs in component_scores]
        weights_list = [
            weights.get(cs.component_type.value, cs.weight)
            for cs in component_scores
        ]
        
        overall_metrics = self.metrics_calculator.aggregate_metrics(
            metrics_list, weights_list
        )
        
        final_score = self.metrics_calculator.calculate_final_score(overall_metrics)
        
        return OverallScore(
            final_score=final_score,
            component_scores=component_scores,
            overall_metrics=overall_metrics
        )
    
    async def _generate_feedback(
        self,
        component_scores: List[ComponentScore],
        overall_score: OverallScore,
        expected: UMLDiagram,
        actual: UMLDiagram
    ) -> List[Any]:
        """
        Generate feedback using LLM service.
        
        Args:
            component_scores: Component scoring results
            overall_score: Overall scoring result
            expected: Expected diagram
            actual: Actual diagram
            
        Returns:
            List of feedback items
        """
        # Placeholder - will be implemented with LLM service injection
        return []
