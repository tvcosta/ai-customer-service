# Architecture

## System Overview

The AI Customer Service system is a three-service architecture that answers customer questions using a Retrieval-Augmented Generation (RAG) pipeline grounded strictly in Knowledge Base content. The system follows DDD (Domain-Driven Design) and Clean Architecture principles across all services.

### Design Principles

- **KB-Only Answers** -- The system never guesses. Every answer must be traceable to source documents.
- **Mandatory Citations** -- Every answered response includes citations with source document, page, and chunk ID.
- **Unknown When Unsupported** -- If the Knowledge Base does not contain the answer, the system returns `status: "unknown"` with the standard message: "I don't have that information in the provided knowledge base."
- **Full Audit Trail** -- Every interaction is traced end-to-end with OpenTelemetry, linked by a unique `interaction_id`.

## Service Boundaries

```
+-------------------+      +--------------------+      +---------------------+      +-----------------+
|                   |      |                    |      |                     |      |                 |
|  Frontend Admin   | ---> |   Backend API      | ---> |   Backend Core      | ---> |     Ollama      |
|  (Next.js :3000)  |      |  (.NET :5000)      |      |  (Python :8000)     |      |    (:11434)     |
|                   |      |                    |      |                     |      |                 |
+-------------------+      +--------------------+      +---------------------+      +-----------------+
```

### Backend Core (Python)

**Role:** The brain of the system. Owns all business logic, the RAG pipeline, LLM orchestration, and data persistence.

**Responsibilities:**
- Knowledge Base and document management (CRUD)
- Document processing: loading, chunking, and embedding
- Vector store management (FAISS)
- RAG pipeline execution via LangGraph
- Grounding verification (ensuring answers are supported by retrieved chunks)
- Citation generation
- Interaction auditing and persistence (SQLite)
- OpenTelemetry instrumentation for RAG pipeline spans

**Publishes:** `docs/contracts/core-api.openapi.yaml`
**Consumes:** `docs/contracts/shared-models.md`

### Backend API (.NET)

**Role:** Public-facing gateway. Validates requests, proxies to Backend Core, and returns responses. Contains no business logic.

**Responsibilities:**
- Request validation via FastEndpoints + FluentValidation
- HTTP proxying to Backend Core via typed `ICoreApiClient`
- Dashboard statistics aggregation
- CORS configuration for Frontend
- Health check that includes Core connectivity status
- OpenTelemetry instrumentation and W3C Trace Context propagation

**Publishes:** `docs/contracts/backend-api.openapi.yaml`
**Consumes:** `docs/contracts/core-api.openapi.yaml`, `docs/contracts/shared-models.md`

### Frontend Admin (Next.js)

**Role:** Admin dashboard for managing the system. Consumer-only; all data comes from Backend API.

**Responsibilities:**
- Dashboard with aggregated statistics
- Knowledge Base management (create, delete, view)
- Document management (upload, delete, trigger re-indexing)
- Playground for live Q&A testing
- Interaction history with search and filtering
- Display `interaction_id` for Grafana cross-referencing

**Publishes:** Nothing
**Consumes:** `docs/contracts/backend-api.openapi.yaml`, `docs/contracts/shared-models.md`

## DDD / Clean Architecture Layers

Each service follows the same layered architecture (adapted to its language and framework):

```
+-----------------------------------------------------+
|                  Interfaces Layer                    |
|  (REST endpoints, Pydantic schemas, FastEndpoints)  |
+-----------------------------------------------------+
|                  Application Layer                   |
|  (Use cases, orchestration, DTOs, port interfaces)  |
+-----------------------------------------------------+
|                    Domain Layer                      |
|  (Entities, value objects, domain services, ports)   |
|  PURE: no framework imports                          |
+-----------------------------------------------------+
|                Infrastructure Layer                  |
|  (LLM adapters, vector store, persistence, OTel)    |
+-----------------------------------------------------+
```

**Dependency rule:** Dependencies point inward. The Domain Layer has zero external framework imports. The Application Layer depends only on Domain. Infrastructure implements the port interfaces defined in Domain.

### Backend Core Layers in Detail

