"""Class Diagram specific parser for Phase 2."""

from typing import List, Dict, Set, Optional
import re
from app.core.models.diagrams.class_diagram_models import (
    ClassDiagram, UMLClass, ClassAttribute, ClassMethod, ClassRelationship,
    Visibility, RelationshipType
)


class ClassDiagramParser:
    """Parser for extracting components from Class diagrams."""
    
    def __init__(self):
        """Initialize the class diagram parser."""
        self.class_patterns = [
            r'class\s+(\w+)\s*{([^}]*)}',  # class ClassName { ... }
            r'class\s+(\w+)',  # class ClassName
            r'abstract\s+class\s+(\w+)',  # abstract class ClassName
            r'interface\s+(\w+)',  # interface InterfaceName
        ]
        
        self.relationship_patterns = [
            r'(\w+)\s*(--|>|\.\.>|\*--|o--|<\|--)\s*(\w+)(?:\s*:\s*(.+))?',  # Class1 --|> Class2 : label
        ]
        
        self.visibility_map = {
            '+': Visibility.PUBLIC,
            '-': Visibility.PRIVATE,
            '#': Visibility.PROTECTED,
            '~': Visibility.PACKAGE
        }
        
        self.relationship_map = {
            '--|>': RelationshipType.INHERITANCE,
            '*--': RelationshipType.COMPOSITION,
            'o--': RelationshipType.AGGREGATION,
            '--': RelationshipType.ASSOCIATION,
            '..>': RelationshipType.DEPENDENCY,
            '..|>': RelationshipType.REALIZATION,
            '<|--': RelationshipType.INHERITANCE  # Reverse inheritance
        }
    
    def parse_diagram(self, plantuml_code: str) -> ClassDiagram:
        """
        Parse PlantUML code to extract class diagram components.
        
        Args:
            plantuml_code: PlantUML code to parse
            
        Returns:
            ClassDiagram with extracted components
        """
        # Clean and normalize the code
        cleaned_code = self._clean_plantuml_code(plantuml_code)
        
        # Extract components
        classes = self._extract_classes(cleaned_code)
        relationships = self._extract_relationships(cleaned_code, classes)
        
        return ClassDiagram(
            classes=classes,
            relationships=relationships
        )
    
    def _clean_plantuml_code(self, code: str) -> str:
        """Clean and normalize PlantUML code."""
        # Remove comments
        code = re.sub(r"'.*$", "", code, flags=re.MULTILINE)
        
        # Remove @startuml and @enduml
        code = re.sub(r'@startuml.*?\n', '', code, flags=re.IGNORECASE)
        code = re.sub(r'@enduml.*', '', code, flags=re.IGNORECASE)
        
        return code.strip()
    
    def _extract_classes(self, code: str) -> List[UMLClass]:
        """Extract classes from PlantUML code."""
        classes = []
        class_names = set()
        
        # Extract classes with body
        class_body_pattern = r'class\s+(\w+)\s*{([^}]*)}'
        matches = re.finditer(class_body_pattern, code, re.IGNORECASE | re.DOTALL)
        
        for match in matches:
            class_name = match.group(1)
            class_body = match.group(2)
            
            if class_name not in class_names:
                attributes, methods = self._parse_class_body(class_body)
                
                classes.append(UMLClass(
                    name=class_name,
                    attributes=attributes,
                    methods=methods,
                    is_abstract='abstract' in code.lower() and class_name in code
                ))
                class_names.add(class_name)
        
        # Extract simple class declarations
        simple_class_patterns = [
            r'class\s+(\w+)(?!\s*{)',  # class ClassName (not followed by {)
            r'abstract\s+class\s+(\w+)',  # abstract class ClassName
            r'interface\s+(\w+)',  # interface InterfaceName
        ]
        
        for pattern in simple_class_patterns:
            matches = re.finditer(pattern, code, re.IGNORECASE)
            for match in matches:
                class_name = match.group(1)
                
                if class_name not in class_names:
                    is_abstract = 'abstract' in match.group(0).lower()
                    stereotype = 'interface' if 'interface' in match.group(0).lower() else None
                    
                    classes.append(UMLClass(
                        name=class_name,
                        is_abstract=is_abstract,
                        stereotype=stereotype
                    ))
                    class_names.add(class_name)
        
        # Extract classes from relationships
        relationship_classes = self._extract_classes_from_relationships(code)
        for class_name in relationship_classes:
            if class_name not in class_names:
                classes.append(UMLClass(name=class_name))
                class_names.add(class_name)
        
        return classes
    
    def _parse_class_body(self, body: str) -> tuple[List[ClassAttribute], List[ClassMethod]]:
        """Parse class body to extract attributes and methods."""
        attributes = []
        methods = []
        
        lines = body.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if it's a method (contains parentheses)
            if '(' in line and ')' in line:
                method = self._parse_method(line)
                if method:
                    methods.append(method)
            else:
                # It's an attribute
                attribute = self._parse_attribute(line)
                if attribute:
                    attributes.append(attribute)
        
        return attributes, methods
    
    def _parse_attribute(self, line: str) -> Optional[ClassAttribute]:
        """Parse a single attribute line."""
        # Pattern: [visibility][static] name [: type] [= default]
        pattern = r'^([+\-#~])?(\{static\}\s*)?(\w+)(?:\s*:\s*(\w+))?(?:\s*=\s*(.+))?'
        match = re.match(pattern, line.strip())
        
        if match:
            visibility_char = match.group(1)
            is_static = match.group(2) is not None
            name = match.group(3)
            type_name = match.group(4)
            default_value = match.group(5)
            
            visibility = self.visibility_map.get(visibility_char, Visibility.PUBLIC)
            
            return ClassAttribute(
                name=name,
                type=type_name,
                visibility=visibility,
                is_static=is_static,
                default_value=default_value
            )
        
        return None
    
    def _parse_method(self, line: str) -> Optional[ClassMethod]:
        """Parse a single method line."""
        # Pattern: [visibility][static][abstract] name(params) [: return_type]
        pattern = r'^([+\-#~])?(\{static\}\s*)?(\{abstract\}\s*)?(\w+)\(([^)]*)\)(?:\s*:\s*(\w+))?'
        match = re.match(pattern, line.strip())
        
        if match:
            visibility_char = match.group(1)
            is_static = match.group(2) is not None
            is_abstract = match.group(3) is not None
            name = match.group(4)
            params_str = match.group(5)
            return_type = match.group(6)
            
            visibility = self.visibility_map.get(visibility_char, Visibility.PUBLIC)
            
            # Parse parameters
            parameters = []
            if params_str.strip():
                param_parts = params_str.split(',')
                for param in param_parts:
                    param = param.strip()
                    if param:
                        parameters.append(param)
            
            return ClassMethod(
                name=name,
                parameters=parameters,
                return_type=return_type,
                visibility=visibility,
                is_static=is_static,
                is_abstract=is_abstract
            )
        
        return None
    
    def _extract_relationships(self, code: str, classes: List[UMLClass]) -> List[ClassRelationship]:
        """Extract relationships from PlantUML code."""
        relationships = []
        class_names = {cls.name for cls in classes}
        
        # Extract relationships using patterns
        for pattern in self.relationship_patterns:
            matches = re.finditer(pattern, code, re.IGNORECASE)
            for match in matches:
                source = match.group(1)
                arrow = match.group(2)
                target = match.group(3)
                label = match.group(4) if len(match.groups()) >= 4 and match.group(4) else None
                
                # Determine relationship type
                rel_type = self.relationship_map.get(arrow, RelationshipType.ASSOCIATION)
                
                # Handle reverse relationships
                if arrow == '<|--':
                    source, target = target, source  # Swap for inheritance
                
                # Validate that source and target exist
                if source in class_names and target in class_names:
                    relationships.append(ClassRelationship(
                        source=source,
                        target=target,
                        relationship_type=rel_type,
                        label=label
                    ))
        
        return relationships
    
    def _extract_classes_from_relationships(self, code: str) -> Set[str]:
        """Extract class names that appear in relationships."""
        classes = set()
        
        # Look for relationship patterns and extract class names
        for pattern in self.relationship_patterns:
            matches = re.finditer(pattern, code, re.IGNORECASE)
            for match in matches:
                source = match.group(1)
                target = match.group(3)
                
                if source and self._looks_like_class_name(source):
                    classes.add(source)
                if target and self._looks_like_class_name(target):
                    classes.add(target)
        
        return classes
    
    def _looks_like_class_name(self, name: str) -> bool:
        """Heuristic to determine if a name looks like a class name."""
        # Class names are typically PascalCase and single words
        return (name and 
                name[0].isupper() and 
                name.isalnum() and 
                not name.isupper())  # Not all caps (likely constant)
