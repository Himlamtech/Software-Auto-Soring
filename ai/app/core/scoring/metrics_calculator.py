"""Core logic for calculating scoring metrics."""

from typing import List, Dict, Any
from app.core.models.scoring import ComparisonResult, ScoringMetrics, ComponentType


class MetricsCalculator:
    """Calculates scoring metrics from comparison results."""
    
    def calculate_metrics(self, comparison: ComparisonResult) -> ScoringMetrics:
        """
        Calculate precision, recall, F1-score, and accuracy from comparison results.
        
        Args:
            comparison: Result of comparing expected vs actual components
            
        Returns:
            ScoringMetrics with calculated values
        """
        tp = len(comparison.true_positives)
        fp = len(comparison.false_positives)
        fn = len(comparison.false_negatives)
        
        # Calculate metrics with zero-division protection
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1_score = (
            2 * (precision * recall) / (precision + recall)
            if (precision + recall) > 0
            else 0.0
        )
        accuracy = tp / (tp + fp + fn) if (tp + fp + fn) > 0 else 0.0
        
        return ScoringMetrics(
            precision=precision,
            recall=recall,
            f1_score=f1_score,
            accuracy=accuracy
        )
    
    def aggregate_metrics(
        self,
        component_metrics: List[ScoringMetrics],
        weights: List[float]
    ) -> ScoringMetrics:
        """
        Aggregate metrics from multiple components with weights.
        
        Args:
            component_metrics: List of metrics for each component type
            weights: Weights for each component type
            
        Returns:
            Aggregated ScoringMetrics
        """
        if not component_metrics or not weights:
            return ScoringMetrics(precision=0.0, recall=0.0, f1_score=0.0, accuracy=0.0)
        
        total_weight = sum(weights)
        if total_weight == 0:
            return ScoringMetrics(precision=0.0, recall=0.0, f1_score=0.0, accuracy=0.0)
        
        weighted_precision = sum(
            m.precision * w for m, w in zip(component_metrics, weights)
        ) / total_weight
        
        weighted_recall = sum(
            m.recall * w for m, w in zip(component_metrics, weights)
        ) / total_weight
        
        weighted_f1 = sum(
            m.f1_score * w for m, w in zip(component_metrics, weights)
        ) / total_weight
        
        weighted_accuracy = sum(
            m.accuracy * w for m, w in zip(component_metrics, weights)
        ) / total_weight
        
        return ScoringMetrics(
            precision=weighted_precision,
            recall=weighted_recall,
            f1_score=weighted_f1,
            accuracy=weighted_accuracy
        )
    
    def calculate_final_score(
        self,
        overall_metrics: ScoringMetrics,
        scale: float = 10.0
    ) -> float:
        """
        Calculate final score from overall metrics.
        
        Args:
            overall_metrics: Aggregated metrics
            scale: Scale for final score (default: 10.0)
            
        Returns:
            Final score scaled to the specified range
        """
        # Weighted combination of metrics
        score = (
            overall_metrics.f1_score * 0.4 +
            overall_metrics.accuracy * 0.3 +
            overall_metrics.precision * 0.2 +
            overall_metrics.recall * 0.1
        )
        
        return min(score * scale, scale)
