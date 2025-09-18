"""Main application entry point."""

import uvicorn
from app.main import app
from app.config.settings import get_settings


if __name__ == "__main__":
    settings = get_settings()
    
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        workers=settings.api_workers,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
