# Orchestration Plan - AI Customer Service System

## Agent Architecture

```
                    +---------------------+
                    |    ORCHESTRATOR      |
                    | (multi-agent-coord)  |
                    +---------------------+
                       /       |        \
                      /        |         \
              +--------+  +--------+  +----------+
              | AGENT 1|  | AGENT 2|  | AGENT 3  |
              |  Core  |  |  API   |  | Frontend |
              | Python |  | .NET   |  | Next.js  |
              +--------+  +--------+  +----------+
                  |            |            |
              src/backend/ src/backend/ src/frontend/
                core/        api/        admin/
```

## Agents

| Agent | Scope | Technology | Directory |
|-------|-------|-----------|-----------|
| **Agent 1 - Core** | Backend Core: domain logic, LLM orchestration, RAG pipeline, internal API | Python 3.12+, LangChain, LangGraph, FastAPI | `src/backend/core/` |
| **Agent 2 - API** | Backend API: public-facing endpoints, proxies to Core, auth | .NET 10, FastEndpoints | `src/backend/api/` |
| **Agent 3 - Frontend** | Admin UI: dashboard, KB management, interaction viewer | Next.js 15, React 19, TypeScript | `src/frontend/admin/` |

## Orchestrator Responsibilities

1. **Contract Management** - Maintain shared API contracts in `docs/contracts/`
2. **Phase Gating** - Ensure agents don't proceed past sync points until dependencies are met
3. **Integration Testing** - Coordinate cross-agent integration tests in `tests/`
4. **Docker Compose** - Maintain the root `docker-compose.yml` for the full stack
5. **Documentation** - Keep root `docs/` up to date

## Communication Protocol

Agents communicate through **shared contract files** rather than direct messaging:

```
docs/contracts/
  core-api.openapi.yaml      # Core's internal API spec (Agent 1 publishes, Agent 2 consumes)
  backend-api.openapi.yaml   # Backend API's public spec (Agent 2 publishes, Agent 3 consumes)
  shared-models.md           # Shared domain concepts and response schemas
```

**Rules:**
- The **publisher** creates and updates the contract file
- The **consumer** reads the contract file before implementing integration code
- The **orchestrator** validates contracts are consistent across boundaries
- Contracts are written BEFORE implementation begins for each phase

## Execution Phases

See `01-phases.md` for the detailed phase breakdown.

## Sync Points

| Sync Point | Gate Condition | Blocks |
|------------|---------------|--------|
| **S1** | All three projects scaffold successfully (build/run) | Phase 2 |
| **S2** | Core internal API spec published to `docs/contracts/core-api.openapi.yaml` | Agent 2 Phase 3 |
| **S3** | Backend API spec published to `docs/contracts/backend-api.openapi.yaml` | Agent 3 Phase 3 |
| **S4** | All endpoints return valid JSON per contract | Phase 4 |
| **S5** | OpenTelemetry traces flow end-to-end in Docker Compose | Phase 5 |

## Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| Core API spec delays block API agent | Agent 2 works against mock/stub spec; orchestrator provides initial contract |
| .NET ↔ Python serialization mismatches | Shared JSON schemas in contracts; integration tests validate |
| Frontend blocked by backend delays | Agent 3 uses MSW (Mock Service Worker) for API mocking during development |
| LLM provider (Ollama) availability | Core agent implements provider abstraction early; tests use deterministic stubs |
