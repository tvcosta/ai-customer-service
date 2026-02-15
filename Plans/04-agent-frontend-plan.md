# Agent 3 - Frontend Admin (Next.js) Detailed Plan

## Identity
- **Agent Type:** `nextjs-developer` or `fullstack-developer`
- **Scope:** `src/frontend/admin/`
- **Publishes:** Nothing (consumer only)
- **Consumes:** `docs/contracts/backend-api.openapi.yaml`, `docs/contracts/shared-models.md`

## Technology Stack
| Component | Technology | Version |
|-----------|-----------|---------|
| Framework | Next.js (App Router) | 15 |
| Language | TypeScript | 5.x |
| Styling | Tailwind CSS | 4 |
| UI Components | shadcn/ui | Latest |
| State | React Server Components + SWR/TanStack Query | Latest |
| Forms | React Hook Form + Zod | Latest |
| Mocking | MSW (Mock Service Worker) | Latest |
| Testing | Vitest + React Testing Library + Playwright | Latest |
| Package Manager | pnpm | Latest |

## Deliverables by Phase

### Phase 1 - Scaffold
- [ ] `pnpm create next-app` with App Router, TypeScript, Tailwind
- [ ] Install shadcn/ui, configure theme
- [ ] App shell layout:
  - Sidebar navigation (Dashboard, Knowledge Bases, Interactions, Playground)
  - Header with title
  - Main content area
- [ ] Root page (`/`) redirects to Dashboard
- [ ] `Dockerfile` (multi-stage, deps → build → runtime)
- [ ] `next.config.ts` with API proxy rewrites to Backend API
- [ ] Basic ESLint + Prettier config

### Phase 2 - Types, API Client & Mock Data
- [ ] **TypeScript Types** (from `docs/contracts/shared-models.md`):
  ```typescript
  interface QueryRequest { knowledgeBaseId: string; question: string; }
  interface QueryResponse { status: 'answered' | 'unknown' | 'error'; answer?: string; citations?: Citation[]; interactionId: string; }
  interface Citation { sourceDocument: string; page?: number; chunkId: string; relevanceScore: number; }
  interface KnowledgeBase { id: string; name: string; description?: string; createdAt: string; }
  interface Document { id: string; kbId: string; filename: string; status: string; chunksCount: number; uploadedAt: string; }
  interface Interaction { id: string; kbId: string; question: string; answer?: string; status: string; citations?: Citation[]; createdAt: string; }
  interface DashboardStats { totalInteractions: number; answeredCount: number; unknownCount: number; knowledgeBaseCount: number; documentCount: number; }
  ```
- [ ] **API Client** (`src/lib/api/client.ts`):
  - Typed fetch wrapper with error handling
  - Base URL from environment variable
  - Functions: `queryKnowledgeBase()`, `listKnowledgeBases()`, `createKnowledgeBase()`, etc.
- [ ] **MSW Setup** for development:
  - Mock handlers for all endpoints
  - Realistic mock data
  - Toggle via environment variable
- [ ] **Pages with mock data**:
  - Dashboard with stat cards
  - Knowledge Base list (table with create/delete actions)
  - Interaction list (table with search)

### Phase 3 - Full Feature Implementation
- [ ] **Dashboard** (`/`):
  - Stats cards: Total Interactions, Answered, Unknown, KBs, Documents
  - Recent interactions list
  - Quick query shortcut
- [ ] **Knowledge Base Management** (`/knowledge-bases`):
  - List page: table with name, doc count, created date, actions
  - Create dialog: name + description form
  - Detail page (`/knowledge-bases/[id]`):
    - KB metadata
    - Documents table
    - Upload document (drag & drop zone)
    - Delete document with confirmation
    - "Re-index" button with status indicator
- [ ] **Interaction History** (`/interactions`):
  - List page: table with question preview, status badge, date
  - Search/filter by status, date range
  - Pagination
  - Detail page (`/interactions/[id]`):
    - Full question and answer
    - Citations list with document links
    - Status badge (answered/unknown)
    - `interaction_id` for Grafana lookup
- [ ] **Playground** (`/playground`):
  - KB selector dropdown
  - Question input (textarea)
  - Submit button with loading state
  - Answer display area:
    - Status indicator
    - Formatted answer text
    - Citations accordion
    - `interaction_id` display
  - History of recent queries in session

### Phase 4 - Polish & Accessibility
- [ ] Loading skeletons for all data-fetching pages
- [ ] Error boundaries with retry actions
- [ ] Toast notifications for actions (create, delete, upload)
- [ ] Empty states for lists
- [ ] `interaction_id` displayed prominently with copy-to-clipboard
- [ ] ARIA labels on all interactive elements
- [ ] Keyboard navigation support
- [ ] Responsive layout (desktop-first, tablet-friendly)

### Phase 5 - Testing
- [ ] Component tests (Vitest):
  - Citation display component
  - Status badge component
  - Query form component
- [ ] Integration tests:
  - Dashboard renders stats from API
  - KB creation flow
  - Query submission and response display
- [ ] E2E smoke test (Playwright):
  - Navigate to playground → select KB → submit question → see answer
- [ ] Accessibility audit (axe-core)

## Page Structure

```
/                           → Dashboard (stats + recent activity)
/knowledge-bases            → KB list + create action
/knowledge-bases/[id]       → KB detail + document management
/interactions               → Interaction history table
/interactions/[id]          → Interaction detail + citations
/playground                 → Live Q&A testing interface
```

## Critical Constraints
1. **All data comes from Backend API** - no direct calls to Core
2. **Server Components by default** - use `"use client"` only when needed for interactivity
3. **Type safety everywhere** - all API responses typed, no `any`
4. **Status badges must visually distinguish** `answered` (green), `unknown` (yellow), `error` (red)
5. **interaction_id must be visible** on every query result for Grafana cross-reference
6. **File upload** must support drag & drop and show progress

## Environment Variables
```
NEXT_PUBLIC_API_URL=http://localhost:5000  # Backend API base URL
```
