"""FastAPI application factory and entry point."""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import Settings
from app.interfaces.api.routes import health


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager for startup and shutdown events."""
    # Startup: Initialize resources here in future phases
    yield
    # Shutdown: Clean up resources here in future phases


def create_app() -> FastAPI:
    """Create and configure the FastAPI application.

    Returns:
        Configured FastAPI application instance.
    """
    settings = Settings()

    app = FastAPI(
        title="AI Customer Service Core",
        version="0.1.0",
        description="RAG and LLM orchestration service for AI customer service",
        lifespan=lifespan,
    )

    # CORS middleware for development
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(health.router)

    return app


if __name__ == "__main__":
    import uvicorn

    settings = Settings()
    uvicorn.run(
        "app.main:create_app",
        host=settings.host,
        port=settings.port,
        factory=True,
        reload=True,
    )
