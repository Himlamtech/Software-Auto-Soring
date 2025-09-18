"""External PlantUML service integration."""

import re
import subprocess
from typing import Dict, List, Optional, Any
from pathlib import Path
from app.services.parsing.plantuml_service import PlantUMLParsingService


class PlantUMLExternalService(PlantUMLParsingService):
    """External PlantUML service implementation using plantuml.jar or online service."""
    
    def __init__(
        self,
        plantuml_jar_path: Optional[str] = None,
        use_online_service: bool = False,
        online_service_url: str = "http://www.plantuml.com/plantuml"
    ):
        """
        Initialize PlantUML external service.
        
        Args:
            plantuml_jar_path: Path to plantuml.jar file for local processing
            use_online_service: Whether to use online PlantUML service
            online_service_url: URL for online PlantUML service
        """
        self.plantuml_jar_path = plantuml_jar_path
        self.use_online_service = use_online_service
        self.online_service_url = online_service_url
    
    async def validate_plantuml_syntax(self, plantuml_code: str) -> Dict[str, Any]:
        """
        Validate PlantUML syntax using external service.
        
        Args:
            plantuml_code: PlantUML code to validate
            
        Returns:
            Dictionary with validation results
        """
        errors = []
        warnings = []
        is_valid = True
        
        # Basic syntax validation
        if not plantuml_code.strip().startswith(('@startuml', '@startuse')):
            errors.append("PlantUML code must start with @startuml or @startusecase")
            is_valid = False
        
        if not plantuml_code.strip().endswith(('@enduml', '@enduse')):
            errors.append("PlantUML code must end with @enduml or @endusecase")
            is_valid = False
        
        # Check for use case diagram specific syntax
        if '@startusecase' in plantuml_code or '@startuml' in plantuml_code:
            # Check for basic use case elements
            has_actors = bool(re.search(r'actor\s+\w+', plantuml_code, re.IGNORECASE))
            has_use_cases = bool(re.search(r'usecase\s+\w+|ellipse\s+\w+|\(\w+\)', plantuml_code))
            
            if not has_actors:
                warnings.append("No actors found in the diagram")
            
            if not has_use_cases:
                warnings.append("No use cases found in the diagram")
        
        # Try to process with external service if available
        if self.plantuml_jar_path and Path(self.plantuml_jar_path).exists():
            validation_result = await self._validate_with_jar(plantuml_code)
            errors.extend(validation_result.get("errors", []))
            warnings.extend(validation_result.get("warnings", []))
            if validation_result.get("errors"):
                is_valid = False
        
        return {
            "is_valid": is_valid,
            "errors": errors,
            "warnings": warnings
        }
    
    async def parse_plantuml_structure(self, plantuml_code: str) -> Dict[str, Any]:
        """
        Parse PlantUML code structure.
        
        Args:
            plantuml_code: PlantUML code to parse
            
        Returns:
            Dictionary with parsed structure elements
        """
        structure = {
            "start_directive": None,
            "end_directive": None,
            "title": None,
            "actors": [],
            "use_cases": [],
            "relationships": [],
            "stereotypes": [],
            "notes": []
        }
        
        lines = plantuml_code.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith("'"):  # Skip empty lines and comments
                continue
            
            # Extract start/end directives
            if line.startswith('@start'):
                structure["start_directive"] = line
            elif line.startswith('@end'):
                structure["end_directive"] = line
            
            # Extract title
            elif line.startswith('title'):
                structure["title"] = line[5:].strip()
            
            # Extract actors
            elif re.match(r'actor\s+', line, re.IGNORECASE):
                actor_match = re.match(r'actor\s+(["\']?)(\w+)\1(\s+as\s+(\w+))?', line, re.IGNORECASE)
                if actor_match:
                    structure["actors"].append({
                        "name": actor_match.group(2),
                        "alias": actor_match.group(4) if actor_match.group(4) else actor_match.group(2),
                        "line": line
                    })
            
            # Extract use cases (various formats)
            elif re.match(r'usecase\s+|ellipse\s+|\(.*\)', line, re.IGNORECASE):
                structure["use_cases"].append({
                    "definition": line,
                    "line": line
                })
            
            # Extract relationships
            elif '-->' in line or '<--' in line or '--' in line:
                structure["relationships"].append({
                    "definition": line,
                    "line": line
                })
        
        return structure
    
    async def extract_raw_components(self, plantuml_code: str) -> Dict[str, List[str]]:
        """
        Extract raw component names from PlantUML code.
        
        Args:
            plantuml_code: PlantUML code to extract from
            
        Returns:
            Dictionary with component lists
        """
        structure = await self.parse_plantuml_structure(plantuml_code)
        
        return {
            "actors": [actor["name"] for actor in structure["actors"]],
            "use_cases": [uc["definition"] for uc in structure["use_cases"]],
            "relationships": [rel["definition"] for rel in structure["relationships"]]
        }
    
    async def normalize_plantuml_code(self, plantuml_code: str) -> str:
        """
        Normalize PlantUML code for consistent processing.
        
        Args:
            plantuml_code: Raw PlantUML code
            
        Returns:
            Normalized PlantUML code
        """
        lines = plantuml_code.split('\n')
        normalized_lines = []
        
        for line in lines:
            # Remove extra whitespace
            line = line.strip()
            
            # Skip empty lines and comments
            if not line or line.startswith("'"):
                continue
            
            # Normalize keywords to lowercase
            line = re.sub(r'^(actor|usecase|ellipse)\s+', lambda m: m.group(1).lower() + ' ', line, flags=re.IGNORECASE)
            
            normalized_lines.append(line)
        
        return '\n'.join(normalized_lines)
    
    async def generate_diagram_preview(
        self,
        plantuml_code: str,
        output_format: str = "svg"
    ) -> Optional[bytes]:
        """
        Generate visual diagram preview.
        
        Args:
            plantuml_code: PlantUML code to render
            output_format: Output format (svg, png, etc.)
            
        Returns:
            Rendered diagram as bytes
        """
        if self.plantuml_jar_path and Path(self.plantuml_jar_path).exists():
            return await self._generate_with_jar(plantuml_code, output_format)
        elif self.use_online_service:
            return await self._generate_with_online_service(plantuml_code, output_format)
        else:
            return None
    
    async def _validate_with_jar(self, plantuml_code: str) -> Dict[str, Any]:
        """Validate using local plantuml.jar."""
        # Implementation placeholder for jar validation
        return {"errors": [], "warnings": []}
    
    async def _generate_with_jar(self, plantuml_code: str, output_format: str) -> Optional[bytes]:
        """Generate diagram using local plantuml.jar."""
        # Implementation placeholder for jar rendering
        return None
    
    async def _generate_with_online_service(
        self,
        plantuml_code: str,
        output_format: str
    ) -> Optional[bytes]:
        """Generate diagram using online PlantUML service."""
        # Implementation placeholder for online service rendering
        return None
