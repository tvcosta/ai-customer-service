# AI Customer Service System - Project Overview

## Purpose
Customer service automation system that answers questions using a Knowledge Base.
Three-service architecture: Python Core (RAG + LLM) -> .NET API (public gateway) -> Next.js Frontend (admin UI).

## Hard Rules
1. **KB-Only Answers** - System answers ONLY from Knowledge Base content. Never guess.
2. **UNKNOWN when unsupported** - If KB doesn't have the answer, return `status: "unknown"`.
3. **Citations mandatory** - Every answered response MUST include citations with source_document, page, chunk_id.
4. **Strict JSON output** - All API responses conform to the response schema.
5. **Audit via OpenTelemetry** - Every interaction traced.

## Communication Flow
```
Frontend (Next.js :3000) → Backend API (.NET :5000) → Backend Core (Python :8000) → Ollama (:11434)
```

## Architecture
- DDD / Clean Architecture across all services
- Domain Layer: Pure business rules, no framework imports
- Application Layer: Use cases, orchestration, port interfaces
- Infrastructure Layer: LLM adapters, persistence, telemetry
- Interfaces Layer: REST endpoints

## Shared Contracts
All inter-service contracts live in `docs/contracts/`:
- `shared-models.md` - Canonical JSON schemas for all shared types
- `core-api.openapi.yaml` - Core internal API spec
- `backend-api.openapi.yaml` - Public API spec

## Current Status
- Phase 0 (Contracts) and Phase 1 (Scaffolding) are COMPLETE
- All 3 services build and have health endpoints (S1 gate passed)
- Phase 2 (Domain & Core Logic) is next
