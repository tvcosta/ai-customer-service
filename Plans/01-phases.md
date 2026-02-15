# Execution Phases

## Phase 0 - Contracts & Shared Definitions (Orchestrator)

**Owner:** Orchestrator
**Duration:** First action before agents begin
**Output:** `docs/contracts/`

### Tasks
1. Create `docs/contracts/shared-models.md` defining:
   - Standard response envelope: `{ status, data, citations, interaction_id, error }`
   - `status` values: `"answered"`, `"unknown"`, `"error"`
   - Citation schema: `{ source_document, page, chunk_id, relevance_score }`
   - Interaction schema: `{ interaction_id, question, answer, status, citations, created_at }`
   - Knowledge Base schemas: `{ kb_id, name, documents[], created_at }`
   - Document schemas: `{ document_id, kb_id, filename, status, chunks_count, uploaded_at }`

2. Create initial `docs/contracts/core-api.openapi.yaml` (draft):
   - `POST /api/v1/query` - Ask a question against a KB
   - `POST /api/v1/knowledge-bases` - Create KB
   - `GET /api/v1/knowledge-bases` - List KBs
   - `POST /api/v1/knowledge-bases/{id}/documents` - Upload document
   - `GET /api/v1/knowledge-bases/{id}/documents` - List documents
   - `DELETE /api/v1/knowledge-bases/{id}/documents/{doc_id}` - Remove document
   - `POST /api/v1/knowledge-bases/{id}/index` - Trigger indexing
   - `GET /api/v1/interactions` - List past interactions
   - `GET /api/v1/interactions/{id}` - Get interaction detail
   - `GET /api/v1/health` - Health check

3. Create initial `docs/contracts/backend-api.openapi.yaml` (draft):
   - Same endpoints as Core but prefixed with `/api/v1/`
   - Adds: `GET /api/v1/dashboard/stats` (aggregated metrics)

4. Create root `docker-compose.yml` scaffold with services:
   - `core` (Python FastAPI)
   - `api` (.NET FastEndpoints)
   - `frontend` (Next.js)
   - `ollama` (LLM provider)
   - `grafana` + `tempo` (observability)

---

## Phase 1 - Project Scaffolding (Parallel)

**All 3 agents work independently**
**Sync Point: S1** - All projects build and run with health endpoints

### Agent 1 - Core (Python)
1. Initialize Python project with `pyproject.toml` (uv/poetry)
2. Create DDD folder structure:
   ```
   src/backend/core/
   ├── pyproject.toml
   ├── Dockerfile
   ├── app/
   │   ├── __init__.py
   │   ├── main.py              # FastAPI entry point
   │   ├── domain/
   │   │   ├── models/          # Entities & Value Objects
   │   │   ├── services/        # Domain services
   │   │   └── ports/           # Abstract interfaces (ABC)
   │   ├── application/
   │   │   ├── use_cases/       # Application services
   │   │   └── dto/             # Data transfer objects
   │   ├── infrastructure/
   │   │   ├── llm/             # LLM provider adapters
   │   │   ├── vectorstore/     # Vector store adapters
   │   │   ├── persistence/     # DB adapters
   │   │   ├── retrieval/       # LangChain/LangGraph implementation
   │   │   ├── document_processing/ # Loaders & chunkers
   │   │   └── telemetry/       # OpenTelemetry setup
   │   └── interfaces/
   │       └── api/
   │           ├── routes/      # FastAPI route handlers
   │           ├── schemas/     # Pydantic request/response schemas
   │           └── middleware/  # CORS, error handling, tracing
   └── tests/                   # Pytest tests (mirrored to root /tests too)
   ```
3. Implement health endpoint: `GET /api/v1/health`
4. Dockerfile builds and runs

### Agent 2 - API (.NET)
1. Create .NET 10 solution with FastEndpoints
2. Create DDD folder structure:
   ```
   src/backend/api/
   ├── AiCustomerService.Api.sln (or .slnx)
   ├── Dockerfile
   ├── src/
   │   └── AiCustomerService.Api/
   │       ├── Program.cs
   │       ├── AiCustomerService.Api.csproj
   │       ├── Domain/
   │       │   ├── Models/
   │       │   └── Interfaces/
   │       ├── Application/
   │       │   ├── Services/
   │       │   └── DTOs/
   │       ├── Infrastructure/
   │       │   ├── HttpClients/     # HttpClient to Core API
   │       │   └── Telemetry/       # OpenTelemetry setup
   │       └── Endpoints/           # FastEndpoints handlers
   │           ├── Query/
   │           ├── KnowledgeBases/
   │           ├── Interactions/
   │           └── Health/
   └── tests/
   ```
