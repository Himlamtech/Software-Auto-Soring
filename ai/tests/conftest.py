"""Pytest configuration and shared fixtures."""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.config.settings import Settings


@pytest.fixture
def test_settings():
    """Get test-specific settings."""
    return Settings(
        debug=True,
        storage_path="./test_data",
        llm_model="gpt-3.5-turbo",  # Use cheaper model for tests
        openai_api_key="test-key"
    )


@pytest.fixture
def test_client():
    """Get test client for API testing."""
    return TestClient(app)


@pytest.fixture
def sample_plantuml():
    """Sample PlantUML code for testing."""
    return """
    @startuml
    actor User
    actor Administrator
    
    usecase "Login to System" as UC1
    usecase "Manage Users" as UC2
    usecase "View Reports" as UC3
    
    User --> UC1
    User --> UC3
    Administrator --> UC1
    Administrator --> UC2
    Administrator --> UC3
    
    UC2 ..> UC1 : <<include>>
    @enduml
    """


@pytest.fixture
def sample_problem_description():
    """Sample problem description for testing."""
    return """
    Design a web-based user management system for a company.
    
    Functional Requirements:
    1. Users should be able to login to the system with username and password
    2. Administrators should be able to create, update, and delete user accounts
    3. Both users and administrators should be able to view system reports
    4. The system should maintain audit logs of all user activities
    
    Expected Actors:
    - User: Regular system user
    - Administrator: System administrator with elevated privileges
    
    Expected Use Cases:
    - Login to System: Authentication functionality
    - Manage Users: CRUD operations for user accounts
    - View Reports: Access to system reports and analytics
    """


@pytest.fixture(autouse=True)
def cleanup_test_data():
    """Clean up test data after each test."""
    yield
    # Cleanup logic here if needed
    pass
