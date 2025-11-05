"""Final score calculation for Phase 3."""

from typing import Dict, Any, List
from pydantic import BaseModel
from .error_analyzer import ErrorAnalysisResult
from .feedback_generator import FeedbackGenerationResult
from app.core.models.diagrams.diagram_factory import DiagramType


class ScoreBreakdown(BaseModel):
    """Breakdown of how the final score was calculated."""
    base_score: float  # Score from quantitative metrics
    penalties: Dict[str, float]  # Penalties applied
    bonuses: Dict[str, float]  # Bonuses applied
    final_score: float  # Final score (0-10)
    grade_letter: str  # Letter grade equivalent
    explanation: str  # Explanation of the scoring


class ScoreCalculator:
    """Calculates final 10-point scale score from metrics and feedback."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize score calculator.
        
        Args:
            config: Configuration with scoring weights and thresholds
        """
        self.config = config
        
        # Default scoring weights
        self.default_weights = {
            'precision': 0.25,
            'recall': 0.25,
            'f1_score': 0.35,
            'accuracy': 0.15
        }
        
        # Penalty/bonus factors
        self.severity_penalties = {
            'critical': 2.0,
            'high': 1.5,
            'medium': 1.0,
            'low': 0.5
        }
        
        # Grade thresholds
        self.grade_thresholds = {
            'A': 9.0,
            'B': 8.0,
            'C': 7.0,
            'D': 6.0,
            'F': 0.0
        }
    
    def calculate_final_score(
        self,
        metrics: Dict[str, Any],
        error_analysis: ErrorAnalysisResult,
        feedback_result: FeedbackGenerationResult,
        diagram_type: DiagramType,
        custom_weights: Dict[str, float] = None
    ) -> ScoreBreakdown:
        """
        Calculate final score on 10-point scale.
        
        Args:
            metrics: Quantitative metrics from Phase 2
            error_analysis: Error analysis from Phase 3
            feedback_result: Generated feedback
            diagram_type: Type of diagram
            custom_weights: Custom scoring weights
            
        Returns:
            ScoreBreakdown with detailed scoring information
        """
        # Use custom weights or defaults
        weights = custom_weights or self.default_weights
        
        # Calculate base score from metrics
        base_score = self._calculate_base_score(metrics, weights)
        
        # Apply penalties for errors
        penalties = self._calculate_penalties(error_analysis, feedback_result)
        
        # Apply bonuses for good practices
        bonuses = self._calculate_bonuses(metrics, feedback_result)
        
        # Calculate final score
        final_score = base_score
        for penalty_value in penalties.values():
            final_score -= penalty_value
        for bonus_value in bonuses.values():
            final_score += bonus_value
        
        # Clamp to 0-10 range
        final_score = max(0.0, min(10.0, final_score))
        
        # Determine letter grade
        grade_letter = self._get_letter_grade(final_score)
        
        # Generate explanation
        explanation = self._generate_score_explanation(
            base_score, penalties, bonuses, final_score, diagram_type
        )
        
        return ScoreBreakdown(
            base_score=round(base_score, 2),
            penalties=penalties,
            bonuses=bonuses,
            final_score=round(final_score, 2),
            grade_letter=grade_letter,
            explanation=explanation
        )
    
    def _calculate_base_score(self, metrics: Dict[str, Any], weights: Dict[str, float]) -> float:
        """Calculate base score from quantitative metrics."""
        overall_metrics = metrics.get('overall_metrics', {})
        
        precision = overall_metrics.get('precision', 0.0)
        recall = overall_metrics.get('recall', 0.0)
        f1_score = overall_metrics.get('f1_score', 0.0)
        accuracy = overall_metrics.get('accuracy', 0.0)
        
        # Weighted average of metrics
        base_score = (
            precision * weights.get('precision', 0.25) +
            recall * weights.get('recall', 0.25) +
            f1_score * weights.get('f1_score', 0.35) +
            accuracy * weights.get('accuracy', 0.15)
        )
        
        # Convert to 10-point scale
        return base_score * 10
    
    def _calculate_penalties(
        self,
        error_analysis: ErrorAnalysisResult,
        feedback_result: FeedbackGenerationResult
    ) -> Dict[str, float]:
        """Calculate penalties based on errors and feedback."""
        penalties = {}
        
        # Penalty for total number of errors
        if error_analysis.total_errors > 0:
            error_penalty = min(2.0, error_analysis.total_errors * 0.2)
            penalties['total_errors'] = error_penalty
        
        # Severity-based penalties
        severity_penalty = 0.0
        for severity, count in error_analysis.severity_breakdown.items():
            if count > 0:
                penalty_factor = self.severity_penalties.get(severity, 1.0)
                severity_penalty += count * penalty_factor * 0.1
        
        if severity_penalty > 0:
            penalties['severity_based'] = min(3.0, severity_penalty)
        
        # Penalty for low confidence in analysis
        if error_analysis.confidence < 0.7:
            penalties['low_confidence'] = 0.5
        
        # Penalty for critical missing components
        critical_missing = any(
            cat.category == 'missing_components' and cat.severity in ['high', 'critical']
            for cat in error_analysis.error_categories
        )
        if critical_missing:
            penalties['critical_missing'] = 1.0
        
        return penalties
    
    def _calculate_bonuses(
        self,
        metrics: Dict[str, Any],
        feedback_result: FeedbackGenerationResult
    ) -> Dict[str, float]:
        """Calculate bonuses for good practices."""
        bonuses = {}
        
        # Bonus for high similarity score
        similarity_score = metrics.get('similarity_score', 0.0)
        if similarity_score > 0.9:
            bonuses['high_similarity'] = 0.5
        elif similarity_score > 0.8:
            bonuses['good_similarity'] = 0.3
        
        # Bonus for having strengths identified
        if len(feedback_result.strengths) >= 2:
            bonuses['identified_strengths'] = 0.3
        
        # Bonus for perfect component matching in any category
        component_metrics = metrics.get('component_metrics', {})
        perfect_components = [
            comp_type for comp_type, comp_metrics in component_metrics.items()
            if comp_metrics.get('f1_score', 0) == 1.0
        ]
        if perfect_components:
            bonuses['perfect_components'] = len(perfect_components) * 0.2
        
        # Bonus for high overall precision (indicates careful work)
        overall_precision = metrics.get('overall_metrics', {}).get('precision', 0)
        if overall_precision > 0.95:
            bonuses['high_precision'] = 0.3
        
        return bonuses
    
    def _get_letter_grade(self, score: float) -> str:
        """Convert numerical score to letter grade."""
        for grade, threshold in self.grade_thresholds.items():
            if score >= threshold:
                return grade
        return 'F'
    
    def _generate_score_explanation(
        self,
        base_score: float,
        penalties: Dict[str, float],
        bonuses: Dict[str, float],
        final_score: float,
        diagram_type: DiagramType
    ) -> str:
        """Generate human-readable explanation of the scoring."""
        explanation_parts = [
            f"Score Calculation for {diagram_type.value.title()} Diagram:",
            f"Base Score (from metrics): {base_score:.2f}/10"
        ]
        
        if penalties:
            explanation_parts.append("\nPenalties Applied:")
            for penalty_type, penalty_value in penalties.items():
                penalty_desc = self._get_penalty_description(penalty_type)
                explanation_parts.append(f"- {penalty_desc}: -{penalty_value:.2f}")
        
        if bonuses:
            explanation_parts.append("\nBonuses Applied:")
            for bonus_type, bonus_value in bonuses.items():
                bonus_desc = self._get_bonus_description(bonus_type)
                explanation_parts.append(f"- {bonus_desc}: +{bonus_value:.2f}")
        
        explanation_parts.append(f"\nFinal Score: {final_score:.2f}/10")
        
        # Add performance interpretation
        if final_score >= 9.0:
            explanation_parts.append("Excellent work! Your diagram demonstrates strong understanding of UML concepts.")
        elif final_score >= 8.0:
            explanation_parts.append("Good work! Your diagram shows solid understanding with room for minor improvements.")
        elif final_score >= 7.0:
            explanation_parts.append("Satisfactory work. Your diagram captures the main concepts but needs some improvements.")
        elif final_score >= 6.0:
            explanation_parts.append("Your diagram shows basic understanding but requires significant improvements.")
        else:
            explanation_parts.append("Your diagram needs substantial revision. Please review the feedback carefully.")
        
        return "\n".join(explanation_parts)
    
    def _get_penalty_description(self, penalty_type: str) -> str:
        """Get human-readable description for penalty type."""
        descriptions = {
            'total_errors': 'Multiple errors found',
            'severity_based': 'High-severity errors',
            'low_confidence': 'Uncertain analysis',
            'critical_missing': 'Missing essential components'
        }
        return descriptions.get(penalty_type, penalty_type.replace('_', ' ').title())
    
    def _get_bonus_description(self, bonus_type: str) -> str:
        """Get human-readable description for bonus type."""
        descriptions = {
            'high_similarity': 'Excellent similarity to reference',
            'good_similarity': 'Good similarity to reference',
            'identified_strengths': 'Multiple strengths identified',
            'perfect_components': 'Perfect component matching',
            'high_precision': 'Very precise diagram'
        }
        return descriptions.get(bonus_type, bonus_type.replace('_', ' ').title())
