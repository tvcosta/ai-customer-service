# Agent 1 - Backend Core (Python)

## Role
You are the Backend Core agent. You own all business logic, the RAG pipeline, LLM orchestration, and the internal API.
You are the brain of the system. The .NET API is just a gateway that proxies to you.

## Scope
- **Your directory:** `src/backend/core/`
- **You publish:** `docs/contracts/core-api.openapi.yaml`
- **You consume:** `docs/contracts/shared-models.md`
- **Your plan:** `Plans/02-agent-core-plan.md`

## Tech Stack
- Python 3.12+, FastAPI, LangChain, LangGraph, FAISS, SQLite, OpenTelemetry
- Package manager: `uv`
- Testing: pytest + pytest-asyncio

## Project Structure
```
src/backend/core/
├── pyproject.toml
├── Dockerfile
├── alembic/                    # DB migrations
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app factory
│   ├── config.py               # Settings via pydantic-settings
│   ├── domain/
│   │   ├── models/             # Entities & Value Objects (PURE Python)
│   │   │   ├── knowledge_base.py
│   │   │   ├── document.py
│   │   │   ├── chunk.py
│   │   │   ├── interaction.py
│   │   │   ├── citation.py
│   │   │   └── grounding.py
│   │   ├── services/           # Domain services
│   │   │   └── grounding_service.py
│   │   └── ports/              # Abstract interfaces (ABC)
│   │       ├── llm_port.py
│   │       ├── vectorstore_port.py
│   │       ├── document_store_port.py
│   │       └── interaction_store_port.py
│   ├── application/
│   │   ├── use_cases/
│   │   │   ├── query_use_case.py
│   │   │   ├── knowledge_base_use_case.py
│   │   │   ├── document_use_case.py
│   │   │   └── interaction_use_case.py
│   │   └── dto/
│   │       └── ...
│   ├── infrastructure/
│   │   ├── llm/
│   │   │   ├── base.py         # LLMProviderStrategy (abstract)
│   │   │   └── ollama.py       # OllamaProvider
│   │   ├── vectorstore/
│   │   │   └── faiss_adapter.py
│   │   ├── persistence/
│   │   │   └── sqlite_adapter.py
│   │   ├── retrieval/
│   │   │   └── rag_graph.py    # LangGraph RAG pipeline
│   │   ├── document_processing/
│   │   │   ├── loader.py       # PDF/text loader
│   │   │   └── chunker.py      # Text splitter
│   │   └── telemetry/
│   │       └── setup.py        # OpenTelemetry configuration
│   └── interfaces/
│       └── api/
│           ├── routes/
│           │   ├── health.py
│           │   ├── query.py
│           │   ├── knowledge_bases.py
│           │   ├── documents.py
│           │   └── interactions.py
│           ├── schemas/        # Pydantic request/response models
│           │   └── ...
│           └── middleware/
│               ├── error_handler.py
│               └── tracing.py
└── tests/
```

## Architecture Rules

### Domain Layer (`app/domain/`)
- **ZERO framework imports** - no LangChain, no FastAPI, no SQLAlchemy, no OpenTelemetry
- Pure Python only: dataclasses, enums, ABC, typing
- Contains entities, value objects, domain services, and port interfaces
- This is the heart of the system - keep it clean

### Application Layer (`app/application/`)
- Orchestrates domain logic via port interfaces
- Use cases call ports, never infrastructure directly
- May import domain models but NOT infrastructure

### Infrastructure Layer (`app/infrastructure/`)
- Implements port interfaces (adapters)
- LangGraph RAG pipeline lives here
- LLM providers, vector stores, persistence all here
- OpenTelemetry instrumentation here

### Interfaces Layer (`app/interfaces/`)
- FastAPI routes and Pydantic schemas
- Thin layer: validate input, call use case, return response
- Error handling middleware

## Critical Business Rules
1. **KB-Only answers**: The RAG pipeline MUST only use retrieved chunks to generate answers
2. **Grounding check**: Every generated answer MUST be verified against source chunks before returning
3. **If not grounded → UNKNOWN**: If `GroundingService` says the answer isn't supported, return:
   ```json
   {"status": "unknown", "answer": "I don't have that information in the provided knowledge base.", "citations": [], "interaction_id": "..."}
   ```
4. **Citations required**: If `status == "answered"`, `citations` MUST be non-empty
5. **interaction_id on everything**: Generate UUID for every query, attach to all telemetry spans

## RAG Pipeline (LangGraph)
```
[Query] → [Retrieve Chunks] → [Ground Check] → [Generate Answer] → [Format Response]
                                     |
                                     ↓ (not grounded)
                               [Return UNKNOWN]
```

State schema:
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

## OpenTelemetry Spans
Each RAG node creates a span with these attributes:
- `interaction.id` - UUID for the entire interaction
- `interaction.kb_id` - which knowledge base
- `retrieval.chunk_count` - number of chunks retrieved
- `retrieval.top_score` - highest relevance score
- `grounding.is_grounded` - boolean
- `grounding.confidence` - float
- `generation.model` - model name
- `generation.provider` - "ollama" | "azure"
- `generation.tokens` - token count

## LLM Provider Strategy
```python
class LLMProviderStrategy(ABC):
    @abstractmethod
    async def generate(self, prompt: str, context: str) -> str: ...
    @abstractmethod
    async def embed(self, text: str) -> list[float]: ...
```
- Implement `OllamaProvider` now
- Azure adapter can be added later by implementing the same interface

## API Endpoints
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/health` | Health check |
| POST | `/api/v1/query` | Ask a question against a KB |
| POST | `/api/v1/knowledge-bases` | Create KB |
| GET | `/api/v1/knowledge-bases` | List KBs |
| GET | `/api/v1/knowledge-bases/{id}` | Get KB detail |
| DELETE | `/api/v1/knowledge-bases/{id}` | Delete KB |
| POST | `/api/v1/knowledge-bases/{id}/documents` | Upload document |
| GET | `/api/v1/knowledge-bases/{id}/documents` | List documents |
| DELETE | `/api/v1/knowledge-bases/{id}/documents/{doc_id}` | Delete document |
| POST | `/api/v1/knowledge-bases/{id}/index` | Trigger re-indexing |
| GET | `/api/v1/interactions` | List interactions |
| GET | `/api/v1/interactions/{id}` | Get interaction detail |

## Coding Standards
- Type hints on ALL functions and method signatures
- Pydantic models for all API schemas
- `async def` for all I/O-bound operations
- Use `from __future__ import annotations` for forward references
- Docstrings on public functions (Google style)
- No mutable default arguments
- Use `pathlib.Path` instead of string paths
