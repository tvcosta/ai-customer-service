namespace AiCustomerService.Api.Domain.Models;

using System.Text.Json.Serialization;

public sealed record QueryRequestDto(
    [property: JsonPropertyName("knowledge_base_id")] string KnowledgeBaseId,
    [property: JsonPropertyName("question")] string Question);

public sealed record QueryResponseDto(
    [property: JsonPropertyName("status")] string Status,
    [property: JsonPropertyName("answer")] string? Answer,
    [property: JsonPropertyName("citations")] List<CitationDto>? Citations,
    [property: JsonPropertyName("interaction_id")] string InteractionId,
    [property: JsonPropertyName("error")] string? Error);

public sealed record CitationDto(
    [property: JsonPropertyName("source_document")] string SourceDocument,
    [property: JsonPropertyName("page")] int? Page,
    [property: JsonPropertyName("chunk_id")] string ChunkId,
    [property: JsonPropertyName("relevance_score")] double RelevanceScore);

public sealed record KnowledgeBaseDto(
    [property: JsonPropertyName("id")] string Id,
    [property: JsonPropertyName("name")] string Name,
    [property: JsonPropertyName("description")] string? Description,
    [property: JsonPropertyName("created_at")] DateTime CreatedAt);

public sealed record CreateKnowledgeBaseRequestDto(
    [property: JsonPropertyName("name")] string Name,
    [property: JsonPropertyName("description")] string? Description);

public sealed record DocumentDto(
    [property: JsonPropertyName("id")] string Id,
    [property: JsonPropertyName("kb_id")] string KbId,
    [property: JsonPropertyName("filename")] string Filename,
    [property: JsonPropertyName("status")] string Status,
    [property: JsonPropertyName("chunks_count")] int ChunksCount,
    [property: JsonPropertyName("uploaded_at")] DateTime UploadedAt);

public sealed record InteractionDto(
    [property: JsonPropertyName("id")] string Id,
    [property: JsonPropertyName("kb_id")] string KbId,
    [property: JsonPropertyName("question")] string Question,
    [property: JsonPropertyName("answer")] string? Answer,
    [property: JsonPropertyName("status")] string Status,
    [property: JsonPropertyName("citations")] List<CitationDto>? Citations,
    [property: JsonPropertyName("created_at")] DateTime CreatedAt);

public sealed record DashboardStatsDto(
    [property: JsonPropertyName("total_interactions")] int TotalInteractions,
    [property: JsonPropertyName("answered_count")] int AnsweredCount,
    [property: JsonPropertyName("unknown_count")] int UnknownCount,
    [property: JsonPropertyName("knowledge_base_count")] int KnowledgeBaseCount,
    [property: JsonPropertyName("document_count")] int DocumentCount);
