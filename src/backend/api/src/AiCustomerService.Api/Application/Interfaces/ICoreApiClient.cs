namespace AiCustomerService.Api.Application.Interfaces;

using AiCustomerService.Api.Domain.Models;

public interface ICoreApiClient
{
    Task<QueryResponseDto> QueryAsync(QueryRequestDto request, CancellationToken ct = default);
    Task<List<KnowledgeBaseDto>> ListKnowledgeBasesAsync(CancellationToken ct = default);
    Task<KnowledgeBaseDto> CreateKnowledgeBaseAsync(CreateKnowledgeBaseRequestDto request, CancellationToken ct = default);
    Task<KnowledgeBaseDto> GetKnowledgeBaseAsync(string id, CancellationToken ct = default);
    Task DeleteKnowledgeBaseAsync(string id, CancellationToken ct = default);
    Task<List<DocumentDto>> ListDocumentsAsync(string kbId, CancellationToken ct = default);
    Task<DocumentDto> UploadDocumentAsync(string kbId, Stream file, string filename, CancellationToken ct = default);
    Task DeleteDocumentAsync(string kbId, string docId, CancellationToken ct = default);
    Task TriggerIndexingAsync(string kbId, CancellationToken ct = default);
    Task<List<InteractionDto>> ListInteractionsAsync(CancellationToken ct = default);
    Task<InteractionDto> GetInteractionAsync(string id, CancellationToken ct = default);
    Task<DashboardStatsDto> GetDashboardStatsAsync(CancellationToken ct = default);
}
