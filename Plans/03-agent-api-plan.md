# Agent 2 - Backend API (.NET) Detailed Plan

## Identity
- **Agent Type:** `csharp-developer` or `backend-developer`
- **Scope:** `src/backend/api/`
- **Publishes:** `docs/contracts/backend-api.openapi.yaml`
- **Consumes:** `docs/contracts/core-api.openapi.yaml`, `docs/contracts/shared-models.md`

## Technology Stack
| Component | Technology | Version |
|-----------|-----------|---------|
| Runtime | .NET | 10 |
| Framework | FastEndpoints | Latest |
| HTTP Client | IHttpClientFactory + typed clients | Built-in |
| Telemetry | OpenTelemetry .NET SDK | Latest |
| Testing | xUnit + WebApplicationFactory | Latest |
| Build | dotnet CLI | Latest |

## Deliverables by Phase

### Phase 1 - Scaffold
- [ ] `AiCustomerService.Api.slnx` solution
- [ ] `AiCustomerService.Api.csproj` with FastEndpoints, OpenTelemetry packages
- [ ] `Program.cs` with minimal API + FastEndpoints registration
- [ ] `GET /api/v1/health` endpoint returns `{"status": "healthy"}`
- [ ] `Dockerfile` (multi-stage, SDK → runtime)
- [ ] `appsettings.json` + `appsettings.Development.json`
- [ ] `Directory.Build.props` for common settings

### Phase 2 - Domain & Integration Foundation
- [ ] **Domain Models** (C# records):
  ```csharp
  record QueryRequest(string KnowledgeBaseId, string Question);
  record QueryResponse(string Status, string? Answer, List<Citation>? Citations, string InteractionId);
  record Citation(string SourceDocument, int? Page, string ChunkId, double RelevanceScore);
  record KnowledgeBase(string Id, string Name, string? Description, DateTime CreatedAt);
  record Document(string Id, string KbId, string Filename, string Status, int ChunksCount, DateTime UploadedAt);
  record Interaction(string Id, string KbId, string Question, string? Answer, string Status, List<Citation>? Citations, DateTime CreatedAt);
  record DashboardStats(int TotalInteractions, int AnsweredCount, int UnknownCount, int KnowledgeBaseCount, int DocumentCount);
  ```
- [ ] **ICoreApiClient interface**:
  ```csharp
  interface ICoreApiClient {
      Task<QueryResponse> QueryAsync(QueryRequest request, CancellationToken ct);
      Task<List<KnowledgeBase>> ListKnowledgeBasesAsync(CancellationToken ct);
      Task<KnowledgeBase> CreateKnowledgeBaseAsync(CreateKbRequest request, CancellationToken ct);
      Task DeleteKnowledgeBaseAsync(string id, CancellationToken ct);
      Task<List<Document>> ListDocumentsAsync(string kbId, CancellationToken ct);
      Task<Document> UploadDocumentAsync(string kbId, Stream file, string filename, CancellationToken ct);
      Task DeleteDocumentAsync(string kbId, string docId, CancellationToken ct);
      Task TriggerIndexingAsync(string kbId, CancellationToken ct);
      Task<List<Interaction>> ListInteractionsAsync(CancellationToken ct);
      Task<Interaction> GetInteractionAsync(string id, CancellationToken ct);
  }
  ```
- [ ] **CoreApiClient implementation** using `HttpClient`
- [ ] **FastEndpoints validators** for request models
- [ ] **Error handling middleware**:
  - Maps Core API errors to appropriate HTTP status codes
  - Wraps errors in standard response envelope
  - Logs errors via structured logging

### Phase 3 - Full Endpoint Implementation
- [ ] **Query Endpoint** (`POST /api/v1/query`):
  - Validates request
  - Forwards to Core
  - Returns response with `interaction_id`
- [ ] **Knowledge Base Endpoints**:
  - `POST /api/v1/knowledge-bases` - create
  - `GET /api/v1/knowledge-bases` - list
  - `GET /api/v1/knowledge-bases/{id}` - detail
  - `DELETE /api/v1/knowledge-bases/{id}` - delete
- [ ] **Document Endpoints**:
  - `POST /api/v1/knowledge-bases/{id}/documents` - upload (multipart)
  - `GET /api/v1/knowledge-bases/{id}/documents` - list
  - `DELETE /api/v1/knowledge-bases/{id}/documents/{docId}` - delete
  - `POST /api/v1/knowledge-bases/{id}/index` - trigger indexing
- [ ] **Interaction Endpoints**:
  - `GET /api/v1/interactions` - list (with pagination, search)
  - `GET /api/v1/interactions/{id}` - detail
- [ ] **Dashboard Endpoint**:
  - `GET /api/v1/dashboard/stats` - aggregate from Core data
- [ ] **Publish OpenAPI spec** to `docs/contracts/backend-api.openapi.yaml`
- [ ] **CORS configuration** for Frontend origin

### Phase 4 - Observability
- [ ] OpenTelemetry setup in `Program.cs`:
  - `AddHttpClientInstrumentation()`
  - `AddAspNetCoreInstrumentation()`
  - OTLP exporter to Tempo
- [ ] W3C Trace Context propagation to Core API calls
- [ ] Custom activity source for business spans
- [ ] Health check that pings Core API health endpoint

### Phase 5 - Testing
- [ ] Unit tests for validators and DTOs
- [ ] Integration tests using `WebApplicationFactory` + mocked `ICoreApiClient`
- [ ] Integration tests with real Core (via TestContainers/Docker)
- [ ] Edge cases: Core unreachable, timeout, malformed responses

## Critical Constraints
1. **Proxy-first architecture** - API does NOT contain business logic; it delegates to Core
2. **All responses must conform** to the standard JSON envelope from shared models
3. **Trace context propagation** is mandatory - every request to Core must include W3C headers
4. **No direct database access** - all data comes from Core API
5. **FastEndpoints only** - do not use minimal API or MVC controllers

## Endpoint Summary

| Method | Path | Proxies To |
|--------|------|-----------|
| GET | `/api/v1/health` | Local + Core health |
| POST | `/api/v1/query` | Core `POST /api/v1/query` |
| POST | `/api/v1/knowledge-bases` | Core `POST /api/v1/knowledge-bases` |
| GET | `/api/v1/knowledge-bases` | Core `GET /api/v1/knowledge-bases` |
| GET | `/api/v1/knowledge-bases/{id}` | Core `GET /api/v1/knowledge-bases/{id}` |
| DELETE | `/api/v1/knowledge-bases/{id}` | Core `DELETE /api/v1/knowledge-bases/{id}` |
| POST | `/api/v1/knowledge-bases/{id}/documents` | Core `POST /api/v1/knowledge-bases/{id}/documents` |
| GET | `/api/v1/knowledge-bases/{id}/documents` | Core `GET /api/v1/knowledge-bases/{id}/documents` |
| DELETE | `/api/v1/knowledge-bases/{id}/documents/{docId}` | Core document delete |
| POST | `/api/v1/knowledge-bases/{id}/index` | Core indexing trigger |
| GET | `/api/v1/interactions` | Core `GET /api/v1/interactions` |
| GET | `/api/v1/interactions/{id}` | Core `GET /api/v1/interactions/{id}` |
| GET | `/api/v1/dashboard/stats` | Aggregated from Core |
