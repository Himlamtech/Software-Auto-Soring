"""FastAPI application setup."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging

from app.config.settings import get_settings
from app.config.logging import setup_logging
from app.api.routers import scoring, problems


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    settings = get_settings()
    setup_logging(settings)
    logger = logging.getLogger(__name__)
    logger.info("Starting UML Auto Scoring AI application")
    
    yield
    
    # Shutdown
    logger.info("Shutting down UML Auto Scoring AI application")


# Create FastAPI application
app = FastAPI(
    title="UML Auto Scoring AI",
    description="""
    AI-powered automatic scoring system for UML Use Case Diagrams.
    
    This system uses Large Language Models with optimized prompt engineering to:
    - Extract components from PlantUML code and problem descriptions
    - Compare and evaluate diagram accuracy
    - Calculate scores using precision, recall, F1-score, and accuracy metrics
    - Generate detailed feedback and improvement suggestions
    """,
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Get settings
settings = get_settings()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(scoring.router)
app.include_router(problems.router)


@app.get("/", response_class=JSONResponse)
async def root():
    """Root endpoint with API information."""
    return {
        "name": "UML Auto Scoring AI",
        "version": "0.1.0",
        "description": "AI-powered automatic scoring system for UML Use Case Diagrams",
        "docs_url": "/docs",
        "endpoints": {
            "scoring": "/scoring",
            "problems": "/problems",
            "health": "/health"
        }
    }


@app.get("/health", response_class=JSONResponse)
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "UML Auto Scoring AI",
        "version": "0.1.0"
    }


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    logger = logging.getLogger(__name__)
    logger.error(f"Global exception: {str(exc)}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred while processing your request."
        }
    )
