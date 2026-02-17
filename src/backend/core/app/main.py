"""FastAPI application factory and entry point."""

from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import Settings
from app.dependencies import init_db, shutdown
from app.infrastructure.telemetry.setup import init_telemetry
from app.interfaces.api.middleware.tracing import InteractionIdMiddleware
from app.interfaces.api.routes import (
    dashboard,
    documents,
    health,
    interactions,
    knowledge_bases,
    query,
)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager for startup and shutdown events."""
    settings = Settings()
    init_telemetry(settings)
    await init_db()
    yield
    await shutdown()


def create_app() -> FastAPI:
    """Create and configure the FastAPI application.

    Returns:
        Configured FastAPI application instance.
    """
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

    # Inject interaction_id into response headers
    app.add_middleware(InteractionIdMiddleware)

    # Include routers
    app.include_router(health.router)
    app.include_router(query.router)
    app.include_router(knowledge_bases.router)
    app.include_router(documents.router)
    app.include_router(interactions.router)
    app.include_router(dashboard.router)

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
