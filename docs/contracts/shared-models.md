# Shared Models - AI Customer Service System

All inter-service communication MUST conform to these schemas.
Field names use `snake_case` in JSON payloads.

---

## Standard Response Envelope

Every API response wraps data in this envelope:

```json
{
  "status": "answered | unknown | error",
  "answer": "string | null",
  "citations": [],
  "interaction_id": "uuid",
  "error": "string | null"
}
```

### `status` Values

| Value | Meaning |
|-------|---------|
| `answered` | KB contained the answer; `answer` and `citations` are populated |
| `unknown` | KB does not contain the answer; `answer` is the standard unknown message |
| `error` | Processing failed; `error` field contains details |

### Standard Unknown Message

Exact text (no variations):

> `"I don't have that information in the provided knowledge base."`

---

## Core Schemas

### QueryRequest

```json
{
  "knowledge_base_id": "string (uuid)",
  "question": "string"
}
```

### QueryResponse

```json
{
  "status": "answered | unknown | error",
  "answer": "string | null",
  "citations": [Citation],
  "interaction_id": "string (uuid)",
  "error": "string | null"
}
```

**Rules:**
- If `status == "answered"`, `citations` MUST be non-empty and `answer` MUST be non-null.
- If `status == "unknown"`, `answer` MUST be the standard unknown message, `citations` MUST be `[]`.
- If `status == "error"`, `error` MUST be non-null.

### Citation

```json
{
  "source_document": "string",
  "page": "integer | null",
  "chunk_id": "string",
  "relevance_score": "number (0.0 - 1.0)"
}
```

### KnowledgeBase

```json
{
  "id": "string (uuid)",
  "name": "string",
  "description": "string | null",
  "created_at": "string (ISO 8601)"
}
```

### CreateKnowledgeBaseRequest

```json
{
  "name": "string",
  "description": "string | null"
}
```

### Document

```json
{
  "id": "string (uuid)",
  "kb_id": "string (uuid)",
  "filename": "string",
  "status": "pending | processing | indexed | error",
  "chunks_count": "integer",
  "uploaded_at": "string (ISO 8601)"
}
```

### Document Status Values

| Value | Meaning |
|-------|---------|
| `pending` | Document uploaded, not yet processed |
| `processing` | Document is being chunked and indexed |
| `indexed` | Document chunks are in the vector store |
| `error` | Processing failed |

### Interaction

```json
{
  "id": "string (uuid)",
  "kb_id": "string (uuid)",
  "question": "string",
  "answer": "string | null",
  "status": "answered | unknown | error",
  "citations": [Citation],
  "created_at": "string (ISO 8601)"
}
```

### DashboardStats

```json
{
  "total_interactions": "integer",
  "answered_count": "integer",
  "unknown_count": "integer",
  "knowledge_base_count": "integer",
  "document_count": "integer"
}
```

---

## Field Naming Convention

- **JSON payloads (Python/API):** `snake_case` — e.g. `knowledge_base_id`, `source_document`
- **C# models:** `PascalCase` properties with `[JsonPropertyName("snake_case")]` or System.Text.Json naming policy
- **TypeScript models:** `camelCase` properties; API client maps from `snake_case`

## ID Format

All `id` fields are UUIDv4 strings, e.g. `"550e8400-e29b-41d4-a716-446655440000"`.

## Timestamps

All timestamps are ISO 8601 UTC strings, e.g. `"2026-02-15T10:30:00Z"`.
