# Customer Service Automation System - Instructions

## 0) Goal
Build a **customer service automation system** that answers customer questions using **IMPORTANT the provided Knowledge Base documents**.

If the answer is not explicitly supported by the Knowledge Base, the system must respond with **UNKNOWN** and must not guess.

This solution must be built with:
- **Backend API** (Dotnet10) with **Fastendpoints**
- **Backend Core** (Python) using **LangChain + LangGraph**
- **Frontend Admin** using **Next.js**
- UI interacts with the core via **REST endpoints only**
- **Auditing via OpenTelemetry** so audits can be viewed in **Grafana**
- **DDD / Clean Architecture** structure for scalability and maintainability
- **LLM Provider Strategy Pattern** (use **Ollama** now, allow Azure later)
- **Centralized root documentation** in `/docs`
- **Centralized root tests** in `/tests` (multi-project, unit + integration, dockerized deps)

---

## 1) Non-Negotiable Rules (Hard Requirements)

### 1.1 Knowledge-Base Only
- The agent must answer using **only** content in the Knowledge Base.
- The agent must not use external knowledge, assumptions, or general advice.
- The agent must not “fill in the blanks.”

### 1.2 Unknown if Not Supported
If the Knowledge Base does not explicitly contain the answer:
- Return `status = "unknown"`
- Do not provide an answer beyond the standardized unknown message.

Standard unknown message (exact text):
> “I don’t have that information in the provided knowledge base.”

### 1.3 Citations Are Mandatory
If `status = "answered"`:
- `citations` must be non-empty
- citations must point to source document + page (if available) + chunk_id

If citations are missing → treat as invalid output → return UNKNOWN.

### 1.4 Strict JSON Output Only
All user-facing outputs from the backend must be valid JSON conforming to the response schema.  
No extra prose outside JSON.

### 1.5 Audit Every Interaction via OpenTelemetry
Every interaction must be audited via **OpenTelemetry traces** (Tempo/Grafana compatible):
- user question (preview by default)
- retrieval results (chunk IDs + scores)
- grounding decision
- final answer status and citations
- timings and model/provider info
- stable `interaction_id` that can be searched in Grafana

Audits must exist even when the answer is UNKNOWN.

---

## 2) Monorepo Layout (Mandatory)
All code must live under a top-level folder named `src/`.

At repo root there must also be:
- `docs/` for markdown documentation
- `tests/` for test projects

```
.
├── README.md
├── .env.example
├── docs/
├── tests/
└── src/
    ├── frontend/admin/ # Frontend Admin (Only communicates with the backend via the backend api)
    └── backend/
        ├── api/        # Backend API (Backend public api that exposes endpoints for the frontend Admin, and the point of communication with Backend Core)
        └── core/       # Backend Core (Core structure of the entire solution logic althow not exposed, it must have an internal API to expose the functionalities to the Backend Api - using FastApi)
```

---

## 3) Architecture (DDD / Clean Architecture)

### 3.1 Bounded Contexts
1) **Support Interaction**
- customer questions → answers
- owns: interactions, messages, responses, grounding decisions

2) **Knowledge Base**
- documents, chunking, indexing, retrieval config, versioning
- owns: KBs, documents, chunks, index versions

3) **Audit & Observability**
- OpenTelemetry spans/events/attributes that serve as audit trail
- owns: trace conventions, observability setup

4) **Evaluation**
- suites, cases, runs, results
- used to measure improvements across KB/index versions

### 3.2 Layering Rules
**Domain Layer** (pure business rules)
- Entities, value objects, domain services
- No LangChain/LangGraph imports
- No DB / HTTP code
- No OpenTelemetry SDK

**Application Layer** (use cases)
- Orchestrates domain logic and calls Ports (interfaces)
- No framework details

**Infrastructure Layer** (adapters)
- LangGraph implementation
- LLM provider adapters (Ollama/Azure)
- persistence adapters (SQLite/Postgres)
- vector store adapters (FAISS/Chroma/Pinecone)
- OpenTelemetry instrumentation and exporters
- document loaders/chunkers

**Interfaces Layer**
- REST API (FastAPI)
- CLI tools
