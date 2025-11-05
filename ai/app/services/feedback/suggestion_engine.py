"""Suggestion engine for Phase 3 feedback generation."""

from typing import List, Dict, Any
from pydantic import BaseModel
from .error_analyzer import ErrorAnalysisResult
from app.core.models.diagrams.diagram_factory import DiagramType


class Suggestion(BaseModel):
    """Individual suggestion for improvement."""
    category: str  # error category this addresses
    priority: str  # high, medium, low
    title: str  # Short title of the suggestion
    description: str  # Detailed description
    action_steps: List[str]  # Specific steps to implement
    examples: List[str] = []  # Code examples if applicable


class SuggestionResult(BaseModel):
    """Result of suggestion generation."""
    diagram_type: DiagramType
    suggestions: List[Suggestion]
    priority_order: List[str]  # Ordered list of suggestion priorities
    estimated_impact: Dict[str, str]  # Impact of each suggestion category


class SuggestionEngine:
    """Generates actionable suggestions based on error analysis."""
    
    def __init__(self):
        """Initialize suggestion engine."""
        self.suggestion_templates = self._load_suggestion_templates()
    
    def generate_suggestions(
        self,
        error_analysis: ErrorAnalysisResult,
        metrics: Dict[str, Any]
    ) -> SuggestionResult:
        """
        Generate actionable suggestions based on error analysis.
        
        Args:
            error_analysis: Structured error analysis
            metrics: Quantitative metrics from Phase 2
            
        Returns:
            SuggestionResult with prioritized suggestions
        """
        suggestions = []
        
        # Generate suggestions for each error category
        for error_category in error_analysis.error_categories:
            category_suggestions = self._generate_category_suggestions(
                error_category, error_analysis.diagram_type, metrics
            )
            suggestions.extend(category_suggestions)
        
        # Prioritize suggestions
        priority_order = self._prioritize_suggestions(suggestions, error_analysis)
        
        # Calculate estimated impact
        estimated_impact = self._calculate_impact(suggestions, metrics)
        
        return SuggestionResult(
            diagram_type=error_analysis.diagram_type,
            suggestions=suggestions,
            priority_order=priority_order,
            estimated_impact=estimated_impact
        )
    
    def _generate_category_suggestions(
        self,
        error_category,
        diagram_type: DiagramType,
        metrics: Dict[str, Any]
    ) -> List[Suggestion]:
        """Generate suggestions for a specific error category."""
        suggestions = []
        
        category_name = error_category.category
        severity = error_category.severity
        
        # Get template for this category and diagram type
        template_key = f"{diagram_type.value}_{category_name}"
        templates = self.suggestion_templates.get(template_key, [])
        
        if not templates:
            # Fallback to generic templates
            templates = self.suggestion_templates.get(f"generic_{category_name}", [])
        
        for template in templates:
            suggestion = Suggestion(
                category=category_name,
                priority=self._determine_priority(severity, error_category.count),
                title=template["title"],
                description=template["description"].format(
                    count=error_category.count,
                    examples=", ".join(error_category.examples[:2])
                ),
                action_steps=template["action_steps"],
                examples=template.get("examples", [])
            )
            suggestions.append(suggestion)
        
        return suggestions
    
    def _determine_priority(self, severity: str, count: int) -> str:
        """Determine suggestion priority based on severity and count."""
        if severity == "critical" or (severity == "high" and count > 2):
            return "high"
        elif severity == "high" or (severity == "medium" and count > 3):
            return "medium"
        else:
            return "low"
    
    def _prioritize_suggestions(
        self,
        suggestions: List[Suggestion],
        error_analysis: ErrorAnalysisResult
    ) -> List[str]:
        """Create priority order for suggestions."""
        # Group by priority
        high_priority = [s.title for s in suggestions if s.priority == "high"]
        medium_priority = [s.title for s in suggestions if s.priority == "medium"]
        low_priority = [s.title for s in suggestions if s.priority == "low"]
        
        return high_priority + medium_priority + low_priority
    
    def _calculate_impact(
        self,
        suggestions: List[Suggestion],
        metrics: Dict[str, Any]
    ) -> Dict[str, str]:
        """Calculate estimated impact of suggestion categories."""
        impact = {}
        
        # Analyze current metrics to estimate impact
        overall_metrics = metrics.get('overall_metrics', {})
        f1_score = overall_metrics.get('f1_score', 0)
        
        for suggestion in suggestions:
            category = suggestion.category
            
            if category not in impact:
                if category in ['missing_components', 'incorrect_relationships']:
                    if f1_score < 0.5:
                        impact[category] = "high"
                    elif f1_score < 0.8:
                        impact[category] = "medium"
                    else:
                        impact[category] = "low"
                else:
                    impact[category] = "medium"
        
        return impact
    
    def _load_suggestion_templates(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load suggestion templates for different error categories and diagram types."""
        return {
            # Use Case Diagram Templates
            "use_case_missing_components": [
                {
                    "title": "Add Missing Actors",
                    "description": "Your diagram is missing {count} essential actors. Examples: {examples}",
                    "action_steps": [
                        "Review the problem requirements to identify all user types",
                        "Add actor declarations using 'actor ActorName' syntax",
                        "Ensure actor names use PascalCase convention",
                        "Connect actors to relevant use cases with associations"
                    ],
                    "examples": ["actor Administrator", "actor Customer"]
                },
                {
                    "title": "Add Missing Use Cases",
                    "description": "Your diagram is missing {count} important use cases. Examples: {examples}",
                    "action_steps": [
                        "Identify all system functions from the requirements",
                        "Add use case declarations using 'usecase \"Name\" as UC1' syntax",
                        "Use descriptive names that clearly indicate the function",
                        "Group related use cases logically"
                    ],
                    "examples": ["usecase \"Manage Users\" as UC1", "usecase \"Generate Reports\" as UC2"]
                }
            ],
            
            "use_case_incorrect_relationships": [
                {
                    "title": "Fix Actor-Use Case Relationships",
                    "description": "Found {count} incorrect relationships between actors and use cases",
                    "action_steps": [
                        "Review which actors should interact with which use cases",
                        "Use simple arrows: Actor --> UseCase",
                        "Ensure all primary actors are connected to their use cases",
                        "Add secondary actors where appropriate"
                    ],
                    "examples": ["User --> UC1", "Administrator --> UC2"]
                }
            ],
            
            "use_case_naming_issues": [
                {
                    "title": "Improve Naming Conventions",
                    "description": "Found {count} naming convention issues in your diagram",
                    "action_steps": [
                        "Use PascalCase for actor names (e.g., 'User', not 'user')",
                        "Use descriptive phrases for use cases (e.g., 'Login to System')",
                        "Be consistent with naming throughout the diagram",
                        "Avoid abbreviations unless they're well-known"
                    ],
                    "examples": ["actor User", "usecase \"Login to System\""]
                }
            ],
            
            # Class Diagram Templates
            "class_missing_components": [
                {
                    "title": "Add Missing Classes",
                    "description": "Your diagram is missing {count} essential classes. Examples: {examples}",
                    "action_steps": [
                        "Identify all entities from the problem domain",
                        "Add class declarations using 'class ClassName' syntax",
                        "Include attributes and methods for each class",
                        "Consider inheritance and composition relationships"
                    ],
                    "examples": ["class User", "class Product"]
                }
            ],
            
            "class_incorrect_relationships": [
                {
                    "title": "Fix Class Relationships",
                    "description": "Found {count} incorrect relationships between classes",
                    "action_steps": [
                        "Use appropriate relationship types (inheritance: --|>, composition: *--, aggregation: o--)",
                        "Ensure relationship directions are correct",
                        "Add multiplicity where appropriate",
                        "Consider the semantic meaning of each relationship"
                    ],
                    "examples": ["User --|> Person", "Order *-- OrderItem"]
                }
            ],
            
            # Generic Templates
            "generic_missing_components": [
                {
                    "title": "Add Missing Components",
                    "description": "Your diagram is missing {count} essential components",
                    "action_steps": [
                        "Review the problem requirements carefully",
                        "Identify all necessary components for your diagram type",
                        "Add missing components using proper syntax",
                        "Ensure all components serve a purpose in the system"
                    ]
                }
            ],
            
            "generic_incorrect_relationships": [
                {
                    "title": "Fix Relationships",
                    "description": "Found {count} incorrect relationships in your diagram",
                    "action_steps": [
                        "Review the semantic meaning of each relationship",
                        "Use appropriate relationship syntax for your diagram type",
                        "Ensure relationships reflect the actual system design",
                        "Check relationship directions and multiplicities"
                    ]
                }
            ],
            
            "generic_naming_issues": [
                {
                    "title": "Improve Naming Conventions",
                    "description": "Found {count} naming issues in your diagram",
                    "action_steps": [
                        "Use consistent naming conventions throughout",
                        "Choose descriptive, meaningful names",
                        "Follow standard conventions for your diagram type",
                        "Avoid abbreviations and unclear terms"
                    ]
                }
            ],
            
            "generic_structural_problems": [
                {
                    "title": "Fix Structural Issues",
                    "description": "Your diagram has {count} structural problems",
                    "action_steps": [
                        "Review the overall organization of your diagram",
                        "Ensure proper grouping of related elements",
                        "Check for missing or redundant components",
                        "Verify that the structure matches the requirements"
                    ]
                }
            ]
        }
