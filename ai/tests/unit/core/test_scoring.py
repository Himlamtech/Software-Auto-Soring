"""Unit tests for core scoring logic."""

import pytest
from app.core.scoring.metrics_calculator import MetricsCalculator
from app.core.scoring.component_matcher import ComponentMatcher
from app.core.models.scoring import ComparisonResult, ComponentType
from app.core.models.uml_components import Actor, UseCase, Relationship


class TestMetricsCalculator:
    """Test cases for MetricsCalculator."""
    
    @pytest.fixture
    def calculator(self):
        """Get metrics calculator instance."""
        return MetricsCalculator()
    
    def test_perfect_score(self, calculator):
        """Test calculation with perfect matching."""
        comparison = ComparisonResult(
            component_type=ComponentType.ACTOR,
            true_positives=["user", "admin"],
            false_positives=[],
            false_negatives=[]
        )
        
        metrics = calculator.calculate_metrics(comparison)
        
        assert metrics.precision == 1.0
        assert metrics.recall == 1.0
        assert metrics.f1_score == 1.0
        assert metrics.accuracy == 1.0
    
    def test_zero_score(self, calculator):
        """Test calculation with no matches."""
        comparison = ComparisonResult(
            component_type=ComponentType.ACTOR,
            true_positives=[],
            false_positives=["wrong1", "wrong2"],
            false_negatives=["expected1", "expected2"]
        )
        
        metrics = calculator.calculate_metrics(comparison)
        
        assert metrics.precision == 0.0
        assert metrics.recall == 0.0
        assert metrics.f1_score == 0.0
        assert metrics.accuracy == 0.0
    
    def test_partial_score(self, calculator):
        """Test calculation with partial matching."""
        comparison = ComparisonResult(
            component_type=ComponentType.ACTOR,
            true_positives=["user"],
            false_positives=["wrong"],
            false_negatives=["admin"]
        )
        
        metrics = calculator.calculate_metrics(comparison)
        
        assert metrics.precision == 0.5  # 1 TP / (1 TP + 1 FP)
        assert metrics.recall == 0.5     # 1 TP / (1 TP + 1 FN)
        assert metrics.f1_score == 0.5   # 2 * (0.5 * 0.5) / (0.5 + 0.5)
        assert metrics.accuracy == pytest.approx(0.333, rel=1e-2)  # 1 TP / (1 TP + 1 FP + 1 FN)


class TestComponentMatcher:
    """Test cases for ComponentMatcher."""
    
    @pytest.fixture
    def matcher(self):
        """Get component matcher instance."""
        return ComponentMatcher()
    
    def test_exact_actor_matching(self, matcher):
        """Test exact matching of actors."""
        expected = [Actor(name="User"), Actor(name="Admin")]
        actual = [Actor(name="User"), Actor(name="Admin")]
        
        result = matcher.match_actors(expected, actual)
        
        assert len(result.true_positives) == 2
        assert len(result.false_positives) == 0
        assert len(result.false_negatives) == 0
        assert result.component_type == ComponentType.ACTOR
    
    def test_partial_actor_matching(self, matcher):
        """Test partial matching of actors."""
        expected = [Actor(name="User"), Actor(name="Admin")]
        actual = [Actor(name="User"), Actor(name="Guest")]
        
        result = matcher.match_actors(expected, actual)
        
        assert len(result.true_positives) == 1
        assert len(result.false_positives) == 1
        assert len(result.false_negatives) == 1
        assert "user" in result.true_positives
        assert "guest" in result.false_positives
        assert "admin" in result.false_negatives
    
    def test_use_case_matching(self, matcher):
        """Test matching of use cases."""
        expected = [UseCase(name="Login"), UseCase(name="Register")]
        actual = [UseCase(name="Login"), UseCase(name="Logout")]
        
        result = matcher.match_use_cases(expected, actual)
        
        assert len(result.true_positives) == 1
        assert len(result.false_positives) == 1
        assert len(result.false_negatives) == 1
        assert result.component_type == ComponentType.USE_CASE
    
    def test_relationship_matching(self, matcher):
        """Test matching of relationships."""
        expected = [
            Relationship(source="User", target="Login", relationship_type="association"),
            Relationship(source="Admin", target="Manage", relationship_type="association")
        ]
        actual = [
            Relationship(source="User", target="Login", relationship_type="association"),
            Relationship(source="Guest", target="Browse", relationship_type="association")
        ]
        
        result = matcher.match_relationships(expected, actual)
        
        assert len(result.true_positives) == 1
        assert len(result.false_positives) == 1
        assert len(result.false_negatives) == 1
        assert result.component_type == ComponentType.RELATIONSHIP
