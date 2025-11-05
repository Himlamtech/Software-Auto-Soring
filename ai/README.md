# UML Auto Scoring AI

🎯 **AI-powered automatic scoring system for UML Use Case Diagrams using Large Language Models with optimized prompt engineering.**

## 📋 Overview

This system automatically evaluates UML Use Case Diagrams created by students in Software Engineering courses. It uses advanced Large Language Models to extract components from PlantUML code and problem descriptions, then provides detailed scoring and feedback.

### Key Features

- **Automated Component Extraction**: Uses LLMs to identify actors, use cases, and relationships
- **Multi-metric Scoring**: Calculates Precision, Recall, F1-Score, and Accuracy
- **Intelligent Feedback**: Generates educational feedback and improvement suggestions
- **Batch Processing**: Supports scoring multiple submissions simultaneously
- **RESTful API**: Modern FastAPI-based web service
- **Extensible Architecture**: Clean architecture with dependency injection

## 🏗️ System Architecture

### Processing Pipeline (5 Steps)

1. **Input Collection & Validation**
   - PlantUML code validation
   - Problem description processing
   - File format verification

2. **LLM-based Component Extraction**
   - Extract actors, use cases, relationships from PlantUML
   - Extract expected components from problem description
   - Use optimized prompts for each component type

3. **Semantic Comparison**
   - Match actual vs expected components
   - Calculate True Positives, False Positives, False Negatives
   - Support for semantic similarity matching

4. **Metrics Calculation**
   - Precision = TP / (TP + FP)
   - Recall = TP / (TP + FN)
   - F1-Score = 2 × (Precision × Recall) / (Precision + Recall)
   - Accuracy = TP / (TP + FP + FN)
   - Weighted final score (0-10 scale)

5. **Feedback Generation**
   - Identify strengths and weaknesses
   - Suggest specific improvements
   - Highlight missing or incorrect components

### Project Structure

```
app/
├── core/                 # Domain logic
│   ├── models/          # Domain models (UML components, scoring)
│   ├── scoring/         # Scoring algorithms and metrics
│   └── pipeline/        # Main processing pipeline
├── services/            # Service abstractions
│   ├── llm/            # LLM interfaces
│   └── parsing/        # PlantUML parsing
├── infra/              # Infrastructure implementations
│   ├── llm_providers/  # LLM provider implementations
│   ├── storage/        # File storage
│   └── external/       # External service integrations
├── api/                # FastAPI application
│   ├── routers/        # API endpoints
│   ├── schemas/        # Request/response models
│   └── dependencies/   # Dependency injection
├── config/             # Configuration and settings
└── utils/              # Utility functions
```

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- LLM API key (OpenAI or Google Gemini)
- Optional: PlantUML jar file for local diagram generation

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd AnDAutoScoring/ai
   ```

2. **Install dependencies**
   ```bash
   # Using uv (recommended)
   uv sync

   # Or using pip
   pip install -e ".[dev]"
   ```

3. **Configure environment**
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

4. **Check configuration**
   ```bash
   python scripts/check_config.py
   ```

5. **Run the application**
   ```bash
   python main.py
   ```

   Or with uvicorn:
   ```bash
   uvicorn app.main:app --reload
   ```

### API Documentation

Once running, visit:
- **Interactive API docs**: http://localhost:8000/docs
- **ReDoc documentation**: http://localhost:8000/redoc

## 📚 Usage Examples

### 1. Submit PlantUML for Scoring

```python
import httpx

# Submit PlantUML code for scoring
response = httpx.post("http://localhost:8000/scoring/submit", json={
    "student_id": "student123",
    "plantuml_code": """
    @startuml
    actor User
    actor Admin
    usecase "Login" as UC1
    usecase "Manage Users" as UC2
    User --> UC1
    Admin --> UC2
    @enduml
    """,
    "problem_id": "problem456"
})

result = response.json()
print(f"Score: {result['final_score']}/10")
```

### 2. Create a Problem

```python
# Create a new problem for assignments
response = httpx.post("http://localhost:8000/problems/", json={
    "title": "User Management System",
    "description": "Design a system for user authentication and management...",
    "functional_requirements": "Login, user CRUD operations, admin panel",
    "expected_actors": "User, Administrator",
    "expected_use_cases": "Login, Manage Users, View Reports"
})

problem_id = response.json()["problem_id"]
```

### 3. Batch Scoring

```python
# Score multiple submissions at once
response = httpx.post("http://localhost:8000/scoring/batch", json={
    "problem_id": "problem456",
    "submissions": [
        {"student_id": "student1", "plantuml_code": "..."},
        {"student_id": "student2", "plantuml_code": "..."},
        # ... more submissions
    ]
})

results = response.json()["results"]
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test types
pytest -m unit           # Unit tests only
pytest -m integration    # Integration tests only
pytest -m "not slow"     # Skip slow tests
```

## 🔧 Configuration

Key configuration options in `.env`:

| Variable | Description | Default |
|----------|-------------|---------|
| `LLM_PROVIDER` | LLM provider to use (openai/gemini) | `openai` |
| `OPENAI_API_KEY` | OpenAI API key | Required if using OpenAI |
| `GEMINI_API_KEY` | Google Gemini API key | Required if using Gemini |
| `LLM_MODEL` | OpenAI model to use | `gpt-4o-mini` |
| `GEMINI_MODEL` | Gemini model to use | `gemini-1.5-flash` |
| `API_PORT` | Server port | `8000` |
| `STORAGE_PATH` | Base path for file storage | `./data` |
| `DEFAULT_ACTOR_WEIGHT` | Weight for actor scoring | `0.3` |
| `DEFAULT_USECASE_WEIGHT` | Weight for use case scoring | `0.5` |
| `DEFAULT_RELATIONSHIP_WEIGHT` | Weight for relationship scoring | `0.2` |

### LLM Provider Setup

**For OpenAI:**
1. Get API key from: https://platform.openai.com/api-keys
2. Set `LLM_PROVIDER=openai` and `OPENAI_API_KEY=your_key`

**For Google Gemini:**
1. Get API key from: https://aistudio.google.com/app/apikey
2. Set `LLM_PROVIDER=gemini` and `GEMINI_API_KEY=your_key`

## 🛠️ Development

### Code Quality

The project uses several tools for code quality:

```bash
# Format code
black app tests

# Lint code
ruff check app tests

# Type checking
mypy app

# Security scanning
bandit -r app

# All checks (via pre-commit)
pre-commit run --all-files
```

### Adding New LLM Providers

1. Create a new provider in `app/infra/llm_providers/`
2. Implement the `LLMExtractionService` and `LLMFeedbackService` interfaces
3. Add configuration options in `app/config/settings.py`
4. Update dependency injection in `app/api/dependencies/services.py`

### Custom Scoring Algorithms

1. Extend `ComponentMatcher` in `app/core/scoring/component_matcher.py`
2. Add new metrics in `MetricsCalculator`
3. Update the scoring pipeline to use new algorithms

## 📊 Metrics and Evaluation

The system provides comprehensive scoring metrics:

- **Precision**: Ratio of correctly identified components to all identified components
- **Recall**: Ratio of correctly identified components to all expected components  
- **F1-Score**: Harmonic mean of precision and recall
- **Accuracy**: Ratio of correct identifications to total components
- **Component-wise Scores**: Separate metrics for actors, use cases, and relationships
- **Weighted Final Score**: Combined score on 0-10 scale

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and quality checks
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- PlantUML project for UML diagram syntax
- OpenAI for GPT models
- FastAPI framework for the web API
- The education technology community for inspiration and requirements
