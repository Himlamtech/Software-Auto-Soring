"""Domain models for UML Class Diagrams."""

from typing import List, Optional
from pydantic import BaseModel, Field
from enum import Enum


class Visibility(str, Enum):
    """Visibility levels for class members."""
    PUBLIC = "public"
    PRIVATE = "private"
    PROTECTED = "protected"
    PACKAGE = "package"


class ClassAttribute(BaseModel):
    """Represents an attribute in a UML class."""
    
    name: str = Field(..., description="Name of the attribute")
    type: Optional[str] = Field(None, description="Data type of the attribute")
    visibility: Visibility = Field(default=Visibility.PUBLIC, description="Visibility of the attribute")
    is_static: bool = Field(default=False, description="Whether the attribute is static")
    default_value: Optional[str] = Field(None, description="Default value if any")
    
    def __str__(self) -> str:
        """String representation for PlantUML generation."""
        visibility_symbol = {
            Visibility.PUBLIC: "+",
            Visibility.PRIVATE: "-", 
            Visibility.PROTECTED: "#",
            Visibility.PACKAGE: "~"
        }
        
        static_prefix = "{static} " if self.is_static else ""
        type_suffix = f": {self.type}" if self.type else ""
        default_suffix = f" = {self.default_value}" if self.default_value else ""
        
        return f"{visibility_symbol[self.visibility]}{static_prefix}{self.name}{type_suffix}{default_suffix}"


class ClassMethod(BaseModel):
    """Represents a method in a UML class."""
    
    name: str = Field(..., description="Name of the method")
    parameters: List[str] = Field(default_factory=list, description="Method parameters")
    return_type: Optional[str] = Field(None, description="Return type of the method")
    visibility: Visibility = Field(default=Visibility.PUBLIC, description="Visibility of the method")
    is_static: bool = Field(default=False, description="Whether the method is static")
    is_abstract: bool = Field(default=False, description="Whether the method is abstract")
    
    def __str__(self) -> str:
        """String representation for PlantUML generation."""
        visibility_symbol = {
            Visibility.PUBLIC: "+",
            Visibility.PRIVATE: "-",
            Visibility.PROTECTED: "#", 
            Visibility.PACKAGE: "~"
        }
        
        static_prefix = "{static} " if self.is_static else ""
        abstract_prefix = "{abstract} " if self.is_abstract else ""
        params_str = ", ".join(self.parameters)
        return_suffix = f": {self.return_type}" if self.return_type else ""
        
        return f"{visibility_symbol[self.visibility]}{static_prefix}{abstract_prefix}{self.name}({params_str}){return_suffix}"


class RelationshipType(str, Enum):
    """Types of relationships between classes."""
    INHERITANCE = "inheritance"  # --|>
    COMPOSITION = "composition"  # *--
    AGGREGATION = "aggregation"  # o--
    ASSOCIATION = "association"  # --
    DEPENDENCY = "dependency"    # ..>
    REALIZATION = "realization"  # ..|>


class UMLClass(BaseModel):
    """Represents a UML class."""
    
    name: str = Field(..., description="Name of the class")
    attributes: List[ClassAttribute] = Field(default_factory=list, description="Class attributes")
    methods: List[ClassMethod] = Field(default_factory=list, description="Class methods")
    stereotype: Optional[str] = Field(None, description="Class stereotype (e.g., <<interface>>)")
    is_abstract: bool = Field(default=False, description="Whether the class is abstract")
    package: Optional[str] = Field(None, description="Package the class belongs to")
    
    def get_attribute_names(self) -> List[str]:
        """Get list of attribute names."""
        return [attr.name for attr in self.attributes]
    
    def get_method_names(self) -> List[str]:
        """Get list of method names."""
        return [method.name for method in self.methods]


class ClassRelationship(BaseModel):
    """Represents a relationship between UML classes."""
    
    source: str = Field(..., description="Source class name")
    target: str = Field(..., description="Target class name")
    relationship_type: RelationshipType = Field(..., description="Type of relationship")
    label: Optional[str] = Field(None, description="Relationship label")
    multiplicity_source: Optional[str] = Field(None, description="Source multiplicity (e.g., '1', '0..*')")
    multiplicity_target: Optional[str] = Field(None, description="Target multiplicity")
    
    def __str__(self) -> str:
        """String representation for PlantUML generation."""
        relationship_symbols = {
            RelationshipType.INHERITANCE: "--|>",
            RelationshipType.COMPOSITION: "*--",
            RelationshipType.AGGREGATION: "o--",
            RelationshipType.ASSOCIATION: "--",
            RelationshipType.DEPENDENCY: "..>",
            RelationshipType.REALIZATION: "..|>"
        }
        
        symbol = relationship_symbols[self.relationship_type]
        label_part = f" : {self.label}" if self.label else ""
        
        return f"{self.source} {symbol} {self.target}{label_part}"


class ClassDiagram(BaseModel):
    """Complete UML Class Diagram representation."""
    
    classes: List[UMLClass] = Field(default_factory=list, description="List of classes in the diagram")
    relationships: List[ClassRelationship] = Field(default_factory=list, description="List of relationships")
    title: Optional[str] = Field(None, description="Diagram title")
    packages: List[str] = Field(default_factory=list, description="List of packages in the diagram")
    
    def get_class_names(self) -> List[str]:
        """Get list of all class names."""
        return [cls.name for cls in self.classes]
    
    def get_all_attributes(self) -> List[ClassAttribute]:
        """Get all attributes from all classes."""
        attributes = []
        for cls in self.classes:
            attributes.extend(cls.attributes)
        return attributes
    
    def get_all_methods(self) -> List[ClassMethod]:
        """Get all methods from all classes."""
        methods = []
        for cls in self.classes:
            methods.extend(cls.methods)
        return methods
    
    def find_class_by_name(self, name: str) -> Optional[UMLClass]:
        """Find a class by name."""
        for cls in self.classes:
            if cls.name == name:
                return cls
        return None
