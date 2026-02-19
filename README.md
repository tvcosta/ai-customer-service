# AI Customer Service

Knowledge Base-powered customer service automation system. Upload documents, ask questions, and get cited answers -- all grounded strictly in your Knowledge Base content.

## Architecture Overview

Three-service architecture following DDD / Clean Architecture principles:

```
+-------------------+      +--------------------+      +---------------------+      +-----------------+
|                   |      |                    |      |                     |      |                 |
|  Frontend Admin   | ---> |   Backend API      | ---> |   Backend Core      | ---> |     Ollama      |
|  (Next.js :3000)  |      |  (.NET :5000)      |      |  (Python :8000)     |      |    (:11434)     |
|                   |      |                    |      |                     |      |                 |
+-------------------+      +--------------------+      +---------------------+      +-----------------+
        |                          |                           |
        |                          |                           |
        +------------- OpenTelemetry (OTLP) ------------------>+---> Tempo (:4317) ---> Grafana (:3001)
```

- **Frontend Admin** -- Next.js 15 dashboard for managing Knowledge Bases, testing queries, and reviewing interaction history.
- **Backend API** -- .NET 10 gateway that validates requests and proxies to Backend Core. Contains no business logic.
- **Backend Core** -- Python FastAPI service that owns all business logic: RAG pipeline, LLM orchestration, grounding, and citation generation.
- **Ollama** -- Local LLM provider running the configured model (default: llama3.2).

The system answers ONLY from Knowledge Base content. If the KB does not contain the answer, it returns `status: "unknown"` with mandatory citations on all answered responses.

## Prerequisites

### Docker (recommended)

