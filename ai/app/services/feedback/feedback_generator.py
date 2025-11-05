"""Feedback generation for Phase 3."""

from typing import List, Dict, Any
from pydantic import BaseModel
import json
from .error_analyzer import ErrorAnalysisResult
from app.core.models.diagrams.diagram_factory import DiagramType


class FeedbackItem(BaseModel):
    """Individual feedback item."""
    type: str  # error, suggestion, praise, warning
    category: str  # component type or error category
    message: str  # Human-readable feedback message
    severity: str  # low, medium, high
    actionable: bool  # Whether this feedback provides actionable advice
    examples: List[str] = []  # Specific examples if applicable


class FeedbackGenerationResult(BaseModel):
    """Result of feedback generation."""
    diagram_type: DiagramType
    feedback_items: List[FeedbackItem]
    summary: str  # Overall summary of the feedback
    strengths: List[str]  # What the student did well
    areas_for_improvement: List[str]  # Key areas to focus on
    confidence: float


class FeedbackGenerator:
    """Generates human-readable feedback from error analysis."""
    
    def __init__(self, llm_service):
        """
        Initialize feedback generator.
        
        Args:
            llm_service: LLM service for AI-based feedback generation
        """
        self.llm_service = llm_service
    
    async def generate_feedback(
        self,
        error_analysis: ErrorAnalysisResult,
        teacher_diagram: Dict[str, Any],
        student_diagram: Dict[str, Any],
        metrics: Dict[str, Any],
        problem_description: str,
        step_name: str = "Feedback Generation"
    ) -> FeedbackGenerationResult:
        """
        Generate comprehensive feedback from error analysis.
        
        Args:
            error_analysis: Structured error analysis from Phase 3
            teacher_diagram: Teacher's reference diagram
            student_diagram: Student's diagram
            metrics: Quantitative metrics from Phase 2
            problem_description: Problem description for context
            
        Returns:
            FeedbackGenerationResult with human-readable feedback
        """
        prompt = self._build_feedback_generation_prompt(
            error_analysis, teacher_diagram, student_diagram, metrics, problem_description
        )
        
        response = await self.llm_service.generate_response(
            prompt,
            temperature=0.3,  # Higher temperature for more creative feedback
            step_name=step_name
        )
        
        return self._parse_feedback_response(response, error_analysis.diagram_type)
    
    def _build_feedback_generation_prompt(
        self,
        error_analysis: ErrorAnalysisResult,
        teacher_diagram: Dict[str, Any],
        student_diagram: Dict[str, Any],
        metrics: Dict[str, Any],
        problem_description: str
    ) -> str:
        """Build prompt for feedback generation."""
        
        # Format error analysis for prompt
        errors_summary = self._format_errors_for_prompt(error_analysis)
        
        # Format metrics summary
        overall_metrics = metrics.get('overall_metrics', {})
        metrics_summary = (
            f"Overall Performance: F1={overall_metrics.get('f1_score', 0):.3f}, "
            f"Precision={overall_metrics.get('precision', 0):.3f}, "
            f"Recall={overall_metrics.get('recall', 0):.3f}"
        )
        
        prompt = f"""
You are a senior UML instructor and software engineering expert providing detailed, educational feedback to a student on their {error_analysis.diagram_type.value} diagram.

ASSIGNMENT CONTEXT:
Problem: {problem_description}
Diagram Type: {error_analysis.diagram_type.value}

STUDENT'S QUANTITATIVE PERFORMANCE:
{metrics_summary}

DETAILED ERROR ANALYSIS:
{errors_summary}

FEEDBACK GENERATION TASK:
Create comprehensive, educational feedback that transforms errors into learning opportunities.

FEEDBACK PRINCIPLES:
1. PRECISION: Be specific about what's wrong and exactly how to fix it
2. EDUCATIONAL: Explain the underlying UML principles and best practices
3. ACTIONABLE: Provide step-by-step improvement suggestions
4. BALANCED: Start with strengths, then address improvement areas systematically
5. PROFESSIONAL: Use appropriate technical terminology while remaining accessible
6. EVIDENCE-BASED: Reference specific elements from both student and reference diagrams

FEEDBACK STRUCTURE REQUIREMENTS:
- Start with positive observations about correct elements
- Address each error category with specific examples
- Provide concrete improvement steps
- End with encouragement and next steps for learning

Generate feedback in the following JSON format:
{{
    "feedback_items": [
        {{
            "type": "error|suggestion|praise|warning",
            "category": "component_category",
            "message": "Detailed feedback message with explanation",
            "severity": "low|medium|high",
            "actionable": true,
            "examples": ["Specific example 1", "Specific example 2"]
        }}
    ],
    "summary": "Overall summary of the student's work and main points",
    "strengths": [
        "What the student did well",
        "Positive aspects of their diagram"
    ],
    "areas_for_improvement": [
        "Key area 1 to focus on",
        "Key area 2 to focus on"
    ],
    "confidence": 0.95
}}

FEEDBACK GUIDELINES:
- Start with positive aspects (what they got right)
- For each error, explain the concept and provide correction guidance
- Use encouraging language ("Consider adding...", "You might want to...", "A good next step would be...")
- Provide specific examples from their diagram
- Connect feedback to UML best practices and the problem requirements
- Limit to the most important issues (max 8-10 feedback items)

Remember: The goal is to help the student learn UML concepts and improve their diagramming skills.
"""
        
        return prompt
    
    def _format_errors_for_prompt(self, error_analysis: ErrorAnalysisResult) -> str:
        """Format error analysis for inclusion in prompt."""
        if not error_analysis.error_categories:
            return "No significant errors detected."
        
        lines = [f"Total Errors: {error_analysis.total_errors}"]
        lines.append("")
        
        for category in error_analysis.error_categories:
            lines.append(f"{category.category.replace('_', ' ').title()} ({category.severity} severity):")
            lines.append(f"  Count: {category.count}")
            lines.append(f"  Description: {category.description}")
            if category.examples:
                lines.append(f"  Examples: {', '.join(category.examples)}")
            lines.append("")
        
        if error_analysis.primary_issues:
            lines.append("Primary Issues:")
            for issue in error_analysis.primary_issues:
                lines.append(f"- {issue}")
        
        return "\n".join(lines)
    
    def _parse_feedback_response(self, response: str, diagram_type: DiagramType) -> FeedbackGenerationResult:
        """Parse AI response into structured feedback."""
        try:
            # Extract JSON from response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start == -1 or json_end == 0:
                raise ValueError("No JSON found in response")
            
            json_str = response[json_start:json_end]
            data = json.loads(json_str)
            
            # Parse feedback items
            feedback_items = [
                FeedbackItem(**item) for item in data.get("feedback_items", [])
            ]
            
            return FeedbackGenerationResult(
                diagram_type=diagram_type,
                feedback_items=feedback_items,
                summary=data.get("summary", "Feedback generated for your diagram."),
                strengths=data.get("strengths", []),
                areas_for_improvement=data.get("areas_for_improvement", []),
                confidence=data.get("confidence", 0.7)
            )
            
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            # Fallback: create basic feedback from text response
            return self._create_fallback_feedback(response, diagram_type)
    
    def _create_fallback_feedback(self, response: str, diagram_type: DiagramType) -> FeedbackGenerationResult:
        """Create fallback feedback when JSON parsing fails."""
        # Extract key points from text response
        feedback_items = []
        
        # Simple text-based feedback extraction
        sentences = response.split('.')
        for sentence in sentences[:5]:  # Take first 5 sentences
            sentence = sentence.strip()
            if len(sentence) > 20:  # Skip very short sentences
                feedback_items.append(FeedbackItem(
                    type="suggestion",
                    category="general",
                    message=sentence,
                    severity="medium",
                    actionable=True
                ))
        
        return FeedbackGenerationResult(
            diagram_type=diagram_type,
            feedback_items=feedback_items,
            summary="Feedback has been generated for your diagram. Please review the suggestions for improvement.",
            strengths=["Your diagram shows understanding of basic UML concepts"],
            areas_for_improvement=["Consider reviewing the feedback items for specific improvements"],
            confidence=0.5
        )
    
    def format_feedback_for_display(self, feedback_result: FeedbackGenerationResult) -> Dict[str, Any]:
        """Format feedback result for display to users."""
        return {
            "diagram_type": feedback_result.diagram_type.value,
            "summary": feedback_result.summary,
            "strengths": feedback_result.strengths,
            "areas_for_improvement": feedback_result.areas_for_improvement,
            "detailed_feedback": [
                {
                    "type": item.type,
                    "category": item.category,
                    "message": item.message,
                    "severity": item.severity,
                    "actionable": item.actionable,
                    "examples": item.examples
                }
                for item in feedback_result.feedback_items
            ],
            "confidence": feedback_result.confidence
        }
    
    def get_feedback_statistics(self, feedback_result: FeedbackGenerationResult) -> Dict[str, Any]:
        """Get statistics about the generated feedback."""
        feedback_by_type = {}
        feedback_by_severity = {}
        
        for item in feedback_result.feedback_items:
            # Count by type
            feedback_by_type[item.type] = feedback_by_type.get(item.type, 0) + 1
            
            # Count by severity
            feedback_by_severity[item.severity] = feedback_by_severity.get(item.severity, 0) + 1
        
        actionable_count = sum(1 for item in feedback_result.feedback_items if item.actionable)
        
        return {
            "total_feedback_items": len(feedback_result.feedback_items),
            "actionable_items": actionable_count,
            "feedback_by_type": feedback_by_type,
            "feedback_by_severity": feedback_by_severity,
            "strengths_identified": len(feedback_result.strengths),
            "improvement_areas": len(feedback_result.areas_for_improvement),
            "confidence": feedback_result.confidence
        }
