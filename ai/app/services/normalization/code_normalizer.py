"""Step 3 of Phase 1: Generate normalized PlantUML code."""

from typing import Dict, Any, List
from pydantic import BaseModel
import re
from .difference_detector import DifferenceDetectionResult
from .convention_analyzer import ConventionAnalysisResult
from app.core.models.diagrams.diagram_factory import DiagramType


class NormalizationRule(BaseModel):
    """Represents a normalization rule to apply."""
    rule_type: str  # naming, structure, style
    description: str
    pattern: str  # regex pattern to match
    replacement: str  # replacement pattern
    priority: int  # higher priority rules applied first


class CodeNormalizationResult(BaseModel):
    """Result of code normalization."""
    normalized_plantuml: str
    applied_rules: List[NormalizationRule]
    changes_made: List[str]
    confidence: float
    warnings: List[str]


class CodeNormalizer:
    """Generates normalized PlantUML code that matches teacher conventions."""
    
    def __init__(self, llm_service):
        """
        Initialize code normalizer.
        
        Args:
            llm_service: LLM service for AI-based normalization
        """
        self.llm_service = llm_service
    
    async def normalize_code(
        self,
        student_plantuml: str,
        teacher_conventions: ConventionAnalysisResult,
        detected_differences: DifferenceDetectionResult,
        problem_description: str,
        step_name: str = "Code Normalization"
    ) -> CodeNormalizationResult:
        """
        Generate normalized PlantUML code that matches teacher conventions.
        
        Args:
            student_plantuml: Original student PlantUML code
            teacher_conventions: Teacher's analyzed conventions
            detected_differences: Detected differences to fix
            problem_description: Problem description for context
            
        Returns:
            CodeNormalizationResult with normalized code
        """
        prompt = self._build_normalization_prompt(
            student_plantuml, teacher_conventions, detected_differences, problem_description
        )
        
        response = await self.llm_service.generate_response(prompt, step_name=step_name)
        return self._parse_normalization_result(response, student_plantuml)
    
    def _build_normalization_prompt(
        self,
        student_plantuml: str,
        teacher_conventions: ConventionAnalysisResult,
        detected_differences: DifferenceDetectionResult,
        problem_description: str
    ) -> str:
        """Build prompt for code normalization."""
        
        # Format conventions and differences for prompt
        conventions_text = self._format_conventions_for_prompt(teacher_conventions)
        differences_text = self._format_differences_for_prompt(detected_differences)
        
        prompt = f"""
You are an expert PlantUML code normalizer. Your task is to rewrite the student's {teacher_conventions.diagram_type.value} diagram to match the teacher's conventions while preserving the student's original logic and intent.

PROBLEM DESCRIPTION:
{problem_description}

TEACHER'S CONVENTIONS TO FOLLOW:
{conventions_text}

IDENTIFIED DIFFERENCES TO FIX:
{differences_text}

STUDENT'S ORIGINAL PLANTUML CODE:
{student_plantuml}

NORMALIZATION REQUIREMENTS:
1. PRESERVE LOGIC: Keep all the student's original components, relationships, and logical structure
2. MATCH CONVENTIONS: Apply teacher's naming, structural, and style conventions
3. FIX DIFFERENCES: Address each identified difference systematically
4. MAINTAIN VALIDITY: Ensure the result is valid PlantUML syntax
5. BE CONSERVATIVE: Only change what's necessary to match conventions

SPECIFIC NORMALIZATION TASKS:
- Apply teacher's naming conventions to all components
- Use teacher's preferred relationship syntax
- Match teacher's style preferences (quotes, aliases, formatting)
- Ensure consistent capitalization and spacing
- Apply any structural patterns the teacher uses

Please provide:
1. The normalized PlantUML code
2. A list of changes made
3. Any warnings about potential issues

Format your response as:
NORMALIZED_CODE:
```plantuml
[normalized PlantUML code here]
```

CHANGES_MADE:
- Change 1: Description of what was changed
- Change 2: Description of what was changed
[etc.]

WARNINGS:
- Warning 1: Any potential issues or concerns
- Warning 2: [if any]

CONFIDENCE: [0.0-1.0 confidence score]

Remember: The goal is to make the student's diagram look like it was written by the teacher while keeping the student's original intent intact.
"""
        
        return prompt
    
    def _format_conventions_for_prompt(self, conventions: ConventionAnalysisResult) -> str:
        """Format teacher conventions for prompt."""
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
    
    def _format_differences_for_prompt(self, differences: DifferenceDetectionResult) -> str:
        """Format detected differences for prompt."""
        if not differences.differences:
            return "No significant differences detected."
        
        sections = []
        for diff in differences.differences:
            sections.append(f"- {diff.category} ({diff.severity} severity):")
            sections.append(f"  Teacher uses: {diff.teacher_convention}")
            sections.append(f"  Student uses: {diff.student_convention}")
            if diff.examples:
                sections.append(f"  Examples to fix: {', '.join(diff.examples)}")
        
        return "\n".join(sections)
    
    def _parse_normalization_result(
        self,
        response: str,
        original_plantuml: str
    ) -> CodeNormalizationResult:
        """Parse LLM response into structured normalization result."""
        try:
            # Extract normalized code
            normalized_code = self._extract_plantuml_code(response)
            if not normalized_code:
                normalized_code = original_plantuml  # Fallback to original
            
            # Extract changes made
            changes_made = self._extract_changes_made(response)
            
            # Extract warnings
            warnings = self._extract_warnings(response)
            
            # Extract confidence
            confidence = self._extract_confidence(response)
            
            return CodeNormalizationResult(
                normalized_plantuml=normalized_code,
                applied_rules=[],  # Will be populated by rule-based post-processing
                changes_made=changes_made,
                confidence=confidence,
                warnings=warnings
            )
            
        except Exception as e:
            # Fallback: return original code with error warning
            return CodeNormalizationResult(
                normalized_plantuml=original_plantuml,
                applied_rules=[],
                changes_made=[],
                confidence=0.0,
                warnings=[f"Normalization failed: {str(e)}"]
            )
    
    def _extract_plantuml_code(self, response: str) -> str:
        """Extract PlantUML code from response."""
        # Look for code blocks
        patterns = [
            r'```plantuml\s*(.*?)\s*```',
            r'```\s*(.*?)\s*```',
            r'NORMALIZED_CODE:\s*(.*?)(?=CHANGES_MADE:|WARNINGS:|CONFIDENCE:|$)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, response, re.DOTALL | re.IGNORECASE)
            if match:
                code = match.group(1).strip()
                # Clean up the code
                code = re.sub(r'^```plantuml\s*', '', code)
                code = re.sub(r'\s*```$', '', code)
                return code.strip()
        
        return ""
    
    def _extract_changes_made(self, response: str) -> List[str]:
        """Extract list of changes made from response."""
        changes = []
        
        # Look for CHANGES_MADE section
        changes_match = re.search(
            r'CHANGES_MADE:\s*(.*?)(?=WARNINGS:|CONFIDENCE:|$)',
            response,
            re.DOTALL | re.IGNORECASE
        )
        
        if changes_match:
            changes_text = changes_match.group(1).strip()
            # Extract bullet points
            for line in changes_text.split('\n'):
                line = line.strip()
                if line.startswith('-') or line.startswith('•'):
                    changes.append(line[1:].strip())
        
        return changes
    
    def _extract_warnings(self, response: str) -> List[str]:
        """Extract warnings from response."""
        warnings = []
        
        # Look for WARNINGS section
        warnings_match = re.search(
            r'WARNINGS:\s*(.*?)(?=CONFIDENCE:|$)',
            response,
            re.DOTALL | re.IGNORECASE
        )
        
        if warnings_match:
            warnings_text = warnings_match.group(1).strip()
            # Extract bullet points
            for line in warnings_text.split('\n'):
                line = line.strip()
                if line.startswith('-') or line.startswith('•'):
                    warnings.append(line[1:].strip())
        
        return warnings
    
    def _extract_confidence(self, response: str) -> float:
        """Extract confidence score from response."""
        # Look for CONFIDENCE section
        confidence_match = re.search(
            r'CONFIDENCE:\s*([0-9]*\.?[0-9]+)',
            response,
            re.IGNORECASE
        )
        
        if confidence_match:
            try:
                return float(confidence_match.group(1))
            except ValueError:
                pass
        
        return 0.7  # Default confidence
