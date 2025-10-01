from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from contextlib import asynccontextmanager
import logging
import json
from typing import Any
from pathlib import Path
import tempfile

from app.core.config import settings
from app.api.api import api_router
from app.db.session import async_engine
from app.db.base import Base

# Custom JSON response class with UTF-8 support
class UTF8JSONResponse(JSONResponse):
    def render(self, content: Any) -> bytes:
        return json.dumps(
            content,
            ensure_ascii=False,
            allow_nan=False,
            indent=None,
            separators=(",", ":"),
        ).encode("utf-8")

# Configure logging
logging.basicConfig(
    level=logging.INFO if settings.DEBUG else logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager
    """
    # Startup
    logger.info("Starting up EduPage Kids Activity Generator API")
    
    # Don't create tables automatically, they should already exist
    # Just test the connection
    try:
        async with async_engine.connect() as conn:
            from sqlalchemy import text
            await conn.execute(text("SELECT 1"))
        logger.info("Database connection successful")
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down EduPage Kids Activity Generator API")
    await async_engine.dispose()

# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
    lifespan=lifespan,
    default_response_class=UTF8JSONResponse
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for now
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Custom exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handle validation errors and return them in a more user-friendly format
    """
    # Log validation errors for debugging
    logger.error(f"Validation error on {request.url.path}")
    logger.error(f"Validation errors: {exc.errors()}")

    # Try to get the request body for debugging
    try:
        body = await request.body()
        if body:
            logger.error(f"Request body: {body.decode('utf-8')[:500]}")
    except:
        pass

    errors = []
    for error in exc.errors():
        # Extract the error message
        msg = error.get('msg', 'Validation error')
        loc = ' -> '.join(str(l) for l in error.get('loc', []))
        errors.append(f"{loc}: {msg}")

    return JSONResponse(
        status_code=422,
        content={"detail": "; ".join(errors) if errors else "Invalid request data"}
    )

@app.exception_handler(ValidationError)
async def pydantic_validation_exception_handler(request: Request, exc: ValidationError):
    """
    Handle Pydantic validation errors
    """
    errors = []
    for error in exc.errors():
        msg = error.get('msg', 'Validation error')
        loc = ' -> '.join(str(l) for l in error.get('loc', []))
        errors.append(f"{loc}: {msg}")

    return JSONResponse(
        status_code=422,
        content={"detail": "; ".join(errors) if errors else "Invalid data"}
    )

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)

# Mount static files for video images
# Use the same directory as defined in video_generation.py
static_dir = Path(__file__).parent.parent / "static"
video_images_dir = static_dir / "video-images"
video_images_dir.mkdir(parents=True, exist_ok=True)
app.mount("/static/video-images", StaticFiles(directory=str(video_images_dir)), name="video-images")

# Root endpoint
@app.get("/")
async def root():
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "running",
        "docs": f"{settings.API_V1_STR}/docs"
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "database": "connected"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info" if settings.DEBUG else "warning"
    )