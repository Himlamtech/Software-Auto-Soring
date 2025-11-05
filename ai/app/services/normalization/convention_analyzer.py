"""Step 1 of Phase 1: Analyze teacher's diagram conventions."""

from typing import Dict, Any, List
from pydantic import BaseModel
import json
from app.core.models.diagrams.diagram_factory import DiagramType


class ConventionPattern(BaseModel):
    """Represents a detected convention pattern."""
    pattern_type: str  # naming, structure, style
    description: str
    examples: List[str]
    confidence: float


class ConventionAnalysisResult(BaseModel):
    """Result of convention analysis."""
    diagram_type: DiagramType
    naming_conventions: List[ConventionPattern]
    structural_patterns: List[ConventionPattern]
    style_preferences: List[ConventionPattern]
    overall_confidence: float


class ConventionAnalyzer:
    """Analyzes teacher's PlantUML diagram to extract conventions and patterns."""
    
    def __init__(self, llm_service):
        """
        Initialize convention analyzer.
        
        Args:
            llm_service: LLM service for AI analysis
        """
        self.llm_service = llm_service
    
    async def analyze_teacher_conventions(
        self,
        teacher_plantuml: str,
        problem_description: str,
        diagram_type: DiagramType,
        step_name: str = "Convention Analysis"
    ) -> ConventionAnalysisResult:
        """
        Analyze teacher's diagram to extract conventions.
        
        Args:
            teacher_plantuml: Teacher's reference PlantUML code
            problem_description: Problem description for context
            diagram_type: Type of diagram being analyzed
            
        Returns:
            ConventionAnalysisResult with detected patterns
        """
        prompt = self._build_convention_analysis_prompt(
            teacher_plantuml, problem_description, diagram_type
        )
        
        response = await self.llm_service.generate_response(prompt, step_name=step_name)
        return self._parse_convention_analysis(response, diagram_type)
    
    def _build_convention_analysis_prompt(
        self,
        teacher_plantuml: str,
        problem_description: str,
        diagram_type: DiagramType
    ) -> str:
        """Build the prompt for convention analysis."""
        
        base_prompt = f"""
You are an expert UML diagram analyzer specializing in {diagram_type.value} diagrams. Your task is to meticulously analyze the teacher's reference diagram and extract ALL conventions, patterns, and style preferences.

CONTEXT:
Problem: {problem_description}
Diagram Type: {diagram_type.value}

TEACHER'S REFERENCE PLANTUML CODE:
{teacher_plantuml}

ANALYSIS REQUIREMENTS:
Perform a comprehensive analysis focusing on:

1. NAMING CONVENTIONS (Critical for matching):
   - Exact naming patterns: CamelCase, snake_case, kebab-case, PascalCase
   - Prefix/suffix patterns (e.g., "I" for interfaces, "Abstract" for abstract classes)
   - Space handling: underscores vs spaces vs camelCase
   - Special character usage and escaping
   - Domain-specific terminology and abbreviations
   - Consistency in plural vs singular forms

2. STRUCTURAL PATTERNS (Essential for correctness):
   - Relationship syntax: --> vs -> vs -|> vs ||--||
   - Cardinality notation and placement
   - Inheritance vs composition vs aggregation preferences
   - Grouping and package organization
   - Stereotype usage and placement
   - Attribute and method visibility markers

3. STYLE PREFERENCES (Important for consistency):
   - Quote usage: when to use quotes vs aliases
   - Indentation and line spacing patterns
   - Comment styles and placement
   - Color and styling directives
   - PlantUML-specific syntax choices
   - Order of elements (attributes before methods, etc.)

Provide your analysis in the following JSON format:
{{
    "naming_conventions": [
        {{
            "pattern_type": "naming",
            "description": "Description of the naming pattern",
            "examples": ["example1", "example2"],
            "confidence": 0.95
        }}
    ],
    "structural_patterns": [
        {{
            "pattern_type": "structure", 
            "description": "Description of structural pattern",
            "examples": ["example1", "example2"],
            "confidence": 0.90
        }}
    ],
    "style_preferences": [
        {{
            "pattern_type": "style",
            "description": "Description of style preference", 
            "examples": ["example1", "example2"],
            "confidence": 0.85
        }}
    ],
    "overall_confidence": 0.90
}}
"""
        
        # Add diagram-specific analysis instructions
        if diagram_type == DiagramType.USE_CASE:
            base_prompt += """

SPECIFIC FOR USE CASE DIAGRAMS:
- Actor naming patterns (User, Admin, Customer, etc.)
- Use case naming patterns (Login, "Manage Users", etc.)
- Relationship conventions (associations, includes, extends)
"""
        elif diagram_type == DiagramType.CLASS:
            base_prompt += """

SPECIFIC FOR CLASS DIAGRAMS:
- Class naming patterns (ClassName, class_name, etc.)
- Attribute and method naming conventions
- Visibility indicators (+, -, #, ~)
- Relationship types (inheritance, composition, etc.)
"""
        elif diagram_type == DiagramType.SEQUENCE:
            base_prompt += """

SPECIFIC FOR SEQUENCE DIAGRAMS:
- Participant naming patterns
- Message labeling conventions
- Activation and lifeline patterns
- Fragment usage patterns
"""
        
        return base_prompt
    
    def _parse_convention_analysis(
        self,
        response: str,
        diagram_type: DiagramType
    ) -> ConventionAnalysisResult:
        """Parse the LLM response into structured convention analysis."""
        try:
            # Extract JSON from response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start == -1 or json_end == 0:
                raise ValueError("No JSON found in response")
            
            json_str = response[json_start:json_end]
            data = json.loads(json_str)
            
            # Parse convention patterns
            naming_conventions = [
                ConventionPattern(**pattern) for pattern in data.get("naming_conventions", [])
            ]
            structural_patterns = [
                ConventionPattern(**pattern) for pattern in data.get("structural_patterns", [])
            ]
            style_preferences = [
                ConventionPattern(**pattern) for pattern in data.get("style_preferences", [])
            ]
            
            return ConventionAnalysisResult(
                diagram_type=diagram_type,
                naming_conventions=naming_conventions,
                structural_patterns=structural_patterns,
                style_preferences=style_preferences,
                overall_confidence=data.get("overall_confidence", 0.5)
            )
            
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            # Fallback: create basic analysis from text response
            return self._create_fallback_analysis(response, diagram_type)
    
    def _create_fallback_analysis(
        self,
        response: str,
        diagram_type: DiagramType
    ) -> ConventionAnalysisResult:
        """Create fallback analysis when JSON parsing fails."""
        # Basic pattern detection from text response
        naming_patterns = []
        structural_patterns = []
        style_patterns = []
        
        # Simple keyword-based pattern detection
        if "CamelCase" in response or "camelCase" in response:
            naming_patterns.append(ConventionPattern(
                pattern_type="naming",
                description="Uses CamelCase naming convention",
                examples=["UserAccount", "LoginSystem"],
                confidence=0.7
            ))
        
        if "snake_case" in response:
            naming_patterns.append(ConventionPattern(
                pattern_type="naming", 
                description="Uses snake_case naming convention",
                examples=["user_account", "login_system"],
                confidence=0.7
            ))
        
        return ConventionAnalysisResult(
            diagram_type=diagram_type,
            naming_conventions=naming_patterns,
            structural_patterns=structural_patterns,
            style_preferences=style_patterns,
            overall_confidence=0.5
        )
