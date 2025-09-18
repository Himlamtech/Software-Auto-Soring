"""Core logic for matching and comparing UML components."""

from typing import List, Tuple, Set
from app.core.models.uml_components import Actor, UseCase, Relationship
from app.core.models.scoring import ComparisonResult, ComponentType


class ComponentMatcher:
    """Handles semantic matching between expected and actual UML components."""
    
    def __init__(self, similarity_threshold: float = 0.8):
        """
        Initialize component matcher.
        
        Args:
            similarity_threshold: Minimum similarity score for component matching
        """
        self.similarity_threshold = similarity_threshold
    
    def match_actors(
        self,
        expected_actors: List[Actor],
        actual_actors: List[Actor]
    ) -> ComparisonResult:
        """
        Match expected and actual actors.
        
        Args:
            expected_actors: List of expected actors from problem description
            actual_actors: List of actual actors from student submission
            
        Returns:
            ComparisonResult with matching details
        """
        expected_names = {actor.name.lower().strip() for actor in expected_actors}
        actual_names = {actor.name.lower().strip() for actor in actual_actors}
        
        # Perform semantic matching
        true_positives, false_positives, false_negatives = self._semantic_match(
            expected_names, actual_names
        )
        
        return ComparisonResult(
            component_type=ComponentType.ACTOR,
            true_positives=list(true_positives),
            false_positives=list(false_positives),
            false_negatives=list(false_negatives)
        )
    
    def match_use_cases(
        self,
        expected_use_cases: List[UseCase],
        actual_use_cases: List[UseCase]
    ) -> ComparisonResult:
        """
        Match expected and actual use cases.
        
        Args:
            expected_use_cases: List of expected use cases from problem description
            actual_use_cases: List of actual use cases from student submission
            
        Returns:
            ComparisonResult with matching details
        """
        expected_names = {uc.name.lower().strip() for uc in expected_use_cases}
        actual_names = {uc.name.lower().strip() for uc in actual_use_cases}
        
        # Perform semantic matching
        true_positives, false_positives, false_negatives = self._semantic_match(
            expected_names, actual_names
        )
        
        return ComparisonResult(
            component_type=ComponentType.USE_CASE,
            true_positives=list(true_positives),
            false_positives=list(false_positives),
            false_negatives=list(false_negatives)
        )
    
    def match_relationships(
        self,
        expected_relationships: List[Relationship],
        actual_relationships: List[Relationship]
    ) -> ComparisonResult:
        """
        Match expected and actual relationships.
        
        Args:
            expected_relationships: List of expected relationships from problem description
            actual_relationships: List of actual relationships from student submission
            
        Returns:
            ComparisonResult with matching details
        """
        expected_rels = {
            f"{rel.source.lower()}-{rel.relationship_type.lower()}-{rel.target.lower()}"
            for rel in expected_relationships
        }
        actual_rels = {
            f"{rel.source.lower()}-{rel.relationship_type.lower()}-{rel.target.lower()}"
            for rel in actual_relationships
        }
        
        # Perform semantic matching
        true_positives, false_positives, false_negatives = self._semantic_match(
            expected_rels, actual_rels
        )
        
        return ComparisonResult(
            component_type=ComponentType.RELATIONSHIP,
            true_positives=list(true_positives),
            false_positives=list(false_positives),
            false_negatives=list(false_negatives)
        )
    
    def _semantic_match(
        self,
        expected: Set[str],
        actual: Set[str]
    ) -> Tuple[Set[str], Set[str], Set[str]]:
        """
        Perform semantic matching between expected and actual component sets.
        
        Args:
            expected: Set of expected component identifiers
            actual: Set of actual component identifiers
            
        Returns:
            Tuple of (true_positives, false_positives, false_negatives)
        """
        # For now, use exact matching (can be enhanced with NLP similarity)
        true_positives = expected.intersection(actual)
        false_positives = actual - expected
        false_negatives = expected - actual
        
        return true_positives, false_positives, false_negatives
    
    def _calculate_semantic_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate semantic similarity between two text strings.
        
        Args:
            text1: First text string
            text2: Second text string
            
        Returns:
            Similarity score between 0 and 1
        """
        # Placeholder for semantic similarity calculation
        # Can be enhanced with NLP models, embeddings, etc.
        if text1.lower() == text2.lower():
            return 1.0
        
        # Simple token-based similarity as fallback
        tokens1 = set(text1.lower().split())
        tokens2 = set(text2.lower().split())
        
        if not tokens1 or not tokens2:
            return 0.0
        
        intersection = tokens1.intersection(tokens2)
        union = tokens1.union(tokens2)
        
        return len(intersection) / len(union) if union else 0.0
