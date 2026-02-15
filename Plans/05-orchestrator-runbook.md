# Orchestrator Runbook

## Role
The orchestrator is a `multi-agent-coordinator` agent that launches and coordinates the 3 worker agents.
It does NOT write application code itself. It manages contracts, integration, and gating.

## Startup Sequence

### 1. Create Shared Contracts (before launching agents)
Create `docs/contracts/shared-models.md` with the canonical JSON schemas:

```json
{
  "QueryResponse": {
    "status": "answered | unknown | error",
    "answer": "string | null",
    "citations": [
      {
        "source_document": "string",
        "page": "number | null",
        "chunk_id": "string",
        "relevance_score": "number"
      }
    ],
    "interaction_id": "uuid"
  }
}
```

### 2. Launch Agents in Parallel (Phase 1)
Launch all 3 agents simultaneously with their Phase 1 tasks:
- Agent 1 (Core): `python-pro` or `backend-developer` → scaffold Python project
- Agent 2 (API): `csharp-developer` or `backend-developer` → scaffold .NET project
- Agent 3 (Frontend): `nextjs-developer` → scaffold Next.js project

### 3. Gate: S1 Verification
After Phase 1 completes, verify:
- `src/backend/core/`: Python project builds, FastAPI starts, health endpoint responds
- `src/backend/api/`: .NET project builds, FastEndpoints starts, health endpoint responds
- `src/frontend/admin/`: Next.js builds, dev server starts, root page renders

### 4. Phase 2 Execution
- Agent 1 works on domain + RAG pipeline + internal API
- Agent 2 works on domain models + HttpClient interface + validators
- Agent 3 works on types + API client + mock data + UI pages
- Wait for Agent 1 to publish Core OpenAPI spec (S2 gate)

### 5. Phase 3 Execution
- All agents implement integration code against published contracts
- Wait for Agent 2 to publish Backend API spec (S3 gate)
- Verify end-to-end round-trip (S4 gate)

### 6. Phase 4 Execution
- All agents add OpenTelemetry instrumentation
- Orchestrator configures Docker Compose with Tempo + Grafana
- Verify traces visible in Grafana (S5 gate)

### 7. Phase 5 Execution
- All agents write tests
- Orchestrator runs full integration test suite
- Orchestrator writes root documentation

## Docker Compose Template

```yaml
services:
  core:
    build: ./src/backend/core
    ports: ["8000:8000"]
    environment:
      - OLLAMA_BASE_URL=http://ollama:11434
      - OTEL_EXPORTER_OTLP_ENDPOINT=http://tempo:4317
    depends_on: [ollama]

  api:
    build: ./src/backend/api
    ports: ["5000:5000"]
    environment:
      - CoreApi__BaseUrl=http://core:8000
      - OTEL_EXPORTER_OTLP_ENDPOINT=http://tempo:4317
    depends_on: [core]

  frontend:
    build: ./src/frontend/admin
    ports: ["3000:3000"]
    environment:
      - NEXT_PUBLIC_API_URL=http://api:5000
    depends_on: [api]

  ollama:
    image: ollama/ollama:latest
    ports: ["11434:11434"]
    volumes:
      - ollama_data:/root/.ollama

  tempo:
    image: grafana/tempo:latest
    ports: ["4317:4317", "3200:3200"]
    command: ["-config.file=/etc/tempo.yaml"]
    volumes:
      - ./docker/tempo.yaml:/etc/tempo.yaml

  grafana:
    image: grafana/grafana:latest
    ports: ["3001:3000"]
    environment:
      - GF_AUTH_ANONYMOUS_ENABLED=true
      - GF_AUTH_ANONYMOUS_ORG_ROLE=Admin
    volumes:
      - ./docker/grafana-datasources.yaml:/etc/grafana/provisioning/datasources/datasources.yaml

volumes:
  ollama_data:
```

## Inter-Agent Communication via Contracts

When an agent needs to publish a contract:
1. Agent writes the spec file to `docs/contracts/`
2. Orchestrator reads the file and validates it
3. Orchestrator signals consuming agents that the contract is available

When an agent needs to consume a contract:
1. Agent reads the spec from `docs/contracts/`
2. Agent generates types/clients from the spec
3. Agent implements against the contract

## Failure Handling
- If an agent fails a phase, the orchestrator re-launches it with error context
- If a sync point is not met, dependent agents continue on independent tasks
- If Core API spec is delayed, API agent works with the draft spec from Phase 0
