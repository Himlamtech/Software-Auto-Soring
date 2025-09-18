"""Abstract service for extracting UML components using LLMs."""

from abc import ABC, abstractmethod
from typing import List, Optional
from app.core.models.uml_components import UMLDiagram, Actor, UseCase, Relationship
from app.core.models.input_output import StudentSubmission, ProblemDescription


class LLMExtractionService(ABC):
    """Abstract service for extracting UML components using Large Language Models."""
    
    @abstractmethod
    async def extract_from_plantuml(
        self,
        plantuml_code: str,
        context: Optional[str] = None
    ) -> UMLDiagram:
        """
        Extract UML components from PlantUML code using LLM.
        
        Args:
            plantuml_code: PlantUML code to analyze
            context: Additional context for extraction
            
        Returns:
            UMLDiagram with extracted components
        """
        pass
    
    @abstractmethod
    async def extract_from_problem_description(
        self,
        problem: ProblemDescription
    ) -> UMLDiagram:
        """
        Extract expected UML components from problem description using LLM.
        
        Args:
            problem: Problem description with requirements
            
        Returns:
            UMLDiagram with expected components
        """
        pass
    
    @abstractmethod
    async def extract_actors(
        self,
        text: str,
        extraction_type: str = "plantuml"
    ) -> List[Actor]:
        """
        Extract actors from text using optimized prompts.
        
        Args:
            text: Text to extract actors from (PlantUML or problem description)
            extraction_type: Type of extraction ("plantuml" or "problem")
            
        Returns:
            List of extracted actors
        """
        pass
    
    @abstractmethod
    async def extract_use_cases(
        self,
        text: str,
        extraction_type: str = "plantuml"
    ) -> List[UseCase]:
        """
        Extract use cases from text using optimized prompts.
        
        Args:
            text: Text to extract use cases from
            extraction_type: Type of extraction ("plantuml" or "problem")
            
        Returns:
            List of extracted use cases
        """
        pass
    
    @abstractmethod
    async def extract_relationships(
        self,
        text: str,
        actors: List[Actor],
        use_cases: List[UseCase],
        extraction_type: str = "plantuml"
    ) -> List[Relationship]:
        """
        Extract relationships from text using optimized prompts.
        
        Args:
            text: Text to extract relationships from
            actors: Previously extracted actors for context
            use_cases: Previously extracted use cases for context
            extraction_type: Type of extraction ("plantuml" or "problem")
            
        Returns:
            List of extracted relationships
        """
        pass
    
    @abstractmethod
    async def validate_extraction(
        self,
        diagram: UMLDiagram,
        original_text: str
    ) -> UMLDiagram:
        """
        Validate and refine extracted components using LLM.
        
        Args:
            diagram: Initially extracted diagram
            original_text: Original text for validation
            
        Returns:
            Validated and refined UMLDiagram
        """
        pass
