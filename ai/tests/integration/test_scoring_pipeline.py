"""Integration tests for scoring pipeline."""

import pytest
from app.core.pipeline.scoring_pipeline import ScoringPipeline
from app.core.models.input_output import ScoringRequest, StudentSubmission, ProblemDescription


class TestScoringPipelineIntegration:
    """Integration tests for scoring pipeline."""
    
    @pytest.fixture
    def pipeline(self):
        """Get scoring pipeline instance."""
        return ScoringPipeline()
    
    @pytest.fixture
    def sample_submission(self):
        """Get sample student submission."""
        return StudentSubmission(
            student_id="student123",
            plantuml_code="""
            @startuml
            actor User
            actor Admin
            usecase "Login System" as UC1
            usecase "Manage Users" as UC2
            User --> UC1
            Admin --> UC2
            @enduml
            """,
            file_name="submission.puml"
        )
    
    @pytest.fixture
    def sample_problem(self):
        """Get sample problem description."""
        return ProblemDescription(
            title="User Management System",
            description="""
            Design a user management system that allows:
            - Users to login to the system
            - Administrators to manage user accounts
            The system should have proper authentication and authorization.
            """,
            functional_requirements="Login functionality and user management",
            expected_actors="User, Administrator",
            expected_use_cases="Login, Manage Users"
        )
    
    @pytest.mark.asyncio
    async def test_complete_scoring_flow(self, pipeline, sample_submission, sample_problem):
        """Test complete scoring flow from request to result."""
        request = ScoringRequest(
            submission=sample_submission,
            problem=sample_problem
        )
        
        result = await pipeline.process_scoring_request(request)
        
        assert result is not None
        assert result.score is not None
        assert 0.0 <= result.score.final_score <= 10.0
        assert len(result.score.component_scores) > 0
        assert result.processing_time is not None
    
    @pytest.mark.asyncio
    async def test_validation_error_handling(self, pipeline):
        """Test handling of validation errors."""
        invalid_request = ScoringRequest(
            submission=StudentSubmission(
                plantuml_code="",  # Empty code should cause validation error
                student_id="test"
            ),
            problem=ProblemDescription(
                title="Test",
                description=""  # Empty description should cause validation error
            )
        )
        
        with pytest.raises(ValueError):
            await pipeline.process_scoring_request(invalid_request)