- [Docker](https://docs.docker.com/get-docker/) 24+
- [Docker Compose](https://docs.docker.com/compose/install/) v2+

### Local development (individual services)

| Service | Requirements |
|---------|-------------|
| Backend Core | Python 3.12+, [uv](https://docs.astral.sh/uv/) |
| Backend API | [.NET 10 SDK](https://dotnet.microsoft.com/download) |
| Frontend Admin | Node.js 22+, [pnpm](https://pnpm.io/) |
| LLM Provider | [Ollama](https://ollama.ai/) with a pulled model |

## Quick Start

```bash
# Clone the repository
git clone <repository-url>
cd ai-customer-service

# Copy environment variables
cp .env.example .env

# Start all services
docker compose up --build
```

Once running:

| Service | URL |
|---------|-----|
| Frontend Admin | http://localhost:3000 |
| Backend API | http://localhost:5000 |
| Backend Core | http://localhost:8000 |
| Grafana (traces) | http://localhost:3001 |
| Ollama | http://localhost:11434 |

Pull the LLM model if not already available:

```bash
docker compose exec ollama ollama pull llama3.2
```

## Development Setup

### Backend Core (Python)

```bash
cd src/backend/core

# Install dependencies
uv sync

# Run the service
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Run tests
uv run pytest
```

Requires Ollama running locally on port 11434.

### Backend API (.NET)

```bash
cd src/backend/api

# Restore and build
dotnet restore
dotnet build

# Run the service
dotnet run --project src/AiCustomerService.Api

# Run tests
dotnet test
```

Requires Backend Core running on port 8000.

### Frontend Admin (Next.js)

```bash
cd src/frontend/admin

# Install dependencies
pnpm install

# Run the dev server
pnpm dev

# Run tests
pnpm test
```

Requires Backend API running on port 5000.

## Environment Variables

| Variable | Service | Default | Description |
|----------|---------|---------|-------------|
| `OLLAMA_BASE_URL` | Core | `http://localhost:11434` | Ollama API base URL |
| `OLLAMA_MODEL` | Core | `llama3.2` | LLM model name |
| `DATABASE_URL` | Core | `sqlite:///data/db/core.db` | SQLite database connection string |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | Core, API | `http://localhost:4317` | OpenTelemetry collector endpoint |
| `OTEL_SERVICE_NAME` | Core | `ai-customer-service-core` | OTel service name for Core |
| `OTEL_SERVICE_NAME` | API | `ai-customer-service-api` | OTel service name for API |
| `CoreApi__BaseUrl` | API | `http://localhost:8000` | Backend Core base URL |
| `CoreApi__TimeoutSeconds` | API | `30` | Timeout for Core API calls (seconds) |
| `ASPNETCORE_URLS` | API | `http://localhost:5000` | .NET listener URL |
| `NEXT_PUBLIC_API_URL` | Frontend | `http://localhost:5000` | Backend API URL for the frontend |
| `GF_AUTH_ANONYMOUS_ENABLED` | Grafana | `true` | Enable anonymous access to Grafana |
| `GF_AUTH_ANONYMOUS_ORG_ROLE` | Grafana | `Admin` | Role for anonymous Grafana users |

See `.env.example` for a ready-to-use template.

## API Endpoints

All endpoints are prefixed with `/api/v1/`. The Backend API mirrors the Core API and adds a dashboard stats endpoint.

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/v1/health` | Health check (API also reports Core connectivity) |
| `POST` | `/api/v1/query` | Ask a question against a Knowledge Base |
| `GET` | `/api/v1/knowledge-bases` | List all Knowledge Bases |
| `POST` | `/api/v1/knowledge-bases` | Create a new Knowledge Base |
| `GET` | `/api/v1/knowledge-bases/{id}` | Get Knowledge Base details |
| `DELETE` | `/api/v1/knowledge-bases/{id}` | Delete a Knowledge Base |
| `GET` | `/api/v1/knowledge-bases/{id}/documents` | List documents in a KB |
| `POST` | `/api/v1/knowledge-bases/{id}/documents` | Upload a document (multipart/form-data) |
| `DELETE` | `/api/v1/knowledge-bases/{id}/documents/{doc_id}` | Delete a document |
| `POST` | `/api/v1/knowledge-bases/{id}/index` | Trigger re-indexing |
| `GET` | `/api/v1/interactions` | List past interactions (filterable) |
| `GET` | `/api/v1/interactions/{id}` | Get interaction details |
| `GET` | `/api/v1/dashboard/stats` | Aggregated dashboard statistics |

Full OpenAPI specs are available in `docs/contracts/`.

## Observability

The system uses OpenTelemetry for distributed tracing, with traces exported to Grafana Tempo.

- **Grafana** is available at http://localhost:3001 (anonymous access enabled by default).
- **Tempo** receives traces via OTLP gRPC on port 4317 and exposes a query API on port 3200.

Each query generates a unique `interaction_id` that is attached to all trace spans across services. You can search for this ID in Grafana to see the full request lifecycle:

1. Request enters the Backend API
2. API forwards to Backend Core
3. Core executes the RAG pipeline (retrieve, ground, generate)
4. Response flows back through the chain

The Frontend displays the `interaction_id` for every query result, making it easy to cross-reference with Grafana traces.

## Project Structure

```
ai-customer-service/
├── src/
│   ├── backend/
│   │   ├── core/              # Python: FastAPI + LangChain + LangGraph
│   │   └── api/               # .NET 10: FastEndpoints gateway
│   └── frontend/
│       └── admin/             # Next.js 15 + TypeScript admin UI
├── docs/
│   ├── contracts/             # Shared API contracts (OpenAPI specs)
│   │   ├── shared-models.md
│   │   ├── core-api.openapi.yaml
│   │   └── backend-api.openapi.yaml
│   └── architecture.md        # System architecture documentation
├── docker/                    # Docker support files (Tempo, Grafana configs)
├── tests/                     # Cross-project integration tests
├── Plans/                     # Execution plans for multi-agent orchestration
├── docker-compose.yml
├── .env.example
└── CLAUDE.md                  # Project instructions for AI agents
```

## Shared Contracts

All inter-service communication conforms to schemas defined in `docs/contracts/`:

- **`shared-models.md`** -- Canonical JSON schemas for all shared types
- **`core-api.openapi.yaml`** -- Core internal API spec (Core publishes, API consumes)
- **`backend-api.openapi.yaml`** -- Public API spec (API publishes, Frontend consumes)

JSON payloads use `snake_case` field names. All IDs are UUIDv4 strings. All timestamps are ISO 8601 UTC.
