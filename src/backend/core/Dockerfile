# Multi-stage build for Python Backend Core
# Stage 1: Builder - install dependencies
FROM python:3.12-slim AS builder

# Install uv for fast package management
RUN pip install --no-cache-dir uv

# Set working directory
WORKDIR /app

# Copy dependency files first (better layer caching)
COPY pyproject.toml ./

# Install dependencies using uv
RUN uv pip install --system --no-cache -r pyproject.toml

# Stage 2: Runtime
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY app/ ./app/

# Create directories for runtime data
RUN mkdir -p /app/data /app/logs

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/v1/health').read()"

# Run the application using the factory pattern
CMD ["uvicorn", "app.main:create_app", "--host", "0.0.0.0", "--port", "8000", "--factory"]
