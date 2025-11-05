"""Metrics calculation engine for Phase 2."""

from typing import List, Dict, Set, Any, Union
from pydantic import BaseModel
from dataclasses import dataclass
import difflib

from app.core.models.uml_components import UMLDiagram, Actor, UseCase, Relationship
from app.core.models.diagrams.class_diagram_models import ClassDiagram, UMLClass, ClassAttribute, ClassMethod, ClassRelationship
from app.core.models.diagrams.sequence_diagram_models import SequenceDiagram, Participant, Message
from app.core.models.diagrams.diagram_factory import DiagramType, DiagramUnion


@dataclass
class ComponentMetrics:
    """Metrics for a specific component type."""
    true_positives: int
    false_positives: int
    false_negatives: int
    precision: float
    recall: float
    f1_score: float
    accuracy: float


class DiagramMetrics(BaseModel):
    """Complete metrics for a diagram comparison."""
    diagram_type: DiagramType
    component_metrics: Dict[str, ComponentMetrics]
    overall_metrics: ComponentMetrics
    similarity_score: float
    total_expected: int
    total_actual: int
    total_matched: int


class MetricsEngine:
    """Engine for calculating quantitative metrics between diagrams."""
    
    def __init__(self, similarity_threshold: float = 0.85):
        """
        Initialize metrics engine.
        
        Args:
            similarity_threshold: Threshold for semantic similarity matching
        """
        self.similarity_threshold = similarity_threshold
    
    def calculate_diagram_metrics(
        self,
        expected_diagram: DiagramUnion,
        actual_diagram: DiagramUnion,
        diagram_type: DiagramType
    ) -> DiagramMetrics:
        """
        Calculate comprehensive metrics between expected and actual diagrams.
        
        Args:
            expected_diagram: Teacher's reference diagram
            actual_diagram: Student's diagram (normalized)
            diagram_type: Type of diagram being compared
            
        Returns:
            DiagramMetrics with complete comparison results
        """
        if diagram_type == DiagramType.USE_CASE:
            return self._calculate_use_case_metrics(expected_diagram, actual_diagram)
        elif diagram_type == DiagramType.CLASS:
            return self._calculate_class_metrics(expected_diagram, actual_diagram)
        elif diagram_type == DiagramType.SEQUENCE:
            return self._calculate_sequence_metrics(expected_diagram, actual_diagram)
        else:
            raise ValueError(f"Unsupported diagram type: {diagram_type}")
    
    def _calculate_use_case_metrics(self, expected: UMLDiagram, actual: UMLDiagram) -> DiagramMetrics:
        """Calculate metrics for use case diagrams."""
        component_metrics = {}
        
        # Calculate actor metrics
        expected_actors = {actor.name for actor in expected.actors}
        actual_actors = {actor.name for actor in actual.actors}
        actor_metrics = self._calculate_component_metrics(expected_actors, actual_actors)
        component_metrics['actor'] = actor_metrics
        
        # Calculate use case metrics
        expected_usecases = {uc.name for uc in expected.use_cases}
        actual_usecases = {uc.name for uc in actual.use_cases}
        usecase_metrics = self._calculate_component_metrics(expected_usecases, actual_usecases)
        component_metrics['use_case'] = usecase_metrics
        
        # Calculate relationship metrics
        expected_relationships = {self._relationship_key(rel) for rel in expected.relationships}
        actual_relationships = {self._relationship_key(rel) for rel in actual.relationships}
        relationship_metrics = self._calculate_component_metrics(expected_relationships, actual_relationships)
        component_metrics['relationship'] = relationship_metrics
        
        # Calculate overall metrics
        overall_metrics = self._aggregate_metrics(list(component_metrics.values()))
        
        # Calculate similarity score
        similarity_score = self._calculate_similarity_score(component_metrics)
        
        return DiagramMetrics(
            diagram_type=DiagramType.USE_CASE,
            component_metrics=component_metrics,
            overall_metrics=overall_metrics,
            similarity_score=similarity_score,
            total_expected=len(expected_actors) + len(expected_usecases) + len(expected_relationships),
            total_actual=len(actual_actors) + len(actual_usecases) + len(actual_relationships),
            total_matched=actor_metrics.true_positives + usecase_metrics.true_positives + relationship_metrics.true_positives
        )
    
    def _calculate_class_metrics(self, expected: ClassDiagram, actual: ClassDiagram) -> DiagramMetrics:
        """Calculate metrics for class diagrams."""
        component_metrics = {}
        
        # Calculate class metrics
        expected_classes = {cls.name for cls in expected.classes}
        actual_classes = {cls.name for cls in actual.classes}
        class_metrics = self._calculate_component_metrics(expected_classes, actual_classes)
        component_metrics['class'] = class_metrics
        
        # Calculate attribute metrics
        expected_attributes = set()
        actual_attributes = set()
        
        for cls in expected.classes:
            for attr in cls.attributes:
                expected_attributes.add(f"{cls.name}.{attr.name}")
        
        for cls in actual.classes:
            for attr in cls.attributes:
                actual_attributes.add(f"{cls.name}.{attr.name}")
        
        attribute_metrics = self._calculate_component_metrics(expected_attributes, actual_attributes)
        component_metrics['attribute'] = attribute_metrics
        
        # Calculate method metrics
        expected_methods = set()
        actual_methods = set()
        
        for cls in expected.classes:
            for method in cls.methods:
                expected_methods.add(f"{cls.name}.{method.name}")
        
        for cls in actual.classes:
            for method in cls.methods:
                actual_methods.add(f"{cls.name}.{method.name}")
        
        method_metrics = self._calculate_component_metrics(expected_methods, actual_methods)
        component_metrics['method'] = method_metrics
        
        # Calculate relationship metrics
        expected_relationships = {self._class_relationship_key(rel) for rel in expected.relationships}
        actual_relationships = {self._class_relationship_key(rel) for rel in actual.relationships}
        relationship_metrics = self._calculate_component_metrics(expected_relationships, actual_relationships)
        component_metrics['relationship'] = relationship_metrics
        
        # Calculate overall metrics
        overall_metrics = self._aggregate_metrics(list(component_metrics.values()))
        
        # Calculate similarity score
        similarity_score = self._calculate_similarity_score(component_metrics)
        
        return DiagramMetrics(
            diagram_type=DiagramType.CLASS,
            component_metrics=component_metrics,
            overall_metrics=overall_metrics,
            similarity_score=similarity_score,
            total_expected=len(expected_classes) + len(expected_attributes) + len(expected_methods) + len(expected_relationships),
            total_actual=len(actual_classes) + len(actual_attributes) + len(actual_methods) + len(actual_relationships),
            total_matched=sum(metrics.true_positives for metrics in component_metrics.values())
        )
    
    def _calculate_sequence_metrics(self, expected: SequenceDiagram, actual: SequenceDiagram) -> DiagramMetrics:
        """Calculate metrics for sequence diagrams."""
        component_metrics = {}
        
        # Calculate participant metrics
        expected_participants = {p.name for p in expected.participants}
        actual_participants = {p.name for p in actual.participants}
        participant_metrics = self._calculate_component_metrics(expected_participants, actual_participants)
        component_metrics['participant'] = participant_metrics
        
        # Calculate message metrics
        expected_messages = {self._message_key(msg) for msg in expected.messages}
        actual_messages = {self._message_key(msg) for msg in actual.messages}
        message_metrics = self._calculate_component_metrics(expected_messages, actual_messages)
        component_metrics['message'] = message_metrics
        
        # Calculate overall metrics
        overall_metrics = self._aggregate_metrics(list(component_metrics.values()))
        
        # Calculate similarity score
        similarity_score = self._calculate_similarity_score(component_metrics)
        
        return DiagramMetrics(
            diagram_type=DiagramType.SEQUENCE,
            component_metrics=component_metrics,
            overall_metrics=overall_metrics,
            similarity_score=similarity_score,
            total_expected=len(expected_participants) + len(expected_messages),
            total_actual=len(actual_participants) + len(actual_messages),
            total_matched=participant_metrics.true_positives + message_metrics.true_positives
        )
    
    def _calculate_component_metrics(self, expected: Set[str], actual: Set[str]) -> ComponentMetrics:
        """Calculate metrics for a specific component type."""
        # Use semantic matching for better comparison
        matched_pairs = self._semantic_matching(expected, actual)
        
        true_positives = len(matched_pairs)
        false_positives = len(actual) - true_positives
        false_negatives = len(expected) - true_positives
        
        # Calculate metrics
        precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0.0
        recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0.0
        f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
        accuracy = true_positives / (true_positives + false_positives + false_negatives) if (true_positives + false_positives + false_negatives) > 0 else 0.0
        
        return ComponentMetrics(
            true_positives=true_positives,
            false_positives=false_positives,
            false_negatives=false_negatives,
            precision=precision,
            recall=recall,
            f1_score=f1_score,
            accuracy=accuracy
        )
    
    def _semantic_matching(self, expected: Set[str], actual: Set[str]) -> Set[tuple]:
        """Perform semantic matching between expected and actual components."""
        matched_pairs = set()
        used_actual = set()
        
        for exp_item in expected:
            best_match = None
            best_similarity = 0.0
            
            for act_item in actual:
                if act_item in used_actual:
                    continue
                
                similarity = self._calculate_similarity(exp_item, act_item)
                if similarity >= self.similarity_threshold and similarity > best_similarity:
                    best_match = act_item
                    best_similarity = similarity
            
            if best_match:
                matched_pairs.add((exp_item, best_match))
                used_actual.add(best_match)
        
        return matched_pairs
    
    def _calculate_similarity(self, str1: str, str2: str) -> float:
        """Calculate similarity between two strings."""
        # Normalize strings
        str1_norm = str1.lower().strip()
        str2_norm = str2.lower().strip()
        
        # Exact match
        if str1_norm == str2_norm:
            return 1.0
        
        # Use difflib for sequence matching
        similarity = difflib.SequenceMatcher(None, str1_norm, str2_norm).ratio()
        
        # Boost similarity for common variations
        if self._are_semantic_variants(str1_norm, str2_norm):
            similarity = min(1.0, similarity + 0.2)
        
        return similarity
    
    def _are_semantic_variants(self, str1: str, str2: str) -> bool:
        """Check if two strings are semantic variants."""
        # Common variations
        variants = [
            ('user', 'nguoi dung', 'người dùng'),
            ('admin', 'quan tri', 'quản trị'),
            ('student', 'hoc sinh', 'học sinh', 'sinh vien', 'sinh viên'),
            ('teacher', 'giao vien', 'giáo viên'),
            ('login', 'dang nhap', 'đăng nhập'),
            ('logout', 'dang xuat', 'đăng xuất'),
            ('manage', 'quan ly', 'quản lý'),
            ('create', 'tao', 'tạo'),
            ('delete', 'xoa', 'xóa'),
            ('update', 'cap nhat', 'cập nhật'),
        ]
        
        for variant_group in variants:
            if str1 in variant_group and str2 in variant_group:
                return True
        
        return False
    
    def _aggregate_metrics(self, metrics_list: List[ComponentMetrics]) -> ComponentMetrics:
        """Aggregate metrics from multiple components."""
        total_tp = sum(m.true_positives for m in metrics_list)
        total_fp = sum(m.false_positives for m in metrics_list)
        total_fn = sum(m.false_negatives for m in metrics_list)
        
        precision = total_tp / (total_tp + total_fp) if (total_tp + total_fp) > 0 else 0.0
        recall = total_tp / (total_tp + total_fn) if (total_tp + total_fn) > 0 else 0.0
        f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
        accuracy = total_tp / (total_tp + total_fp + total_fn) if (total_tp + total_fp + total_fn) > 0 else 0.0
        
        return ComponentMetrics(
            true_positives=total_tp,
            false_positives=total_fp,
            false_negatives=total_fn,
            precision=precision,
            recall=recall,
            f1_score=f1_score,
            accuracy=accuracy
        )
    
    def _calculate_similarity_score(self, component_metrics: Dict[str, ComponentMetrics]) -> float:
        """Calculate overall similarity score."""
        if not component_metrics:
            return 0.0
        
        # Weighted average of F1 scores
        total_weight = 0
        weighted_sum = 0
        
        for component_type, metrics in component_metrics.items():
            weight = 1.0  # Equal weight for now, can be customized
            weighted_sum += metrics.f1_score * weight
            total_weight += weight
        
        return weighted_sum / total_weight if total_weight > 0 else 0.0
    
    def _relationship_key(self, rel: Relationship) -> str:
        """Generate key for relationship comparison."""
        return f"{rel.source}->{rel.target}:{rel.relationship_type}"
    
    def _class_relationship_key(self, rel: ClassRelationship) -> str:
        """Generate key for class relationship comparison."""
        return f"{rel.source}->{rel.target}:{rel.relationship_type.value}"
    
    def _message_key(self, msg: Message) -> str:
        """Generate key for message comparison."""
        return f"{msg.source}->{msg.target}:{msg.label}"
