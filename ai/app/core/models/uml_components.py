"""Domain models for UML diagram components."""

from typing import List, Optional
from pydantic import BaseModel, Field


class Actor(BaseModel):
    """Represents an actor in UML Use Case Diagram."""
    
    name: str = Field(..., description="Name of the actor")
    description: Optional[str] = Field(None, description="Description of the actor")
    stereotype: Optional[str] = Field(None, description="Actor stereotype if any")


class UseCase(BaseModel):
    """Represents a use case in UML Use Case Diagram."""
    
    name: str = Field(..., description="Name of the use case")
    description: Optional[str] = Field(None, description="Description of the use case")
    primary_actor: Optional[str] = Field(None, description="Primary actor for this use case")
    preconditions: Optional[List[str]] = Field(default_factory=list, description="Use case preconditions")
    postconditions: Optional[List[str]] = Field(default_factory=list, description="Use case postconditions")


class Relationship(BaseModel):
    """Represents a relationship between UML components."""
    
    source: str = Field(..., description="Source component name")
    target: str = Field(..., description="Target component name")
    relationship_type: str = Field(..., description="Type of relationship (association, include, extend, etc.)")
    label: Optional[str] = Field(None, description="Relationship label if any")


class UMLDiagram(BaseModel):
    """Complete UML Use Case Diagram representation."""
    
    actors: List[Actor] = Field(default_factory=list, description="List of actors in the diagram")
    use_cases: List[UseCase] = Field(default_factory=list, description="List of use cases in the diagram")
    relationships: List[Relationship] = Field(default_factory=list, description="List of relationships in the diagram")
    title: Optional[str] = Field(None, description="Diagram title")
