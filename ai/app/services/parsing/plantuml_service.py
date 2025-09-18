"""Abstract service for PlantUML parsing and validation."""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from app.core.models.uml_components import UMLDiagram


class PlantUMLParsingService(ABC):
    """Abstract service for parsing and validating PlantUML code."""
    
    @abstractmethod
    async def validate_plantuml_syntax(self, plantuml_code: str) -> Dict[str, Any]:
        """
        Validate PlantUML syntax and structure.
        
        Args:
            plantuml_code: PlantUML code to validate
            
        Returns:
            Dictionary with validation results:
            - is_valid: bool
            - errors: List of error messages
            - warnings: List of warning messages
        """
        pass
    
    @abstractmethod
    async def parse_plantuml_structure(self, plantuml_code: str) -> Dict[str, Any]:
        """
        Parse PlantUML code structure without semantic interpretation.
        
        Args:
            plantuml_code: PlantUML code to parse
            
        Returns:
            Dictionary with parsed structure elements
        """
        pass
    
    @abstractmethod
    async def extract_raw_components(self, plantuml_code: str) -> Dict[str, List[str]]:
        """
        Extract raw component names and relationships from PlantUML.
        
        Args:
            plantuml_code: PlantUML code to extract from
            
        Returns:
            Dictionary with raw component lists:
            - actors: List of actor names
            - use_cases: List of use case names
            - relationships: List of relationship strings
        """
        pass
    
    @abstractmethod
    async def normalize_plantuml_code(self, plantuml_code: str) -> str:
        """
        Normalize PlantUML code for consistent processing.
        
        Args:
            plantuml_code: Raw PlantUML code
            
        Returns:
            Normalized PlantUML code
        """
        pass
    
    @abstractmethod
    async def generate_diagram_preview(
        self,
        plantuml_code: str,
        output_format: str = "svg"
    ) -> Optional[bytes]:
        """
        Generate visual diagram preview from PlantUML code.
        
        Args:
            plantuml_code: PlantUML code to render
            output_format: Output format (svg, png, etc.)
            
        Returns:
            Rendered diagram as bytes, or None if failed
        """
        pass
