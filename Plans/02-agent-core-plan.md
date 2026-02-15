# Agent 1 - Backend Core (Python) Detailed Plan

## Identity
- **Agent Type:** `python-pro` or `backend-developer`
- **Scope:** `src/backend/core/`
- **Publishes:** `docs/contracts/core-api.openapi.yaml`
- **Consumes:** `docs/contracts/shared-models.md`

## Technology Stack
| Component | Technology | Version |
|-----------|-----------|---------|
| Language | Python | 3.12+ |
| Framework | FastAPI | Latest |
| LLM Orchestration | LangChain + LangGraph | Latest |
| Vector Store | FAISS (local) | Latest |
| Embeddings | Ollama | Latest |
| Persistence | SQLite + aiosqlite | Latest |
| Migrations | Alembic | Latest |
| Telemetry | opentelemetry-sdk | Latest |
| Testing | pytest + pytest-asyncio | Latest |
| Package Manager | uv | Latest |

## Deliverables by Phase

### Phase 1 - Scaffold
- [ ] `pyproject.toml` with all dependencies
- [ ] DDD folder structure under `app/`
- [ ] `app/main.py` with FastAPI app factory
- [ ] `GET /api/v1/health` returns `{"status": "healthy"}`
- [ ] `Dockerfile` (multi-stage, slim)
- [ ] `.env.example` with Core-specific vars
- [ ] Basic pytest setup with conftest

### Phase 2 - Domain & Core Logic
- [ ] **Domain Models** (pure Python, no framework imports):
  - `KnowledgeBase(id, name, description, created_at, updated_at)`
  - `Document(id, kb_id, filename, content_hash, status, chunks_count, uploaded_at)`
  - `Chunk(id, document_id, content, metadata, embedding_vector)`
  - `Interaction(id, kb_id, question, answer, status, citations, created_at)`
  - `Citation(source_document, page, chunk_id, relevance_score)`
  - `GroundingDecision(is_grounded, confidence, reasoning, supporting_chunks)`
  - `QueryResult(status, answer, citations, interaction_id)`
- [ ] **Domain Ports** (ABC interfaces):
  - `LLMPort`: `generate(prompt, context) -> str`, `embed(text) -> list[float]`
  - `VectorStorePort`: `store(chunks)`, `search(query_embedding, top_k) -> list[Chunk]`
  - `DocumentStorePort`: CRUD for KBs, Documents, Chunks
  - `InteractionStorePort`: CRUD for Interactions
- [ ] **Domain Services**:
  - `GroundingService.evaluate(question, answer, chunks) -> GroundingDecision`
- [ ] **Application Use Cases**:
  - `QueryUseCase.execute(kb_id, question) -> QueryResult`
  - `KnowledgeBaseUseCase`: create, list, get, delete
  - `DocumentUseCase`: upload, process, list, delete
  - `InteractionUseCase`: list, get_by_id
- [ ] **LLM Provider - Ollama Adapter**:
  - Implements `LLMPort`
  - Configurable model name, base URL
  - Strategy pattern base class for future Azure adapter
- [ ] **RAG Pipeline (LangGraph)**:
  - State: `{ question, kb_id, chunks, grounding_decision, answer, citations }`
  - Nodes: `retrieve` -> `ground` -> `generate` -> `format_response`
  - Conditional edge: if not grounded -> return UNKNOWN
- [ ] **FastAPI Routes** (all endpoints from contract)
- [ ] **Publish OpenAPI spec** to `docs/contracts/core-api.openapi.yaml`

### Phase 3 - Infrastructure Adapters
- [ ] **FAISS Vector Store Adapter** implements `VectorStorePort`
- [ ] **SQLite Persistence Adapter** implements `DocumentStorePort`, `InteractionStorePort`
- [ ] **Alembic migrations** for schema
- [ ] **Document Processing Pipeline**:
  - PDF loader (pdfplumber)
  - Text splitter (recursive character, 512 tokens, 50 overlap)
  - Embedding generator (via LLMPort)
- [ ] Integration tests with deterministic LLM stubs

### Phase 4 - Observability
- [ ] OpenTelemetry SDK setup in `app/infrastructure/telemetry/`
- [ ] OTLP exporter config (Tempo endpoint)
- [ ] Custom spans per RAG node with attributes:
  - `interaction.id`, `interaction.kb_id`
  - `retrieval.chunk_count`, `retrieval.top_score`
  - `grounding.is_grounded`, `grounding.confidence`
  - `generation.model`, `generation.provider`, `generation.tokens`
- [ ] Middleware: inject `interaction_id` into all response headers

### Phase 5 - Testing
- [ ] Unit tests: GroundingService, domain models, use cases
- [ ] Integration tests: full RAG pipeline with test KB
- [ ] Edge cases: empty KB query, no matches, malformed docs
- [ ] Tests runnable from root `tests/` directory

## Critical Constraints
1. **Domain layer MUST NOT import** LangChain, LangGraph, FastAPI, SQLAlchemy, or any infrastructure package
2. **All answers MUST cite sources** - if citations empty, return UNKNOWN
3. **JSON only** - all endpoints return structured Pydantic models
4. **Every interaction gets an `interaction_id`** (UUID) that flows through all telemetry spans
5. The standard unknown message is exactly: `"I don't have that information in the provided knowledge base."`

## API Endpoints Summary

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/health` | Health check |
| POST | `/api/v1/query` | Ask a question |
| POST | `/api/v1/knowledge-bases` | Create KB |
| GET | `/api/v1/knowledge-bases` | List KBs |
| GET | `/api/v1/knowledge-bases/{id}` | Get KB detail |
| DELETE | `/api/v1/knowledge-bases/{id}` | Delete KB |
| POST | `/api/v1/knowledge-bases/{id}/documents` | Upload document |
| GET | `/api/v1/knowledge-bases/{id}/documents` | List documents |
| DELETE | `/api/v1/knowledge-bases/{id}/documents/{doc_id}` | Delete document |
| POST | `/api/v1/knowledge-bases/{id}/index` | Trigger indexing |
| GET | `/api/v1/interactions` | List interactions |
| GET | `/api/v1/interactions/{id}` | Get interaction detail |
