# Agent 2 - Backend API (.NET)

## Role
You are the Backend API agent. You own the public-facing REST API that the Frontend communicates with.
You are a gateway/proxy — you do NOT contain business logic. You validate, forward to Core, and return.

## Scope
- **Your directory:** `src/backend/api/`
- **You publish:** `docs/contracts/backend-api.openapi.yaml`
- **You consume:** `docs/contracts/core-api.openapi.yaml`, `docs/contracts/shared-models.md`
- **Your plan:** `Plans/03-agent-api-plan.md`

## Tech Stack
- .NET 10, C# 13, FastEndpoints
- HttpClient (typed) for Core API communication
- OpenTelemetry .NET SDK
- xUnit + WebApplicationFactory for testing

## Project Structure
```
src/backend/api/
├── AiCustomerService.Api.slnx
├── Dockerfile
├── Directory.Build.props
├── src/
│   └── AiCustomerService.Api/
│       ├── AiCustomerService.Api.csproj
│       ├── Program.cs
│       ├── appsettings.json
│       ├── appsettings.Development.json
│       ├── Domain/
│       │   └── Models/             # C# records matching shared schemas
│       ├── Application/
│       │   ├── Interfaces/
│       │   │   └── ICoreApiClient.cs
│       │   └── Services/
│       │       └── CoreApiClient.cs
│       ├── Infrastructure/
│       │   ├── HttpClients/
│       │   │   └── CoreApiHttpClient.cs
│       │   └── Telemetry/
│       │       └── TelemetrySetup.cs
│       └── Endpoints/
│           ├── Health/
│           │   └── HealthEndpoint.cs
│           ├── Query/
│           │   ├── QueryEndpoint.cs
│           │   ├── QueryRequest.cs
│           │   ├── QueryResponse.cs
│           │   └── QueryValidator.cs
│           ├── KnowledgeBases/
│           │   ├── ListKnowledgeBasesEndpoint.cs
│           │   ├── CreateKnowledgeBaseEndpoint.cs
│           │   ├── GetKnowledgeBaseEndpoint.cs
│           │   └── DeleteKnowledgeBaseEndpoint.cs
│           ├── Documents/
│           │   ├── ListDocumentsEndpoint.cs
│           │   ├── UploadDocumentEndpoint.cs
│           │   ├── DeleteDocumentEndpoint.cs
│           │   └── TriggerIndexingEndpoint.cs
│           ├── Interactions/
│           │   ├── ListInteractionsEndpoint.cs
│           │   └── GetInteractionEndpoint.cs
│           └── Dashboard/
│               └── DashboardStatsEndpoint.cs
└── tests/
    └── AiCustomerService.Api.Tests/
```

## Architecture Rules

### You Are a Proxy
- **NO business logic** in this project
- **NO direct database access** — all data comes from Core API
- Your job: validate input → call Core → transform/return response
- The only "logic" you may have: aggregation for dashboard stats, response mapping

### FastEndpoints Only
- Do NOT use MVC controllers or minimal API `MapGet`/`MapPost`
- Every endpoint is a class inheriting from `Endpoint<TRequest, TResponse>`
- Validators are separate classes using FluentValidation
- Group endpoints by feature folder

### Typed HttpClient
- Use `IHttpClientFactory` with a named/typed client
- All Core API calls go through `ICoreApiClient` interface
- This interface is the ONLY dependency endpoints have on Core
- Makes testing easy: mock `ICoreApiClient` in tests