3. Implement health endpoint: `GET /api/v1/health`
4. Dockerfile builds and runs

### Agent 3 - Frontend (Next.js)
1. Create Next.js 15 project with App Router, TypeScript
2. Create folder structure:
   ```
   src/frontend/admin/
   ├── package.json
   ├── Dockerfile
   ├── next.config.ts
   ├── tailwind.config.ts
   ├── tsconfig.json
   ├── src/
   │   ├── app/
   │   │   ├── layout.tsx
   │   │   ├── page.tsx              # Dashboard
   │   │   ├── knowledge-bases/
   │   │   │   ├── page.tsx          # KB list
   │   │   │   └── [id]/page.tsx     # KB detail + doc management
   │   │   ├── interactions/
   │   │   │   ├── page.tsx          # Interaction history
   │   │   │   └── [id]/page.tsx     # Interaction detail
   │   │   └── playground/
   │   │       └── page.tsx          # Live Q&A testing
   │   ├── components/
   │   │   ├── ui/                   # Reusable UI primitives
   │   │   ├── layout/               # Shell, sidebar, header
   │   │   └── features/             # Feature-specific components
   │   ├── lib/
   │   │   ├── api/                  # API client functions
   │   │   └── types/                # TypeScript interfaces (from contract)
   │   └── hooks/                    # Custom React hooks
   └── tests/
   ```
3. Implement shell layout with sidebar navigation
4. Dockerfile builds and runs

**S1 Gate:** Orchestrator verifies all 3 services start and return 200 on `/api/v1/health` (or Next.js on `/`)

---

## Phase 2 - Domain & Core Logic (Core leads, others parallel)

**Agent 1 is primary; Agents 2 & 3 work on non-dependent tasks**
**Sync Point: S2** - Core OpenAPI spec finalized

### Agent 1 - Core
1. **Domain Layer:**
   - `KnowledgeBase` entity (id, name, created_at)
   - `Document` entity (id, kb_id, filename, status, content_hash)
   - `Chunk` value object (id, document_id, content, embedding, metadata)
   - `Interaction` entity (id, kb_id, question, answer, status, citations, created_at)
   - `Citation` value object (source_document, page, chunk_id, relevance_score)
   - `GroundingDecision` value object (is_grounded, confidence, reasoning)
   - Port interfaces: `LLMPort`, `VectorStorePort`, `DocumentStorePort`, `InteractionStorePort`
   - Domain service: `GroundingService` (validates answer is supported by retrieved chunks)

2. **Application Layer:**
   - `QueryUseCase` - orchestrates: retrieve → ground → answer → audit
   - `KnowledgeBaseUseCase` - CRUD for KBs
   - `DocumentUseCase` - upload, process, chunk, index
   - `InteractionUseCase` - list/get interactions

3. **Infrastructure - LLM Provider:**
   - `LLMProviderStrategy` (abstract)
   - `OllamaProvider` implementation
   - Configuration for model selection

4. **Infrastructure - RAG Pipeline (LangGraph):**
   - Retrieval node: query vector store
   - Grounding node: verify answer is KB-supported
   - Answer generation node: format response with citations
   - Graph compilation and execution

5. **FastAPI Endpoints (Internal API):**
   - Implement all endpoints from `docs/contracts/core-api.openapi.yaml`
   - Pydantic schemas matching shared models
   - **Publish final OpenAPI spec** to `docs/contracts/core-api.openapi.yaml`

