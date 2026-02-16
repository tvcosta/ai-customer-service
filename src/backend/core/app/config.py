"""Application configuration management using pydantic-settings."""

from __future__ import annotations

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    app_name: str = "AI Customer Service Core"
    host: str = "0.0.0.0"
    port: int = 8000
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2"
    database_url: str = "sqlite+aiosqlite:///data/db/core.db"
    otel_exporter_otlp_endpoint: str = "http://localhost:4317"
    otel_service_name: str = "ai-customer-service-core"

    model_config = {"env_prefix": "", "case_sensitive": False}