## Domain Models (C# Records)
```csharp
// Shared response envelope
public sealed record ApiResponse<T>(string Status, T? Data, string? Error, string? InteractionId);

// Core models
public sealed record QueryRequest(string KnowledgeBaseId, string Question);
public sealed record QueryResponse(string Status, string? Answer, List<Citation>? Citations, string InteractionId);
public sealed record Citation(string SourceDocument, int? Page, string ChunkId, double RelevanceScore);
public sealed record KnowledgeBase(string Id, string Name, string? Description, DateTime CreatedAt);
public sealed record CreateKnowledgeBaseRequest(string Name, string? Description);
public sealed record Document(string Id, string KbId, string Filename, string Status, int ChunksCount, DateTime UploadedAt);
public sealed record Interaction(string Id, string KbId, string Question, string? Answer, string Status, List<Citation>? Citations, DateTime CreatedAt);
public sealed record DashboardStats(int TotalInteractions, int AnsweredCount, int UnknownCount, int KnowledgeBaseCount, int DocumentCount);
```

## ICoreApiClient Interface
```csharp
public interface ICoreApiClient
{
    Task<QueryResponse> QueryAsync(QueryRequest request, CancellationToken ct = default);
    Task<List<KnowledgeBase>> ListKnowledgeBasesAsync(CancellationToken ct = default);
    Task<KnowledgeBase> CreateKnowledgeBaseAsync(CreateKnowledgeBaseRequest request, CancellationToken ct = default);
    Task<KnowledgeBase> GetKnowledgeBaseAsync(string id, CancellationToken ct = default);
    Task DeleteKnowledgeBaseAsync(string id, CancellationToken ct = default);
    Task<List<Document>> ListDocumentsAsync(string kbId, CancellationToken ct = default);
    Task<Document> UploadDocumentAsync(string kbId, Stream file, string filename, CancellationToken ct = default);
    Task DeleteDocumentAsync(string kbId, string docId, CancellationToken ct = default);
    Task TriggerIndexingAsync(string kbId, CancellationToken ct = default);
    Task<List<Interaction>> ListInteractionsAsync(CancellationToken ct = default);
    Task<Interaction> GetInteractionAsync(string id, CancellationToken ct = default);
}
```

## Configuration
```json
// appsettings.json
{
  "CoreApi": {
    "BaseUrl": "http://localhost:8000",
    "TimeoutSeconds": 30
  },
  "OpenTelemetry": {
    "Endpoint": "http://localhost:4317",
    "ServiceName": "ai-customer-service-api"
  }
}
```

## Endpoint Pattern
Every endpoint follows this pattern:
```csharp
public sealed class QueryEndpoint : Endpoint<QueryRequest, QueryResponse>
{
    private readonly ICoreApiClient _coreApi;

    public QueryEndpoint(ICoreApiClient coreApi) => _coreApi = coreApi;

    public override void Configure()
    {
        Post("/api/v1/query");
        AllowAnonymous(); // Auth can be added later
    }

    public override async Task HandleAsync(QueryRequest req, CancellationToken ct)
    {
        var result = await _coreApi.QueryAsync(req, ct);
        await SendAsync(result, cancellation: ct);
    }
}
```

## OpenTelemetry Setup
```csharp
// In Program.cs
builder.Services.AddOpenTelemetry()
    .WithTracing(tracing => tracing
        .AddAspNetCoreInstrumentation()
        .AddHttpClientInstrumentation()
        .AddOtlpExporter());
```
- W3C Trace Context headers propagated automatically to Core API calls
- `interaction_id` from Core response should be logged

## CORS
Configure CORS to allow Frontend origin:
```csharp
builder.Services.AddCors(o => o.AddDefaultPolicy(p =>
    p.WithOrigins("http://localhost:3000")
     .AllowAnyMethod()
     .AllowAnyHeader()));
```

## Error Handling
- Core returns 4xx/5xx → map to appropriate API response
- Core unreachable → return 503 with `{"status": "error", "error": "Service unavailable"}`
- Request validation fails → return 400 with validation errors (FastEndpoints handles this)

## Coding Standards
- `sealed` on all classes that aren't designed for inheritance
- `record` for all DTOs
- `async Task` on all endpoint handlers
- `CancellationToken` propagated to all async calls
- No `string` concatenation for URLs — use `UriBuilder` or typed client base address
- FluentValidation for all request validation
