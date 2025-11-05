"""Extended UML diagram models for multi-diagram support."""

from .class_diagram_models import (
    ClassAttribute,
    ClassMethod,
    UMLClass,
    ClassRelationship,
    ClassDiagram
)

from .sequence_diagram_models import (
    Participant,
    Message,
    Activation,
    SequenceDiagram
)

from .diagram_factory import DiagramFactory, DiagramType

__all__ = [
    # Class diagram models
    "ClassAttribute",
    "ClassMethod", 
    "UMLClass",
    "ClassRelationship",
    "ClassDiagram",
    
    # Sequence diagram models
    "Participant",
    "Message",
    "Activation", 
    "SequenceDiagram",
    
    # Factory and types
    "DiagramFactory",
    "DiagramType"
]
