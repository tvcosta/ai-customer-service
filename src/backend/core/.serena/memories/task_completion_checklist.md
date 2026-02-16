# Task Completion Checklist

When a task is completed, ensure:

## Python Core
1. All functions have type hints
2. Pydantic models for all DTOs
3. Domain layer has zero framework imports
4. `uv run python3 -c "from app.main import create_app; print('OK')"` passes
5. Tests pass: `uv run pytest`

## .NET API
1. Code compiles: `dotnet build src/backend/api/AiCustomerService.Api.slnx` (0 errors, 0 warnings)
2. Tests pass: `dotnet test src/backend/api/AiCustomerService.Api.slnx`
3. Records for DTOs, sealed classes where appropriate
4. All JSON uses `[JsonPropertyName("snake_case")]`

## Next.js Frontend
1. Build succeeds: `cd src/frontend/admin && pnpm build`
2. Lint passes: `cd src/frontend/admin && pnpm lint`
3. No `any` types
4. Server Components by default

## Cross-cutting
1. Shared contracts in `docs/contracts/` are respected
2. Standard response envelope used (status, answer, citations, interaction_id)
3. OpenTelemetry instrumentation present