### Agent 2 - API (independent work)
1. Domain models mirroring shared schemas (C# records/DTOs)
2. `ICoreApiClient` interface and typed HttpClient
3. Request/response validation with FastEndpoints validators
4. Error handling middleware (maps Core errors to API responses)

### Agent 3 - Frontend (independent work)
1. TypeScript type definitions from shared models
2. API client module with typed fetch wrappers
3. MSW (Mock Service Worker) setup for development mocking
4. Dashboard page with placeholder stats
5. Knowledge Base list page (mock data)
6. Interaction list page (mock data)

**S2 Gate:** `docs/contracts/core-api.openapi.yaml` is finalized and committed

---

## Phase 3 - Integration Wiring (Parallel with contracts)

**All agents work in parallel, consuming published contracts**
**Sync Points: S3, S4**

### Agent 1 - Core
1. **Vector Store Adapter:**
   - FAISS adapter (default local)
   - Abstract port for future Chroma/Pinecone
2. **Document Processing:**
   - PDF loader (PyPDF2/pdfplumber)
   - Text chunking with overlap
   - Embedding generation via LLM provider
3. **Persistence:**
   - SQLite adapter for interactions, KBs, documents
   - Alembic migrations
4. **Integration tests** with deterministic LLM stubs

### Agent 2 - API
1. **Implement all FastEndpoints** consuming Core API:
   - `POST /api/v1/query` → proxy to Core
   - `POST /api/v1/knowledge-bases` → proxy to Core
   - `GET /api/v1/knowledge-bases` → proxy to Core
   - Document upload (multipart) → forward to Core
   - Interaction listing → proxy to Core
   - Dashboard stats → aggregate from Core
2. **Publish Backend API OpenAPI spec** to `docs/contracts/backend-api.openapi.yaml`
3. **HttpClient integration** with Core's actual endpoints
4. Health check that verifies Core connectivity

### Agent 3 - Frontend
1. **Remove MSW mocks**, connect to real Backend API
2. **Knowledge Base Management:**
   - Create/delete KBs
   - Upload documents (drag & drop)
   - View document processing status
   - Trigger re-indexing
3. **Playground (Live Q&A):**
   - Question input
   - Answer display with citations
   - Status indicators (answered/unknown)
4. **Interaction History:**
   - List with search/filter
   - Detail view with full trace info

**S3 Gate:** `docs/contracts/backend-api.openapi.yaml` is finalized
**S4 Gate:** End-to-end: Frontend → API → Core → LLM round-trip works

---

## Phase 4 - Observability & Audit (Parallel)

**All agents instrument their layer**
**Sync Point: S5** - Traces visible in Grafana

### Agent 1 - Core
1. OpenTelemetry SDK setup with OTLP exporter
2. Custom spans for each RAG pipeline node:
   - `retrieval` span (chunk IDs, scores, duration)
   - `grounding` span (decision, confidence)
   - `generation` span (model, provider, token count)
3. `interaction_id` as trace attribute on all spans
4. Audit events: question received, retrieval results, grounding decision, answer generated

### Agent 2 - API
1. OpenTelemetry SDK setup (.NET) with OTLP exporter
2. HTTP request/response tracing
3. Propagate trace context to Core (W3C Trace Context headers)
4. Health check endpoint includes Core connectivity status

### Agent 3 - Frontend
1. Display `interaction_id` in UI for each query
2. Loading states and error boundaries
3. Accessibility pass (ARIA labels, keyboard navigation)

### Orchestrator
1. Configure `docker-compose.yml` with Tempo + Grafana
2. Grafana dashboard JSON for:
   - Interaction trace search by `interaction_id`
   - Response time distribution
   - Answer status breakdown (answered vs unknown)
3. Validate end-to-end traces in Grafana

**S5 Gate:** Submit a question via Frontend → see complete trace in Grafana

---

## Phase 5 - Testing & Polish (Parallel then converge)

### Agent 1 - Core
1. Unit tests: domain services, grounding logic
2. Integration tests: RAG pipeline with test KB
3. Edge cases: empty KB, no relevant chunks, malformed input

### Agent 2 - API
1. Unit tests: endpoint validators, error mapping
2. Integration tests: API → Core round-trip (TestContainers)
3. Edge cases: Core unavailable, timeout handling

### Agent 3 - Frontend
1. Component tests (Vitest + Testing Library)
2. E2E smoke test (Playwright)
3. Responsive design verification

### Orchestrator
1. Full-stack integration test in `tests/`
2. Root `README.md` with setup instructions
3. `docs/` architecture documentation
4. Final `docker-compose.yml` validation
5. `.env.example` with all required variables
