"""Step 4 of Phase 1: Validate normalized PlantUML code."""

from typing import List, Dict, Any
from pydantic import BaseModel
import re
from .code_normalizer import CodeNormalizationResult
from .convention_analyzer import ConventionAnalysisResult
from app.core.models.diagrams.diagram_factory import DiagramType


class ValidationIssue(BaseModel):
    """Represents a validation issue found in normalized code."""
    issue_type: str  # syntax, logic, convention
    severity: str  # low, medium, high, critical
    description: str
    location: str  # where in the code
    suggestion: str  # how to fix it


class ValidationResult(BaseModel):
    """Result of normalization validation."""
    is_valid: bool
    validated_plantuml: str
    issues: List[ValidationIssue]
    syntax_valid: bool
    logic_preserved: bool
    conventions_matched: bool
    confidence: float


class NormalizationValidator:
    """Validates that normalized PlantUML code is correct and preserves intent."""
    
    def __init__(self, llm_service):
        """
        Initialize normalization validator.
        
        Args:
            llm_service: LLM service for AI-based validation
        """
        self.llm_service = llm_service
    
    async def validate_normalization(
        self,
        original_plantuml: str,
        normalization_result: CodeNormalizationResult,
        teacher_conventions: ConventionAnalysisResult,
        problem_description: str,
        step_name: str = "Normalization Validation"
    ) -> ValidationResult:
        """
        Validate that normalized code is correct and preserves original intent.
        
        Args:
            original_plantuml: Original student PlantUML code
            normalization_result: Result from code normalization
            teacher_conventions: Teacher's conventions to validate against
            problem_description: Problem description for context
            
        Returns:
            ValidationResult with validation status and any issues
        """
        # First, perform basic syntax validation
        syntax_issues = self._validate_syntax(normalization_result.normalized_plantuml)
        
        # Then, perform AI-based validation for logic and conventions
        ai_validation = await self._ai_validate_normalization(
            original_plantuml,
            normalization_result,
            teacher_conventions,
            problem_description,
            step_name
        )
        
        # Combine results
        all_issues = syntax_issues + ai_validation.issues
        
        return ValidationResult(
            is_valid=len([i for i in all_issues if i.severity in ["high", "critical"]]) == 0,
            validated_plantuml=normalization_result.normalized_plantuml,
            issues=all_issues,
            syntax_valid=len(syntax_issues) == 0,
            logic_preserved=ai_validation.logic_preserved,
            conventions_matched=ai_validation.conventions_matched,
            confidence=ai_validation.confidence
        )
    
    def _validate_syntax(self, plantuml_code: str) -> List[ValidationIssue]:
        """Perform basic syntax validation on PlantUML code."""
        issues = []
        
        # Check for basic PlantUML structure
        if not plantuml_code.strip().startswith('@start'):
            issues.append(ValidationIssue(
                issue_type="syntax",
                severity="high",
                description="PlantUML code should start with @startuml",
                location="beginning",
                suggestion="Add @startuml at the beginning"
            ))
        
        if not plantuml_code.strip().endswith('@enduml'):
            issues.append(ValidationIssue(
                issue_type="syntax",
                severity="high", 
                description="PlantUML code should end with @enduml",
                location="end",
                suggestion="Add @enduml at the end"
            ))
        
        # Check for unmatched quotes
        quote_count = plantuml_code.count('"')
        if quote_count % 2 != 0:
            issues.append(ValidationIssue(
                issue_type="syntax",
                severity="medium",
                description="Unmatched quotes detected",
                location="throughout",
                suggestion="Ensure all quotes are properly closed"
            ))
        
        # Check for common syntax errors
        lines = plantuml_code.split('\n')
        for i, line in enumerate(lines, 1):
            line = line.strip()
            if not line or line.startswith("'"):  # Skip empty lines and comments
                continue
            
            # Check for invalid characters in relationships
            if '-->' in line or '--|>' in line:
                # Basic relationship syntax check
                if line.count('-->') + line.count('--|>') > 1:
                    issues.append(ValidationIssue(
                        issue_type="syntax",
                        severity="medium",
                        description="Multiple relationship arrows in single line",
                        location=f"line {i}",
                        suggestion="Split into separate relationship lines"
                    ))
        
        return issues
    
    async def _ai_validate_normalization(
        self,
        original_plantuml: str,
        normalization_result: CodeNormalizationResult,
        teacher_conventions: ConventionAnalysisResult,
        problem_description: str,
        step_name: str = "Phase 1 Step 4: Validation"
    ) -> ValidationResult:
        """Use AI to validate logic preservation and convention matching."""
        
        prompt = self._build_validation_prompt(
            original_plantuml,
            normalization_result,
            teacher_conventions,
            problem_description
        )
        
        response = await self.llm_service.generate_response(prompt, step_name=step_name)
        return self._parse_validation_response(response, normalization_result.normalized_plantuml)
    
    def _build_validation_prompt(
        self,
        original_plantuml: str,
        normalization_result: CodeNormalizationResult,
        teacher_conventions: ConventionAnalysisResult,
        problem_description: str
    ) -> str:
        """Build prompt for AI validation."""
        
        conventions_text = self._format_conventions_for_prompt(teacher_conventions)
        changes_text = "\n".join([f"- {change}" for change in normalization_result.changes_made])
        
        prompt = f"""
You are an expert PlantUML validator. Validate that the normalized {teacher_conventions.diagram_type.value} diagram preserves the original student's intent while properly matching the teacher's conventions.

PROBLEM DESCRIPTION:
{problem_description}

TEACHER'S CONVENTIONS:
{conventions_text}

ORIGINAL STUDENT CODE:
{original_plantuml}

NORMALIZED CODE:
{normalization_result.normalized_plantuml}

CHANGES MADE:
{changes_text}

VALIDATION TASKS:
1. LOGIC PRESERVATION: Verify that all original components, relationships, and logical structure are preserved
2. CONVENTION MATCHING: Verify that teacher's conventions are properly applied
3. IDENTIFY ISSUES: Find any problems with the normalization

Please validate and provide:

LOGIC_PRESERVED: [true/false - whether original intent is preserved]
CONVENTIONS_MATCHED: [true/false - whether teacher conventions are followed]
CONFIDENCE: [0.0-1.0 confidence in the validation]

ISSUES_FOUND:
[List any issues found, or "None" if no issues]
- Issue 1: [type] [severity] [description] [suggestion]
- Issue 2: [type] [severity] [description] [suggestion]

VALIDATION_SUMMARY:
[Brief summary of validation results]

Focus on:
- Are all original actors/classes/participants still present?
- Are all original relationships preserved?
- Do naming conventions match the teacher's style?
- Is the PlantUML syntax correct?
- Are there any logical inconsistencies?
"""
        
        return prompt
    
    def _format_conventions_for_prompt(self, conventions: ConventionAnalysisResult) -> str:
        """Format teacher conventions for prompt."""
        sections = []
        
        for pattern_list, title in [
            (conventions.naming_conventions, "NAMING CONVENTIONS"),
            (conventions.structural_patterns, "STRUCTURAL PATTERNS"),
            (conventions.style_preferences, "STYLE PREFERENCES")
        ]:
            if pattern_list:
                sections.append(f"{title}:")
                for pattern in pattern_list:
                    sections.append(f"- {pattern.description}")
        
        return "\n".join(sections)
    
    def _parse_validation_response(self, response: str, normalized_code: str) -> ValidationResult:
        """Parse AI validation response."""
        try:
            # Extract validation results
            logic_preserved = self._extract_boolean_field(response, "LOGIC_PRESERVED")
            conventions_matched = self._extract_boolean_field(response, "CONVENTIONS_MATCHED")
            confidence = self._extract_confidence_field(response)
            issues = self._extract_issues(response)
            
            return ValidationResult(
                is_valid=logic_preserved and conventions_matched and len([i for i in issues if i.severity in ["high", "critical"]]) == 0,
                validated_plantuml=normalized_code,
                issues=issues,
                syntax_valid=True,  # Will be set by caller
                logic_preserved=logic_preserved,
                conventions_matched=conventions_matched,
                confidence=confidence
            )
            
        except Exception as e:
            # Fallback validation
            return ValidationResult(
                is_valid=False,
                validated_plantuml=normalized_code,
                issues=[ValidationIssue(
                    issue_type="validation",
                    severity="medium",
                    description=f"Validation parsing failed: {str(e)}",
                    location="unknown",
                    suggestion="Manual review recommended"
                )],
                syntax_valid=True,
                logic_preserved=True,  # Assume preserved if can't validate
                conventions_matched=True,  # Assume matched if can't validate
                confidence=0.5
            )
    
    def _extract_boolean_field(self, response: str, field_name: str) -> bool:
        """Extract boolean field from response."""
        pattern = rf'{field_name}:\s*(true|false)'
        match = re.search(pattern, response, re.IGNORECASE)
        if match:
            return match.group(1).lower() == 'true'
        return True  # Default to true if not found
    
    def _extract_confidence_field(self, response: str) -> float:
        """Extract confidence field from response."""
        pattern = r'CONFIDENCE:\s*([0-9]*\.?[0-9]+)'
        match = re.search(pattern, response, re.IGNORECASE)
        if match:
            try:
                return float(match.group(1))
            except ValueError:
                pass
        return 0.8  # Default confidence
    
    def _extract_issues(self, response: str) -> List[ValidationIssue]:
        """Extract issues from response."""
        issues = []
        
        # Look for ISSUES_FOUND section
        issues_match = re.search(
            r'ISSUES_FOUND:\s*(.*?)(?=VALIDATION_SUMMARY:|$)',
            response,
            re.DOTALL | re.IGNORECASE
        )
        
        if issues_match:
            issues_text = issues_match.group(1).strip()
            if issues_text.lower() != "none":
                # Parse issue lines
                for line in issues_text.split('\n'):
                    line = line.strip()
                    if line.startswith('-'):
                        # Try to parse issue format: type severity description suggestion
                        parts = line[1:].strip().split(' ', 3)
                        if len(parts) >= 3:
                            issues.append(ValidationIssue(
                                issue_type=parts[0] if len(parts) > 0 else "unknown",
                                severity=parts[1] if len(parts) > 1 else "medium",
                                description=parts[2] if len(parts) > 2 else line,
                                location="unknown",
                                suggestion=parts[3] if len(parts) > 3 else "Review manually"
                            ))
        
        return issues
