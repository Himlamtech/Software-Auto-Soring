"""Error analysis for Phase 3 feedback generation."""

from typing import List, Dict, Any
from pydantic import BaseModel
import json
from app.core.models.diagrams.diagram_factory import DiagramType


class ErrorCategory(BaseModel):
    """Represents a category of errors found."""
    category: str  # missing_components, incorrect_relationships, etc.
    severity: str  # low, medium, high, critical
    count: int
    description: str
    examples: List[str]


class ErrorAnalysisResult(BaseModel):
    """Result of error analysis."""
    diagram_type: DiagramType
    total_errors: int
    error_categories: List[ErrorCategory]
    severity_breakdown: Dict[str, int]
    primary_issues: List[str]  # Top 3-5 most important issues
    confidence: float


class ErrorAnalyzer:
    """Analyzes errors from Phase 2 metrics to provide structured error information."""
    
    def __init__(self, llm_service):
        """
        Initialize error analyzer.
        
        Args:
            llm_service: LLM service for AI-based error analysis
        """
        self.llm_service = llm_service
    
    async def analyze_errors(
        self,
        teacher_diagram: Dict[str, Any],
        student_diagram: Dict[str, Any],
        metrics: Dict[str, Any],
        problem_description: str,
        diagram_type: DiagramType,
        step_name: str = "Error Analysis"
    ) -> ErrorAnalysisResult:
        """
        Analyze errors from Phase 2 metrics and provide structured error information.
        
        Args:
            teacher_diagram: Teacher's reference diagram (serialized)
            student_diagram: Student's diagram (serialized)
            metrics: Calculated metrics from Phase 2
            problem_description: Problem description for context
            diagram_type: Type of diagram being analyzed
            
        Returns:
            ErrorAnalysisResult with structured error analysis
        """
        prompt = self._build_error_analysis_prompt(
            teacher_diagram, student_diagram, metrics, problem_description, diagram_type
        )
        
        response = await self.llm_service.generate_response(prompt, step_name=step_name)
        return self._parse_error_analysis(response, diagram_type)
    
    def _build_error_analysis_prompt(
        self,
        teacher_diagram: Dict[str, Any],
        student_diagram: Dict[str, Any],
        metrics: Dict[str, Any],
        problem_description: str,
        diagram_type: DiagramType
    ) -> str:
        """Build prompt for AI-based error analysis."""
        
        # Format metrics for prompt
        metrics_summary = self._format_metrics_for_prompt(metrics)
        
        # Format diagrams for comparison
        teacher_summary = self._format_diagram_for_prompt(teacher_diagram, "Teacher's Reference")
        student_summary = self._format_diagram_for_prompt(student_diagram, "Student's Submission")
        
        prompt = f"""
You are a senior UML expert and software engineering educator with deep expertise in {diagram_type.value} diagrams. Perform a comprehensive error analysis comparing the student's work against the reference solution.

ASSIGNMENT CONTEXT:
Problem: {problem_description}
Diagram Type: {diagram_type.value}

QUANTITATIVE ANALYSIS RESULTS:
{metrics_summary}

REFERENCE SOLUTION (Teacher's Diagram):
{teacher_summary}

STUDENT SUBMISSION:
{student_summary}

COMPREHENSIVE ERROR ANALYSIS TASK:
Conduct a systematic comparison to identify ALL discrepancies, errors, and areas for improvement.

ERROR CATEGORIZATION FRAMEWORK:
1. MISSING CRITICAL COMPONENTS: Essential elements required by the problem but absent
2. INCORRECT COMPONENTS: Elements present but wrong (wrong type, wrong properties)
3. EXTRA/UNNECESSARY COMPONENTS: Elements that don't belong or add confusion
4. RELATIONSHIP ERRORS: Missing, incorrect, or improperly defined relationships
5. NAMING CONVENTION VIOLATIONS: Inconsistent or incorrect naming patterns
6. STRUCTURAL ORGANIZATION ISSUES: Poor layout, grouping, or hierarchy
7. SEMANTIC ERRORS: Technically correct but conceptually wrong elements
8. SYNTAX/NOTATION ERRORS: PlantUML syntax issues or UML notation mistakes

ANALYSIS REQUIREMENTS:
- Compare element-by-element systematically
- Consider both presence/absence AND correctness of elements
- Evaluate semantic meaning, not just syntactic matching
- Assess adherence to UML best practices and conventions
- Identify patterns of errors that suggest conceptual misunderstandings

Respond in JSON format:
{{
    "total_errors": 5,
    "error_categories": [
        {{
            "category": "missing_components",
            "severity": "high",
            "count": 2,
            "description": "Essential components are missing from the diagram",
            "examples": ["Missing Actor: Administrator", "Missing Use Case: User Management"]
        }},
        {{
            "category": "incorrect_relationships", 
            "severity": "medium",
            "count": 1,
            "description": "Relationships between components are incorrect",
            "examples": ["User should be connected to Login use case"]
        }}
    ],
    "severity_breakdown": {{
        "low": 0,
        "medium": 1,
        "high": 2,
        "critical": 0
    }},
    "primary_issues": [
        "Missing essential actors from the system",
        "Incorrect relationships between user and use cases"
    ],
    "confidence": 0.95
}}

Focus on educational value - identify errors that help the student learn UML concepts and improve their diagram.
"""
        
        return prompt
    
    def _format_metrics_for_prompt(self, metrics: Dict[str, Any]) -> str:
        """Format metrics for inclusion in prompt."""
        overall = metrics.get('overall_metrics', {})
        component_metrics = metrics.get('component_metrics', {})
        
        lines = [
            f"Overall Precision: {overall.get('precision', 0):.3f}",
            f"Overall Recall: {overall.get('recall', 0):.3f}",
            f"Overall F1-Score: {overall.get('f1_score', 0):.3f}",
            f"Similarity Score: {metrics.get('similarity_score', 0):.3f}",
            "",
            "Component-wise Metrics:"
        ]
        
        for component_type, comp_metrics in component_metrics.items():
            lines.append(f"- {component_type.title()}: "
                        f"P={comp_metrics.get('precision', 0):.3f}, "
                        f"R={comp_metrics.get('recall', 0):.3f}, "
                        f"F1={comp_metrics.get('f1_score', 0):.3f}")
            
            # Add error counts
            fp = comp_metrics.get('false_positives', 0)
            fn = comp_metrics.get('false_negatives', 0)
            if fp > 0 or fn > 0:
                lines.append(f"  Errors: {fn} missing, {fp} extra")
        
        return "\n".join(lines)
    
    def _format_diagram_for_prompt(self, diagram: Dict[str, Any], title: str) -> str:
        """Format diagram information for prompt."""
        lines = [f"{title}:"]
        
        # Handle different diagram types
        if 'actors' in diagram:  # Use case diagram
            actors = diagram.get('actors', [])
            use_cases = diagram.get('use_cases', [])
            relationships = diagram.get('relationships', [])
            
            lines.append(f"Actors ({len(actors)}): {[a.get('name', '') for a in actors]}")
            lines.append(f"Use Cases ({len(use_cases)}): {[uc.get('name', '') for uc in use_cases]}")
            rel_list = [f"{r.get('source', '')}->{r.get('target', '')}" for r in relationships]
            lines.append(f"Relationships ({len(relationships)}): {rel_list}")
        
        elif 'classes' in diagram:  # Class diagram
            classes = diagram.get('classes', [])
            relationships = diagram.get('relationships', [])
            
            lines.append(f"Classes ({len(classes)}): {[c.get('name', '') for c in classes]}")
            
            # Add attribute and method counts
            total_attrs = sum(len(c.get('attributes', [])) for c in classes)
            total_methods = sum(len(c.get('methods', [])) for c in classes)
            lines.append(f"Total Attributes: {total_attrs}, Total Methods: {total_methods}")
            rel_list = [f"{r.get('source', '')}->{r.get('target', '')}" for r in relationships]
            lines.append(f"Relationships ({len(relationships)}): {rel_list}")
        
        elif 'participants' in diagram:  # Sequence diagram
            participants = diagram.get('participants', [])
            messages = diagram.get('messages', [])
            
            lines.append(f"Participants ({len(participants)}): {[p.get('name', '') for p in participants]}")
            lines.append(f"Messages ({len(messages)}): {[m.get('label', '') for m in messages]}")
        
        return "\n".join(lines)
    
    def _parse_error_analysis(self, response: str, diagram_type: DiagramType) -> ErrorAnalysisResult:
        """Parse AI response into structured error analysis."""
        try:
            # Extract JSON from response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start == -1 or json_end == 0:
                raise ValueError("No JSON found in response")
            
            json_str = response[json_start:json_end]
            data = json.loads(json_str)
            
            # Parse error categories
            error_categories = [
                ErrorCategory(**category) for category in data.get("error_categories", [])
            ]
            
            return ErrorAnalysisResult(
                diagram_type=diagram_type,
                total_errors=data.get("total_errors", 0),
                error_categories=error_categories,
                severity_breakdown=data.get("severity_breakdown", {}),
                primary_issues=data.get("primary_issues", []),
                confidence=data.get("confidence", 0.5)
            )
            
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            # Fallback: create basic error analysis from metrics
            return self._create_fallback_error_analysis(response, diagram_type)
    
    def _create_fallback_error_analysis(self, response: str, diagram_type: DiagramType) -> ErrorAnalysisResult:
        """Create fallback error analysis when JSON parsing fails."""
        # Basic error detection from text response
        error_categories = []
        
        # Simple keyword-based error detection
        if "missing" in response.lower():
            error_categories.append(ErrorCategory(
                category="missing_components",
                severity="medium",
                count=1,
                description="Some components appear to be missing",
                examples=["Components missing from diagram"]
            ))
        
        if "incorrect" in response.lower() or "wrong" in response.lower():
            error_categories.append(ErrorCategory(
                category="incorrect_relationships",
                severity="medium",
                count=1,
                description="Some relationships appear to be incorrect",
                examples=["Relationship issues detected"]
            ))
        
        severity_breakdown = {"low": 0, "medium": 0, "high": 0, "critical": 0}
        for category in error_categories:
            severity_breakdown[category.severity] += category.count
        
        return ErrorAnalysisResult(
            diagram_type=diagram_type,
            total_errors=len(error_categories),
            error_categories=error_categories,
            severity_breakdown=severity_breakdown,
            primary_issues=["General diagram issues detected"],
            confidence=0.3
        )
