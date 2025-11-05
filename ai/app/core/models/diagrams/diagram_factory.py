"""Factory for creating different types of UML diagrams."""

from typing import Union, Dict, Any, List
from enum import Enum
from pydantic import BaseModel

from ..uml_components import UMLDiagram  # Use case diagram (existing)
from .class_diagram_models import ClassDiagram
from .sequence_diagram_models import SequenceDiagram


class DiagramType(str, Enum):
    """Supported UML diagram types."""
    USE_CASE = "use_case"
    CLASS = "class"
    SEQUENCE = "sequence"


# Type alias for all diagram types
DiagramUnion = Union[UMLDiagram, ClassDiagram, SequenceDiagram]


class DiagramFactory:
    """Factory class for creating and managing different UML diagram types."""
    
    @staticmethod
    def create_diagram(diagram_type: DiagramType, **kwargs) -> DiagramUnion:
        """
        Create a diagram of the specified type.
        
        Args:
            diagram_type: Type of diagram to create
            **kwargs: Arguments to pass to the diagram constructor
            
        Returns:
            Diagram instance of the specified type
            
        Raises:
            ValueError: If diagram type is not supported
        """
        if diagram_type == DiagramType.USE_CASE:
            return UMLDiagram(**kwargs)
        elif diagram_type == DiagramType.CLASS:
            return ClassDiagram(**kwargs)
        elif diagram_type == DiagramType.SEQUENCE:
            return SequenceDiagram(**kwargs)
        else:
            raise ValueError(f"Unsupported diagram type: {diagram_type}")
    
    @staticmethod
    def get_diagram_type_from_string(type_str: str) -> DiagramType:
        """
        Convert string to DiagramType enum.
        
        Args:
            type_str: String representation of diagram type
            
        Returns:
            DiagramType enum value
            
        Raises:
            ValueError: If string doesn't match any diagram type
        """
        type_mapping = {
            "use_case": DiagramType.USE_CASE,
            "usecase": DiagramType.USE_CASE,
            "use case": DiagramType.USE_CASE,
            "class": DiagramType.CLASS,
            "class_diagram": DiagramType.CLASS,
            "sequence": DiagramType.SEQUENCE,
            "sequence_diagram": DiagramType.SEQUENCE
        }
        
        normalized_str = type_str.lower().strip()
        if normalized_str in type_mapping:
            return type_mapping[normalized_str]
        else:
            raise ValueError(f"Unknown diagram type: {type_str}")
    
    @staticmethod
    def detect_diagram_type_from_plantuml(plantuml_code: str) -> DiagramType:
        """
        Detect diagram type from PlantUML code.
        
        Args:
            plantuml_code: PlantUML code to analyze
            
        Returns:
            Detected diagram type
            
        Raises:
            ValueError: If diagram type cannot be detected
        """
        code_lower = plantuml_code.lower()
        
        # Check for sequence diagram indicators
        sequence_indicators = [
            "participant", "actor", "boundary", "control", "entity",
            "->", "->>", "<--", "activate", "deactivate"
        ]
        
        # Check for class diagram indicators  
        class_indicators = [
            "class", "interface", "abstract", "enum",
            "--|>", "*--", "o--", "+", "-", "#", "~"
        ]
        
        # Check for use case diagram indicators
        usecase_indicators = [
            "usecase", "actor", "-->", "<<include>>", "<<extend>>"
        ]
        
        sequence_score = sum(1 for indicator in sequence_indicators if indicator in code_lower)
        class_score = sum(1 for indicator in class_indicators if indicator in code_lower)
        usecase_score = sum(1 for indicator in usecase_indicators if indicator in code_lower)
        
        # Determine diagram type based on highest score
        scores = {
            DiagramType.SEQUENCE: sequence_score,
            DiagramType.CLASS: class_score,
            DiagramType.USE_CASE: usecase_score
        }
        
        max_score = max(scores.values())
        if max_score == 0:
            # Default to use case if no clear indicators
            return DiagramType.USE_CASE
        
        # Return the type with highest score
        for diagram_type, score in scores.items():
            if score == max_score:
                return diagram_type
        
        return DiagramType.USE_CASE  # Fallback
    
    @staticmethod
    def get_supported_types() -> List[DiagramType]:
        """Get list of all supported diagram types."""
        return list(DiagramType)
    
    @staticmethod
    def get_diagram_schema(diagram_type: DiagramType) -> Dict[str, Any]:
        """
        Get the Pydantic schema for a specific diagram type.
        
        Args:
            diagram_type: Type of diagram
            
        Returns:
            Dictionary containing the schema
        """
        if diagram_type == DiagramType.USE_CASE:
            return UMLDiagram.model_json_schema()
        elif diagram_type == DiagramType.CLASS:
            return ClassDiagram.model_json_schema()
        elif diagram_type == DiagramType.SEQUENCE:
            return SequenceDiagram.model_json_schema()
        else:
            raise ValueError(f"Unsupported diagram type: {diagram_type}")
    
    @staticmethod
    def validate_diagram(diagram: DiagramUnion, expected_type: DiagramType) -> bool:
        """
        Validate that a diagram matches the expected type.
        
        Args:
            diagram: Diagram instance to validate
            expected_type: Expected diagram type
            
        Returns:
            True if diagram matches expected type
        """
        type_mapping = {
            DiagramType.USE_CASE: UMLDiagram,
            DiagramType.CLASS: ClassDiagram,
            DiagramType.SEQUENCE: SequenceDiagram
        }
        
        expected_class = type_mapping.get(expected_type)
        return isinstance(diagram, expected_class) if expected_class else False
