"""Text processing utilities for PlantUML and problem descriptions."""

import re
import unicodedata
from typing import List, Dict, Set, Optional, Tuple
from pathlib import Path


class TextProcessor:
    """Utility class for text processing operations."""
    
    @staticmethod
    def clean_text(text: str) -> str:
        """
        Clean and normalize text content.
        
        Args:
            text: Raw text content
            
        Returns:
            Cleaned and normalized text
        """
        if not text:
            return ""
        
        # Normalize unicode characters
        text = unicodedata.normalize('NFKD', text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove leading/trailing whitespace
        text = text.strip()
        
        return text
    
    @staticmethod
    def extract_plantuml_elements(plantuml_code: str) -> Dict[str, List[str]]:
        """
        Extract basic elements from PlantUML code using regex patterns.
        
        Args:
            plantuml_code: PlantUML code content
            
        Returns:
            Dictionary with extracted elements
        """
        elements = {
            "actors": [],
            "use_cases": [],
            "relationships": [],
            "notes": [],
            "stereotypes": []
        }
        
        if not plantuml_code:
            return elements
        
        lines = plantuml_code.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith("'"):  # Skip comments and empty lines
                continue
            
            # Extract actors
            actor_match = re.search(r'actor\s+(["\']?)(\w+)\1', line, re.IGNORECASE)
            if actor_match:
                elements["actors"].append(actor_match.group(2))
            
            # Extract use cases (multiple patterns)
            usecase_patterns = [
                r'usecase\s+(["\']?)(\w+)\1',
                r'ellipse\s+(["\']?)(\w+)\1',
                r'\(([^)]+)\)'
            ]
            
            for pattern in usecase_patterns:
                usecase_match = re.search(pattern, line, re.IGNORECASE)
                if usecase_match:
                    use_case_name = usecase_match.group(1) if len(usecase_match.groups()) == 1 else usecase_match.group(2)
                    elements["use_cases"].append(use_case_name)
                    break
            
            # Extract relationships
            if any(rel in line for rel in ['-->', '<--', '--', '..']):
                elements["relationships"].append(line)
            
            # Extract notes
            if 'note' in line.lower():
                elements["notes"].append(line)
            
            # Extract stereotypes
            stereotype_match = re.search(r'<<([^>]+)>>', line)
            if stereotype_match:
                elements["stereotypes"].append(stereotype_match.group(1))
        
        return elements
    
    @staticmethod
    def extract_keywords(text: str, min_length: int = 3) -> Set[str]:
        """
        Extract keywords from text content.
        
        Args:
            text: Text content
            min_length: Minimum keyword length
            
        Returns:
            Set of extracted keywords
        """
        if not text:
            return set()
        
        # Common stop words to filter out
        stop_words = {
            'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
            'by', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has',
            'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may',
            'might', 'must', 'can', 'this', 'that', 'these', 'those', 'there', 'their'
        }
        
        # Extract words using regex
        words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
        
        # Filter keywords
        keywords = {
            word for word in words
            if len(word) >= min_length and word not in stop_words
        }
        
        return keywords
    
    @staticmethod
    def normalize_component_name(name: str) -> str:
        """
        Normalize component names for consistent comparison.
        
        Args:
            name: Component name
            
        Returns:
            Normalized component name
        """
        if not name:
            return ""
        
        # Remove quotes and special characters
        name = re.sub(r'["\']', '', name)
        name = re.sub(r'[^\w\s]', ' ', name)
        
        # Normalize whitespace and convert to lowercase
        name = re.sub(r'\s+', ' ', name.strip().lower())
        
        return name
    
    @staticmethod
    def extract_requirements_keywords(description: str) -> Dict[str, List[str]]:
        """
        Extract requirement-related keywords from problem description.
        
        Args:
            description: Problem description text
            
        Returns:
            Dictionary with categorized keywords
        """
        keywords = {
            "actors": [],
            "actions": [],
            "entities": [],
            "systems": []
        }
        
        if not description:
            return keywords
        
        # Actor-related patterns
        actor_patterns = [
            r'\b(user|admin|customer|client|manager|employee|student|teacher|operator)\b',
            r'\b(\w+er)\b',  # Words ending in 'er' (often roles)
            r'\b(person|people|individual|role)\b'
        ]
        
        # Action-related patterns
        action_patterns = [
            r'\b(login|register|create|delete|update|modify|view|search|browse|select)\b',
            r'\b(manage|process|handle|execute|perform|submit|approve|reject)\b'
        ]
        
        # System-related patterns
        system_patterns = [
            r'\b(system|database|server|application|platform|service|api)\b',
            r'\b(module|component|interface|portal|dashboard)\b'
        ]
        
        text_lower = description.lower()
        
        # Extract actors
        for pattern in actor_patterns:
            matches = re.findall(pattern, text_lower)
            keywords["actors"].extend(matches)
        
        # Extract actions
        for pattern in action_patterns:
            matches = re.findall(pattern, text_lower)
            keywords["actions"].extend(matches)
        
        # Extract systems
        for pattern in system_patterns:
            matches = re.findall(pattern, text_lower)
            keywords["systems"].extend(matches)
        
        # Extract entities (nouns)
        noun_pattern = r'\b([A-Z][a-z]+)\b'
        entities = re.findall(noun_pattern, description)
        keywords["entities"] = entities
        
        # Remove duplicates
        for key in keywords:
            keywords[key] = list(set(keywords[key]))
        
        return keywords
    
    @staticmethod
    def calculate_text_similarity(text1: str, text2: str) -> float:
        """
        Calculate similarity between two text strings using Jaccard similarity.
        
        Args:
            text1: First text string
            text2: Second text string
            
        Returns:
            Similarity score between 0 and 1
        """
        if not text1 or not text2:
            return 0.0
        
        # Tokenize and normalize
        tokens1 = set(TextProcessor.extract_keywords(text1))
        tokens2 = set(TextProcessor.extract_keywords(text2))
        
        if not tokens1 or not tokens2:
            return 0.0
        
        # Jaccard similarity
        intersection = tokens1.intersection(tokens2)
        union = tokens1.union(tokens2)
        
        return len(intersection) / len(union) if union else 0.0
    
    @staticmethod
    def validate_plantuml_syntax(plantuml_code: str) -> Tuple[bool, List[str]]:
        """
        Basic PlantUML syntax validation.
        
        Args:
            plantuml_code: PlantUML code to validate
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []
        
        if not plantuml_code.strip():
            errors.append("PlantUML code is empty")
            return False, errors
        
        # Check for start/end tags
        if not re.search(r'@start(uml|usecase)', plantuml_code, re.IGNORECASE):
            errors.append("Missing @startuml or @startusecase directive")
        
        if not re.search(r'@end(uml|usecase)', plantuml_code, re.IGNORECASE):
            errors.append("Missing @enduml or @endusecase directive")
        
        # Check for balanced parentheses
        open_parens = plantuml_code.count('(')
        close_parens = plantuml_code.count(')')
        if open_parens != close_parens:
            errors.append("Unbalanced parentheses")
        
        # Check for balanced quotes
        single_quotes = plantuml_code.count("'")
        double_quotes = plantuml_code.count('"')
        if double_quotes % 2 != 0:
            errors.append("Unbalanced double quotes")
        
        return len(errors) == 0, errors