**Domain Layer** (`app/domain/`)
- Entities: `KnowledgeBase`, `Document`, `Interaction`
- Value Objects: `Chunk`, `Citation`, `GroundingDecision`
- Domain Services: `GroundingService` (validates answer against source chunks)
- Ports (abstract interfaces): `LLMPort`, `VectorStorePort`, `DocumentStorePort`, `InteractionStorePort`
- Pure Python only: dataclasses, enums, ABC, typing

**Application Layer** (`app/application/`)
- `QueryUseCase` -- orchestrates: retrieve, ground, answer, audit
- `KnowledgeBaseUseCase` -- CRUD for Knowledge Bases
- `DocumentUseCase` -- upload, process, chunk, index
- `InteractionUseCase` -- list and retrieve past interactions

**Infrastructure Layer** (`app/infrastructure/`)
- `OllamaProvider` -- LLM adapter implementing `LLMPort`
- `FaissAdapter` -- vector store implementing `VectorStorePort`
- `SqliteAdapter` -- persistence implementing `DocumentStorePort` and `InteractionStorePort`
- `RAGGraph` -- LangGraph pipeline implementation
- `TelemetrySetup` -- OpenTelemetry configuration

**Interfaces Layer** (`app/interfaces/`)
- FastAPI route handlers (thin: validate input, call use case, return response)
- Pydantic request/response schemas
- Error handling and tracing middleware

## RAG Pipeline

The RAG (Retrieval-Augmented Generation) pipeline is implemented as a LangGraph state machine in Backend Core. It processes every query through a strict sequence of steps to ensure answers are grounded in Knowledge Base content.

### Pipeline Flow

```
                         +------------------+
                         |                  |
                         |   Receive Query  |
                         |                  |
                         +--------+---------+
                                  |
                                  v
                         +------------------+
                         |                  |
                         | Embed Question   |
                         | (via LLM Port)   |
                         |                  |
                         +--------+---------+
                                  |
                                  v
                         +------------------+
                         |                  |
                         | Retrieve Chunks  |
                         | (Vector Store)   |
                         |                  |
                         +--------+---------+
                                  |
                                  v
                         +------------------+
                         |                  |
                         |  Ground Check    |
                         | (GroundingService|
                         |  + LLM verify)   |
                         |                  |
                         +-------+--+-------+
                                 |  |
                        grounded |  | not grounded
                                 |  |
                    +------------+  +-------------+
                    |                              |
                    v                              v
           +----------------+            +------------------+
           |                |            |                  |
           | Generate Answer|            |  Return UNKNOWN  |
           | (LLM + context)|            |  status with     |
           |                |            |  standard message|
           +-------+--------+            |                  |
                   |                     +------------------+
                   v
           +----------------+
           |                |
           | Format Response|
           | (add citations)|
           |                |
           +-------+--------+
                   |
                   v
           +----------------+
           |                |
           |  Audit & Store |
           | (interaction + |
           |  OTel spans)   |
           |                |
           +----------------+
```

### Pipeline State

```python
class RAGState(TypedDict):
    question: str
    kb_id: str
    chunks: list[Chunk]
    grounding_decision: GroundingDecision | None
    answer: str | None
    citations: list[Citation]
    interaction_id: str
```

### Grounding Logic

The `GroundingService` is a domain service that determines whether a generated answer is supported by the retrieved chunks. This is the core safety mechanism:

1. Retrieved chunks are passed alongside the generated answer to the LLM for verification.
2. The LLM evaluates whether the answer is fully supported by the provided context.
3. A `GroundingDecision` is produced with `is_grounded` (boolean), `confidence` (float), and `reasoning` (string).
4. If `is_grounded` is false, the pipeline short-circuits and returns `status: "unknown"`.
5. If `is_grounded` is true, the answer proceeds with mandatory citations attached.

This ensures the system never fabricates information beyond what exists in the Knowledge Base.

## Data Flow

### Query Request (end-to-end)

