"""File-based storage implementation for submissions and results."""

import json
import os
from typing import Optional, Dict, Any
from datetime import datetime
from pathlib import Path
from app.core.models.input_output import StudentSubmission, ProblemDescription, ScoringRequest
from app.core.models.scoring import ScoringResult


class FileStorageService:
    """File-based storage service for submissions and scoring results."""
    
    def __init__(self, base_path: str = "./data"):
        """
        Initialize file storage service.
        
        Args:
            base_path: Base directory for file storage
        """
        self.base_path = Path(base_path)
        self.submissions_path = self.base_path / "submissions"
        self.results_path = self.base_path / "results"
        self.problems_path = self.base_path / "problems"
        
        # Create directories if they don't exist
        for path in [self.submissions_path, self.results_path, self.problems_path]:
            path.mkdir(parents=True, exist_ok=True)
    
    async def save_submission(
        self,
        submission: StudentSubmission,
        submission_id: str
    ) -> str:
        """
        Save student submission to file storage.
        
        Args:
            submission: Student submission to save
            submission_id: Unique identifier for the submission
            
        Returns:
            File path where submission was saved
        """
        timestamp = datetime.now().isoformat()
        submission_data = {
            "submission_id": submission_id,
            "timestamp": timestamp,
            "student_id": submission.student_id,
            "plantuml_code": submission.plantuml_code,
            "submission_time": submission.submission_time,
            "file_name": submission.file_name
        }
        
        file_path = self.submissions_path / f"{submission_id}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(submission_data, f, indent=2, ensure_ascii=False)
        
        # Also save PlantUML code as separate file
        puml_path = self.submissions_path / f"{submission_id}.puml"
        with open(puml_path, "w", encoding="utf-8") as f:
            f.write(submission.plantuml_code)
        
        return str(file_path)
    
    async def load_submission(self, submission_id: str) -> Optional[StudentSubmission]:
        """
        Load student submission from file storage.
        
        Args:
            submission_id: Unique identifier for the submission
            
        Returns:
            StudentSubmission if found, None otherwise
        """
        file_path = self.submissions_path / f"{submission_id}.json"
        if not file_path.exists():
            return None
        
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        return StudentSubmission(
            student_id=data.get("student_id"),
            plantuml_code=data["plantuml_code"],
            submission_time=data.get("submission_time"),
            file_name=data.get("file_name")
        )
    
    async def save_scoring_result(
        self,
        result: ScoringResult,
        submission_id: str,
        result_id: str
    ) -> str:
        """
        Save scoring result to file storage.
        
        Args:
            result: Scoring result to save
            submission_id: Associated submission ID
            result_id: Unique identifier for the result
            
        Returns:
            File path where result was saved
        """
        timestamp = datetime.now().isoformat()
        result_data = {
            "result_id": result_id,
            "submission_id": submission_id,
            "timestamp": timestamp,
            "final_score": result.score.final_score,
            "overall_metrics": result.score.overall_metrics.dict(),
            "component_scores": [cs.dict() for cs in result.score.component_scores],
            "feedback": [fb.dict() for fb in result.feedback],
            "processing_time": result.processing_time,
            "llm_model_used": result.llm_model_used
        }
        
        file_path = self.results_path / f"{result_id}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(result_data, f, indent=2, ensure_ascii=False)
        
        return str(file_path)
    
    async def load_scoring_result(self, result_id: str) -> Optional[Dict[str, Any]]:
        """
        Load scoring result from file storage.
        
        Args:
            result_id: Unique identifier for the result
            
        Returns:
            Scoring result data if found, None otherwise
        """
        file_path = self.results_path / f"{result_id}.json"
        if not file_path.exists():
            return None
        
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    
    async def save_problem_description(
        self,
        problem: ProblemDescription,
        problem_id: str
    ) -> str:
        """
        Save problem description to file storage.
        
        Args:
            problem: Problem description to save
            problem_id: Unique identifier for the problem
            
        Returns:
            File path where problem was saved
        """
        timestamp = datetime.now().isoformat()
        problem_data = {
            "problem_id": problem_id,
            "timestamp": timestamp,
            "title": problem.title,
            "description": problem.description,
            "functional_requirements": problem.functional_requirements,
            "expected_actors": problem.expected_actors,
            "expected_use_cases": problem.expected_use_cases,
            "grading_criteria": problem.grading_criteria
        }
        
        file_path = self.problems_path / f"{problem_id}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(problem_data, f, indent=2, ensure_ascii=False)
        
        return str(file_path)
    
    async def load_problem_description(self, problem_id: str) -> Optional[ProblemDescription]:
        """
        Load problem description from file storage.
        
        Args:
            problem_id: Unique identifier for the problem
            
        Returns:
            ProblemDescription if found, None otherwise
        """
        file_path = self.problems_path / f"{problem_id}.json"
        if not file_path.exists():
            return None
        
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        return ProblemDescription(
            title=data["title"],
            description=data["description"],
            functional_requirements=data.get("functional_requirements"),
            expected_actors=data.get("expected_actors"),
            expected_use_cases=data.get("expected_use_cases"),
            grading_criteria=data.get("grading_criteria")
        )
    
    async def list_submissions(self, student_id: Optional[str] = None) -> list:
        """
        List all submissions, optionally filtered by student ID.
        
        Args:
            student_id: Optional student ID filter
            
        Returns:
            List of submission metadata
        """
        submissions = []
        for file_path in self.submissions_path.glob("*.json"):
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            if student_id is None or data.get("student_id") == student_id:
                submissions.append({
                    "submission_id": data["submission_id"],
                    "student_id": data.get("student_id"),
                    "timestamp": data["timestamp"],
                    "file_name": data.get("file_name")
                })
        
        return sorted(submissions, key=lambda x: x["timestamp"], reverse=True)
    
    async def cleanup_old_files(self, days_old: int = 30) -> int:
        """
        Clean up files older than specified days.
        
        Args:
            days_old: Number of days after which files are considered old
            
        Returns:
            Number of files cleaned up
        """
        cutoff_time = datetime.now().timestamp() - (days_old * 24 * 60 * 60)
        cleaned_count = 0
        
        for directory in [self.submissions_path, self.results_path]:
            for file_path in directory.glob("*"):
                if file_path.stat().st_mtime < cutoff_time:
                    file_path.unlink()
                    cleaned_count += 1
        
        return cleaned_count
