# Suggested Commands

## Python Core (src/backend/core/)
```bash
# Install dependencies
cd src/backend/core && uv sync

# Run the app
cd src/backend/core && uv run uvicorn app.main:create_app --factory --host 0.0.0.0 --port 8000

# Run tests
cd src/backend/core && uv run pytest

# Lint / format
cd src/backend/core && uv run ruff check . && uv run ruff format .

# Verify imports work
cd src/backend/core && uv run python3 -c "from app.main import create_app; print('OK')"
```

## .NET API (src/backend/api/)
```bash
# Build
dotnet build src/backend/api/AiCustomerService.Api.slnx

# Run the app
dotnet run --project src/backend/api/src/AiCustomerService.Api

# Run tests
dotnet test src/backend/api/AiCustomerService.Api.slnx

# Restore packages
dotnet restore src/backend/api/AiCustomerService.Api.slnx
```

## Next.js Frontend (src/frontend/admin/)
```bash
# Install dependencies
cd src/frontend/admin && pnpm install

# Run dev server
cd src/frontend/admin && pnpm dev

# Build
cd src/frontend/admin && pnpm build

# Lint
cd src/frontend/admin && pnpm lint
```

## Docker (full stack)
```bash
# Start all services
docker compose up -d

# Start specific service
docker compose up -d core api frontend

# View logs
docker compose logs -f core
```

## Git
```bash
git status
git diff
git log --oneline -10
```