```
1. User enters question in Frontend Playground
          |
          v
2. Frontend sends POST /api/v1/query to Backend API
          |
          v
3. Backend API validates request (FastEndpoints + FluentValidation)
          |
          v
4. Backend API forwards to Backend Core POST /api/v1/query
          |
          v
5. Core generates interaction_id (UUIDv4)
          |
          v
6. Core executes RAG pipeline:
   a. Embed question via Ollama
   b. Retrieve top-k chunks from FAISS vector store
   c. Ground-check: verify answer is KB-supported
   d. If grounded: generate answer with citations
   e. If not grounded: return UNKNOWN status
          |
          v
7. Core persists Interaction record to SQLite
          |
          v
8. Core returns QueryResponse to Backend API
          |
          v
9. Backend API returns response to Frontend
          |
          v
10. Frontend displays answer, citations, status badge, and interaction_id
```

### Document Upload Flow

```
1. User uploads file in Frontend KB detail page
          |
          v
2. Frontend sends POST /api/v1/knowledge-bases/{id}/documents (multipart)
          |
          v
3. Backend API forwards to Backend Core
          |
          v
4. Core stores document, sets status to "pending"
          |
          v
5. Core processes document:
   a. Load content (PDF/text)
   b. Split into chunks with overlap
   c. Generate embeddings for each chunk via Ollama
   d. Store chunks in FAISS vector store
   e. Update document status to "indexed"
          |
          v
6. Document is now available for queries against this KB
```

## Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Backend Core | Python 3.12+, FastAPI | Internal API and business logic |
| RAG Orchestration | LangChain, LangGraph | Pipeline state machine |
| Vector Store | FAISS | Similarity search over document chunks |
| Database | SQLite (aiosqlite) | Persistence for KBs, documents, interactions |
| LLM Provider | Ollama (llama3.2) | Text generation and embeddings |
| Backend API | .NET 10, FastEndpoints | Public gateway with validation |
| HTTP Client | IHttpClientFactory | Typed HTTP communication to Core |
| Frontend | Next.js 15, React 19, TypeScript | Admin dashboard UI |
| UI Framework | Tailwind CSS, shadcn/ui | Styling and component library |
| Tracing | OpenTelemetry | Distributed tracing across services |
| Trace Backend | Grafana Tempo | Trace storage and querying |
| Visualization | Grafana | Trace exploration and dashboards |

## OpenTelemetry Instrumentation

All three services export traces via OTLP gRPC to Grafana Tempo. The `interaction_id` links spans across the entire request lifecycle.

### Trace Propagation

```
Frontend (displays interaction_id)
    |
    v
Backend API (AspNetCore + HttpClient instrumentation)
    | --- W3C Trace Context headers --->
    v
Backend Core (custom RAG pipeline spans)
```

W3C Trace Context headers are propagated automatically from the Backend API to Backend Core, creating a single distributed trace for each request.

### Core Pipeline Spans

Each RAG pipeline node creates a span with structured attributes:

| Span | Attributes |
|------|-----------|
| `retrieval` | `interaction.id`, `interaction.kb_id`, `retrieval.chunk_count`, `retrieval.top_score` |
| `grounding` | `interaction.id`, `grounding.is_grounded`, `grounding.confidence` |
| `generation` | `interaction.id`, `generation.model`, `generation.provider`, `generation.tokens` |

### API Instrumentation

The .NET Backend API uses the OpenTelemetry .NET SDK with:
- `AddAspNetCoreInstrumentation()` -- automatic spans for incoming HTTP requests
- `AddHttpClientInstrumentation()` -- automatic spans for outgoing calls to Core
- `AddOtlpExporter()` -- export to Tempo via gRPC

### Viewing Traces

1. Open Grafana at http://localhost:3001
2. Navigate to the Explore view and select the Tempo data source
3. Search by `interaction_id` or browse recent traces
4. The trace waterfall shows the full request lifecycle across Backend API and Backend Core

## Standard Response Envelope

All query responses conform to this schema:

```json
{
  "status": "answered | unknown | error",
  "answer": "string or null",
  "citations": [
    {
      "source_document": "filename.pdf",
      "page": 1,
      "chunk_id": "uuid",
      "relevance_score": 0.95
    }
  ],
  "interaction_id": "uuid"
}
```

**Invariants:**
- `status: "answered"` requires non-empty `citations` and non-null `answer`
- `status: "unknown"` requires `answer` to be the exact standard message and `citations` to be `[]`
- `status: "error"` requires non-null `error` field

Field names use `snake_case` in JSON payloads. All IDs are UUIDv4 strings. All timestamps are ISO 8601 UTC.
