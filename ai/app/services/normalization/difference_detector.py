"""Step 2 of Phase 1: Detect differences between student and teacher conventions."""

from typing import List, Dict, Any
from pydantic import BaseModel
import json
from .convention_analyzer import ConventionAnalysisResult
from app.core.models.diagrams.diagram_factory import DiagramType


class ConventionDifference(BaseModel):
    """Represents a difference in conventions between student and teacher."""
    difference_type: str  # naming, structure, style
    category: str  # specific category like "actor_naming", "relationship_style"
    teacher_convention: str
    student_convention: str
    examples: List[str]
    severity: str  # low, medium, high
    confidence: float


class DifferenceDetectionResult(BaseModel):
    """Result of difference detection analysis."""
    diagram_type: DiagramType
    differences: List[ConventionDifference]
    total_differences: int
    severity_breakdown: Dict[str, int]  # count by severity
    overall_confidence: float


class DifferenceDetector:
    """Detects differences between student and teacher conventions."""
    
    def __init__(self, llm_service):
        """
        Initialize difference detector.
        
        Args:
            llm_service: LLM service for AI analysis
        """
        self.llm_service = llm_service
    
    async def detect_differences(
        self,
        student_plantuml: str,
        teacher_conventions: ConventionAnalysisResult,
        problem_description: str,
        step_name: str = "Difference Detection"
    ) -> DifferenceDetectionResult:
        """
        Detect differences between student diagram and teacher conventions.
        
        Args:
            student_plantuml: Student's PlantUML code
            teacher_conventions: Analyzed teacher conventions
            problem_description: Problem description for context
            
        Returns:
            DifferenceDetectionResult with identified differences
        """
        prompt = self._build_difference_detection_prompt(
            student_plantuml, teacher_conventions, problem_description
        )
        
        response = await self.llm_service.generate_response(prompt, step_name=step_name)
        return self._parse_difference_detection(response, teacher_conventions.diagram_type)
    
    def _build_difference_detection_prompt(
        self,
        student_plantuml: str,
        teacher_conventions: ConventionAnalysisResult,
        problem_description: str
    ) -> str:
        """Build prompt for difference detection."""
        
        # Convert teacher conventions to readable format
        conventions_summary = self._format_conventions_for_prompt(teacher_conventions)
        
        prompt = f"""
You are an expert UML diagram analyzer. Compare the student's {teacher_conventions.diagram_type.value} diagram with the teacher's established conventions and identify all differences.

PROBLEM DESCRIPTION:
{problem_description}

TEACHER'S CONVENTIONS:
{conventions_summary}

STUDENT'S PLANTUML CODE:
{student_plantuml}

Please identify ALL differences between the student's diagram and the teacher's conventions. Focus on:

1. NAMING DIFFERENCES:
   - Different naming patterns (CamelCase vs snake_case, etc.)
   - Missing prefixes/suffixes that teacher uses
   - Inconsistent capitalization
   - Different handling of spaces and special characters

2. STRUCTURAL DIFFERENCES:
   - Different relationship types used
   - Different ways of organizing hierarchy
   - Missing or extra structural elements
   - Different PlantUML syntax approaches

3. STYLE DIFFERENCES:
   - Different use of quotes, aliases, labels
   - Different formatting patterns
   - Missing stereotypes or annotations
   - Different PlantUML syntax preferences

For each difference, assess:
- Severity: "low" (cosmetic), "medium" (affects readability), "high" (affects meaning)
- Confidence: How certain you are about this difference (0.0-1.0)

Provide your analysis in JSON format:
{{
    "differences": [
        {{
            "difference_type": "naming|structure|style",
            "category": "specific_category_name",
            "teacher_convention": "How teacher does it",
            "student_convention": "How student does it", 
            "examples": ["example1 from student", "example2 from student"],
            "severity": "low|medium|high",
            "confidence": 0.95
        }}
    ],
    "total_differences": 5,
    "severity_breakdown": {{
        "low": 2,
        "medium": 2, 
        "high": 1
    }},
    "overall_confidence": 0.90
}}

Be thorough but focus on meaningful differences that would benefit from normalization.
"""
        
        return prompt
    
    def _format_conventions_for_prompt(self, conventions: ConventionAnalysisResult) -> str:
        """Format teacher conventions for inclusion in prompt."""
        sections = []
        
        if conventions.naming_conventions:
            sections.append("NAMING CONVENTIONS:")
            for pattern in conventions.naming_conventions:
                sections.append(f"- {pattern.description}")
                if pattern.examples:
                    sections.append(f"  Examples: {', '.join(pattern.examples)}")
        
        if conventions.structural_patterns:
            sections.append("\nSTRUCTURAL PATTERNS:")
            for pattern in conventions.structural_patterns:
                sections.append(f"- {pattern.description}")
                if pattern.examples:
                    sections.append(f"  Examples: {', '.join(pattern.examples)}")
        
        if conventions.style_preferences:
            sections.append("\nSTYLE PREFERENCES:")
            for pattern in conventions.style_preferences:
                sections.append(f"- {pattern.description}")
                if pattern.examples:
                    sections.append(f"  Examples: {', '.join(pattern.examples)}")
        
        return "\n".join(sections)
    
    def _parse_difference_detection(
        self,
        response: str,
        diagram_type: DiagramType
    ) -> DifferenceDetectionResult:
        """Parse LLM response into structured difference detection result."""
        try:
            # Extract JSON from response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start == -1 or json_end == 0:
                raise ValueError("No JSON found in response")
            
            json_str = response[json_start:json_end]
            data = json.loads(json_str)
            
            # Parse differences
            differences = [
                ConventionDifference(**diff) for diff in data.get("differences", [])
            ]
            
            return DifferenceDetectionResult(
                diagram_type=diagram_type,
                differences=differences,
                total_differences=data.get("total_differences", len(differences)),
                severity_breakdown=data.get("severity_breakdown", {}),
                overall_confidence=data.get("overall_confidence", 0.5)
            )
            
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            # Fallback: create basic difference analysis
            return self._create_fallback_differences(response, diagram_type)
    
    def _create_fallback_differences(
        self,
        response: str,
        diagram_type: DiagramType
    ) -> DifferenceDetectionResult:
        """Create fallback difference analysis when JSON parsing fails."""
        differences = []
        
        # Simple text-based difference detection
        if "naming" in response.lower():
            differences.append(ConventionDifference(
                difference_type="naming",
                category="general_naming",
                teacher_convention="Consistent naming pattern",
                student_convention="Inconsistent naming pattern",
                examples=["Various naming inconsistencies found"],
                severity="medium",
                confidence=0.6
            ))
        
        severity_breakdown = {"low": 0, "medium": 0, "high": 0}
        for diff in differences:
            severity_breakdown[diff.severity] += 1
        
        return DifferenceDetectionResult(
            diagram_type=diagram_type,
            differences=differences,
            total_differences=len(differences),
            severity_breakdown=severity_breakdown,
            overall_confidence=0.5
        )
