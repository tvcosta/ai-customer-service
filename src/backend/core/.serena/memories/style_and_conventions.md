# Code Style and Conventions

## Python (Backend Core)
- Python 3.12+, type hints on all functions
- Pydantic for all DTOs and API schemas
- async/await for all I/O operations
- Domain layer: zero framework imports
- `uv` for package management
- snake_case for variables, functions, modules
- PascalCase for classes

## C# (Backend API)
- .NET 10, C# 13
- FastEndpoints only (no MVC controllers, no minimal API)
- Records for DTOs, sealed classes
- IHttpClientFactory for all outbound HTTP
- Async all the way down
- PascalCase for public members
- `[JsonPropertyName("snake_case")]` for JSON serialization (snake_case wire format)
- TreatWarningsAsErrors enabled

## TypeScript (Frontend)
- Next.js 15 App Router, React 19
- Server Components by default, `"use client"` only when needed
- No `any` types - everything strictly typed
- Tailwind CSS for styling
- `pnpm` for package management
- camelCase for variables/functions, PascalCase for types/components

## Cross-cutting
- JSON field naming: snake_case on the wire
- Composition over inheritance
- Structured logging, not string concatenation
- No over-engineering or premature abstraction
