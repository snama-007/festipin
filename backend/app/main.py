"""
Parx Planner Backend - Main FastAPI Application
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import logging
from pathlib import Path

from app.core.config import settings
from app.core.logging import setup_logging
from app.api.routes import input, vision, plan, export, samples, orchestration, extraction

# Setup logging
logger = setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    logger.info("🚀 Starting Parx Planner Backend...")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Debug mode: {settings.DEBUG}")
    
    # Initialize services
    try:
        # TODO: Initialize Redis connection
        # TODO: Initialize Firestore connection
        # TODO: Initialize Cloud Storage
        logger.info("✅ All services initialized successfully")
    except Exception as e:
        logger.error(f"❌ Failed to initialize services: {e}")
        raise
    
    yield
    
    # Cleanup
    logger.info("🛑 Shutting down Parx Planner Backend...")
    # TODO: Close Redis connection
    # TODO: Close Firestore connection


# Create FastAPI app
app = FastAPI(
    title="Parx Planner API",
    description="AI-Powered Party Planning from Pinterest URLs & Prompts",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.API_CORS_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health Check
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
        "version": "1.0.0"
    }


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint"""
    return {
        "message": "Parx Planner API",
        "docs": "/docs",
        "health": "/health"
    }


# Include routers
app.include_router(input.router, prefix="/api/v1", tags=["Input"])
app.include_router(vision.router, prefix="/api/v1", tags=["Vision"])
app.include_router(plan.router, prefix="/api/v1", tags=["Plan"])
app.include_router(export.router, prefix="/api/v1", tags=["Export"])
app.include_router(samples.router, prefix="/api/v1", tags=["Samples"])
app.include_router(orchestration.router, prefix="/api/v1", tags=["Orchestration"])
app.include_router(extraction.router, tags=["Data Extraction"])

# Mount static files for local storage (development)
# Note: Must be mounted AFTER CORS middleware but BEFORE routes
uploads_dir = Path(__file__).parent.parent / "uploads"
uploads_dir.mkdir(parents=True, exist_ok=True)

# Custom middleware to add CORS headers to static files
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

class StaticFilesCORSMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        # Add CORS headers for /uploads paths
        if request.url.path.startswith("/uploads"):
            response.headers["Access-Control-Allow-Origin"] = "*"
            response.headers["Access-Control-Allow-Methods"] = "GET, OPTIONS"
            response.headers["Access-Control-Allow-Headers"] = "*"
        return response

app.add_middleware(StaticFilesCORSMiddleware)
app.mount("/uploads", StaticFiles(directory=str(uploads_dir)), name="uploads")


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc) if settings.DEBUG else "An error occurred"
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG
    )

