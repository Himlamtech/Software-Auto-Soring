"""Use Case Diagram specific parser for Phase 2."""

from typing import List, Dict, Set, Tuple
import re
from app.core.models.uml_components import UMLDiagram, Actor, UseCase, Relationship


class UseCaseParser:
    """Parser for extracting components from Use Case diagrams."""
    
    def __init__(self):
        """Initialize the use case parser."""
        self.actor_patterns = [
            r'actor\s+(["\']?)([^"\'\s]+)\1',  # actor ActorName or actor "Actor Name"
            r'actor\s+(["\'])([^"\']+)\1\s+as\s+(\w+)',  # actor "Actor Name" as A1
            r':([^:]+):',  # :ActorName:
            r'\(([^)]+)\)',  # (ActorName)
        ]
        
        self.usecase_patterns = [
            r'usecase\s+(["\']?)([^"\'\s]+)\1',  # usecase UseCaseName
            r'usecase\s+(["\'])([^"\']+)\1\s+as\s+(\w+)',  # usecase "Use Case Name" as UC1
            r'\(([^)]+)\)',  # (Use Case Name) - when used as usecase
        ]
        
        self.relationship_patterns = [
            r'([^-\s]+)\s*(-->|\.\.>|--)\s*([^:\s]+)(?:\s*:\s*(.+))?',  # Actor --> UseCase : label
            r'([^<\s]+)\s*(<--|\.\.<|<--)\s*([^:\s]+)(?:\s*:\s*(.+))?',  # UseCase <-- Actor : label
        ]
    
    def parse_diagram(self, plantuml_code: str) -> UMLDiagram:
        """
        Parse PlantUML code to extract use case diagram components.
        
        Args:
            plantuml_code: PlantUML code to parse
            
        Returns:
            UMLDiagram with extracted components
        """
        # Clean and normalize the code
        cleaned_code = self._clean_plantuml_code(plantuml_code)
        
        # Extract components
        actors = self._extract_actors(cleaned_code)
        use_cases = self._extract_use_cases(cleaned_code)
        relationships = self._extract_relationships(cleaned_code, actors, use_cases)
        
        return UMLDiagram(
            actors=actors,
            use_cases=use_cases,
            relationships=relationships
        )
    
    def _clean_plantuml_code(self, code: str) -> str:
        """Clean and normalize PlantUML code."""
        # Remove comments
        code = re.sub(r"'.*$", "", code, flags=re.MULTILINE)
        
        # Remove @startuml and @enduml
        code = re.sub(r'@startuml.*?\n', '', code, flags=re.IGNORECASE)
        code = re.sub(r'@enduml.*', '', code, flags=re.IGNORECASE)
        
        # Normalize whitespace
        code = re.sub(r'\s+', ' ', code)
        
        return code.strip()
    
    def _extract_actors(self, code: str) -> List[Actor]:
        """Extract actors from PlantUML code."""
        actors = []
        actor_names = set()
        
        # Try each actor pattern
        for pattern in self.actor_patterns:
            matches = re.finditer(pattern, code, re.IGNORECASE)
            for match in matches:
                if len(match.groups()) >= 2:
                    # Handle quoted names
                    name = match.group(2) if match.group(1) else match.group(1)
                else:
                    name = match.group(1)
                
                name = self._clean_component_name(name)
                
                if name and name not in actor_names:
                    actors.append(Actor(name=name))
                    actor_names.add(name)
        
        # Also look for actors in relationships
        relationship_actors = self._extract_actors_from_relationships(code)
        for actor_name in relationship_actors:
            if actor_name not in actor_names:
                actors.append(Actor(name=actor_name))
                actor_names.add(actor_name)
        
        return actors
    
    def _extract_use_cases(self, code: str) -> List[UseCase]:
        """Extract use cases from PlantUML code."""
        use_cases = []
        usecase_names = set()
        
        # Try each use case pattern
        for pattern in self.usecase_patterns:
            matches = re.finditer(pattern, code, re.IGNORECASE)
            for match in matches:
                if len(match.groups()) >= 2:
                    # Handle quoted names
                    name = match.group(2) if match.group(1) else match.group(1)
                else:
                    name = match.group(1)
                
                name = self._clean_component_name(name)
                
                if name and name not in usecase_names:
                    use_cases.append(UseCase(name=name))
                    usecase_names.add(name)
        
        # Also look for use cases in relationships
        relationship_usecases = self._extract_usecases_from_relationships(code)
        for usecase_name in relationship_usecases:
            if usecase_name not in usecase_names:
                use_cases.append(UseCase(name=usecase_name))
                usecase_names.add(usecase_name)
        
        return use_cases
    
    def _extract_relationships(self, code: str, actors: List[Actor], use_cases: List[UseCase]) -> List[Relationship]:
        """Extract relationships from PlantUML code."""
        relationships = []
        actor_names = {actor.name for actor in actors}
        usecase_names = {uc.name for uc in use_cases}
        
        # Extract relationships using patterns
        for pattern in self.relationship_patterns:
            matches = re.finditer(pattern, code, re.IGNORECASE)
            for match in matches:
                source = self._clean_component_name(match.group(1))
                target = self._clean_component_name(match.group(3))
                label = match.group(4) if len(match.groups()) >= 4 and match.group(4) else None
                
                # Determine relationship type based on arrow
                arrow = match.group(2)
                rel_type = self._determine_relationship_type(arrow, label)
                
                # Validate that source and target exist
                if source in actor_names or source in usecase_names:
                    if target in actor_names or target in usecase_names:
                        relationships.append(Relationship(
                            source=source,
                            target=target,
                            relationship_type=rel_type,
                            label=label
                        ))
        
        return relationships
    
    def _extract_actors_from_relationships(self, code: str) -> Set[str]:
        """Extract actor names that appear in relationships."""
        actors = set()
        
        # Look for patterns like "Actor -->" or "--> Actor"
        patterns = [
            r'(\w+)\s*-->',  # Actor -->
            r'-->\s*(\w+)',  # --> Actor
            r'(\w+)\s*<--',  # Actor <--
            r'<--\s*(\w+)',  # <-- Actor
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, code, re.IGNORECASE)
            for match in matches:
                name = self._clean_component_name(match.group(1))
                if name and self._looks_like_actor(name):
                    actors.add(name)
        
        return actors
    
    def _extract_usecases_from_relationships(self, code: str) -> Set[str]:
        """Extract use case names that appear in relationships."""
        usecases = set()
        
        # Look for quoted names in relationships (likely use cases)
        pattern = r'["\']([^"\']+)["\']'
        matches = re.finditer(pattern, code)
        for match in matches:
            name = match.group(1).strip()
            if name and self._looks_like_usecase(name):
                usecases.add(name)
        
        return usecases
    
    def _clean_component_name(self, name: str) -> str:
        """Clean component name from PlantUML syntax."""
        if not name:
            return ""
        
        # Remove quotes
        name = name.strip('"\'')
        
        # Remove aliases (text after 'as')
        if ' as ' in name:
            name = name.split(' as ')[0].strip()
        
        # Remove special characters but keep spaces for use case names
        name = re.sub(r'[<>(){}[\]]', '', name)
        
        return name.strip()
    
    def _determine_relationship_type(self, arrow: str, label: str = None) -> str:
        """Determine relationship type from arrow and label."""
        if label:
            label_lower = label.lower()
            if 'include' in label_lower:
                return 'include'
            elif 'extend' in label_lower:
                return 'extend'
        
        # Default relationship types based on arrow
        if arrow == '-->':
            return 'association'
        elif arrow == '..>':
            return 'dependency'
        elif arrow == '--':
            return 'association'
        else:
            return 'association'
    
    def _looks_like_actor(self, name: str) -> bool:
        """Heuristic to determine if a name looks like an actor."""
        # Actors are typically single words or short phrases
        # Common actor patterns: User, Admin, Customer, System, etc.
        actor_keywords = ['user', 'admin', 'customer', 'client', 'system', 'manager', 'operator']
        name_lower = name.lower()
        
        # Check if it's a single word or contains actor keywords
        return (len(name.split()) <= 2 or 
                any(keyword in name_lower for keyword in actor_keywords) or
                name.endswith('er') or name.endswith('or'))
    
    def _looks_like_usecase(self, name: str) -> bool:
        """Heuristic to determine if a name looks like a use case."""
        # Use cases are typically longer phrases describing actions
        # Common use case patterns: "Login", "Manage Users", "Create Account", etc.
        usecase_keywords = ['login', 'create', 'delete', 'update', 'manage', 'view', 'search', 'add', 'remove']
        name_lower = name.lower()
        
        # Check if it contains action keywords or is a longer phrase
        return (len(name.split()) >= 2 or 
                any(keyword in name_lower for keyword in usecase_keywords) or
                name_lower.startswith(('create', 'delete', 'update', 'manage', 'view')))
