# AI Customer Service - Frontend Admin

Admin dashboard for the AI Customer Service system built with Next.js 15.

## Tech Stack

- **Framework**: Next.js 15 (App Router) + React 19
- **Language**: TypeScript 5.7+ (strict mode)
- **Styling**: Tailwind CSS 3.4
- **Icons**: Lucide React
- **Package Manager**: pnpm

## Project Structure

```
src/
├── app/                          # Next.js App Router pages
│   ├── layout.tsx                # Root layout
│   ├── page.tsx                  # Dashboard
│   ├── knowledge-bases/          # KB management
│   ├── interactions/             # Interaction history
│   └── playground/               # Live testing (client component)
├── components/
│   └── layout/                   # Shell, Sidebar, Header
├── lib/
│   ├── api/                      # API client
│   ├── types/                    # TypeScript interfaces
│   └── utils.ts                  # Utilities (cn helper)
└── hooks/                        # Custom React hooks (future)
```

## Getting Started

### Prerequisites

- Node.js 22+
- pnpm 9+

### Installation

```bash
# Install dependencies
pnpm install

# Run development server with Turbopack
pnpm dev

# Build for production
pnpm build

# Start production server
pnpm start

# Run linter
pnpm lint
```

The app will be available at [http://localhost:3000](http://localhost:3000).

## Environment Variables

Create a `.env.local` file:

```env
NEXT_PUBLIC_API_URL=http://localhost:5000
```

## Pages

- **Dashboard** (`/`) - Overview with stats and recent interactions
- **Knowledge Bases** (`/knowledge-bases`) - Manage KB collections and documents
- **Interactions** (`/interactions`) - View query history with full audit trail
- **Playground** (`/playground`) - Test queries in real-time

## Docker

Build and run with Docker:

```bash
# Build image
docker build -t ai-customer-service-admin .

# Run container
docker run -p 3000:3000 -e NEXT_PUBLIC_API_URL=http://backend-api:5000 ai-customer-service-admin
```

## Architecture

- **Server Components by default** - Optimal performance and SEO
- **Client Components** (`"use client"`) - Only for interactive features
- **API Client** - Typed wrapper around Backend API
- **Strict TypeScript** - No `any` types allowed
- **Tailwind CSS** - Utility-first styling

## API Integration

All API calls go through the Backend API (`/api/v1/*`), never directly to Backend Core.

See `docs/contracts/backend-api.openapi.yaml` for the complete API specification.

## Coding Standards

- TypeScript strict mode enabled
- Server Components by default
- Client Components only when necessary
- Tailwind utility classes preferred
- Descriptive naming conventions
- Co-locate related components

## Development Notes

- Uses Next.js 15 `output: 'standalone'` for optimized Docker builds
- Turbopack enabled for fast development builds
- React 19 with automatic batching and transitions
- Strict TypeScript configuration with path aliases (`@/*`)
