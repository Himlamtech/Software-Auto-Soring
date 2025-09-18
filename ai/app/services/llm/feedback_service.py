"""Abstract service for generating feedback using LLMs."""

from abc import ABC, abstractmethod
from typing import List
from app.core.models.scoring import ComponentScore, OverallScore, FeedbackItem
from app.core.models.uml_components import UMLDiagram


class LLMFeedbackService(ABC):
    """Abstract service for generating educational feedback using Large Language Models."""
    
    @abstractmethod
    async def generate_overall_feedback(
        self,
        overall_score: OverallScore,
        expected_diagram: UMLDiagram,
        actual_diagram: UMLDiagram
    ) -> List[FeedbackItem]:
        """
        Generate overall feedback for the student submission.
        
        Args:
            overall_score: Overall scoring results
            expected_diagram: Expected UML diagram
            actual_diagram: Actual student diagram
            
        Returns:
            List of feedback items with suggestions and comments
        """
        pass
    
    @abstractmethod
    async def generate_component_feedback(
        self,
        component_score: ComponentScore,
        expected_components: List[any],
        actual_components: List[any]
    ) -> List[FeedbackItem]:
        """
        Generate specific feedback for a component type.
        
        Args:
            component_score: Scoring results for specific component
            expected_components: Expected components of this type
            actual_components: Actual components of this type
            
        Returns:
            List of feedback items for this component type
        """
        pass
    
    @abstractmethod
    async def generate_strength_feedback(
        self,
        component_scores: List[ComponentScore]
    ) -> List[FeedbackItem]:
        """
        Generate feedback highlighting student's strengths.
        
        Args:
            component_scores: All component scoring results
            
        Returns:
            List of positive feedback items
        """
        pass
    
    @abstractmethod
    async def generate_improvement_suggestions(
        self,
        component_scores: List[ComponentScore],
        expected_diagram: UMLDiagram,
        actual_diagram: UMLDiagram
    ) -> List[FeedbackItem]:
        """
        Generate specific suggestions for improvement.
        
        Args:
            component_scores: All component scoring results
            expected_diagram: Expected UML diagram
            actual_diagram: Actual student diagram
            
        Returns:
            List of improvement suggestion feedback items
        """
        pass
    
    @abstractmethod
    async def generate_missing_components_feedback(
        self,
        component_scores: List[ComponentScore]
    ) -> List[FeedbackItem]:
        """
        Generate feedback about missing components.
        
        Args:
            component_scores: All component scoring results
            
        Returns:
            List of feedback items about missing components
        """
        pass
    
    @abstractmethod
    async def generate_incorrect_components_feedback(
        self,
        component_scores: List[ComponentScore]
    ) -> List[FeedbackItem]:
        """
        Generate feedback about incorrect or unnecessary components.
        
        Args:
            component_scores: All component scoring results
            
        Returns:
            List of feedback items about incorrect components
        """
        pass
