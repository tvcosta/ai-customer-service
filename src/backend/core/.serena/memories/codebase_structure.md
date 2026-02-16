# Codebase Structure

## Monorepo Layout
```
CLAUDE.md                          → Root project instructions
Plans/                             → Execution plans for multi-agent orchestration
  00-orchestration-plan.md
  01-phases.md
  02-agent-core-plan.md
  03-agent-api-plan.md
  04-agent-frontend-plan.md
  05-orchestrator-runbook.md
docs/contracts/                    → Shared API contracts
  shared-models.md
  core-api.openapi.yaml
  backend-api.openapi.yaml
docker-compose.yml                 → Full stack: core, api, frontend, ollama, tempo, grafana
docker/                            → Docker configs (grafana-datasources.yaml, tempo.yaml)
.env.example                       → Environment variable template

src/backend/core/                  → Python Core (FastAPI + LangChain + LangGraph)
  app/
    main.py                        → FastAPI app factory
    config.py                      → Pydantic Settings
    domain/models/                 → Domain entities (citation, chunk, document, etc.)
    domain/ports/                  → Port interfaces (llm, vectorstore, document_store, interaction_store)
    domain/services/               → Domain services (grounding_service)
    application/use_cases/         → Use case orchestration (TODO Phase 2)
    application/dto/               → DTOs (TODO Phase 2)
    infrastructure/                → LLM, vectorstore, persistence, telemetry adapters
    interfaces/api/routes/         → REST routes (health.py)
  pyproject.toml
  Dockerfile

src/backend/api/                   → .NET API (FastEndpoints)
  AiCustomerService.Api.slnx       → Solution file
  Directory.Build.props             → .NET 10, C# 13, TreatWarningsAsErrors
  src/AiCustomerService.Api/
    Program.cs                     → FastEndpoints + OpenTelemetry setup
    Domain/Models/SharedModels.cs  → Domain records matching contracts
    Application/Interfaces/        → ICoreApiClient
    Application/Services/          → CoreApiClient (HttpClient-based)
    Infrastructure/Telemetry/      → TelemetrySetup
  tests/AiCustomerService.Api.Tests/
  Dockerfile

src/frontend/admin/                → Next.js 15 Frontend
  src/app/                         → App Router pages (dashboard, knowledge-bases, interactions, playground)
  src/components/layout/           → Shell, sidebar, header
  src/lib/types/                   → TypeScript interfaces matching contracts
  src/lib/api/client.ts            → API client
  package.json
  Dockerfile
```
