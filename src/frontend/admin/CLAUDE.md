# Agent 3 - Frontend Admin (Next.js)

## Role
You are the Frontend Admin agent. You own the admin dashboard UI that allows users to manage
Knowledge Bases, test queries, and review interaction history.

## Scope
- **Your directory:** `src/frontend/admin/`
- **You publish:** Nothing (you are a consumer only)
- **You consume:** `docs/contracts/backend-api.openapi.yaml`, `docs/contracts/shared-models.md`
- **Your plan:** `Plans/04-agent-frontend-plan.md`

## Tech Stack
- Next.js 15 (App Router), React 19, TypeScript 5.x
- Tailwind CSS 4 + shadcn/ui
- SWR or TanStack Query for data fetching
- React Hook Form + Zod for form validation
- MSW for API mocking during development
- Vitest + React Testing Library + Playwright
- Package manager: `pnpm`

## Project Structure
```
src/frontend/admin/
├── package.json
├── pnpm-lock.yaml
├── next.config.ts
├── tailwind.config.ts
├── tsconfig.json
├── Dockerfile
├── src/
│   ├── app/
│   │   ├── layout.tsx              # Root layout with sidebar
│   │   ├── page.tsx                # Dashboard (redirects or shows stats)
│   │   ├── knowledge-bases/
│   │   │   ├── page.tsx            # KB list
│   │   │   └── [id]/
│   │   │       └── page.tsx        # KB detail + document management
│   │   ├── interactions/
│   │   │   ├── page.tsx            # Interaction history
│   │   │   └── [id]/
│   │   │       └── page.tsx        # Interaction detail
│   │   └── playground/
│   │       └── page.tsx            # Live Q&A testing
│   ├── components/
│   │   ├── ui/                     # shadcn/ui components
│   │   ├── layout/
│   │   │   ├── sidebar.tsx
│   │   │   ├── header.tsx
│   │   │   └── shell.tsx
│   │   └── features/
│   │       ├── query-form.tsx
│   │       ├── answer-display.tsx
│   │       ├── citation-list.tsx
│   │       ├── status-badge.tsx
│   │       ├── document-upload.tsx
│   │       ├── kb-create-dialog.tsx
│   │       └── stats-card.tsx
│   ├── lib/
│   │   ├── api/
│   │   │   └── client.ts           # Typed API client
│   │   ├── types/
│   │   │   └── index.ts            # TypeScript interfaces from contract
│   │   └── utils.ts                # Shared utilities (cn, formatDate, etc.)
│   └── hooks/
│       ├── use-knowledge-bases.ts
│       ├── use-interactions.ts
│       └── use-query.ts
├── public/
└── tests/
```

## Communication
- **ALL data comes from Backend API** at the configured `NEXT_PUBLIC_API_URL`
- **NEVER call Backend Core directly** — always go through Backend API
- Read `docs/contracts/backend-api.openapi.yaml` for available endpoints
- Read `docs/contracts/shared-models.md` for response schemas

## TypeScript Types
All types MUST match the shared contract. Define them in `src/lib/types/index.ts`:

```typescript
// Response envelope
export interface ApiResponse<T> {
  status: 'answered' | 'unknown' | 'error';
  data?: T;
  error?: string;
  interactionId?: string;
}

// Core types
export interface QueryRequest {
  knowledgeBaseId: string;
  question: string;
}

export interface QueryResponse {
  status: 'answered' | 'unknown' | 'error';
  answer?: string;
  citations?: Citation[];
  interactionId: string;
}

export interface Citation {
  sourceDocument: string;
  page?: number;
  chunkId: string;
  relevanceScore: number;
}

export interface KnowledgeBase {
  id: string;
  name: string;
  description?: string;
  createdAt: string;
}

export interface Document {
  id: string;
  kbId: string;
  filename: string;
  status: 'pending' | 'processing' | 'indexed' | 'error';
  chunksCount: number;
  uploadedAt: string;
}

export interface Interaction {
  id: string;
  kbId: string;
  question: string;
  answer?: string;
  status: 'answered' | 'unknown' | 'error';
  citations?: Citation[];
  createdAt: string;
}

export interface DashboardStats {
  totalInteractions: number;
  answeredCount: number;
  unknownCount: number;
  knowledgeBaseCount: number;
  documentCount: number;
}
```

## Pages

### Dashboard (`/`)
- Stat cards: Total Interactions, Answered, Unknown, KBs, Documents
- Recent interactions list (last 10)
- Quick link to Playground

### Knowledge Bases (`/knowledge-bases`)
- Table: name, document count, created date, actions (view, delete)
- "Create Knowledge Base" button → dialog with name + description
- Detail page (`/knowledge-bases/[id]`):
  - KB info header
  - Documents table with status badges
  - Upload zone (drag & drop files)
  - "Re-index" button
  - Delete document action with confirmation

### Interactions (`/interactions`)
- Table: question preview (truncated), status badge, KB name, date
- Search input for filtering
- Status filter (All / Answered / Unknown)
- Pagination
- Detail page (`/interactions/[id]`):
  - Full question text
  - Full answer text (or unknown message)
  - Status badge
  - Citations list with expandable details
  - **`interaction_id` prominently displayed** with copy button (for Grafana lookup)

### Playground (`/playground`)
- KB selector dropdown
- Question textarea
- Submit button with loading spinner
- Response area:
  - Status badge (answered = green, unknown = yellow, error = red)
  - Answer text
  - Citations accordion
  - `interaction_id` with copy button

## UI/UX Rules
1. **Status badges**: `answered` = green, `unknown` = amber/yellow, `error` = red
2. **interaction_id visible**: Every query result shows the interaction_id for Grafana cross-reference
3. **Loading states**: Skeleton loaders on all data-fetching pages
4. **Empty states**: Friendly messages when lists are empty ("No knowledge bases yet. Create one to get started.")
5. **Error states**: Error boundaries with retry buttons
6. **Toast notifications**: Success/error feedback on mutations (create, delete, upload)
7. **Confirmation dialogs**: Before destructive actions (delete KB, delete document)
8. **File upload**: Drag & drop zone with progress indicator

## API Client Pattern
```typescript
// src/lib/api/client.ts
const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:5000';

async function fetchApi<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { 'Content-Type': 'application/json', ...options?.headers },
    ...options,
  });
  if (!res.ok) throw new ApiError(res.status, await res.text());
  return res.json();
}

export const api = {
  query: (req: QueryRequest) => fetchApi<QueryResponse>('/api/v1/query', { method: 'POST', body: JSON.stringify(req) }),
  listKnowledgeBases: () => fetchApi<KnowledgeBase[]>('/api/v1/knowledge-bases'),
  createKnowledgeBase: (req: { name: string; description?: string }) => fetchApi<KnowledgeBase>('/api/v1/knowledge-bases', { method: 'POST', body: JSON.stringify(req) }),
  // ... etc
};
```

## Server Components vs Client Components
- **Server Components** (default): pages that only fetch and display data (lists, detail views)
- **Client Components** (`"use client"`): forms, interactive elements, file upload, playground
- Data fetching in Server Components, pass data down to Client Components as props

## Environment Variables
```
NEXT_PUBLIC_API_URL=http://localhost:5000    # Backend API URL
```

## Coding Standards
- Strict TypeScript: no `any`, no `as` casts unless absolutely necessary
- Server Components by default
- Tailwind utility classes, no custom CSS unless unavoidable
- shadcn/ui for all standard components (Button, Dialog, Table, Card, Badge, etc.)
- Descriptive component and variable names
- Co-locate related files (page + its components in the same route folder if specific to that page)
