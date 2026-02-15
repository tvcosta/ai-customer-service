# Project Instructions - AI Customer Service System

## Overview
Customer service automation system that answers questions using a Knowledge Base.
Three-service architecture: Python Core (RAG + LLM) -> .NET API (public gateway) -> Next.js Frontend (admin UI).

## Monorepo Layout
```
src/backend/core/    → Agent 1 (Python: FastAPI + LangChain + LangGraph)
src/backend/api/     → Agent 2 (.NET 10: FastEndpoints)
src/frontend/admin/  → Agent 3 (Next.js 15 + TypeScript)
docs/contracts/      → Shared API contracts (OpenAPI specs, shared models)
tests/               → Cross-project integration tests
Plans/               → Execution plans for multi-agent orchestration
```

## Hard Rules (Non-Negotiable)
1. **KB-Only Answers** - The system answers ONLY from Knowledge Base content. Never guess.
2. **UNKNOWN when unsupported** - If KB doesn't contain the answer, return `status: "unknown"` with message: `"I don't have that information in the provided knowledge base."`
3. **Citations mandatory** - Every `status: "answered"` response MUST include non-empty `citations` with source_document, page, chunk_id.
4. **Strict JSON output** - All API responses are valid JSON conforming to the response schema. No prose outside JSON.
5. **Audit via OpenTelemetry** - Every interaction traced with: question, retrieval results, grounding decision, final answer, `interaction_id`.

## Architecture
- **DDD / Clean Architecture** across all services
- **Domain Layer**: Pure business rules, no framework imports
- **Application Layer**: Use cases, orchestration, port interfaces
- **Infrastructure Layer**: LangGraph, LLM adapters, persistence, telemetry
- **Interfaces Layer**: REST endpoints

## Communication Flow
```
Frontend (Next.js :3000) → Backend API (.NET :5000) → Backend Core (Python :8000) → Ollama (:11434)
```
- Frontend ONLY talks to Backend API
- Backend API proxies to Backend Core
- Backend Core owns all business logic and LLM orchestration

## Shared Contracts
All inter-service contracts live in `docs/contracts/`:
- `shared-models.md` - Canonical JSON schemas for all shared types
- `core-api.openapi.yaml` - Core internal API spec (Core publishes, API consumes)
- `backend-api.openapi.yaml` - Public API spec (API publishes, Frontend consumes)

**Rule: Always read the contract before implementing integration code.**

## Standard Response Envelope
```json
{
  "status": "answered | unknown | error",
  "answer": "string or null",
  "citations": [{"source_document": "str", "page": 1, "chunk_id": "str", "relevance_score": 0.95}],
  "interaction_id": "uuid"
}
```

## Multi-Agent Orchestration
This project is built by 3 parallel agents coordinated by an orchestrator.
See `Plans/` for detailed execution plans and phase breakdowns.

### Agent Boundaries
| Agent | Directory | Publishes | Consumes |
|-------|-----------|-----------|----------|
| Core (Python) | `src/backend/core/` | `core-api.openapi.yaml` | `shared-models.md` |
| API (.NET) | `src/backend/api/` | `backend-api.openapi.yaml` | `core-api.openapi.yaml`, `shared-models.md` |
| Frontend (Next.js) | `src/frontend/admin/` | Nothing | `backend-api.openapi.yaml`, `shared-models.md` |

### Sync Points
- **S1**: All 3 projects scaffold, build, and run with health endpoints
- **S2**: Core API spec published to `docs/contracts/core-api.openapi.yaml`
- **S3**: Backend API spec published to `docs/contracts/backend-api.openapi.yaml`
- **S4**: End-to-end round-trip works (Frontend → API → Core → LLM)
- **S5**: OpenTelemetry traces visible in Grafana

## Coding Standards

### Python (Backend Core)
- Python 3.12+, type hints on all functions
- Pydantic for all DTOs and API schemas
- async/await for all I/O operations
- Domain layer: zero framework imports
- Use `uv` for package management

### C# (Backend API)
- .NET 10, C# 13
- FastEndpoints only (no MVC controllers, no minimal API)
- Records for DTOs, sealed classes
- IHttpClientFactory for all outbound HTTP
- Async all the way down

### TypeScript (Frontend)
- Next.js 15 App Router, React 19
- Server Components by default, `"use client"` only when needed
- No `any` types - everything strictly typed
- Tailwind CSS + shadcn/ui for styling
- `pnpm` for package management

## Preferences
- Keep solutions simple and focused
- No over-engineering or premature abstraction
- Tests must be meaningful, not just for coverage
- Prefer composition over inheritance
- Log structured data, not string concatenation
